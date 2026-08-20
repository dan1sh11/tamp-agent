from pathlib import Path

from nli.schema import Instruction


SCENE_OBJECTS = [
    "large_cube_red", "large_cube_blue", "cylinder_green", "cylinder_yellow",
    "small_cube_red", "cylinder_red", "small_cube_blue",
]
RECEPTACLES = ["box"]


class PDDLGenerationError(RuntimeError):
    pass


class PDDLGenerator:
    def __init__(self, domain_path: str | Path):
        self.domain_path = Path(domain_path)

    def generate_problem(self, instruction: Instruction, held_object: str | None = None) -> str:
        if instruction.action == "unknown":
            raise PDDLGenerationError(instruction.error or "Unable to interpret instruction.")

        if instruction.action in {"pick", "drop", "place", "move"} and instruction.object is None:
            if instruction.action in {"drop", "place"} and held_object is not None:
                instruction.object = held_object
            else:
                raise PDDLGenerationError("The instruction does not identify an executable object.")

        if instruction.object not in SCENE_OBJECTS:
            raise PDDLGenerationError(
                f"Unknown object '{instruction.object}'. Known objects: {SCENE_OBJECTS}"
            )
        if held_object is not None and held_object not in SCENE_OBJECTS:
            raise PDDLGenerationError(f"Unknown held object: {held_object}")

        if instruction.action in {"place", "move"}:
            if instruction.target is None:
                raise PDDLGenerationError(
                    f"The {instruction.action} action requires a target."
                )
            if instruction.target not in RECEPTACLES:
                raise PDDLGenerationError(
                    f"Unknown target '{instruction.target}'. Known targets: {RECEPTACLES}"
                )

        if instruction.action == "drop" and instruction.target is not None:
            instruction.target = None

        if instruction.action in {"drop", "place"}:
            if held_object != instruction.object:
                raise PDDLGenerationError(
                    f"Cannot {instruction.action} '{instruction.object}': robot is holding '{held_object}'."
                )
        elif instruction.action in {"pick", "move"} and held_object is not None:
            raise PDDLGenerationError(
                f"Cannot {instruction.action} '{instruction.object}': robot is already holding '{held_object}'."
            )

        objects = "\n".join(f"        {name} - object" for name in SCENE_OBJECTS)
        receptacles = "\n".join(f"        {name} - receptacle" for name in RECEPTACLES)

        initial_state_lines = [
            f"        (on-table {name})"
            for name in SCENE_OBJECTS
            if name != held_object
        ]
        initial_state_lines.append(
            f"        (holding {held_object})" if held_object else "        (hand-empty)"
        )

        return f"""(define (problem tamp-task)
    (:domain tamp-agent)
    (:objects
{objects}
{receptacles}
    )
    (:init
{chr(10).join(initial_state_lines)}
    )
    (:goal
        {self._generate_goal(instruction)}
    )
)
"""

    @staticmethod
    def _generate_goal(instruction: Instruction) -> str:
        if instruction.action == "pick":
            return f"(holding {instruction.object})"
        if instruction.action == "drop":
            return f"(and (on-table {instruction.object}) (hand-empty))"
        if instruction.action in {"place", "move"}:
            return f"(in {instruction.object} {instruction.target})"
        raise PDDLGenerationError(f"Unsupported action: {instruction.action}")
