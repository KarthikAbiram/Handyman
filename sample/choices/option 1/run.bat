@echo off
pushd "%~dp0"
REM Made this folder as current working directory

..\..\handyman.exe rename RenameList.csv

REM Switching back
popd