#include <arpa/inet.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>

#include <freeDiameter/freeDiameter-host.h>
#include <freeDiameter/libfdcore.h>

#include "diameter.h"
#include "routing.h"

static pthread_rwlock_t routing_snapshot_lock =
    PTHREAD_RWLOCK_INITIALIZER;

static dra_context_t routing_snapshot;
static int routing_snapshot_valid = 0;

int
dra_diameter_write_config(
    const dra_context_t *ctx,
    const char *path)
{
    FILE *fp;

    if (ctx == NULL || path == NULL)
        return -1;

    fp = fopen(path, "w");
    if (fp == NULL) {
        fprintf(stderr,
            "opncell-drad: unable to write freeDiameter config %s\n",
            path);
        return -1;
    }

    fprintf(fp,
        "Identity = \"%s\";\n",
        ctx->diameter_identity);

    fprintf(fp,
        "Realm = \"%s\";\n",
        ctx->diameter_realm);

    fprintf(fp,
        "Port = %u;\n",
        ctx->listen_port);

    fprintf(fp,
        "SecPort = 0;\n");

    fprintf(fp,
        "No_TCP;\n");

    if (fclose(fp) != 0) {
        fprintf(stderr,
            "opncell-drad: failed closing freeDiameter config %s\n",
            path);
        return -1;
    }

    printf(
        "opncell-drad: wrote freeDiameter config %s\n",
        path);

    return 0;
}

static int
add_peer_endpoint(
    struct peer_info *info,
    const dra_peer_t *peer)
{
    sSS ss;
    socklen_t sl;

    memset(&ss, 0, sizeof(ss));

    if (inet_pton(AF_INET, peer->address,
            &((sSA4 *)&ss)->sin_addr) == 1) {
        sSA4 *sin = (sSA4 *)&ss;

        sin->sin_family = AF_INET;
        sin->sin_port = htons(peer->port);
        sl = sizeof(*sin);
    } else if (inet_pton(AF_INET6, peer->address,
                   &((sSA6 *)&ss)->sin6_addr) == 1) {
        sSA6 *sin6 = (sSA6 *)&ss;

        sin6->sin6_family = AF_INET6;
        sin6->sin6_port = htons(peer->port);
        sl = sizeof(*sin6);
    } else {
        fprintf(stderr,
            "opncell-drad: invalid peer address %s for %s\n",
            peer->address,
            peer->name);
        return -1;
    }

    if (fd_ep_add_merge(
            &info->pi_endpoints,
            (sSA *)&ss,
            sl,
            EP_FL_CONF) != 0) {
        fprintf(stderr,
            "opncell-drad: failed to add endpoint for peer %s\n",
            peer->name);
        return -1;
    }

    return 0;
}

int
dra_diameter_peer_transport_equal(
    const dra_peer_t *a,
    const dra_peer_t *b)
{
    if (a == NULL || b == NULL)
        return 0;

    return strcmp(a->identity, b->identity) == 0 &&
           strcmp(a->realm, b->realm) == 0 &&
           strcmp(a->address, b->address) == 0 &&
           a->port == b->port &&
           a->transport == b->transport &&
           a->enabled == b->enabled;
}

int
dra_diameter_preflight_peers(
    const dra_context_t *ctx)
{
    unsigned int i;

    if (ctx == NULL)
        return -1;

    for (i = 0; i < ctx->peer_count; i++) {
        const dra_peer_t *peer;
        char *diamid;
        char *realm;
        size_t diamid_len = 0;
        size_t realm_len = 0;
        struct in_addr addr4;
        struct in6_addr addr6;

        peer = &ctx->peers[i];

        if (!peer->enabled)
            continue;

        /*
         * Peer endpoints currently require a literal IPv4 or IPv6
         * address. DNS discovery will be handled separately later.
         */
        if (inet_pton(AF_INET, peer->address, &addr4) != 1 &&
            inet_pton(AF_INET6, peer->address, &addr6) != 1) {
            fprintf(stderr,
                "opncell-drad: preflight failed for peer %s: "
                "invalid IP address %s\n",
                peer->name,
                peer->address);
            return -1;
        }

        diamid = (char *)peer->identity;

        if (fd_os_validate_DiameterIdentity(
                &diamid,
                &diamid_len,
                1) != 0) {
            fprintf(stderr,
                "opncell-drad: preflight failed for peer %s: "
                "invalid Diameter identity %s\n",
                peer->name,
                peer->identity);
            return -1;
        }

        free(diamid);

        realm = (char *)peer->realm;

        if (fd_os_validate_DiameterIdentity(
                &realm,
                &realm_len,
                1) != 0) {
            fprintf(stderr,
                "opncell-drad: preflight failed for peer %s: "
                "invalid Diameter realm %s\n",
                peer->name,
                peer->realm);
            return -1;
        }

        free(realm);
    }

    return 0;
}

