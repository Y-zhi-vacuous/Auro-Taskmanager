import sys
import os
from pathlib import Path


def resource_path(relative_path: str) -> str:
    """兼容 PyInstaller / Nuitka 的资源路径解析函数。
    打包后资源位于 sys._MEIPASS/aura_tasks_pro/resources/ 下；
    开发环境下从项目源码 resources/ 子目录查找。
    """
    if hasattr(sys, '_MEIPASS'):
        base_path = Path(sys._MEIPASS) / "aura_tasks_pro" / "resources"
    elif getattr(sys, 'frozen', False):
        base_path = Path(sys.executable).parent / "aura_tasks_pro" / "resources"
    else:
        base_path = Path(__file__).resolve().parent.parent / "resources"
    return str(base_path / relative_path)


def get_db_path() -> str:
    """将数据库文件放在用户 AppData 目录下，避免权限问题。"""
    if sys.platform == 'win32':
        app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
        db_dir = Path(app_data) / "AuraTasksPro"
    else:
        db_dir = Path.home() / ".aurataskspro"
    db_dir.mkdir(parents=True, exist_ok=True)
    return str(db_dir / "tasks.db")
