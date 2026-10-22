"""Replay the explicitly authored release cohort; no native verdict interpretation."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

from witness_register import (
    RelationRecord,
    RelationType,
    ReturnContractRecord,
    canonical_json,
    canonical_projection,
    canonical_state_payload,
    genesis_state,
    intake_envelope,
    project,
    update_state,
    verify_chain,
)


def build_cohort(directory: Path) -> dict:
    """Bind exported bytes to one declared cohort, without claiming a shared subject."""
    manifest = json.loads((directory / "manifest.json").read_text())
    envelopes = []
    for entry in manifest["siblings"]:
        raw = (directory / entry["file"]).read_bytes()
        if sha256(raw).hexdigest() != entry["sha256"]:
            raise ValueError(f"export bytes changed: {entry['file']}")
        envelope, issues = intake_envelope(json.loads(raw))
        if envelope is None:
            raise ValueError(f"refused export {entry['file']}: {issues}")
        if envelope.line_id != entry["repository"].split("/")[1]:
            raise ValueError("export line does not match its provenance")
        envelopes.append(envelope)
    first = genesis_state(
        manifest["cohort_id"], manifest["reviewed_on"], envelopes=tuple(envelopes)
    )
    refs = tuple(e.report_ref for e in envelopes)
    contract = ReturnContractRecord(
        contract_id="released-cohort-subject-correspondence",
        subject_id=first.subject_id,
        why_held="Released worked examples retain their different native subjects.",
        alternatives_live=("inspect this release cohort as a transport demonstration",),
        change_condition="a registrar declares and evidences a shared subject correspondence",
        standing="the registrar responsible for a proposed shared subject",
        protected="private material outside the published envelopes remains outside this cohort",
        trigger="a proposed use as a shared-subject record",
        acceptance_condition="new envelopes and an explicit correspondence declaration, without erasing these worked subjects",
        prior_state_ref=first.state_digest,
    )
    relations = (
        RelationRecord(
            "released-worked-incomparability",
            first.subject_id,
            refs,
            RelationType.CANNOT_COMPARE,
            "The imported worked subjects are distinct; no cross-instrument comparison is admitted.",
            classification_decision_ref="registrar:release-cohort-20261021",
        ),
        RelationRecord(
            "released-worked-return-due",
            first.subject_id,
            refs,
            RelationType.RETURN_DUE,
            "Using the cohort as one subject record requires explicit correspondence first.",
            return_contract_ref=contract.contract_id,
            classification_decision_ref="registrar:release-cohort-20261021",
        ),
    )
    second = update_state(
        first, manifest["reviewed_on"], relations=relations, returns=(contract,)
    )
    errors = verify_chain((first, second))
    if errors:
        raise ValueError(errors)
    states = []
    for state in (first, second):
        payload = canonical_state_payload(
            state.subject_id,
            state.review_moment,
            state.envelopes,
            state.relations,
            state.unclassified,
            state.returns,
            state.prior_ref,
            state.decisions,
            state.history_refs,
        )
        states.append({"state_digest": state.state_digest, "payload": payload})
    projection = project(second, manifest["declared_next_use"])
    return {"states": states, "projection": canonical_projection(projection)}


def main() -> None:
    """Write deterministic replay evidence from the committed release manifest."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "directory",
        type=Path,
        nargs="?",
        default=Path(__file__).resolve().parents[1] / "data/envelopes/releases/v0.2.0",
    )
    args = parser.parse_args()
    payload = build_cohort(args.directory)
    (args.directory / "co_registration.json").write_text(canonical_json(payload) + "\n")


if __name__ == "__main__":
    main()
