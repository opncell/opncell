#include <inttypes.h>
#include <pthread.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include <freeDiameter/freeDiameter-host.h>
#include <freeDiameter/libfdcore.h>

#include "diameter.h"
#include "dra-context.h"
#include "provisioning.h"
#include "routing.h"

static volatile sig_atomic_t shutdown_requested = 0;
static volatile sig_atomic_t reload_requested = 0;

static pthread_rwlock_t context_lock = PTHREAD_RWLOCK_INITIALIZER;

static void
signal_handler(int signo)
{
    switch (signo) {
    case SIGHUP:
        reload_requested = 1;
        break;

    case SIGINT:
    case SIGTERM:
        shutdown_requested = 1;
        break;

    default:
        break;
    }
}

static int
install_signal_handlers(void)
{
    struct sigaction sa;

    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;
    sa.sa_handler = signal_handler;

    if (sigaction(SIGHUP, &sa, NULL) == -1)
        return -1;

    if (sigaction(SIGINT, &sa, NULL) == -1)
        return -1;

    if (sigaction(SIGTERM, &sa, NULL) == -1)
        return -1;

    return 0;
}

static void
log_routing_test(const dra_context_t *ctx)
{
    const dra_route_t *route;
    const dra_peer_t *peer;

    if (pthread_rwlock_rdlock(&context_lock) != 0) {
        fprintf(stderr,
            "opncell-drad: failed to lock context for routing test\n");
        return;
    }

    route = dra_route_find(
        ctx,
        "operator-a.net",
        16777251);

    if (route == NULL) {
        pthread_rwlock_unlock(&context_lock);

        fprintf(stderr,
            "opncell-drad: routing test found no matching route\n");
        return;
    }

    peer = dra_peer_select(ctx, route);

    if (peer == NULL) {
        pthread_rwlock_unlock(&context_lock);

        fprintf(stderr,
            "opncell-drad: routing test found no eligible peer\n");
        return;
    }

    printf(
        "opncell-drad: routing test realm=%s app=%u "
        "route=%s group=%s peer=%s priority=%u\n",
        route->realm,
        route->application_id,
        route->name,
        route->peer_group,
        peer->name,
        peer->priority);

    pthread_rwlock_unlock(&context_lock);
}

static void
refresh_peer_runtime_states(
    dra_context_t *ctx)
{
    dra_peer_t *peers = NULL;
    unsigned int peer_count;
    unsigned int i;

    if (ctx == NULL)
        return;

    /*
     * Snapshot configured peers while holding only the DRA lock.
     * Do not call freeDiameter while context_lock is held.
     */
    if (pthread_rwlock_rdlock(&context_lock) != 0) {
        fprintf(stderr,
            "opncell-drad: failed to lock context "
            "for peer-state snapshot\n");
        return;
    }

    peer_count = ctx->peer_count;

    if (peer_count != 0) {
        peers = malloc(
            peer_count * sizeof(*peers));

        if (peers == NULL) {
            pthread_rwlock_unlock(&context_lock);

            fprintf(stderr,
                "opncell-drad: failed to allocate "
                "peer-state snapshot for %u peers\n",
                peer_count);
            return;
        }

        memcpy(
            peers,
            ctx->peers,
            peer_count * sizeof(*peers));
    }

    pthread_rwlock_unlock(&context_lock);

    /*
     * Query freeDiameter outside context_lock.
     */
    for (i = 0; i < peer_count; i++) {
        dra_peer_state_t state;

        if (dra_diameter_get_peer_state(
                &peers[i],
                &state) != 0)
            continue;

        /*
         * Publish the state only after the freeDiameter call
         * has completed.
         */
        if (pthread_rwlock_wrlock(&context_lock) != 0) {
            fprintf(stderr,
                "opncell-drad: failed to lock context "
                "for peer-state update\n");
            free(peers);
            return;
        }

        /*
         * Verify that the same configured peer still exists before
         * publishing the sampled state.
         */
        {
            const dra_peer_t *current_peer;

            current_peer = dra_peer_find_by_name(
                ctx,
                peers[i].name);

            if (current_peer != NULL &&
                strcmp(
                    current_peer->identity,
                    peers[i].identity) == 0) {
                dra_peer_state_set(
                    ctx,
                    peers[i].name,
                    state);
            }
        }

        pthread_rwlock_unlock(&context_lock);
    }

    free(peers);
}

