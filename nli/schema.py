from typing import Literal

from pydantic import BaseModel, ConfigDict, model_validator


Action = Literal["pick", "place", "drop", "move", "unknown"]


class Instruction(BaseModel):
    """Structured semantic interpretation consumed by grounding/planning."""

    model_config = ConfigDict(extra="ignore")

    action: Action
    object: str | None = None
    target: str | None = None
    error: str | None = None

    @model_validator(mode="after")
    def validate_semantics(self) -> "Instruction":
        if self.action == "unknown":
            return self
        if self.action == "pick":
            if self.object is None:
                raise ValueError("pick requires an object")
            if self.target is not None:
                raise ValueError("pick cannot have a target")
        elif self.action == "place":
            if self.target is None:
                raise ValueError("place requires a target")
        elif self.action == "drop":
            if self.target is not None:
                raise ValueError("drop cannot have a target; use place instead")
        elif self.action == "move":
            if self.target is None:
                raise ValueError("move requires a target")
        return self
