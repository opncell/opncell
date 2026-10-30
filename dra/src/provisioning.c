#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <yaml.h>

#include "provisioning.h"

static void
copy_string(char *dst, size_t dst_len, const yaml_char_t *src)
{
    if (dst == NULL || dst_len == 0 || src == NULL)
        return;

    snprintf(dst, dst_len, "%s", (const char *)src);
}

static int
parse_bool(const yaml_char_t *value)
{
    if (value == NULL)
        return 0;

    return strcmp((const char *)value, "true") == 0 ||
           strcmp((const char *)value, "yes") == 0 ||
           strcmp((const char *)value, "1") == 0;
}

static unsigned long
parse_ulong(const yaml_char_t *value)
{
    if (value == NULL)
        return 0;

    return strtoul((const char *)value, NULL, 10);
}

static yaml_node_t *
mapping_lookup(
    yaml_document_t *document,
    yaml_node_t *mapping,
    const char *key)
{
    yaml_node_pair_t *pair;

    if (document == NULL || mapping == NULL ||
        mapping->type != YAML_MAPPING_NODE || key == NULL)
        return NULL;

    for (pair = mapping->data.mapping.pairs.start;
         pair < mapping->data.mapping.pairs.top;
         pair++) {
        yaml_node_t *key_node;
        yaml_node_t *value_node;

        key_node = yaml_document_get_node(document, pair->key);
        value_node = yaml_document_get_node(document, pair->value);

        if (key_node == NULL || value_node == NULL)
            continue;

        if (key_node->type != YAML_SCALAR_NODE)
            continue;

        if (strcmp((const char *)key_node->data.scalar.value, key) == 0)
            return value_node;
    }

    return NULL;
}

static int
parse_diameter(
    dra_context_t *ctx,
    yaml_document_t *document,
    yaml_node_t *diameter)
{
    yaml_node_t *node;
    yaml_node_t *listen;

    if (diameter == NULL || diameter->type != YAML_MAPPING_NODE)
        return -1;

    node = mapping_lookup(document, diameter, "identity");
    if (node != NULL && node->type == YAML_SCALAR_NODE)
        copy_string(
            ctx->diameter_identity,
            sizeof(ctx->diameter_identity),
            node->data.scalar.value);

    node = mapping_lookup(document, diameter, "realm");
    if (node != NULL && node->type == YAML_SCALAR_NODE)
        copy_string(
            ctx->diameter_realm,
            sizeof(ctx->diameter_realm),
            node->data.scalar.value);

    listen = mapping_lookup(document, diameter, "listen");
    if (listen == NULL || listen->type != YAML_MAPPING_NODE)
        return -1;

    node = mapping_lookup(document, listen, "address");
    if (node != NULL && node->type == YAML_SCALAR_NODE)
        copy_string(
            ctx->listen_address,
            sizeof(ctx->listen_address),
            node->data.scalar.value);

    node = mapping_lookup(document, listen, "port");
    if (node != NULL && node->type == YAML_SCALAR_NODE)
        ctx->listen_port = (uint16_t)parse_ulong(node->data.scalar.value);

    node = mapping_lookup(document, listen, "transport");
    if (node != NULL && node->type == YAML_SCALAR_NODE) {
        const char *value =
            (const char *)node->data.scalar.value;

        if (strcmp(value, "sctp") == 0)
            ctx->listen_transport = DRA_TRANSPORT_SCTP;
        else {
            fprintf(stderr,
                "opncell-drad: unsupported listen transport '%s'\n",
                value);
            return -1;
        }
    }

    return 0;
}

