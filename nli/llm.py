from ollama import chat

from nli.schema import Instruction


MODEL = "mistral:7b"


SYSTEM_PROMPT = """
You are the natural language interface for a robotic
task-and-motion planning system.

Your job is ONLY to translate the user's natural-language
instruction into the provided structured representation.

You are NOT the planner.

You are NOT allowed to invent actions.

You are NOT allowed to explain your reasoning.

You must determine:

1. The intended robotic action.
2. The object involved.
3. The target, if applicable.

If the instruction is ambiguous, incomplete, contradictory,
or cannot be mapped reliably to one of the permitted actions,
set action to "unknown" and provide an error message.

Use only information explicitly provided by the user.

Do not infer unsupported objects, locations, or actions.
"""


def parse_instruction(user_input: str) -> Instruction:

    response = chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_input
            }
        ],
        format=Instruction.model_json_schema(),
        options={
            "temperature": 0
        }
    )

    return Instruction.model_validate_json(
        response.message.content
    )