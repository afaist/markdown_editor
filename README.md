# Markdown Editor (PyQt6)

A simple and functional Markdown editor with real-time preview and LaTeX formula support.

> 🇷🇺 [Русская версия / Russian version](README.ru.md)

## 📋 Description

Markdown Editor is a desktop application for creating and editing Markdown documents with instant preview. It supports inline and block LaTeX formulas via KaTeX, multiple themes, HTML and PDF export, GitHub Callouts, strikethrough text, task lists, and numerous formatting tools.

**Version:** 1.0.3  
**Technologies:** Python 3.12+, PyQt6, QtWebEngine, KaTeX, Python-Markdown, Prism.js

## ✨ Features

- ✏️ **Markdown Editor** — convenient text editor based on QTextEdit with formatting support
- 👀 **Real-time Preview** — automatic HTML preview update on text input (with 300ms delay)
- 📐 **LaTeX Formulas** — support for inline (`$...$`) and block (`$$...$$`) formulas via KaTeX
- 📤 **Export** — save in HTML and PDF formats with customizable headers/footers
- 🖼️ **Images** — insert images via file selection dialog
- 🎨 **Themes** — three themes for preview and three themes for editor (light, dark, high-contrast)
- 💾 **Auto-save** — automatic file saving every 3 seconds after changes
- 🔍 **Find and Replace** — dialog for searching and replacing text
- 📊 **Statistics** — character and word counters in the status bar
- 📁 **File Management** — create, open, save, save as, close
- 📝 **Markdown Extensions Support** — fenced code blocks, syntax highlighting (Prism.js), tables, table of contents
- 📌 **GitHub Callouts** — support for `> [!note]`, `> [!tip]`, `> [!important]`, `> [!warning]`, `> [!caution]` blocks
- ~~ ~~ **Strikethrough** — support for `~~text~~`
- 💿 **Last Session** — automatic loading of the last opened file on startup
- 🔤 **Font Customization** — font selection from list, size adjustment (+/−), reset to defaults
- 📋 **Task Lists** — support for `<input type="checkbox">` via `- [ ]`
- 🧮 **LaTeX Templates** — quick insertion of fractions, roots, integrals, sums, matrices, etc.
- 📊 **Table Insertion** — generation of a 3×3 Markdown table template
- 📝 **Language-specific Code Blocks** — quick templates for Python, Bash, Markdown, C++, Rust
- 🌍 **Internationalization (i18n)** — support for English and Russian languages via Qt QTranslator
- ⚙️ **Settings** — centralized settings storage (language, theme, font) with JSON persistence in `~/.markdown_editor_config.json`
- 🖥️ **Resource Path Resolution** — correct resource path handling (katex/, prism/) in both development mode and PyInstaller-built binary
- 😀 **Emoji Picker** — searchable emoji picker with categories and grid display, accessible via toolbar

## 🚀 Installation

### Requirements

- Python 3.12 or higher
- pip (Python package manager)
- Operating System: Linux / macOS / Windows

### Installation Steps

1. **Clone the repository** (or download the files):

```bash
git clone https://github.com/afaist/markdown_editor.git
cd markdown_editor
```

1. **Create a virtual environment** (recommended):

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
```

1. **Install dependencies**:

```bash
pip install -e .
```

1. **Run the application**:

```bash
python main.py
```

### Installation from Releases

Pre-built binaries are available on the [Releases page](https://github.com/afaist/markdown_editor/releases).

#### Linux

1. **Download** the latest release archive: `markdown-editor-linux-x86_64.tar.gz`
2. **Extract** the archive:

```bash
tar -xzf markdown-editor-linux-x86_64.tar.gz
cd markdown-editor
```

3. **Run** the application:

```bash
./markdown-editor
```

**System dependencies** (may be required on some distributions):

```bash
# Debian/Ubuntu
sudo apt-get install -y libgl1 libxkbcommon-x11-0 libxcb-cursor0 libegl1 libwebp-dev libfontconfig1 libfreetype6 libx11-xcb1

