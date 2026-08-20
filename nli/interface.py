import re

from nli.schema import Instruction
from nli.validator import validate_instruction
from nli.llm import parse_instruction


TARGET_PHRASES = {
    "box": "box",
    "container": "box",
}


def _recover_explicit_target(user_input: str, instruction: Instruction) -> Instruction:
    """Recover an explicitly stated target if the LLM emitted an unknown value.

    This is a grounding safeguard, not a semantic validator. The LLM remains
    free to interpret the sentence; this only prevents information explicitly
    present in the user's text from being discarded by an imperfect local model.
    """
    text = " ".join(user_input.lower().replace("_", " ").split())
    if instruction.target in {None, "unknown"}:
        for phrase, canonical in TARGET_PHRASES.items():
            if re.search(rf"\b{re.escape(phrase)}\b", text):
                instruction.target = canonical
                break
    return instruction


def process_instruction(user_input: str) -> Instruction:
    instruction = parse_instruction(user_input)
    instruction = _recover_explicit_target(user_input, instruction)
    return validate_instruction(instruction)
