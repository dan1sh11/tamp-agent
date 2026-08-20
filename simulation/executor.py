import pybullet as p

from .actions import Action, ActionType
from .environment import TAMPEnvironment


class PlanExecutionError(RuntimeError):
    pass


class PlanExecutor:
    """Translate normalized symbolic planner actions into robot procedures."""

    def __init__(self, env: TAMPEnvironment):
        self.env = env
        self.held_object: str | None = None
        self.grasp_constraint: int | None = None

    def execute(self, actions: list[Action]) -> None:
        for index, action in enumerate(actions):
            try:
                self.execute_one(action)
            except Exception as exc:
                raise PlanExecutionError(
                    f"Action {index} failed: {action} ({exc})"
                ) from exc

    def execute_one(self, action: Action) -> None:
        if action.type == ActionType.MOVE_TO:
            self.move_to(action.parameters["object"])
        elif action.type == ActionType.GRASP:
            self.grasp(action.parameters["object"])
        elif action.type == ActionType.RELEASE:
            self.release()
        elif action.type == ActionType.WAIT:
            self.wait(action.parameters.get("steps", 60))
        elif action.type == ActionType.HOME:
            self.home()
        else:
            raise ValueError(f"Unsupported action: {action.type}")

    def _grasp_orientation(self):
        return p.getQuaternionFromEuler([0.0, 3.14159265, 0.0])

    def _move_checked(self, position, label: str):
        if not self.env.robot.move_ee(
            position,
            self._grasp_orientation(),
            self.env.config.max_motion_steps,
            self.env.config.position_tolerance,
        ):
            raise PlanExecutionError(f"Robot could not reach {label} at {position}")

    def move_to(self, object_name: str):
        # Resolve the symbolic name through the simulator registry so that the
        # planner/simulator scene contract fails explicitly if names diverge.
        if object_name != "box":
            self.env.registry.get(object_name)

        x, y, z = self.env.get_target_position(object_name)
        approach_z = z + self.env.config.approach_height
        target_z = z + self.env.config.grasp_height_offset

        if self.held_object is None:
            self.env.robot.open_gripper()

        # Do not drive the arm directly from its current joint configuration to
        # a tabletop target. A joint-space IK transition can sweep through the
        # table even when the final pose is valid. Move above the workspace,
        # translate in XY, then descend vertically.
        safe_z = max(approach_z, self.env.config.home_position[2])
        self._move_checked([x, y, safe_z], f"safe transit pose for '{object_name}'")
        self._move_checked([x, y, approach_z], f"approach pose for '{object_name}'")
        self._move_checked([x, y, target_z], f"grasp pose for '{object_name}'")

    def grasp(self, object_name: str):
        if self.held_object is not None:
            raise PlanExecutionError(f"Robot already holds '{self.held_object}'")

        obj = self.env.registry.get(object_name)
        self.env.robot.close_gripper()
        self.env.robot.step(self.env.config.grasp_settle_steps)

        self.grasp_constraint = p.createConstraint(
            self.env.robot.body_id,
            self.env.robot.ee_link,
            obj.body_id,
            -1,
            p.JOINT_FIXED,
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        )
        self.held_object = object_name

    def release(self):
        if self.held_object is None:
            return

        if self.grasp_constraint is not None:
            p.removeConstraint(self.grasp_constraint)

        self.grasp_constraint = None
        self.env.robot.open_gripper()
        self.env.robot.step(45)
        self.held_object = None

    def home(self):
        self._move_checked(self.env.config.home_position, "home pose")

    def wait(self, steps: int):
        self.env.robot.step(max(0, int(steps)))