# Fedora
sudo dnf install -y libglvnd-glx libxkbcommon libegl libwebp fontconfig
```

#### Windows

1. **Download** the latest release archive: `markdown-editor-windows-x86_64.zip`
2. **Extract** the archive to any folder (e.g., `C:\Program Files\Markdown Editor\`)
3. **Run** `markdown-editor.exe`

> **Note:** On first launch, Windows SmartScreen may show a warning. Click "More info" → "Run anyway". No administrator privileges are required.

## 📖 Usage

### Basic Functions

#### Text Editing

Enter text in the left panel (**Markdown Editor**). The preview in the right panel updates automatically when the text changes.

#### Toolbar

The toolbar contains dropdowns and buttons grouped by function:

**Dropdowns:**

| Control | Options | Action |
| ------- | ------- | ------ |
| Headings | H1–H6 | Inserts heading at selected level |
| Styles | Bold, Italic, Strikethrough, Code | Applies selected formatting style |
| List | Bulleted, Numbered, Task List | Inserts selected list type |
| **Insert** | Quote, Code, LaTeX inline, LaTeX block, Link, Image | Inserts selected element |
| Font Selection | Consolas, Courier New, Fira Code, etc. | Changes editor font family |
| **Export** | Export to PDF, Export to HTML | Exports document in selected format |

**Buttons:**

| Button | Action |
| -------- | ---------- |
| **+** | Increase font size |
| **−** | Decrease font size |
| Reset Font | Reset font and size to defaults |

> **Note:** Open and Save actions are available via **File** menu (`Ctrl+O`, `Ctrl+S`) or via keyboard shortcuts.

#### Markdown Menu

All formatting tools with hotkeys are available in the **Markdown** menu:

**Headings** (`Ctrl+Shift+1`–`8`):

- Headings H1–H7

**Styles**:

- **Bold** (`Ctrl+B`)
- *Italic* (`Ctrl+I`)
- ~~Strikethrough~~ (`Ctrl+Shift+X`)
- `Inline Code` (`Ctrl+``)

**Lists**:

- Bulleted (`Ctrl+Shift+U`)
- Numbered (`Ctrl+Shift+O`)
- Task List (`Ctrl+Shift+T`)

**Quote** (`Ctrl+Shift+Q`)

**Code**:

- Python (`Ctrl+Shift+C`)
- Bash (`Ctrl+Shift+B`)
- Markdown (`Ctrl+Shift+M`)
- C++ (`Ctrl+Shift+P`)
- Rust (`Ctrl+Shift+R`)

**LaTeX**:

- Inline `($...$)` (`Ctrl+L`)
- Block (`$$...$$`) (`Ctrl+Shift+L`)
- Fraction `\frac` (`Ctrl+Shift+F`)
- Square root `\sqrt` (`Ctrl+Shift+R`)
- Superscript (`Ctrl+Shift+S`)
- Subscript (`Ctrl+Shift+N`)
- Sum `\sum` (`Ctrl+Shift+A`)
- Integral `\int` (`Ctrl+Shift+G`)
- Matrix `\begin{matrix}` (`Ctrl+Shift+M`)

**Additional**:

- Divider (`---`) (`Ctrl+Shift+H`)
- Table (`Ctrl+Shift+Tab`)
- HTML comment (`Ctrl+Shift+/`)

#### Menus

**File:**

- New (`Ctrl + N`)
- Open (`Ctrl + O`)
- Save (`Ctrl + S`)
- Save As...
- Close (`Ctrl + W`)
- Export to HTML
- Export to PDF
- PDF Export Settings...
- Exit (`Ctrl + Q`)

**Edit:**

- Undo (`Ctrl + Z`)
- Redo (`Ctrl + Y`)
- Cut / Copy / Paste
- Find and Replace (`Ctrl + F`)
- Insert Image...

**View:**

