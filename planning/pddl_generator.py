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

    def generate_problem(
        self,
        instruction: Instruction,
        held_object: str | None = None,
    ) -> str:
        if instruction.action == "unknown":
            raise PDDLGenerationError(instruction.error or "Unknown instruction.")
        if instruction.object not in SCENE_OBJECTS:
            raise PDDLGenerationError(f"Unknown object: {instruction.object}")
        if held_object is not None and held_object not in SCENE_OBJECTS:
            raise PDDLGenerationError(f"Unknown held object: {held_object}")

        if instruction.action == "place" and instruction.target not in RECEPTACLES:
            raise PDDLGenerationError(f"Unknown target: {instruction.target}")
        if instruction.action == "drop" and instruction.target is not None:
            raise PDDLGenerationError("Drop does not accept a target.")

        # The PDDL problem must represent the simulator's current state.
        # Otherwise every command starts from an artificial empty-hand state,
        # causing a second pick to be planned for a drop/place command issued
        # after a previous pick.
        if instruction.action in {"drop", "place"}:
            if held_object is None:
                raise PDDLGenerationError(
                    f"Cannot {instruction.action} '{instruction.object}': the robot is not holding an object."
                )
            if held_object != instruction.object:
                raise PDDLGenerationError(
                    f"Cannot {instruction.action} '{instruction.object}': robot is holding '{held_object}'."
                )
        elif instruction.action == "pick" and held_object is not None:
            raise PDDLGenerationError(
                f"Cannot pick '{instruction.object}': robot is already holding '{held_object}'."
            )

        objects = "\n".join(f"        {name} - object" for name in SCENE_OBJECTS)
        receptacles = "\n".join(f"        {name} - receptacle" for name in RECEPTACLES)

        initial_state_lines = []
        for name in SCENE_OBJECTS:
            if name != held_object:
                initial_state_lines.append(f"        (on-table {name})")
        if held_object is not None:
            initial_state_lines.append(f"        (holding {held_object})")
        else:
            initial_state_lines.append("        (hand-empty)")

        initial_state = "\n".join(initial_state_lines)
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
        if instruction.action == "drop":
            return f"(and (on-table {obj}) (hand-empty))"
        if instruction.action == "place":
            return f"(in {obj} {instruction.target})"
        raise PDDLGenerationError(f"Unsupported action: {instruction.action}")
