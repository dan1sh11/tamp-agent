import pybullet as p
import pybullet_data

from .config import SimulationConfig
from .objects import (
    ObjectRegistry,
    create_box,
    create_cylinder,
    create_sphere,
    create_capsule,
    create_banana_like,
    create_box_container,
)
from .robot import PandaRobot


class TAMPEnvironment:
    def __init__(self, config: SimulationConfig | None = None, gui=True):
        self.config = config or SimulationConfig()
        self.gui = gui
        self.client_id = p.connect(p.GUI if gui else p.DIRECT)

        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, 0, self.config.gravity)
        p.setTimeStep(1.0 / self.config.simulation_hz)
        p.setPhysicsEngineParameter(numSolverIterations=150)

        self.registry = ObjectRegistry()
        self.container_ids = []
        self.robot = None
        self.table_id = None

        self._build_scene()

    def _build_scene(self):
        p.loadURDF("plane.urdf")

        self._create_table()

        self.container_ids = create_box_container(
            "box",
            self.config.box_center,
            self.config.box_size,
            self.config.table_top_z,
        )

        self.robot = PandaRobot(self.config.panda_base)
        self._spawn_objects()

        if self.gui:
            p.resetDebugVisualizerCamera(
                cameraDistance=2.4,
                cameraYaw=48,
                cameraPitch=-38,
                cameraTargetPosition=[0.0, 0.0, 0.7],
            )

    def _create_table(self):
        sx, sy, sz = self.config.table_size
        half = [sx / 2, sy / 2, sz / 2]

        collision = p.createCollisionShape(p.GEOM_BOX, halfExtents=half)
        visual = p.createVisualShape(
            p.GEOM_BOX,
            halfExtents=half,
            rgbaColor=(0.45, 0.45, 0.45, 1),
        )

        center_z = self.config.table_top_z - sz / 2

        self.table_id = p.createMultiBody(
            baseMass=0,
            baseCollisionShapeIndex=collision,
            baseVisualShapeIndex=visual,
            basePosition=[0, 0, center_z],
        )

    def _spawn_objects(self):
        # Ten stable symbolic names used by the planner.
        z = self.config.table_top_z + 0.04

        specs = [
            ("small_cube_red", "cube", (-0.18, -0.30)),
            ("cube_blue", "cube", (0.05, -0.30)),
            ("cylinder_green", "cylinder", (0.28, -0.30)),
            ("cylinder_yellow", "cylinder", (-0.28, 0.05)),
            ("sphere", "sphere", (-0.05, 0.08)),
            ("capsule", "capsule", (0.20, 0.06)),
            ("small_cube", "cube", (-0.38, 0.32)),
            ("small_cylinder", "cylinder", (-0.12, 0.33)),
            ("large_cube", "cube", (0.40, -0.02)),
        ]

        for name, kind, (x, y) in specs:
            if kind == "cube":
                obj = create_box(
                    name, [x, y, z],
                    [0.045, 0.045, 0.045],
                    mass=0.15,
                )
            elif kind == "cylinder":
                obj = create_cylinder(
                    name, [x, y, z],
                    radius=0.045,
                    height=0.09,
                    mass=0.15,
                )
            elif kind == "sphere":
                obj = create_sphere(
                    name, [x, y, z],
                    radius=0.05,
                    mass=0.12,
                )
            elif kind == "capsule":
                obj = create_capsule(
                    name, [x, y, z],
                    radius=0.035,
                    height=0.10,
                    mass=0.12,
                )
            elif kind == "banana":
                obj = create_banana_like(
                    name, [x, y, z],
                    mass=0.08,
                )
            else:
                raise ValueError(f"Unknown object kind: {kind}")

            self.registry.add(obj)

        # Allow initial dynamics to settle.
        for _ in range(240):
            p.stepSimulation()

    def get_object_pose(self, name):
        obj = self.registry.get(name)
        return p.getBasePositionAndOrientation(obj.body_id)

    def get_object_position(self, name):
        return self.get_object_pose(name)[0]

    def contact_points(self, body_a, body_b=None):
        if body_b is None:
            return p.getContactPoints(bodyA=body_a)
        return p.getContactPoints(bodyA=body_a, bodyB=body_b)

    def close(self):
        if p.isConnected(self.client_id):
            p.disconnect(self.client_id)

    def run_forever(self):
        if not self.gui:
            raise RuntimeError("run_forever requires GUI mode")

        import time

        while p.isConnected(self.client_id):
            p.stepSimulation()
            time.sleep(1.0 / self.config.simulation_hz)