- Refresh Preview
- Theme: light / dark / high-contrast
- Editor Theme: light / dark / high-contrast
- Increase Font (`Ctrl + +`)
- Decrease Font (`Ctrl + -`)
- Reset Font (`Ctrl + 0`)

**Language:**

- English
- Русский

**Help:**

- About

#### Export

- **Export to HTML**: menu **File → Export to HTML**
- **Export to PDF**: **Export to PDF** button on the toolbar or menu **File → Export to PDF**
- **PDF Export Settings**: menu **File → PDF Export Settings** — enable/disable headers, header and footer text, automatic page numbering

### Hotkeys

| Keys | Action |
| --------- | ---------- |
| `Ctrl + N` | New file |
| `Ctrl + O` | Open file |
| `Ctrl + S` | Save |
| `Ctrl + W` | Close file |
| `Ctrl + F` | Find and Replace |
| `Ctrl + Z` | Undo |
| `Ctrl + Y` | Redo |
| `Ctrl + Q` | Exit |
| `Ctrl + B` | Bold |
| `Ctrl + I` | Italic |
| `Ctrl + L` | Inline LaTeX |
| `Ctrl + Shift + L` | Block LaTeX |
| `Ctrl + Shift + 1..7` | Headings H1–H7 |
| `Ctrl + Shift + X` | Strikethrough |
| `Ctrl + +` | Increase font |
| `Ctrl + -` | Decrease font |
| `Ctrl + 0` | Reset font |

## 🏗️ Architecture

### Project Structure

```text
markdown_editor/
├── main.py                      # Entry point
├── markdown_editor_pkg/         # Main application package
│   ├── __init__.py              # Export MarkdownEditorPyQt
│   ├── editor.py                # Main MarkdownEditorPyQt class (wrapper)
│   ├── editor_components.py     # UIBuilder, ToolbarBuilder, MenuBuilder
│   ├── editor_events.py         # EventHandler — event handlers
│   ├── editor_find.py           # FindReplaceHandler — find and replace
│   ├── editor_help.py           # HelpHandler — help information
│   ├── editor_keypress.py       # MarkdownTextEdit — custom QTextEdit
│   ├── editor_markdown_menu.py  # MarkdownMenuBuilder — formatting menu
│   ├── editor_pdf.py            # PDFHandler — PDF export processing
│   ├── editor_session.py        # SessionHandler — session save/load
│   ├── editor_themes.py         # ThemeFontHandler — font management
│   ├── editor_close.py          # CloseHandler — window close handling
│   ├── themes.py                  # CSS preview themes and QSS editor themes
│   ├── markdown_renderer.py     # MarkdownRenderer — Markdown → HTML conversion
│   ├── latex_processor.py       # LaTeXProcessor — LaTeX formula processing
│   ├── callout_processor.py     # CalloutProcessor — GitHub Callouts
│   ├── prism_processor.py       # PrismJSProcessor — syntax highlighting
│   ├── text_insertions.py       # TextInsertions — formatted text insertion
│   ├── file_operations.py       # FileIO, FileExport, EditorState
│   ├── find_replace.py          # FindReplaceDialog — find dialog
│   ├── session_manager.py       # SessionManager — session management
│   ├── header_footer_dialog.py  # HeaderFooterDialog — PDF headers
│   ├── download_katex.py        # KaTeX download script (Python)
│   ├── get_katex.sh             # KaTeX download script (bash)
│   ├── download_prism.py        # Prism.js download script
│   ├── i18n.py                  # Internationalization (i18n) — Qt QTranslator
│   ├── i18n_build.py            # i18n build script (lupdate/lrelease)
│   ├── resource_path.py         # Resource path resolver (PyInstaller-aware)
│   ├── settings.py              # Centralized settings manager (JSON-backed)
│   ├── emoji_picker.py          # EmojiPickerDialog — searchable emoji picker
│   ├── katex/                   # KaTeX library
│   │   ├── katex.min.css
│   │   ├── katex.min.js
│   │   └── auto-render.min.js
│   └── prism/                   # Prism.js for syntax highlighting
│       ├── prism.min.js
│       ├── components/          # Language localizations
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
│       └── themes/              # Prism CSS themes
│           ├── prism-okaidia.min.css
│           └── prism-tomorrow.min.css
├── tests/                       # Unit tests (pytest)
│   ├── conftest.py              # pytest setup (Qt headless)
│   └── test_*.py                # Component tests
├── locales/                     # Translations (.ts, .qm)
├── .github/                     # CI/CD
│   └── workflows/
│       ├── ci.yml               # GitHub Actions (pytest + ruff + mypy)
│       └── release.yml          # Release workflow (PyInstaller)
├── .pre-commit-config.yaml      # Pre-commit hooks (ruff + mypy)
├── requirements.txt             # Python dependencies
├── pyproject.toml               # pytest, mypy, ruff, setuptools configuration
├── build.sh                     # PyInstaller build (Linux/macOS)
├── build.bat                    # PyInstaller build (Windows)
├── markdown-editor.spec         # PyInstaller spec file
├── markdown-editor.desktop      # Linux desktop entry
├── markdown-editor.service      # Linux systemd service
├── icon.png / icon.ico          # Application icons
├── README.md                    # This file
└── venv/                        # Virtual environment
```

