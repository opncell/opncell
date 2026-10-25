#include <inttypes.h>
#include <stdio.h>

#include "provisioning.h"

int
dra_provisioning_load(dra_context_t *ctx, const char *path)
{
    if (ctx == NULL || path == NULL)
        return -1;

    ctx->generation++;

    printf(
        "opncell-drad: configuration generation %" PRIu64 " loaded from %s\n",
        ctx->generation,
        path
    );

    return 0;
}

int
dra_provisioning_reload(dra_context_t *ctx, const char *path)
{
    if (ctx == NULL || path == NULL)
        return -1;

    printf("opncell-drad: provisioning reload requested\n");

    return dra_provisioning_load(ctx, path);
}
