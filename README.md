# Robotic Agents — UGV Beast Telegram Controller

Control a UGV Beast ground vehicle via Telegram using natural language. Uses keyboard-style teleoperation and joint control via the Cyberwave digital twin platform.

```
Telegram → OpenClaw + Codex → robot_controller.py → Cyberwave SDK → UGV Beast
```

## Prerequisites

- macOS (setup script uses launchd)
- Python 3.10+ (miniconda recommended)
- [Cyberwave](https://cyberwave.com) account with a UGV Beast digital twin
- [Telegram bot token](https://core.telegram.org/bots#botfather) from BotFather
- [OpenAI Codex](https://openai.com) account (OAuth login, no API key needed)

## Installation

**1. Clone the repo**

```bash
git clone https://github.com/adotzh/robotic_agents.git
cd robotic_agents
```

**2. Create your `.env`**

```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials:

```
CYBERWAVE_API_KEY=your_cyberwave_api_key
CYBERWAVE_TWIN_ID=your-twin-uuid              # find in the Cyberwave dashboard
CYBERWAVE_ENVIRONMENT_ID=your-environment-uuid
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
```

**3. Run setup**

```bash
./setup.sh
```

This will:
- Install the Cyberwave CLI and Python SDK
- Install and configure the OpenClaw daemon (background AI gateway)
- Authenticate with OpenAI Codex (opens browser)
- Register the Cyberwave skill with OpenClaw
- Inject credentials into the daemon's environment
- Configure the Telegram bot
- Reload the daemon

## Verify it works

```bash
source .env && ./robot_controller.py status
```

Expected output:
```json
{"status": "connected", "twin": "<your-twin-id>", "environment": "<env-id>", ...}
```

Check OpenClaw is running:

```bash
openclaw status
```

Telegram should show `ON · OK`.

## Usage

Message your Telegram bot:

| Message | What happens |
|---------|-------------|
| `check robot status` | Reports connection state and joint list |
| `drive forward 1 meter` | UGV moves forward |
| `turn left` | UGV rotates left |
| `stop` | UGV stops immediately |
| `set joint arm_joint_1 to 45 degrees` | Individual joint control |
| `explore the area and tell me what you see` | 360° camera sweep with description |

## Architecture

```
skills/cyberwave/SKILL.md   — OpenClaw skill: tells the AI how to use the robot
robot_controller.py          — CLI wrapper around the Cyberwave Python SDK
setup.sh                     — One-shot install and configuration script
.env                         — Your credentials (never committed)
experiment_design.md         — Experiment plan and success criteria
```

### robot_controller.py commands

```
status
move_vel <vx> <vy> <vyaw> <duration>   velocity teleop (m/s, rad/s, seconds)
stop                                    emergency stop
joint <joint_id> <degrees>             individual joint control
capture [path]                         save camera frame to JPEG
reset                                  return to origin
```

## Troubleshooting

**`ModuleNotFoundError: No module named 'cyberwave'`**
The daemon is using the wrong Python. Run `setup.sh` — it injects the correct Python path into the daemon environment.

**Shell commands blocked in webchat**
`tools.elevated` must be enabled. Run `setup.sh` to configure this automatically.

**Telegram: not configured in `openclaw status`**
Re-run `setup.sh` to re-inject the bot token.

**Memory search errors in OpenClaw**
Disabled by default (no embedding provider configured). Safe to ignore.
