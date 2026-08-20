from dataclasses import dataclass


@dataclass(frozen=True)
class SimulationConfig:
    table_size: tuple[float, float, float] = (1.6, 1.1, 0.12)
    table_top_z: float = 0.72

    # The Panda is mounted at the table surface. Keep the mounting position
    # independent of any particular object so every scene object uses the same
    # robot/world coordinate frame.
    panda_base_xy: tuple[float, float] = (-0.48, 0.0)

    box_center: tuple[float, float] = (0.48, 0.20)
    box_size: tuple[float, float, float] = (0.46, 0.38, 0.20)

    simulation_hz: int = 240
    gravity: float = -9.81
    seed: int = 7

    approach_height: float = 0.20
    grasp_height_offset: float = 0.055
    home_position: tuple[float, float, float] = (0.15, 0.0, 1.05)

    position_tolerance: float = 0.015
    max_motion_steps: int = 1200
    grasp_settle_steps: int = 30

    @property
    def panda_base(self) -> tuple[float, float, float]:
        return (*self.panda_base_xy, self.table_top_z)