static int
parse_peers(
    dra_context_t *ctx,
    yaml_document_t *document,
    yaml_node_t *peers)
{
    yaml_node_item_t *item;

    if (peers == NULL || peers->type != YAML_SEQUENCE_NODE)
        return -1;

    ctx->peer_count = 0;

    for (item = peers->data.sequence.items.start;
        item < peers->data.sequence.items.top;
        item++) {
        yaml_node_t *entry;
        yaml_node_t *node;
        dra_peer_t *peer;

        if (dra_context_reserve_peers(
                ctx,
                ctx->peer_count + 1) != 0) {
            fprintf(stderr,
                "opncell-drad: failed to grow peer store "
                "for peer %u\n",
                ctx->peer_count + 1);
            return -1;
        }

        entry = yaml_document_get_node(document, *item);
        if (entry == NULL || entry->type != YAML_MAPPING_NODE)
            return -1;

        peer = &ctx->peers[ctx->peer_count];
        memset(peer, 0, sizeof(*peer));

        node = mapping_lookup(document, entry, "name");
        if (node != NULL && node->type == YAML_SCALAR_NODE)
            copy_string(peer->name, sizeof(peer->name),
                node->data.scalar.value);

        node = mapping_lookup(document, entry, "group");
        if (node != NULL && node->type == YAML_SCALAR_NODE)
            copy_string(peer->group, sizeof(peer->group),
                node->data.scalar.value);

        node = mapping_lookup(document, entry, "identity");
        if (node != NULL && node->type == YAML_SCALAR_NODE)
            copy_string(peer->identity, sizeof(peer->identity),
                node->data.scalar.value);

        node = mapping_lookup(document, entry, "realm");
        if (node != NULL && node->type == YAML_SCALAR_NODE)
            copy_string(peer->realm, sizeof(peer->realm),
                node->data.scalar.value);

        node = mapping_lookup(document, entry, "address");
        if (node != NULL && node->type == YAML_SCALAR_NODE)
            copy_string(peer->address, sizeof(peer->address),
                node->data.scalar.value);

        node = mapping_lookup(document, entry, "port");
        if (node != NULL && node->type == YAML_SCALAR_NODE)
            peer->port = (uint16_t)parse_ulong(node->data.scalar.value);

        node = mapping_lookup(document, entry, "transport");
        if (node != NULL && node->type == YAML_SCALAR_NODE) {
            const char *value =
                (const char *)node->data.scalar.value;

            if (strcmp(value, "sctp") == 0)
                peer->transport = DRA_TRANSPORT_SCTP;
            else {
                fprintf(stderr,
                    "opncell-drad: unsupported peer transport '%s'\n",
                    value);
                return -1;
            }
        }

        node = mapping_lookup(document, entry, "priority");
        if (node != NULL && node->type == YAML_SCALAR_NODE)
            peer->priority = (uint32_t)parse_ulong(node->data.scalar.value);

        node = mapping_lookup(document, entry, "enabled");
        if (node != NULL && node->type == YAML_SCALAR_NODE)
            peer->enabled = parse_bool(node->data.scalar.value);

        ctx->peer_count++;
    }

    return 0;
}

