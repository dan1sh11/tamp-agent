import os
import pybullet as p
import pybullet_data


class PandaRobot:
    def __init__(self, base_position):
        self.body_id = p.loadURDF(
            os.path.join(
                pybullet_data.getDataPath(),
                "franka_panda",
                "panda.urdf",
            ),
            base_position,
            useFixedBase=True,
        )

        self.arm_joints = list(range(7))
        self.finger_joints = [9, 10]
        self.ee_link = 11

        self.home_joint_positions = [
            0.0, -0.4, 0.0, -2.2, 0.0, 1.8, 0.8
        ]

        # The Panda URDF has 9 movable degrees of freedom: 7 arm joints and
        # 2 finger joints. PyBullet's IK damping/limit arrays must match that
        # DOF count, not just the seven arm joints that we control directly.
        self.ik_lower_limits = [
            -2.8973, -1.7628, -2.8973, -3.0718,
            -2.8973, -0.0175, -2.8973,
            0.0, 0.0,
        ]
        self.ik_upper_limits = [
            2.8973, 1.7628, 2.8973, -0.0698,
            2.8973, 3.7525, 2.8973,
            0.04, 0.04,
        ]
        self.ik_joint_ranges = [
            upper - lower
            for lower, upper in zip(self.ik_lower_limits, self.ik_upper_limits)
        ]
        self.ik_rest_poses = self.home_joint_positions + [0.04, 0.04]
        self.ik_joint_damping = [0.1] * 9

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

    def move_ee(
        self,
        target_position,
        target_orientation=None,
        max_steps=1200,
        tolerance=0.015,
    ):
        if target_orientation is None:
            target_orientation = p.getQuaternionFromEuler([0.0, 3.14159, 0.0])

        for _ in range(max_steps):
            joint_targets = p.calculateInverseKinematics(
                self.body_id,
                self.ee_link,
                target_position,
                targetOrientation=target_orientation,
                lowerLimits=self.ik_lower_limits,
                upperLimits=self.ik_upper_limits,
                jointRanges=self.ik_joint_ranges,
                restPoses=self.ik_rest_poses,
                jointDamping=self.ik_joint_damping,
                maxNumIterations=200,
                residualThreshold=1e-5,
            )

            for joint, target in zip(self.arm_joints, joint_targets[:7]):
                p.setJointMotorControl2(
                    self.body_id,
                    joint,
                    p.POSITION_CONTROL,
                    targetPosition=target,
                    force=250,
                    positionGain=0.25,
                    velocityGain=1.0,
                )

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
