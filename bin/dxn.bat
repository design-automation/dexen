@echo on
c:
mkdir -p "%temp%/dexen_db"
start mongod --dbpath %temp%/dexen_db
timeout 5

REM start db --log-path dexen_server_backend.log
REM timeout 5
REM start df --log-path dexen_server_frontend.log
REM timeout 5
REM start dn --log-path dexen_node.log
REM timeout 5

title "Dexen"
@echo off
%~d0
cd %~dp0\..\scripts\
@echo on
python dexen_all.py --log-path dexen.log
