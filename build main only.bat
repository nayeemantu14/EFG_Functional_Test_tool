@echo off
DEL /s/q EFG_Test_tool.exe
copy NUL EFG_Test_tool.temp
C:\Users\nayeen.antu\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\local-packages\Python312\Scripts\pyinstaller.exe main.py -F --distpath ./ -n EFG_Test_tool --add-data binaries/EFG.hex; binaries/
rmdir /s/q __pycache__
rmdir /s/q build
DEL /s/q EFG_Test_tool.spec
DEL /s/q EFG_Test_tool.temp
pause