int
dra_diameter_get_peer_state(
    const dra_peer_t *peer,
    dra_peer_state_t *state)
{
    int fd_state;
    int rc;

    if (peer == NULL || state == NULL)
        return -1;

    if (!peer->enabled) {
        *state = DRA_PEER_STATE_DOWN;
        return 0;
    }

    rc = fd_peer_get_state_byid(
        (DiamId_t)peer->identity,
        strlen(peer->identity),
        0,
        &fd_state);

    if (rc == ENOENT) {
        *state = DRA_PEER_STATE_DOWN;
        return 0;
    }

    if (rc != 0) {
        fprintf(stderr,
            "opncell-drad: failed reading Diameter peer "
            "state for %s identity=%s rc=%d\n",
            peer->name,
            peer->identity,
            rc);
        return -1;
    }

    switch (fd_state) {
    case STATE_OPEN:
        *state = DRA_PEER_STATE_OPEN;
        break;

    case STATE_ZOMBIE:
        *state = DRA_PEER_STATE_DOWN;
        break;

    default:
        *state = DRA_PEER_STATE_CONNECTING;
        break;
    }

    return 0;
}

int
dra_diameter_add_peer(
    const dra_peer_t *peer)
{
    struct peer_info info;

    if (peer == NULL)
        return -1;

    if (!peer->enabled)
        return 0;

    memset(&info, 0, sizeof(info));

    fd_list_init(&info.pi_endpoints, NULL);

    info.pi_diamid = (DiamId_t)peer->identity;
    info.pi_diamidlen = strlen(peer->identity);

    info.config.pic_realm = (DiamId_t)peer->realm;
    info.config.pic_port = peer->port;

    info.config.pic_flags.pro3 = PI_P3_DEFAULT;
    info.config.pic_flags.pro4 = PI_P4_SCTP;
    info.config.pic_flags.alg = PI_ALGPREF_SCTP;
    info.config.pic_flags.sec = PI_SEC_NONE;
    info.config.pic_flags.persist = PI_PRST_ALWAYS;

    if (add_peer_endpoint(&info, peer) != 0)
        return -1;

    if (fd_peer_add(
            &info,
            "opncell-dra",
            NULL,
            NULL) != 0) {
        fprintf(stderr,
            "opncell-drad: failed to add Diameter peer %s (%s)\n",
            peer->name,
            peer->identity);
        return -1;
    }

    printf(
        "opncell-drad: added Diameter peer %s identity=%s "
        "address=%s:%u transport=sctp\n",
        peer->name,
        peer->identity,
        peer->address,
        peer->port);

    return 0;
}

int
dra_diameter_add_configured_peers(
    const dra_context_t *ctx)
{
    unsigned int i;

    if (ctx == NULL)
        return -1;

    for (i = 0; i < ctx->peer_count; i++) {
        if (dra_diameter_add_peer(&ctx->peers[i]) != 0)
            return -1;
    }

    return 0;
}

int
dra_diameter_remove_peer(
    const char *identity)
{
    int rc;

    if (identity == NULL || identity[0] == '\0')
        return EINVAL;

    rc = fd_peer_remove(
        (DiamId_t)identity,
        strlen(identity));

    switch (rc) {
    case 0:
        printf(
            "opncell-drad: removed Diameter peer identity=%s\n",
            identity);
        break;

    case EAGAIN:
        printf(
            "opncell-drad: Diameter peer removal in progress "
            "identity=%s\n",
            identity);
        break;

    case ENOENT:
        printf(
            "opncell-drad: Diameter peer not present "
            "identity=%s\n",
            identity);
        break;

    default:
        fprintf(stderr,
            "opncell-drad: failed removing Diameter peer "
            "identity=%s rc=%d\n",
            identity,
            rc);
        break;
    }

    return rc;
}

