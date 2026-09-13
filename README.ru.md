# Markdown Editor (PyQt6)

Простой и функциональный редактор Markdown с предпросмотром в реальном времени и поддержкой LaTeX-формул.

> 🇬🇧 [English version](README.md)

## 📋 Описание

Markdown Editor — это desktop-приложение для создания и редактирования документов в формате Markdown с мгновенным предпросмотром. Поддерживает встроенные и блочные LaTeX-формулы через библиотеку KaTeX, несколько тем оформления, экспорт в HTML и PDF, GitHub Callouts, зачёркнутый текст, списки задач и множество инструментов форматирования.

**Версия:** 1.0.3  
**Технологии:** Python 3.12+, PyQt6, QtWebEngine, KaTeX, Python-Markdown, Prism.js

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
- 🌍 **Интернационализация (i18n)** — поддержка английского и русского языков через Qt QTranslator
- ⚙️ **Настройки** — централизованное хранилище настроек (язык, тема, шрифт) с JSON-персистентностью в `~/.markdown_editor_config.json`
- 🖥️ **Распознавание ресурсов** — корректная работа путей к ресурсам (katex/, prism/) в режиме разработки и в собранном PyInstaller-бинарнике
- 😀 **Выбор emoji** — диалог поиска и вставки emoji с категориями и сеточным отображением, доступен через панель инструментов

## 🚀 Установка

### Требования

- Python 3.12 или выше
- pip (менеджер пакетов Python)
- Операционная система: Linux / macOS / Windows

### Шаги установки

1. **Клонируйте репозиторий** (или скачайте файлы):

```bash
git clone https://github.com/afaist/markdown_editor.git
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
pip install -e .
```

1. **Запустите приложение**:

```bash
python main.py
```

### Установка из релизов

