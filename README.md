# Markdown Editor (PyQt6)

Простой и функциональный редактор Markdown с предпросмотром в реальном времени и поддержкой LaTeX-формул.

## 📋 Описание

Markdown Editor — это desktop-приложение для создания и редактирования документов в формате Markdown с мгновенным предпросмотром. Поддерживает встроенные и блочные LaTeX-формулы через библиотеку KaTeX, несколько тем оформления, экспорт в HTML и PDF, GitHub Callouts, зачёркнутый текст, списки задач и множество инструментов форматирования.

**Версия:** 1.0  
**Технологии:** Python 3.8+, PyQt6, QtWebEngine, KaTeX, Python-Markdown, Prism.js

## ✨ Особенности

- ✏️ **Редактор Markdown** — удобный текстовый редактор на базе QTextEdit с поддержкой форматирования
- 👀 **Предпросмотр в реальном времени** — автоматическое обновление HTML-предпросмотра при вводе текста (с задержкой 300 мс)
- 📐 **LaTeX-формулы** — поддержка встроенных (`$...$`) и блочных (`$$...$$`) формул через KaTeX
- 📤 **Экспорт** — сохранение в HTML и PDF форматы с настраиваемыми колонтитулами
- 🖼️ **Изображения** — вставка изображений через диалог выбора файла
- 🎨 **Темы оформления** — три темы для предпросмотра и три темы для редактора (светлая, тёмная, контрастная)
- 💾 **Автосохранение** — автоматическое сохранение файла каждые 3 секунды после изменений
- 🔍 **Поиск и замена** — диалоговое окно для поиска и замены текста
- 📊 **Статистика** — счётчики символов и слов в строке состояния
- 📁 **Управление файлами** — создание, открытие, сохранение, сохранение как, закрытие
- 📝 **Поддержка расширений Markdown** — fenced code blocks, syntax highlighting (Prism.js), таблицы, оглавление
- 📌 **GitHub Callouts** — поддержка блоков `> [!note]`, `> [!tip]`, `> [!important]`, `> [!warning]`, `> [!caution]`
- ~~ ~~ **Зачёркнутый текст** — поддержка `~~текст~~`
- 💿 **Последняя сессия** — автоматическая загрузка последнего открытого файла при старте
- 🔤 **Настройка шрифта** — выбор шрифта из списка, изменение размера (+/−), сброс к значениям по умолчанию
- 📋 **Списки задач** — поддержка `<input type="checkbox">` через `- [ ]`
- 🧮 **Шаблоны LaTeX** — быстрая вставка дробей, корней, интегралов, сумм, матриц и т.д.
- 📊 **Вставка таблиц** — генерация шаблона таблицы Markdown 3×3
- 📝 **Блоки кода по языкам** — быстрые шаблоны для Python, Bash, Markdown, C++, Rust

## 🚀 Установка

### Требования

- Python 3.8 или выше
- pip (менеджер пакетов Python)
- Операционная система: Linux / macOS / Windows

### Шаги установки

1. **Клонируйте репозиторий** (или скачайте файлы):

```bash
git clone <url-репозитория>
cd markdown_editor
```

1. **Создайте виртуальное окружение** (рекомендуется):

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# или
venv\Scripts\activate     # Windows
```

1. **Установите зависимости**:

```bash
pip install -r requirements.txt
```

1. **Запустите приложение**:

```bash
python main.py
```

## 📖 Использование

### Основные функции

#### Редактирование текста

Введите текст в левой панели (**Редактор Markdown**). Предпросмотр в правой панели обновляется автоматически при изменении текста.

#### Панель инструментов

| Кнопка | Действие |
| -------- | ---------- |
| Заголовок 1 | Вставляет `#` (заголовок H1) |
| Заголовок 2 | Вставляет `##` (заголовок H2) |
| Жирный | Обернёт выделение в `**...**` |
| Курсив | Обернёт выделение в `*...*` |
| Список | Вставляет маркированный список |
| Цитата | Вставляет `>` (блок цитаты) |
| Код | Вставляет блок кода с тройными бэккиками |
| LaTeX inline | Вставляет `$` для встроенных формул |
| LaTeX block | Вставляет `$$\n$$` для блочных формул |
| Ссылка | Открывает диалог для вставки ссылки |
| Изображение | Открывает диалог выбора файла изображения |
| Тема | Циклическое переключение темы предпросмотра |
| Тема редактора | Циклическое переключение темы редактора |
| Открыть | Открывает диалог выбора файла |
| Сохранить | Сохраняет текущий файл |
| Экспорт в PDF | Экспортирует документ в PDF |
| Выбор шрифта | Комбобокс выбора шрифта (Consolas, Courier New, Fira Code и др.) |
| Размер +/− | Увеличение/уменьшение размера шрифта |
| Сбросить шрифт | Сброс шрифта и размера к значениям по умолчанию |

