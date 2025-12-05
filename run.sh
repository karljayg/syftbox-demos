cat > run.sh << 'EOF'
#!/usr/bin/env bash
set -e

# SyftBox sets these env vars when running the app:
#   SYFTBOX_APP_DIR  - path to this app's directory
#   SYFTBOX_PYTHON   - Python interpreter inside the sandbox

cd "$SYFTBOX_APP_DIR"
"$SYFTBOX_PYTHON" main.py
EOF

