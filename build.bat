# AuraTasks Pro 打包脚本

## 方式一：Nuitka（推荐，性能更好）
# nuitka --standalone --onefile --enable-qt=pyqt6 --windows-disable-console --output-filename=AuraTasksPro.exe run.py

## 方式二：PyInstaller
# pyinstaller --noconfirm --onefile --windowed --name AuraTasksPro run.py
