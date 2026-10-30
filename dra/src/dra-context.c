#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "dra-context.h"

int
dra_context_init(dra_context_t *ctx)
{
    if (ctx == NULL)
        return -1;

    memset(ctx, 0, sizeof(*ctx));

    ctx->generation = 0;
    ctx->running = 1;

    printf("opncell-drad: context initialized\n");

    return 0;
}

int
dra_context_clone(
    dra_context_t *dst,
    const dra_context_t *src)
{
    dra_peer_t *peers = NULL;
    dra_peer_runtime_t *peer_runtime = NULL;
    dra_route_t *routes = NULL;

    if (dst == NULL || src == NULL)
        return -1;

    if (src->peer_count != 0) {
        peers = malloc(
            src->peer_count * sizeof(*peers));

        if (peers == NULL)
            return -1;

        memcpy(
            peers,
            src->peers,
            src->peer_count * sizeof(*peers));
    }

    if (src->peer_runtime_count != 0) {
        peer_runtime = malloc(
            src->peer_runtime_count * sizeof(*peer_runtime));

        if (peer_runtime == NULL) {
            free(peers);
            return -1;
        }

        memcpy(
            peer_runtime,
            src->peer_runtime,
            src->peer_runtime_count * sizeof(*peer_runtime));
    }

    if (src->route_count != 0) {
        routes = malloc(
            src->route_count * sizeof(*routes));

        if (routes == NULL) {
            free(peers);
            free(peer_runtime);
            return -1;
        }

        memcpy(
            routes,
            src->routes,
            src->route_count * sizeof(*routes));
    }

    /*
     * Release any dynamically owned storage already present
     * in the destination before replacing its contents.
     */
    free(dst->peers);
    free(dst->peer_runtime);
    free(dst->routes);

    *dst = *src;

    dst->peers = peers;
    dst->peer_capacity = src->peer_count;
    dst->peer_runtime = peer_runtime;
    dst->peer_runtime_capacity = src->peer_runtime_count;
    dst->routes = routes;
    dst->route_capacity = src->route_count;

    return 0;
}

int
dra_context_reserve_peers(
    dra_context_t *ctx,
    unsigned int capacity)
{
    dra_peer_t *new_peers;
    unsigned int new_capacity;

    if (ctx == NULL)
        return -1;

    if (capacity <= ctx->peer_capacity)
        return 0;

    new_capacity = ctx->peer_capacity;

    if (new_capacity == 0)
        new_capacity = 16;

    while (new_capacity < capacity) {
        if (new_capacity > UINT32_MAX / 2)
            return -1;

        new_capacity *= 2;
    }

    new_peers = realloc(
        ctx->peers,
        new_capacity * sizeof(*new_peers));

    if (new_peers == NULL)
        return -1;

    if (new_capacity > ctx->peer_capacity) {
        memset(
            &new_peers[ctx->peer_capacity],
            0,
            (new_capacity - ctx->peer_capacity) *
                sizeof(*new_peers));
    }

    ctx->peers = new_peers;
    ctx->peer_capacity = new_capacity;

    return 0;
}

int
dra_context_reserve_peer_runtime(
    dra_context_t *ctx,
    unsigned int capacity)
{
    dra_peer_runtime_t *new_runtime;
    unsigned int new_capacity;

    if (ctx == NULL)
        return -1;

    if (capacity <= ctx->peer_runtime_capacity)
        return 0;

    new_capacity = ctx->peer_runtime_capacity;

    if (new_capacity == 0)
        new_capacity = 16;

    while (new_capacity < capacity) {
        if (new_capacity > UINT32_MAX / 2)
            return -1;

        new_capacity *= 2;
    }

    new_runtime = realloc(
        ctx->peer_runtime,
        new_capacity * sizeof(*new_runtime));

    if (new_runtime == NULL)
        return -1;

    if (new_capacity > ctx->peer_runtime_capacity) {
        memset(
            &new_runtime[ctx->peer_runtime_capacity],
            0,
            (new_capacity - ctx->peer_runtime_capacity) *
                sizeof(*new_runtime));
    }

    ctx->peer_runtime = new_runtime;
    ctx->peer_runtime_capacity = new_capacity;

    return 0;
}

int
dra_context_reserve_routes(
    dra_context_t *ctx,
    unsigned int capacity)
{
    dra_route_t *new_routes;
    unsigned int new_capacity;

    if (ctx == NULL)
        return -1;

    if (capacity <= ctx->route_capacity)
        return 0;

    new_capacity = ctx->route_capacity;

    if (new_capacity == 0)
        new_capacity = 16;

    while (new_capacity < capacity) {
        if (new_capacity > UINT32_MAX / 2)
            return -1;

        new_capacity *= 2;
    }

    new_routes = realloc(
        ctx->routes,
        new_capacity * sizeof(*new_routes));

    if (new_routes == NULL)
        return -1;

    if (new_capacity > ctx->route_capacity) {
        memset(
            &new_routes[ctx->route_capacity],
            0,
            (new_capacity - ctx->route_capacity) *
                sizeof(*new_routes));
    }

    ctx->routes = new_routes;
    ctx->route_capacity = new_capacity;

    return 0;
}

void
dra_context_reset(dra_context_t *ctx)
{
    if (ctx == NULL)
        return;

    free(ctx->peers);
    free(ctx->peer_runtime);
    free(ctx->routes);

    memset(ctx, 0, sizeof(*ctx));
}

void
dra_context_final(dra_context_t *ctx)
{
    if (ctx == NULL)
        return;

    ctx->running = 0;

    dra_context_reset(ctx);

    printf("opncell-drad: context finalized\n");
}

dra_peer_runtime_t *
dra_peer_runtime_find(
    dra_context_t *ctx,
    const char *name)
{
    unsigned int i;

    if (ctx == NULL || name == NULL || name[0] == '\0')
        return NULL;

    for (i = 0; i < ctx->peer_runtime_count; i++) {
        if (strcmp(ctx->peer_runtime[i].name, name) == 0)
            return &ctx->peer_runtime[i];
    }

    return NULL;
}

const dra_peer_runtime_t *
dra_peer_runtime_find_const(
    const dra_context_t *ctx,
    const char *name)
{
    unsigned int i;

    if (ctx == NULL || name == NULL || name[0] == '\0')
        return NULL;

    for (i = 0; i < ctx->peer_runtime_count; i++) {
        if (strcmp(ctx->peer_runtime[i].name, name) == 0)
            return &ctx->peer_runtime[i];
    }

    return NULL;
}

int
dra_peer_state_set(
    dra_context_t *ctx,
    const char *name,
    dra_peer_state_t state)
{
    dra_peer_runtime_t *runtime;

    runtime = dra_peer_runtime_find(ctx, name);
    if (runtime == NULL)
        return -1;

    runtime->state = state;

    return 0;
}

const dra_peer_t *
dra_peer_find_by_identity(
    const dra_context_t *ctx,
    const char *identity)
{
    unsigned int i;

    if (ctx == NULL || identity == NULL || identity[0] == '\0')
        return NULL;

    for (i = 0; i < ctx->peer_count; i++) {
        if (strcmp(ctx->peers[i].identity, identity) == 0)
            return &ctx->peers[i];
    }

    return NULL;
}

const dra_peer_t *
dra_peer_find_by_name(
    const dra_context_t *ctx,
    const char *name)
{
    unsigned int i;

    if (ctx == NULL || name == NULL || name[0] == '\0')
        return NULL;

    for (i = 0; i < ctx->peer_count; i++) {
        if (strcmp(ctx->peers[i].name, name) == 0)
            return &ctx->peers[i];
    }

    return NULL;
}