static void
peer_hook_cb(
    enum fd_hook_type type,
    struct msg *msg,
    struct peer_hdr *peer,
    void *other,
    struct fd_hook_permsgdata *pmd,
    void *regdata)
{
    dra_context_t *ctx = regdata;
    const dra_peer_t *configured_peer;
    const char *identity;
    int fd_state;

    (void)msg;
    (void)other;
    (void)pmd;

    if (ctx == NULL || peer == NULL)
        return;

    identity = (const char *)peer->info.pi_diamid;
    if (identity == NULL || identity[0] == '\0')
        return;

    if (pthread_rwlock_wrlock(&context_lock) != 0)
        return;

    configured_peer = dra_peer_find_by_identity(
        ctx,
        identity);

    if (configured_peer == NULL) {
        pthread_rwlock_unlock(&context_lock);
        return;
    }

    fd_state = fd_peer_get_state(peer);

    switch (type) {
    case HOOK_PEER_CONNECT_SUCCESS:
        if (fd_state == STATE_OPEN) {
            dra_peer_state_set(
                ctx,
                configured_peer->name,
                DRA_PEER_STATE_OPEN);
        } else {
            dra_peer_state_set(
                ctx,
                configured_peer->name,
                DRA_PEER_STATE_CONNECTING);
        }
        break;

    case HOOK_PEER_CONNECT_FAILED:
        dra_peer_state_set(
            ctx,
            configured_peer->name,
            DRA_PEER_STATE_DOWN);
        break;

    default:
        break;
    }

    pthread_rwlock_unlock(&context_lock);
}

