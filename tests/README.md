# NLI Evaluation

This directory evaluates only the Natural Language Interface. It does not evaluate PDDL planning or PyBullet execution.

The benchmark deliberately mixes canonical commands, paraphrases, descriptive references, typos, ambiguous references, compound commands, and unsupported requests.

## Run

From the repository root on the machine with Ollama and `mistral:7b`:

```bash
python tests/run_nli_benchmark.py
```

The runner writes the model's actual outputs and pass/fail comparison to `tests/nli_results.json`.

The checked-in result file is a placeholder until the benchmark is run against the local model. No accuracy number is fabricated.
