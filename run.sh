#!/usr/bin/env bash
set -e

# Navigate to the app directory SyftBox provides
cd "$SYFTBOX_APP_DIR"

# Select a Python interpreter
if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN=python3
elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN=python
else
    echo "Error: No Python interpreter found."
    exit 1
fi

# Execute the app
"$PYTHON_BIN" main.py

