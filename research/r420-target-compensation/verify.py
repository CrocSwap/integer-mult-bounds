"""Exact finite verification, without rerunning the search.

Apache-2.0; prepared with substantial OpenAI Codex assistance.
"""

import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (HERE, N, R, ROOT, V, Reject, bill, canonical, digest,
                    make_word, need, norm_replay, read_word, rows_of, scalar_stream)

XCHECK = "research/e8-bit-r420/code/xcheck.py"


def pins(manifest):
    for name, expected in manifest["files"].items():
        need(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected,
             "source pin mismatch: " + name)


def boundary(original, word):
    """An exact transcript-level substitute for the old gate-local H2."""
    values = [1 << r for r in range(N)]
    for frame, destination, sources in word["D"]:
        need(frame == 0, "D left frame zero")
        need(V <= destination < 2 * V, "D destination is not a target")
        need(bool(sources) and len(set(sources + [destination])) == len(sources) + 1,
             "D has duplicate or self operands")
        need(all(type(s) is int and V <= s < N for s in sources), "D source outside target/helper rows")
        for source in sources:
            values[destination] ^= values[source]
    expected = [1 << r for r in range(N)]
    for t, row in enumerate(rows_of(original)):
        expected[V + t] ^= row << (2 * V)
    need(values == expected, "D boundary is not (x, y + K s, s)")
    return digest(values)


def columns(word, reverse=False):
    """A separate Boolean-column walk, including explicit copy/clear work.

    This does not import the symbolic-row engine or the scalar-stream builder.
    The two implementations are computational cross-checks, not human review.
    """
    phases = ["D", "A", "scatter", "B", "C"]
    if reverse:
        phases.reverse()
    for column in range(N):
        values = bytearray(N + 1)
        values[column] = 1
        for section in phases:
            if section == "scatter":
                indices = range(len(word["ret"]))
                if reverse:
                    indices = reversed(indices)
                for k in indices:
                    values[N] = values[word["ret"][k]]
                    for t, row in enumerate(word["scatter"]):
                        if k in row:
                            values[V + t] ^= values[N]
                    values[N] = 0
            else:
                gates = reversed(word[section]) if reverse else word[section]
                for _, destination, sources in gates:
                    for source in sources:
                        values[destination] ^= values[source]
        expected = bytearray(N + 1)
        expected[column] = 1
        if column < V:
            expected[V + column] = 1
        need(values == expected, f"column {column}, reverse={reverse}: bad full endpoint")
    return N


def geometry(word, dimensions):
    current = list(word["start"])
    paths = [[f] for f in current]
    profile, moves = Counter(), 0

    def visit(register, frame):
        nonlocal moves
        if current[register] != frame:
            rank = dimensions[frame] - dimensions[current[register]]
            need(rank > 0, "non-increasing frame visit")
            profile[rank] += 1
            current[register] = frame
            paths[register].append(frame)
            moves += 1

    for section in ("D", "A", "scatter", "B", "C"):
        if section == "scatter":
            for register in word["ret"]:
                profile[dimensions[current[register]]] += 1
        else:
            for frame, destination, sources in word[section]:
                for register in [destination] + sources:
                    visit(register, frame)
    for register, frame in enumerate(word["final"]):
        visit(register, frame)
    return {
        "frame_paths_sha256": digest(paths),
        "moves": moves,
        "copies": len(word["ret"]),
        "erasures": len(word["ret"]),
        "helpers": word["R"],
        "paid_profile": {str(k): v for k, v in sorted(profile.items())},
        "rank_mass": sum(k * v for k, v in profile.items()),
    }


def budget(original_bill, result):
    need(result["total_adds"] < original_bill["total_adds"], "no scalar saving")
    need(result["forward"] <= original_bill["forward"], "larger forward allowance")
    need(result["five_stage_bits"] <= 104, "five-stage prefix allowance exceeded")
    need(result["nine_stage_bits"] <= 192, "nine-stage prefix allowance exceeded")


