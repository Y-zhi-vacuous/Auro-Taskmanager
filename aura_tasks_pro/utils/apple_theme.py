"""AuraTasks Pro — UI-UX-Pro-Max Generated Design System.

Style:     Micro-interactions + Modern Clean
Product:   Productivity Tool
Palette:   Teal primary (#0D9488), mint background (#F0FDFA), orange CTA (#F97316)
Typography: Modern sans-serif, clean hierarchy
"""


class AppleTheme:
    # ─── 背景层次 (Mint → White) ───────────────────────
    WINDOW_BG = "#F0FDFA"
    SIDEBAR_BG = "rgba(240, 253, 250, 0.95)"
    EDITOR_BG = "#FFFFFF"
    EDITOR_BG_SEMI = "rgba(255, 255, 255, 0.94)"
    CARD_BG = "rgba(255, 255, 255, 0.88)"
    CARD_BG_SOLID = "#FFFFFF"
    SURFACE_BG = "rgba(248, 252, 251, 0.75)"
    CARD_BORDER = "rgba(13, 148, 136, 0.08)"
    TOOLBAR_BG = "rgba(252, 254, 253, 0.92)"
    TITLEBAR_BG = "rgba(240, 253, 250, 0.96)"

    # ─── 文字 (Dark Teal hierarchy) ────────────────────
    TEXT_PRIMARY = "#134E4A"
    TEXT_SECONDARY = "#5F8B86"
    TEXT_TERTIARY = "#8AAAA5"
    TEXT_DISABLED = "#B8CFCB"

    # ─── 语义色 (Teal family) ──────────────────────────
    ACCENT = "#0D9488"            # Teal-600
    ACCENT_HOVER = "#0F766E"      # Teal-700
    ACCENT_LIGHT = "rgba(13, 148, 136, 0.10)"
    ACCENT_SOFT = "rgba(13, 148, 136, 0.06)"

    PINK = "#EF4444"              # Red-500 (danger)
    ORANGE = "#F97316"            # Orange-500 (warning / CTA)
    CYAN = "#06B6D4"              # Cyan-500 (info)
    PURPLE = "#8B5CF6"            # Violet-500 (special)
    YELLOW = "#EAB308"            # Yellow-500 (attention)

    # ─── 语义别名 ──────────────────────────────────────
    SUCCESS = "#10B981"           # Emerald-500
    WARNING = "#F97316"           # Orange-500
    DANGER = "#EF4444"            # Red-500
    INFO = "#0D9488"              # Teal-600

    # ─── 优先级 (5-level gradient) ────────────────────
    PRIORITY_COLORS = {
        1: "#94A3B8",             # Slate-400 (极低)
        2: "#64748B",             # Slate-500 (低)
        3: "#0D9488",             # Teal-600 (中)
        4: "#F97316",             # Orange-500 (高)
        5: "#EF4444",             # Red-500 (紧急)
    }

    # ─── 圆角 ──────────────────────────────────────────
    RADIUS_WINDOW = 14
    RADIUS_CARD = 12
    RADIUS_BUTTON = 8
    RADIUS_INPUT = 6

    # ─── 字体 ──────────────────────────────────────────
    FONT_FAMILY = '"Microsoft YaHei", "PingFang SC", "Inter", sans-serif'
    FONT_SIZE_TITLE = 18
    FONT_SIZE_SUBTITLE = 14
    FONT_SIZE_BODY = 13
    FONT_SIZE_SMALL = 11

    # ─── 状态标签 ─────────────────────────────────────
    STATUS_COLORS = {
        "待办": ("#94A3B8", "rgba(148,163,184,0.12)"),
        "进行中": ("#0D9488", "rgba(13,148,136,0.12)"),
        "已完成": ("#10B981", "rgba(16,185,129,0.12)"),
        "已挂起": ("#F59E0B", "rgba(245,158,11,0.12)"),
    }

    # ─── Glass/Card ───────────────────────────────────
    GLASS_BG = "rgba(255, 255, 255, 0.85)"
    GLASS_BG_LIGHT = "rgba(252, 254, 253, 0.72)"
    GLASS_BG_DARK = "rgba(240, 253, 250, 0.94)"
    GLASS_BORDER = "rgba(13, 148, 136, 0.20)"
    GLASS_BORDER_SUBTLE = "rgba(13, 148, 136, 0.08)"
    GLASS_BLUR = 16
    GLASS_SHADOW = (
        "0 1px 2px rgba(19, 78, 74, 0.04), "
        "0 4px 16px rgba(19, 78, 74, 0.06)"
    )

    # ─── Bento ────────────────────────────────────────
    RADIUS_BENTO = 16
    RADIUS_BENTO_INNER = 10
    BENTO_PADDING = 18
    BENTO_GAP = 14

    # ─── TOP3 ─────────────────────────────────────────
    TOP1_BG = "rgba(13, 148, 136, 0.08)"
    TOP1_BORDER = "rgba(13, 148, 136, 0.30)"
    TOP2_BG = "rgba(6, 182, 212, 0.06)"
    TOP2_BORDER = "rgba(6, 182, 212, 0.22)"
    TOP3_BG = "rgba(249, 115, 22, 0.06)"
    TOP3_BORDER = "rgba(249, 115, 22, 0.22)"
    DANGER_BG = "rgba(239, 68, 68, 0.08)"
    DANGER_BORDER = "rgba(239, 68, 68, 0.28)"
