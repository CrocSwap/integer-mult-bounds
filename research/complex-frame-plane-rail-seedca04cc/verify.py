#!/usr/bin/env python3
"""Replay the finite frame-rail search and audit its serialized best word."""
from __future__ import annotations

import gzip
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def run(argv: list[str], *, timeout: int = 600, expect_success: bool = True):
    result = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
    if expect_success and result.returncode != 0:
        raise RuntimeError(f"command failed ({result.returncode}): {' '.join(argv)}\n{result.stdout}\n{result.stderr}")
    if not expect_success and result.returncode == 0:
        raise RuntimeError(f"negative control unexpectedly passed: {' '.join(argv)}")
    return result


def normalized_search(value):
    """Drop only float ranking and the tie-selected closure serialization."""
    value = json.loads(json.dumps(value))
    best = value["best"]
    for key in ("approx_a", "seed_event", "plane", "profile_sha256", "word_output_sha256"):
        best.pop(key, None)
    return value


def main() -> None:
    expected = load_json(PACKAGE / "SEARCH.json")
    receipt = load_json(PACKAGE / "NATIVE-AUDIT.json")
    require(expected["status"] == "PASS_TWO_PLANE_FRAME_RAIL_SEARCH", "search result status")
    require(expected["search_domain"] == {"planes": 36, "helper_helper_seed_gates": 2525,
                                          "seed_plane_pairs": 90900}, "search domain drift")
    require(expected["totals"] == {"tested": 90331, "no_op": 569, "endpoint_reject": 89737,
                                   "interface_reject": 56830, "below_5pct": 594,
                                   "above_5pct": 0, "ambiguous": 0}, "search totals drift")
    require(expected["distinct_valid_profiles"] == 13, "distinct profile count")
    require(expected["exact_best_separation"]["strictly_separated"], "exact profile ceilings do not separate")
    control = expected["negative_control"]["example"]
    require(control["boundary_kind"] == "center_frame", "expected internal centre-frame negative control")
    require(not set(control["plane"]).issubset(set(control["endpoint_frame"])),
            "negative-control plane unexpectedly fits the exact centre frame")
    require(expected["negative_control"]["interface_rejections"] > 0, "no exact interface conflicts exercised")
    require(expected["best"]["profile"] == expected["exact_best_separation"]["best_profile"],
            "best profile differs from exact ceiling winner")
    require(expected["best"]["ceiling_bracket"] == expected["base_ceiling_bracket"],
            "scoped result no longer ties the pinned baseline ceiling")

    with tempfile.TemporaryDirectory(prefix="imb-frame-rail-") as directory:
        temporary = Path(directory)
        generated_search = temporary / "SEARCH.json"
        generated_word = temporary / "BEST-WORD.json.gz"
        run([sys.executable, "-B", str(PACKAGE / "search.py"), "--out", str(generated_search),
             "--candidate-word", str(generated_word)])
        regenerated = load_json(generated_search)
        require(normalized_search(regenerated) == normalized_search(expected),
                "replayed finite search differs from committed exact evidence")
        generated_word_data = json.loads(gzip.decompress(generated_word.read_bytes()))
        require(generated_word_data["report"]["local_profile"] == expected["best"]["profile"],
                "replayed best word has a different paid profile")

        # Independently check the committed candidate. Then corrupt only its
        # claimed paid histogram and require the same auditor to reject it.
        word = PACKAGE / "BEST-WORD.json.gz"
        audit_out = temporary / "NATIVE-AUDIT.json"
        audit_script = ROOT / "research/gauge44-slots/independent/audit_local.py"
        run([sys.executable, "-B", str(audit_script), "--word", str(word), "--output", str(audit_out)], timeout=120)
        actual_audit = load_json(audit_out)
        stable_actual = {k: v for k, v in actual_audit.items() if k != "elapsed_seconds"}
        stable_expected = {k: v for k, v in receipt.items() if k != "elapsed_seconds"}
        require(stable_actual == stable_expected, "native audit receipt differs")
        require(actual_audit["local_profile"] == expected["best"]["profile"],
                "native audited paid profile differs from exact search winner")
        compressed = word.read_bytes()
        content = gzip.decompress(compressed)
        require(hashlib.sha256(content).hexdigest() == receipt["content_sha256"], "candidate content pin mismatch")

        bad = json.loads(content)
        bad["report"]["local_profile"]["1"] += 1
        bad_word = temporary / "BAD-PAID-PROFILE.json.gz"
        bad_word.write_bytes(gzip.compress(json.dumps(bad, sort_keys=True, separators=(",", ":")).encode(), mtime=0))
        rejected = run([sys.executable, "-B", str(audit_script), "--word", str(bad_word),
                        "--output", str(temporary / "BAD-AUDIT.json")], timeout=120, expect_success=False)
        require("paid profile mismatch" in rejected.stderr, "negative control failed for an unrelated reason")

    print("PASS_FRAME_RAIL_FINITE_SEARCH_NATIVE_AUDIT_AND_NEGATIVE_CONTROL")


if __name__ == "__main__":
    main()
