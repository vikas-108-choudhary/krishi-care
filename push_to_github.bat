@echo off
cd /d "c:\CropApp - Copy"
"C:\Program Files\Git\bin\git.exe" init
"C:\Program Files\Git\bin\git.exe" config user.email "admin@krishicare.com"
"C:\Program Files\Git\bin\git.exe" config user.name "KrishiCare Admin"
"C:\Program Files\Git\bin\git.exe" add .
"C:\Program Files\Git\bin\git.exe" commit -m "Initial commit: KrishiCare AI agricultural disease detection system"
"C:\Program Files\Git\bin\git.exe" branch -M main
"C:\Program Files\Git\bin\git.exe" remote add origin https://github.com/vikas-108-choudhary/krishi-care.git
"C:\Program Files\Git\bin\git.exe" push -u origin main
pause
