"""Rebuild and check one fixed-output R420 block rewrite. Standard library only.

Prepared for x0hu with substantial OpenAI Codex assistance; Apache-2.0.
"""
import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

import record_audit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = "research/e8-bit-r420/data/bitE8mut-r420.json.gz"
CHECKER = "research/e8-bit-r420/code/xcheck.py"
START, STOP, FRAME = 371, 417, 547
REGISTERS = [19, 24, 35, 40, 54, 56, 65, 74, 84, 95, 100, 111]
# Each move advances dst += src before a reader, removing the now-redundant
# direct additions of src to that reader. Outputs stay on the original wires.
STEPS = [
    ((111, 100), (54, 100), [(54, 100), (65, 100), (56, 100)]),
    ((74, 100), (40, 100), [(40, 100), (84, 100), (19, 100), (95, 100)]),
    ((65, 54), (74, 56), [(74, 54), (56, 54)]),
    ((56, 65), (74, 56), [(74, 65)]),
    ((40, 35), (100, 95), [(100, 35), (95, 35)]),
]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def transfer(ops, sign=1):
    """Exact integer matrix, so positive bounds and signed inverses are checked."""
    n = len(REGISTERS)
    index = {r: i for i, r in enumerate(REGISTERS)}
    rows = [[int(i == j) for j in range(n)] for i in range(n)]
    for dst, src in ops:
        require(dst in index and src in index and dst != src, "invalid block operands")
        d, s = index[dst], index[src]
        rows[d] = [x + sign * y for x, y in zip(rows[d], rows[s])]
    return rows


def dominates(before, after):
    return all(y <= x for a, b in zip(before, after) for x, y in zip(a, b))


def improvement(before, after):
    require(transfer(before) == transfer(after), "integer forward transfer changed")
    require(transfer(before[::-1], -1) == transfer(after[::-1], -1),
            "signed inverse transfer changed")
    require(dominates(transfer(before[::-1]), transfer(after[::-1])),
            "reverse cancellation-free transfer increased")


def rebuild(word):
    block = word["B"][START:STOP]
    require(len(block) == 46 and all(f == FRAME and len(s) == 1 for f, d, s in block),
            "unexpected block boundaries")
    before = [(d, s[0]) for f, d, s in block]
    require(sorted({r for op in before for r in op}) == REGISTERS, "block wires changed")
    ops, stages = list(before), []
    for gate, anchor, removed in STEPS:
        previous = list(ops)
        ops.remove(gate)
        ops.insert(ops.index(anchor), gate)
        for op in removed:
            ops.remove(op)
        improvement(previous, ops)
        stages.append({"gates": len(ops), "roundtrip_unit_peak":
                       max(map(sum, transfer(ops + ops[::-1])))})
    improvement(before, ops)
    require(len(ops) == 34, "unexpected rewritten length")
    candidate = copy.deepcopy(word)
    candidate["B"][START:STOP] = [[FRAME, d, [s]] for d, s in ops]
    candidate["C"] = [[1, d, srcs] for _, d, srcs in reversed(candidate["A"] + candidate["B"])
                      if not 120 <= d < 240]
    return candidate, before, ops, stages


def must_reject(name, callback, catches=(ValueError,)):
    try:
        callback()
    except catches:
        return name
    raise ValueError("negative control accepted: " + name)


