"""NLI benchmark cases for the fix/simulation-ik-execution scene.

Expected object values MUST be names registered by TAMPEnvironment._spawn_objects
in simulation/environment.py. The scene contains seven manipulable objects and
one receptacle named ``box``.
"""

CASES = [
    # Canonical picks: every scene object is represented at least once.
    {"id": "pick_large_red", "input": "Pick up the large red cube.", "expected": {"action": "pick", "object": "large_cube_red", "target": None}},
    {"id": "pick_large_blue", "input": "Grab the big blue block.", "expected": {"action": "pick", "object": "large_cube_blue", "target": None}},
    {"id": "pick_small_red", "input": "Take the tiny red block.", "expected": {"action": "pick", "object": "small_cube_red", "target": None}},
    {"id": "pick_small_blue", "input": "Grab the little blue cube.", "expected": {"action": "pick", "object": "small_cube_blue", "target": None}},
    {"id": "pick_green", "input": "Take the green cylinder.", "expected": {"action": "pick", "object": "cylinder_green", "target": None}},
    {"id": "pick_yellow", "input": "Get the yellow cylinder off the table.", "expected": {"action": "pick", "object": "cylinder_yellow", "target": None}},
    {"id": "pick_red_cylinder", "input": "Grab the red cylinder.", "expected": {"action": "pick", "object": "cylinder_red", "target": None}},
    {"id": "pick_sphere", "input": "Lift the sphere.", "expected": {"action": "pick", "object": "sphere", "target": None}},
    {"id": "pick_capsule", "input": "Get the capsule.", "expected": {"action": "pick", "object": "capsule", "target": None}},

    # Lexical variation and typo tolerance.
    {"id": "alias_little", "input": "Grab the little blue cube.", "expected": {"action": "pick", "object": "small_cube_blue", "target": None}},
    {"id": "alias_big", "input": "Take the big blue block.", "expected": {"action": "pick", "object": "large_cube_blue", "target": None}},
    {"id": "alias_tiny", "input": "Pick up the tiny red cube.", "expected": {"action": "pick", "object": "small_cube_red", "target": None}},
    {"id": "typo_green", "input": "Grab the greeen cylinder.", "expected": {"action": "pick", "object": "cylinder_green", "target": None}},

    # Direct placement. All targets normalize to the one real box.
    {"id": "place_box", "input": "Put the red cylinder in the box.", "expected": {"action": "place", "object": "cylinder_red", "target": "box"}},
    {"id": "place_container", "input": "Drop the sphere into the container.", "expected": {"action": "place", "object": "sphere", "target": "box"}},
    {"id": "place_bin", "input": "Set the big blue block inside the bin.", "expected": {"action": "place", "object": "large_cube_blue", "target": "box"}},
    {"id": "place_move_verb", "input": "Move the capsule into the box.", "expected": {"action": "place", "object": "capsule", "target": "box"}},
    {"id": "place_set", "input": "Set the small red cube in the receptacle.", "expected": {"action": "place", "object": "small_cube_red", "target": "box"}},

    # Untargeted release.
    {"id": "drop_contextual", "input": "Drop it.", "expected": {"action": "drop", "object": None, "target": None}},
    {"id": "drop_release", "input": "Release it.", "expected": {"action": "drop", "object": None, "target": None}},

    # Compound transfer is represented as move.
    {"id": "compound_pick_place", "input": "Pick up the green cylinder and put it in the box.", "expected": {"action": "move", "object": "cylinder_green", "target": "box"}},
    {"id": "compound_grab_place", "input": "Grab the sphere, then place it in the box.", "expected": {"action": "move", "object": "sphere", "target": "box"}},
    {"id": "transfer_take_to", "input": "Take the sphere to the container.", "expected": {"action": "move", "object": "sphere", "target": "box"}},

    # Ambiguity must not be resolved by guessing.
    {"id": "ambiguous_red_cube", "input": "Pick up the red cube.", "expected": {"action": "unknown", "object": None, "target": None}},
    {"id": "ambiguous_blue_cube", "input": "Put the blue cube in the box.", "expected": {"action": "unknown", "object": None, "target": None}},
    {"id": "ambiguous_pronoun", "input": "Grab that one.", "expected": {"action": "unknown", "object": None, "target": None}},
    {"id": "contextual_object", "input": "Put it in the box.", "expected": {"action": "place", "object": None, "target": "box"}},

    # Unsupported requests must not be converted into executable actions.
    {"id": "unsupported_rotate", "input": "Rotate the cube ninety degrees.", "expected": {"action": "unknown", "object": "cube", "target": None}},
    {"id": "unsupported_robot_move", "input": "Move the robot arm to the left side of the table.", "expected": {"action": "unknown", "object": None, "target": "left side of the table"}},
    {"id": "unsupported_push", "input": "Push the sphere toward the box.", "expected": {"action": "unknown", "object": "sphere", "target": "box"}},
]