### Components

1. **MarkdownEditorPyQt** (`editor.py`) — main class, inherits from `QMainWindow`, wrapper that assembles components and delegates work to them.
2. **UIBuilder** (`editor_components.py`) — creates the main UI: splitter, editor, preview, statusbar.
3. **ToolbarBuilder** (`editor_components.py`) — creates the toolbar.
4. **MenuBuilder** (`editor_components.py`) — creates menus (File, Edit, View, Help).
5. **MarkdownMenuBuilder** (`editor_markdown_menu.py`) — Markdown formatting menu with hotkeys.
6. **EventHandler** (`editor_events.py`) — event handlers: `textChanged`, preview update, status.
7. **ThemesManager** (`themes.py`) — manages CSS preview themes, QSS editor themes, fonts, and font size.
8. **ThemeFontHandler** (`editor_themes.py`) — theme and font handler.
9. **MarkdownRenderer** (`markdown_renderer.py`) — Markdown → HTML conversion with LaTeX, themes, Callouts, and code highlighting.
10. **LaTeXProcessor** (`latex_processor.py`) — extracts LaTeX formulas, replaces with placeholders, restores them.
11. **CalloutProcessor** (`callout_processor.py`) — processes GitHub Callouts from blockquotes.
12. **PrismJSProcessor** (`prism_processor.py`) — Prism.js integration for code highlighting.
13. **FileIO / FileExport** (`file_operations.py`) — open, save, HTML/PDF export. `EditorState` — unified file state context.
14. **TextInsertions** (`text_insertions.py`) — inserts formatted text (headings, styles, lists, LaTeX, tables, etc.).
15. **FindReplaceHandler** (`editor_find.py`) — "Find and Replace" dialog.
16. **FindReplaceDialog** (`find_replace.py`) — find and replace dialog (for backward compatibility).
17. **SessionHandler** (`editor_session.py`) — save/load last session.
18. **SessionManager** (`session_manager.py`) — session management.
19. **PDFHandler** (`editor_pdf.py`) — PDF export processing.
20. **HelpHandler** (`editor_help.py`) — help information (About).
21. **CloseHandler** (`editor_close.py`) — window close handling.
22. **MarkdownTextEdit** (`editor_keypress.py`) — custom `QTextEdit` with custom keyboard handling.
23. **HeaderFooterDialog** (`header_footer_dialog.py`) — PDF header/footer settings dialog.
24. **Settings** (`settings.py`) — centralized settings storage (JSON-backed): language, theme, font, font size, last file.
25. **i18n** (`i18n.py`) — internationalization module: `setup_translator()`, `load_language()`, `tr()`, `get_available_languages()`. Supports `en` and `ru`.
26. **i18n_build** (`i18n_build.py`) — CLI for Qt translation workflow: `lupdate`, `lrelease`, `all`.
27. **EmojiPickerDialog** (`emoji_picker.py`) — emoji picker dialog with categories, grid display, and search.
28. **resource_path** (`resource_path.py`) — helper for resolving resource paths (works in both development mode and PyInstaller binary).
29. **Editor** — `QTextEdit` (`MarkdownTextEdit`) with the current theme's highlighting.
30. **Preview** — `QWebEngineView` for displaying HTML.
31. **Export** — `export_to_pdf()` uses `QWebEngineView.page().printToPdf()` for PDF generation.

