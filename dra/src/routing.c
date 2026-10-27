#include <string.h>

#include "routing.h"

const dra_route_t *
dra_route_find(
    const dra_context_t *ctx,
    const char *realm,
    uint32_t application_id)
{
    const dra_route_t *best = NULL;
    unsigned int i;

    if (ctx == NULL || realm == NULL || realm[0] == '\0')
        return NULL;

    for (i = 0; i < ctx->route_count; i++) {
        const dra_route_t *route = &ctx->routes[i];

        if (!route->enabled)
            continue;

        if (route->application_id != application_id)
            continue;

        if (strcmp(route->realm, realm) != 0)
            continue;

        if (best == NULL || route->priority < best->priority)
            best = route;
    }

    return best;
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
