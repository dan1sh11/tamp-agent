"""Run the Mistral NLI benchmark and write real outputs to nli_results.json."""

import json
from pathlib import Path

from nli.interface import process_instruction
from nli_cases import CASES

RESULTS = Path(__file__).with_name("nli_results.json")


def normalized(value):
    return {
        "action": value.action,
        "object": value.object,
        "target": value.target,
    }


def main():
    results = []
    passed = 0

    for case in CASES:
        try:
            actual_model = process_instruction(case["input"])
            actual = normalized(actual_model)
            expected = case["expected"]
            ok = actual == expected
            if ok:
                passed += 1
            results.append({
                "id": case["id"],
                "input": case["input"],
                "expected": expected,
                "actual": actual,
                "model_error": actual_model.error,
                "pass": ok,
            })
        except Exception as exc:
            results.append({
                "id": case["id"],
                "input": case["input"],
                "expected": case["expected"],
                "actual": None,
                "model_error": f"{type(exc).__name__}: {exc}",
                "pass": False,
            })

    report = {
        "model": "mistral:7b",
        "temperature": 0,
        "case_count": len(CASES),
        "passed": passed,
        "failed": len(CASES) - passed,
        "accuracy": passed / len(CASES) if CASES else 0.0,
        "note": "Results are generated from the local Ollama model; run this script on the machine hosting mistral:7b.",
        "cases": results,
    }
    RESULTS.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"NLI accuracy: {passed}/{len(CASES)} ({report['accuracy']:.1%})")
    print(f"Results: {RESULTS}")


if __name__ == "__main__":
    main()
