# Future Fast Downward -> simulator adapter.
#
# Keep PDDL/SAS parsing here, not inside the PyBullet environment.
#
# Example:
#
# Fast Downward:
#     (pick cube_red)
#     (place cube_red box)
#
# Adapter:
#     Action.move_to("cube_red")
#     Action.grasp("cube_red")
#     Action.move_to("box")
#     Action.release()
#
# The exact mapping must match the PDDL domain used by component 2.

import re

from .actions import Action


class FastDownwardPlanError(RuntimeError):
    pass


ACTION_PATTERN = re.compile(
    r"^\s*\((\w+)(.*?)\)\s*$"
)


def parse_fast_downward_plan(
    plan_text: str,
) -> list[Action]:

    actions = []

    for line in plan_text.splitlines():

        line = line.strip()

        if not line:
            continue

        if line.startswith(";"):
            continue

        match = ACTION_PATTERN.match(line)

        if not match:
            continue

        action_name = match.group(1).lower()
        arguments = match.group(2).strip().split()

        if action_name == "pick":

            if len(arguments) != 1:
                raise FastDownwardPlanError(
                    f"Invalid pick action: {line}"
                )

            obj = arguments[0]

            actions.append(
                Action.move_to(obj)
            )

            actions.append(
                Action.grasp(obj)
            )

        elif action_name == "place":

            if len(arguments) != 2:
                raise FastDownwardPlanError(
                    f"Invalid place action: {line}"
                )

            obj, target = arguments

            actions.append(
                Action.move_to(target)
            )

            actions.append(
                Action.release()
            )

        else:
            raise FastDownwardPlanError(
                f"Unknown planner action: {action_name}"
            )

    return actions
