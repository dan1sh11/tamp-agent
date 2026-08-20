from nli.schema import Instruction


# Stable symbolic object names from simulation/scene_contract.json.
# There are exactly nine manipulable scene objects.
OBJECT_ALIASES = {
    "large_cube_red": "large_cube_red",
    "large red cube": "large_cube_red",
    "big red cube": "large_cube_red",
    "large red block": "large_cube_red",
    "big red block": "large_cube_red",

    "large_cube_blue": "large_cube_blue",
    "large blue cube": "large_cube_blue",
    "big blue cube": "large_cube_blue",
    "large blue block": "large_cube_blue",
    "big blue block": "large_cube_blue",

    "small_cube_red": "small_cube_red",
    "small red cube": "small_cube_red",
    "small red block": "small_cube_red",
    "tiny red cube": "small_cube_red",
    "tiny red block": "small_cube_red",
    "little red cube": "small_cube_red",
    "little red block": "small_cube_red",

    "small_cube_blue": "small_cube_blue",
    "small blue cube": "small_cube_blue",
    "small blue block": "small_cube_blue",
    "tiny blue cube": "small_cube_blue",
    "tiny blue block": "small_cube_blue",
    "little blue cube": "small_cube_blue",
    "little blue block": "small_cube_blue",

    "cylinder_green": "cylinder_green",
    "green cylinder": "cylinder_green",

    "cylinder_yellow": "cylinder_yellow",
    "yellow cylinder": "cylinder_yellow",

    "cylinder_red": "cylinder_red",
    "red cylinder": "cylinder_red",

    "sphere": "sphere",
    "ball": "sphere",

    "capsule": "capsule",
}

# The simulator exposes exactly one receptacle: box.
TARGET_ALIASES = {
    "box": "box",
    "the box": "box",
    "container": "box",
    "the container": "box",
    "bin": "box",
    "the bin": "box",
    "receptacle": "box",
    "the receptacle": "box",
}

SUPPORTED_OBJECTS = {
    "large_cube_red",
    "large_cube_blue",
    "cylinder_green",
    "cylinder_yellow",
    "sphere",
    "capsule",
    "small_cube_red",
    "cylinder_red",
    "small_cube_blue",
}
SUPPORTED_TARGETS = {"box"}
SUPPORTED_ACTIONS = {"pick", "place", "drop", "move", "unknown"}


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
    """Normalize an NLI result into the simulator's stable symbolic contract.

    This layer does not decide what the user meant. It only canonicalizes
    aliases after the LLM has selected an interpretation. Ambiguous phrases
    such as "red cube" are intentionally absent because two red cubes exist;
    therefore the LLM must return unknown instead of guessing.
    """
    if instruction.action not in SUPPORTED_ACTIONS:
        instruction.action = "unknown"
        instruction.error = "Unsupported action structure."
        return instruction

    instruction.object = _ground(instruction.object, OBJECT_ALIASES) or instruction.object
    instruction.target = _ground(instruction.target, TARGET_ALIASES) or instruction.target

    # A targeted release is a placement operation. Never discard an explicit
    # destination before the deterministic planner sees it.
    if instruction.action == "drop" and instruction.target is not None:
        instruction.action = "place"

    return instruction
