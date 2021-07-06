@echo off
cd ./
REM 使用UTF-8编码，避免参数传进去时中文显示乱码
chcp 65001

set CFGS=./config_sg1.json
set PORT=5005

python main.py --cfgs %CFGS% --port %PORT%