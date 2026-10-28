@echo off
REM 一键打包成 exe（Windows）
pip install -r requirements.txt
pip install pyinstaller
pyinstaller -w -F -i icon.ico --name "桌面企鹅" pet.py
echo 打包完成，exe 在 dist/ 目录
pause
