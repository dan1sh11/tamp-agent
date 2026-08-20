"""NLI benchmark cases for Mistral 7B.

Expected values are the FINAL NLI contract after deterministic grounding. They
therefore use the stable symbolic names from simulation/scene_contract.json.
The benchmark contains only objects and the single receptacle that actually
exist in the simulator.
"""

CASES = [
    {"id": "pick_01", "input": "Pick up the large red cube.", "expected": {"action": "pick", "object": "large red cube", "target": None}},
    {"id": "pick_02", "input": "Grab the little blue cube.", "expected": {"action": "pick", "object": "small blue cube", "target": None}},
    {"id": "pick_03", "input": "Take the green cylinder.", "expected": {"action": "pick", "object": "green cylinder", "target": None}},
    {"id": "pick_04", "input": "Get the yellow cylinder off the table.", "expected": {"action": "pick", "object": "yellow cylinder", "target": None}},
    {"id": "place_01", "input": "Put the red cylinder in the box.", "expected": {"action": "place", "object": "red cylinder", "target": "box"}},
    {"id": "place_02", "input": "Drop the sphere into the container.", "expected": {"action": "place", "object": "sphere", "target": "container"}},
    {"id": "place_03", "input": "Set the big blue block inside the bin.", "expected": {"action": "place", "object": "large blue cube", "target": "bin"}},
    {"id": "place_04", "input": "Move the capsule into the box.", "expected": {"action": "place", "object": "capsule", "target": "box"}},
    {"id": "typo_01", "input": "Grab the greeen cylinder.", "expected": {"action": "pick", "object": "green cylinder", "target": None}},
    {"id": "desc_01", "input": "Take the tiny red block.", "expected": {"action": "pick", "object": "small red cube", "target": None}},
    {"id": "desc_02", "input": "Put the large blue block in the box.", "expected": {"action": "place", "object": "large blue cube", "target": "box"}},
    {"id": "ambiguous_01", "input": "Pick up the red cube.", "expected": {"action": "unknown", "object": None, "target": None}},
    {"id": "ambiguous_02", "input": "Put the blue cube in the box.", "expected": {"action": "unknown", "object": None, "target": None}},
    {"id": "ambiguous_03", "input": "Grab that one.", "expected": {"action": "unknown", "object": None, "target": None}},
    {"id": "ambiguous_04", "input": "Put it in the box.", "expected": {"action": "place", "object": None, "target": "box"}},
    {"id": "compound_01", "input": "Pick up the green cylinder and put it in the box.", "expected": {"action": "move", "object": "green cylinder", "target": "box"}},
    {"id": "compound_02", "input": "Take the sphere to the container.", "expected": {"action": "move", "object": "sphere", "target": "container"}},
    {"id": "drop_01", "input": "Drop it.", "expected": {"action": "drop", "object": None, "target": None}},
    {"id": "unsupported_01", "input": "Rotate the cube ninety degrees.", "expected": {"action": "unknown", "object": "cube", "target": None}},
    {"id": "unsupported_02", "input": "Move the robot arm to the left side of the table.", "expected": {"action": "unknown", "object": None, "target": "left side of the table"}},
]
