#!/usr/bin/env python3
"""A cheap, source-bound entry to the selected bottleneck; not a full cold replay.

Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path

from verify_selected_result import check

ROOT = Path(__file__).resolve().parents[1]


def summarize(record, certificate, target=Fraction(1, 100)):
    if not 0 < target < 1:
        raise ValueError("target kappa must be between zero and one")
    bit, complex_ = Fraction(certificate["bit_lower"]), Fraction(certificate["complex_lower"])
    if bit <= 0 or complex_ <= 0:
        raise ValueError("supplier savings must be positive")
    required = target / (1 - target)
    return {
        "status": "PASS_RESEARCH_BASELINE_BINDINGS_ONLY",
        "selected_kappa": record["kappa"], "review": record["review"],
        "certificate": record["certificate"], "full_replay": record["reproduce"],
        "bit_saving": str(bit), "complex_saving": str(complex_),
        "binding_primitive": "bit" if bit < complex_ else "complex" if complex_ < bit else "equal",
        "ideal_balanced_cap": str(min(bit, complex_) / (1 + min(bit, complex_))),
        "target_kappa": str(target), "target_primitive_under_retained_transfer": str(required),
        "required_bit_multiplier": float(required / bit),
        "required_complex_multiplier": float(required / complex_),
        "scope": "Selected source bindings and arithmetic only. The a/(1+a) transfer is a planning model under retained hypotheses, not a universal requirement or supplier verification.",
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--target", default="1/100", help="rational target kappa for planning")
    args = ap.parse_args()
    raw = (ROOT / "certificates/selected-result.json").read_bytes()
    record = json.loads(raw)
    check(record, ROOT)
    certificate = json.loads((ROOT / record["certificate"]).read_bytes())
    report = summarize(record, certificate, Fraction(args.target))
    report["selected_record_sha256"] = hashlib.sha256(raw).hexdigest()
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
