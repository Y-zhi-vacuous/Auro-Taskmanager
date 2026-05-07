# AuraTasks Pro 工程总结文档

## 一、工程文件架构及构建思路

### 1.1 项目概述

AuraTasks Pro 是一款基于 Python 的个人任务管理桌面工具，支持三级嵌套子任务、多维度排序、Excel/PDF 导入导出，采用 MVC 架构分离数据层、业务层与视图层。

### 1.2 技术栈

| 类别 | 技术选型 |
|------|----------|
| GUI 框架 | PyQt6 + PyQt6-Fluent-Widgets (qfluentwidgets) |
| 数据库 | SQLite3，邻接表模型自关联分级 |
| 主题风格 | Monokai Pro 暗色主题 + Windows 11 Acrylic 毛玻璃 |
| 导出格式 | xlsx (openpyxl) + pdf (reportlab + 中文字体) |
| 打包工具 | PyInstaller (单文件 exe) |
| 运行环境 | conda 隔离环境 (auratasks) |

### 1.3 目录结构

```
aura_tasks_pro/
├── __init__.py
├── main.py                          # 应用入口（全局异常捕获 + HiDPI + 字体 + 图标）
├── models/
│   ├── __init__.py
│   └── task.py                      # Task 数据模型 (dataclass)
├── views/
│   ├── __init__.py
│   ├── main_window.py               # 主窗口 (FluentWindow + Monokai Pro QSS + TreeWidget)
│   └── edit_dialog.py               # 任务编辑对话框 (暗色 Monokai 风格)
├── controllers/
│   └── __init__.py                  # 预留扩展
├── services/
│   ├── __init__.py
│   ├── repository.py                # TaskRepository (SQLite 邻接表 CRUD)
│   ├── task_service.py              # TaskService (复合排序算法 + 递归进度 + 状态管理)
│   └── export_import.py             # xlsx/pdf 导出、xlsx 导入
├── delegates/
│   ├── __init__.py
│   └── task_delegates.py            # ProgressBarDelegate + RiskIconDelegate
├── utils/
│   ├── __init__.py
│   ├── enums.py                     # TaskStatus、Priority 枚举
│   ├── path_utils.py                # resource_path + get_db_path
│   ├── apple_theme.py               # Monokai Pro 主题色定义
│   └── blur_effect.py               # Windows Acrylic/Mica 毛玻璃效果 (DWM API)
└── resources/
    ├── app_icon.ico                  # 应用图标 (7尺寸 16~256px)
    ├── app_icon.png                  # 图标 PNG 源
    └── gen_icon.py                   # 图标生成脚本

run.py                               # 根入口
requirements.txt                     # 依赖清单
AuraTasksPro.spec                    # PyInstaller 打包配置
build.bat                            # 打包命令参考
```

### 1.4 MVC 架构设计

```
┌─────────────────────────────────────────────────────────┐
│                      View 层                            │
│  MainWindow (FluentWindow + QSS + TreeWidget)           │
│  TaskEditDialog (QDialog + Fluent Widgets)              │
│  ProgressBarDelegate / RiskIconDelegate (自定义绘制)     │
└──────────────────────┬──────────────────────────────────┘
                       │ 调用
┌──────────────────────▼──────────────────────────────────┐
│                    Service 层                           │
│  TaskService                                            │
│    ├── calculate_progress()  递归加权平均进度           │
│    ├── compute_score()       复合权重排序公式           │
│    │   Score = Priority×10 - DaysToDeadline + RiskWeight│
│    ├── sort_by_score()       自动排序                   │
│    ├── mark_status()         状态切换                   │
│    └── increase/decrease_priority()  优先级调整         │
└──────────────────────┬──────────────────────────────────┘
                       │ 调用
┌──────────────────────▼──────────────────────────────────┐
│                  Repository 层                          │
│  TaskRepository (SQLite3)                               │
│    ├── 邻接表模型: parent_id 自关联                    │
│    ├── get_max_depth()  三级深度限制                    │
│    ├── create/update/delete/reorder                     │
│    └── get_all_tasks()  递归构建树形结构                │
└─────────────────────────────────────────────────────────┘
```

### 1.5 数据库设计 (邻接表模型)

