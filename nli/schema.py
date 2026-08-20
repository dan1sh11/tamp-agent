from typing import Literal

from pydantic import BaseModel, ConfigDict


Action = Literal["pick", "place", "drop", "move", "unknown"]


class Instruction(BaseModel):
    """Semantic NLI result passed to deterministic grounding/planning.

    The schema deliberately validates only the output *shape*. Semantic
    interpretation and grounding are performed by the NLI prompt and the
    deterministic validator respectively. In particular, this model must not
    reject a model output before the validator has a chance to normalize it.
    """

    model_config = ConfigDict(extra="ignore")

    action: Action
    object: str | None = None
    target: str | None = None
    error: str | None = None
