# AuraTasks Pro UI 重构 + 功能增强 设计文档

**日期**: 2026-05-06
**版本**: 1.0

---

## 1. 概述

在现有 AuraTasks Pro 任务管理工具基础上，进行 UI 全面重构和新功能开发：
- UI 风格升级为 **Glassmorphism + Bento Grid 卡片布局**
- 任务属性支持树内直接编辑（始终可见控件）
- 同层级任务支持鼠标拖拽排序
- 底部 TOP3 关键任务高亮卡片

## 2. UI 风格系统

### 2.1 整体风格

Glassmorphism 底层 + Bento 模块卡片布局：
- 各功能区独立 Glass Card（半透明背景 + 圆角 + 发光边框）
- 多层毛玻璃景深效果（侧栏 → 主区 → Top3 → 底栏，透明度逐层增加）
- Monokai Pro 暗色调色板保留（绿色 #A6E22A 作为强调色）

### 2.2 布局架构

```
Glass 顶栏：标题 + 搜索 + 排序
┌─ 左侧 Bento Card ─┬─ 主区 Bento Card ──────────────┐
│ 快捷操作按钮        │ 任务树 (QTreeWidget)            │
│                   │  进度 | 状态▼ | 优先级▼ | 风险  │
│ 统计信息           │  ← 列中直接嵌入编辑控件          │
├───────────────────┼────────────────────────────────┤
│ 底栏 Card: 🔴 TOP3 关键任务                          │
│ 🥇 Top1 / 🥈 Top2 / 🥉 Top3                         │
└────────────────────────────────────────────────────┘
```

### 2.3 卡片样式规范

- 背景: `rgba(35, 33, 36, 0.7)` 到 `rgba(25, 23, 26, 0.5)` 渐变
- 边框: `1px solid rgba(166, 226, 42, 0.15)` 到 `rgba(255, 255, 255, 0.08)`
- 圆角: 卡片 `12px`，按钮/输入 `8px`
- 模糊: `backdrop-filter: blur(20px)` (Windows Acrylic / DWM API)
- 阴影: 外发光 `0 8px 32px rgba(0, 0, 0, 0.4)`

## 3. 功能一：树内直接编辑

### 3.1 交互设计

任务属性始终显示为可操作控件，无需进入编辑对话框：

| 列 | 控件类型 | 交互 |
|---|---|---|
| 进度 | `QClickableProgressBar` (自定义) | 点击即设置百分比，支持拖拽滑块 |
| 状态 | `QComboBox` | 下拉选择即保存 |
| 优先级 | `QComboBox` | 下拉选择即保存，选项带对应颜色标识 |
| 风险 | `QLineEdit` | 输入文本 500ms 防抖后自动保存 |

### 3.2 实现方案

- 使用 `QTreeWidget.setItemWidget()` 在对应列嵌入控件
- 各控件连接 `currentIndexChanged` / `editingFinished` / slider `valueChanged` 信号
- 信号处理函数调用 `TaskService.update_task()` 写入数据库
- 风险输入框使用 `QTimer` 做 500ms 防抖
- 名称和备注列保留双击弹出编辑对话框的行为

### 3.3 动态刷新

- 编辑控件的值变更 → `refresh_tree()` 重绘整棵树
- 优先级变更后，同行的优先级列前景色即时更新
- 进度变更后，父任务的进度条（Delegate）同步重新计算

## 4. 功能二：拖拽排序

### 4.1 交互规则

- 仅允许同层级（同 parent_id）任务之间拖拽交换顺序
- 拖拽视觉反馈：插入位置显示绿色高亮线

### 4.2 实现方案

```python
# 启用内部拖拽
self.tree.setDragEnabled(True)
self.tree.setAcceptDrops(True)
self.tree.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
self.tree.setDefaultDropAction(Qt.DropAction.MoveAction)
```

