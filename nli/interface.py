from nli.schema import Instruction
from nli.validator import validate_instruction
from nli.llm import parse_instruction


def process_instruction(user_input: str) -> Instruction:

    instruction = parse_instruction(user_input)

    instruction = validate_instruction(instruction)

    return instruction

