#!/bin/bash
# a small script to set up contributors' development environment

echo "# ----------------------------------------------------------------------------"
echo "# Setup development Python environment"
echo "# ----------------------------------------------------------------------------"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip

echo "# ----------------------------------------------------------------------------"
echo "# Install modules from requirements.txt and requirements.dev.txt"
echo "# ----------------------------------------------------------------------------"
pip install -r requirements.txt
pip install -r requirements.dev.txt
python setup.py develop

echo "# ----------------------------------------------------------------------------"
echo "# Install pre-commit hooks"
echo "# ----------------------------------------------------------------------------"
pre-commit install

echo "# ----------------------------------------------------------------------------"
echo "# Create new branch"
echo "# ----------------------------------------------------------------------------"
echo "Type the name of your new branch, followed by [ENTER]:"
read NEW_BRANCH_NAME
git checkout -b "${NEW_BRANCH_NAME}"

echo "# ----------------------------------------------------------------------------"
echo "# Bump version and stage changes"
echo "# ----------------------------------------------------------------------------"
bumpversion build --no-commit

git status
