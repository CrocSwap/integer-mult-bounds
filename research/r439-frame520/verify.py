#!/usr/bin/env python3
"""Independent finite frame-520 certificate replay; imports no search code.

Ross Richardson, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
import tempfile
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
CHECKER = "research/e8-bit-p111-tuned/code/xcheck_p.py"
PRIOR = "research/r439-frame520/inputs/pr844-CANDIDATE.json"
PINS = {
    SOURCE: "e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f",
    CHECKER: "af3decc877e27c00001cf56f50c6c09566e8e101297ab34c7860aed96a06d80e",
    PRIOR: "ebbefa267265a555ee0e959df0d62363203fdf514ad617a9a1ccd934af27831c",
}
WIRES = [21, 26, 36, 44, 51, 55, 64, 71, 80, 84, 94, 102]
FRAME, START, STOP = 520, 242, 283


class Reject(ValueError):
    pass


def need(ok, message):
    if not ok:
        raise Reject(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def matrix(ops, wires=WIRES, sign=1):
    """Compose elementary shears, using columns instead of search's row updates."""
    n = len(wires)
    index = {r: i for i, r in enumerate(wires)}
    columns = []
    for j in range(n):
        col = [int(i == j) for i in range(n)]
        for d, s in ops:
            need(d in index and s in index and d != s, "invalid block operand")
            col[index[d]] += sign * col[index[s]]
        columns.append(col)
    return [list(row) for row in zip(*columns)]


def pairs(gates):
    need(all(f == FRAME and len(ss) == 1 for f, _, ss in gates), "block shape")
    return [[d, ss[0]] for _, d, ss in gates]


def check_block(old, operations):
    need(0 < len(operations) < 31, "must beat PR844's 31-ADD block")
    forward = matrix(operations)
    need(forward == matrix(old), "ordered forward integer map differs")
    # Also check the signed inverse, independently of mod-2 replay.
    need(matrix(operations[::-1], sign=-1) == matrix(old[::-1], sign=-1),
         "signed inverse differs")
    reverse = matrix(operations[::-1])
    old_reverse = matrix(old[::-1])
    need(all(a <= b for ar, br in zip(reverse, old_reverse) for a, b in zip(ar, br)),
         "positive reverse transfer is not dominated")
    index = {r: i for i, r in enumerate(WIRES)}
    for bits in range(1 << len(WIRES)):
        outputs = []
        for program in (old, operations):
            state = [(bits >> i) & 1 for i in range(len(WIRES))]
            for d, s in program:
                state[index[d]] ^= state[index[s]]
            outputs.append(state)
        need(outputs[0] == outputs[1], "Boolean truth table differs")
    return {
        "before": len(old), "after": len(operations), "truth_table_inputs": 4096,
        "ordered_forward_integer_transfer": forward,
        "positive_reverse_before": old_reverse, "positive_reverse_after": reverse,
        "reverse_strict_entries": sum(a < b for ar, br in zip(reverse, old_reverse)
                                      for a, b in zip(ar, br)),
    }


def cleanup(word):
    v = word["v"]
    full = next(i for i, frame in enumerate(word["frames"]) if len(frame) == v)
    return [[full, d, list(ss)] for _, d, ss in reversed(word["A"] + word["B"])
            if d < v or d >= 2 * v]


def splice(word, operations):
    result = copy.deepcopy(word)
    result["B"][START:STOP] = [[FRAME, d, [s]] for d, s in operations]
    result["C"] = cleanup(result)
    return result


def scalar_events(word):
    """Independent literal COPY/ADD/ERASE stream, including all scatter reads."""
    n = 2 * word["v"] + word["R"]
    events = []
    for section in ("D", "A", "scatter", "B", "C"):
        if section == "scatter":
            for k, source in enumerate(word["ret"]):
                events.append(("COPY", n, source))
                for t, row in enumerate(word["scatter"]):
                    if k in row:
                        events.append(("ADD", word["v"] + t, n))
                events.append(("ERASE", n, source))
        else:
            for _, d, sources in word[section]:
                for s in sources:
                    events.append(("ADD", d, s))
    return events