- 重写 `MainWindow.dropEvent()` 或继承 `QTreeWidget` 重写 `dropEvent()`
- 在 drop 前检查合法性：drag item 与 drop target 的 parent 是否一致
- 若合法则执行默认 drop，然后调用 `TaskService.reorder_siblings(parent_id, [new_order])`
- 若不合法（跨层级）则取消 drop，不执行任何操作

### 4.3 视觉反馈

- 拖拽中 item 显示半透明
- 有效 drop 位置显示绿色 accent 色插入线
- 无效 drop 位置光标变为禁止符号

## 5. 功能三：TOP3 关键任务

### 5.1 评分公式

复用 `TaskService.compute_score()`：

```
Score = Priority × 10 - DaysToDeadline + RiskWeight

RiskWeight: {"高":5, "严重":8, "紧急":10, "critical":10, "high":5}
```

### 5.2 计算与展示逻辑

1. `TaskService.get_top3()` 遍历所有任务（含子任务），逐个计算 score
2. 按 score 降序排序，取前 3（任务不足 3 个则显示实际数量）
3. 对每个 top task 构建完整祖先路径字符串：`根任务 → 子任务 → ...`
4. 每个 Top 项展示：排名奖牌、路径、风险等级、截止日期、距今天数

### 5.3 UI 渲染

底部 Glass Card，3 行等高排列（或少于 3 行居中）：

```
🥇 Top1: 核心功能 - 登录模块  │  风险:严重  │  截止: 05/03  │  已逾期 3 天
🥈 Top2: 数据导出 - PDF导出   │  风险:高    │  截止: 05/08  │  剩余 2 天
🥉 Top3: UI重构 - 暗色主题   │  风险:中    │  截止: 05/15  │  剩余 9 天
```

- 每行背景透明度按排名递减（Top1 最高光）
- Top1 项边缘带脉冲呼吸动画（`QPropertyAnimation`）
- 点击任意 Top 项 → 自动定位到树中对应任务

### 5.4 刷新时机

- `refresh_tree()` 时同步刷新 TOP3 面板
- 任何任务编辑后自动重新计算

## 6. 文件变更清单

| 文件 | 变更类型 | 说明 |
|---|---|---|
| `aura_tasks_pro/views/main_window.py` | **重写** | 新布局、拖拽、内联编辑、Top3 面板 |
| `aura_tasks_pro/views/edit_dialog.py` | 保留 | 仅名称/备注编辑用 |
| `aura_tasks_pro/utils/apple_theme.py` | 增强 | 新增 Glass/Bento 卡片样式常量 |
| `aura_tasks_pro/delegates/task_delegates.py` | 增强 | 可点击进度条委托 |
| `aura_tasks_pro/services/task_service.py` | 增强 | 新增 `get_top3()` 方法 |
| `aura_tasks_pro/models/task.py` | 不变 | 现有模型足够 |

## 7. 边缘情况与约束

- 空数据库：显示空状态提示，TOP3 区域显示"暂无任务"
- 任务 < 3 个：TOP3 只显示实际数量
- 所有任务已完成：TOP3 正常显示（以完成作为优先级的任务也可能为最高风险）
- 拖拽跨层级：静默拒绝，不做任何操作
- 内联编辑触发刷新时：保留搜索/排序状态
- Windows 7/非 Win11：毛玻璃降级为纯色半透明

## 8. 验收清单

- [ ] 顶栏、侧栏、任务树、TOP3 四个区域均为独立 Glass Card
- [ ] 任务树中状态列、优先级列为下拉框，可直接选择
- [ ] 任务树中进度列可点击/拖拽直接修改
- [ ] 任务树中风险列可直接输入文字编辑
- [ ] 同层级任务可拖拽排序，跨层级拖拽被拒绝
- [ ] 底部显示 TOP3 关键任务，含路径、风险、截止日期
- [ ] 所有编辑操作触发自动保存
- [ ] 毛玻璃效果在 Windows 11 上正常显示
