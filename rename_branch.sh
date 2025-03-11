#!/bin/bash
# Script to rename the master branch to main

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "Git is not installed. Please install Git first."
    exit 1
fi

# Check if we're in a git repository
if ! git rev-parse --is-inside-work-tree &> /dev/null; then
    echo "This is not a Git repository. Please run this script from within a Git repository."
    exit 1
fi

# Get the current branch name
current_branch=$(git branch --show-current)
echo "Current branch: $current_branch"

# Check if master branch exists
if ! git show-ref --verify --quiet refs/heads/master; then
    echo "No 'master' branch found. It might already be renamed or never existed."
    exit 1
fi

echo "Renaming 'master' branch to 'main'..."

# Create main branch at the same point as master
git branch -m master main

# Push the new main branch to remote (if remote exists)
if git remote -v | grep -q origin; then
    echo "Pushing 'main' branch to remote..."
    git push -u origin main

    # Delete the old master branch from remote
    echo "Deleting 'master' branch from remote..."
    git push origin --delete master
    
    echo "Remote branch updated successfully."
else
    echo "No remote repository found. Only local branch has been renamed."
fi

echo "Branch successfully renamed from 'master' to 'main'."
echo "If you're using GitHub, don't forget to update the default branch in repository settings." 