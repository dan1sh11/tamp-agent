import pybullet as p
import pybullet_data

from .config import SimulationConfig
from .objects import (
    ObjectRegistry,
    create_box,
    create_box_container,
    create_capsule,
    create_cylinder,
    create_sphere,
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

        if self.gui:
            p.configureDebugVisualizer(p.COV_ENABLE_SHADOWS, 1)
            p.configureDebugVisualizer(p.COV_ENABLE_GUI, 0)
            p.configureDebugVisualizer(rgbBackground=[0.06, 0.08, 0.11])

        self.registry = ObjectRegistry()
        self.container_ids = []
        self.robot = None
        self.table_id = None
        self._build_scene()

    def _build_scene(self):
        p.loadURDF("plane.urdf")
        self._create_table()
        self.container_ids = create_box_container(
            "box", self.config.box_center, self.config.box_size, self.config.table_top_z
        )
        self.robot = PandaRobot(self.config.panda_base)
        self._spawn_objects()
        self._add_scene_labels()
        if self.gui:
            p.resetDebugVisualizerCamera(
                cameraDistance=2.25,
                cameraYaw=48,
                cameraPitch=-35,
                cameraTargetPosition=[0.03, 0.05, 0.72],
            )

    def _create_table(self):
        sx, sy, sz = self.config.table_size
        half = [sx / 2, sy / 2, sz / 2]
        center_z = self.config.table_top_z - sz / 2
        collision = p.createCollisionShape(p.GEOM_BOX, halfExtents=half)
        visual = p.createVisualShape(
            p.GEOM_BOX, halfExtents=half, rgbaColor=(0.16, 0.19, 0.23, 1)
        )
        self.table_id = p.createMultiBody(
            baseMass=0,
            baseCollisionShapeIndex=collision,
            baseVisualShapeIndex=visual,
            basePosition=[0, 0, center_z],
        )

        leg_half = [0.055, 0.055, 0.34]
        for x in (-sx / 2 + 0.11, sx / 2 - 0.11):
            for y in (-sy / 2 + 0.11, sy / 2 - 0.11):
                leg_collision = p.createCollisionShape(p.GEOM_BOX, halfExtents=leg_half)
                leg_visual = p.createVisualShape(
                    p.GEOM_BOX, halfExtents=leg_half, rgbaColor=(0.08, 0.10, 0.12, 1)
                )
                p.createMultiBody(
                    baseMass=0,
                    baseCollisionShapeIndex=leg_collision,
                    baseVisualShapeIndex=leg_visual,
                    basePosition=[x, y, 0.34],
                )

        mat_visual = p.createVisualShape(
            p.GEOM_BOX,
            halfExtents=[sx * 0.44, sy * 0.42, 0.002],
            rgbaColor=(0.10, 0.13, 0.16, 1),
        )
        p.createMultiBody(
            baseMass=0,
            baseCollisionShapeIndex=-1,
            baseVisualShapeIndex=mat_visual,
            basePosition=[0, 0, self.config.table_top_z + 0.002],
        )

    def _spawn_objects(self):
        z = self.config.table_top_z + 0.045
        specs = [
            ("small_cube_red", "cube", (-0.18, -0.30), (0.85, 0.10, 0.10, 1)),
            ("large_cube_red", "cube", (0.05, -0.30), (0.95, 0.18, 0.12, 1)),
            ("cylinder_red", "cylinder", (0.28, -0.30), (0.85, 0.10, 0.10, 1)),
            ("cylinder_green", "cylinder", (-0.28, 0.05), (0.10, 0.75, 0.25, 1)),
            ("sphere", "sphere", (-0.05, 0.08), (0.95, 0.65, 0.10, 1)),
            ("capsule", "capsule", (0.20, 0.06), (0.55, 0.20, 0.90, 1)),
            ("small_cube_blue", "cube", (-0.38, 0.32), (0.10, 0.30, 0.95, 1)),
            ("cylinder_yellow", "cylinder", (-0.12, 0.33), (0.95, 0.75, 0.10, 1)),
            ("large_cube_blue", "cube", (0.40, -0.02), (0.10, 0.30, 0.95, 1)),
        ]
        for name, kind, (x, y), rgba in specs:
            if kind == "cube":
                obj = create_box(name, [x, y, z], [0.045, 0.045, 0.045], mass=0.15, rgba=rgba)
            elif kind == "cylinder":
                obj = create_cylinder(name, [x, y, z], radius=0.045, height=0.09, mass=0.15, rgba=rgba)
            elif kind == "sphere":
                obj = create_sphere(name, [x, y, z], radius=0.05, mass=0.12, rgba=rgba)
            elif kind == "capsule":
                obj = create_capsule(name, [x, y, z], radius=0.035, height=0.10, mass=0.12, rgba=rgba)
            else:
                raise ValueError(f"Unknown object kind: {kind}")
            self.registry.add(obj)
        for _ in range(240):
            p.stepSimulation()

    def _add_scene_labels(self):
        if not self.gui:
            return
        p.addUserDebugText(
            "TAMP WORKCELL", [0.0, -0.53, 0.82], textSize=1.2, textColorRGB=[0.85, 0.9, 1.0]
        )
        p.addUserDebugText(
            "PLACE TARGET",
            [self.config.box_center[0], self.config.box_center[1], 0.97],
            textSize=0.9,
            textColorRGB=[0.9, 0.9, 0.9],
        )

    def get_object_pose(self, name):
        obj = self.registry.get(name)
        return p.getBasePositionAndOrientation(obj.body_id)

    def get_object_position(self, name):
        return self.get_object_pose(name)[0]

    def contact_points(self, body_a, body_b=None):
        if body_b is None:
            return p.getContactPoints(bodyA=body_a)
        return p.getContactPoints(bodyA=body_a, bodyB=body_b)

    def get_target_position(self, name):
        if name == "box":
            return (
                self.config.box_center[0],
                self.config.box_center[1],
                self.config.table_top_z + self.config.box_size[2] * 0.65,
            )
        return self.get_object_position(name)

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
