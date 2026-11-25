#!/usr/bin/env python3
"""Bind one selected bootstrap stage to the retained completed-call contract."""
from fractions import Fraction
import hashlib
import io
import json
from pathlib import Path
import tarfile

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def main():
    pins = json.loads((PACKAGE / "SOURCES.json").read_text())
    by_path = {row["path"]: row for row in pins["files"]}

    def source(path):
        require(path in by_path, "undeclared source: " + path)
        data = (ROOT / path).read_bytes()
        require(sha256(data) == by_path[path]["sha256"], "source hash mismatch: " + path)
        return data

    selected_bytes = source("certificates/selected-result.json")
    assembly_bytes = source("research/community-frontier1094-audit/ASSEMBLY.json")
    manifest_bytes = source("research/community-frontier1094-audit/SELECTED-SOURCE.json")
    archive_bytes = source("research/complex-t16-rare-pattern-exchanges/upstream1087.tar.gz")
    proof_bytes = source("research/bootstrap-depth-audit/sources/pr387/PROOF.md")
    reviewed_bytes = source(
        "research/bootstrap-depth-audit/sources/pr387/bootstrap-sources/"
        "research/community-round8-audit/pr185-proof-reviewed.md")
    row_note = source("notes/three-stage-cover-rows.tex")
    row_note_copy = source("research/five-stage-source527-banks/proof/three-stage-cover-rows.tex")
    require(row_note == row_note_copy, "retained row-note copy differs from the source note")

    selected = json.loads(selected_bytes)
    require(sha256(selected_bytes) == "bb2eaa58647b353f88d0aec2eafb9d30df1be53589231b23e12ceef3e4bad129",
            "selected record changed")
    require(selected["source_manifest"] == "research/community-frontier1094-audit/SELECTED-SOURCE.json",
            "selected source manifest pointer changed")

    selected_manifest = json.loads(manifest_bytes)
    archive_path = "research/complex-t16-rare-pattern-exchanges/upstream1087.tar.gz"
    require(selected_manifest["files"].get(archive_path) == sha256(archive_bytes),
            "selected manifest does not bind the frozen PR1087 archive")

    audit_sources = json.loads(source("research/selected-bootstrap-stock-audit/SOURCES.json"))
    audit_files = {row["path"]: row["sha256"] for row in audit_sources["files"]}
    proof_path = "research/bootstrap-depth-audit/sources/pr387/PROOF.md"
    reviewed_path = (
        "research/bootstrap-depth-audit/sources/pr387/bootstrap-sources/"
        "research/community-round8-audit/pr185-proof-reviewed.md")
    require(audit_files.get(proof_path) == sha256(proof_bytes), "stock audit does not bind PR387 proof")
    require(audit_files.get(reviewed_path) == sha256(reviewed_bytes), "stock audit does not bind PR185 review")

    with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:gz") as archive:
        member = archive.extractfile("code/assemble.py")
        require(member is not None, "frozen PR1087 assembler is absent")
        assembler = member.read().decode("utf-8")
    for fragment in (
        "chain=[Q(384599,10**10)];cuts=[]",
        "for _ in range(7):",
        "a=(1-s)*s+s*old",
        "eta=beta=Q(1,10**24)",
        "native_moments=check_moment('complex',H,73,owner['live'],b,5120,False)",
    ):
        require(fragment in assembler, "selected assembler source mismatch: " + fragment)

    assembly = json.loads(assembly_bytes)
    stages = assembly["bootstrap"]
    require(len(stages) == 7, "selected native branch is not seven stages")
    bit = Fraction(assembly["bit_lower"])
    complex_lower = Fraction(assembly["complex_lower"])
    beta = Fraction(1, 10**24)
    backoff = Fraction(1, 10**27)
    s = min(bit, (1 - beta) * complex_lower) - backoff
    a = Fraction(384599, 10**10)
    require(Fraction(384599, 10**10) < s < bit, "selected stage exponent assumptions changed")
    require(s < (1 - beta) * complex_lower < Fraction(1, 32), "selected complex bound assumption changed")
    exact = []
    for row in stages:
        a = (1 - s) * s + s * a
        exact.append(a)
        require(a == Fraction(row["exponent"]), "selected native recurrence mismatch")

    require(exact[5] != exact[6], "stage-index control failed: stage six equals stage seven")
    wrong_s = min(bit, (1 - beta) * complex_lower)
    wrong_a = Fraction(384599, 10**10)
    for _ in range(6):
        wrong_a = (1 - wrong_s) * wrong_s + wrong_s * wrong_a
    require(wrong_a != exact[5], "backoff control failed")
    require(sha256(row_note + b"\n") != by_path["notes/three-stage-cover-rows.tex"]["sha256"],
            "source-tamper control failed")

    pr387 = proof_bytes.decode("utf-8")
    for fragment in (
        "For j=1,...,6 define A_j",
        "Each inner completed call borrows from its two supplied chunks",
        "restores its row coordinate before returning",
        "does not need an external row multiplier",
        "The retained external 252 allowance is unused slack",
    ):
        require(fragment in pr387, "PR387 interface statement is absent: " + fragment)
    pr185 = reviewed_bytes.decode("utf-8")
    for fragment in (
        "two complete address chunks",
        "arbitrary intervening and preceding complete spectators",
        "restores preceding row coordinates",
        "borrows and restores its required high-digit stock internally",
    ):
        require(fragment in pr185, "PR185 completed-call statement is absent: " + fragment)

    result = {
        "status": "PASS_SELECTED_STAGE6_RECURRENCE_AND_SOURCE_PINS",
        "native_stages": len(stages),
        "selected_arithmetic_stage": 6,
        "pr387_source_parent_layer": 6,
        "pr387_source_child_layer": 5,
        "selected_s": str(s),
        "stage6_cutoff_log2": stages[5]["cutoff_log2"],
        "source_boundary_split": "conditional on k < e/2",
        "source_contract": "PR185 completed-call interface; PR387 separately states its six-level A6 to A5 use",
        "conditional_additional_external_child_rows": "0 at the retained source boundary",
        "selected_physical_call_map": "not bound",
        "selected_stage_external_increment": "unknown",
        "selected_parent_stock_coefficient": "uncomputed",
        "controls": ["stage-index", "omitted-backoff", "source-tamper"],
    }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
