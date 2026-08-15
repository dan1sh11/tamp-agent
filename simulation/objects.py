from dataclasses import dataclass
from typing import Optional
import math
import pybullet as p


@dataclass
class SimObject:
    name: str
    body_id: int
    kind: str
    mass: float
    graspable: bool = True
    held_constraint: Optional[int] = None


class ObjectRegistry:
    def __init__(self):
        self._objects: dict[str, SimObject] = {}

    def add(self, obj: SimObject) -> None:
        if obj.name in self._objects:
            raise ValueError(f"Duplicate simulator object name: {obj.name}")
        self._objects[obj.name] = obj

    def get(self, name: str) -> SimObject:
        try:
            return self._objects[name]
        except KeyError:
            raise KeyError(
                f"Unknown simulator object '{name}'. "
                f"Known objects: {sorted(self._objects)}"
            )

    def names(self) -> list[str]:
        return sorted(self._objects)

    def values(self):
        return self._objects.values()


def create_box(name, pos, half_extents, mass=0.15, rgba=(0.7, 0.2, 0.2, 1)):
    collision = p.createCollisionShape(p.GEOM_BOX, halfExtents=half_extents)
    visual = p.createVisualShape(
        p.GEOM_BOX, halfExtents=half_extents, rgbaColor=rgba
    )
    body = p.createMultiBody(
        baseMass=mass,
        baseCollisionShapeIndex=collision,
        baseVisualShapeIndex=visual,
        basePosition=pos,
    )
    return SimObject(name, body, "cube", mass)


def create_cylinder(name, pos, radius, height, mass=0.15, rgba=(0.2, 0.5, 0.8, 1)):
    collision = p.createCollisionShape(
        p.GEOM_CYLINDER, radius=radius, height=height
    )
    visual = p.createVisualShape(
        p.GEOM_CYLINDER, radius=radius, length=height, rgbaColor=rgba
    )
    body = p.createMultiBody(
        baseMass=mass,
        baseCollisionShapeIndex=collision,
        baseVisualShapeIndex=visual,
        basePosition=pos,
    )
    return SimObject(name, body, "cylinder", mass)


def create_sphere(name, pos, radius, mass=0.12, rgba=(0.8, 0.7, 0.1, 1)):
    collision = p.createCollisionShape(p.GEOM_SPHERE, radius=radius)
    visual = p.createVisualShape(
        p.GEOM_SPHERE, radius=radius, rgbaColor=rgba
    )
    body = p.createMultiBody(
        baseMass=mass,
        baseCollisionShapeIndex=collision,
        baseVisualShapeIndex=visual,
        basePosition=pos,
    )
    return SimObject(name, body, "sphere", mass)


def create_capsule(name, pos, radius, height, mass=0.12, rgba=(0.95, 0.75, 0.15, 1)):
    collision = p.createCollisionShape(
        p.GEOM_CAPSULE, radius=radius, height=height
    )
    visual = p.createVisualShape(
        p.GEOM_CAPSULE, radius=radius, length=height, rgbaColor=rgba
    )
    body = p.createMultiBody(
        baseMass=mass,
        baseCollisionShapeIndex=collision,
        baseVisualShapeIndex=visual,
        basePosition=pos,
    )
    return SimObject(name, body, "capsule", mass)



def create_box_container(name, center_xy, size, table_top_z):
    # Open-top box constructed from five static panels.
    sx, sy, sz = size
    cx, cy = center_xy
    wall = 0.025
    bottom_z = table_top_z + 0.01 + sz * 0.5

    panels = [
        ([sx / 2, sy / 2, wall / 2], [cx, cy, table_top_z + 0.01]),
        ([wall / 2, sy / 2, sz / 2], [cx - sx / 2, cy, bottom_z]),
        ([wall / 2, sy / 2, sz / 2], [cx + sx / 2, cy, bottom_z]),
        ([sx / 2, wall / 2, sz / 2], [cx, cy - sy / 2, bottom_z]),
        ([sx / 2, wall / 2, sz / 2], [cx, cy + sy / 2, bottom_z]),
    ]

    ids = []
    for half, pos in panels:
        cid = p.createCollisionShape(p.GEOM_BOX, halfExtents=half)
        vid = p.createVisualShape(
            p.GEOM_BOX, halfExtents=half, rgbaColor=(0.35, 0.35, 0.35, 0.35)
        )
        ids.append(
            p.createMultiBody(
                baseMass=0,
                baseCollisionShapeIndex=cid,
                baseVisualShapeIndex=vid,
                basePosition=pos,
            )
        )
    return ids
