import re

from .actions import Action


class FastDownwardPlanError(RuntimeError):
    pass


ACTION_PATTERN = re.compile(r"^\s*\((\w+)(.*?)\)\s*$")


def parse_fast_downward_plan(plan_text: str) -> list[Action]:
    actions: list[Action] = []
    for raw_line in plan_text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith(";"):
            continue

        match = ACTION_PATTERN.match(line)
        if not match:
            continue

        action_name = match.group(1).lower()
        arguments = match.group(2).strip().split()

        if action_name == "pick" and len(arguments) == 1:
            obj = arguments[0]
            actions.extend([Action.move_to(obj), Action.grasp(obj)])
        elif action_name == "drop" and len(arguments) == 1:
            actions.append(Action.release())
        elif action_name == "place" and len(arguments) == 2:
            _, target = arguments
            actions.extend([Action.move_to(target), Action.release()])
        elif action_name == "move" and len(arguments) == 2:
            obj, target = arguments
            actions.extend([
                Action.move_to(obj),
                Action.grasp(obj),
                Action.move_to(target),
                Action.release(),
            ])
        else:
            raise FastDownwardPlanError(f"Unsupported or malformed planner action: {line}")

    if not actions:
        raise FastDownwardPlanError("Fast Downward returned no executable actions.")
    return actions