static void
force_candidate_no_delivery(
    struct rtd_candidate *candidate)
{
    if (candidate == NULL)
        return;

    /*
     * Make the score definitively negative regardless of any
     * earlier freeDiameter routing score.
     */
    if (candidate->score >= 0)
        candidate->score = -1;
}

int
dra_diameter_update_routing(
    const dra_context_t *ctx)
{
    int rc;

    if (ctx == NULL)
        return -1;

    if (pthread_rwlock_wrlock(
            &routing_snapshot_lock) != 0)
        return -1;

    rc = dra_context_clone(
        &routing_snapshot,
        ctx);

    if (rc == 0)
        routing_snapshot_valid = 1;

    pthread_rwlock_unlock(
        &routing_snapshot_lock);

    return rc;
}

static void
dra_score_candidates(
    const dra_context_t *ctx,
    const unsigned char *realm,
    size_t realm_len,
    uint32_t application_id,
    const unsigned char *destination_host,
    size_t destination_host_len,
    struct fd_list *candidates)
{
    const dra_route_t *route;
    struct fd_list *li;

    if (ctx == NULL ||
        realm == NULL ||
        realm_len == 0 ||
        candidates == NULL)
        return;

    route = dra_route_find_len(
        ctx,
        realm,
        realm_len,
        application_id);

    /*
     * Only relay routing is implemented at this stage.
     * Proxy and redirect routes must fail closed rather than
     * silently behaving as relay routes.
     */
    if (route != NULL &&
        route->action != DRA_ROUTE_ACTION_RELAY) {
        for (li = candidates->next;
             li != candidates;
             li = li->next) {
            force_candidate_no_delivery(
                (struct rtd_candidate *)li);
        }

        return;
    }

    /*
     * No provisioned route: fail closed.
     */
    if (route == NULL) {
        for (li = candidates->next;
             li != candidates;
             li = li->next) {
            force_candidate_no_delivery(
                (struct rtd_candidate *)li);
        }

        return;
    }

    for (li = candidates->next;
         li != candidates;
         li = li->next) {
        struct rtd_candidate *candidate;
        const dra_peer_t *peer;
        const dra_peer_runtime_t *runtime;
        unsigned int i;

        candidate = (struct rtd_candidate *)li;
        peer = NULL;

        for (i = 0; i < ctx->peer_count; i++) {
            if (strlen(ctx->peers[i].identity) !=
                candidate->diamidlen)
                continue;

            if (fd_os_almostcasesrch(
                    candidate->diamid,
                    candidate->diamidlen,
                    (const unsigned char *)
                        ctx->peers[i].identity,
                    strlen(ctx->peers[i].identity),
                    NULL) == 0) {
                peer = &ctx->peers[i];
                break;
            }
        }

        if (peer == NULL ||
            !peer->enabled ||
            strcmp(peer->group, route->peer_group) != 0) {
            force_candidate_no_delivery(candidate);
            continue;
        }

        /*
         * An explicit Destination-Host is authoritative within the
         * peer group selected by the DRA route.
         *
         * Candidates other than the requested host are excluded.
         * If the requested host is unknown, outside the selected group,
         * disabled, or unavailable, all candidates will therefore become
         * unroutable and the request will fail closed.
         */
        if (destination_host != NULL &&
            destination_host_len != 0) {
            if (candidate->diamidlen != destination_host_len ||
                fd_os_almostcasesrch(
                    candidate->diamid,
                    candidate->diamidlen,
                    destination_host,
                    destination_host_len,
                    NULL) != 0) {
                force_candidate_no_delivery(candidate);
                continue;
            }
        }

        runtime = dra_peer_runtime_find_const(
            ctx,
            peer->name);

        if (runtime == NULL ||
            runtime->state != DRA_PEER_STATE_OPEN) {
            force_candidate_no_delivery(candidate);
            continue;
        }

        /*
         * DRA routing policy is authoritative among eligible peers.
         *
         * freeDiameter routing callbacks are additive, so add the delta
         * required to normalize the candidate to a DRA-controlled score.
         * Lower configured peer priority produces the higher final score.
         */
        candidate->score +=
            (1000000 - (int)peer->priority) -
            candidate->score;
    }
}