static int
parse_routes(
    dra_context_t *ctx,
    yaml_document_t *document,
    yaml_node_t *routes)
{
    yaml_node_item_t *item;

    if (routes == NULL || routes->type != YAML_SEQUENCE_NODE)
        return -1;

    ctx->route_count = 0;

    for (item = routes->data.sequence.items.start;
         item < routes->data.sequence.items.top;
         item++) {
        yaml_node_t *entry;
        yaml_node_t *node;
        dra_route_t *route;

        if (dra_context_reserve_routes(
                ctx,
                ctx->route_count + 1) != 0) {
            fprintf(stderr,
                "opncell-drad: failed to grow route store "
                "for route %u\n",
                ctx->route_count + 1);
            return -1;
        }

        entry = yaml_document_get_node(document, *item);
        if (entry == NULL || entry->type != YAML_MAPPING_NODE)
            return -1;

        route = &ctx->routes[ctx->route_count];
        memset(route, 0, sizeof(*route));

        node = mapping_lookup(document, entry, "name");
        if (node != NULL && node->type == YAML_SCALAR_NODE)
            copy_string(route->name, sizeof(route->name),
                node->data.scalar.value);

        node = mapping_lookup(document, entry, "realm");
        if (node != NULL && node->type == YAML_SCALAR_NODE)
            copy_string(route->realm, sizeof(route->realm),
                node->data.scalar.value);

        node = mapping_lookup(document, entry, "peer_group");
        if (node != NULL && node->type == YAML_SCALAR_NODE)
            copy_string(route->peer_group, sizeof(route->peer_group),
                node->data.scalar.value);

        node = mapping_lookup(document, entry, "application_id");
        if (node != NULL && node->type == YAML_SCALAR_NODE)
            route->application_id =
                (uint32_t)parse_ulong(node->data.scalar.value);

        node = mapping_lookup(document, entry, "action");
        if (node != NULL && node->type == YAML_SCALAR_NODE) {
            const char *value =
                (const char *)node->data.scalar.value;

            if (strcmp(value, "relay") == 0)
                route->action = DRA_ROUTE_ACTION_RELAY;
            else if (strcmp(value, "proxy") == 0)
                route->action = DRA_ROUTE_ACTION_PROXY;
            else if (strcmp(value, "redirect") == 0)
                route->action = DRA_ROUTE_ACTION_REDIRECT;
            else {
                fprintf(stderr,
                    "opncell-drad: invalid route action '%s'\n",
                    value);
                return -1;
            }
        }

        node = mapping_lookup(document, entry, "priority");
        if (node != NULL && node->type == YAML_SCALAR_NODE)
            route->priority =
                (uint32_t)parse_ulong(node->data.scalar.value);

        node = mapping_lookup(document, entry, "enabled");
        if (node != NULL && node->type == YAML_SCALAR_NODE)
            route->enabled = parse_bool(node->data.scalar.value);

        ctx->route_count++;
    }

    return 0;
}

static int
peer_group_exists(const dra_context_t *ctx, const char *group)
{
    unsigned int i;

    if (ctx == NULL || group == NULL || group[0] == '\0')
        return 0;

    for (i = 0; i < ctx->peer_count; i++) {
        if (strcmp(ctx->peers[i].group, group) == 0)
            return 1;
    }

    return 0;
}

static int
validate_config(const dra_context_t *ctx)
{
    unsigned int i;

    if (ctx == NULL)
        return -1;

    if (ctx->diameter_identity[0] == '\0') {
        fprintf(stderr, "opncell-drad: diameter identity is required\n");
        return -1;
    }

    if (ctx->diameter_realm[0] == '\0') {
        fprintf(stderr, "opncell-drad: diameter realm is required\n");
        return -1;
    }

    if (ctx->listen_address[0] == '\0') {
        fprintf(stderr, "opncell-drad: listen address is required\n");
        return -1;
    }

    if (ctx->listen_port == 0) {
        fprintf(stderr, "opncell-drad: listen port must be non-zero\n");
        return -1;
    }

    for (i = 0; i < ctx->peer_count; i++) {
        const dra_peer_t *peer = &ctx->peers[i];

        if (peer->name[0] == '\0' ||
            peer->group[0] == '\0' ||
            peer->identity[0] == '\0' ||
            peer->realm[0] == '\0' ||
            peer->address[0] == '\0' ||
            peer->port == 0) {
            fprintf(
                stderr,
                "opncell-drad: peer %u is incomplete or invalid\n",
                i);
            return -1;
        }
    }

    /*
     * Peer names are the stable configuration keys used during
     * reconciliation, so they must be unique.
     *
     * Diameter identities must also be unique because freeDiameter
     * maintains peers by Diameter Identity.
     */
    for (i = 0; i < ctx->peer_count; i++) {
        unsigned int j;

        for (j = i + 1; j < ctx->peer_count; j++) {
            if (strcmp(
                    ctx->peers[i].name,
                    ctx->peers[j].name) == 0) {
                fprintf(
                    stderr,
                    "opncell-drad: duplicate peer name %s\n",
                    ctx->peers[i].name);
                return -1;
            }

            if (strcmp(
                    ctx->peers[i].identity,
                    ctx->peers[j].identity) == 0) {
                fprintf(
                    stderr,
                    "opncell-drad: duplicate Diameter peer "
                    "identity %s\n",
                    ctx->peers[i].identity);
                return -1;
            }
        }
    }

    for (i = 0; i < ctx->route_count; i++) {
        const dra_route_t *route = &ctx->routes[i];

        if (route->name[0] == '\0' ||
            route->realm[0] == '\0' ||
            route->peer_group[0] == '\0' ||
            route->application_id == 0) {
            fprintf(
                stderr,
                "opncell-drad: route %u is incomplete or invalid\n",
                i);
            return -1;
        }

        if (!peer_group_exists(ctx, route->peer_group)) {
            fprintf(
                stderr,
                "opncell-drad: route %s references unknown peer group %s\n",
                route->name,
                route->peer_group);
            return -1;
        }
    }

    return 0;
}

