@echo off
REM Simple script to run a job search on Windows
REM Usage: run_job_search.bat

echo ======================================
echo LinkedIn Job Search
echo ======================================
echo.

REM Activate virtual environment
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo Error: Virtual environment not found!
    echo Please run: python -m venv venv
    pause
    exit /b 1
)

REM Prompt for job search details
set /p job_title="What job title are you looking for? "
echo.

set /p location="Where? (Leave blank for 'Any location') "
echo.

set /p num_jobs="How many jobs? (Default: 25) "
if "%num_jobs%"=="" set num_jobs=25
echo.

set /p remote="Remote jobs only? (y/n) "
echo.

set /p easy_apply="Easy Apply only? (y/n) "
echo.

REM Build command
set cmd=python scrape_jobs.py "%job_title%"

if not "%location%"=="" (
    set cmd=%cmd% -l "%location%"
)

set cmd=%cmd% -n %num_jobs%

if /i "%remote%"=="y" (
    set cmd=%cmd% --remote
)

if /i "%easy_apply%"=="y" (
    set cmd=%cmd% --easy-apply
)

echo ======================================
echo Running search...
echo ======================================
echo.

REM Run the command
%cmd%

echo.
echo ======================================
echo Search complete!
echo Check your Notion database for results
echo ======================================
echo.
pause
