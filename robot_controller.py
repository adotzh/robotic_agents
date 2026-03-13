#!/Users/azhiboedova/miniconda3/bin/python3
"""
Cyberwave UGV Beast controller — called by the OpenClaw skill via shell exec.
Usage: python robot_controller.py <command> [args...]

Commands:
  status
  move_vel <vx> <vy> <vyaw> <duration>
  stop
  joint <joint_id> <degrees>
  capture [output_path]
  reset
"""

import sys
import json
import os
import cyberwave as cw


def get_robot():
    twin_id = os.environ.get("CYBERWAVE_TWIN_ID")
    if not twin_id:
        print(json.dumps({"error": "CYBERWAVE_TWIN_ID not set"}))
        sys.exit(1)
    return cw.twin(twin_id)


def get_env_id():
    return os.environ.get("CYBERWAVE_ENVIRONMENT_ID")


def cmd_status():
    robot = get_robot()
    caps = robot.capabilities
    result = {
        "status": "connected",
        "twin": os.environ.get("CYBERWAVE_TWIN_ID"),
        "environment": get_env_id(),
        "can_locomote": caps.get("can_locomote"),
        "locomotion_mode": caps.get("locomotion_mode"),
        "joints": robot.get_controllable_joint_names(),
    }
    print(json.dumps(result))


def cmd_move_vel(vx, vy, vyaw, duration):
    robot = get_robot()
    robot.navigation.follow_path(
        [{"vx": float(vx), "vy": float(vy), "vyaw": float(vyaw)}],
        wait_s=float(duration),
        environment_uuid=get_env_id(),
    )
    print(json.dumps({"ok": True, "action": "move_vel", "vx": vx, "vy": vy, "vyaw": vyaw, "duration": duration}))


def cmd_stop():
    robot = get_robot()
    robot.navigation.stop(environment_uuid=get_env_id())
    print(json.dumps({"ok": True, "action": "stop"}))


def cmd_joint(joint_id, degrees):
    robot = get_robot()
    robot.controller.joints.set(str(joint_id), float(degrees))
    print(json.dumps({"ok": True, "action": "joint", "joint": joint_id, "degrees": degrees}))


def cmd_capture(output_path=None):
    robot = get_robot()
    if not output_path:
        import tempfile, time
        output_path = os.path.join(tempfile.gettempdir(), f"ugv_frame_{int(time.time())}.jpg")
    frame = robot.camera.capture()
    with open(output_path, "wb") as f:
        f.write(frame)
    print(json.dumps({"ok": True, "action": "capture", "path": output_path}))


def cmd_reset():
    robot = get_robot()
    robot.edit_position(x=0.0, y=0.0, z=0.0)
    robot.edit_rotation(yaw=0)
    print(json.dumps({"ok": True, "action": "reset"}))


COMMANDS = {
    "status":   (cmd_status,   0),
    "move_vel": (cmd_move_vel, 4),
    "stop":     (cmd_stop,     0),
    "joint":    (cmd_joint,    2),
    "capture":  (cmd_capture,  None),  # 0 or 1 arg
    "reset":    (cmd_reset,    0),
}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No command provided. Available: " + ", ".join(COMMANDS)}))
        sys.exit(1)

    command = sys.argv[1]
    args = sys.argv[2:]

    if command not in COMMANDS:
        print(json.dumps({"error": f"Unknown command '{command}'. Available: {', '.join(COMMANDS)}"}))
        sys.exit(1)

    fn, expected_args = COMMANDS[command]

    if expected_args is not None and len(args) != expected_args:
        print(json.dumps({"error": f"'{command}' expects {expected_args} args, got {len(args)}"}))
        sys.exit(1)

    try:
        fn(*args)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
