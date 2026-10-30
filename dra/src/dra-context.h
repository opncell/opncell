#ifndef OPNCELL_DRA_CONTEXT_H
#define OPNCELL_DRA_CONTEXT_H

#include <stdint.h>

#define DRA_NAME_LEN      64
#define DRA_IDENTITY_LEN 256
#define DRA_REALM_LEN    256
#define DRA_ADDRESS_LEN   64

typedef uint32_t dra_peer_id_t;
typedef uint32_t dra_route_id_t;

#define DRA_INVALID_PEER_ID UINT32_MAX
#define DRA_INVALID_ROUTE_ID UINT32_MAX

typedef enum dra_transport_e {
    DRA_TRANSPORT_SCTP = 0
} dra_transport_t;

typedef struct dra_peer_s {
    char name[DRA_NAME_LEN];
    char group[DRA_NAME_LEN];
    char identity[DRA_IDENTITY_LEN];
    char realm[DRA_REALM_LEN];
    char address[DRA_ADDRESS_LEN];

    uint16_t port;
    uint32_t priority;

    dra_transport_t transport;
    int enabled;
} dra_peer_t;

typedef enum dra_peer_state_e {
    DRA_PEER_STATE_DOWN = 0,
    DRA_PEER_STATE_CONNECTING,
    DRA_PEER_STATE_OPEN,
    DRA_PEER_STATE_DRAINING
} dra_peer_state_t;

typedef struct dra_peer_runtime_s {
    char name[DRA_NAME_LEN];

    dra_peer_state_t state;
} dra_peer_runtime_t;

typedef enum dra_route_action_e {
    DRA_ROUTE_ACTION_RELAY = 0,
    DRA_ROUTE_ACTION_PROXY,
    DRA_ROUTE_ACTION_REDIRECT
} dra_route_action_t;

typedef struct dra_route_s {
    char name[DRA_NAME_LEN];
    char realm[DRA_REALM_LEN];
    char peer_group[DRA_NAME_LEN];

    uint32_t application_id;
    uint32_t priority;

    dra_route_action_t action;
    int enabled;
} dra_route_t;

typedef struct dra_context_s {
    uint64_t generation;
    int running;

    char diameter_identity[DRA_IDENTITY_LEN];
    char diameter_realm[DRA_REALM_LEN];
    char listen_address[DRA_ADDRESS_LEN];
    uint16_t listen_port;
    dra_transport_t listen_transport;

    dra_peer_t *peers;
    unsigned int peer_count;
    unsigned int peer_capacity;

    dra_peer_runtime_t *peer_runtime;
    unsigned int peer_runtime_count;
    unsigned int peer_runtime_capacity;

    dra_route_t *routes;
    unsigned int route_count;
    unsigned int route_capacity;

} dra_context_t;

int dra_context_init(dra_context_t *ctx);

int
dra_context_clone(
    dra_context_t *dst,
    const dra_context_t *src);

int
dra_context_reserve_peers(
    dra_context_t *ctx,
    unsigned int capacity);

int
dra_context_reserve_peer_runtime(
    dra_context_t *ctx,
    unsigned int capacity);

int
dra_context_reserve_routes(
    dra_context_t *ctx,
    unsigned int capacity);

void dra_context_reset(dra_context_t *ctx);
void dra_context_final(dra_context_t *ctx);

dra_peer_runtime_t *
dra_peer_runtime_find(
    dra_context_t *ctx,
    const char *name);

const dra_peer_runtime_t *
dra_peer_runtime_find_const(
    const dra_context_t *ctx,
    const char *name);

int
dra_peer_state_set(
    dra_context_t *ctx,
    const char *name,
    dra_peer_state_t state);

const dra_peer_t *
dra_peer_find_by_identity(
    const dra_context_t *ctx,
    const char *identity);

const dra_peer_t *dra_peer_find_by_name(
    const dra_context_t *ctx,
    const char *name);

#endif /* OPNCELL_DRA_CONTEXT_H */
