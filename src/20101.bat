@echo off
python setup.py py2exe
echo === === === === === === ===
copy /Y dist\yyaddondraw.exe  "%appdata%\duowan\yy4.0\addons\10004\20101"
copy /Y dist\library.zip  "%appdata%\duowan\yy4.0\addons\10004\20101"
echo === === === === === === === 
time /t
