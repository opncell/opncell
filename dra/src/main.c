#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <unistd.h>

#include "dra-context.h"
#include "provisioning.h"

static volatile sig_atomic_t shutdown_requested = 0;
static volatile sig_atomic_t reload_requested = 0;

static void
signal_handler(int signo)
{
    switch (signo) {
    case SIGHUP:
        reload_requested = 1;
        break;

    case SIGINT:
    case SIGTERM:
        shutdown_requested = 1;
        break;

    default:
        break;
    }
}

static int
install_signal_handlers(void)
{
    struct sigaction sa;

    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;
    sa.sa_handler = signal_handler;

    if (sigaction(SIGHUP, &sa, NULL) == -1)
        return -1;

    if (sigaction(SIGINT, &sa, NULL) == -1)
        return -1;

    if (sigaction(SIGTERM, &sa, NULL) == -1)
        return -1;

    return 0;
}

int
main(int argc, char *argv[])
{
    dra_context_t ctx;
    const char *config_path = "/usr/local/etc/opncell/dra.yaml";

    if (argc > 1)
        config_path = argv[1];

    printf("opncell-drad: starting\n");

    if (dra_context_init(&ctx) != 0) {
        fprintf(stderr, "opncell-drad: failed to initialize context\n");
        return EXIT_FAILURE;
    }

    if (install_signal_handlers() != 0) {
        perror("opncell-drad: sigaction");
        dra_context_final(&ctx);
        return EXIT_FAILURE;
    }

    if (dra_provisioning_load(&ctx, config_path) != 0) {
        fprintf(stderr, "opncell-drad: failed to load configuration\n");
        dra_context_final(&ctx);
        return EXIT_FAILURE;
    }

    printf("opncell-drad: ready\n");

    while (!shutdown_requested) {
        if (reload_requested) {
            reload_requested = 0;

            if (dra_provisioning_reload(&ctx, config_path) != 0)
                fprintf(stderr, "opncell-drad: reload failed\n");
        }

        sleep(1);
    }

    printf("opncell-drad: shutdown requested\n");

    dra_context_final(&ctx);

    printf("opncell-drad: terminated\n");

    return EXIT_SUCCESS;
}
