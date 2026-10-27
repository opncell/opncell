#include <stdio.h>
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

void
dra_context_final(dra_context_t *ctx)
{
    if (ctx == NULL)
        return;

    ctx->running = 0;

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