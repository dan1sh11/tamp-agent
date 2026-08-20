# TAMP Agent

A web-accessible task-and-motion planning prototype that converts natural-language robot commands into validated symbolic plans and, locally, executes those plans in a PyBullet Franka Panda simulation.

## Architecture

```text
Browser
   |
   v
Flask Web Interface
   |
   +--> Local Mistral 7B via Ollama
   |        |
   |        v
   |    Structured Instruction
   |        |
   +--------+
            v
      PDDL Problem Generator
            |
            v
       Fast Downward
            |
            v
     Plan -> Action Adapter
            |
            v
       PyBullet + Panda
```

The LLM is deliberately restricted to natural-language interpretation. PDDL planning and robot execution remain deterministic layers.

## Web interface

The browser dashboard exposes the NLI output, generated PDDL, symbolic plan, and execution status. Start it locally with:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open `http://localhost:5000`.

## Local Mistral

Install Ollama and pull the model used by `nli/llm.py`:

```bash
ollama pull mistral:7b
ollama serve
```

The web backend calls Ollama through its local API. No paid LLM API is required.

If Ollama is unavailable, the web API falls back to a deterministic parser for the supported scene vocabulary so the interface can still demonstrate the planning pipeline.

## Local robot simulation

The full PyBullet GUI remains available through:

```bash
python main.py
```

The web server intentionally does not attempt to launch a desktop PyBullet GUI. A future browser-based 3D viewer can consume simulation state from a headless PyBullet process.

## Supported objects

- large red cube
- large blue cube
- small red cube
- small blue cube
- red / green / yellow cylinders
- sphere
- capsule
- box receptacle

## Example commands

```text
Pick up the blue cube.
Put the red cube in the box.
Pick up the green cylinder.
```

## Project status

This is a research/portfolio prototype. The current web layer plans and validates tasks; full physical execution is retained as a local PyBullet workflow. Browser-based 3D execution is the next architectural extension.
