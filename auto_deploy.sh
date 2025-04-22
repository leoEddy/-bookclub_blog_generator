#!/usr/bin/env bash

# Read ISBN(s) passed as arguments
ISBN_ARGS="$@"

# 1) Change into the blog generator project directory
cd ~/Documents/Python/bookclub_blog_generator

# 2) Activate your virtual environment (adjust this path if your venv is located elsewhere)
source ../venv/bin/activate

# 3) Pass ISBN(s) to the generator script
python3 generator.py $ISBN_ARGS

# 4) Stage, commit, and push any new posts to GitHub
git add .
git commit -m "Update blog content"
git push
