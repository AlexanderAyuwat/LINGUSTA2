@echo off
echo Adding files to Git...
git add .
echo.
echo Committing changes...
git commit -m "Upload latest changes"
echo.
echo Pushing to GitHub...
git push
echo.
echo All done! You can close this window now.
pause
