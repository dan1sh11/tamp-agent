from dataclasses import dataclass


@dataclass(frozen=True)
class SimulationConfig:
    table_size: tuple[float, float, float] = (1.6, 1.1, 0.12)
    table_top_z: float = 0.72
    panda_base_xy: tuple[float, float] = (-0.65, 0.0)

    # The receptacle is centered on the table and on the Panda's approach axis.
    box_center: tuple[float, float] = (0.0, 0.0)
    box_size: tuple[float, float, float] = (0.34, 0.28, 0.20)

    simulation_hz: int = 240
    gravity: float = -9.81
    seed: int = 7

    approach_height: float = 0.20
    grasp_height_offset: float = 0.055
    grasp_tolerance: float = 0.050
    release_clearance: float = 0.012
    release_settle_steps: int = 45
    home_position: tuple[float, float, float] = (0.05, 0.0, 1.05)

    position_tolerance: float = 0.015
    max_motion_steps: int = 1200
    grasp_settle_steps: int = 30

    @property
    def panda_base(self) -> tuple[float, float, float]:
        return (*self.panda_base_xy, self.table_top_z)
