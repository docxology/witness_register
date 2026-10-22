"""Execute operator examples and bind their structural and authority guidance."""

from dataclasses import fields
from pathlib import Path
import re

from witness_register import WitnessState, canonical_json

SKILL = Path(__file__).resolve().parents[1] / ".agents/skills/witness-register/SKILL.md"


def test_operator_python_examples_execute_without_fallbacks():
    examples = re.findall(r"```python\n(.*?)```", SKILL.read_text(), re.DOTALL)
    assert examples
    namespace = {"__name__": "operator_skill_acceptance"}
    for example in examples:
        exec(compile(example, str(SKILL), "exec"), namespace)


def test_operator_guidance_matches_state_and_authority_contract():
    text = SKILL.read_text()
    for field in fields(WitnessState):
        assert f"`{field.name}`" in text
    for term in (
        "classification_decision_ref",
        "DecisionEvent",
        "STATE",
        "RELATION",
        "RETURN",
    ):
        assert term in text
    assert "sorted keys" in text
    assert "real clone" in text
    assert "stage_04_validate.py" in text
    assert canonical_json({"a": 1, "b": 2}) == canonical_json({"b": 2, "a": 1})
