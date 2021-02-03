@echo off
cd ./
REM 使用UTF-8编码，避免参数传进去时中文显示乱码
chcp 65001

set PROJECT=枪战3
set ROOT=I:/newQz/client/yxqz/
set PROTO=http://192.168.61.142:8080/ProtocolNewQZ/
set CFG=I:/newQz/策划/配置表/
set PORT=5001

start python main.py --project %PROJECT% --root %ROOT% --proto %PROTO% --cfg %CFG% --port %PORT%