# NLI Evaluation

This directory evaluates the Natural Language Interface for the `fix/simulation-ik-execution` branch. It does not evaluate PDDL planning or PyBullet execution.

The benchmark is derived from the actual simulation scene contract:

- **9 manipulable objects:** `large_cube_red`, `large_cube_blue`, `cylinder_green`, `cylinder_yellow`, `sphere`, `capsule`, `small_cube_red`, `cylinder_red`, `small_cube_blue`
- **1 receptacle:** `box`
- **NLI actions:** `pick`, `place`, `drop`, `move`, `unknown`

The tests intentionally cover canonical commands, synonyms, descriptive object references, spelling errors, ambiguity, contextual references, direct placement, compound transfer, and unsupported commands.

Expected values are the **final structured NLI contract after deterministic grounding**, so simulator-facing identifiers are used rather than arbitrary natural-language aliases.

## Run

From the repository root on the machine hosting Ollama and `mistral:7b`:

```bash
python tests/run_nli_benchmark.py
```

The runner writes the actual model outputs and pass/fail comparison to `tests/nli_results.json`.

The checked-in result file is intentionally a placeholder until the benchmark is run against the local model. No accuracy number is fabricated.
