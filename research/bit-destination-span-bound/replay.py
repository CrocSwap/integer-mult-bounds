"""Authenticate the bundled word and replay the complete destination census."""

import argparse
from hashlib import sha1, sha256
import json
from pathlib import Path
import runpy
import shutil
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent


def json_data(path):
    return json.loads(path.read_bytes())


def check_provenance():
    seen = set()
    for line in (ROOT / "PROVENANCE.tsv").read_text().splitlines():
        key, digest, blob, _ = line.split("\t")
        path = Path(key)
        if path.is_absolute() or ".." in path.parts or path in seen:
            raise ValueError(f"ambiguous provenance path {key}")
        seen.add(path)
        raw = (ROOT / path).read_bytes()
        exact_blob = sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()
        if sha256(raw).hexdigest() != digest or exact_blob != blob:
            raise ValueError(f"changed provenance source {key}")
    assert len(seen) == 4


def rejects(call, reason):
    try:
        call()
    except ValueError as error:
        if reason not in str(error):
            raise
    else:
        raise AssertionError(f"missing rejection for {reason}")


def check_controls(verify, audit, receipt):
    verify["control"]()
    audit["control"]()
    base = ROOT / "inputs"
    first = json_data(ROOT / "DUALS.json")[0][0]
    forged = dict(receipt, eligible_paid_moves=1, all_eligible=[{"clock": first}])
    rejects(lambda: audit["audit"](base, forged), "forged destination membership")

    capped = verify["run"](base, 240, 1)
    assert capped["status"] == "INCOMPLETE_CAP"
    assert capped["cases_visited"] == 1 and len(capped["unvisited_move_ids"]) == 2870
    assert not ({"decision", "net_after_free_synthesis"} & capped.keys())

    with TemporaryDirectory() as tmp:
        altered = Path(tmp) / "inputs"
        shutil.copytree(base, altered)
        word = altered / audit["WORD"]
        raw = word.read_bytes()
        word.write_bytes(bytes([raw[0] ^ 1]) + raw[1:])
        rejects(lambda: verify["run"](altered, 240, 2871), "changed source")
        rejects(lambda: audit["audit"](altered, receipt), "changed source")
    print("PASS_BIT_DESTINATION_SPAN_CONTROLS changed_source=2 forged_membership=1 cap=1")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--controls", action="store_true")
    args = parser.parse_args()
    assert __debug__, "run with assertions enabled"
    check_provenance()
    verify = runpy.run_path(str(ROOT / "verify.py"))
    audit = runpy.run_path(str(ROOT / "audit.py"))
    receipt = verify["run"](ROOT / "inputs", 240, 2871)
    assert receipt == json_data(ROOT / "RESULT.json")
    report, duals = audit["audit"](ROOT / "inputs", receipt)
    encoded = (json.dumps(report, sort_keys=True, indent=2) + "\n").encode()
    assert encoded == (ROOT / "AUDIT.json").read_bytes()
    assert duals == (ROOT / "DUALS.json").read_bytes()
    assert receipt["decision"] == "PIVOT_NEGATIVE_UPPER" and receipt["eligible_paid_moves"] == 0
    print("PASS_BIT_DESTINATION_SPAN moves=2871 duals=2871 eligible=0 savings=0 kappa_change=0")
    if args.controls:
        check_controls(verify, audit, receipt)


if __name__ == "__main__":
    main()