def endpoint(word):
    """Set-valued symbolic replay, including arbitrary source/target/helper dirt."""
    n = 2 * word["v"] + word["R"]
    values = [{r} for r in range(n)] + [set()]
    opened = False
    for op, d, s in scalar_events(word):
        if op == "ADD":
            values[d].symmetric_difference_update(values[s])
        elif op == "COPY":
            need(not opened, "nested copied scratch")
            values[d] = set(values[s])
            opened = True
        else:
            need(opened, "erase without copy")
            values[d] = set()
            opened = False
    need(not opened and not values[n], "scratch not closed")
    for r in range(n):
        expected = {r, r - word["v"]} if word["v"] <= r < 2 * word["v"] else {r}
        need(values[r] == expected, f"endpoint differs at register {r}")
    return n


def prefixes(word):
    events = scalar_events(word)
    n = 2 * word["v"] + word["R"]
    bounds = []
    for reverse in (False, True):
        values = [1] * (n + 1)
        largest, opened = 1, False
        for op, d, s in reversed(events) if reverse else events:
            if reverse and op != "ADD":
                op = "ERASE" if op == "COPY" else "COPY"
            if op == "ADD":
                values[d] += values[s]
                largest = max(largest, values[d])
            elif op == "COPY":
                need(not opened, "nested positive copy")
                values[d] = values[s]
                opened = True
            else:
                need(opened, "unmatched positive erase")
                values[d] = 0
                opened = False
        need(not opened, "positive copy not closed")
        bounds.append(largest)
    payload = 64 * bounds[0] ** 3 * bounds[1] ** 2
    need(payload < 2 ** 104, "104-bit payload cap exceeded")
    return {"forward": bounds[0], "reverse": bounds[1], "payload": str(payload),
            "payload_bits": payload.bit_length(), "payload_cap_bits": 104}


def paths_and_bill(word, dimensions):
    cur = list(word["start"])
    paths = [[f] for f in cur]
    masks = [set(frame) for frame in word["frames"]]
    paid = Counter()
    copies = []

    def climb(r, f):
        if cur[r] != f:
            need(masks[cur[r]] < masks[f] and dimensions[cur[r]] < dimensions[f],
                 f"illegal frame descent for {r}: {cur[r]}->{f}")
            paid[dimensions[f] - dimensions[cur[r]]] += 1
            paths[r].append(f)
            cur[r] = f

    for section in ("D", "A", "scatter", "B", "C"):
        if section == "scatter":
            copies = [dimensions[cur[r]] for r in word["ret"]]
            paid.update(copies)
        else:
            for f, d, ss in word[section]:
                need(len(set([d] + ss)) == 1 + len(ss), "duplicate gate operands")
                for r in [d] + ss:
                    climb(r, f)
    for r, f in enumerate(word["final"]):
        climb(r, f)
    adds = {key: sum(len(ss) for _, _, ss in word[key]) for key in "DABC"}
    adds["scatter"] = sum(map(len, word["scatter"]))
    return paths, {"additions": adds, "total_additions": sum(adds.values()),
                   "paid_profile": dict(sorted(paid.items())),
                   "rank_mass": sum(d * c for d, c in paid.items()),
                   "copy_ranks": copies, "copies": len(copies), "erasures": len(copies)}