```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_id INTEGER,                    -- 递归关联 (邻接表)
    name TEXT NOT NULL,
    progress INTEGER DEFAULT 0,           -- 0-100
    status TEXT DEFAULT '待办',           -- 待办/进行中/已完成/已挂起
    priority INTEGER DEFAULT 3,           -- 1-5
    start_date DATE,
    due_date DATE,
    risk TEXT DEFAULT '',
    remarks TEXT DEFAULT '',
    order_index INTEGER DEFAULT 0,        -- 手动排序
    FOREIGN KEY (parent_id) REFERENCES tasks(id) ON DELETE CASCADE
);
```

- **三级嵌套**: `parent_id` 递归关联，`get_max_depth()` 限制最深 3 级 (主任务→子任务→孙任务)
- **自动进度**: 父任务进度 = 子任务进度的优先级加权平均值
- **手动排序**: `order_index` 保存拖拽顺序

### 1.6 主题系统设计

采用 Monokai Pro (VSCode) 主题色方案：

| 角色 | 色值 | 用途 |
|------|------|------|
| 背景 | `#1E1E1E` / `#2D2A2E` | 窗口 / 编辑器 |
| 前景 | `#FCFCFA` | 主文字 |
| 绿 (Accent) | `#A6E22A` | 强调/新建/完成 |
| 粉红 | `#FF6188` | 危险/删除/紧急优先级 |
| 橙 | `#FC9867` | 警告/高优先级 |
| 青 | `#78DCE8` | 信息/低优先级 |
| 紫 | `#AB9DF2` | 特殊标记 |
| 灰 | `#727072` | 注释/次要文字 |

毛玻璃效果通过 Windows DWM API `SetWindowCompositionAttribute` 启用 `ACCENT_ENABLE_ACRYLICBLURBEHIND`。

### 1.7 关键算法

**复合权重排序公式：**

```
Score = (Priority × 10) - DaysToDeadline + RiskWeight
```

- `Priority`: 1-5 级
- `DaysToDeadline`: 距截止日期天数 (越近分越高)
- `RiskWeight`: 关键词映射 {"高":5, "严重":8, "紧急":10, "critical":10, "high":5}

**递归加权进度计算：**

```python
progress = Σ(child_progress × child_priority) / Σ(child_priority)
```

### 1.8 缓存文件位置

- 数据库: `%APPDATA%\AuraTasksPro\tasks.db`
- 路径解析: `get_db_path()` 自动创建 AppData 子目录，避免权限问题

---

## 二、完成该工程遇到的问题及解决方案

### 2.1 PyQt6 DLL 加载失败

**问题**: 在 Anaconda Python 创建的 venv 中，`from PyQt6.QtWidgets import QWidget` 报错 `ImportError: DLL load failed while importing QtWidgets: 找不到指定的程序。`

**根因**: Anaconda 的 venv 使用 `--system-site-packages` 默认行为，`sys.path` 中泄露了 `D:\anaconda\DLLs` 和 `D:\anaconda\Lib`，这些路径下的旧版 Qt5 DLL 与 PyQt6 冲突。

**尝试的方案**:
1. ❌ `os.add_dll_directory()` — 无效，Python 已在导入时锁定搜索路径
2. ❌ 设置 `PATH` 环境变量加入 Qt6/bin — 无效，Anaconda DLLs 优先级更高
3. ❌ 清除 PATH 中 Anaconda 路径 — 无效，venv 内部硬编码了基础路径
4. ✅ **使用 `conda create -n auratasks` 创建独立 conda 环境** — conda 对 DLL 隔离管理更好，问题解决

### 2.2 全局 site-packages 旧版包冲突

**问题**: `C:\Users\26698\AppData\Roaming\Python\Python312\site-packages\` 下存在 PyQt5 版本的 `qfluentwidgets` 和 `qframelesswindow`，被优先加载导致 `ModuleNotFoundError: No module named 'PyQt5.sip'`。

**解决方案**: 手动删除 Roaming 目录下的旧版包：
```
qfluentwidgets/  (PyQt5 版)
qframelesswindow/  (PyQt5 版)
PyQt5/
PyQt5-5.15.9.dist-info/
PyQt5_Frameless_Window-0.3.9.dist-info/
PyQt5_Qt5-5.15.2.dist-info/
PyQt_Fluent_Widgets-1.5.5.dist-info/
```

### 2.3 FluentDialog 不存在

**问题**: `from qfluentwidgets import FluentDialog` 报错 `ImportError: cannot import name 'FluentDialog'`。

**根因**: PyQt6-Fluent-Widgets 1.11.2 版本中没有 `FluentDialog` 类。

**解决方案**: 改用标准 `QDialog` 作为基类，内部仍使用 qfluentwidgets 的 Fluent 组件 (LineEdit, ComboBox, SpinBox, DatePicker 等)。

### 2.4 addSubInterface objectName 为空

**问题**: `FluentWindow.addSubInterface()` 报错 `ValueError: The object name of 'interface' can't be empty string.`

