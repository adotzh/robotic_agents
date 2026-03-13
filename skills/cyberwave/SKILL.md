---
name: cyberwave
description: UGV Beast robot control via Cyberwave. Activate when user mentions robot, UGV, Beast, drive, move, steer, joint, or explore.
---

# Cyberwave — UGV Beast Control

Control the UGV Beast ground vehicle via Cyberwave digital twin (`9b4a8188...`).
Supports keyboard-style teleoperation and individual joint control.

**Controller:** `$HOME/PetProjects/robotics-hackathon/robot_controller.py`
**Required env:** `CYBERWAVE_TWIN_ID`, `CYBERWAVE_ENVIRONMENT_ID`

All commands return JSON. Always confirm actions in plain English.

> **IMPORTANT:** Call `robot_controller.py` directly as an executable — do NOT invoke it via `python3`. Do NOT check Python versions. Do NOT assume the environment is broken based on prior messages — always run the command and report the actual output.

---

## Commands

### Status
```
$HOME/PetProjects/robotics-hackathon/robot_controller.py status
```

### Drive (velocity-based teleop)
```
$HOME/PetProjects/robotics-hackathon/robot_controller.py move_vel <vx> <vy> <vyaw> <duration_seconds>
```
- `vx`: forward/backward (m/s), positive = forward
- `vy`: left/right (m/s), positive = left
- `vyaw`: rotation rate (rad/s), positive = turn left
- Example — drive forward 1 m/s for 2 seconds: `move_vel 1.0 0 0 2`
- Example — turn left: `move_vel 0 0 0.5 2`

### Stop
```
$HOME/PetProjects/robotics-hackathon/robot_controller.py stop
```

### Joint control
```
$HOME/PetProjects/robotics-hackathon/robot_controller.py joint <joint_id> <degrees>
```
Use `status` to get the list of controllable joint names.

### Capture camera frame
```
$HOME/PetProjects/robotics-hackathon/robot_controller.py capture
```
Returns `{"ok": true, "path": "/tmp/ugv_frame_<timestamp>.jpg"}`. Read the image at that path to see what the robot sees.

### Reset to origin
```
$HOME/PetProjects/robotics-hackathon/robot_controller.py reset
```

---

## Explore and Describe

When the user asks the robot to **explore**, **look around**, or **describe what it sees**, follow this loop:

1. For each yaw angle in `[0, 60, 120, 180, 240, 300]`:
   a. `move_vel 0 0 0.5 2` — rotate to face that direction
   b. `capture` — grab a frame
   c. Read the saved image file and describe what you see (objects, layout, notable features)
   d. If the user asked to find something specific — stop and report immediately if found
2. After the full sweep, summarize the area in plain English

Keep descriptions concise (1–2 sentences per angle). End with an overall summary.
