#!/usr/bin/env bash
# Wrapper for robot_controller.py — finds Python 3.10+ automatically.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

for py in \
  "$PYTHON3" \
  "$HOME/miniconda3/bin/python3" \
  "$HOME/anaconda3/bin/python3" \
  "$HOME/.pyenv/shims/python3" \
  "$(brew --prefix 2>/dev/null)/bin/python3" \
  python3.12 python3.11 python3.10 python3
do
  [ -z "$py" ] && continue
  if command -v "$py" &>/dev/null; then
    minor=$("$py" -c "import sys; print(sys.version_info.minor)" 2>/dev/null)
    major=$("$py" -c "import sys; print(sys.version_info.major)" 2>/dev/null)
    if [ "$major" -ge 3 ] && [ "$minor" -ge 10 ]; then
      exec "$py" "$SCRIPT_DIR/robot_controller.py" "$@"
    fi
  fi
done

echo '{"error": "No Python 3.10+ found. Install miniconda or run setup.sh."}' >&2
exit 1
