@echo off
cd ./
REM 使用UTF-8编码，避免参数传进去时中文显示乱码
chcp 65001

set CFGS=./config.json
set PORT=5004

start python main.py --cfgs %CFGS% --port %PORT%