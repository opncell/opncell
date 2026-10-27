#include <string.h>

#include <freeDiameter/freeDiameter-host.h>
#include <freeDiameter/libfdcore.h>

#include "routing.h"

const dra_route_t *
dra_route_find_len(
    const dra_context_t *ctx,
    const unsigned char *realm,
    size_t realm_len,
    uint32_t application_id)
{
    const dra_route_t *best = NULL;
    unsigned int i;

    if (ctx == NULL ||
        realm == NULL ||
        realm_len == 0)
        return NULL;

    for (i = 0; i < ctx->route_count; i++) {
        const dra_route_t *route = &ctx->routes[i];
        size_t route_realm_len;

        if (!route->enabled)
            continue;

        if (route->application_id != application_id)
            continue;

        route_realm_len = strlen(route->realm);

        if (fd_os_almostcasesrch(
                realm,
                realm_len,
                (const unsigned char *)route->realm,
                route_realm_len,
                NULL) != 0)
            continue;

        if (best == NULL ||
            route->priority < best->priority)
            best = route;
    }

    return best;
}

const dra_route_t *
dra_route_find(
    const dra_context_t *ctx,
    const char *realm,
    uint32_t application_id)
{
    if (realm == NULL)
        return NULL;

    return dra_route_find_len(
        ctx,
        (const unsigned char *)realm,
        strlen(realm),
        application_id);
}

const dra_peer_t *
dra_peer_select(
    const dra_context_t *ctx,
    const dra_route_t *route)
{
    const dra_peer_t *best = NULL;
    unsigned int i;

    if (ctx == NULL || route == NULL)
        return NULL;

    for (i = 0; i < ctx->peer_count; i++) {
        const dra_peer_t *peer = &ctx->peers[i];

        const dra_peer_runtime_t *runtime;

        if (!peer->enabled)
            continue;

        if (strcmp(peer->group, route->peer_group) != 0)
            continue;

        runtime = dra_peer_runtime_find_const(ctx, peer->name);
        if (runtime == NULL)
            continue;

        if (runtime->state != DRA_PEER_STATE_OPEN)
            continue;

        if (best == NULL || peer->priority < best->priority)
            best = peer;
    }

    return best;
}
