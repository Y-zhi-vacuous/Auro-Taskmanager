import sys
import os
import traceback
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon
from aura_tasks_pro.views.main_window import MainWindow
from aura_tasks_pro.utils.path_utils import resource_path


def global_exception_handler(exc_type, exc_value, exc_tb):
    """全局异常捕获：所有未处理异常以弹窗形式输出，不让应用崩溃。"""
    tb_text = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print(tb_text, file=sys.stderr)
    try:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("AuraTasks Pro - 错误")
        msg.setText(f"发生未预期的错误：\n{exc_value}")
        msg.setDetailedText(tb_text)
        msg.exec()
    except Exception:
        pass


def main():
    sys.excepthook = global_exception_handler

    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    font = QFont("Microsoft YaHei", 13)
    font.setHintingPreference(QFont.HintingPreference.PreferVerticalHinting)
    app.setFont(font)

    icon_path = resource_path("app_icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    try:
        window = MainWindow()
        if os.path.exists(icon_path):
            window.setWindowIcon(QIcon(icon_path))
        window.show()
    except Exception as e:
        QMessageBox.critical(None, "启动失败", f"应用启动失败：\n{e}\n\n{traceback.format_exc()}")
        sys.exit(1)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
