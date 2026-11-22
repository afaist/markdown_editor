/* ld_preload_gio.c — перехватывает g_module_open, чтобы предотвратить
 * загрузку libgvfsdbus.so и других GIO-модулей с несовместимыми символами GLib.
 *
 * GIO модули загружаются через g_module_open() (GLib API).
 * Возвращаем специальный "заблокированный" указатель, который
 * g_module_symbol/g_module_close распознают как безопасный для игнорирования.
 *
 * Собирается: gcc -shared -fPIC -o libgio_preload.so ld_preload_gio.c -ldl
 * Запускается: LD_PRELOAD=./libgio_preload.so ./markdown-editor.bin
 */

#define _GNU_SOURCE
#include <dlfcn.h>
#include <string.h>

/* Специальный указатель, обозначающий "заблокированный модуль" */
static const char g_blocked_module_marker = 0;

typedef void* (*orig_g_module_open_t)(const char*, int);
static orig_g_module_open_t orig_g_module_open = NULL;

typedef int (*orig_g_module_symbol_t)(void*, const char*, void**);
static orig_g_module_symbol_t orig_g_module_symbol = NULL;

typedef void (*orig_g_module_close_t)(void*);
static orig_g_module_close_t orig_g_module_close = NULL;

__attribute__((constructor))
static void init_preload(void) {
    orig_g_module_open = (orig_g_module_open_t)dlsym(RTLD_NEXT, "g_module_open");
    orig_g_module_symbol = (orig_g_module_symbol_t)dlsym(RTLD_NEXT, "g_module_symbol");
    orig_g_module_close = (orig_g_module_close_t)dlsym(RTLD_NEXT, "g_module_close");
}

/* Проверяет, является ли указатель "заблокированным модулем" */
static int is_blocked_module(void* module) {
    return module == (void*)&g_blocked_module_marker;
}

void* g_module_open(const char* filename, int flags) {
    if (!filename)
        return orig_g_module_open ? orig_g_module_open(filename, flags) : NULL;

    /* Блокируем загрузку GIO-модулей и GVFS */
    if (strstr(filename, "gio/modules") ||
        strstr(filename, "libgvfs") ||
        strstr(filename, "libgioremote") ||
        strstr(filename, "libdconfsettings")) {
        /* Возвращаем специальный указатель, который g_module_symbol/g_module_close
         * распознают как безопасный для игнорирования */
        return (void*)&g_blocked_module_marker;
    }

    return orig_g_module_open ? orig_g_module_open(filename, flags) : NULL;
}

int g_module_symbol(void* module, const char* symbol, void** result) {
    if (is_blocked_module(module))
        return 0; /* Игнорируем запросы к заблокированным модулям */
    return orig_g_module_symbol ? orig_g_module_symbol(module, symbol, result) : 0;
}

void g_module_close(void* module) {
    if (is_blocked_module(module))
        return; /* Игнорируем закрытие заблокированных модулей */
    if (orig_g_module_close)
        orig_g_module_close(module);
}
