@echo off
git pull origin master > NUL 2>&1
cd "C:\Program Files\HasulamLessonNameManager"
"C:\Python27\python.exe" "C:\Program Files\HasulamLessonNameManager\OpenWME.py"
cd "C:\Users\Administrator\Desktop\HodsRecorder"
start "C:\Python27\python.exe" "C:\Users\Administrator\Desktop\HodsRecorder\HasulamRecorder.py"
"C:\Program Files (x86)\HasulamRecorderButton\RecorderGUI.exe"