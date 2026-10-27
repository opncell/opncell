#ifndef OPNCELL_DRA_DIAMETER_H
#define OPNCELL_DRA_DIAMETER_H

#include <stddef.h>

#include "dra-context.h"

int dra_diameter_write_config(
    const dra_context_t *ctx,
    const char *path);

int dra_diameter_add_peer(
    const dra_peer_t *peer);

int dra_diameter_add_configured_peers(
    const dra_context_t *ctx);

int dra_diameter_remove_peer(
    const char *identity);

int dra_diameter_peer_transport_equal(
    const dra_peer_t *a,
    const dra_peer_t *b);

int dra_diameter_reconcile_peers(
    const dra_context_t *current,
    const dra_context_t *next);

int dra_diameter_remove_stale_peers(
    const dra_context_t *current,
    const dra_context_t *next);

int dra_diameter_add_pending_peers(
    const dra_context_t *current,
    const dra_context_t *next);

int dra_diameter_preflight_peers(
    const dra_context_t *ctx);

int dra_diameter_get_peer_state(
    const dra_peer_t *peer,
    dra_peer_state_t *state);

int dra_diameter_remove_candidate_peers(
    const dra_context_t *current,
    const dra_context_t *candidate);

int dra_diameter_restore_current_peers(
    const dra_context_t *current,
    const dra_context_t *candidate);

#endif /* OPNCELL_DRA_DIAMETER_H */