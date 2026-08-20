from dataclasses import dataclass


@dataclass(frozen=True)
class SimulationConfig:
    table_size: tuple[float, float, float] = (1.6, 1.1, 0.12)
    table_top_z: float = 0.72

    # Fixed robot mounting point for the workcell. Object placement remains
    # independent of the robot and is defined in environment.py.
    panda_base_xy: tuple[float, float] = (-0.65, 0.0)

    # Keep the receptacle near the center of the reachable workspace rather
    # than at the far-right edge of the table.
    box_center: tuple[float, float] = (0.25, 0.18)
    box_size: tuple[float, float, float] = (0.36, 0.30, 0.20)

    simulation_hz: int = 240
    gravity: float = -9.81
    seed: int = 7

    approach_height: float = 0.20
    grasp_height_offset: float = 0.055
    home_position: tuple[float, float, float] = (0.10, 0.0, 1.05)

    position_tolerance: float = 0.015
    max_motion_steps: int = 1200
    grasp_settle_steps: int = 30

    @property
    def panda_base(self) -> tuple[float, float, float]:
        return (*self.panda_base_xy, self.table_top_z)
