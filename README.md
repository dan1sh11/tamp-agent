# TAMP Agent

A CLI-based Task-and-Motion Planning (TAMP) pipeline that connects a local language model to symbolic planning and a PyBullet Franka Panda simulation.

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

The LLM is limited to language interpretation. It does not generate robot commands directly. The planner owns symbolic action sequencing, the executor maintains the current held-object state, and PyBullet owns physical execution.

## Supported actions

The current domain supports:

- `pick <object>` — grasp an object.
- `drop` — release the currently held object at its current location.
- `place ... in the box` — place the currently held object into the box.

The system is stateful. After a successful pick, commands such as `drop it`, `place it in the box`, `put the object in the container`, and similar contextual instructions can omit the object name. The current held object is resolved from the simulator state before PDDL generation.

## Supported scene objects

The workcell intentionally uses only simple, reliable grasp primitives:

- large red cube
- small red cube
- large blue cube
- small blue cube
- red cylinder
- green cylinder
- yellow cylinder

The sphere and capsule were removed because they produced less reliable manipulation behavior. Object positions are clustered around the Panda's reachable workspace rather than being placed at the edges of the table.

## Workcell layout

The table is 1.6 m × 1.1 m. The fixed-base Panda is mounted at the left side of the table. The open-top placement box is centered on the table and on the Panda's forward approach axis, with its long axis transverse to the robot's forward direction. Objects are positioned around the box so that no object starts inside the receptacle and all remain within the compact manipulation workspace.

The workcell geometry is centralized in `simulation/config.py` and `simulation/environment.py`; individual task commands do not contain object-specific motion hacks.

## Execution logs

Every non-empty user instruction creates a separate runtime log under `logs/`:

```text
logs/
├── execution_1.log
├── execution_2.log
└── execution_3.log
```

The counter continues from the highest existing execution number. Each file records:

- user input
- NLI JSON
- PDDL / planner output
- normalized simulation actions
- execution status or failure message

The same output continues to appear in the terminal. Runtime logs are ignored by Git so simulator output is not committed to the repository.

## Running locally

Install the Python dependencies:

```bash
pip install -r requirements.txt
```

Install and build Fast Downward separately. The project does not vendor the planner distribution because its compiled binaries exceed GitHub's normal repository file-size limit.

Fast Downward can be supplied explicitly:

```bash
export FAST_DOWNWARD_PATH=/path/to/fast-downward.py
```

The application also checks for `fast-downward.py` on `PATH` and falls back to the deterministic local planner when Fast Downward is unavailable. The fallback preserves the same normalized action interface used by the simulator.

Start the system:

```bash
python main.py
```

Example interaction:

```text
Robot instruction: pick up the green cylinder
Robot instruction: place it in the box
Robot instruction: drop it
```

The PyBullet GUI shows the Panda operating in the workcell while the corresponding diagnostic information is printed to the terminal and written to the numbered execution log.

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
├── logs/                  # runtime-generated; execution_*.log ignored by Git
└── requirements.txt
```

## Design boundaries

### NLI
Produces a validated `Instruction` object. It is responsible for language semantics and object/target aliases. It can leave the object unspecified for contextual `drop` and `place` commands.

### Planner
Generates a typed PDDL problem using the robot's current held-object state. This prevents the planner from inserting an unnecessary `pick` before `drop` or `place`.

### Simulation
Converts symbolic actions into robot motion, grasp, and release procedures. The scene contains a fixed-base Franka Panda, a centered placement box, and a compact set of simple colored manipulation objects.

## Debugging

For each input, inspect the corresponding `logs/execution_N.log`. The log is the canonical per-task trace for reproducing failures across the NLI, planner, and simulation stages.

## Status

The project is CLI-first and intended to provide a reliable, inspectable end-to-end TAMP pipeline before adding the web interface.
