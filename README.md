# Task-and-Motion Planning Agent

A hybrid **Task-and-Motion Planning (TAMP)** system that translates natural-language instructions into executable robotic behaviors. The project combines a local large language model, symbolic PDDL planning, geometric feasibility verification, and PyBullet simulation.

## Overview

The system addresses the gap between flexible human language and the deterministic representations required by robotic planning systems. A user provides a natural-language instruction such as:

> "Pick up the blue cube."

The instruction passes through three major stages:

1. **Natural Language Interface** - Mistral 7B interprets the instruction and converts it into a structured JSON goal specification.
2. **Hybrid PDDL Planner** - The JSON goal is translated into a PDDL problem and processed by Fast Downward. Symbolic preconditions and geometric feasibility are evaluated before an action sequence is produced.
3. **PyBullet Simulation** - The resulting action sequence is executed in a physics-based robotic environment, with feasibility checks performed during execution.

This architecture intentionally separates **language interpretation**, **symbolic planning**, and **physical execution** rather than relying on the LLM to directly control the robot.

## System Architecture

```text
┌──────────────────────────────┐
│      Human Instruction       │
│    "Pick up the blue cube"   │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│   Natural Language Interface │
│          Mistral 7B          │
│                              │
│ Natural Language -> JSON Goal │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│      PDDL-Based Planner      │
│        Fast Downward         │
│                              │
│ JSON -> PDDL -> Symbolic Plan  │
│ + Geometric Feasibility      │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│       PyBullet Simulator     │
│                              │
│     Franka Panda Robot       │
│     + Simulated Environment  │
└──────────────┬───────────────┘
               │
               ▼
        Task Success / Failure
```

The project therefore forms a pipeline from **natural language -> structured representation -> symbolic/geometric plan -> simulated robot execution**.

## Components

### 1. Natural Language Interface

The first component accepts free-form English instructions and uses a locally deployed **Mistral 7B** model to produce a structured JSON representation.

Example input:

```text
Pick up the blue cube.
```

Conceptually, the output is a machine-readable goal specification:

```json
{
  "goal": "pick",
  "object": "blue_cube"
}
```

The JSON representation provides an intermediate layer between ambiguous natural language and the deterministic symbolic planner. Invalid or nonsensical input can also be rejected at this stage.

### 2. PDDL Planner

The second component converts the structured goal specification into a **PDDL problem** and uses **Fast Downward** to perform symbolic planning.

The planner is responsible for determining whether the requested task is achievable according to the symbolic representation of the environment and action preconditions.

The planning stage also incorporates geometric feasibility considerations such as:

* Reachability
* Collision constraints
* Physical action validity
* Robot/environment constraints

If a valid plan exists, the planner produces an ordered action sequence for execution.

### 3. PyBullet Simulation

The third component provides the physical simulation environment.

PyBullet executes the actions produced by the planner using a simulated robotic system. After each action, the environment can perform feasibility checks to determine whether the intended state transition was successfully achieved.

The simulation serves both as a **feasibility validator** and as a **closed-loop execution environment** for evaluating the resulting plans.

## Planning Pipeline

The complete execution flow is:

```text
Natural Language
       │
       ▼
   Mistral 7B
       │
       ▼
Structured JSON
       │
       ▼
 PDDL Problem
       │
       ▼
Fast Downward
       │
       ▼
 Symbolic Plan
       │
       ▼
Geometric Validation
       │
       ▼
 PyBullet Execution
       │
       ▼
Success / Failure Log
```

At runtime, the system is intended to validate the request at multiple levels rather than allowing an unverified language-model output to directly control the simulator.

## Evaluation

The proposed evaluation benchmark is divided into three levels:

### Tier 1 - Unambiguous Instructions

Simple instructions with low semantic and planning complexity.

Examples:

```text
Pick up the blue cube.
Turn left.
Move the cube to the table.
```

### Tier 2 - Moderately Ambiguous Instructions

Instructions requiring limited contextual or common-sense inference.

### Tier 3 - Complex Instructions

Highly non-specific or multi-step instructions requiring more extensive reasoning and consideration of implicit constraints.

Potential evaluation metrics include:

* Task success rate
* Plan validity rate
* Failure-mode distribution
* LLM-to-planner parsing accuracy

These metrics are intended to measure both the reliability of the individual components and the performance of the complete pipeline.

## Technology Stack

| Component                 | Technology         |
| ------------------------- | ------------------ |
| Language interface        | Mistral 7B         |
| Structured representation | JSON               |
| Symbolic representation   | PDDL               |
| Classical planner         | Fast Downward      |
| Robotics simulation       | PyBullet           |
| Robot                     | Franka Emika Panda |
| Primary language          | Python             |

## Project Structure

The implementation is organized conceptually around the three system stages:

```text
tamp-agent/
│
├── interface/       # Natural-language processing and JSON generation
│
├── planner/         # PDDL domain/problem generation and Fast Downward
│
├── simulation/      # PyBullet environment and robot execution
│
├── pddl/            # PDDL domain definitions
│
├── tests/            # Component and integration tests
│
└── README.md
```

> The exact directory structure may change as development progresses.

## Design Philosophy

The central design decision is to **constrain the role of the LLM**.

Rather than asking the language model to reason about every aspect of robotic execution, the LLM primarily performs language interpretation and converts human instructions into a structured representation. Deterministic planning and simulation components then provide verification and execution.

This separation is intended to reduce the semantic gap between human instructions and robotic actions while preserving explicit validation at the planning and execution stages.

## Status

This project is under active development. The architecture, planner implementation, PDDL representation, and simulation environment are subject to change as the system is integrated and evaluated.

## References

* [Fast Downward](https://www.fast-downward.org/)
* [PyBullet](https://pybullet.org/)
* [PDDL Reference](https://planning.wiki/ref/pddl)
* [Integrated Task and Motion Planning](https://doi.org/10.1146/annurev-control-091420-084139)
* [The Fast Downward Planning System](https://doi.org/10.1613/jair.1705)
* [Language Models as Zero-Shot Planners](https://arxiv.org/abs/2201.07207)
* [Inner Monologue: Embodied Reasoning through Planning with Language Models](https://arxiv.org/abs/2207.05608)
* [Do As I Can, Not As I Say](https://arxiv.org/abs/2204.01691)
* [Logic-Geometric Programming](https://www.ijcai.org/Proceedings/15/Papers/274.pdf)

## Author

**Danish Lnu**
