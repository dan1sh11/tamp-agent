from nli.schema import Instruction


OBJECT_ALIASES = {
    "red cube": "large_cube_red",
    "large red cube": "large_cube_red",
    "small red cube": "small_cube_red",
    "blue cube": "large_cube_blue",
    "large blue cube": "large_cube_blue",
    "small blue cube": "small_cube_blue",
    "green cylinder": "cylinder_green",
    "yellow cylinder": "cylinder_yellow",
    "red cylinder": "cylinder_red",
    "sphere": "sphere",
    "capsule": "capsule",
}

TARGET_ALIASES = {
    "box": "box",
    "container": "box",
    "the box": "box",
    "the container": "box",
}

SUPPORTED_OBJECTS = set(OBJECT_ALIASES.values())
SUPPORTED_TARGETS = {"box"}


def _canonicalize(value: str | None, aliases: dict[str, str]) -> str | None:
    if value is None:
        return None

    normalized = " ".join(value.lower().strip().replace("_", " ").split())
    if normalized in aliases:
        return aliases[normalized]

    canonical = normalized.replace(" ", "_")
    if canonical in aliases.values():
        return canonical
    return None


def validate_instruction(instruction: Instruction) -> Instruction:
    if instruction.action == "unknown":
        instruction.error = instruction.error or "Unable to determine a supported action."
        return instruction

    instruction.object = _canonicalize(instruction.object, OBJECT_ALIASES)
    instruction.target = _canonicalize(instruction.target, TARGET_ALIASES)

    # PLACE and DROP may intentionally omit the object. The planner resolves
    # that reference from the robot's current held-object state. This allows
    # commands such as "place it in the box" after a successful pick.
    if instruction.action in {"place", "drop"}:
        if instruction.target is not None and instruction.action == "drop":
            instruction.action = "unknown"
            instruction.error = "Drop does not accept a target."
            return instruction

        if instruction.action == "place" and instruction.target not in SUPPORTED_TARGETS:
            instruction.action = "unknown"
            instruction.error = "Place requires the target box/container."
            return instruction

        return instruction

    if instruction.object not in SUPPORTED_OBJECTS:
        instruction.action = "unknown"
        instruction.error = "The instruction does not identify a supported scene object."
        return instruction

    if instruction.action == "pick":
        if instruction.target is not None:
            instruction.action = "unknown"
            instruction.error = "Pick should not contain a target."
        return instruction

    instruction.action = "unknown"
    instruction.error = "Unsupported action."
    return instruction
