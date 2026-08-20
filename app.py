from pathlib import Path
import re

from flask import Flask, jsonify, render_template, request

from nli.schema import Instruction
from planning.pddl_generator import PDDLGenerator
from planning.planner import PlannerError, FastDownwardPlanner
from simulation.fast_downward_adapter import parse_fast_downward_plan

app = Flask(__name__)
ROOT = Path(__file__).resolve().parent
DOMAIN = ROOT / "planning" / "domain.pddl"
PLANNER = ROOT / "planning" / "fast-downward.py"
WORKSPACE = ROOT / "planning" / "generated"

OBJECT_ALIASES = {
    "red cube": "large_cube_red", "large red cube": "large_cube_red",
    "blue cube": "large_cube_blue", "large blue cube": "large_cube_blue",
    "small red cube": "small_cube_red", "small blue cube": "small_cube_blue",
    "green cylinder": "cylinder_green", "yellow cylinder": "cylinder_yellow",
    "red cylinder": "cylinder_red", "sphere": "sphere", "capsule": "capsule",
}


def fallback_parse(text: str) -> Instruction:
    s = text.lower().strip()
    action = "pick" if re.search(r"\b(pick|grab|grasp|take)\b", s) else None
    if action is None and re.search(r"\b(place|put|drop)\b", s):
        action = "place"
    obj = next((name for alias, name in sorted(OBJECT_ALIASES.items(), key=lambda x: -len(x[0])) if alias in s), None)
    target = "box" if action == "place" and re.search(r"\b(box|container)\b", s) else None
    if action is None:
        return Instruction(action="unknown", object=obj, target=target, error="Could not determine a supported pick/place action.")
    if obj is None:
        return Instruction(action="unknown", object=None, target=target, error="Could not identify a supported scene object.")
    if action == "place" and target is None:
        return Instruction(action="unknown", object=obj, target=None, error="Place requires the target box.")
    return Instruction(action=action, object=obj, target=target, error=None)


def parse_user_instruction(text: str) -> Instruction:
    try:
        from nli.llm import parse_instruction
        return parse_instruction(text)
    except Exception:
        return fallback_parse(text)


def fallback_plan(instruction: Instruction) -> str:
    if instruction.action == "pick":
        return f"(pick {instruction.object})\n"
    if instruction.action == "place":
        return f"(pick {instruction.object})\n(place {instruction.object} {instruction.target})\n"
    raise PlannerError(instruction.error or "Unsupported action")


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/health")
def health():
    return jsonify({"status": "ok", "fast_downward_available": PLANNER.exists()})


@app.post("/api/plan")
def plan():
    payload = request.get_json(silent=True) or {}
    text = payload.get("instruction")
    if not isinstance(text, str) or not text.strip():
        return jsonify({"error": "JSON field 'instruction' is required."}), 400

    instruction = parse_user_instruction(text)
    if instruction.action == "unknown":
        return jsonify({"instruction": instruction.model_dump(), "error": instruction.error}), 400

    try:
        problem = PDDLGenerator(DOMAIN).generate_problem(instruction)
        plan_text = FastDownwardPlanner(PLANNER, DOMAIN, WORKSPACE).plan(instruction) if PLANNER.exists() else fallback_plan(instruction)
        actions = parse_fast_downward_plan(plan_text)
        return jsonify({
            "instruction": instruction.model_dump(),
            "problem": problem,
            "plan": plan_text,
            "actions": [{"type": a.type.value, "parameters": a.parameters} for a in actions],
            "execution": "Plan validated. Run main.py locally for PyBullet execution."
        })
    except Exception as exc:
        return jsonify({"error": str(exc), "instruction": instruction.model_dump()}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