Готовые бинарные файлы доступны на [странице релизов](https://github.com/afaist/markdown_editor/releases).

#### Linux

1. **Скачайте** архив последнего релиза: `markdown-editor-linux-x86_64.tar.gz`
2. **Распакуйте** архив:

```bash
tar -xzf markdown-editor-linux-x86_64.tar.gz
cd markdown-editor
```

3. **Запустите** приложение:

```bash
./markdown-editor
```

**Системные зависимости** (могут потребоваться на некоторых дистрибутивах):

```bash
# Debian/Ubuntu
sudo apt-get install -y libgl1 libxkbcommon-x11-0 libxcb-cursor0 libegl1 libwebp-dev libfontconfig1 libfreetype6 libx11-xcb1

# Fedora
sudo dnf install -y libglvnd-glx libxkbcommon libegl libwebp fontconfig
```

#### Windows

1. **Скачайте** архив последнего релиза: `markdown-editor-windows-x86_64.zip`
2. **Распакуйте** архив в любую папку (например, `C:\Program Files\Markdown Editor\`)
3. **Запустите** `markdown-editor.exe`

> **Примечание:** При первом запуске Windows SmartScreen может показать предупреждение. Нажмите «Подробнее» → «Запустить всё-таки». Права администратора не требуются.

## 📖 Использование

### Основные функции

#### Редактирование текста

Введите текст в левой панели (**Редактор Markdown**). Предпросмотр в правой панели обновляется автоматически при изменении текста.

#### Панель инструментов

Панель инструментов содержит выпадающие списки и кнопки, сгруппированные по функциям:

**Выпадающие списки:**

| Элемент | Варианты | Действие |
| ------- | ------- | ------ |
| Заголовки | H1–H6 | Вставляет заголовок выбранного уровня |
| Стили | Жирный, Курсив, Зачёркнутый, Код | Применяет выбранный стиль форматирования |
| Список | Маркированный, Нумерованный, Список задач | Вставляет выбранный тип списка |
| **Вставить** | Цитата, Код, LaTeX inline, LaTeX block, Ссылка, Изображение | Вставляет выбранный элемент |
| Выбор шрифта | Consolas, Courier New, Fira Code и др. | Изменяет семейство шрифта редактора |
| **Экспорт** | В PDF, В HTML | Экспортирует документ в выбранном формате |

**Кнопки:**

| Кнопка | Действие |
| -------- | ---------- |
| **+** | Увеличить размер шрифта |
| **−** | Уменьшить размер шрифта |
| Сбросить шрифт | Сброс шрифта и размера к значениям по умолчанию |

> **Примечание:** Действия «Открыть» и «Сохранить» доступны через меню **Файл** (`Ctrl+O`, `Ctrl+S`) или по горячим клавишам.

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

**Язык:**

- English
- Русский

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
│   ├── download_katex.py        # Скрипт для загрузки KaTeX (Python)
│   ├── get_katex.sh             # Скрипт для загрузки KaTeX (bash)
│   ├── download_prism.py        # Скрипт для загрузки Prism.js
│   ├── i18n.py                  # Internationalization (i18n) — Qt QTranslator
│   ├── i18n_build.py            # i18n build script (lupdate/lrelease)
│   ├── resource_path.py         # Resource path resolver (PyInstaller-aware)
│   ├── settings.py              # Centralized settings manager (JSON-backed)
│   ├── emoji_picker.py          # EmojiPickerDialog — диалог выбора emoji
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
├── locales/                     # Переводы (.ts, .qm)
├── .github/                     # CI/CD
│   └── workflows/
│       ├── ci.yml               # GitHub Actions (pytest + ruff + mypy)
│       └── release.yml          # Release workflow (PyInstaller)
├── .pre-commit-config.yaml      # Pre-commit hooks (ruff + mypy)
├── requirements.txt             # Зависимости Python
├── pyproject.toml               # Конфигурация pytest, mypy, ruff, setuptools
├── build.sh                     # Сборка PyInstaller (Linux/macOS)
├── build.bat                    # Сборка PyInstaller (Windows)
├── markdown-editor.spec         # PyInstaller spec-файл
├── markdown-editor.desktop      # Linux desktop entry
├── markdown-editor.service      # Linux systemd service
├── icon.png / icon.ico          # Иконки приложения
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
13. **FileIO / FileExport** (`file_operations.py`) — открытие, сохранение, экспорт HTML/PDF. `EditorState` — единый контекст состояния файлов.
14. **TextInsertions** (`text_insertions.py`) — вставка форматированного текста (заголовки, стили, списки, LaTeX, таблицы и т. д.).
15. **FindReplaceHandler** (`editor_find.py`) — диалог «Найти и заменить».
16. **FindReplaceDialog** (`find_replace.py`) — диалог поиска и замены (для обратной совместимости).
17. **SessionHandler** (`editor_session.py`) — сохранение/загрузка последней сессии.
18. **SessionManager** (`session_manager.py`) — менеджмент сессий.
19. **PDFHandler** (`editor_pdf.py`) — обработка PDF‑экспорта.
20. **HelpHandler** (`editor_help.py`) — справочная информация (О программе).
21. **CloseHandler** (`editor_close.py`) — обработка закрытия окна.
22. **MarkdownTextEdit** (`editor_keypress.py`) — кастомный `QTextEdit` с кастомными клавиатурными обработками.
23. **HeaderFooterDialog** (`header_footer_dialog.py`) — диалог настроек PDF‑колонтитулов.
24. **Settings** (`settings.py`) — централизованное хранилище настроек (JSON-backed): язык, тема, шрифт, размер шрифта, последний файл.
25. **i18n** (`i18n.py`) — модуль интернационализации: `setup_translator()`, `load_language()`, `tr()`, `get_available_languages()`. Поддерживает `en` и `ru`.
26. **i18n_build** (`i18n_build.py`) — CLI для Qt translation workflow: `lupdate`, `lrelease`, `all`.
27. **EmojiPickerDialog** (`emoji_picker.py`) — диалог выбора emoji с категориями, сеточным отображением и поиском.
28. **resource_path** (`resource_path.py`) — хелпер для определения путей к ресурсам (работает в режиме разработки и в PyInstaller-бинарнике).
29. **Редактор** — `QTextEdit` (`MarkdownTextEdit`) с подсветкой текущей темы.
30. **Предпросмотр** — `QWebEngineView` для отображения HTML.
31. **Экспорт** — `export_to_pdf()` использует `QWebEngineView.page().printToPdf()` для генерации PDF.

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

**Требования к Python:** 3.12+

## 🧪 Разработка

### Запуск тестов

```bash
# pytest (все тесты)
python3 -m pytest tests/ -v

# С покрытием
python3 -m pytest tests/ -v --cov=markdown_editor_pkg --cov-report=term-missing
```

> **Примечание:** Для тестирования используется `QT_QPA_PLATFORM=offscreen`, чтобы запускать Qt без графической оболочки.

### Линтинг и статический анализ

```bash
# ruff — линтинг и форматирование
ruff check markdown_editor_pkg/ tests/      # проверка
ruff check --fix markdown_editor_pkg/ tests/ # автоисправление
ruff format markdown_editor_pkg/ tests/      # форматирование

# mypy — проверка типов
mypy markdown_editor_pkg/
```

### Pre-commit хуки

```bash
# Установка
pip install pre-commit
pre-commit install

# Ручной запуск
pre-commit run --all-files
```

### CI/CD

GitHub Actions автоматически запускается при push/pull request:

- **test** — pytest на Python 3.12
- **lint** — ruff check + ruff format + mypy
- **release** — сборка PyInstaller-бинарника

Конфигурация: `.github/workflows/ci.yml`, `.github/workflows/release.yml`

### Настройка тестов

Конфигурация pytest находится в `pyproject.toml` — создаётся единый экземпляр `QApplication` для всех тестов в `tests/conftest.py`.

### Структура тестов

| Файл | Покрытие |
| ------ | ---------- |
| `test_latex_processor.py` | LaTeXProcessor |
| `test_callout_processor.py` | CalloutProcessor |
| `test_strikethrough.py` | StrikethroughProcessor |
| `test_themes.py` | ThemesManager |
| `test_font_settings.py` | Font settings |
| `test_session_manager.py` | SessionManager |
| `test_prism_processor.py` | PrismJSProcessor |
| `test_markdown_render.py` | MarkdownRenderer |
| `test_text_insertions.py` | TextInsertions |
| `test_file_operations.py` | FileIO + FileExport |
| `test_find_replace.py` | FindReplaceHandler |
| `test_header_footer_dialog.py` | HeaderFooterDialog |
| `test_pdf_headers.py` | PDF headers |
| `test_editor_ui.py` | Editor UI |

### Интернационализация (i18n)

Приложение поддерживает переключение языка интерфейса между английским и русским.

**Поддерживаемые языки:**

| Код | Язык | Файл |
|-----|------|------|
| `en` | English | `messages_en.qm` |
| `ru` | Русский | `messages_ru.qm` |

**Как это работает:**

1. Строки, помеченные для перевода, обёрнуты в `tr("text")` — обёртка вокруг `QCoreApplication.translate("App", text)`.
2. Переводчики хранятся в `locales/` в формате Qt `.ts` и `.qm`.
3. Язык загружается из `Settings` при старте приложения.
4. Переключение языка доступно через меню **Язык** — применяется через `load_language()` с уведомлением о необходимости перезапуска.

**Сборка переводов:**

```bash
# Извлечь переводимые строки из .py файлов
python -m markdown_editor_pkg.i18n_build lupdate

# Скомпилировать .ts в .qm
python -m markdown_editor_pkg.i18n_build lrelease

# Выполнить оба шага
python -m markdown_editor_pkg.i18n_build all
```

### Создание релизов

Релизы создаются с помощью Git-тегов и автоматизируются через GitHub Actions.

#### Ручной процесс создания релиза

1. **Убедитесь, что все тесты проходят**:

```bash
pytest tests/ -v
```

2. **Создайте новый тег версии**:

```bash
# Проверить текущие теги
git tag -l | sort -V | tail -5

# Создать новый тег (формат: vM.m.p)
git tag v1.0.4

# Отправить тег на GitHub
git push origin main --tags
```

3. **GitHub Actions** автоматически:
   - Соберёт бинарные файлы для Linux и Windows с помощью PyInstaller
   - Создаст GitHub Release с артефактами сборки
   - Сгенерирует заметки к релизу автоматически

#### Автоматический релиз через GitHub Actions

Также можно запустить сборку вручную через вкладку **Actions**:

1. Откройте репозиторий на GitHub
2. Перейдите в **Actions** → **Release**
3. Нажмите **"Run workflow"**
4. Выберите ветку и режим сборки:
   - `all` — сборка для Linux и Windows
   - `linux` — сборка только для Linux
   - `windows` — сборка только для Windows
   - `deb` — сборка только Debian-пакета

#### Релиз-воркфлоу

Релиз-воркфлоу (`.github/workflows/release.yml`) выполняет следующие шаги:

| Задача | Платформа | Результат |
| --- | -------- | ------ |
| `build-linux` | Ubuntu 24.04 | `dist/markdown-editor/` (PyInstaller onedir) |
| `build-windows` | Windows 2022 | `dist/markdown-editor/` + `dist/markdown-editor.exe` |
| `create-release` | Ubuntu 24.04 | Создаёт GitHub Release с артефактами tarball/zip |

**Артефакты, публикуемые с каждым релизом:**

| Файл | Платформа | Формат |
| ---- | -------- | ------ |
| `markdown-editor-linux-x86_64.tar.gz` | Linux | Tarball |
| `markdown-editor-windows-x86_64.zip` | Windows | ZIP-архив |

#### Локальная сборка (для тестирования)

```bash
# Linux/macOS
./build.sh onedir          # Сборка в папку (рекомендуется)
./build.sh onefile         # Сборка в один файл
./build.sh deb             # Сборка .deb-пакета
./build.sh clean           # Очистка артефактов сборки

# Windows
build.bat onedir           # Сборка в папку
build.bat onefile          # Сборка в один файл
build.bat clean            # Очистка артефактов
```

### Распределение (Distribution)

Приложение собирается в standalone-бинарник с помощью PyInstaller.

**Скрипты сборки:**

- `build.sh` — Linux/macOS (собирает `.spec`, упаковывает ресурсы)
- `build.bat` — Windows

**Конфигурация:**

- `markdown-editor.spec` — файл спецификации PyInstaller
- `.github/workflows/release.yml` — CI/CD релиз-воркфлоу

**Linux-интеграция:**

- `markdown-editor.desktop` — запись в меню приложений
- `markdown-editor.service` — systemd service unit
- `icon.png` / `icon.ico` — иконки приложения

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

Александр Зиновьев (<afaist@gmail.com>)

Markdown Editor (PyQt6) — редактор Markdown с поддержкой LaTeX, созданный с использованием Python 3.12+, PyQt6, QtWebEngine, KaTeX и Prism.js.
