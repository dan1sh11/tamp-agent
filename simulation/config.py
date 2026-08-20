from dataclasses import dataclass


@dataclass(frozen=True)
class SimulationConfig:
    table_size: tuple[float, float, float] = (1.6, 1.1, 0.12)
    table_top_z: float = 0.72

    # Panda base is fixed to the tabletop.
    panda_base: tuple[float, float, float] = (-0.48, 0.0, 0.80)

    box_center: tuple[float, float] = (0.48, 0.20)
    box_size: tuple[float, float, float] = (0.46, 0.38, 0.20)

    simulation_hz: int = 240
    gravity: float = -9.81
    seed: int = 7

    # Objects are spawned with their center 0.045 m above the tabletop.
    # A 0.045 m cylinder radius/height combination therefore puts the
    # cylinder bottom at the table surface.  The end effector should approach
    # above the object and descend only to the object's center/top grasp zone,
    # not below the tabletop.
    approach_height: float = 0.20
    grasp_height_offset: float = 0.055
    home_position: tuple[float, float, float] = (0.15, 0.0, 1.05)

    position_tolerance: float = 0.015
    max_motion_steps: int = 1200
    grasp_settle_steps: int = 30
