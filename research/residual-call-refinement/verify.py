"""Read-only contextual residual/CALL audit. Apache-2.0."""

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate(root=ROOT):
    manifest = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    entries = [entry for entry in manifest["files"] if entry["usage"] == "input"]
    need(4 <= len(entries) <= 2048, "bounded nonempty source inventory")
    for entry in entries:
        path = (root / entry["path"]).resolve()
        need(
            path.is_relative_to(root.resolve()) and path.is_file(),
            "canonical source input",
        )
        raw = path.read_bytes()
        need(
            hashlib.sha256(raw).hexdigest() == entry["sha256"],
            "source changed: " + entry["path"],
        )
    return len(entries)


def activate():
    count = authenticate()
    sys.path.insert(0, str(HERE))
    source = ROOT / "research/selected-bit-physical-caller"
    sys.path.insert(0, str(source))
    import loader

    need(
        Path(loader.__file__).resolve() == source / "loader.py", "literal source loader"
    )
    loader.activate()
    return count


def run():
    count = activate()
    import geometry_checks
    import protocol_checks
    import trace_checks

    return {
        "status": "PASS_RESIDUAL_CALL_REFINEMENT",
        "source_files": count,
        "trace": trace_checks.run(),
        "trace_controls": trace_checks.controls(),
        "geometry": geometry_checks.run(),
        "protocol": protocol_checks.run(),
        "theorem": "conditional all-width contextual refinement; written proof, not formal verification",
        "selected_kappa_unchanged": True,
    }


def check_receipt(actual, stored):
    need(
        json.dumps(actual, sort_keys=True) == json.dumps(stored, sort_keys=True),
        "typed result receipt differs",
    )


def main():
    actual = run()
    stored = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))
    check_receipt(actual, stored)
    print(json.dumps(actual, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
