"""Exact premises for joint late-block mixing; standard library, read-only replay.

Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance. Apache-2.0.
Block extraction follows Ali Romman's PR1429, pinned in SOURCES.json.
Global localization, joint boundary and independent checks are new here.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import gzip
import hashlib
from itertools import combinations
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASES = (592, 600, 608, 624, 632, 640, 648, 656, 672, 680, 688, 696)
ARCHIVE = "research/community-frontier1042-audit/selected-replay.tar.gz"
MEMBER = "t16/global/base/providers/gauge44/CANONICAL-WORD.json.gz"
PAYLOAD_HASH = "4ddb29fb9bc6f27e0c0fbfcf19a2a93a3496ad900d0f6d89059d0305c9576c0c"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def basis(values):
    pivots = {}
    for x in values:
        while x:
            p = x.bit_length()
            if p in pivots:
                x ^= pivots[p]
            else:
                pivots[p] = x
                break
    for p in sorted(pivots):
        for q in pivots:
            if q > p and pivots[q] >> (p - 1) & 1:
                pivots[q] ^= pivots[p]
    return tuple(pivots[p] for p in sorted(pivots, reverse=True))


def inside(a, b):
    return len(basis(tuple(a) + tuple(b))) == len(basis(b))


def rank(matrix):
    rows = [list(map(Q, row)) for row in matrix]
    if not rows:
        return 0
    k = 0
    for col in range(len(rows[0])):
        p = next((i for i in range(k, len(rows)) if rows[i][col]), None)
        if p is None:
            continue
        rows[k], rows[p] = rows[p], rows[k]
        d = rows[k][col]
        rows[k] = [v / d for v in rows[k]]
        for i in range(k + 1, len(rows)):
            if rows[i][col]:
                d = rows[i][col]
                rows[i] = [a - d * b for a, b in zip(rows[i], rows[k])]
        k += 1
        if k == len(rows):
            break
    return k


def incident(g):
    need(g[0] in ("add", "scale"), "unknown scalar opcode")
    return g[1:3] if g[0] == "add" else g[1:2]


def scalar(g, rows):
    if g[0] == "add":
        _, dst, src, n, d, _ = g
        rows[dst] = [a + Q(n, d) * b for a, b in zip(rows[dst], rows[src])]
    else:
        _, dst, n, d, _ = g
        rows[dst] = [Q(n, d) * a for a in rows[dst]]


def load_word():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    for pin in pins["files"]:
        if pin["usage"] == "input":
            data = (ROOT / pin["path"]).read_bytes()
            need(hashlib.sha256(data).hexdigest() == pin["sha256"], "source hash mismatch")
    with tarfile.open(ROOT / ARCHIVE, "r:gz") as archive:
        payload = gzip.decompress(archive.extractfile(MEMBER).read())
    need(hashlib.sha256(payload).hexdigest() == PAYLOAD_HASH, "canonical payload mismatch")
    return json.loads(payload)


def frame_states(w):
    f = w["frames"]
    state = list(w["start"])
    for g in w["A"]:
        for r in incident(g):
            need(inside(f[state[r]], f[g[-1]]), "A frame descent")
            state[r] = g[-1]
    states = []
    for g in w["B"]:
        states.append(state.copy())
        for r in incident(g):
            need(inside(f[state[r]], f[g[-1]]), "B frame descent")
            state[r] = g[-1]
    states.append(state)
    return states


def extract(w, states, base):
    helpers = list(range(base, base + 8))
    hs = set(helpers)
    f, gates = w["frames"], w["B"]
    arrivals = [(i, g) for i, g in enumerate(gates)
                if g[0] == "add" and g[1] in hs and g[2] not in hs]
    reads = [(i, g) for i, g in arrivals if len(basis(f[g[-1]])) > 1]
    need(len(reads) == 8 and len({g[1] for _, g in reads}) == 8
         and len({g[2] for _, g in reads}) == 8, "eight independent input slots")
    first = reads[0][0]
    need(reads[-1][0] == first + 7, "input segment is not contiguous")
    correction = [i for i, g in enumerate(gates[:first])
                  if g[0] == "add" and g[1] in hs and g[2] in hs]
    need(correction, "missing correction")
    start = min(correction)
    need(all(i < start for i, g in arrivals if (i, g) not in reads), "extra late input")
    low = [r for r in helpers if len(basis(f[states[start][r]])) == 1]
    high = [r for r in helpers if r not in low]
    need(len(low) == len(high) == 4, "four low and four high helpers required")
    common = basis(f[states[start][high[0]]])
    need(len(common) in (4, 5), "common rank")
    need(all(basis(f[states[start][r]]) == common for r in high), "unequal high frames")
    need(all(inside(f[states[start][r]], common) for r in low), "low outside common")
    need(all(basis(f[gates[i][-1]]) == common for i in correction), "correction frame")
    outputs = [(i, g) for i, g in enumerate(gates) if i >= start and g[0] == "add"
               and g[2] in hs and g[1] not in hs]
    need(len(outputs) == 8 and min(i for i, _ in outputs) > first + 7, "late output segment")
    targets = sorted({g[1] for _, g in outputs})
    need(len(targets) == 4, "four target ports")
    inputs = [g[2] for _, g in reads]
    input_frames = [basis(f[g[-1]]) for _, g in reads]
    entries = [next(i for i, g in outputs if g[1] == r) for r in targets]
    entry_frames = [basis(f[states[i][r]]) for i, r in zip(entries, targets)]
    caps = [basis(f[w["final"][r]]) for r in targets]
    need(all(len(x) in (5, 6) and inside(common, x) for x in input_frames), "input frame")
    need(all(len(x) in (7, 8) for x in entry_frames) and all(len(x) == 8 for x in caps), "target ranks")
    need(all(inside(g, h) for g, h in zip(entry_frames, caps)), "target entry outside cap")
    need(all(not (g[0] == "scale" and g[1] in targets)
             and not (g[0] == "add" and g[2] in targets)
             for g in gates[min(entries):]), "late target used as scratch")
    variables = helpers + inputs
    need(len(set(variables + targets)) == 20, "block register alias")
    rows = {r: [Q(int(i == j)) for i in range(16)] for j, r in enumerate(variables)}
    rows.update({r: [Q(0)] * 16 for r in targets})
    current = {r: basis(f[states[start][r]]) for r in helpers}
    profile = Counter()
    for i, g in enumerate(gates):
        if i >= start and hs.intersection(incident(g)):
            need(set(incident(g)) <= set(rows), "undeclared block wire")
            scalar(g, rows)
            for r in hs.intersection(incident(g)):
                new = basis(f[g[-1]])
                need(inside(current[r], new), "helper descent")
                if len(new) > len(current[r]):
                    profile[len(new) - len(current[r])] += 1
                current[r] = new
    for r in helpers:
        need(len(basis(f[w["final"][r]])) == 9, "helper endpoint not full")
        if len(current[r]) < 9:
            profile[9 - len(current[r])] += 1
    out = [rows[r] for r in targets]
    need(all(row[helpers.index(r)] == 0 for row in out for r in high), "high dirt reaches output")
    q = [row[8:] for row in out]
    need(rank(q) == 4, "Q rank")
    need(all(sum(row[j] != 0 for row in q) == 2 for j in range(8)), "two output demands per input")
    expected = Counter({1: 24, 2: 8, 3: 4}) if len(common) == 4 else Counter({1: 32, 4: 4})
    need(profile == expected, "complete block profile")
    return dict(base=base, helpers=helpers, low=low, high=high, common=list(common),
                first_correction=start, corrections=correction, first_input=first,
                inputs=inputs, input_frames=list(map(list, input_frames)), targets=targets,
                output_entries=entries, target_entries=list(map(list, entry_frames)),
                caps=list(map(list, caps)), Q=[[str(v) for v in row] for row in q],
                R=[[str(row[helpers.index(r)]) for r in low] for row in out],
                profile={str(k): v for k, v in sorted(profile.items())})


def local_premises(block):
    q, fs = block["Q"], block["input_frames"]
    kernel_frames = {}
    projection = Counter()
    spectrum = Counter()
    for mask in range(1, 256):
        cols = [i for i in range(8) if mask >> i & 1]
        r = rank([[row[i] for i in cols] for row in q])
        f = basis(v for i in cols for v in fs[i])
        spectrum[(len(cols), len(f), r)] += 1
        if len(cols) <= 4:
            comp = [i for i in range(8) if i not in cols]
            proj = len(cols) - 4 + rank([[row[i] for i in comp] for row in q])
            need(proj >= (3 * len(cols) + 3) // 4, "kernel projection too small")
            projection[(len(cols), proj)] += 1
        if r < len(cols):
            need(len(f) >= 7, "kernel below rank seven")
            if len(f) == 7:
                kernel_frames[f] = True
    return {"kernels": [list(f) for f in sorted(kernel_frames)],
            "spectrum": [list(k) + [v] for k, v in sorted(spectrum.items())],
            "projections": [list(k) + [v] for k, v in sorted(projection.items())]}


def global_premises(blocks, local):
    inputs = [(b["base"], r, f) for b in blocks for r, f in zip(b["inputs"], b["input_frames"])]
    targets = [(b["base"], r, f) for b in blocks for r, f in zip(b["targets"], b["caps"])]
    need(len({r for _, r, _ in inputs}) == 96, "global input alias")
    need(len({r for _, r, _ in targets}) == 48, "global target alias")
    main = {r for b in blocks for r in b["helpers"] + b["inputs"]}
    need(not main.intersection(r for _, r, _ in targets), "output aliases a source/helper")
    for (_, _, f), (_, _, g) in combinations(inputs, 2):
        need(not inside(f, g) and not inside(g, f), "global input antichain")
    for (_, _, f), (_, _, g) in combinations(targets, 2):
        need(basis(f) != basis(g), "global target caps distinct")
    high_tests = 0
    for b in blocks:
        for owner, _, f in inputs:
            if owner != b["base"]:
                need(not inside(b["common"], f), "foreign high-frame access")
                high_tests += 1
    for _, _, f in inputs:
        for b in blocks:
            for g in b["target_entries"]:
                need(len(basis(f + g)) >= 8, "global output below rank eight")
    kernel_records = []
    for b, result in zip(blocks, local):
        for f in result["kernels"]:
            contained = [(owner, r, len(g)) for owner, r, g in inputs if inside(g, f)]
            eligible = [r for _, r, g in targets if inside(f, g)]
            need(all(owner == b["base"] for owner, _, _ in contained), "foreign input in kernel frame")
            need(all(dim == 5 for _, _, dim in contained), "rank-six input in kernel frame")
            need(len(eligible) <= 1, "kernel frame reaches two global outputs")
            kernel_records.append({"owner": b["base"], "frame": f,
                                   "contained_inputs": [r for _, r, _ in contained],
                                   "eligible_targets": eligible})
    need(len({tuple(k["frame"]) for k in kernel_records}) == len(kernel_records), "shared kernel frame")
    return {"input_pairs": len(inputs) * (len(inputs) - 1) // 2,
            "foreign_high_tests": high_tests, "input_target_tests": len(inputs) * len(targets),
            "kernel_frames": kernel_records}


def boundary(w, states, blocks):
    """All corrections commute to one actual, full-rank main-array boundary."""
    cut = min(b["first_input"] for b in blocks)
    helpers = {r for b in blocks for r in b["helpers"]}
    inputs = {r for b in blocks for r in b["inputs"]}
    need(len(helpers | inputs) == 192, "joint boundary aliases")
    removed = {i for b in blocks for i in b["corrections"]}
    earliest = min(b["first_correction"] for b in blocks)
    for b in blocks:
        hs = set(b["helpers"])
        need(all(basis(w["frames"][states[earliest][r]]) ==
                 basis(w["frames"][states[b["first_correction"]][r]]) for r in hs),
             "helper not ready at joint entry")
        for i in range(b["first_correction"], b["first_input"]):
            g = w["B"][i]
            if hs.intersection(incident(g)):
                need(i in b["corrections"] and set(incident(g)) <= hs, "correction crosses exterior event")
        for r, f in zip(b["inputs"], b["input_frames"]):
            need(basis(w["frames"][states[cut][r]]) == tuple(f), "input not ready at common cut")
            need(all(g[1] != r for g in w["B"][cut:b["first_input"]]), "input changes before own read")
    prefix = w["A"] + w["cut"] + [g for i, g in enumerate(w["B"][:cut]) if i not in removed]
    determinant = Q(1)
    for g in prefix:
        need(all(0 <= r < len(w["start"]) for r in incident(g)), "private array in boundary prefix")
        if g[0] == "add":
            need(g[1] != g[2] and g[4] != 0, "noninvertible ADD in prefix")
        else:
            need(g[2] != 0 and g[3] != 0, "noninvertible SCALE in prefix")
            determinant *= Q(g[2], g[3])
    need(determinant != 0, "singular joint prefix")
    return {"B_cut": cut, "main_arrays": len(w["start"]), "independent_coordinates": 192,
            "prefix_gates": len(prefix), "deferred_corrections": sorted(removed),
            "prefix_determinant": str(determinant), "registers": sorted(helpers | inputs)}


def controls(w, states, blocks, local):
    names = []
    def rejects(name, run, expected):
        try:
            run()
        except ValueError as error:
            need(expected in str(error), name + " rejected for wrong reason: " + str(error))
        else:
            raise ValueError(name + " incorrectly passed")
        names.append(name)
    bad = deepcopy(blocks)
    bad[1]["input_frames"][0] = bad[0]["input_frames"][0]
    rejects("foreign_equal_input", lambda: global_premises(bad, local), "antichain")
    bad = deepcopy(blocks)
    bad[1]["common"] = bad[0]["common"]
    rejects("high_information_can_escape", lambda: global_premises(bad, local), "high-frame")
    bad = deepcopy(blocks)
    bad[1]["caps"][0] = bad[0]["caps"][0]
    rejects("shared_output_cap", lambda: global_premises(bad, local), "caps distinct")
    bad = deepcopy(blocks)
    bad[1]["target_entries"][0] = bad[0]["input_frames"][0]
    rejects("early_output_access", lambda: global_premises(bad, local), "below rank eight")
    bad = deepcopy(blocks)
    f = local[0]["kernels"][0]
    old_caps = {tuple(basis(cap)) for b in bad for cap in b["caps"]}
    extensions = []
    for v in range(1, 512):
        cap = basis(f + [v])
        if len(cap) == 8 and cap not in old_caps and cap not in extensions:
            extensions.append(cap)
    need(len(extensions) >= 2, "kernel-output control has no witness")
    bad[1]["caps"][:2] = [list(c) for c in extensions[:2]]
    rejects("two_global_readers_for_kernel", lambda: global_premises(bad, local), "two global outputs")
    bad = deepcopy(blocks[0])
    for row in bad["Q"]:
        row[0] = "0"
    rejects("zero_output_column", lambda: local_premises(bad), "kernel below rank seven")
    bad = deepcopy(w)
    bad["B"][1054] = ["add", blocks[1]["inputs"][0], 0, 1, 1, bad["B"][1054][-1]]
    rejects("asynchronous_input_mutation", lambda: boundary(bad, states, blocks), "input changes")
    bad = deepcopy(w)
    i = blocks[0]["corrections"][0]
    bad["B"][i] = ["add", blocks[0]["helpers"][0], 0, 1, 1, bad["B"][i][-1]]
    rejects("noncommuting_deferred_correction", lambda: boundary(bad, states, blocks), "exterior event")
    bad = deepcopy(w)
    bad["A"][0] = ["scale", 0, 0, 1, bad["A"][0][-1]]
    rejects("singular_prefix", lambda: boundary(bad, states, blocks), "noninvertible SCALE")
    bad = deepcopy(w)
    bad["final"][BASES[0]] = w["start"][BASES[0]]
    rejects("unpaid_helper_restoration", lambda: extract(bad, states, BASES[0]), "endpoint not full")
    return names


def compute():
    w = load_word()
    states = frame_states(w)
    blocks = [extract(w, states, b) for b in BASES]
    local = [local_premises(b) for b in blocks]
    global_result = global_premises(blocks, local)
    joint = boundary(w, states, blocks)
    total = Counter()
    for b in blocks:
        total.update({int(k): v for k, v in b["profile"].items()})
    need(total == Counter({1: 328, 2: 56, 3: 28, 4: 20}), "total moment profile")
    return {"schema_version": 1, "status": "PASS_CROSS_BLOCK_LOCALITY_PREMISES",
            "source_payload_sha256": PAYLOAD_HASH, "blocks": blocks, "local": local,
            "global": global_result, "boundary": joint,
            "profile": {str(k): v for k, v in sorted(total.items())},
            "controls": controls(w, states, blocks, local)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", action="store_true")
    parser.add_argument("--certificate", type=Path, default=HERE / "CERTIFICATE.json")
    args = parser.parse_args()
    result = compute()
    if args.record:
        args.certificate.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        need(json.loads(args.certificate.read_text()) == result, "saved certificate mismatch")
    print("PASS_CROSS_BLOCK_LOCALITY_PREMISES blocks=12 inputs=96 ports=48 "
          "input_pairs=4560 foreign_high=1056 output_pairs=4608 kernels=24 controls="
          + str(len(result["controls"])))


if __name__ == "__main__":
    main()
