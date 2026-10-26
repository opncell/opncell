#ifndef OPNCELL_DRA_ROUTING_H
#define OPNCELL_DRA_ROUTING_H

#include <stdint.h>

#include "dra-context.h"

const dra_route_t *
dra_route_find(
    const dra_context_t *ctx,
    const char *realm,
    uint32_t application_id);

const dra_peer_t *
dra_peer_select(
    const dra_context_t *ctx,
    const dra_route_t *route);

#endif /* OPNCELL_DRA_ROUTING_H */
