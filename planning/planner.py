import os
import shutil
import subprocess
from pathlib import Path

from nli.schema import Instruction
from .pddl_generator import PDDLGenerator


class PlannerError(RuntimeError):
    pass


class FastDownwardPlanner:
    def __init__(
        self,
        fast_downward_path: str | Path | None,
        domain_path: str | Path,
        working_directory: str | Path,
    ):
        self.fast_downward_path = self._resolve_planner(fast_downward_path)
        self.domain_path = Path(domain_path).resolve()
        self.working_directory = Path(working_directory).resolve()
        self.working_directory.mkdir(parents=True, exist_ok=True)
        self.generator = PDDLGenerator(self.domain_path)

    @staticmethod
    def _resolve_planner(path: str | Path | None) -> Path | None:
        candidates = []
        if path:
            candidates.append(Path(path))
        env_path = os.getenv("FAST_DOWNWARD_PATH")
        if env_path:
            candidates.append(Path(env_path))

        discovered = shutil.which("fast-downward.py")
        if discovered:
            candidates.append(Path(discovered))

        for candidate in candidates:
            if candidate.exists():
                return candidate.resolve()
        return None

    @property
    def using_fast_downward(self) -> bool:
        return self.fast_downward_path is not None

    def plan(self, instruction: Instruction) -> str:
        problem_path = self.working_directory / "problem.pddl"
        problem_path.write_text(
            self.generator.generate_problem(instruction),
            encoding="utf-8",
        )

        if self.fast_downward_path is None:
            return self._deterministic_fallback(instruction)

        command = [
            str(self.fast_downward_path),
            str(self.domain_path),
            str(problem_path),
            "--search",
            "astar(lmcut())",
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

    @staticmethod
    def _deterministic_fallback(instruction: Instruction) -> str:
        """Keep the CLI runnable when Fast Downward is not installed."""
        if instruction.action == "pick":
            return f"(pick {instruction.object})\n"
        if instruction.action == "place":
            return (
                f"(pick {instruction.object})\n"
                f"(place {instruction.object} {instruction.target})\n"
            )
        raise PlannerError(instruction.error or "Unsupported action")