**解决方案**: 给传入的 widget 设置 objectName：
```python
self.main_widget = QWidget()
self.main_widget.setObjectName("mainInterface")
```

### 2.5 AA_UseHighDpiPixmaps 属性不存在

**问题**: `app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)` 报错 `AttributeError: type object 'ApplicationAttribute' has no attribute 'AA_UseHighDpiPixmaps'`。

**根因**: PyQt6 (Qt6) 已移除 `AA_UseHighDpiPixmaps` 和 `AA_EnableHighDpiScaling`，HiDPI 由 Qt6 自动处理。

**解决方案**: 删除这两行 `setAttribute` 调用，仅保留 `setHighDpiScaleFactorRoundingPolicy`。

### 2.6 添加子任务直接保存导致崩溃

**问题**: 新建子任务后不修改任何字段直接点击保存，应用崩溃。

**根因**: `DatePicker.date` 在某些状态下返回的类型不一致，`date(sd.year(), sd.month(), sd.day())` 转换失败导致未捕获异常。

**解决方案**:
1. 日期获取加 try/except 保护，失败时设为 None
2. 所有操作方法用 `_safe_exec()` 包装，捕获所有异常以弹窗形式输出
3. `main.py` 设置 `sys.excepthook = global_exception_handler`，全局兜底

### 2.7 PDF 导出中文乱码

**问题**: reportlab 默认使用 Helvetica 字体，不支持中文字符，导出的 PDF 中文显示为空白或方块。

**解决方案**: 自动查找系统中文字体 (`msyh.ttc` 微软雅黑)，通过 `pdfmetrics.registerFont()` 注册，应用到所有 Paragraph 样式和 Table 的 `FONTNAME` 属性：
```python
font_path = _find_chinese_font()  # 查找 C:/Windows/Fonts/msyh.ttc
pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
```

### 2.8 exe 文件图标未生效

**问题**: 任务栏图标生效但 exe 文件本身仍显示 PyInstaller 默认图标。

**根因**: 1) ICO 文件尺寸不完整；2) `resource_path()` 在 PyInstaller `_MEIPASS` 下路径不正确。

**解决方案**:
1. 重新生成包含 7 种尺寸 (16/24/32/48/64/128/256) 的 ICO 文件
2. 修正 `resource_path()` 在打包后指向 `sys._MEIPASS/aura_tasks_pro/resources/`
3. spec 文件中 `icon=` 指向 ICO 绝对路径，`datas` 包含 resources 目录

### 2.9 UI 风格迭代历程

| 阶段 | 风格 | 问题 |
|------|------|------|
| V1 | FluentWindow 默认样式 | 界面老气，缺乏设计感 |
| V2 | Apple 浅色风格 | 半透明但缺乏暗色对比度 |
| V3 | Apple 暗色风格 | 暗色但配色不够协调 |
| V4 | **Monokai Pro** | ✅ 最终方案，VSCode 经典暗色主题，绿/粉/橙/青/紫五色体系 |

### 2.10 打包体积

单文件 exe 约 105MB，主要组成：
- PyQt6 + Qt6 运行时: ~60MB
- qfluentwidgets + 资源: ~15MB
- Python 解释器: ~15MB
- openpyxl + reportlab + pillow: ~15MB

---

## 三、快速使用指南

### 3.1 开发环境

```bash
conda create -n auratasks python=3.12 -y
conda activate auratasks
pip install PyQt6 PyQt6-Qt6 PyQt6-sip PyQt6-Fluent-Widgets openpyxl reportlab pyinstaller
python run.py
```

### 3.2 打包

```bash
pyinstaller --noconfirm AuraTasksPro.spec
# 输出: dist/AuraTasksPro.exe
```

### 3.3 缓存清理

数据库位置: `%APPDATA%\AuraTasksPro\tasks.db`
删除即可清空所有任务数据。
