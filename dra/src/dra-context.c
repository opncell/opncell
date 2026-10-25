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