def run(output):
    sources = json.loads((HERE / "SOURCES.json").read_text())
    for path, sha in sources["sha256"].items():
        require(digest((ROOT / path).read_bytes()) == sha, "source pin mismatch: " + path)
    baseline = json.loads(gzip.decompress((ROOT / WORD).read_bytes()))
    candidate, before, after, stages = rebuild(baseline)
    spec = importlib.util.spec_from_file_location("r420_original_xcheck", ROOT / CHECKER)
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    for word in (baseline, candidate):
        _, labels, full, hypotheses, conclusion, _ = checker.check(word)
        require(all(hypotheses.values()) and all(conclusion.values()), "interface failure")
        require(full["columns"] == 660 and labels["frames"] == 672, "coverage changed")
    output.mkdir(parents=True, exist_ok=True)
    path = output / "candidate.json.gz"
    # Canonical decompressed bytes, not the platform's gzip header, identify the word.
    with path.open("wb") as stream:
        with gzip.GzipFile(fileobj=stream, mode="wb", filename="", mtime=0) as compressed:
            compressed.write(canonical(candidate))
    cost = record_audit.compare(ROOT / WORD, path, output / "records")
    controls = []
    controls.append(must_reject("omit block gate", lambda: improvement(before, after[1:])))
    wrong = list(after)
    wrong[0] = (40, 19)
    controls.append(must_reject("change block source", lambda: improvement(before, wrong)))
    doubled = after + [after[0], after[0]]
    require([[x % 2 for x in row] for row in transfer(doubled)] ==
            [[x % 2 for x in row] for row in transfer(after)], "invalid parity-only control")
    controls.append(must_reject("parity-preserving duplicated pair", lambda: improvement(before, doubled)))
    bad_cleanup = copy.deepcopy(candidate)
    bad_cleanup["C"].pop()
    controls.append(must_reject("omit cleanup gate", lambda: checker.check(bad_cleanup), (checker.Reject,)))
    bad_frame = copy.deepcopy(candidate)
    bad_frame["B"][START][0] = 0
    controls.append(must_reject("block gate at zero frame", lambda: checker.check(bad_frame), (checker.Reject,)))
    # Check that the original cleanup cannot be reused after the rewrite.
    stale = copy.deepcopy(candidate)
    stale["C"] = baseline["C"]
    stale_hypotheses = checker.Word(stale).interface()[0]
    require(not stale_hypotheses["H4_C_literal_reverse_at_full"], "stale cleanup passed H4")
    controls.append("stale cleanup violates literal-reverse interface")
    old_reverse, new_reverse = transfer(before[::-1]), transfer(after[::-1])
    result = {
        "status": "PASS_R420_BLOCK5_RESYNTHESIS",
        "base_commit": sources["base_commit"],
        "registers": REGISTERS,
        "source_B_slice": [START, STOP],
        "source_offsets": [before.index(op) for op in after],
        "replacement_ops": after,
        "steps": stages,
        "integer_forward_matrix": transfer(after),
        "baseline_reverse_majorant": old_reverse,
        "candidate_reverse_majorant": new_reverse,
        "strict_reverse_entries": sum(y < x for a, b in zip(old_reverse, new_reverse) for x, y in zip(a, b)),
        "baseline_local_roundtrip_peak": max(map(sum, transfer(before + before[::-1]))),
        "candidate_local_roundtrip_peak": max(map(sum, transfer(after + after[::-1]))),
        "candidate_canonical_sha256": digest(canonical(candidate)),
        "full_word_checks": {"columns": 660, "closed_frames": 672, "H1_H5_and_conclusion": True},
        "cost": cost,
        "negative_controls": controls,
        "scope": "Finite block and native-word improvement; no new kappa, full hosting replay or full theorem proof",
    }
    # Normalize JSON object keys and tuple/list representations before comparison.
    return json.loads(canonical(result))


def main():
    if not __debug__:
        raise SystemExit("REJECT: run without -O; inherited checkers use assertions")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="directory for candidate and replay records")
    parser.add_argument("--write-certificate", action="store_true", help="regenerate the committed exact certificate")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="r420-block5-") as scratch:
        result = run(args.output if args.output else Path(scratch))
    cert = HERE / "certificate.json"
    if args.write_certificate:
        cert.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    expected = json.loads(cert.read_text())
    require(result == expected, "certificate mismatch")
    print("PASS_R420_BLOCK5_RESYNTHESIS block=46->34 native_adds=26916->26892 rank_mass=5112 kappa=unchanged")


if __name__ == "__main__":
    main()
