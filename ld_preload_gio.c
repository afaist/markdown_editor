/* ld_preload_gio.c — перехватывает dlopen GIO-модулей, чтобы предотвратить
 * загрузку libgvfsdbus.so с несовместимыми символами GLib.
 *
 * Собирается: gcc -shared -fPIC -o libgio_preload.so ld_preload_gio.c -ldl
 * Запускается: LD_PRELOAD=./libgio_preload.so ./markdown-editor.bin
 */

#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

typedef void *(*orig_dlopen_t)(const char *, int);

void *dlopen(const char *filename, int flags) {
    static orig_dlopen_t orig_dlopen = NULL;
    if (!orig_dlopen)
        orig_dlopen = (orig_dlopen_t)dlsym(RTLD_NEXT, "dlopen");

    /* Не блокируем загрузку, если filename NULL (RTLD_NOW и т.д.) */
    if (!filename)
        return orig_dlopen(filename, flags);

    /* Блокируем загрузку GIO-модулей и GVFS */
    if (strstr(filename, "gio/modules") ||
        strstr(filename, "libgvfs") ||
        strstr(filename, "libgvfscommon")) {
        return NULL;
    }

    return orig_dlopen(filename, flags);
}
