"""The 3x3 witness battery: green on the real register, rejecting when wronged."""

from __future__ import annotations

import pytest

from witness_register import CASE_IDS, BatteryError, run_battery


def test_the_battery_is_green_on_the_real_register() -> None:
    results = run_battery()
    assert {item.case_id for item in results} == set(CASE_IDS)
    assert all(item.passed for item in results)
    # Every case contributes at least two named checks.
    for case_id in CASE_IDS:
        assert sum(1 for item in results if item.case_id == case_id) >= 2


def test_the_case_grid_is_the_reviews_three_by_three() -> None:
    assert CASE_IDS == ("S1", "S2", "S3", "R4", "R5", "R6", "T7", "T8", "T9")
    assert len(CASE_IDS) == 9


@pytest.mark.parametrize("case_id", CASE_IDS)
def test_every_injected_wrong_variant_is_rejected(case_id: str) -> None:
    """A guard that has never rejected is not protection."""

    with pytest.raises(BatteryError, match=case_id):
        run_battery(defeat=case_id)


def test_an_unknown_defeat_name_is_refused_not_run_clean() -> None:
    with pytest.raises(ValueError, match="unknown battery case"):
        run_battery(defeat="S0")


def test_battery_results_carry_actionable_detail() -> None:
    for item in run_battery():
        assert item.check
        assert item.detail
