import subprocess
from pathlib import Path

from nli.schema import Instruction
from .pddl_generator import PDDLGenerator


class PlannerError(RuntimeError):
    pass


class FastDownwardPlanner:
    def __init__(self, fast_downward_path: str | Path, domain_path: str | Path, working_directory: str | Path):
        self.fast_downward_path = Path(fast_downward_path)
        self.domain_path = Path(domain_path)
        self.working_directory = Path(working_directory)
        self.working_directory.mkdir(parents=True, exist_ok=True)
        self.generator = PDDLGenerator(self.domain_path)

    def plan(self, instruction: Instruction) -> str:
        problem_path = self.working_directory / "problem.pddl"
        problem_path.write_text(self.generator.generate_problem(instruction), encoding="utf-8")

        # The full Fast Downward distribution is intentionally optional in deployment.
        # For the current two-action domain, this deterministic fallback preserves the
        # planner -> simulator contract when the native planner binary is unavailable.
        if not self.fast_downward_path.exists():
            if instruction.action == "pick":
                return f"(pick {instruction.object})\n"
            if instruction.action == "place":
                return f"(pick {instruction.object})\n(place {instruction.object} {instruction.target})\n"
            raise PlannerError(f"Unsupported action: {instruction.action}")

        command = [
            str(self.fast_downward_path), str(self.domain_path), str(problem_path),
            "--search", "astar(lmcut())",
        ]
        result = subprocess.run(
            command,
            cwd=self.fast_downward_path.parent,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise PlannerError(
                "Fast Downward failed.\n\n"
                f"STDOUT:\n{result.stdout}\n\n"
                f"STDERR:\n{result.stderr}"
            )
        return result.stdout
