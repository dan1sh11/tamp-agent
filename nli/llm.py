from ollama import chat

from nli.schema import Instruction


MODEL = "mistral:7b"


SYSTEM_PROMPT = """
You are the natural-language interface for a robotic task-and-motion planning system.

Translate the user's instruction into exactly one supported action:
- pick: pick up one named object
- place: put one named object into the box/container
- drop: release one named object at its current location without moving it to a target
- unknown: use when the request is unsupported, ambiguous, incomplete, or cannot be mapped reliably

You are NOT the planner and must not invent a plan.
Do not explain your reasoning.
Use only information stated by the user.

Supported scene objects are:
large red cube, large blue cube, small red cube, small blue cube,
red cylinder, green cylinder, yellow cylinder, sphere, capsule.

The only supported placement target is the box/container. A drop has no target.

Return only the supplied JSON schema.
"""


def parse_instruction(user_input: str) -> Instruction:
    response = chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input},
        ],
        format=Instruction.model_json_schema(),
        options={"temperature": 0},
    )

    return Instruction.model_validate_json(response.message.content)
