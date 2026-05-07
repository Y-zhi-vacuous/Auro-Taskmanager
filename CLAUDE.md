# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common commands

```bash
# Run the app
python run.py

# Build single-file exe with PyInstaller
pyinstaller --noconfirm AuraTasksPro.spec
# Output: dist/AuraTasksPro.exe

# Build with Nuitka (alternative)
nuitka --standalone --onefile --enable-qt=pyqt6 --windows-disable-console --output-filename=AuraTasksPro.exe run.py
```

The recommended development environment is a conda environment (isolated from Anaconda base to avoid DLL conflicts):
```bash
conda create -n auratasks python=3.12 -y
conda activate auratasks
pip install PyQt6 PyQt6-Qt6 PyQt6-sip PyQt6-Fluent-Widgets openpyxl reportlab
```

There is no test suite and no linter configuration.

## Architecture

AuraTasks Pro is a PyQt6 desktop task manager with three-level nested tasks, multi-mode sorting, and Excel/PDF import-export. It follows an MVC-like layering:

```
run.py  →  aura_tasks_pro/main.py  →  MainWindow (views/)
                                       ├── TaskEditDialog (views/)
                                       ├── TaskService (services/)
                                       │     └── TaskRepository (services/)
                                       ├── export_import (services/)
                                       ├── delegates/ (custom tree rendering)
                                       └── utils/ (theme, enums, path helpers, blur effect)
```

**Layer responsibilities:**

- **`models/task.py`** — `Task` dataclass with fields: id, parent_id, name, progress, status, priority, dates, risk, remarks, order_index, children (tree). Depth is always 1 (child) since the max nesting is 3 levels (root → child → grandchild).
- **`services/repository.py`** — `TaskRepository`: all SQLite access via adjacency list (`parent_id` self-referencing FK). `get_all_tasks()` builds the in-memory tree from flat rows using `task_map`. `get_max_depth()` enforces the 3-level nesting limit. `get_children()` exist separately for depth checks. DB path: `%APPDATA%/AuraTasksPro/tasks.db`.
- **`services/task_service.py`** — `TaskService`: business logic layer. Owns `calculate_progress()` (recursive weighted average by child priority), `compute_score()` (composite formula: `Priority×10 − DaysToDeadline + RiskWeight`), `sort_by_score()` (auto-sort mode), `mark_status()` / `increase_priority()` / `decrease_priority()`.
- **`views/main_window.py`** — `MainWindow(FluentWindow)`: the single main window with a `QTreeWidget`, toolbar, search, and sort combo. Applies Monokai Pro dark QSS theme. Uses custom delegates for progress bar (column 1) and risk icon (column 6) rendering. All user-triggered operations are wrapped in `_safe_exec()` which shows a `QMessageBox` on error instead of crashing.
- **`views/edit_dialog.py`** — `TaskEditDialog(QDialog)`: dark-themed dialog for creating/editing tasks, uses qfluentwidgets components (LineEdit, ComboBox, SpinBox, DatePicker, TextEdit).
- **`delegates/task_delegates.py`** — `ProgressBarDelegate` renders a colored progress bar (cyan/green/orange thresholds at 30/70). `RiskIconDelegate` renders a pink warning badge for high-risk tasks.
- **`services/export_import.py`** — Standalone functions (not class-based): `export_xlsx()`, `import_xlsx()`, `export_pdf()`. PDF export auto-detects Chinese fonts from `C:/Windows/Fonts/`.
- **`utils/`** — `apple_theme.py` defines the full Monokai Pro color palette. `blur_effect.py` enables Windows 11 Acrylic/Mica via DWM `SetWindowCompositionAttribute` API. `path_utils.py` handles resource path resolution for both dev and frozen (PyInstaller/Nuitka) modes.
- **`controllers/`** — Empty placeholder; logic currently lives in `TaskService`.

## Key design details

- **3-level nesting limit**: enforced in `TaskRepository.create_task()` via `get_max_depth(parent_id) < 2`. The `Task.depth` property is always 0 or 1 for any task (root tasks have `parent_id=None`, children have `parent_id` set).
- **Progress inheritance**: parent tasks whose `progress` field is 0 but have children will show the weighted average of children's progress in the tree. Setting a task's own progress to a non-zero value without children shows that value directly.
- **Global exception handling**: `sys.excepthook` is overridden in `main.py` to show a `QMessageBox` for unhandled exceptions. Additionally, `MainWindow._safe_exec()` wraps all UI operation callbacks to catch exceptions and show them as dialogs.
- **Sort modes**: Auto (composite score), Priority, Due Date, Manual. Manual mode preserves `order_index` from the database (drag-and-drop reordering is stored via `reorder_siblings()`).
- **Packaging**: PyInstaller spec includes `collect_data_files` for qfluentwidgets and PyQt6, plus the `resources/` directory. The `resource_path()` function resolves paths differently in dev vs frozen (`sys._MEIPASS` for PyInstaller, `sys.executable.parent` for Nuitka).
