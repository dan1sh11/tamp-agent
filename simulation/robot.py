import os
import pybullet as p
import pybullet_data


class PandaRobot:
    def __init__(self, base_position):
        self.body_id = p.loadURDF(
            os.path.join(pybullet_data.getDataPath(), "franka_panda", "panda.urdf"),
            base_position,
            useFixedBase=True,
        )

        self.arm_joints = list(range(7))
        self.finger_joints = [9, 10]
        self.ee_link = 11

        self.home_joint_positions = [0.0, -0.4, 0.0, -2.2, 0.0, 1.8, 0.8]
        self.set_joint_positions(self.home_joint_positions)

    def set_joint_positions(self, positions):
        if len(positions) != 7:
            raise ValueError("Expected 7 Panda arm joint positions")
        for joint, target in zip(self.arm_joints, positions):
            p.resetJointState(self.body_id, joint, target)
        for joint in self.finger_joints:
            p.resetJointState(self.body_id, joint, 0.04)

    def ee_pose(self):
        state = p.getLinkState(
            self.body_id,
            self.ee_link,
            computeForwardKinematics=True,
        )
        return state[4], state[5]

    def _ik_solution(self, target_position, target_orientation=None):
        # Do not constrain the solver with hand-maintained joint-limit/null-space
        # arrays. The Panda URDF already supplies the joint limits, and those
        # arrays were producing a systematic Cartesian error for reachable poses.
        # Position/orientation IK is sufficient here; the resulting seven arm
        # targets are then applied through POSITION_CONTROL.
        if target_orientation is None:
            solution = p.calculateInverseKinematics(
                self.body_id,
                self.ee_link,
                target_position,
                maxNumIterations=1000,
                residualThreshold=1e-6,
            )
        else:
            solution = p.calculateInverseKinematics(
                self.body_id,
                self.ee_link,
                target_position,
                targetOrientation=target_orientation,
                maxNumIterations=1000,
                residualThreshold=1e-6,
            )

        if len(solution) < 7:
            raise RuntimeError(
                f"PyBullet returned an invalid Panda IK solution with {len(solution)} joints"
            )
        return solution[:7]

    def move_ee(self, target_position, target_orientation=None, max_steps=1200, tolerance=0.015):
        joint_targets = self._ik_solution(target_position, target_orientation)

        for joint, target in zip(self.arm_joints, joint_targets):
            p.setJointMotorControl2(
                self.body_id,
                joint,
                p.POSITION_CONTROL,
                targetPosition=target,
                force=400,
                positionGain=0.5,
                velocityGain=1.0,
            )

        for _ in range(max_steps):
            p.stepSimulation()
            current_pos, _ = self.ee_pose()
            error = sum(
                (current_pos[i] - target_position[i]) ** 2
                for i in range(3)
            ) ** 0.5
            if error <= tolerance:
                return True

        return False

    def open_gripper(self):
        for joint in self.finger_joints:
            p.setJointMotorControl2(
                self.body_id,
                joint,
                p.POSITION_CONTROL,
                targetPosition=0.04,
                force=100,
            )

    def close_gripper(self):
        for joint in self.finger_joints:
            p.setJointMotorControl2(
                self.body_id,
                joint,
                p.POSITION_CONTROL,
                targetPosition=0.0,
                force=100,
            )

    def step(self, steps=1):
        for _ in range(steps):
            p.stepSimulation()