int
dra_diameter_test_routing(
    const dra_context_t *ctx)
{
    dra_context_t test_ctx;
    struct fd_list candidates;
    struct rtd_candidate a;
    struct rtd_candidate a_backup;
    struct rtd_candidate b;
    int rc = -1;

    if (ctx == NULL)
        return -1;

    memset(&test_ctx, 0, sizeof(test_ctx));

    if (dra_context_clone(
            &test_ctx,
            ctx) != 0)
        return -1;

    if (dra_peer_state_set(
            &test_ctx,
            "operator-a",
            DRA_PEER_STATE_OPEN) != 0)
        goto out;

    if (dra_peer_state_set(
            &test_ctx,
            "operator-a-backup",
            DRA_PEER_STATE_OPEN) != 0)
        goto out;

    if (dra_peer_state_set(
            &test_ctx,
            "operator-b",
            DRA_PEER_STATE_OPEN) != 0)
        goto out;

    fd_list_init(&candidates, NULL);

    memset(&a, 0, sizeof(a));
    memset(&a_backup, 0, sizeof(a_backup));
    memset(&b, 0, sizeof(b));

    fd_list_init(&a.chain, &a);
    fd_list_init(&a_backup.chain, &a_backup);
    fd_list_init(&b.chain, &b);

    a.diamid = (DiamId_t)"dra.operator-a.net";
    a.diamidlen = strlen(a.diamid);
    a.score = 100;

    a_backup.diamid = (DiamId_t)"dra2.operator-a.net";
    a_backup.diamidlen = strlen(a_backup.diamid);
    a_backup.score = 100;

    b.diamid = (DiamId_t)"dra.operator-b.net";
    b.diamidlen = strlen(b.diamid);
    b.score = 100;

    fd_list_insert_before(&candidates, &a.chain);
    fd_list_insert_before(&candidates, &a_backup.chain);
    fd_list_insert_before(&candidates, &b.chain);

    dra_score_candidates(
        &test_ctx,
        (const unsigned char *)"OPERATOR-A.NET",
        strlen("OPERATOR-A.NET"),
        16777251,
        NULL,
        0,
        &candidates);

    printf(
        "opncell-drad: routing diagnostic "
        "operator-a=%d operator-a-backup=%d operator-b=%d\n",
        a.score,
        a_backup.score,
        b.score);

    if (a.score <= a_backup.score)
        goto out;

    if (b.score >= 0)
        goto out;

    a.score = 100;
    a_backup.score = 100;
    b.score = 100;

    dra_score_candidates(
        &test_ctx,
        (const unsigned char *)"operator-a.net",
        strlen("operator-a.net"),
        16777251,
        (const unsigned char *)"dra2.operator-a.net",
        strlen("dra2.operator-a.net"),
        &candidates);

    printf(
        "opncell-drad: routing destination-host diagnostic "
        "operator-a=%d operator-a-backup=%d operator-b=%d\n",
        a.score,
        a_backup.score,
        b.score);

    if (a.score >= 0)
        goto out;

    if (a_backup.score < 0)
        goto out;

    if (b.score >= 0)
        goto out;

    if (dra_peer_state_set(
            &test_ctx,
            "operator-a-backup",
            DRA_PEER_STATE_DOWN) != 0)
        goto out;

    a.score = 100;
    a_backup.score = 100;
    b.score = 100;

    dra_score_candidates(
        &test_ctx,
        (const unsigned char *)"operator-a.net",
        strlen("operator-a.net"),
        16777251,
        (const unsigned char *)"dra2.operator-a.net",
        strlen("dra2.operator-a.net"),
        &candidates);

    printf(
        "opncell-drad: routing destination-host unavailable diagnostic "
        "operator-a=%d operator-a-backup=%d operator-b=%d\n",
        a.score,
        a_backup.score,
        b.score);

    if (a.score >= 0 ||
        a_backup.score >= 0 ||
        b.score >= 0)
        goto out;

    if (dra_peer_state_set(
            &test_ctx,
            "operator-a-backup",
            DRA_PEER_STATE_OPEN) != 0)
        goto out;

    a.score = 100;
    a_backup.score = 100;
    b.score = 100;

    dra_score_candidates(
        &test_ctx,
        (const unsigned char *)"operator-a.net",
        strlen("operator-a.net"),
        16777251,
        (const unsigned char *)"dra.operator-b.net",
        strlen("dra.operator-b.net"),
        &candidates);

    printf(
        "opncell-drad: routing destination-host fail-closed diagnostic "
        "operator-a=%d operator-a-backup=%d operator-b=%d\n",
        a.score,
        a_backup.score,
        b.score);

    if (a.score >= 0 ||
        a_backup.score >= 0 ||
        b.score >= 0)
        goto out;

    a.score = 100;
    a_backup.score = 100;
    b.score = 100;

    test_ctx.routes[0].action = DRA_ROUTE_ACTION_PROXY;

    dra_score_candidates(
        &test_ctx,
        (const unsigned char *)"operator-a.net",
        strlen("operator-a.net"),
        16777251,
        NULL,
        0,
        &candidates);

    printf(
        "opncell-drad: routing unsupported-action diagnostic "
        "operator-a=%d operator-a-backup=%d operator-b=%d\n",
        a.score,
        a_backup.score,
        b.score);

    if (a.score >= 0 ||
        a_backup.score >= 0 ||
        b.score >= 0)
        goto out;

    test_ctx.routes[0].action = DRA_ROUTE_ACTION_RELAY;

    a.score = 100;
    a_backup.score = 100;
    b.score = 100;

    dra_score_candidates(
        &test_ctx,
        (const unsigned char *)"operator-a.net",
        strlen("operator-a.net"),
        4,
        NULL,
        0,
        &candidates);

    printf(
        "opncell-drad: routing application-id fail-closed diagnostic "
        "operator-a=%d operator-a-backup=%d operator-b=%d\n",
        a.score,
        a_backup.score,
        b.score);

    if (a.score >= 0 ||
        a_backup.score >= 0 ||
        b.score >= 0)
        goto out;

    a.score = 100;
    a_backup.score = 100;
    b.score = 100;

    dra_score_candidates(
        &test_ctx,
        (const unsigned char *)"unmatched.example.net",
        strlen("unmatched.example.net"),
        16777251,
        NULL,
        0,
        &candidates);

    printf(
        "opncell-drad: routing fail-closed diagnostic "
        "operator-a=%d operator-a-backup=%d operator-b=%d\n",
        a.score,
        a_backup.score,
        b.score);

    if (a.score >= 0 ||
        a_backup.score >= 0 ||
        b.score >= 0)
        goto out;

    rc = 0;

out:
    dra_context_reset(&test_ctx);
    return rc;
}

