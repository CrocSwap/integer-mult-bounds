#!/usr/bin/env python3
"""Source-bound orientation for the selected productive-helper certificate.

The pinned historical research_baseline.py expects a different certificate and
balanced-transfer model. Keep its bytes unchanged for existing research inputs.
This report checks metadata consistency, not operators or the all-size theorem.

Mihir Srivastava, with substantial OpenAI Codex assistance. Apache-2.0.
Source-binding machinery: Douglas Colkitt and its retained contributors.
"""
import argparse
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import sys

from runpy import run_path

ROOT = Path(__file__).resolve().parents[1]
# -B still reads cached bytecode; source-binding guards must use current source.
check = run_path(str(ROOT / "scripts/verify_selected_result.py"),
                 run_name="verify_selected_result")["check"]
SCHEMA = "proposed-conditional-integer-multiplication-claim/1"
OUTER_ROWS = frozenset({
    "boundary_algebraic_matrix", "fused_gaussian", "global_coordinate_router",
    "group_bit_router", "group_scans", "main_transform",
    "microbox_face_corrections", "polynomial_products", "sparse_union_movement",
})


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rational(value, label, *, unit_interval=False):
    require(isinstance(value, str), label + " must be an exact rational string")
    try:
        result = Fraction(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError(label + " must be an exact rational string") from exc
    require(result > 0, label + " must be positive")
    if unit_interval:
        require(result < 1, label + " must be less than one")
    return result


def summarize(record, certificate):
    """Project this schema's distinct budget stages without a transfer guess."""
    require(certificate.get("schema") == SCHEMA,
            "Unsupported productive-helper certificate schema; "
            "the historical bit_lower/complex_lower report is research_baseline.py")
    kappa = rational(record["kappa"], "selected kappa", unit_interval=True)
    require(kappa == rational(certificate.get("kappa"), "certificate kappa"),
            "Selected kappa differs from certificate")

    templates = certificate.get("uniform_templates")
    require(isinstance(templates, list) and len(templates) == 2,
            "Expected exactly the complex and BIT before cover templates")
    uniform = {}
    for item in templates:
        require(isinstance(item, dict), "Invalid uniform template")
        family = item.get("family")
        require(isinstance(family, str) and family in {"complex", "BIT before cover"}
                and family not in uniform, "Unknown or duplicate uniform-template family")
        saving = rational(item.get("saving"), family + " saving", unit_interval=True)
        rank = item.get("rank_encoding")
        require(isinstance(rank, str) and bool(rank.strip()), "Missing template rank encoding")
        # Keep the enormous algorithm-defined rank symbolic; do not materialize it.
        uniform[family] = {"rank_encoding": rank, "saving": str(saving)}

    ordinary = rational(certificate.get("ordinary_BIT_saving"),
                        "ordinary BIT saving", unit_interval=True)
    admitted = rational(certificate.get("admitted_BIT_saving"),
                        "admitted BIT saving", unit_interval=True)
    require(admitted <= ordinary <= Fraction(uniform["BIT before cover"]["saving"]),
            "BIT budget stages are out of order")

    rows = certificate.get("nine_outer_savings")
    require(isinstance(rows, dict) and rows.keys() == OUTER_ROWS,
            "Expected the schema's complete nine-row outer ledger")
    # Some cost rows have savings above one; only primitive savings use (0, 1).
    outer = {name: rational(value, "outer row " + name) for name, value in rows.items()}
    limiting = min(outer.values())
    require(limiting == rational(certificate.get("limiting_outer_saving"),
                                 "limiting outer saving"),
            "Declared outer minimum differs from its rows")
    slack = limiting - kappa
    require(slack > 0, "Selected kappa needs strict slack below every outer row")
    require(slack == rational(certificate.get("strict_limiting_slack"),
                              "strict limiting slack"),
            "Declared strict slack differs from outer minimum minus selected kappa")

    return {
        "status": "PASS_RESEARCH_BASELINE_BINDINGS_ONLY",
        "certificate_schema": SCHEMA,
        "selected_kappa": str(kappa),
        "review": record["review"],
        "certificate": record["certificate"],
        "full_replay": record["reproduce"],
        "uniform_templates": uniform,
        "ordinary_BIT_saving": str(ordinary),
        "admitted_BIT_saving": str(admitted),
        "nine_outer_savings": {name: str(value) for name, value in outer.items()},
        "binding_outer_rows": sorted(name for name, value in outer.items() if value == limiting),
        "limiting_outer_saving": str(limiting),
        "strict_limiting_slack": str(slack),
        "selected_scope": record.get("scope"),
        "scope": "Selected source bindings and exact metadata consistency only. "
                 "Uniform-template, ordinary BIT, admitted BIT and outer budgets "
                 "are distinct stages. No balanced a/(1+a) cap is inferred. "
                 "This is not a native replay, supplier admission or theorem proof.",
    }


def report(root=ROOT):
    raw = (root / "certificates/selected-result.json").read_bytes()
    record = json.loads(raw)
    # Always authenticate the entire selected closure before reporting success.
    check(record, root)
    certificate = json.loads((root / record["certificate"]).read_bytes())
    result = summarize(record, certificate)
    result["selected_record_sha256"] = sha256(raw).hexdigest()
    return result


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    try:
        result = report()
    except (OSError, ValueError, KeyError, TypeError) as exc:
        # ASCII JSON is also printable on a legacy Windows console.
        print(json.dumps({"status": "FAIL_RESEARCH_BASELINE", "error": str(exc)}), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
