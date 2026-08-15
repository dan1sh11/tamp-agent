import pybullet as p

from .actions import Action, ActionType
from .environment import TAMPEnvironment


class PlanExecutionError(RuntimeError):
    pass


class PlanExecutor:
    # The only layer that translates normalized symbolic actions into
    # physical manipulation procedures.
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
                    f"Action {index} failed: {action}"
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

    def move_to(self, object_name: str):
        x, y, z = self.env.get_target_position(object_name)

        approach = [x, y, z + self.env.config.approach_height]
        target = [x, y, z + self.env.config.grasp_height_offset]

        self.env.robot.open_gripper()

        if not self.env.robot.move_ee(
            approach,
            self._grasp_orientation(),
            self.env.config.max_motion_steps,
            self.env.config.position_tolerance,
        ):
            raise PlanExecutionError(
                f"Robot could not reach approach pose for '{object_name}'"
            )

        if not self.env.robot.move_ee(
            target,
            self._grasp_orientation(),
            self.env.config.max_motion_steps,
            self.env.config.position_tolerance,
        ):
            raise PlanExecutionError(
                f"Robot could not reach grasp pose for '{object_name}'"
            )

    def grasp(self, object_name: str):
        if self.held_object is not None:
            raise PlanExecutionError(
                f"Robot already holds '{self.held_object}'"
            )

        obj = self.env.registry.get(object_name)

        self.env.robot.close_gripper()
        self.env.robot.step(self.env.config.grasp_settle_steps)

        # Prototype grasp model: attach the object to the end effector.
        # Later this can be replaced with contact/force-based grasp validation.
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
        self.env.robot.move_ee(
            self.env.config.home_position,
            self._grasp_orientation(),
            self.env.config.max_motion_steps,
            self.env.config.position_tolerance,
        )

    def wait(self, steps: int):
        self.env.robot.step(max(0, int(steps)))
