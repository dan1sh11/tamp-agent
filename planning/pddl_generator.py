from pathlib import Path

from nli.schema import Instruction


SCENE_OBJECTS = [
    "large_cube_red", "large_cube_blue", "cylinder_green", "cylinder_yellow",
    "sphere", "capsule", "small_cube_red", "cylinder_red", "small_cube_blue",
]
RECEPTACLES = ["box"]


class PDDLGenerationError(RuntimeError):
    pass


class PDDLGenerator:
    def __init__(self, domain_path: str | Path):
        self.domain_path = Path(domain_path)

    def generate_problem(self, instruction: Instruction) -> str:
        if instruction.action == "unknown":
            raise PDDLGenerationError(instruction.error or "Unknown instruction.")
        if instruction.object not in SCENE_OBJECTS:
            raise PDDLGenerationError(f"Unknown object: {instruction.object}")
        if instruction.action == "place" and instruction.target not in RECEPTACLES:
            raise PDDLGenerationError(f"Unknown target: {instruction.target}")

        objects = "\n".join(f"        {name} - object" for name in SCENE_OBJECTS)
        receptacles = "\n".join(f"        {name} - receptacle" for name in RECEPTACLES)
        initial_state = "\n".join(f"        (on-table {name})" for name in SCENE_OBJECTS)
        initial_state += "\n        (hand-empty)"
        goal = self._generate_goal(instruction)

        return f"""(define (problem tamp-task)
    (:domain tamp-agent)
    (:objects
{objects}
{receptacles}
    )
    (:init
{initial_state}
    )
    (:goal
        {goal}
    )
)
"""

    def _generate_goal(self, instruction: Instruction) -> str:
        obj = instruction.object
        if instruction.action == "pick":
            return f"(holding {obj})"
        if instruction.action == "place":
            return f"(in {obj} {instruction.target})"
        raise PDDLGenerationError(f"Unsupported action: {instruction.action}")
