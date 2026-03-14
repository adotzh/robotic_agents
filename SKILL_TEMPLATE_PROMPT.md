# Prompt: Generate an OpenClaw Skill for a Cyberwave Robot

Use this prompt to generate a `SKILL.md` for any robot connected via the Cyberwave platform.

---

## How to use

1. Run `./run_robot.sh status` and copy the output
2. Fill in the fields below
3. Paste the full prompt into Claude (or any LLM)
4. Save the output as `skills/cyberwave/SKILL.md`
5. Copy to `~/.openclaw/skills/cyberwave/SKILL.md` and reload the daemon

---

## Prompt

```
Generate an OpenClaw SKILL.md file for a Cyberwave robot with the following details.

---

Robot name: [e.g. UGV Beast, Unitree GO2, custom arm]
Robot type: [wheeled / quadruped / arm / drone / other]
Controller script: $HOME/PetProjects/robotics-hackathon/robot_controller.py
Status output from ./run_robot.sh status:
[PASTE JSON HERE]

Capabilities:
- can_locomote: [true/false]
- locomotion_mode: [wheeled / legged / stationary / other]
- joints: [paste list from status output]

Available robot_controller.py commands and their arguments:
[PASTE output of: ./run_robot.sh 2>&1 | head -20, or describe manually]

Primary use case / mission:
[e.g. "keyboard teleoperation and camera pan-tilt control"
      "explore a room and describe what the camera sees"
      "pick and place objects using arm joints"]

Special behaviors the agent should know about:
[e.g. "joint 1 = camera pan, joint 2 = camera tilt"
      "vx is forward/backward in m/s, vyaw is rotation in rad/s"
      "always stop before changing direction"]

---

Requirements for the generated SKILL.md:
- Frontmatter with name and description that triggers on relevant user phrases
- A brief robot description section at the top
- IMPORTANT notice: call robot_controller.py directly as executable, do NOT invoke via python3, do NOT check Python versions, do NOT assume environment is broken — always run and report actual output
- One section per available command with exact shell syntax using $HOME path
- Parameter explanations for any non-obvious arguments
- An "Explore and Describe" section if the robot has a camera, using capture + vision loop
- Keep it concise — the skill is a reference for the agent, not a user manual
```

---

## Example filled-in prompt (UGV Beast)

```
Robot name: UGV Beast
Robot type: wheeled (tracked off-road)
Controller script: $HOME/PetProjects/robotics-hackathon/robot_controller.py
Status output:
{"status":"connected","twin":"waveshare/ugv-beast","environment":"55c24ede...","can_locomote":true,"locomotion_mode":"wheeled","joints":["left_down_wheel_link_joint","left_up_wheel_link_joint","pt_base_link_to_pt_link1","pt_link1_to_pt_link2","right_down_wheel_link_joint","right_up_wheel_link_joint"]}

Available commands: status, move_vel <vx> <vy> <vyaw> <duration>, stop, joint <name> <degrees>, capture, reset

Primary use case: keyboard-style teleoperation and camera pan-tilt control

Special behaviors:
- pt_base_link_to_pt_link1 = camera pan (left/right)
- pt_link1_to_pt_link2 = camera tilt (up/down)
- vx positive = forward, vyaw positive = turn left
- always call stop before reversing direction
```
