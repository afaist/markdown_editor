/* ld_preload_gio.c — перехватывает g_module_open, чтобы предотвратить
 * загрузку libgvfsdbus.so и других GIO-модулей с несовместимыми символами GLib.
 *
 * GIO модули загружаются через g_module_open() (GLib API).
 * Используем void* для совместимости с разными версиями GLib.
 *
 * Собирается: gcc -shared -fPIC -o libgio_preload.so ld_preload_gio.c -ldl
 * Запускается: LD_PRELOAD=./libgio_preload.so ./markdown-editor.bin
 */

#define _GNU_SOURCE
#include <dlfcn.h>
#include <string.h>

typedef void* (*orig_g_module_open_t)(const char*, int);
static orig_g_module_open_t orig_g_module_open = NULL;

__attribute__((constructor))
static void init_preload(void) {
    orig_g_module_open = (orig_g_module_open_t)dlsym(RTLD_NEXT, "g_module_open");
}

void* g_module_open(const char* filename, int flags) {
    if (!filename)
        return orig_g_module_open ? orig_g_module_open(filename, flags) : NULL;

    /* Блокируем загрузку GIO-модулей и GVFS */
    if (strstr(filename, "gio/modules") ||
        strstr(filename, "libgvfs") ||
        strstr(filename, "libgioremote") ||
        strstr(filename, "libdconfsettings")) {
        return NULL;
    }

    return orig_g_module_open ? orig_g_module_open(filename, flags) : NULL;
}
