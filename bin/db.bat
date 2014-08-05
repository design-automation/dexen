title "Dexen server backend"
@echo off
%~d0
cd %~dp0\..\scripts\
@echo on
python dexen_server_backend.py %*