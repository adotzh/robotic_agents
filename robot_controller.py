#!/Users/azhiboedova/miniconda3/bin/python3
"""
Cyberwave UGV Beast controller — called by the OpenClaw skill via shell exec.
Robot runs ROS2 on Raspberry Pi at ROBOT_HOST. Commands are sent via SSH.

Usage: ./robot_controller.py <command> [args...]

Commands:
  status
  move <vx> <vyaw> <duration>   drive forward/turn (m/s, rad/s, seconds)
  stop
  joint <joint_name> <degrees>  camera pan-tilt control
  capture [output_path]
  ros2 <ros2_command...>        run any ros2 command on the robot Pi
"""

import sys
import json
import os
import subprocess
import cyberwave as cw


ROBOT_HOST = os.environ.get("ROBOT_HOST", "172.20.10.2")
ROBOT_USER = os.environ.get("ROBOT_USER", "ws")
ROBOT_PORT = os.environ.get("ROBOT_PORT", "22")
DOCKER_CONTAINER = os.environ.get("ROBOT_DOCKER_CONTAINER", "cyberwave-driver-f15d8ba2")


def ssh(cmd, timeout=10):
    """Run a command on the robot Pi via SSH. Returns (stdout, stderr, returncode)."""
    full_cmd = [
        "ssh", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=5",
        "-p", ROBOT_PORT, f"{ROBOT_USER}@{ROBOT_HOST}", cmd
    ]
    result = subprocess.run(full_cmd, capture_output=True, text=True, timeout=timeout)
    return result.stdout.strip(), result.stderr.strip(), result.returncode


def ros2_pub_cmd_vel(vx=0.0, vyaw=0.0, duration=1.0):
    """Publish cmd_vel to the robot for a given duration, then stop."""
    twist = f"{{linear: {{x: {vx}, y: 0.0, z: 0.0}}, angular: {{x: 0.0, y: 0.0, z: {vyaw}}}}}"
    move_cmd = f"cd /home/ws/ugv_ws && source install/setup.bash && ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist \"{twist}\""
    stop_cmd = "cd /home/ws/ugv_ws && source install/setup.bash && ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist \"{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}\""

    # Send move command repeatedly for duration seconds
    import time
    deadline = time.time() + float(duration)
    while time.time() < deadline:
        ssh(move_cmd, timeout=5)
    ssh(stop_cmd, timeout=5)


def get_robot():
    twin_id = os.environ.get("CYBERWAVE_TWIN_ID")
    if not twin_id:
        print(json.dumps({"error": "CYBERWAVE_TWIN_ID not set"}))
        sys.exit(1)
    env_id = os.environ.pop("CYBERWAVE_ENVIRONMENT_ID", None)
    return cw.twin(twin_id, environment=env_id)


def cmd_status():
    env_id = os.environ.get("CYBERWAVE_ENVIRONMENT_ID")
    robot = get_robot()
    caps = robot.capabilities

    # Also check SSH connectivity
    try:
        _, _, rc = ssh("echo ok", timeout=3)
        ssh_ok = rc == 0
    except Exception:
        ssh_ok = False

    result = {
        "status": "connected",
        "twin_key": os.environ.get("CYBERWAVE_TWIN_ID"),
        "twin_name": robot.name,
        "twin_uuid": robot.uuid,
        "environment": env_id,
        "can_locomote": caps.get("can_locomote"),
        "locomotion_mode": caps.get("locomotion_mode"),
        "joints": robot.get_controllable_joint_names(),
        "robot_ssh": f"{ROBOT_USER}@{ROBOT_HOST}:{ROBOT_PORT}",
        "robot_ssh_reachable": ssh_ok,
    }
    print(json.dumps(result))


def cmd_move(vx, vyaw, duration):
    """Drive robot: vx m/s forward, vyaw rad/s rotation, for duration seconds."""
    ros2_pub_cmd_vel(float(vx), float(vyaw), float(duration))
    print(json.dumps({"ok": True, "action": "move", "vx": vx, "vyaw": vyaw, "duration": duration}))


def cmd_stop():
    ssh("cd /home/ws/ugv_ws && source install/setup.bash && ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist \"{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}\"", timeout=5)
    print(json.dumps({"ok": True, "action": "stop"}))


def cmd_joint(joint_name, degrees):
    """Control camera pan-tilt joints via Cyberwave SDK."""
    robot = get_robot()
    robot.joints.set(str(joint_name), float(degrees))
    print(json.dumps({"ok": True, "action": "joint", "joint": joint_name, "degrees": degrees}))


def cmd_capture(output_path=None):
    robot = get_robot()
    if not output_path:
        import tempfile, time
        output_path = os.path.join(tempfile.gettempdir(), f"ugv_frame_{int(time.time())}.jpg")
    frame = robot.camera.capture()
    with open(output_path, "wb") as f:
        f.write(frame)
    print(json.dumps({"ok": True, "action": "capture", "path": output_path}))


def cmd_ros2(*args):
    """Run any ros2 command on the robot Pi directly."""
    ros2_cmd = " ".join(args)
    full_cmd = f"cd /home/ws/ugv_ws && source install/setup.bash && {ros2_cmd}"
    stdout, stderr, rc = ssh(full_cmd, timeout=15)
    print(json.dumps({"ok": rc == 0, "stdout": stdout, "stderr": stderr, "returncode": rc}))


COMMANDS = {
    "status":  (cmd_status, 0),
    "move":    (cmd_move,   3),   # vx vyaw duration
    "stop":    (cmd_stop,   0),
    "joint":   (cmd_joint,  2),
    "capture": (cmd_capture, None),
    "ros2":    (cmd_ros2,   None),  # any number of args
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
