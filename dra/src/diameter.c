#include <arpa/inet.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <freeDiameter/freeDiameter-host.h>
#include <freeDiameter/libfdcore.h>

#include "diameter.h"

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