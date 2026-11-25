/* ld_preload_gio.c — перехватывает загрузку GIO/GVFS модулей
 *
 * Блокирует загрузку libgvfsdbus.so, libgvfscommon.so и других GIO-модулей через:
 *   1. dlopen/dlsym/dlclose — для прямого динамического линкинга
 *   2. g_module_open/g_module_symbol/g_module_close — для GLib API
 *   3. g_io_modules_load_all_in_directory — загрузка всех модулей из директории
 *   4. g_io_module_load — загрузка конкретного модуля
 *
 * Проблема: системный libgvfsdbus.so и libgvfscommon.so требуют glib 2.80+
 * (g_variant_builder_init_static), но запускаются на системах со старым glib.
 *
 * Собирается: gcc -shared -fPIC -o libgio_preload.so ld_preload_gio.c -ldl
 */

#define _GNU_SOURCE
#include <dlfcn.h>
#include <string.h>
#include <stdio.h>
#include <dirent.h>

/* ─── Маркер "заблокированного модуля" ─── */
static const char g_blocked_module_marker = 0;

/* ─── Функции оригинального GLib ─── */
typedef void* (*orig_g_module_open_t)(const char*, int);
static orig_g_module_open_t orig_g_module_open = NULL;

typedef int (*orig_g_module_symbol_t)(void*, const char*, void**);
static orig_g_module_symbol_t orig_g_module_symbol = NULL;

typedef void (*orig_g_module_close_t)(void*);
static orig_g_module_close_t orig_g_module_close = NULL;

typedef void (*orig_g_io_modules_load_all_in_directory_t)(const char*, void*);
static orig_g_io_modules_load_all_in_directory_t orig_g_io_modules_load_all_in_directory = NULL;

typedef void (*orig_g_io_module_load_t)(void*);
static orig_g_io_module_load_t orig_g_io_module_load = NULL;

/* ─── Проверка, нужно ли блокировать загрузку ─── */
static int should_block_module(const char* filename) {
    if (!filename)
        return 0;

    /* Блокируем GIO-модули, GVFS, D-Bus settings */
    if (strstr(filename, "gio/modules")       ||
        strstr(filename, "libgvfs")            ||
        strstr(filename, "libgioremote")       ||
        strstr(filename, "libdconfsettings")   ||
        strstr(filename, "libgvfsdbus")) {
        return 1;
    }
    return 0;
}

/* ─── Проверка, является ли указатель "заблокированным модулем" ─── */
static int is_blocked_module(void* module) {
    return module == (void*)&g_blocked_module_marker;
}

/* ─── Конструктор: сохраняем оригинальные функции ─── */
__attribute__((constructor))
static void init_preload(void) {
    orig_g_module_open  = (orig_g_module_open_t)dlsym(RTLD_NEXT, "g_module_open");
    orig_g_module_symbol = (orig_g_module_symbol_t)dlsym(RTLD_NEXT, "g_module_symbol");
    orig_g_module_close = (orig_g_module_close_t)dlsym(RTLD_NEXT, "g_module_close");
    orig_g_io_modules_load_all_in_directory = (orig_g_io_modules_load_all_in_directory_t)dlsym(RTLD_NEXT, "g_io_modules_load_all_in_directory");
    orig_g_io_module_load = (orig_g_io_module_load_t)dlsym(RTLD_NEXT, "g_io_module_load");
}

/* ═══════════════════════════════════════════════════════════
 * Перехват dlopen/dlsym/dlclose — для прямого линкинга
 * ═══════════════════════════════════════════════════════════ */

void* dlopen(const char* filename, int flags) {
    static void* (*orig_dlopen)(const char*, int) = NULL;
    if (!orig_dlopen)
        orig_dlopen = (void*(*)(const char*, int))dlsym(RTLD_NEXT, "dlopen");

    if (should_block_module(filename)) {
        return NULL;
    }
    return orig_dlopen(filename, flags);
}

void* dlsym(void* handle, const char* symbol) {
    static void* (*orig_dlsym)(void*, const char*) = NULL;
    if (!orig_dlsym)
        orig_dlsym = (void*(*)(void*, const char*))dlsym(RTLD_NEXT, "dlsym");

    if (is_blocked_module(handle))
        return NULL;

    return orig_dlsym(handle, symbol);
}

int dlclose(void* handle) {
    static int (*orig_dlclose)(void*) = NULL;
    if (!orig_dlclose)
        orig_dlclose = (int(*)(void*))dlsym(RTLD_NEXT, "dlclose");

    if (is_blocked_module(handle))
        return 0;

    return orig_dlclose(handle);
}

/* ═══════════════════════════════════════════════════════════
 * Перехват g_module_open/g_module_symbol/g_module_close
 * ═══════════════════════════════════════════════════════════ */

void* g_module_open(const char* filename, int flags) {
    if (!filename)
        return orig_g_module_open ? orig_g_module_open(filename, flags) : NULL;

    if (should_block_module(filename)) {
        return (void*)&g_blocked_module_marker;
    }

    return orig_g_module_open ? orig_g_module_open(filename, flags) : NULL;
}

int g_module_symbol(void* module, const char* symbol, void** result) {
    if (is_blocked_module(module))
        return 0;
    return orig_g_module_symbol ? orig_g_module_symbol(module, symbol, result) : 0;
}

void g_module_close(void* module) {
    if (is_blocked_module(module))
        return;
    if (orig_g_module_close)
        orig_g_module_close(module);
}

/* ═══════════════════════════════════════════════════════════
 * Перехват g_io_modules_load_all_in_directory
 * — блокирует загрузку всех GIO-модулей из директории
 * ═══════════════════════════════════════════════════════════ */

void g_io_modules_load_all_in_directory(const char* directory, void* error) {
    /* Игнорируем — не загружаем ни один GIO-модуль из директории */
    (void)directory;
    (void)error;
}

/* ═══════════════════════════════════════════════════════════
 * Перехват g_io_module_load
 * ═══════════════════════════════════════════════════════════ */

void g_io_module_load(void* module) {
    if (is_blocked_module(module))
        return;
    if (orig_g_io_module_load)
        orig_g_io_module_load(module);
}
