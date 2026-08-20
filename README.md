# TAMP Agent

A CLI-based Task-and-Motion Planning (TAMP) pipeline connecting a local language model to symbolic planning and a PyBullet Franka Panda simulation.

## Architecture

```text
Natural-language instruction
          |
          v
+-------------------------+
| NLI / Mistral 7B        |
| language -> JSON        |
+------------+------------+
             |
             v
+-------------------------+
| Semantic grounding      |
| aliases + robot state   |
+------------+------------+
             |
             v
+-------------------------+
| PDDL Generator          |
| JSON + world state      |
| -> problem.pddl         |
+------------+------------+
             |
             v
+-------------------------+
| Fast Downward           |
| PDDL -> symbolic plan   |
+------------+------------+
             |
             v
+-------------------------+
| Plan Adapter            |
| symbolic -> robot ops   |
+------------+------------+
             |
             v
+-------------------------+
| PyBullet / Franka Panda |
| simulated execution     |
+-------------------------+
```

The LLM is responsible for language interpretation and mapping natural-language requests into a stable JSON structure. Pydantic validates the **structure of that JSON**, while downstream grounding determines whether an object or target maps to a known simulator entity. The semantic validator deliberately does not reject unfamiliar natural-language wording merely because it is not present in an alias table.

## Supported actions

The NLI and symbolic domain support four user-level actions:

- `pick` — acquire/grasp an object.
- `place` — place an object at a specified target.
- `drop` — release an object without a placement target.
- `move` — a compound manipulation request combining acquisition and placement, e.g. `Pick and place the green cylinder into the box` or `Move the green cylinder into the box`.

`move` is represented as a symbolic compound action and is expanded by the execution adapter into:

```text
move_to(object)
grasp(object)
move_to(target)
release()
```

The planner still controls the symbolic sequence; the simulator does not interpret natural language.

## Stateful commands

The executor maintains the currently held object. Consequently, after a successful pick, commands can omit the object when context makes the reference unambiguous:

```text
Pick up the green cylinder
Place it in the box
```

or:

```text
Pick up the green cylinder
Drop it
```

If the local LLM emits `target: "unknown"` even though the input explicitly contains `box` or `container`, the NLI interface performs a narrow information-preservation recovery. This is not a semantic whitelist: it only prevents an explicitly stated target from being discarded by the local model.

## Natural-language interpretation

The NLI accepts ordinary phrasing rather than requiring exact commands. Examples include:

```text
Pick up the green cylinder
Grab the green cylinder
Put the green cylinder in the box
Place it in the container
Release it
Pick and place the green cylinder into the box
Move the green cylinder into the box
```

Minor spelling errors such as `greeen cylinder` are intended to remain part of the language interpretation layer rather than being rejected by Pydantic. Scene grounding is performed separately.

## Supported scene objects

The current workcell uses simple primitive objects:

- large red cube
- small red cube
- large blue cube
- small blue cube
- red cylinder
- green cylinder
- yellow cylinder

The sphere and capsule were removed because they produced unreliable manipulation behavior. Objects are clustered around the Panda's reachable workspace.

## Workcell layout

The table is 1.6 m × 1.1 m. The fixed-base Panda is mounted at the left side of the table. The open-top box is centered on the table and aligned with the Panda's approach axis. Objects are distributed around the container without initially occupying the receptacle.

Placement uses a dedicated vertical-entry motion: the Panda first clears the top of the container, moves laterally to its center, and then descends through the opening to a release height derived from the actual held object's geometry. This avoids treating the container's visual center as the object's release height and reduces collisions with the box walls.

## Execution logs

Every non-empty user instruction creates a separate runtime log:

```text
logs/
├── execution_1.log
├── execution_2.log
└── execution_3.log
```

Each log records:

- user input
- NLI JSON
- PDDL / planner output
- normalized simulation actions
- execution status or failure message

The same diagnostic output remains visible in the terminal. Runtime logs are ignored by Git.

## Running locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Install Fast Downward separately. The planner distribution is not vendored because its compiled binaries exceed GitHub's normal repository file-size limit.

Fast Downward can be supplied explicitly:

```bash
export FAST_DOWNWARD_PATH=/path/to/fast-downward.py
```

The application also searches for `fast-downward.py` on `PATH` and uses a deterministic local fallback if it is unavailable.

Start the system:

```bash
python main.py
```

Example:

```text
Robot instruction: Pick and place the green cylinder into the box
```

Expected high-level interpretation:

```json
{
  "action": "move",
  "object": "cylinder_green",
  "target": "box",
  "error": null
}
```

The resulting symbolic operation is a compound move, which the execution adapter expands into pick and place motion primitives.

## Repository layout

```text
tamp-agent/
├── main.py
├── nli/
│   ├── interface.py
│   ├── llm.py
│   ├── schema.py
│   └── validator.py
├── planning/
│   ├── domain.pddl
│   ├── pddl_generator.py
│   ├── planner.py
│   └── plan_parser.py
├── simulation/
│   ├── actions.py
│   ├── config.py
│   ├── environment.py
│   ├── executor.py
│   ├── fast_downward_adapter.py
│   ├── objects.py
│   └── robot.py
├── logs/
└── requirements.txt
```

## Design boundaries

### NLI
Interprets natural language and emits the stable JSON contract. Pydantic checks structure; it is not the source of semantic limitations.

### Grounding
Maps natural-language object and target references to simulator identifiers and resolves contextual references using the current robot state.

### Planner
Generates a typed PDDL problem using the current world state. This prevents redundant `pick` operations before `drop` or `place` and allows compound `move` goals.

### Simulation
Converts symbolic actions into motion, grasp, and release procedures. Container placement uses geometry-aware approach and release poses rather than blindly moving to the container's visual center.

## Debugging

Inspect the corresponding `logs/execution_N.log` for each input. The log is the canonical per-task trace across NLI, planning, and simulation.

## Status

The project is CLI-first and intended to provide an inspectable end-to-end TAMP pipeline before adding a web interface.
