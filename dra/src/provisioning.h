#ifndef OPNCELL_DRA_PROVISIONING_H
#define OPNCELL_DRA_PROVISIONING_H

#include "dra-context.h"

int dra_provisioning_load(dra_context_t *ctx, const char *path);
int dra_provisioning_reload(dra_context_t *ctx, const char *path);

#endif /* OPNCELL_DRA_PROVISIONING_H */
