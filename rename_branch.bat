@echo off
REM Script to rename the master branch to main

REM Check if git is installed
where git >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Git is not installed. Please install Git first.
    exit /b 1
)

REM Check if we're in a git repository
git rev-parse --is-inside-work-tree >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo This is not a Git repository. Please run this script from within a Git repository.
    exit /b 1
)

REM Get the current branch name
for /f "tokens=*" %%a in ('git branch --show-current') do set current_branch=%%a
echo Current branch: %current_branch%

REM Check if master branch exists
git show-ref --verify --quiet refs/heads/master
if %ERRORLEVEL% NEQ 0 (
    echo No 'master' branch found. It might already be renamed or never existed.
    exit /b 1
)

echo Renaming 'master' branch to 'main'...

REM Create main branch at the same point as master
git branch -m master main

REM Check if remote exists
git remote -v | findstr origin >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Pushing 'main' branch to remote...
    git push -u origin main

    echo Deleting 'master' branch from remote...
    git push origin --delete master
    
    echo Remote branch updated successfully.
) else (
    echo No remote repository found. Only local branch has been renamed.
)

echo Branch successfully renamed from 'master' to 'main'.
echo If you're using GitHub, don't forget to update the default branch in repository settings.

pause 