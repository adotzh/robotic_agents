#!/usr/bin/env bash
set -e

echo "=== Robotics Hackathon Setup ==="

# Load .env if present
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
  echo "✓ Loaded .env"
else
  echo "⚠ No .env found — copy .env.example to .env and fill in your tokens first."
  exit 1
fi

# Validate required env vars
for var in TELEGRAM_BOT_TOKEN CYBERWAVE_TWIN_ID CYBERWAVE_API_KEY; do
  if [ -z "${!var}" ]; then
    echo "⚠ $var is not set in .env — aborting."
    exit 1
  fi
done

# 1. Install Cyberwave CLI
echo ""
echo "--- Installing Cyberwave CLI ---"
curl -fsSL https://cyberwave.com/install.sh | bash
sudo cyberwave edge install

# 2. Install Cyberwave Python SDK
echo ""
echo "--- Installing Cyberwave Python SDK ---"
PYTHON3=$(python3 --version 2>&1)
PY_MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")
if [ "$(python3 -c 'import sys; print(sys.version_info.major)')" -lt 3 ] || [ "$PY_MINOR" -lt 10 ]; then
  echo "⚠ python3 is $(python3 --version) — need 3.10+. Install via miniconda or pyenv first."
  exit 1
fi
pip install cyberwave
python3 -c "import cyberwave" || { echo "⚠ cyberwave failed to import — check Python environment."; exit 1; }
echo "✓ cyberwave installed and importable with $(python3 --version)"

# 3. Install OpenClaw
echo ""
echo "--- Installing OpenClaw ---"
curl -fsSL https://openclaw.ai/install.sh | bash

# 3a. Authenticate with OpenAI Codex (OAuth — opens browser for ChatGPT sign-in)
echo ""
echo "--- Authenticating with OpenAI Codex ---"
openclaw models auth login --provider openai-codex

# 4. Copy OpenClaw skill (directory with SKILL.md — auto-discovered by OpenClaw)
echo ""
echo "--- Registering Cyberwave skill with OpenClaw ---"
mkdir -p ~/.openclaw/skills/cyberwave
cp skills/cyberwave/SKILL.md ~/.openclaw/skills/cyberwave/SKILL.md
echo "✓ Skill copied to ~/.openclaw/skills/cyberwave/"

# 5. Install and configure the OpenClaw daemon
echo ""
echo "--- Installing OpenClaw daemon ---"
openclaw onboard --install-daemon --flow manual --skip-skills --skip-channels --skip-search --non-interactive --accept-risk

PLIST=~/Library/LaunchAgents/ai.openclaw.gateway.plist

if [ ! -f "$PLIST" ]; then
  echo "⚠ Daemon plist not found at $PLIST — skipping env var injection."
else
  echo ""
  echo "--- Injecting env vars into daemon plist ---"
  plist_set() {
    /usr/libexec/PlistBuddy -c "Set :EnvironmentVariables:$1 $2" "$PLIST" 2>/dev/null \
      || /usr/libexec/PlistBuddy -c "Add :EnvironmentVariables:$1 string $2" "$PLIST"
  }
  PYTHON3=$(which python3)
  plist_set PYTHON3 "$PYTHON3"
  plist_set TELEGRAM_BOT_TOKEN "$TELEGRAM_BOT_TOKEN"
  plist_set CYBERWAVE_TWIN_ID "$CYBERWAVE_TWIN_ID"
  plist_set CYBERWAVE_API_KEY "$CYBERWAVE_API_KEY"
  echo "✓ Env vars injected into $PLIST"

  echo ""
  echo "--- Reloading daemon ---"
  launchctl unload "$PLIST" 2>/dev/null || true
  launchctl load "$PLIST"
  echo "✓ Daemon reloaded"
fi

# 6. Configure Telegram channel via openclaw config
echo ""
echo "--- Configuring Telegram channel ---"
openclaw config set channels.telegram.enabled true
openclaw config set channels.telegram.botToken "$TELEGRAM_BOT_TOKEN"
openclaw config set channels.telegram.dmPolicy pairing
openclaw config set channels.telegram.groupPolicy open
echo "✓ Telegram configured"

# 7. Disable memory search (no embedding provider)
echo ""
echo "--- Disabling memory search (no embedding provider configured) ---"
openclaw config set agents.defaults.memorySearch.enabled false
echo "✓ Memory search disabled"

echo ""
echo "=== Setup complete! ==="
echo ""
echo "Example commands to try in Telegram:"
echo "  • 'check robot status'"
echo "  • 'stand up'"
echo "  • 'move forward 1 meter'"
echo "  • 'rotate 90 degrees'"
echo "  • 'explore the room and tell me what you see'"
