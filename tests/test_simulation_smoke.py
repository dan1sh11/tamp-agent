"""Headless regression test for the pick -> place execution path."""

import pybullet as p

from simulation.actions import Action
from simulation.environment import TAMPEnvironment
from simulation.executor import PlanExecutor


def main():
    env = TAMPEnvironment(gui=False)
    try:
        executor = PlanExecutor(env)
        executor.execute([
            Action.move_to("large_cube_red"),
            Action.grasp("large_cube_red"),
            Action.place("large_cube_red", "box"),
        ])

        if executor.held_object is not None:
            raise AssertionError("Robot still holds the object after place")

        obj = env.registry.get("large_cube_red")
        aabb_min, aabb_max = p.getAABB(obj.body_id)
        bx, by = env.config.box_center
        sx, sy, _ = env.config.box_size
        cx = (aabb_min[0] + aabb_max[0]) / 2.0
        cy = (aabb_min[1] + aabb_max[1]) / 2.0

        if not (bx - sx / 2 < cx < bx + sx / 2):
            raise AssertionError(f"Object x={cx} is outside the box")
        if not (by - sy / 2 < cy < by + sy / 2):
            raise AssertionError(f"Object y={cy} is outside the box")

        print("PASS: headless pick -> grasp -> place execution")
    finally:
        env.close()


if __name__ == "__main__":
    main()
