#!/bin/bash
# Bash script to install dependencies with proper numpy handling
# This script installs numpy first to let pip find the best version for Python 3.13

echo "Installing numpy first (to find Python 3.13 compatible version)..."
pip install --upgrade pip
pip install numpy

echo "Installing remaining dependencies..."
pip install -r requirements.txt

echo "Installation complete!"