static int
reconcile_peer_runtime(
    dra_context_t *next,
    const dra_context_t *current)
{
    unsigned int i;
    unsigned int j;

    next->peer_runtime_count = 0;

    for (i = 0; i < next->peer_count; i++) {
        dra_peer_runtime_t *runtime;

        if (dra_context_reserve_peer_runtime(
                next,
                next->peer_runtime_count + 1) != 0) {
            fprintf(stderr,
                "opncell-drad: failed to grow peer runtime store "
                "for peer %u\n",
                next->peer_runtime_count + 1);
            return -1;
        }

        runtime = &next->peer_runtime[next->peer_runtime_count];
        memset(runtime, 0, sizeof(*runtime));

        copy_string(
            runtime->name,
            sizeof(runtime->name),
            (const unsigned char *)next->peers[i].name);

        runtime->state = DRA_PEER_STATE_DOWN;

        if (current != NULL) {
            const dra_peer_t *old_peer;

            old_peer = dra_peer_find_by_name(
                current,
                next->peers[i].name);

            if (old_peer != NULL &&
                strcmp(old_peer->identity,
                    next->peers[i].identity) == 0 &&
                strcmp(old_peer->realm,
                    next->peers[i].realm) == 0 &&
                strcmp(old_peer->address,
                    next->peers[i].address) == 0 &&
                old_peer->port == next->peers[i].port &&
                old_peer->transport == next->peers[i].transport &&
                old_peer->enabled == next->peers[i].enabled) {

                for (j = 0;
                     j < current->peer_runtime_count;
                     j++) {
                    if (strcmp(
                            current->peer_runtime[j].name,
                            next->peers[i].name) == 0) {
                        runtime->state =
                            current->peer_runtime[j].state;
                        break;
                    }
                }
            }
        }


        next->peer_runtime_count++;
    }
    return 0;
}

static int
config_equal(
    const dra_context_t *a,
    const dra_context_t *b)
{
    unsigned int i;

    if (a == NULL || b == NULL)
        return 0;

    if (strcmp(a->diameter_identity, b->diameter_identity) != 0 ||
        strcmp(a->diameter_realm, b->diameter_realm) != 0 ||
        strcmp(a->listen_address, b->listen_address) != 0 ||
        a->listen_port != b->listen_port ||
        a->listen_transport != b->listen_transport ||
        a->peer_count != b->peer_count ||
        a->route_count != b->route_count)
        return 0;

    for (i = 0; i < a->peer_count; i++) {
        const dra_peer_t *pa = &a->peers[i];
        const dra_peer_t *pb = &b->peers[i];

        if (strcmp(pa->name, pb->name) != 0 ||
            strcmp(pa->group, pb->group) != 0 ||
            strcmp(pa->identity, pb->identity) != 0 ||
            strcmp(pa->realm, pb->realm) != 0 ||
            strcmp(pa->address, pb->address) != 0 ||
            pa->port != pb->port ||
            pa->transport != pb->transport ||
            pa->priority != pb->priority ||
            pa->enabled != pb->enabled)
            return 0;
    }

    for (i = 0; i < a->route_count; i++) {
        const dra_route_t *ra = &a->routes[i];
        const dra_route_t *rb = &b->routes[i];

        if (strcmp(ra->name, rb->name) != 0 ||
            strcmp(ra->realm, rb->realm) != 0 ||
            strcmp(ra->peer_group, rb->peer_group) != 0 ||
            ra->application_id != rb->application_id ||
            ra->priority != rb->priority ||
            ra->action != rb->action ||
            ra->enabled != rb->enabled)
            return 0;
    }

    return 1;
}

