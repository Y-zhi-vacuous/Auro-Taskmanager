"""AuraTasks Pro 主题 — 现代浅色暖白设计。

色彩体系：
- 背景: 暖白层级 (#F5F5F7 → #FFFFFF)
- 强调: 电光蓝 (#3B82F6)
- 语义: 翠绿成功 / 琥珀警告 / 柔红危险
- 优先级: 灰→青→蓝→橙→红 五级热力梯度
"""


class AppleTheme:
    # ─── 背景层级 ────────────────────────────────────────
    WINDOW_BG = "#F2F3F5"
    SIDEBAR_BG = "rgba(235, 236, 240, 0.95)"
    EDITOR_BG = "#FFFFFF"
    EDITOR_BG_SEMI = "rgba(255, 255, 255, 0.92)"
    CARD_BG = "rgba(255, 255, 255, 0.85)"
    CARD_BG_SOLID = "#FFFFFF"
    SURFACE_BG = "rgba(245, 245, 247, 0.70)"
    CARD_BORDER = "rgba(0, 0, 0, 0.06)"
    TOOLBAR_BG = "rgba(250, 250, 252, 0.90)"
    TITLEBAR_BG = "rgba(242, 243, 245, 0.95)"

    # ─── 文字 ────────────────────────────────────────────
    TEXT_PRIMARY = "#1A1D28"
    TEXT_SECONDARY = "#6B7280"
    TEXT_TERTIARY = "#9CA3AF"
    TEXT_DISABLED = "#D1D5DB"

    # ─── 语义色 ──────────────────────────────────────────
    ACCENT = "#3B82F6"            # 电光蓝
    ACCENT_HOVER = "#2563EB"      # 深蓝
    ACCENT_LIGHT = "rgba(59, 130, 246, 0.10)"
    ACCENT_SOFT = "rgba(59, 130, 246, 0.06)"

    PINK = "#EF4444"              # 柔红
    ORANGE = "#F59E0B"            # 琥珀
    CYAN = "#06B6D4"              # 青
    PURPLE = "#8B5CF6"            # 紫
    YELLOW = "#EAB308"            # 金

    # ─── 语义别名 ────────────────────────────────────────
    SUCCESS = "#10B981"           # 翠绿
    WARNING = "#F59E0B"           # 琥珀
    DANGER = "#EF4444"            # 柔红
    INFO = "#3B82F6"              # 蓝

    # ─── 优先级色彩 ─────────────────────────────────────
    PRIORITY_COLORS = {
        1: "#9CA3AF",             # 极低 - 浅灰
        2: "#06B6D4",             # 低   - 青
        3: "#3B82F6",             # 中   - 蓝
        4: "#F59E0B",             # 高   - 琥珀
        5: "#EF4444",             # 紧急 - 红
    }

    # ─── 圆角 ────────────────────────────────────────────
    RADIUS_WINDOW = 12
    RADIUS_CARD = 10
    RADIUS_BUTTON = 8
    RADIUS_INPUT = 6

    # ─── 字体 ────────────────────────────────────────────
    FONT_FAMILY = '"Microsoft YaHei", "PingFang SC", "Inter", "SF Pro Display", sans-serif'
    FONT_SIZE_TITLE = 18
    FONT_SIZE_SUBTITLE = 14
    FONT_SIZE_BODY = 13
    FONT_SIZE_SMALL = 11

    # ─── 状态 ────────────────────────────────────────────
    STATUS_COLORS = {
        "待办": ("#6B7280", "rgba(107,114,128,0.12)"),
        "进行中": ("#3B82F6", "rgba(59,130,246,0.12)"),
        "已完成": ("#10B981", "rgba(16,185,129,0.12)"),
        "已挂起": ("#F59E0B", "rgba(245,158,11,0.12)"),
    }

    # ─── Glassmorphism ──────────────────────────────────
    GLASS_BG = "rgba(255, 255, 255, 0.82)"
    GLASS_BG_LIGHT = "rgba(250, 250, 252, 0.70)"
    GLASS_BG_DARK = "rgba(242, 243, 245, 0.92)"
    GLASS_BORDER = "rgba(59, 130, 246, 0.18)"
    GLASS_BORDER_SUBTLE = "rgba(0, 0, 0, 0.06)"
    GLASS_BLUR = 20
    GLASS_SHADOW = "0 1px 3px rgba(0, 0, 0, 0.06), 0 8px 24px rgba(0, 0, 0, 0.04)"

    # ─── Bento Grid ─────────────────────────────────────
    RADIUS_BENTO = 14
    RADIUS_BENTO_INNER = 10
    BENTO_PADDING = 16
    BENTO_GAP = 14

    # ─── TOP3 ───────────────────────────────────────────
    TOP1_BG = "rgba(59, 130, 246, 0.08)"
    TOP1_BORDER = "rgba(59, 130, 246, 0.30)"
    TOP2_BG = "rgba(6, 182, 212, 0.06)"
    TOP2_BORDER = "rgba(6, 182, 212, 0.25)"
    TOP3_BG = "rgba(245, 158, 11, 0.06)"
    TOP3_BORDER = "rgba(245, 158, 11, 0.22)"
    DANGER_BG = "rgba(239, 68, 68, 0.08)"
    DANGER_BORDER = "rgba(239, 68, 68, 0.30)"
