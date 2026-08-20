from typing import Literal

from pydantic import BaseModel


class Instruction(BaseModel):
    """Canonical interface between language interpretation and planning."""

    action: Literal["pick", "place", "unknown"]
    object: str | None = None
    target: str | None = None
    error: str | None = None
