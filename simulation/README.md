# PyBullet TAMP Simulation Component

Third component of the LLM -> PDDL/Fast Downward -> PyBullet pipeline.

## Architecture

Fast Downward plan -> planner adapter -> `sim.actions.Action` -> `sim.executor.PlanExecutor` -> PyBullet

The simulator deliberately does not parse PDDL/SAS files. The future planner adapter translates
grounded planner actions into the small simulator action vocabulary.

## Environment

- Fixed tabletop
- Franka Panda with fixed base
- Open-top box made from five static panels
- Exactly 10 manipulable objects
- Primitive shapes plus a procedural banana-like object
- Stable symbolic object names
- IK-based end-effector motion
- Basic grasp/release execution
- Contact-query support
- Demo plan using the same normalized action interface that the Fast Downward adapter will use

## Run

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/WSL:
source .venv/bin/activate

pip install -r requirements.txt
python main.py
```

## Planner integration

The PDDL problem should use the same symbolic names as `scene_contract.json`.

For example, a future Fast Downward action such as:

```text
(pick cube_red)
```

should be translated by the planner adapter into:

```python
Action.move_to("cube_red")
Action.grasp("cube_red")
```

A placement action can become:

```python
Action.move_to("box")
Action.release()
```

The exact mapping must match the PDDL domain you build in component 2.
