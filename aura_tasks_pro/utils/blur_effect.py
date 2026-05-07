"""Windows 11 Acrylic / 毛玻璃模糊效果。
使用 DWM API 为窗口启用亚克力模糊 (SWCA) 或 Mica 效果。
若 API 不可用则优雅降级为半透明背景。
"""
import sys
import ctypes
from ctypes import wintypes, Structure, POINTER, byref, sizeof, c_int, c_uint, c_void_p
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt


class ACCENT_POLICY(Structure):
    _fields_ = [
        ("AccentState", ctypes.c_uint),
        ("AccentFlags", ctypes.c_uint),
        ("GradientColor", ctypes.c_uint),
        ("AnimationId", ctypes.c_uint),
    ]


class WINDOWCOMPOSITIONATTRIBDATA(Structure):
    _fields_ = [
        ("Attrib", ctypes.c_uint),
        ("pvData", ctypes.POINTER(ACCENT_POLICY)),
        ("cbData", ctypes.c_size_t),
    ]


WCA_ACCENT_POLICY = 19
ACCENT_ENABLE_ACRYLICBLURBEHIND = 4
ACCENT_ENABLE_HOSTBACKDROP = 5


def enable_acrylic(widget: QWidget, gradient_color: int = 0x99000000):
    """为 QWidget 启用 Windows 11 亚克力模糊效果。
    gradient_color: AABBGGRR 格式的颜色值 (前两位为透明度)。
    """
    if sys.platform != "win32":
        return False
    try:
        hwnd = int(widget.winId())
        user32 = ctypes.windll.user32
        set_window_composition_attribute = user32.SetWindowCompositionAttribute
        set_window_composition_attribute.argtypes = [
            wintypes.HWND,
            POINTER(WINDOWCOMPOSITIONATTRIBDATA),
        ]
        set_window_composition_attribute.restype = wintypes.BOOL

        accent = ACCENT_POLICY()
        accent.AccentState = ACCENT_ENABLE_ACRYLICBLURBEHIND
        accent.AccentFlags = 2
        accent.GradientColor = gradient_color
        accent.AnimationId = 0

        data = WINDOWCOMPOSITIONATTRIBDATA()
        data.Attrib = WCA_ACCENT_POLICY
        data.pvData = ctypes.pointer(accent)
        data.cbData = sizeof(accent)

        result = set_window_composition_attribute(hwnd, byref(data))
        return bool(result)
    except Exception:
        return False


def enable_mica(widget: QWidget):
    """尝试启用 Windows 11 Mica 效果（比 Acrylic 更轻量）。"""
    if sys.platform != "win32":
        return False
    try:
        hwnd = int(widget.winId())
        user32 = ctypes.windll.user32
        set_window_composition_attribute = user32.SetWindowCompositionAttribute
        set_window_composition_attribute.argtypes = [
            wintypes.HWND,
            POINTER(WINDOWCOMPOSITIONATTRIBDATA),
        ]
        set_window_composition_attribute.restype = wintypes.BOOL

        accent = ACCENT_POLICY()
        accent.AccentState = ACCENT_ENABLE_HOSTBACKDROP
        accent.AccentFlags = 2
        accent.GradientColor = 0x00000000
        accent.AnimationId = 0

        data = WINDOWCOMPOSITIONATTRIBDATA()
        data.Attrib = WCA_ACCENT_POLICY
        data.pvData = ctypes.pointer(accent)
        data.cbData = sizeof(accent)

        result = set_window_composition_attribute(hwnd, byref(data))
        return bool(result)
    except Exception:
        return False
