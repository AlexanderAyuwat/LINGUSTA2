@echo off
echo Preparing to upload your real code to the new LINGUSTA2 repository...

:: Initialize Git if not already done
git init

:: Remove the old origin link and add the new one
git remote remove origin 2>nul
git remote add origin https://github.com/AlexanderAyuwat/LINGUSTA2.git

:: Set branch to main and package files
git branch -M main
git add .

echo.
echo Committing everything...
git commit -m "Upload real source code to LINGUSTA2"

echo.
echo Pushing to GitHub (this might take a second)...
git push -u origin main

echo.
echo Done! Your code is now live on https://github.com/AlexanderAyuwat/LINGUSTA2
pause
