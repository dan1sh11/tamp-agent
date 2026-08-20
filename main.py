import os
import sys
from contextlib import redirect_stdout
from pathlib import Path

from nli.interface import process_instruction
from nli.schema import Instruction
from planning.planner import FastDownwardPlanner, PlannerError
from simulation.environment import TAMPEnvironment
from simulation.executor import PlanExecutionError, PlanExecutor
from simulation.fast_downward_adapter import FastDownwardPlanError, parse_fast_downward_plan

ROOT = Path(__file__).resolve().parent
DOMAIN = ROOT / "planning" / "domain.pddl"
DEFAULT_PLANNER = ROOT / "planning" / "fast-downward.py"
WORKSPACE = ROOT / "planning" / "generated"
LOG_DIR = ROOT / "logs"


class Tee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for stream in self.streams:
            stream.write(data)
            stream.flush()
        return len(data)

    def flush(self):
        for stream in self.streams:
            stream.flush()


def _next_execution_log() -> Path:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    numbers = []
    for path in LOG_DIR.glob("execution_*.log"):
        try:
            numbers.append(int(path.stem.split("_")[-1]))
        except ValueError:
            pass
    return LOG_DIR / f"execution_{max(numbers, default=0) + 1}.log"


def _resolve_instruction_state(instruction: Instruction, held_object: str | None) -> Instruction:
    if instruction.action in {"place", "drop"} and instruction.object is None:
        if held_object is None:
            raise PlannerError(
                f"Cannot {instruction.action}: the robot is not currently holding an object."
            )
        instruction.object = held_object
    return instruction


def _run_instruction(user_input: str, planner: FastDownwardPlanner, executor: PlanExecutor) -> None:
    instruction = process_instruction(user_input)
    held_object = executor.held_object
    instruction = _resolve_instruction_state(instruction, held_object)

    print("\n[NLI]")
    print(instruction.model_dump_json(indent=2))

    if instruction.action == "unknown":
        print(f"Rejected: {instruction.error}")
        return

    print("\n[PDDL / PLANNER]")
    plan_text = planner.plan(instruction, held_object=held_object)
    actions = parse_fast_downward_plan(plan_text)
    print(plan_text.strip())

    print("\n[SIMULATION]")
    for action in actions:
        print(f"  {action.type.value}: {action.parameters}")
    executor.execute(actions)
    print("Execution complete.")


def main() -> None:
    planner_path = os.getenv("FAST_DOWNWARD_PATH", str(DEFAULT_PLANNER))
    planner = FastDownwardPlanner(planner_path, DOMAIN, WORKSPACE)

    print("TAMP Agent")
    print("Language -> PDDL -> Plan -> PyBullet")
    print(
        "Planner: "
        + (
            f"Fast Downward ({planner.fast_downward_path})"
            if planner.using_fast_downward
            else "deterministic local fallback"
        )
    )
    print("Type 'quit' or press Ctrl+C to exit.")
    print(f"Execution logs: {LOG_DIR}")

    env = TAMPEnvironment(gui=True)
    executor = PlanExecutor(env)

    try:
        while True:
            user_input = input("\nRobot instruction: ").strip()
            if not user_input:
                continue
            if user_input.lower() in {"quit", "exit"}:
                break

            log_path = _next_execution_log()
            with log_path.open("w", encoding="utf-8") as log_file:
                log_file.write(f"Execution log: {log_path.name}\n")
                log_file.write(f"User input: {user_input}\n")
                log_file.write("=" * 72 + "\n")
                tee = Tee(sys.stdout, log_file)
                try:
                    with redirect_stdout(tee):
                        _run_instruction(user_input, planner, executor)
                except (
                    PlannerError,
                    FastDownwardPlanError,
                    PlanExecutionError,
                    ValueError,
                ) as exc:
                    print(f"\nTask failed: {exc}")

            print(f"[LOG] {log_path}")

    except KeyboardInterrupt:
        print("\nShutting down.")
    finally:
        env.close()


if __name__ == "__main__":
    main()
