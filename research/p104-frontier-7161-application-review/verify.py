#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Replay the exact #7161 mathematical review from a checkout or source export."""

import argparse
from collections import Counter
from hashlib import sha1, sha256
from pathlib import Path
import gzip
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "e54523517d0f03e58352e647c403a5af3e525a57"
HEADS = {
    7161: "e3f8d39c43b07063dfc5b800f71c5d21015259e6",
    7156: "b44944c3058d522cbff17836e16240d40d77a927",
    7113: "07a76c5e2738882c0cb322278e56f6cae3c9885d",
    7158: "cc48fe3098b639c9100aff5fad31ad9c917205a5",
}
LIVE = {
    "selected": "certificates/frontier7000/CLAIM.json",
    "scalar": "docs/research/pr-intake-evidence/pr7000-application/check_exact_scalar.py",
    "compiler": "research/shared-wire-split-composition/frozen/clifford_exact.py",
    "outer": "research/final4610-independent-admission/checks/outer.py",
}


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def canonical_hash(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def exact_blob(raw):
    return sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def regular_file(root, relative):
    require(not Path(relative).is_absolute() and ".." not in Path(relative).parts, "Relative source path")
    target = root / relative
    require(target.is_file() and target.resolve().is_relative_to(root) and
            all(not p.is_symlink() for p in [target, *target.parents] if p.is_relative_to(root)),
            "Regular unaliased source " + relative)
    return target


def authenticate():
    pins = read(HERE/"INPUTS.json")["files"]
    paths = {r["file"] for r in pins}
    require(len(paths) == len(pins) == 14 and paths == {
        p.relative_to(HERE).as_posix() for p in (HERE/"inputs").rglob("*") if p.is_file()
    }, "Complete vendored inventory")
    for pin in pins:
        require(HEADS[pin["pr"]] == pin["head"] and pin["git_mode"] == "100644", "Exact reviewed source head and mode")
        data = regular_file(HERE, pin["file"]).read_bytes()
        require((len(data), sha256(data).hexdigest(), exact_blob(data)) ==
                (pin["bytes"], pin["sha256"], pin["git_blob"]), "Vendored Git bytes differ: " + pin["file"])
    src = read(HERE/"SOURCES.json")
    inputs = {p["path"]:p for p in src["files"] if p["usage"] == "input"}
    require(src["base_commit"] == BASE and set(inputs) == set(LIVE.values()), "Complete live source dependencies")
    for path, pin in inputs.items():
        data = regular_file(ROOT, path).read_bytes()
        require((sha256(data).hexdigest(), exact_blob(data)) == (pin["sha256"], pin["git_blob"]),
                "Live Git bytes differ: " + path)
    return len(pins)


def run():
    total = authenticate()
    # Exact #7158 review helpers, authenticated before import.
    sys.path[:0] = [str(HERE), str(HERE/"inputs/pr7158")]
    from application import boundary_check, check_outer, check_precision, check_price, scalar_checks, signed_difference, timed_witness
    from check_dense_native import check as check_native
    from check_exit_phase import check as check_phase
    from check_signed_application import check as check_signed
    from word import trace

    new_dir = HERE/"inputs/pr7161"
    prior_dir = HERE/"inputs/pr7156"
    caller_path = HERE/"inputs/pr7113/ODD-TYPE-AB-CALLER.json"
    word, old = (read(p/"WORD.json.gz") for p in (new_dir, prior_dir))
    fixture, receipt, early = (read(new_dir/p) for p in ("NATIVE-RESULT.json", "RESULT.json", "EARLY-RESULT.json"))
    witness, paths = (read(new_dir/p) for p in ("WITNESS.json", "PATHS.json"))
    caller = read(caller_path)
    new_hash, old_hash = map(canonical_hash, (word, old))
    caller_hash = sha256(caller_path.read_bytes()).hexdigest()
    require(new_hash == receipt["price"]["new_native"] == fixture["word_canonical_sha256"] and
            old_hash == receipt["price"]["old_native"] and caller_hash == receipt["caller_sha256"],
            "Native and signed caller bound to the complete candidate result")

    boundary = boundary_check(word, witness)
    timed = timed_witness(old, word, witness, paths)
    old_counts, new_counts = trace(old), trace(word)
    require(signed_difference(new_counts["paid"], old_counts["paid"]) == {1:1} and
            signed_difference(new_counts["helpers"], old_counts["helpers"]) == {4:1,5:1,8:-1},
            "One paid exit and exact new helper targets")
    dense = check_native(word, fixture)
    require(dense["result"]["paid"] == new_counts["paid"], "Two literal paid histograms agree")
    phase = check_phase(word, ROOT/LIVE["compiler"])
    print("PASS exact timed splice, dense endpoint, guarded COPY, grid and rank-one phase", flush=True)

    signed = check_signed(caller, word, dense["result"], receipt, fixture)
    bill = signed["bill"]
    paid, target = [Counter(bill[name]) for name in ("paid_histogram", "productive_histogram")]
    prior_paid, prior_target = paid.copy(), target.copy()
    for current, key in ((prior_paid,"paid"),(prior_target,"helpers")):
        current.subtract({rank:17*n for rank,n in signed_difference(new_counts[key],old_counts[key]).items()})
    published_before = receipt["price"]["before"]
    for actual, key in ((prior_paid,"P"),(prior_target,"T")):
        require({str(r):n for r,n in actual.items() if n} == published_before[key], "Old complete literal histogram")
    require(all(receipt["price"][part]["empty_root_credits"] == 0 for part in ("before","after")),
            "No empty root credits")
    scalar = scalar_checks(word, caller, ROOT/LIVE["scalar"])
    print("PASS formal signed caller, actual 17-stage tariffs and fixed scalar controls", flush=True)
    price = check_price(paid, target, signed_difference(prior_target, prior_paid), new_counts,
                        receipt["price"]["gate"], early)
    precision = check_precision(receipt, new_hash, caller_hash, price["H"])
    outer = check_outer(receipt, read(ROOT/LIVE["selected"]), price, ROOT/LIVE["outer"],
                        read(HERE/"PROPOSED-CLAIM.json"))
    print("PASS funded carrier, common precision, nine outer savings and actual BIT rejection controls", flush=True)
    return dict(status="PASS_EXACT_7161_APPLICATION_REVIEW", main=BASE, source_heads=HEADS,
                vendored_inputs=total, native_sha256=new_hash, predecessor_native_sha256=old_hash,
                caller_sha256=caller_hash, boundary=boundary, timed=timed, dense_native=dense,
                paid_exit_phase=phase, signed_application=signed, scalar=scalar, directed_price=price,
                precision=precision, outer=outer)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="Generate the complete receipt at a new path")
    args = parser.parse_args()
    result = json.loads(json.dumps(run(), default=str))
    if args.out:
        with args.out.open("x") as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write("\n")
    else:
        require(result == read(HERE/"RESULT.json"), "Every frozen review receipt field")
    print(result["status"], result["outer"]["kappa"], flush=True)


if __name__ == "__main__":
    main()