def controls(original, replacement, old, operations, source_checker, dimensions):
    result = {}

    def rejects(name, function):
        try:
            function()
        except (Reject, source_checker.Reject):
            result[name] = "rejected"
        else:
            raise Reject("vacuous control: " + name)

    rejects("omit_preparation", lambda: check_block(old, operations[1:]))
    rejects("omit_final_add", lambda: check_block(old, operations[:-1]))
    # Find an actual noncommuting adjacent exchange, rather than assuming one.
    for i in range(len(operations) - 1):
        swapped = copy.deepcopy(operations)
        swapped[i], swapped[i + 1] = swapped[i + 1], swapped[i]
        if matrix(swapped) != matrix(old):
            break
    else:
        raise Reject("no noncommuting exchange control")
    rejects("reverse_dependent_order", lambda: check_block(old, swapped))
    # Same F2 endpoint, distinct integer map: two identical shears cancel only mod 2.
    neutral = operations + [operations[0], operations[0]]
    endpoint(splice(original, neutral))
    rejects("F2_neutral_pair_is_not_integer_neutral",
            lambda: need(matrix(neutral) == matrix(old), "integer transfer differs"))
    costly = operations + [operations[0], operations[0]] * 7
    endpoint(splice(original, costly))
    rejects("free_gate_accounting", lambda: check_block(old, costly))
    # A genuine shorter integer factorization from rejected search trajectory 588.
    # It passes the forward and length guards, but grows some reverse coefficients.
    reverse_growth = [[36, 80], [44, 84], [44, 36], [71, 44], [94, 21], [55, 51],
                      [55, 64], [55, 71], [51, 94], [51, 102], [44, 26], [71, 26],
                      [26, 55], [21, 26], [80, 102], [80, 21], [84, 71], [21, 94],
                      [26, 51], [26, 36], [84, 94], [71, 51], [84, 64], [94, 55],
                      [51, 44], [84, 102], [102, 94], [44, 102], [64, 51], [36, 44]]
    need(len(reverse_growth) < 31 and matrix(reverse_growth) == matrix(old),
         "reverse-growth control does not reach its intended guard")
    rejects("exact_forward_but_reverse_growth", lambda: check_block(old, reverse_growth))
    omitted = copy.deepcopy(replacement)
    omitted["C"].pop(0)
    rejects("omit_cleanup", lambda: endpoint(omitted))
    stale = copy.deepcopy(replacement)
    stale["C"] = original["C"]
    endpoint(stale)
    stale_h = source_checker.Word(stale).interface()[0]
    need(not stale_h["H4_C_literal_reverse_at_full"], "stale C falsely accepted as literal")
    result["stale_cleanup_endpoint_positive_H4_negative"] = "endpoint passes; H4 rejects"
    descent = copy.deepcopy(replacement)
    descent["B"][START][0] = 0
    rejects("frame_zero_descent", lambda: paths_and_bill(descent, dimensions))
    return result


