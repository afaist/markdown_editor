/* ld_preload_gio.c — перехватывает g_module_open, чтобы предотвратить
 * загрузку libgvfsdbus.so и других GIO-модулей с несовместимыми символами GLib.
 *
 * GIO модули загружаются через g_module_open() (GLib API), а не dlopen().
 *
 * Собирается: gcc -shared -fPIC -o libgio_preload.so ld_preload_gio.c -ldl
 * Запускается: LD_PRELOAD=./libgio_preload.so ./markdown-editor.bin
 */

#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

typedef void *(*orig_g_module_open_t)(const char *, int);

void *g_module_open(const char *filename, int flags) {
    static orig_g_module_open_t orig_g_module_open = NULL;
    if (!orig_g_module_open)
        orig_g_module_open = (orig_g_module_open_t)dlsym(RTLD_NEXT, "g_module_open");

    if (!filename)
        return orig_g_module_open(filename, flags);

    /* Блокируем загрузку GIO-модулей и GVFS */
    if (strstr(filename, "gio/modules") ||
        strstr(filename, "libgvfs") ||
        strstr(filename, "libgioremote") ||
        strstr(filename, "libdconfsettings")) {
        return NULL;
    }

    return orig_g_module_open(filename, flags);
}
