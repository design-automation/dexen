title "Dexen node"
@echo off
%~d0
cd %~dp0\..\scripts\
@echo on
python dexen_node.py %*