def controls(original, word, candidate, original_bill):
    rejected = []

    def rejects(name, thunk):
        try:
            thunk()
        except Reject:
            rejected.append(name)
        else:
            raise Reject("negative control accepted: " + name)

    def changed(gates):
        return dict(word, D=gates)

    d = word["D"]
    count = len(candidate["basis_operations"])
    rejects("omit one entrance basis gate", lambda: boundary(original, changed(d[1:])))
    rejects("omit one exit basis gate", lambda: boundary(original, changed(d[:-1])))
    wrong_inverse = d[:len(d) - count] + list(reversed(d[len(d) - count:]))
    rejects("apply exit basis in forward order", lambda: boundary(original, changed(wrong_inverse)))
    rejects("omit all entrance basis gates (zero targets would miss this)",
            lambda: boundary(original, changed(d[count:])))
    # Explicitly exhibit the blind spot of a test restricted to zero targets.
    values = [0] * V + [0] * V + [1 << r for r in range(R)]
    for _, destination, sources in d[count:]:
        for source in sources:
            values[destination] ^= values[source]
    need(values[V:2 * V] == rows_of(original), "zero-target blind-spot control changed")
    wrong_middle = d[:count] + copy.deepcopy(original["D"]) + d[len(d) - count:]
    rejects("inject K instead of E K", lambda: boundary(original, changed(wrong_middle)))
    missing = copy.deepcopy(d)
    missing[count][2].pop()
    rejects("omit one dirty-helper injection", lambda: boundary(original, changed(missing)))
    illegal = copy.deepcopy(d)
    illegal[0][0] = 1
    rejects("basis operation at full frame", lambda: boundary(original, changed(illegal)))
    illegal = copy.deepcopy(d)
    illegal[count][2][0] = 0
    rejects("read a source at frame zero", lambda: boundary(original, changed(illegal)))
    illegal = copy.deepcopy(d)
    illegal[0][2][0] = illegal[0][1]
    rejects("self XOR", lambda: boundary(original, changed(illegal)))
    illegal = copy.deepcopy(d)
    illegal[0][1] = 240
    rejects("write a helper", lambda: boundary(original, changed(illegal)))
    # A neutral pair is a valid F2 circuit but is unacceptable to this paid budget.
    _, reverse_values = norm_replay(scalar_stream(word), reverse=True)
    source = V + max(range(V), key=lambda t: reverse_values[V + t])
    destination = V + (source - V + 1) % V
    pair = [[0, destination, [source]], [0, destination, [source]]]
    neutral = changed(pair + d)
    need(boundary(original, neutral) == boundary(original, word), "neutral pair changed F2 map")
    rejects("F2-neutral pair exceeds the prefix allowance", lambda: budget(original_bill, bill(neutral)))
    bad_ops = copy.deepcopy(candidate["basis_operations"])
    bad_ops[0][0] = V
    rejects("basis recipe uses an extra register", lambda: make_word(original, bad_ops))
    bad_pin = {"files": {"research/e8-bit-r420/data/bitE8mut-r420.json.gz": "0" * 64}}
    rejects("incorrect immutable source pin", lambda: pins(bad_pin))
    return rejected


def verify(candidate):
    original = read_word()
    need(candidate["format"] == "r420-compensation-target-basis-v1", "candidate format")
    need(candidate["assignment_seed"] == 18, "assignment seed")
    need(candidate["original_word_sha256"] == digest(original), "candidate source mismatch")
    word, reduced = make_word(original, candidate["basis_operations"])
    need(all(word[k] == original[k] for k in original if k != "D"), "outside D changed")
    endpoint = boundary(original, word)
    spec = importlib.util.spec_from_file_location("predecessor_xcheck", ROOT / XCHECK)
    predecessor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(predecessor)
    base = predecessor.Word(original)
    labels, base_full = base.labels(), base.full()
    base_h, base_c, _ = base.interface()
    need(all(base_h.values()) and all(base_c.values()), "baseline interface failure")
    check = predecessor.Word(word)
    full = check.full()
    h, c, _ = check.interface()
    need(all(v for k, v in h.items() if k != "H2_D_frame0_targets_from_helpers"), "unchanged hypothesis failed")
    need(all(v for k, v in c.items() if k != "K_equals_D"), "unchanged conclusion failed")
    # The old gate-local predicate and its direct-summation K calculation really
    # do reject this circuit. They are replaced by the checked D boundary above.
    need(h["H2_D_frame0_targets_from_helpers"] is False and c["K_equals_D"] is False,
         "expected old interface rejection not observed")
    before, after = bill(original), bill(word)
    budget(before, after)
    old_geometry, new_geometry = geometry(original, base.fdim), geometry(word, check.fdim)
    need(old_geometry == new_geometry, "frame/copy/recursive profile changed")
    need(after == candidate["search"]["guarded"]["bill"], "nomination bill mismatch")
    coverage = [columns(word, reverse) for reverse in (False, True)]
    negative = controls(original, word, candidate, before)
    result = {
        "status": "PASS_R420_TARGET_COMPENSATION",
        "original_word_sha256": digest(original),
        "word_sha256": digest(word),
        "basis_operations": len(candidate["basis_operations"]),
        "helper_injections": sum(r.bit_count() for r in reduced),
        "reduced_matrix_sha256": digest(reduced),
        "D_boundary_sha256": endpoint,
        "labels": labels,
        "native_columns": [base_full["columns"], full["columns"]],
        "separate_column_walk_forward_reverse": coverage,
        "original_bill": before,
        "candidate_bill": after,
        "geometry": new_geometry,
        "saved_local_adds": before["total_adds"] - after["total_adds"],
        "saved_9_stage_32_replica_adds": 9 * 32 * (before["total_adds"] - after["total_adds"]),
        "old_gate_local_H2_accepts": False,
        "replacement_D_boundary_accepts": True,
        "negative_controls": negative,
    }
    return result, word


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="new output directory for the word and report")
    parser.add_argument("--write-certificate", action="store_true", help="create a missing certificate after fresh verification")
    args = parser.parse_args()
    need(not sys.flags.optimize, "assertions must remain enabled in predecessor checks")
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    pins(manifest)
    candidate = json.loads((HERE / "candidate.json").read_text())
    result, word = verify(candidate)
    certificate = HERE / "CERTIFICATE.json"
    if args.write_certificate:
        with certificate.open("x") as f:
            json.dump(result, f, indent=2)
            f.write("\n")
    else:
        need(result == json.loads(certificate.read_text()), "certificate mismatch")
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output / "word.json.gz").write_bytes(gzip.compress(canonical(word), mtime=0))
        (args.output / "report.json").write_text(json.dumps(result, indent=2) + "\n")
    pins(manifest)
    print(f"PASS_R420_TARGET_COMPENSATION D=19922->12043 total=26916->19037 "
          f"columns=660 rank_mass=5112 nine_bits=192 controls={len(result['negative_controls'])}")


if __name__ == "__main__":
    main()
