@echo off
setlocal
if defined R420_PYTHON (
    "%R420_PYTHON%" -B "%~dp0verify.py" %*
) else (
    py -3 -B "%~dp0verify.py" %*
)
set "R420_EXIT=%ERRORLEVEL%"
if not "%R420_EXIT%"=="0" echo Verification failed. See README.md for dependency installation.
if not "%R420_NO_PAUSE%"=="1" pause
exit /b %R420_EXIT%