int
dra_provisioning_prepare(
    const dra_context_t *current,
    const char *path,
    dra_context_t *next)
{
    FILE *fp;
    yaml_parser_t parser;
    yaml_document_t document;
    yaml_node_t *root;
    yaml_node_t *diameter;
    yaml_node_t *peers;
    yaml_node_t *routes;
    int rc = -1;

    if (current == NULL || path == NULL || next == NULL)
        return -1;

    memset(next, 0, sizeof(*next));
    next->running = current->running;

    fp = fopen(path, "r");
    if (fp == NULL) {
        perror("opncell-drad: fopen");
        return -1;
    }

    if (!yaml_parser_initialize(&parser)) {
        fclose(fp);
        return -1;
    }

    yaml_parser_set_input_file(&parser, fp);

    if (!yaml_parser_load(&parser, &document)) {
        fprintf(
            stderr,
            "opncell-drad: YAML parse error at line %lu column %lu\n",
            (unsigned long)parser.problem_mark.line + 1,
            (unsigned long)parser.problem_mark.column + 1);
        goto out_parser;
    }

    root = yaml_document_get_root_node(&document);
    if (root == NULL || root->type != YAML_MAPPING_NODE) {
        fprintf(stderr, "opncell-drad: YAML root must be a mapping\n");
        goto out_document;
    }

    diameter = mapping_lookup(&document, root, "diameter");
    peers = mapping_lookup(&document, root, "peers");
    routes = mapping_lookup(&document, root, "routes");

    if (parse_diameter(next, &document, diameter) != 0)
        goto out_document;

    if (parse_peers(next, &document, peers) != 0)
        goto out_document;

    if (parse_routes(next, &document, routes) != 0)
        goto out_document;

    if (validate_config(next) != 0)
        goto out_document;

    if (reconcile_peer_runtime(next, current) != 0)
        goto out_document;

    if (config_equal(current, next))
        next->generation = current->generation;
    else
        next->generation = current->generation + 1;

    rc = 0;

out_document:
    yaml_document_delete(&document);

out_parser:
    yaml_parser_delete(&parser);
    fclose(fp);

    if (rc != 0)
        dra_context_reset(next);

    return rc;
}

int
dra_provisioning_commit(
    dra_context_t *ctx,
    const dra_context_t *next)
{
    if (ctx == NULL || next == NULL)
        return -1;

    if (dra_context_clone(ctx, next) != 0) {
        fprintf(stderr,
            "opncell-drad: failed to commit configuration context\n");
        return -1;
    }

    return 0;
}

int
dra_provisioning_load(
    dra_context_t *ctx,
    const char *path)
{
    dra_context_t next;
    int rc;

    if (ctx == NULL || path == NULL)
        return -1;

    if (dra_provisioning_prepare(ctx, path, &next) != 0)
        return -1;

    rc = dra_provisioning_commit(ctx, &next);

    /*
     * ctx owns its own deep copy after a successful commit.
     * Always release the temporary candidate.
     */
    dra_context_reset(&next);

    if (rc != 0)
        return -1;

    printf(
        "opncell-drad: configuration generation %" PRIu64
        " loaded from %s\n",
        ctx->generation,
        path);

    printf(
        "opncell-drad: diameter identity=%s realm=%s listen=%s:%u\n",
        ctx->diameter_identity,
        ctx->diameter_realm,
        ctx->listen_address,
        ctx->listen_port);

    printf(
        "opncell-drad: loaded %u roaming peers and %u routes\n",
        ctx->peer_count,
        ctx->route_count);

    return 0;
}

int
dra_provisioning_reload(
    dra_context_t *ctx,
    const char *path)
{
    if (ctx == NULL || path == NULL)
        return -1;

    printf("opncell-drad: provisioning reload requested\n");

    return dra_provisioning_load(ctx, path);
}