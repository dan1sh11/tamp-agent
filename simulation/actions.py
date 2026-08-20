from dataclasses import dataclass
from enum import Enum
from typing import Any


class ActionType(str, Enum):
    MOVE_TO = "move_to"
    GRASP = "grasp"
    PLACE = "place"
    RELEASE = "release"
    WAIT = "wait"
    HOME = "home"


@dataclass(frozen=True)
class Action:
    type: ActionType
    parameters: dict[str, Any]

    @staticmethod
    def move_to(object_name: str) -> "Action":
        return Action(ActionType.MOVE_TO, {"object": object_name})

    @staticmethod
    def grasp(object_name: str) -> "Action":
        return Action(ActionType.GRASP, {"object": object_name})

    @staticmethod
    def place(object_name: str, target_name: str) -> "Action":
        return Action(ActionType.PLACE, {"object": object_name, "target": target_name})

    @staticmethod
    def release() -> "Action":
        return Action(ActionType.RELEASE, {})

    @staticmethod
    def wait(steps: int = 60) -> "Action":
        return Action(ActionType.WAIT, {"steps": steps})

    @staticmethod
    def home() -> "Action":
        return Action(ActionType.HOME, {})
