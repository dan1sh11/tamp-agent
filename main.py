from pathlib import Path

from nli.interface import process_instruction

from planning.planner import FastDownwardPlanner

from simulation.environment import TAMPEnvironment
from simulation.executor import PlanExecutor
from simulation.fast_downward_adapter import (
    parse_fast_downward_plan,
)


ROOT = Path(__file__).resolve().parent

DOMAIN = ROOT / "planning" / "domain.pddl"

PLANNER = ROOT / "fast-downward.py"

WORKSPACE = (
    ROOT / "planning" / "generated"
)


def main():

    planner = FastDownwardPlanner(
        fast_downward_path=PLANNER,
        domain_path=DOMAIN,
        working_directory=WORKSPACE,
    )

    env = TAMPEnvironment(gui=True)

    executor = PlanExecutor(env)

    try:

        while True:

            user_input = input(
                "\nRobot instruction: "
            )

            if not user_input.strip():
                continue

            instruction = process_instruction(
                user_input
            )

            print(
                "\nNLI output:"
            )

            print(
                instruction.model_dump_json(
                    indent=2
                )
            )

            if instruction.action == "unknown":
                print(
                    f"Rejected: {instruction.error}"
                )
                continue

            print(
                "\nPlanning..."
            )

            plan_text = planner.plan(
                instruction
            )

            print(
                "\nFast Downward plan:"
            )

            print(plan_text)

            actions = (
                parse_fast_downward_plan(
                    plan_text
                )
            )

            print(
                "\nSimulator actions:"
            )

            for action in actions:
                print(action)

            executor.execute(actions)

            print(
                "\nExecution complete."
            )

    except KeyboardInterrupt:

        pass

    finally:

        env.close()


if __name__ == "__main__":
    main()