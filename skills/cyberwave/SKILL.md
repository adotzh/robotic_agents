---
name: cyberwave
description: Unitree GO2 robot control via Cyberwave. Activate when user mentions robot, GO2, move, rotate, explore, look around, or describe what you see.
---

# Cyberwave — Unitree GO2 Control

Control the Unitree GO2 quadruped robot ("Unitree Go2 (9b4a8188...)") via Cyberwave digital twin.

**Controller:** `$HOME/PetProjects/robotics-hackathon/run_robot.sh`
**Required env:** `CYBERWAVE_TWIN_ID`

All commands return JSON. Always confirm actions in plain English.

---

## Commands

### Status
```
$HOME/PetProjects/robotics-hackathon/run_robot.sh status
```

### Move to absolute position (meters)
```
$HOME/PetProjects/robotics-hackathon/run_robot.sh move <x> <y> <z>
```

### Rotate (yaw in degrees, 0–360)
```
$HOME/PetProjects/robotics-hackathon/run_robot.sh rotate <yaw>
```

### Move at velocity
```
$HOME/PetProjects/robotics-hackathon/run_robot.sh move_vel <vx> <vy> <vyaw> <duration_seconds>
```
- `vx`: forward/backward (m/s), positive = forward
- `vy`: left/right (m/s), positive = left
- `vyaw`: rotation rate (rad/s)

### Set gait
```
$HOME/PetProjects/robotics-hackathon/run_robot.sh gait <mode>
```
Modes: `walk`, `trot`, `run`

### Set pose
```
$HOME/PetProjects/robotics-hackathon/run_robot.sh pose <name>
```
Poses: `stand`, `sit`, `liedown`, `stretch`

### Body height (meters, e.g. 0.25–0.40)
```
$HOME/PetProjects/robotics-hackathon/run_robot.sh height <meters>
```

### Set joint angle
```
$HOME/PetProjects/robotics-hackathon/run_robot.sh joint <joint_id> <degrees>
```

### Capture camera frame
```
$HOME/PetProjects/robotics-hackathon/run_robot.sh capture
```
Returns `{"ok": true, "path": "/tmp/go2_frame_<timestamp>.jpg"}`. Read the image at that path to see what the robot sees.

### Reset to default position
```
$HOME/PetProjects/robotics-hackathon/run_robot.sh reset
```

---

## Explore and Describe

When the user asks the robot to **explore**, **look around**, or **describe what it sees**, follow this loop:

1. `pose stand` — ensure the robot is standing
2. For each yaw angle in `[0, 60, 120, 180, 240, 300]`:
   a. `rotate <yaw>` — face that direction
   b. `capture` — grab a frame
   c. Read the saved image file and describe what you see (objects, layout, notable features)
   d. If the user asked to find something specific — stop and report immediately if found
3. After the full sweep, summarize the room in plain English

Keep descriptions concise (1–2 sentences per angle). End with an overall summary.
