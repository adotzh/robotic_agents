# Robotic Agents — Telegram Scout

Control a Unitree GO2 robot dog via Telegram using natural language. Send a mission like *"explore the room and tell me what you see"* — the robot rotates through 360°, captures camera frames, and replies with a description of what it sees.

```
Telegram → OpenClaw + Codex → robot_controller.py → Cyberwave SDK → Unitree GO2
```

## Prerequisites

- macOS (setup script uses launchd)
- Python 3.10+ (miniconda recommended)
- [Cyberwave](https://cyberwave.com) account with a GO2 digital twin
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
CYBERWAVE_TWIN_ID=your-twin-uuid          # find this in the Cyberwave dashboard
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

Check robot connectivity:

```bash
source .env && python3 robot_controller.py status
```

Expected output:
```json
{"status": "connected", "twin": "<your-twin-id>", "can_locomote": true, ...}
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
| `check robot status` | Reports connection state |
| `stand up` | GO2 stands |
| `sit` | GO2 sits |
| `move forward 1 meter` | GO2 moves forward |
| `rotate 90 degrees` | GO2 turns 90° |
| `explore the room and tell me what you see` | Full 360° scan with camera + description |

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
pose <name>              stand | sit | liedown | stretch
gait <mode>              walk | trot | run
move <x> <y> <z>         absolute position (meters)
move_vel <vx> <vy> <vyaw> <duration>
rotate <yaw>             0–360 degrees
height <meters>          body height
joint <joint_id> <deg>   individual joint control
capture [path]           save camera frame to JPEG
reset                    return to origin
```

## Troubleshooting

**`ModuleNotFoundError: No module named 'cyberwave'`**
The daemon is using the wrong Python. Run `setup.sh` again — it injects the correct Python path into the daemon environment.

**`can_locomote: false` in status**
The twin UUID in `.env` may not be a GO2 locomotion twin. Check the Cyberwave dashboard and confirm the twin type.

**Telegram: not configured in `openclaw status`**
Re-run `setup.sh` to re-inject the bot token.

**Memory search errors in OpenClaw**
Disabled by default (no embedding provider configured). Safe to ignore.