static int
dra_rt_out_cb(
    void *cbdata,
    struct msg **pmsg,
    struct fd_list *candidates)
{
    const dra_context_t *ctx;
    struct msg *msg;
    struct msg_hdr *hdr;
    struct avp *avp;
    union avp_value *destination_realm = NULL;
    union avp_value *destination_host = NULL;
    struct fd_list *li;

    (void)cbdata;

    if (pmsg == NULL ||
        *pmsg == NULL ||
        candidates == NULL)
        return EINVAL;

    msg = *pmsg;

    if (fd_msg_hdr(msg, &hdr) != 0)
        return EINVAL;

    /*
     * Find Destination-Realm.
     */
    if (fd_msg_browse(
            msg,
            MSG_BRW_FIRST_CHILD,
            &avp,
            NULL) != 0)
        return EINVAL;

    while (avp != NULL) {
        struct avp_hdr *ahdr;

        if (fd_msg_avp_hdr(avp, &ahdr) != 0)
            return EINVAL;

        if (!(ahdr->avp_flags & AVP_FLAG_VENDOR)) {
            if (ahdr->avp_code == AC_DESTINATION_REALM) {
                if (fd_msg_parse_dict(
                        avp,
                        fd_g_config->cnf_dict,
                        NULL) != 0)
                    return EINVAL;

                destination_realm = ahdr->avp_value;
            } else if (ahdr->avp_code == AC_DESTINATION_HOST) {
                if (fd_msg_parse_dict(
                        avp,
                        fd_g_config->cnf_dict,
                        NULL) != 0)
                    return EINVAL;

                destination_host = ahdr->avp_value;
            }
        }

        if (fd_msg_browse(
                avp,
                MSG_BRW_NEXT,
                &avp,
                NULL) != 0)
            return EINVAL;
    }

