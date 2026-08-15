from typing import Literal
from pydantic import BaseModel


class Instruction(BaseModel):
    action: Literal[
        "pick",
        "place",
        "move",
        "unknown",
        None
    ]

    object: str | None
    target: str | None
    error: str | None