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

        if (ctx->peer_count >= DRA_MAX_PEERS) {
            fprintf(stderr, "opncell-drad: too many configured peers\n");
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

        if (ctx->route_count >= DRA_MAX_ROUTES) {
            fprintf(stderr, "opncell-drad: too many configured routes\n");
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

        node = mapping_lookup(document, entry, "peer");
        if (node != NULL && node->type == YAML_SCALAR_NODE)
            copy_string(route->peer, sizeof(route->peer),
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
peer_exists(const dra_context_t *ctx, const char *name)
{
    unsigned int i;

    if (ctx == NULL || name == NULL || name[0] == '\0')
        return 0;

    for (i = 0; i < ctx->peer_count; i++) {
        if (strcmp(ctx->peers[i].name, name) == 0)
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

    for (i = 0; i < ctx->route_count; i++) {
        const dra_route_t *route = &ctx->routes[i];

        if (route->name[0] == '\0' ||
            route->realm[0] == '\0' ||
            route->peer[0] == '\0' ||
            route->application_id == 0) {
            fprintf(
                stderr,
                "opncell-drad: route %u is incomplete or invalid\n",
                i);
            return -1;
        }

        if (!peer_exists(ctx, route->peer)) {
            fprintf(
                stderr,
                "opncell-drad: route %s references unknown peer %s\n",
                route->name,
                route->peer);
            return -1;
        }
    }

    return 0;
}

int
dra_provisioning_load(dra_context_t *ctx, const char *path)
{
    FILE *fp;
    yaml_parser_t parser;
    yaml_document_t document;
    yaml_node_t *root;
    yaml_node_t *diameter;
    yaml_node_t *peers;
    yaml_node_t *routes;
    dra_context_t next;
    int rc = -1;

    if (ctx == NULL || path == NULL)
        return -1;
    memset(&next, 0, sizeof(next));
    next.running = ctx->running;
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

    if (parse_diameter(&next, &document, diameter) != 0)
        goto out_document;

    if (parse_peers(&next, &document, peers) != 0)
        goto out_document;

    if (parse_routes(&next, &document, routes) != 0)
        goto out_document;

    if (validate_config(&next) != 0)
        goto out_document;

    next.generation = ctx->generation + 1;
    *ctx = next;

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

    rc = 0;

out_document:
    yaml_document_delete(&document);

out_parser:
    yaml_parser_delete(&parser);
    fclose(fp);

    return rc;
}

int
dra_provisioning_reload(dra_context_t *ctx, const char *path)
{
    if (ctx == NULL || path == NULL)
        return -1;

    printf("opncell-drad: provisioning reload requested\n");

    return dra_provisioning_load(ctx, path);
}