    /*
     * Fail closed if Destination-Realm is absent or empty.
     */
    if (destination_realm == NULL ||
        destination_realm->os.data == NULL ||
        destination_realm->os.len == 0) {
        for (li = candidates->next;
             li != candidates;
             li = li->next) {
            force_candidate_no_delivery(
                (struct rtd_candidate *)li);
        }

        return 0;
    }

    if (pthread_rwlock_rdlock(
            &routing_snapshot_lock) != 0)
        return EINVAL;

    if (!routing_snapshot_valid) {
        pthread_rwlock_unlock(
            &routing_snapshot_lock);

        for (li = candidates->next;
             li != candidates;
             li = li->next) {
            force_candidate_no_delivery(
                (struct rtd_candidate *)li);
        }

        return 0;
    }

    ctx = &routing_snapshot;

    dra_score_candidates(
        ctx,
        destination_realm->os.data,
        destination_realm->os.len,
        hdr->msg_appl,
        destination_host != NULL
            ? destination_host->os.data
            : NULL,
        destination_host != NULL
            ? destination_host->os.len
            : 0,
        candidates);

    pthread_rwlock_unlock(
        &routing_snapshot_lock);

    return 0;
}

int
dra_diameter_register_routing(
    dra_context_t *ctx,
    struct fd_rt_out_hdl **handler)
{
    if (ctx == NULL || handler == NULL)
        return -1;

    if (dra_diameter_update_routing(ctx) != 0)
        return -1;

    return fd_rt_out_register(
        dra_rt_out_cb,
        NULL,
        0,
        handler);
}

int
dra_diameter_unregister_routing(
    struct fd_rt_out_hdl *handler)
{
    int rc = 0;

    if (handler != NULL) {
        rc = fd_rt_out_unregister(
            handler,
            NULL);

        if (rc != 0)
            return rc;
    }

    if (pthread_rwlock_wrlock(
            &routing_snapshot_lock) != 0)
        return -1;

    if (routing_snapshot_valid) {
        dra_context_reset(&routing_snapshot);
        routing_snapshot_valid = 0;
    }

    pthread_rwlock_unlock(
        &routing_snapshot_lock);

    return 0;
}

int
dra_diameter_reconcile_peers(
    const dra_context_t *current,
    const dra_context_t *next)
{
    unsigned int i;
    int changes = 0;

    if (current == NULL || next == NULL)
        return -1;

    for (i = 0; i < current->peer_count; i++) {
        const dra_peer_t *old_peer;
        const dra_peer_t *new_peer;

        old_peer = &current->peers[i];
        new_peer = dra_peer_find_by_name(
            next,
            old_peer->name);

        if (new_peer == NULL) {
            printf(
                "opncell-drad: peer %s scheduled for removal\n",
                old_peer->name);
            changes = 1;
            continue;
        }

        if (!dra_diameter_peer_transport_equal(
                old_peer,
                new_peer)) {
            printf(
                "opncell-drad: peer %s requires Diameter replacement\n",
                old_peer->name);
            changes = 1;
        }
    }

    for (i = 0; i < next->peer_count; i++) {
        const dra_peer_t *new_peer;
        const dra_peer_t *old_peer;

        new_peer = &next->peers[i];
        old_peer = dra_peer_find_by_name(
            current,
            new_peer->name);

        if (old_peer == NULL) {
            printf(
                "opncell-drad: peer %s scheduled for addition\n",
                new_peer->name);
            changes = 1;
        }
    }

    return changes;
}

int
dra_diameter_remove_stale_peers(
    const dra_context_t *current,
    const dra_context_t *next)
{
    unsigned int i;
    int pending = 0;

    if (current == NULL || next == NULL)
        return -1;

    for (i = 0; i < current->peer_count; i++) {
        const dra_peer_t *old_peer;
        const dra_peer_t *new_peer;
        int rc;

        old_peer = &current->peers[i];

        /*
         * Disabled peers were never installed in freeDiameter.
         */
        if (!old_peer->enabled)
            continue;

        new_peer = dra_peer_find_by_name(
            next,
            old_peer->name);

        /*
         * Keep an unchanged Diameter association.
         */
        if (new_peer != NULL &&
            dra_diameter_peer_transport_equal(
                old_peer,
                new_peer))
            continue;

        rc = dra_diameter_remove_peer(
            old_peer->identity);

        if (rc == 0 || rc == ENOENT)
            continue;

        if (rc == EAGAIN) {
            pending = 1;
            continue;
        }

        fprintf(stderr,
            "opncell-drad: failed reconciling removal "
            "of peer %s identity=%s rc=%d\n",
            old_peer->name,
            old_peer->identity,
            rc);

        return -1;
    }

    return pending;
}