def run(out, certificate_path=HERE / "candidate.json"):
    need(not out.exists(), "output path already exists")
    for path, expected in PINS.items():
        need(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected,
             "source digest differs: " + path)
    original = json.loads(gzip.decompress((ROOT / SOURCE).read_bytes()))
    certificate = json.loads(certificate_path.read_text())
    # Bind the frozen research claims. Search regeneration separately checks the
    # trajectory counts; these constants alone are not an optimality certificate.
    for key, expected in {
        "base_commit": "91a2094f2e022930069e8cfdc810a3ea1b81cd09",
        "assignment_seed": 5, "search_seed": 5, "phase": "B",
        "source": SOURCE,
        "completed_trajectories": 1833, "exact_factorizations": 372,
        "requested_trajectories": 5000, "selected_attempt_zero_based": 1832,
        "status": "strict_forward_improvement_reverse_dominated",
        "reverse_positive_entrywise_dominated": True,
    }.items():
        need(certificate[key] == expected, "frozen certificate metadata differs: " + key)
    need(sum(certificate["length_histogram"].values()) == 372, "search histogram count differs")
    need(certificate["source_sha256"] == PINS[SOURCE], "certificate source pin differs")
    need((certificate["frame"], certificate["start"], certificate["stop"], certificate["wires"])
         == (FRAME, START, STOP, WIRES), "certificate object differs")
    old = pairs(original["B"][START:STOP])
    operations = certificate["operations"]
    local = check_block(old, operations)
    need(certificate["candidate_ops"] == [[FRAME, d, [s]] for d, s in operations],
         "certificate program aliases disagree")
    need(certificate["original_ops"] == original["B"][START:STOP], "old program differs")
    need(certificate["forward_transfer"] == local["ordered_forward_integer_transfer"] and
         certificate["candidate_reverse_positive_transfer"] == local["positive_reverse_after"] and
         certificate["original_reverse_positive_transfer"] == local["positive_reverse_before"],
         "certificate matrix differs")
    need(certificate["candidate_gate_count"] == len(operations) and
         certificate["original_gate_count"] == len(old), "certificate gate bill differs")
    replacement = splice(original, operations)
    need(all(original[k] == replacement[k] for k in original if k not in ("B", "C")),
         "unrelated word field differs")
    spec = importlib.util.spec_from_file_location("pinned_xcheck", ROOT / CHECKER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    receipts = {}
    all_paths = []
    for name, word in (("baseline", original), ("replacement", replacement)):
        checker, labels, full, hypotheses, conclusion, _ = module.check(word)
        need(all(hypotheses.values()) and all(conclusion.values()), "source interface rejects")
        columns = endpoint(word)
        paths, bill = paths_and_bill(word, checker.fdim)
        all_paths.append(paths)
        receipts[name] = {"word_content_sha256": digest(word), "labels": labels,
                          "columns": columns, "hypotheses": hypotheses, "conclusion": conclusion,
                          "bill": bill, "prefix": prefixes(word), "frame_paths_sha256": digest(paths)}
    need(all_paths[0] == all_paths[1], "per-register frame paths differ")
    b, c = receipts["baseline"], receipts["replacement"]
    for key in ("paid_profile", "rank_mass", "copy_ranks", "copies", "erasures"):
        need(b["bill"][key] == c["bill"][key], "paid bill differs: " + key)
    need(b["bill"]["total_additions"] - c["bill"]["total_additions"] == 2 * (len(old) - len(operations)),
         "complete cleanup bill differs")
    need(c["prefix"]["forward"] <= b["prefix"]["forward"] and
         c["prefix"]["reverse"] <= b["prefix"]["reverse"], "complete prefix bound grew")
    control_receipt = controls(original, replacement, old, operations, module, checker.fdim)
    # PR904's exact published three-gate rewrite is separately accounted on this block.
    comparison = copy.deepcopy(old)
    need(comparison[36:39] == [[21, 55], [21, 94], [94, 55]], "PR904 comparison source differs")
    comparison[36:39] = [[94, 55], [21, 94]]
    need(matrix(comparison) == matrix(old), "PR904 comparison integer map differs")
    prior_certificate = json.loads((ROOT / PRIOR).read_text())
    need(prior_certificate["registers"] == WIRES and prior_certificate["slice"] == [START, STOP],
         "PR844 object differs")
    prior_ops = [[WIRES[d], WIRES[s]] for d, s in prior_certificate["operations"]]
    need(len(prior_ops) == 31 and matrix(prior_ops) == matrix(old), "PR844 identity differs")
    prior_word = splice(original, prior_ops)
    endpoint(prior_word)
    prior_reverse = matrix(prior_ops[::-1])
    old_factor = matrix(old[:20])
    need(all(matrix(operations[:i]) != old_factor for i in range(len(operations) + 1)),
         "candidate only reschedules the original fixed factor boundary")
    receipt = {
        "status": "PASS_R439_FRAME520", "base_commit": "91a2094f2e022930069e8cfdc810a3ea1b81cd09",
        "source_pins": PINS, "candidate_sha256": digest(certificate), "local": local,
        **receipts, "controls": control_receipt,
        "comparison_PR904": {"head": "883a0bdf7792693e57c16be660824b57aacfbe05",
                             "block_additions": len(comparison),
                             "additional_complete_saving": 2 * (len(comparison) - len(operations))},
        "comparison_PR844": {"head": "dee2c7d506312d2e555a59fb0916c161b4e64028",
                             "block_additions": len(prior_ops), "prefix": prefixes(prior_word),
                             "additional_complete_saving": 2 * (len(prior_ops) - len(operations)),
                             "no_candidate_prefix_equals_original_first_factor": True,
                             "reverse_matrix_decreases": sum(a < b for ar, br in zip(local["positive_reverse_after"], prior_reverse) for a, b in zip(ar, br)),
                             "reverse_matrix_increases": sum(a > b for ar, br in zip(local["positive_reverse_after"], prior_reverse) for a, b in zip(ar, br))},
        "scope": "finite exact block and whole-word checks; unchanged paid profile; no new kappa",
    }
    out.mkdir(parents=True, exist_ok=False)
    for name, word in (("baseline", original), ("replacement", replacement)):
        (out / (name + ".json.gz")).write_bytes(gzip.compress(canonical(word), mtime=0))
    (out / "receipt.json").write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--certificate", type=Path, default=HERE / "candidate.json")
    args = parser.parse_args()
    out = args.out or Path(tempfile.mkdtemp(prefix="r439-frame520-")) / "replay"
    receipt = run(out, args.certificate)
    a, b = receipt["baseline"]["bill"], receipt["replacement"]["bill"]
    local = receipt["local"]
    print(f"PASS_R439_FRAME520 block={local['before']}->{local['after']} ADDs={a['total_additions']}->{b['total_additions']} "
          f"columns=661 rank_mass={b['rank_mass']} controls={len(receipt['controls'])} no_new_kappa")
    print("Evidence:", out)


if __name__ == "__main__":
    main()
