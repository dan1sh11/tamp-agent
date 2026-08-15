from nli.schema import Instruction


def validate_instruction(instruction: Instruction) -> Instruction:

    # Model could not understand the instruction
    if instruction.action == "unknown":
        if not instruction.error:
            instruction.error = "Unable to determine a valid action."

        return instruction

    # Every non-unknown action requires an object
    if instruction.object is None:
        instruction.action = "unknown"
        instruction.error = "No object was identified."

        return instruction

    # Pick should not have a target
    if instruction.action == "pick":
        if instruction.target is not None:
            instruction.action = "unknown"
            instruction.error = (
                "Pick action should not contain a target."
            )

    # Place requires a target
    if instruction.action == "place":
        if instruction.target is None:
            instruction.action = "unknown"
            instruction.error = (
                "Place action requires a target."
            )

    return instruction