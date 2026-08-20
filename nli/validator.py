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
}

TARGET_ALIASES = {
    "box": "box",
    "container": "box",
    "the box": "box",
    "the container": "box",
}

SUPPORTED_OBJECTS = set(OBJECT_ALIASES.values())
SUPPORTED_TARGETS = {"box"}


def _normalize_text(value: str | None) -> str | None:
    if value is None:
        return None
    return " ".join(value.lower().strip().replace("_", " ").split())


def _ground(value: str | None, aliases: dict[str, str]) -> str | None:
    normalized = _normalize_text(value)
    if normalized is None:
        return None
    if normalized in aliases:
        return aliases[normalized]
    canonical = normalized.replace(" ", "_")
    if canonical in aliases.values():
        return canonical
    return None


def validate_instruction(instruction: Instruction) -> Instruction:
    """Validate the JSON contract without constraining LLM language semantics.

    Unknown natural-language entities are preserved in the Instruction. Only
    execution/planning grounding decides whether a phrase maps to a known scene
    entity. This prevents the validator from turning a valid interpretation into
    an artificial 'unknown' instruction.
    """
    if instruction.action not in {"pick", "place", "drop", "move", "unknown"}:
        instruction.action = "unknown"
        instruction.error = "Unsupported action structure."
        return instruction

    instruction.object = _ground(instruction.object, OBJECT_ALIASES) or instruction.object
    instruction.target = _ground(instruction.target, TARGET_ALIASES) or instruction.target

    if instruction.action == "drop":
        if instruction.target is not None:
            instruction.error = "Drop ignores placement targets."
            instruction.target = None
        return instruction

    if instruction.action in {"place", "move"}:
        return instruction

    if instruction.action == "pick":
        return instruction

    return instruction
