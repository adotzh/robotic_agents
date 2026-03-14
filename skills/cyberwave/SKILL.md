---
name: cyberwave
description: UGV Beast robot control via Cyberwave and ROS2. Activate when user mentions robot, UGV, Beast, drive, move, turn, camera, joint, explore, or any robot action.
---

# Cyberwave — UGV Beast Control

Control the UGV Beast ground vehicle. Movement is sent via SSH to the robot's Raspberry Pi ROS2 stack (`/cmd_vel` topic). Camera and joint control use the Cyberwave SDK.

**Controller:** `$HOME/PetProjects/robotics-hackathon/robot_controller.py`
**Required env:** `CYBERWAVE_TWIN_ID`, `CYBERWAVE_ENVIRONMENT_ID`, `ROBOT_HOST`

> **IMPORTANT:** Call `robot_controller.py` directly as an executable. Do NOT invoke via `python3`. Do NOT check Python versions. Do NOT assume environment is broken — always run and report actual output.

---

## Commands

### Status (shows SSH reachability + twin info)
```
$HOME/PetProjects/robotics-hackathon/robot_controller.py status
```

### Move (drive forward/turn via ROS2 cmd_vel)
```
$HOME/PetProjects/robotics-hackathon/robot_controller.py move <vx> <vyaw> <duration_seconds>
```
- `vx`: forward speed in m/s (positive = forward, negative = backward)
- `vyaw`: rotation in rad/s (positive = turn left, negative = turn right)
- `duration`: seconds to drive
- Forward 1 meter at 0.3 m/s ≈ `move 0.3 0 3`
- Turn left: `move 0 0.5 2`
- Turn right: `move 0 -0.5 2`

### Stop
```
$HOME/PetProjects/robotics-hackathon/robot_controller.py stop
```

### Joint control (camera pan-tilt)
```
$HOME/PetProjects/robotics-hackathon/robot_controller.py joint <joint_name> <degrees>
```
- `pt_base_link_to_pt_link1` — camera pan (left/right)
- `pt_link1_to_pt_link2` — camera tilt (up/down)

### Capture camera frame
```
$HOME/PetProjects/robotics-hackathon/robot_controller.py capture
```
Returns `{"ok": true, "path": "/tmp/ugv_frame_<timestamp>.jpg"}`. Read the image to describe what the robot sees.

### Run any ROS2 command on the robot
```
$HOME/PetProjects/robotics-hackathon/robot_controller.py ros2 <ros2_command...>
```
Examples:
- `robot_controller.py ros2 ros2 topic list`
- `robot_controller.py ros2 ros2 topic echo /cmd_vel --once`
- `robot_controller.py ros2 ros2 run ugv_tools keyboard_ctrl`

---

## Enriching the controller

If a user asks for a new robot capability that `robot_controller.py` doesn't support yet, you can add it:

1. Read the current controller: `cat $HOME/PetProjects/robotics-hackathon/robot_controller.py`
2. Add a new `cmd_<name>` function following the existing pattern
3. Register it in the `COMMANDS` dict
4. Test it with `$HOME/PetProjects/robotics-hackathon/robot_controller.py <new_command>`
5. Commit and push: `cd $HOME/PetProjects/robotics-hackathon && git add robot_controller.py && git commit -m "add <command> command" && git push`

ROS2 commands available on the robot Pi:
- `ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "..."` — velocity control
- `ros2 topic list` — list all active topics
- `ros2 run ugv_tools keyboard_ctrl` — start keyboard control node

---

## Explore and Describe

When the user asks to **explore**, **look around**, or **describe what the robot sees**:

1. `move 0 0 0` (ensure stopped)
2. For each angle in `[0°, 60°, 120°, 180°, 240°, 300°]`:
   a. Pan camera: `joint pt_base_link_to_pt_link1 <angle>`
   b. `capture` — grab frame
   c. Read saved image and describe what you see (1–2 sentences)
   d. If user asked to find something specific — stop and report if found
3. Reset camera: `joint pt_base_link_to_pt_link1 0`
4. Summarize the full scene