int
dra_diameter_add_pending_peers(
    const dra_context_t *current,
    const dra_context_t *next)
{
    unsigned int i;

    if (current == NULL || next == NULL)
        return -1;

    for (i = 0; i < next->peer_count; i++) {
        const dra_peer_t *new_peer;
        const dra_peer_t *old_peer;

        new_peer = &next->peers[i];

        if (!new_peer->enabled)
            continue;

        old_peer = dra_peer_find_by_name(
            current,
            new_peer->name);

        /*
         * An unchanged enabled Diameter peer remains installed.
         */
        if (old_peer != NULL &&
            old_peer->enabled &&
            dra_diameter_peer_transport_equal(
                old_peer,
                new_peer))
            continue;

        if (dra_diameter_add_peer(new_peer) != 0) {
            fprintf(stderr,
                "opncell-drad: failed adding pending "
                "Diameter peer %s identity=%s\n",
                new_peer->name,
                new_peer->identity);

            return -1;
        }
    }

    return 0;
}

int
dra_diameter_remove_candidate_peers(
    const dra_context_t *current,
    const dra_context_t *candidate)
{
    unsigned int i;
    int pending = 0;

    if (current == NULL || candidate == NULL)
        return -1;

    for (i = 0; i < candidate->peer_count; i++) {
        const dra_peer_t *candidate_peer;
        const dra_peer_t *current_peer;
        int rc;

        candidate_peer = &candidate->peers[i];

        /*
         * A disabled candidate peer could not have been added to
         * freeDiameter, so there is nothing to roll back.
         */
        if (!candidate_peer->enabled)
            continue;

        current_peer = dra_peer_find_by_name(
            current,
            candidate_peer->name);

        /*
         * An unchanged enabled peer existed before the transaction
         * and must remain in place during rollback.
         */
        if (current_peer != NULL &&
            current_peer->enabled &&
            dra_diameter_peer_transport_equal(
                current_peer,
                candidate_peer))
            continue;

        /*
         * This peer was either newly introduced by the candidate or
         * was a replacement. It may or may not have been successfully
         * installed before another add failed.
         *
         * ENOENT is therefore a successful rollback condition.
         */
        rc = dra_diameter_remove_peer(
            candidate_peer->identity);

        if (rc == 0 || rc == ENOENT)
            continue;

        if (rc == EAGAIN) {
            pending = 1;
            continue;
        }

        fprintf(stderr,
            "opncell-drad: rollback failed removing "
            "candidate peer %s identity=%s rc=%d\n",
            candidate_peer->name,
            candidate_peer->identity,
            rc);

        return -1;
    }

    return pending;
}

int
dra_diameter_restore_current_peers(
    const dra_context_t *current,
    const dra_context_t *candidate)
{
    unsigned int i;

    if (current == NULL || candidate == NULL)
        return -1;

    for (i = 0; i < current->peer_count; i++) {
        const dra_peer_t *current_peer;
        const dra_peer_t *candidate_peer;

        current_peer = &current->peers[i];

        if (!current_peer->enabled)
            continue;

        candidate_peer = dra_peer_find_by_name(
            candidate,
            current_peer->name);

        /*
         * An unchanged enabled peer was never removed during the
         * candidate transaction, so leave it alone.
         */
        if (candidate_peer != NULL &&
            candidate_peer->enabled &&
            dra_diameter_peer_transport_equal(
                current_peer,
                candidate_peer))
            continue;

        /*
         * This peer belonged to the active configuration but was
         * removed as part of the candidate transaction. Restore it.
         */
        if (dra_diameter_add_peer(current_peer) != 0) {
            fprintf(stderr,
                "opncell-drad: rollback failed restoring "
                "current peer %s identity=%s\n",
                current_peer->name,
                current_peer->identity);

            return -1;
        }
    }

    return 0;
}