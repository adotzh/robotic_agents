# Experiment Design: Telegram Scout — "Explore and Describe"

## Concept

User sends a natural language mission to a Telegram bot. The Unitree GO2 quadruped
robot explores the room, captures frames from its camera, and replies with a
plain-English description of what it sees.

**Demo message:**
> "Explore the room and tell me what you see"

**Expected reply:**
> "At 0°: empty corridor, white walls, a door on the left.
> At 60°: desk with a laptop and a water bottle.
> At 120°: window with blinds, electrical socket below it on the right.
> ...
> Overall: a small office room with a desk, window, and one visible socket on the east wall."

---

## Robot

**Unitree GO2** — quadruped robot dog connected via Cyberwave digital twin (`Unitree Go2 (9b4a8188...)`).

---

## Architecture

```
Telegram (user)
     │
     ▼
OpenClaw + Codex          ← interprets the mission, orchestrates tools
     │
     ├─► pose / gait / height     ← body control
     ├─► move / move_vel / rotate ← navigation
     ├─► capture                  ← grabs JPEG from GO2 camera
     └─► (reads image + describes) ← agent uses vision to describe frame
          │
          ▼
     Cyberwave SDK (Python)       ← robot_controller.py → cw.twin()
          │
          ▼
     Unitree GO2 (physical or sim)
```

---

## What Needs to Be Built

### Already done
- [x] Cyberwave SDK connected (`robot_controller.py`)
- [x] OpenClaw skill (`skills/cyberwave/SKILL.md`)
- [x] Telegram channel configured
- [x] `pose`, `gait`, `move_vel`, `height` commands
- [x] `capture` command — grabs JPEG from GO2 camera
- [x] Explore-and-describe loop in skill (rotate 6 angles, capture, describe)

### To add
- [ ] Verify `robot.camera.capture()` is the correct Cyberwave SDK call for GO2
- [ ] Test `capture` command produces a non-blank JPEG
- [ ] Add `TELEGRAM_BOT_TOKEN` and `CYBERWAVE_TWIN_ID` to launchd plist
- [ ] End-to-end test via Telegram

---

## Experiment Steps

### Phase 1 — Manual control sanity check
1. Run `setup.sh` and confirm GO2 appears in Cyberwave dashboard
2. In Telegram: *"stand up"* → confirm GO2 stands
3. In Telegram: *"move forward 1 meter"* → confirm GO2 moves
4. In Telegram: *"rotate 90 degrees"* → confirm rotation

### Phase 2 — Frame capture check
1. Point GO2 at something recognizable
2. Run directly: `python3 robot_controller.py capture`
3. Verify JPEG is saved and not blank
4. Ask OpenClaw to read and describe the saved image

### Phase 3 — Full explore loop (simulation)
1. Load GO2 in Cyberwave test environment
2. Send: *"explore the room and tell me what you see"*
3. GO2 should: stand → rotate through 6 angles → capture + describe at each → summarize

### Phase 4 — Physical demo
1. Place GO2 in a real room
2. Repeat Phase 3 with live hardware
3. Record the Telegram conversation as demo artifact

---

## Exploration Strategy

Simple **rotate-and-scan** loop (no SLAM needed for a hackathon):

```
pose stand
for angle in [0°, 60°, 120°, 180°, 240°, 300°]:
    rotate to angle
    capture frame
    describe what is visible (1–2 sentences)
    if target found → stop and report
summarize full room
```

6 positions × 1 frame = 6 frames max.

---

## Success Criteria

| Criterion | Pass |
|-----------|------|
| GO2 responds to Telegram commands | moves in sim/physical |
| `capture` produces a usable JPEG | file saved, not blank |
| Agent correctly describes test frame | accurate description |
| Full explore loop completes in < 3 minutes | end-to-end timing |
| Telegram reply includes description per angle + summary | message received |

---

## Demo Script (for judges)

1. Show the Telegram chat on a phone/screen
2. Show the Cyberwave dashboard (live GO2 view) on a laptop
3. Type: *"Explore the room and tell me what you see"*
4. Watch the GO2 rotate and pause at each angle in the dashboard
5. Show Telegram reply arriving with per-angle descriptions and summary

**One-liner pitch:** *"You describe a mission in plain English, the robot dog
explores the room and reports back what it found."*

---

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| `robot.camera.capture()` API differs in Cyberwave GO2 SDK | check SDK docs, try `robot.video.snapshot()` as fallback |
| Captured JPEG is blank or too dark | ensure GO2 camera is enabled in Cyberwave, test in good lighting |
| Agent vision quality insufficient | use a well-lit scene with obvious objects for demo |
| GO2 walks out of bounds in sim | use `move_vel` with short duration instead of absolute `move` |
| Telegram bot token not loaded by daemon | add to launchd plist `EnvironmentVariables` |