#### Меню Markdown

В меню **Markdown** доступны все инструменты форматирования с горячими клавишами:

**Заголовки** (`Ctrl+Shift+1`–`8`):

- Заголовки H1–H7

**Стили**:

- **Жирный** (`Ctrl+B`)
- *Курсив* (`Ctrl+I`)
- ~~Зачёркнутый~~ (`Ctrl+Shift+X`)
- `Встроенный код` (`Ctrl+``)

**Списки**:

- Маркированный (`Ctrl+Shift+U`)
- Нумерованный (`Ctrl+Shift+O`)
- Список задач (`Ctrl+Shift+T`)

**Цитата** (`Ctrl+Shift+Q`)

**Код**:

- Python (`Ctrl+Shift+C`)
- Bash (`Ctrl+Shift+B`)
- Markdown (`Ctrl+Shift+M`)
- C++ (`Ctrl+Shift+P`)
- Rust (`Ctrl+Shift+R`)

**LaTeX**:

- Встроенная `($...$)` (`Ctrl+L`)
- Блочная (`$$...$$`) (`Ctrl+Shift+L`)
- Дробь `\frac` (`Ctrl+Shift+F`)
- Квадратный корень `\sqrt` (`Ctrl+Shift+R`)
- Надстрочный (`Ctrl+Shift+S`)
- Подстрочный (`Ctrl+Shift+N`)
- Сумма `\sum` (`Ctrl+Shift+A`)
- Интеграл `\int` (`Ctrl+Shift+G`)
- Матрица `\begin{matrix}` (`Ctrl+Shift+M`)

**Дополнительно**:

- Разделитель (`---`) (`Ctrl+Shift+H`)
- Таблица (`Ctrl+Shift+Tab`)
- HTML-комментарий (`Ctrl+Shift+/`)

#### Меню

**Файл:**

- Новый (`Ctrl + N`)
- Открыть (`Ctrl + O`)
- Сохранить (`Ctrl + S`)
- Сохранить как...
- Закрыть (`Ctrl + W`)
- Экспорт в HTML
- Экспорт в PDF
- Настройки PDF-экспорта...
- Выход (`Ctrl + Q`)

**Правка:**

- Отменить (`Ctrl + Z`)
- Повторить (`Ctrl + Y`)
- Вырезать / Копировать / Вставить
- Найти и заменить (`Ctrl + F`)
- Вставить изображение...

**Вид:**

- Обновить предпросмотр
- Тема: светлая / тёмная / контрастная
- Тема редактора: светлая / тёмная / контрастная
- Увеличить шрифт (`Ctrl + +`)
- Уменьшить шрифт (`Ctrl + -`)
- Сбросить шрифт (`Ctrl + 0`)

**Справка:**

- О программе

#### Экспорт

- **Экспорт в HTML**: меню **Файл → Экспорт в HTML**
- **Экспорт в PDF**: кнопка **Экспорт в PDF** на панели инструментов или меню **Файл → Экспорт в PDF**
- **Настройки PDF-экспорта**: меню **Файл → Настройки PDF-экспорта** — включение/отключение колонтитулов, текст верхнего и нижнего колонтитулов, автоматическая нумерация страниц

### Горячие клавиши

| Клавиши | Действие |
| --------- | ---------- |
| `Ctrl + N` | Новый файл |
| `Ctrl + O` | Открыть файл |
| `Ctrl + S` | Сохранить |
| `Ctrl + W` | Закрыть файл |
| `Ctrl + F` | Найти и заменить |
| `Ctrl + Z` | Отменить |
| `Ctrl + Y` | Повторить |
| `Ctrl + Q` | Выход |
| `Ctrl + B` | Жирный |
| `Ctrl + I` | Курсив |
| `Ctrl + L` | Встроенная LaTeX |
| `Ctrl + Shift + L` | Блочная LaTeX |
| `Ctrl + Shift + 1..7` | Заголовки H1–H7 |
| `Ctrl + Shift + X` | Зачёркнутый текст |
| `Ctrl + +` | Увеличить шрифт |
| `Ctrl + -` | Уменьшить шрифт |
| `Ctrl + 0` | Сбросить шрифт |

## 🏗️ Архитектура

### Структура проекта

```text
markdown_editor/
├── main.py                      # Точка входа
├── markdown_editor_pkg/         # Основной пакет приложения
│   ├── __init__.py              # Экспорт MarkdownEditorPyQt
│   ├── editor.py                # Главный класс MarkdownEditorPyQt (обёртка)
│   ├── editor_components.py     # UIBuilder, ToolbarBuilder, MenuBuilder
│   ├── editor_events.py         # EventHandler — обработчики событий
│   ├── editor_find.py           # FindReplaceHandler — поиск и замена
│   ├── editor_help.py           # HelpHandler — справочная информация
│   ├── editor_keypress.py       # MarkdownTextEdit — кастомный QTextEdit
│   ├── editor_markdown_menu.py  # MarkdownMenuBuilder — меню форматирования
│   ├── editor_pdf.py            # PDFHandler — обработка PDF‑экспорта
│   ├── editor_session.py        # SessionHandler — сохранение/загрузка сессии
│   ├── editor_themes.py         # ThemeFontHandler — управление шрифтами
│   ├── editor_close.py          # CloseHandler — обработка закрытия окна
│   ├── themes.py                  # CSS‑темы предпросмотра и QSS‑темы редактора
│   ├── markdown_renderer.py     # MarkdownRenderer — конвертация Markdown → HTML
│   ├── latex_processor.py       # LaTeXProcessor — обработка LaTeX‑формул
│   ├── callout_processor.py     # CalloutProcessor — GitHub Callouts
│   ├── prism_processor.py       # PrismJSProcessor — подсветка синтаксиса
│   ├── text_insertions.py       # TextInsertions — вставка форматирования
│   ├── file_operations.py       # FileIO, FileExport, EditorState
│   ├── find_replace.py          # FindReplaceDialog — диалог поиска
│   ├── session_manager.py       # SessionManager — менеджмент сессий
│   ├── header_footer_dialog.py  # HeaderFooterDialog — колонтитулы PDF
│   ├── download_katex.py        # Скрипт для загрузки KaTeX
│   ├── download_prism.py        # Скрипт для загрузки Prism.js
│   ├── katex/                   # Библиотека KaTeX
│   │   ├── katex.min.css
│   │   ├── katex.min.js
│   │   └── auto-render.min.js
│   └── prism/                   # Prism.js для подсветки синтаксиса
│       ├── prism.min.js
│       ├── components/          # Локализации языков
│       │   ├── prism-bash.min.js
│       │   ├── prism-c.min.js
│       │   ├── prism-cpp.min.js
│       │   ├── prism-css.min.js
│       │   ├── prism-java.min.js
│       │   ├── prism-javascript.min.js
│       │   ├── prism-markup.min.js
│       │   ├── prism-python.min.js
│       │   ├── prism-sql.min.js
│       │   └── prism-typescript.min.js
│       └── themes/              # CSS‑темы Prism
│           ├── prism-okaidia.min.css
│           └── prism-tomorrow.min.css
├── tests/                       # Юнит‑тесты (pytest)
│   ├── conftest.py              # Настройка pytest (Qt headless)
│   └── test_*.py                # Тесты компонентов
├── requirements.txt             # Зависимости Python
├── pyproject.toml               # Конфигурация pytest и mypy
├── README.md                    # Этот файл
└── venv/                        # Виртуальное окружение
```

### Компоненты

1. **MarkdownEditorPyQt** (`editor.py`) — основной класс, наследник `QMainWindow`, обёртка, собирающая компоненты и делегирующая им работу.
2. **UIBuilder** (`editor_components.py`) — создание основного UI: сплиттер, редактор, предпросмотр, статусбар.
3. **ToolbarBuilder** (`editor_components.py`) — создание панели инструментов.
4. **MenuBuilder** (`editor_components.py`) — создание меню (Файл, Правка, Вид, Справка).
5. **MarkdownMenuBuilder** (`editor_markdown_menu.py`) — меню форматирования Markdown с горячими клавишами.
6. **EventHandler** (`editor_events.py`) — обработчики событий: `textChanged`, обновление предпросмотра, статус.
7. **ThemesManager** (`themes.py`) — управление CSS‑темами предпросмотра, QSS‑темами редактора, шрифтами и размером шрифта.
8. **ThemeFontHandler** (`editor_themes.py`) — обработчик тем и шрифтов.
9. **MarkdownRenderer** (`markdown_renderer.py`) — конвертация Markdown → HTML с LaTeX, темами, Callouts и подсветкой кода.
10. **LaTeXProcessor** (`latex_processor.py`) — извлечение LaTeX‑формул, замена плейсхолдерами, восстановление.
11. **CalloutProcessor** (`callout_processor.py`) — обработка GitHub Callouts из blockquote.
12. **PrismJSProcessor** (`prism_processor.py`) — интеграция Prism.js для подсветки кода.
13. **FileIO / FileExport** (`file_operations.py`) — открытие, сохранение, экспорт HTML/PDF. `EditorState` — единый контекст состояния файлов.
14. **TextInsertions** (`text_insertions.py`) — вставка форматированного текста (заголовки, стили, списки, LaTeX, таблицы и т. д.).
15. **FindReplaceHandler** (`editor_find.py`) — диалог «Найти и заменить».
16. **FindReplaceDialog** (`find_replace.py`) — диалог поиска и замены (для обратной совместимости).
17. **SessionHandler** (`editor_session.py`) — сохранение/загрузка последней сессии.
18. **SessionManager** (`session_manager.py`) — менеджмент сессий.
19. **PDFHandler** (`editor_pdf.py`) — обработка PDF‑экспорта.
20. **HelpHandler** (`editor_help.py`) — справочная информация (О программе).
21. **CloseHandler** (`editor_close.py`) — обработка закрытия окна.
22. **MarkdownTextEdit** (`editor_keypress.py`) — кастомный `QTextEdit` с кастомными клавиатурными обработками.
23. **HeaderFooterDialog** (`header_footer_dialog.py`) — диалог настроек PDF‑колонтитулов.
24. **Редактор** — `QTextEdit` (`MarkdownTextEdit`) с подсветкой текущей темы.
25. **Предпросмотр** — `QWebEngineView` для отображения HTML.
26. **Экспорт** — `export_to_pdf()` использует `QWebEngineView.page().printToPdf()` для генерации PDF.

### Используемые расширения Markdown

- `fenced_code` — блоки кода с тройными бэккиками
- **Prism.js** — подсветка синтаксиса в блоках кода (подключается через JavaScript в предпросмотре)
- `tables` — Markdown-таблицы
- `toc` — автоматическое оглавление

### Подсветка синтаксиса

Подсветка кода реализована через **Prism.js** — клиентскую библиотеку на JavaScript. Это обеспечивает:

- Динамическое переключение цветов подсветки при смене темы (светлая/тёмная/контрастная)
- Поддержку языков: Python, Java, C, C++, JavaScript, TypeScript, Bash, SQL, CSS, HTML
- Автоматическое определение языка по классу `language-xxx` в блоке кода
- Быструю работу без серверной обработки

Для переключения тем используются CSS-темы Prism.js:

- **Светлая тема** — `prism-okaidia.min.css`
- **Тёмная тема** — `prism-tomorrow.min.css`
- **Контрастная тема** — `prism-okaidia.min.css` (fallback)

Все ресурсы Prism.js загружаются скриптом `download_prism.py` в папку `markdown_editor_pkg/prism/`.

## 📦 Зависимости

| Пакет | Назначение |
| ------- | ----------- |
| `PyQt6>=6.6.0` | GUI-фреймворк |
| `PyQt6-WebEngine>=6.6.0` | `QWebEngineView` для предпросмотра и экспорта в PDF |
| `markdown>=3.4.0` | Конвертация Markdown в HTML |

## 🧪 Разработка

### Запуск тестов

```bash
# Через unittest
python test_markdown_editor.py

# Через pytest
python3 -m pytest test_markdown_editor.py -v

# Быстрый тестовый скрипт
python test_runner.py
```

> **Примечание:** Для тестирования используется `QT_QPA_PLATFORM=offscreen`, чтобы запускать Qt без графической оболочки.

### Настройка тестов

Конфигурация pytest находится в файле `conftest.py` — создаётся единый экземпляр `QApplication` для всех тестов.

## 🛠️ Решение проблем

| Проблема | Решение |
| ---------- | --------- |
| Модуль PyQt6 не найден | `pip install PyQt6 PyQt6-WebEngine` |
| LaTeX-формулы не отображаются | Проверьте наличие файлов в папке `markdown_editor_pkg/katex/` (`katex.min.css`, `katex.min.js`, `auto-render.min.js`) |
| Ошибка при экспорте в PDF | Убедитесь, что `PyQt6-WebEngine` установлен |
| Предпросмотр не обновляется | Проверьте, что JavaScript KaTeX загружен корректно |
| Подсветка синтаксиса не работает | Проверьте наличие файлов в папке `markdown_editor_pkg/prism/` |

### Загрузка ресурсов

Если файлы KaTeX или Prism.js отсутствуют, запустите соответствующие скрипты:

```bash
# Загрузка KaTeX (Python, загружает в markdown_editor_pkg/katex/)
python markdown_editor_pkg/download_katex.py

# Загрузка Prism.js (Python, загружает в markdown_editor_pkg/prism/)
python markdown_editor_pkg/download_prism.py
```

## 📄 Лицензия

MIT License

## 👤 Автор

Afaist

Markdown Editor (PyQt6) — редактор Markdown с поддержкой LaTeX, созданный с использованием Python 3.8+, PyQt6, QtWebEngine, KaTeX и Prism.js.
