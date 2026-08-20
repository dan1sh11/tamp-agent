"""NLI benchmark for the actual simulation scene on this branch.

Expected object values MUST be names registered by TAMPEnvironment._spawn_objects
in simulation/environment.py. The scene contains seven manipulable objects and
one receptacle named ``box``.
"""

CASES = [
    {"id": "pick_01", "input": "Pick up the large red cube.", "expected": {"action": "pick", "object": "large_cube_red", "target": None}},
    {"id": "pick_02", "input": "Grab the little blue cube.", "expected": {"action": "pick", "object": "small_cube_blue", "target": None}},
    {"id": "pick_03", "input": "Take the green cylinder.", "expected": {"action": "pick", "object": "cylinder_green", "target": None}},
    {"id": "pick_04", "input": "Get the yellow cylinder off the table.", "expected": {"action": "pick", "object": "cylinder_yellow", "target": None}},
    {"id": "pick_05", "input": "Grab the red cylinder.", "expected": {"action": "pick", "object": "cylinder_red", "target": None}},
    {"id": "pick_06", "input": "Take the small red cube.", "expected": {"action": "pick", "object": "small_cube_red", "target": None}},
    {"id": "pick_07", "input": "Take the large blue cube.", "expected": {"action": "pick", "object": "large_cube_blue", "target": None}},
    {"id": "desc_01", "input": "Grab the tiny red block.", "expected": {"action": "pick", "object": "small_cube_red", "target": None}},
    {"id": "desc_02", "input": "Take the big blue block.", "expected": {"action": "pick", "object": "large_cube_blue", "target": None}},
    {"id": "desc_03", "input": "Grab the little blue block.", "expected": {"action": "pick", "object": "small_cube_blue", "target": None}},
    {"id": "typo_01", "input": "Grab the greeen cylinder.", "expected": {"action": "pick", "object": "cylinder_green", "target": None}},
    {"id": "place_01", "input": "Put the red cylinder in the box.", "expected": {"action": "place", "object": "cylinder_red", "target": "box"}},
    {"id": "place_02", "input": "Drop the small blue cube into the box.", "expected": {"action": "place", "object": "small_cube_blue", "target": "box"}},
    {"id": "place_03", "input": "Set the big blue block inside the box.", "expected": {"action": "place", "object": "large_cube_blue", "target": "box"}},
    {"id": "place_04", "input": "Move the yellow cylinder into the box.", "expected": {"action": "place", "object": "cylinder_yellow", "target": "box"}},
    {"id": "place_05", "input": "Put the small red cube in the box.", "expected": {"action": "place", "object": "small_cube_red", "target": "box"}},
    {"id": "drop_01", "input": "Drop it.", "expected": {"action": "drop", "object": None, "target": None}},
    {"id": "drop_02", "input": "Release it.", "expected": {"action": "drop", "object": None, "target": None}},
    {"id": "compound_01", "input": "Pick up the green cylinder and put it in the box.", "expected": {"action": "move", "object": "cylinder_green", "target": "box"}},
    {"id": "compound_02", "input": "Grab the small red cube and place it in the box.", "expected": {"action": "move", "object": "small_cube_red", "target": "box"}},
    {"id": "ambiguous_01", "input": "Pick up the red cube.", "expected": {"action": "unknown", "object": None, "target": None}},
    {"id": "ambiguous_02", "input": "Put the blue cube in the box.", "expected": {"action": "unknown", "object": None, "target": None}},
    {"id": "ambiguous_03", "input": "Grab that one.", "expected": {"action": "unknown", "object": None, "target": None}},
    {"id": "context_01", "input": "Put it in the box.", "expected": {"action": "place", "object": None, "target": "box"}},
    {"id": "unsupported_01", "input": "Rotate the cube ninety degrees.", "expected": {"action": "unknown", "object": "cube", "target": None}},
    {"id": "unsupported_02", "input": "Push the small red cube toward the box.", "expected": {"action": "unknown", "object": "small_cube_red", "target": "box"}},
    {"id": "unsupported_03", "input": "Move the robot arm to the left side of the table.", "expected": {"action": "unknown", "object": None, "target": "left side of the table"}},
]
