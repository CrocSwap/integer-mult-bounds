"""Source inventory and independently replayed finite controls. Apache-2.0."""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path

ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}

def need(condition, message):
    if not condition:
        raise ValueError(message)

def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()

def inventory(root):
    root = Path(root)
    pins = json.loads((root / "MANIFEST.json").read_text(encoding="utf-8"))
    actual = {p.relative_to(root).as_posix() for p in root.rglob("*")
              if p.is_file() and ".lake" not in p.relative_to(root).parts
              and "__pycache__" not in p.relative_to(root).parts
              and p.relative_to(root).as_posix() != "MANIFEST.json"}
    need(actual == set(pins), "exact package source inventory differs")
    for name, expected in pins.items():
        p = root / name
        need(not p.is_symlink() and p.resolve().is_relative_to(root.resolve()), "external source: " + name)
        need(digest(p) == expected, "source hash differs: " + name)
    return pins

def validate_audit(rows, expected_names, expected_modules):
    need(isinstance(rows, list) and rows, "empty declaration audit")
    names = [r.get("name") for r in rows]
    need(len(names) == len(set(names)), "duplicate declaration reports")
    need(set(names) == set(expected_names), "missing or unexpected declaration reports")
    need(all(r.get("module") in expected_modules for r in rows), "foreign defining module")
    need(set(r["module"] for r in rows) == set(expected_modules), "missing defining module coverage")
    for row in rows:
        need(row.get("kind") in {"theorem", "definition", "opaque", "axiom", "other"}, "missing declaration kind")
        need(row["kind"] != "axiom", "package declares its own axiom: " + row["name"])
        need(isinstance(row.get("axioms"), list), "missing axiom list")
        need(set(row["axioms"]) <= ALLOWED_AXIOMS, "unapproved dependency: " + row["name"])
    need(any(r["kind"] == "theorem" for r in rows), "no actual theorem audit")

def audit_controls():
    good = [{"name": "MultitapeToolkit.fixture", "module": "MultitapeToolkit.Model", "kind": "theorem", "axioms": ["propext"]},
            {"name": "_private.MultitapeToolkit.Model.0.helper", "module": "MultitapeToolkit.Model", "kind": "theorem", "axioms": []}]
    expected = [r["name"] for r in good]
    modules = {"MultitapeToolkit.Model"}
    validate_audit(good, expected, modules)
    cases = [([], "zero reports"), (good[:1], "missing report"),
             (good + [good[0]], "duplicate report"),
             (good + [dict(good[0], name="MultitapeToolkit.extra")], "unexpected report"),
             ([dict(good[0], axioms=["sorryAx"]), good[1]], "unproved theorem"),
             ([dict(good[0], axioms=["arbitraryOracle"]), good[1]], "unproved oracle"),
             ([dict(r, kind="definition") for r in good], "no theorem"),
             ([dict(good[0], axioms=None), good[1]], "absent axiom list"),
             ([dict(good[0], kind="axiom", axioms=[]), good[1]], "forged empty own axiom"),
             ([dict(good[0], module="Foreign.Model"), good[1]], "foreign ownership"),
             ([dict(good[0], module="MultitapeToolkit.Trace"), good[1]], "unexpected module")]
    for rows, label in cases:
        try:
            validate_audit(rows, expected, modules)
        except (ValueError, TypeError):
            continue
        raise ValueError("accepted audit corruption: " + label)
    return len(cases)


def main():
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    root=Path(__file__).resolve().parent
    pins=inventory(root)
    controls=audit_controls()
    print(json.dumps(dict(status="PASS_SOURCE_INVENTORY_AND_AUDIT_CONTROLS",files=len(pins),audit_corruptions_rejected=controls,kernel_checked=False)))

if __name__=="__main__":
    main()
