import os
from pathlib import Path

from nli.interface import process_instruction
from planning.planner import FastDownwardPlanner, PlannerError
from simulation.environment import TAMPEnvironment
from simulation.executor import PlanExecutionError, PlanExecutor
from simulation.fast_downward_adapter import (
    FastDownwardPlanError,
    parse_fast_downward_plan,
)

ROOT = Path(__file__).resolve().parent
DOMAIN = ROOT / "planning" / "domain.pddl"
DEFAULT_PLANNER = ROOT / "planning" / "fast-downward.py"
WORKSPACE = ROOT / "planning" / "generated"


def main() -> None:
    planner_path = os.getenv("FAST_DOWNWARD_PATH", str(DEFAULT_PLANNER))
    planner = FastDownwardPlanner(planner_path, DOMAIN, WORKSPACE)

    print("TAMP Agent")
    print("Language -> PDDL -> Plan -> PyBullet")
    print(
        "Planner: "
        + (f"Fast Downward ({planner.fast_downward_path})" if planner.using_fast_downward else "deterministic local fallback")
    )
    print("Type 'quit' or press Ctrl+C to exit.")

    env = TAMPEnvironment(gui=True)
    executor = PlanExecutor(env)

    try:
        while True:
            user_input = input("\nRobot instruction: ").strip()
            if not user_input:
                continue
            if user_input.lower() in {"quit", "exit"}:
                break

            try:
                instruction = process_instruction(user_input)
                print("\n[NLI]")
                print(instruction.model_dump_json(indent=2))

                if instruction.action == "unknown":
                    print(f"Rejected: {instruction.error}")
                    continue

                print("\n[PDDL / PLANNER]")
                plan_text = planner.plan(instruction)
                actions = parse_fast_downward_plan(plan_text)
                print(plan_text.strip())

                print("\n[SIMULATION]")
                for action in actions:
                    print(f"  {action.type.value}: {action.parameters}")
                executor.execute(actions)
                print("Execution complete.")

            except (
                PlannerError,
                FastDownwardPlanError,
                PlanExecutionError,
                ValueError,
            ) as exc:
                print(f"\nTask failed: {exc}")

    except KeyboardInterrupt:
        print("\nShutting down.")
    finally:
        env.close()


if __name__ == "__main__":
    main()
