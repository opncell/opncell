#ifndef OPNCELL_DRA_CONTEXT_H
#define OPNCELL_DRA_CONTEXT_H

#include <stdint.h>

#define DRA_MAX_PEERS   64
#define DRA_MAX_ROUTES  128

#define DRA_NAME_LEN      64
#define DRA_IDENTITY_LEN 256
#define DRA_REALM_LEN    256
#define DRA_ADDRESS_LEN   64

typedef struct dra_peer_s {
    char name[DRA_NAME_LEN];
    char group[DRA_NAME_LEN];
    char identity[DRA_IDENTITY_LEN];
    char realm[DRA_REALM_LEN];
    char address[DRA_ADDRESS_LEN];

    uint16_t port;
    uint32_t priority;

    int enabled;
} dra_peer_t;

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

    dra_peer_t peers[DRA_MAX_PEERS];
    unsigned int peer_count;

    dra_route_t routes[DRA_MAX_ROUTES];
    unsigned int route_count;
} dra_context_t;

int dra_context_init(dra_context_t *ctx);
void dra_context_final(dra_context_t *ctx);

#endif /* OPNCELL_DRA_CONTEXT_H */