### Markdown Extensions Used

- `fenced_code` — code blocks with triple backticks
- **Prism.js** — syntax highlighting in code blocks (loaded via JavaScript in the preview)
- `tables` — Markdown tables
- `toc` — automatic table of contents

### Syntax Highlighting

Code highlighting is implemented via **Prism.js** — a client-side JavaScript library. This provides:

- Dynamic switching of highlight colors when changing themes (light/dark/high-contrast)
- Language support: Python, Java, C, C++, JavaScript, TypeScript, Bash, SQL, CSS, HTML
- Automatic language detection based on the `language-xxx` class in code blocks
- Fast performance without server-side processing

The following Prism.js CSS themes are used for theme switching:

- **Light theme** — `prism-okaidia.min.css`
- **Dark theme** — `prism-tomorrow.min.css`
- **High-contrast theme** — `prism-okaidia.min.css` (fallback)

All Prism.js resources are downloaded by the `download_prism.py` script into the `markdown_editor_pkg/prism/` folder.

## 📦 Dependencies

| Package | Purpose |
| ------- | ----------- |
| `PyQt6>=6.6.0` | GUI framework |
| `PyQt6-WebEngine>=6.6.0` | `QWebEngineView` for preview and PDF export |
| `markdown>=3.4.0` | Markdown to HTML conversion |

**Python requirements:** 3.12+

## 🧪 Development

### Running Tests

```bash
# pytest (all tests)
python3 -m pytest tests/ -v

# With coverage
python3 -m pytest tests/ -v --cov=markdown_editor_pkg --cov-report=term-missing
```

> **Note:** Testing uses `QT_QPA_PLATFORM=offscreen` to run Qt without a graphical display.

### Linting and Static Analysis

```bash
# ruff — linting and formatting
ruff check markdown_editor_pkg/ tests/      # check
ruff check --fix markdown_editor_pkg/ tests/ # auto-fix
ruff format markdown_editor_pkg/ tests/      # formatting

# mypy — type checking
mypy markdown_editor_pkg/
```

### Pre-commit Hooks

```bash
# Install
pip install pre-commit
pre-commit install

# Run manually
pre-commit run --all-files
```

### CI/CD

GitHub Actions runs automatically on push/pull request:

- **test** — pytest on Python 3.12
- **lint** — ruff check + ruff format + mypy
- **release** — PyInstaller binary build

Configuration: `.github/workflows/ci.yml`, `.github/workflows/release.yml`

### Test Configuration

The pytest configuration is in `pyproject.toml` — a single `QApplication` instance is created for all tests in `tests/conftest.py`.

### Test Structure

| File | Coverage |
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

### Internationalization (i18n)

The application supports switching the interface language between English and Russian.

**Supported Languages:**

| Code | Language | File |
| ----- | ------ | ------ |
| `en` | English | `messages_en.qm` |
| `ru` | Русский | `messages_ru.qm` |

**How it works:**

1. Strings marked for translation are wrapped in `tr("text")` — a wrapper around `QCoreApplication.translate("App", text)`.
2. Translators are stored in `locales/` in Qt `.ts` and `.qm` formats.
3. The language is loaded from `Settings` on application startup.
4. Language switching is available via the **Language** menu — applied via `load_language()` with a restart notification.

**Building Translations:**

```bash
# Extract translatable strings from .py files
python -m markdown_editor_pkg.i18n_build lupdate

# Compile .ts to .qm
python -m markdown_editor_pkg.i18n_build lrelease

# Execute both steps
python -m markdown_editor_pkg.i18n_build all
```

