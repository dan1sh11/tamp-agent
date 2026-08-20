from typing import Literal

from pydantic import BaseModel, ConfigDict


class Instruction(BaseModel):
    """Structured language interpretation passed to grounding and planning.

    This model intentionally validates structure, not scene semantics. The LLM
    may use natural-language object/target names; grounding happens downstream.
    """

    model_config = ConfigDict(extra="ignore")

    action: Literal["pick", "place", "drop", "move", "unknown"]
    object: str | None = None
    target: str | None = None
    error: str | None = None