int
main(int argc, char *argv[])
{
    dra_context_t ctx;
    dra_context_t pending_ctx = {0};
    int pending_reload = 0;
    int rollback_pending = 0;
    struct fd_hook_hdl *peer_hook = NULL;
    struct fd_rt_out_hdl *routing_hook = NULL;
    const char *config_path =
        "/usr/local/etc/opncell/dra.yaml";

    if (argc > 1)
        config_path = argv[1];

    printf("opncell-drad: starting\n");

    if (fd_core_initialize() != 0) {
        fprintf(stderr,
            "opncell-drad: freeDiameter initialization failed\n");
        return EXIT_FAILURE;
    }

    printf("opncell-drad: freeDiameter initialized\n");

    if (dra_context_init(&ctx) != 0) {
        fprintf(stderr,
            "opncell-drad: failed to initialize context\n");
        return EXIT_FAILURE;
    }

    if (fd_hook_register(
            HOOK_MASK(
                HOOK_PEER_CONNECT_SUCCESS,
                HOOK_PEER_CONNECT_FAILED),
            peer_hook_cb,
            &ctx,
            NULL,
            &peer_hook) != 0) {
        fprintf(stderr,
            "opncell-drad: failed to register peer hook\n");

        dra_context_final(&ctx);
        return EXIT_FAILURE;
    }

    if (install_signal_handlers() != 0) {
        perror("opncell-drad: sigaction");

        fd_hook_unregister(peer_hook);
        dra_context_final(&ctx);

        return EXIT_FAILURE;
    }

    if (dra_provisioning_load(
            &ctx,
            config_path) != 0) {
        fprintf(stderr,
            "opncell-drad: failed to load configuration\n");

        fd_hook_unregister(peer_hook);
        dra_context_final(&ctx);

        return EXIT_FAILURE;
    }

    if (dra_diameter_write_config(
            &ctx,
            "/tmp/opncell-drad-freediameter.conf") != 0) {
        fprintf(stderr,
            "opncell-drad: failed to generate "
            "freeDiameter config\n");

        fd_hook_unregister(peer_hook);
        dra_context_final(&ctx);

        return EXIT_FAILURE;
    }

    if (fd_core_parseconf(
            "/tmp/opncell-drad-freediameter.conf") != 0) {
        fprintf(stderr,
            "opncell-drad: freeDiameter configuration failed\n");

        fd_hook_unregister(peer_hook);
        dra_context_final(&ctx);

        return EXIT_FAILURE;
    }

    printf(
        "opncell-drad: freeDiameter configuration ready\n");

    /*
     * Validate every configured peer before adding anything to
     * freeDiameter. This prevents a partially populated peer table
     * during startup.
     */
    if (dra_diameter_preflight_peers(&ctx) != 0) {
        fprintf(stderr,
            "opncell-drad: Diameter peer preflight failed\n");

        fd_hook_unregister(peer_hook);
        dra_context_final(&ctx);

        return EXIT_FAILURE;
    }

    if (dra_diameter_add_configured_peers(
            &ctx) != 0) {
        fprintf(stderr,
            "opncell-drad: failed to add configured "
            "Diameter peers\n");

        fd_hook_unregister(peer_hook);
        dra_context_final(&ctx);

        return EXIT_FAILURE;
    }

    if (fd_core_start() != 0) {
        fprintf(stderr,
            "opncell-drad: failed to start freeDiameter core\n");

        fd_hook_unregister(peer_hook);
        dra_context_final(&ctx);

        return EXIT_FAILURE;
    }

    if (fd_core_waitstartcomplete() != 0) {
        fprintf(stderr,
            "opncell-drad: freeDiameter startup "
            "did not complete\n");

        fd_core_shutdown();
        fd_core_wait_shutdown_complete();

        fd_hook_unregister(peer_hook);
        dra_context_final(&ctx);

        return EXIT_FAILURE;
    }

    printf("opncell-drad: freeDiameter core running\n");

    if (dra_diameter_register_routing(
            &ctx,
            &routing_hook) != 0) {
        fprintf(stderr,
            "opncell-drad: failed to register "
            "Diameter routing callback\n");

        fd_core_shutdown();
        fd_core_wait_shutdown_complete();

        fd_hook_unregister(peer_hook);
        dra_context_final(&ctx);

        return EXIT_FAILURE;
    }

    printf(
        "opncell-drad: Diameter routing callback registered\n");

    if (dra_diameter_test_routing(&ctx) != 0) {
        fprintf(stderr,
            "opncell-drad: Diameter routing diagnostic failed\n");

        dra_diameter_unregister_routing(routing_hook);
        routing_hook = NULL;

        fd_core_shutdown();
        fd_core_wait_shutdown_complete();

        fd_hook_unregister(peer_hook);
        dra_context_final(&ctx);

        return EXIT_FAILURE;
    }

    printf(
        "opncell-drad: Diameter routing diagnostic passed\n");

    log_routing_test(&ctx);

    printf("opncell-drad: ready\n");

    while (!shutdown_requested) {
        /*
         * Stage a new candidate configuration on SIGHUP.
         *
         * Do not allow pending_ctx to be overwritten while an
         * earlier reconciliation or rollback is still active.
         */
        if (reload_requested) {
            reload_requested = 0;

            if (pending_reload || rollback_pending) {
                fprintf(stderr,
                    "opncell-drad: reload deferred; "
                    "Diameter reconciliation already in progress\n");
            } else if (pthread_rwlock_wrlock(
                    &context_lock) != 0) {
                fprintf(stderr,
                    "opncell-drad: failed to lock context "
                    "for reload\n");
            } else {
                dra_context_t next;
                int reload_rc;

                printf(
                    "opncell-drad: provisioning reload "
                    "requested\n");

                reload_rc = dra_provisioning_prepare(
                    &ctx,
                    config_path,
                    &next);

                /*
                 * No persistent configuration delta.
                 */
                if (reload_rc == 0 &&
                    next.generation == ctx.generation) {
                    printf(
                        "opncell-drad: configuration "
                        "unchanged\n");

                    reload_rc = 2;
                }

                /*
                 * Validate all candidate Diameter peers before
                 * touching any live association.
                 */
                if (reload_rc == 0) {
                    int reconcile_rc;

                    if (dra_diameter_preflight_peers(
                            &next) != 0) {
                        reload_rc = -1;
                    } else {
                        reconcile_rc =
                            dra_diameter_reconcile_peers(
                                &ctx,
                                &next);

                        if (reconcile_rc < 0) {
                            reload_rc = -1;
                        } else if (reconcile_rc > 0) {
                            /*
                             * Diameter peer changes are
                             * asynchronous. Retain a deep copy of
                             * the validated candidate until
                             * reconciliation completes.
                             */
                            if (dra_context_clone(
                                    &pending_ctx,
                                    &next) != 0) {
                                fprintf(stderr,
                                    "opncell-drad: failed to retain "
                                    "pending configuration context\n");

                                reload_rc = -1;
                            } else {
                                pending_reload = 1;

                                printf(
                                    "opncell-drad: reload pending "
                                    "Diameter peer reconciliation\n");

                                reload_rc = 1;
                            }
                        } else {
                            /*
                             * Routing/policy-only change.
                             * No Diameter association needs
                             * to be disturbed.
                             */
                            if (dra_provisioning_commit(
                                    &ctx,
                                    &next) != 0) {
                                fprintf(stderr,
                                    "opncell-drad: failed to commit "
                                    "routing-only configuration\n");

                                reload_rc = -1;
                            } else if (dra_diameter_update_routing(
                                    &ctx) != 0) {
                                fprintf(stderr,
                                    "opncell-drad: failed to update "
                                    "Diameter routing snapshot\n");
                            }
                        }
                    }
                }

                /*
                 * The candidate has either been cloned into
                 * pending_ctx, committed into ctx, rejected,
                 * or determined to be a no-op. Release its
                 * dynamically owned storage.
                 */
                dra_context_reset(&next);

                pthread_rwlock_unlock(
                    &context_lock);

                if (reload_rc < 0) {
                    fprintf(stderr,
                        "opncell-drad: reload failed\n");
                } else if (reload_rc == 2) {
                    /*
                     * No-op reload was already logged.
                     */
                } else if (reload_rc > 0 &&
                    pending_reload) {
                    printf(
                        "opncell-drad: reload staged pending "
                        "Diameter reconciliation\n");
                } else {
                    printf(
                        "opncell-drad: configuration "
                        "generation %" PRIu64
                        " loaded from %s\n",
                        ctx.generation,
                        config_path);

                    printf(
                        "opncell-drad: loaded %u roaming "
                        "peers and %u routes\n",
                        ctx.peer_count,
                        ctx.route_count);

                    log_routing_test(&ctx);
                }
            }
        }

        /*
         * Forward reconciliation.
         *
         * Remove obsolete or replaced peers first. Removal is
         * asynchronous and may require multiple main-loop passes.
         *
         * Do not hold context_lock while invoking freeDiameter.
         */
        if (pending_reload) {
            int reconcile_rc;

            reconcile_rc =
                dra_diameter_remove_stale_peers(
                    &ctx,
                    &pending_ctx);

            if (reconcile_rc < 0) {
                fprintf(stderr,
                    "opncell-drad: pending Diameter "
                    "removal failed; starting rollback\n");

                /*
                 * Keep pending_ctx intact. Rollback needs it to
                 * determine which candidate peers may need removal
                 * and which active peers must be restored.
                 */
                pending_reload = 0;
                rollback_pending = 1;
            } else if (reconcile_rc == 0) {
                printf(
                    "opncell-drad: pending Diameter "
                    "removals complete\n");

                /*
                 * Obsolete peers are gone. Install peers required
                 * by the candidate.
                 */
                if (dra_diameter_add_pending_peers(
                        &ctx,
                        &pending_ctx) != 0) {
                    fprintf(stderr,
                        "opncell-drad: failed adding pending "
                        "Diameter peers; starting rollback\n");

                    /*
                     * Do not clear pending_ctx here.
                     * Rollback still requires the candidate.
                     */
                    pending_reload = 0;
                    rollback_pending = 1;
                } else {
                    /*
                     * freeDiameter now reflects the candidate.
                     * Commit pending_ctx as the authoritative DRA
                     * configuration.
                     */
                    if (pthread_rwlock_wrlock(
                            &context_lock) != 0) {
                        fprintf(stderr,
                            "opncell-drad: failed to lock "
                            "context for pending reload "
                            "commit; starting rollback\n");

                        pending_reload = 0;
                        rollback_pending = 1;
                    } else {
                        int commit_rc;

                        commit_rc = dra_provisioning_commit(
                            &ctx,
                            &pending_ctx);

                        pthread_rwlock_unlock(
                            &context_lock);

                        if (commit_rc != 0) {
                            fprintf(stderr,
                                "opncell-drad: failed to commit "
                                "pending configuration; "
                                "starting rollback\n");

                            /*
                             * freeDiameter already reflects the
                             * candidate, but ctx remains authoritative.
                             * Keep pending_ctx intact for rollback.
                             */
                            pending_reload = 0;
                            rollback_pending = 1;
                        } else {
                            printf(
                                "opncell-drad: configuration "
                                "generation %" PRIu64
                                " committed after Diameter "
                                "reconciliation\n",
                                ctx.generation);

                            printf(
                                "opncell-drad: loaded %u roaming "
                                "peers and %u routes\n",
                                ctx.peer_count,
                                ctx.route_count);

                            pending_reload = 0;

                            /*
                             * ctx owns its own deep copy after commit.
                             * Release the pending candidate.
                             */
                            dra_context_reset(&pending_ctx);

                            log_routing_test(&ctx);
                        }
                    }
                }
            }
        }

        /*
         * Rollback reconciliation.
         *
         * ctx is still authoritative because pending_ctx was never
         * committed.
         *
         * First remove any candidate-specific peers that may have
         * been installed before the forward transaction failed.
         */
        if (rollback_pending) {
            int rollback_rc;

            rollback_rc =
                dra_diameter_remove_candidate_peers(
                    &ctx,
                    &pending_ctx);

            if (rollback_rc < 0) {
                fprintf(stderr,
                    "opncell-drad: Diameter rollback failed\n");

                /*
                 * Leave pending_ctx intact for diagnosis.
                 * The active DRA context remains unchanged, but
                 * operator intervention may be required to repair
                 * the freeDiameter peer table.
                 *
                 * pending_ctx will still be released during
                 * process shutdown.
                 */
                rollback_pending = 0;
            } else if (rollback_rc == 0) {
                /*
                 * Candidate-specific peers are now gone.
                 * Restore any enabled peers required by the active
                 * configuration that were removed during the failed
                 * forward transaction.
                 */
                if (dra_diameter_restore_current_peers(
                        &ctx,
                        &pending_ctx) != 0) {
                    fprintf(stderr,
                        "opncell-drad: failed restoring active "
                        "Diameter configuration\n");

                    /*
                     * Keep pending_ctx available for diagnosis.
                     * It will be released during process shutdown.
                     */
                    rollback_pending = 0;
                } else {
                    printf(
                        "opncell-drad: Diameter rollback complete; "
                        "active configuration unchanged\n");

                    rollback_pending = 0;

                    dra_context_reset(&pending_ctx);

                    log_routing_test(&ctx);
                }
            }
        }

        refresh_peer_runtime_states(&ctx);

        if (dra_diameter_update_routing(&ctx) != 0) {
            fprintf(stderr,
                "opncell-drad: failed to update "
                "Diameter routing runtime snapshot\n");
        }

        sleep(1);
    }

    printf("opncell-drad: shutdown requested\n");

    if (routing_hook != NULL) {
        if (dra_diameter_unregister_routing(
                routing_hook) != 0) {
            fprintf(stderr,
                "opncell-drad: failed to unregister "
                "Diameter routing callback\n");
        }

        routing_hook = NULL;
    }

    if (fd_core_shutdown() != 0) {
        fprintf(stderr,
            "opncell-drad: freeDiameter shutdown "
            "request failed\n");
    }

    if (fd_core_wait_shutdown_complete() != 0) {
        fprintf(stderr,
            "opncell-drad: freeDiameter shutdown "
            "did not complete cleanly\n");
    }

    if (peer_hook != NULL) {
        if (fd_hook_unregister(peer_hook) != 0) {
            fprintf(stderr,
                "opncell-drad: failed to unregister "
                "peer hook\n");
        }

        peer_hook = NULL;
    }

    if (unlink(
            "/tmp/opncell-drad-freediameter.conf") != 0) {
        perror(
            "opncell-drad: unlink freeDiameter config");
    }

    /*
     * pending_ctx may intentionally have been retained for
     * diagnosis after a failed rollback. Always release any
     * dynamically owned storage before process termination.
     */
    dra_context_reset(&pending_ctx);

    dra_context_final(&ctx);

    printf("opncell-drad: terminated\n");

    return EXIT_SUCCESS;
}