### Creating Releases

Releases are created using Git tags and automated via GitHub Actions.

#### Manual Release Process

1. **Ensure all tests pass**:

```bash
pytest tests/ -v
```

2. **Update the version tag**:

```bash
# Check current tag
git tag -l | sort -V | tail -5

# Create a new tag (format: vM.m.p)
git tag v1.0.4

# Push the tag to GitHub
git push origin main --tags
```

3. **GitHub Actions** will automatically:
   - Build binaries for Linux and Windows using PyInstaller
   - Create a GitHub Release with the build artifacts
   - Generate release notes automatically

#### Automated Release via GitHub Actions

You can also trigger a build manually from the **Actions** tab:

1. Open the repository on GitHub
2. Go to **Actions** → **Release**
3. Click **"Run workflow"**
4. Select the branch and build mode:
   - `all` — build for Linux and Windows
   - `linux` — build only Linux
   - `windows` — build only Windows
   - `deb` — build only Debian package

#### Release Workflow

The release workflow (`.github/workflows/release.yml`) performs the following steps:

| Job | Platform | Output |
| --- | -------- | ------ |
| `build-linux` | Ubuntu 24.04 | `dist/markdown-editor/` (PyInstaller onedir) |
| `build-windows` | Windows 2022 | `dist/markdown-editor/` + `dist/markdown-editor.exe` |
| `create-release` | Ubuntu 24.04 | Creates GitHub Release with tarball/zip artifacts |

**Artifacts published with each release:**

| File | Platform | Format |
| ---- | -------- | ------ |
| `markdown-editor-linux-x86_64.tar.gz` | Linux | Tarball |
| `markdown-editor-windows-x86_64.zip` | Windows | ZIP archive |

#### Local Build (for testing)

```bash
# Linux/macOS
./build.sh onedir          # Build in folder mode (recommended)
./build.sh onefile         # Build as single file
./build.sh deb             # Build .deb package
./build.sh clean           # Clean build artifacts

# Windows
build.bat onedir           # Build in folder mode
build.bat onefile          # Build as single file
build.bat clean            # Clean build artifacts
```

### Distribution

The application is built into a standalone binary using PyInstaller.

**Build Scripts:**

- `build.sh` — Linux/macOS (builds `.spec`, packages resources)
- `build.bat` — Windows

**Configuration:**

- `markdown-editor.spec` — PyInstaller spec file
- `.github/workflows/release.yml` — CI/CD release workflow

**Linux Integration:**

- `markdown-editor.desktop` — application menu entry
- `markdown-editor.service` — systemd service unit
- `icon.png` / `icon.ico` — application icons

## 🛠️ Troubleshooting

| Problem | Solution |
| ---------- | --------- |
| PyQt6 module not found | `pip install PyQt6 PyQt6-WebEngine` |
| LaTeX formulas not displayed | Check that files exist in `markdown_editor_pkg/katex/` (`katex.min.css`, `katex.min.js`, `auto-render.min.js`) |
| Error during PDF export | Ensure `PyQt6-WebEngine` is installed |
| Preview not updating | Check that KaTeX JavaScript is loaded correctly |
| Syntax highlighting not working | Check that files exist in `markdown_editor_pkg/prism/` |

### Downloading Resources

If KaTeX or Prism.js files are missing, run the corresponding scripts:

```bash
# Download KaTeX (Python, downloads to markdown_editor_pkg/katex/)
python markdown_editor_pkg/download_katex.py

# Download Prism.js (Python, downloads to markdown_editor_pkg/prism/)
python markdown_editor_pkg/download_prism.py
```

## 📄 License

MIT License

## 👤 Author

Alexander Zinovev (<afaist@gmail.com>)

Markdown Editor (PyQt6) — a Markdown editor with LaTeX support, built using Python 3.12+, PyQt6, QtWebEngine, KaTeX, and Prism.js.
