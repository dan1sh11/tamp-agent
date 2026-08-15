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

from .actions import Action


def parse_fast_downward_plan(plan_text: str) -> list[Action]:
    raise NotImplementedError(
        "Implement after the PDDL action vocabulary is finalized."
    )
