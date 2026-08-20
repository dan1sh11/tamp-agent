# TAMP Agent

A CLI-based Task-and-Motion Planning (TAMP) pipeline that connects a local language model to symbolic planning and a PyBullet robot simulation.

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
| JSON -> problem.pddl    |
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
| Plan Adapter             |
| symbolic -> robot ops   |
+------------+------------+
             |
             v
+-------------------------+
| PyBullet / Franka Panda |
| simulated execution     |
+-------------------------+
```

The LLM is deliberately limited to language interpretation. It does not generate robot commands directly. The planner owns symbolic action sequencing, and the simulator owns physical execution.

## Supported tasks

The current domain intentionally stays small and deterministic:

- `pick <object>`
- `place <object> in the box`

Supported scene objects:

- large red cube
- large blue cube
- small red cube
- small blue cube
- red cylinder
- green cylinder
- yellow cylinder
- sphere
- capsule

Natural-language aliases such as `red cube`, `blue cube`, `container`, and `box` are canonicalized before PDDL generation.

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

The application also checks for `fast-downward.py` on `PATH` and falls back to a deterministic local planner for the two supported task types when Fast Downward is unavailable. This keeps the complete CLI and simulator runnable while preserving the same planner-to-simulator contract.

Start the system:

```bash
python main.py
```

Example:

```text
Robot instruction: pick up the blue cube
```

The terminal displays the NLI JSON, generated planner output, normalized simulator actions, and execution status while the PyBullet GUI shows the Panda operating in the workcell.

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
└── requirements.txt
```

## Design boundaries

### NLI
Produces a validated `Instruction` object. It is responsible for semantics, object aliases, and rejecting unsupported requests.

### Planner
Generates a typed PDDL problem and obtains a symbolic plan from Fast Downward when available. The fallback produces the same normalized action language for the small current domain.

### Simulation
Converts symbolic actions into robot motion, grasp, and release procedures. The PyBullet scene contains a fixed-base Franka Panda, a complete workbench, a placement box, and a set of colored manipulation objects.

## Status

The project is intentionally CLI-first. The current goal is a reliable, inspectable end-to-end architecture rather than a web interface.
