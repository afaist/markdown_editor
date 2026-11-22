/* ld_preload_gio.c — перехватывает dlopen, чтобы предотвратить
 * загрузку libgvfsdbus.so и других GIO-модулей с несовместимыми символами GLib.
 *
 * GIO модули загружаются через g_module_open(), который внутри вызывает dlopen().
 * Перехватываем dlopen и блокируем загрузку GIO/GVFS библиотек.
 *
 * Собирается: gcc -shared -fPIC -o libgio_preload.so ld_preload_gio.c -ldl
 * Запускается: LD_PRELOAD=./libgio_preload.so ./markdown-editor.bin
 */

#define _GNU_SOURCE
#include <dlfcn.h>
#include <string.h>
#include <stdio.h>

static int g_initialized = 0;
static void *(*orig_dlopen)(const char *, int);

__attribute__((constructor))
static void init_preload(void) {
    orig_dlopen = dlsym(RTLD_NEXT, "dlopen");
    g_initialized = 1;
}

void *dlopen(const char *filename, int flags) {
    if (!g_initialized || !orig_dlopen || !filename) {
        return (g_initialized && orig_dlopen) ? orig_dlopen(filename, flags) : NULL;
    }

    /* Блокируем загрузку GIO-модулей и GVFS */
    if (strstr(filename, "gio/modules") ||
        strstr(filename, "libgvfs") ||
        strstr(filename, "libgioremote") ||
        strstr(filename, "libdconfsettings")) {
        return NULL;
    }

    return orig_dlopen(filename, flags);
}
