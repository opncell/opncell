#ifndef OPNCELL_DRA_CONTEXT_H
#define OPNCELL_DRA_CONTEXT_H

#include <stdint.h>

typedef struct dra_context_s {
    uint64_t generation;
    int running;
} dra_context_t;

int dra_context_init(dra_context_t *ctx);
void dra_context_final(dra_context_t *ctx);

#endif /* OPNCELL_DRA_CONTEXT_H */
