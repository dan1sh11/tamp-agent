from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


Action = Literal["pick", "place", "drop", "move", "unknown"]


class Instruction(BaseModel):
    """Semantic NLI result passed to deterministic grounding/planning."""

    model_config = ConfigDict(extra="ignore")

    action: Action = Field(
        description=(
            "Semantic action. pick=acquire an object; place=directly put an object "
            "at a target; drop=untargeted release; move=explicit compound/transfer "
            "request; unknown=unsupported or unresolved request."
        )
    )
    object: str | None = Field(
        default=None,
        description="Object referred to by the user, or null when unresolved/contextual.",
    )
    target: str | None = Field(
        default=None,
        description="Destination/receptacle referred to by the user, or null when none is stated.",
    )
    error: str | None = Field(
        default=None,
        description="Optional interpretation error; normally null for valid requests.",
    )
