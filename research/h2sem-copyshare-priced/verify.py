#!/usr/bin/env python3
"""Price PR848 helper-sharing wraps under the PR1194 H2-sem contract.

Finite bit construction and paid invoice under a replacement interface;
no new kappa. Apache-2.0.
"""
from __future__ import annotations

import copy
import gzip
import hashlib
import importlib.util
import itertools
import json
import random
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = ROOT / "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
CHECKER = ROOT / "research/e8-bit-p111-tuned/code/xcheck_p.py"
SEED = 42
PROFILE = {1: 1323, 2: 1342, 3: 79, 4: 44, 5: 102, 6: 11, 7: 19}
BASE_BILL = {
    "native_ADDs": 24305,
    "D_adds": 18085,
    "F": 49347,
    "B": 1113070,
    "local_bits": 93,
    "nine_stage_bits": 177,
}
SINGLE_BILL = {
    "native_ADDs": 24240,
    "D_adds": 18020,
    "F": 50535,
    "B": 1113070,
    "local_bits": 94,
    "nine_stage_bits": 177,
}
MATCH_BILL = {
    "native_ADDs": 18074,
    "D_adds": 11854,
    "F": 75381,
    "B": 1196402,
    "local_bits": 95,
    "nine_stage_bits": 180,
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def load_word():
    return json.loads(gzip.decompress(WORD.read_bytes()))


def load_checker():
    spec = importlib.util.spec_from_file_location("r439_xcheck_priced", CHECKER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_pins():
    pins = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    need(pins["base_commit"] == "0b1cccf86e2f5132ed286a26ef0a681a495740ea", "unexpected base")
    for item in pins["files"]:
        digest = hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest()
        need(digest == item["sha256"], "source pin mismatch: " + item["path"])


def nominate_d(word, seed):
    """Exact PR848 oriented-pair census and seed-42 greedy matching."""
    v, ret = word["v"], set(word["ret"])
    rows = [set(g[2]) for g in word["D"]]
    pool = sorted(set.union(*rows) - ret - set(range(2 * v)))
    need(min(pool) >= 2 * v, "D reads a non-helper")
    scored = []
    for a, b in itertools.permutations(pool, 2):
        saving = sum((1 if b in row else -1) for row in rows if a in row) - 2
        if saving > 0:
            scored.append((saving, a, b))
    random.Random(seed).shuffle(scored)
    scored.sort(key=lambda item: -item[0])
    chosen, used, total = [], set(), 0
    for saving, a, b in scored:
        if a not in used and b not in used:
            chosen.append([a, b])
            used.update((a, b))
            total += saving
    return chosen, {
        "operands": len(pool),
        "oriented_pairs": len(pool) * (len(pool) - 1),
        "positive_pairs": len(scored),
        "best_saving": scored[0][0],
        "best_pair": [scored[0][1], scored[0][2]],
        "matching_pairs": len(chosen),
        "matching_saving": total,
    }


def construct_d(word, pairs):
    """PR848 helper-temp wrap: prep, rewritten D body, reverse restore."""
    v, ret = word["v"], set(word["ret"])
    rows_pool = set().union(*(set(g[2]) for g in word["D"]))
    flat = [r for pair in pairs for r in pair]
    need(all(len(pair) == 2 for pair in pairs), "malformed pair")
    need(len(flat) == len(set(flat)), "pairs must be disjoint")
    need(all(r >= 2 * v and r not in ret for r in flat) and set(flat) <= rows_pool,
         "temps must be non-retained D-operand helpers")
    pre = [[0, a, [b]] for a, b in pairs]
    body = []
    for frame, dst, srcs in word["D"]:
        need(frame == 0 and v <= dst < 2 * v, "D gate not frame-zero target write")
        row = set(srcs)
        for a, b in pairs:
            if a in row:
                row.symmetric_difference_update({b})
        body.append([frame, dst, sorted(row)])
    result = copy.deepcopy(word)
    result["D"] = pre + body + list(reversed(pre))
    return result


def stream(w):
    out = [("add", d, s) for sec in ("D", "A") for _, d, ss in w[sec] for s in ss]
    tmp = 2 * w["v"] + w["R"]
    for j, centre in enumerate(w["ret"]):
        out.append(("copy", tmp, centre))
        out += [("add", w["v"] + i, tmp) for i, ss in enumerate(w["scatter"]) if j in ss]
        out.append(("erase", tmp, centre))
    out += [("add", d, s) for sec in ("B", "C") for _, d, ss in w[sec] for s in ss]
    return out


def flip(kind):
    return {"copy": "erase", "erase": "copy"}.get(kind, kind)


def literal_rows(w, reverse=False):
    n = 2 * w["v"] + w["R"]
    rows = [{i} for i in range(n)] + [set()]
    ins = stream(w)
    for kind, d, s in (reversed(ins) if reverse else ins):
        kind = flip(kind) if reverse else kind
        if kind == "add":
            rows[d] ^= rows[s]
        elif kind == "copy":
            need(not rows[d], "copy into a live temporary")
            rows[d] = set(rows[s])
        else:
            need(rows[d] == rows[s], "erase of a changed copy")
            rows[d] = set()
    need(not rows[-1], "temporary not erased")
    return rows[:-1]


def literal_bounds(w):
    peaks = []
    for reverse in (False, True):
        val = [1] * (2 * w["v"] + w["R"] + 1)
        peak = 1
        ins = stream(w)
        for kind, d, s in (reversed(ins) if reverse else ins):
            kind = flip(kind) if reverse else kind
            val[d] = val[d] + val[s] if kind == "add" else (val[s] if kind == "copy" else 0)
            peak = max(peak, val[d])
        peaks.append(peak)
    F, B = peaks
    return {
        "native_ADDs": sum(k == "add" for k, _, _ in stream(w)),
        "D_adds": sum(len(g[2]) for g in w["D"]),
        "F": F,
        "B": B,
        "local_bits": (64 * F**3 * B**2).bit_length(),
        "nine_stage_bits": ((1 << 18) * F**5 * B**4).bit_length(),
    }


def frame_paths(w):
    fs = [frozenset(f) for f in w["frames"]]
    ps = [[f] for f in w["start"]]
    for sec in "DABC":
        for f, d, ss in w[sec]:
            for r in (d, *ss):
                if ps[r][-1] != f:
                    need(fs[ps[r][-1]] < fs[f], "illegal frame move")
                    ps[r].append(f)
    for r, f in enumerate(w["final"]):
        if ps[r][-1] != f:
            need(fs[ps[r][-1]] < fs[f], "illegal final move")
            ps[r].append(f)
    return ps


def semantic_n(gates, v, R):
    """Independent bit-column oracle for D; no row-engine import."""
    n = 2 * v + R
    flat = [(d, s) for _, d, ss in gates for s in ss]
    mask = (1 << v) - 1
    N = [0] * v
    for j in range(n):
        state = 1 << j
        for d, s in flat:
            if (state >> s) & 1:
                state ^= 1 << d
        delta = state ^ (1 << j)
        if j < 2 * v:
            need(delta == 0, "source/target column changed in D")
        else:
            need(delta & ~(mask << v) == 0, "helper restoration failed")
            for t in range(v):
                if (delta >> (v + t)) & 1:
                    N[t] |= 1 << (j - 2 * v)
    return N


def h2sem_shape(w):
    """H2-sem conditions 1-2: zero-frame, source-free, no target->helper."""
    v = w["v"]
    for frame, dst, srcs in w["D"]:
        need(frame == 0, "nonzero D frame")
        need(dst >= v, "D writes a source")
        for s in srcs:
            need(s >= v, "D reads a source")
            need(not (v <= s < 2 * v and dst >= 2 * v), "target feeds helper")
            need(dst != s, "self XOR")
    return True


def paid_profile(mod, w):
    dim, _labels, flow, hyp, con, _parts = mod.check(w)
    prof = Counter(dim.fdim[b] - dim.fdim[a] for p in frame_paths(w) for a, b in itertools.pairwise(p))
    prof.update(t["rank"] for t in flow["totals"])
    return {
        "profile": {k: prof[k] for k in sorted(prof)},
        "copy_ranks": [t["rank"] for t in flow["totals"]],
        "hypotheses": hyp,
        "conclusions": con,
    }


def controls(word, single, matching, base_n, mod):
    """Meaningful negative controls; each must fail the stated obligation."""
    rejected = []

    unrestored = copy.deepcopy(single)
    del unrestored["D"][-1]
    try:
        semantic_n(unrestored["D"], word["v"], word["R"])
        raise ValueError("unrestored helper temp accepted")
    except ValueError as exc:
        need("helper restoration" in str(exc), "unexpected unrestored failure")
        rejected.append("unrestored_helper_temp")

    a, b = matching[0]
    other = next(h for h in range(2 * word["v"], 2 * word["v"] + word["R"]) if h not in (a, b))
    wrong_restore = copy.deepcopy(single)
    wrong_restore["D"][-1] = [0, a, [other]]
    failed = False
    try:
        semantic_n(wrong_restore["D"], word["v"], word["R"])
    except ValueError as exc:
        need("helper restoration" in str(exc), "unexpected wrong-restore failure: " + str(exc))
        failed = True
    need(failed, "wrong restore operand accepted")
    rejected.append("wrong_restore_operand")

    feedback = copy.deepcopy(word)
    # Target feeds helper before D body: violates H2-sem condition 2 / H1.
    target, helper = word["D"][0][1], matching[0][1]
    feedback["D"] = [[0, helper, [target]]] + [list(g) for g in word["D"]] + [[0, helper, [target]]]
    try:
        h2sem_shape(feedback)
        raise ValueError("target-feedback wrap accepted by H2-sem shape")
    except ValueError as exc:
        need("target feeds helper" in str(exc), "unexpected feedback failure")
        rejected.append("target_feeds_helper")

    source_read = copy.deepcopy(word)
    source_read["D"] = [[0, matching[0][0], [0]]] + [list(g) for g in word["D"]] + [[0, matching[0][0], [0]]]
    try:
        h2sem_shape(source_read)
        raise ValueError("source-read wrap accepted by H2-sem shape")
    except ValueError as exc:
        need("D reads a source" in str(exc), "unexpected source-read failure")
        rejected.append("source_reads_in_D")

    # Dropping one matching pair's restore breaks N or restoration.
    drop = construct_d(word, matching[:2])
    del drop["D"][-1]
    try:
        semantic_n(drop["D"], word["v"], word["R"])
        raise ValueError("partial matching unrestored accepted")
    except ValueError:
        rejected.append("partial_matching_unrestored")

    # Mutate a body gate destination: changes N.
    mutated = copy.deepcopy(single)
    mutated["D"][1] = [0, mutated["D"][1][1], list(mutated["D"][1][2])]  # keep shape
    # Flip one source bit in first body gate after prep.
    body_idx = 1  # after single prep
    dst, srcs = mutated["D"][body_idx][1], list(mutated["D"][body_idx][2])
    need(srcs, "empty body gate")
    # Remove one source if present else add a helper.
    if len(srcs) > 1:
        srcs = srcs[1:]
    else:
        srcs = srcs + [matching[0][1]]
    mutated["D"][body_idx] = [0, dst, sorted(set(srcs))]
    n = semantic_n(mutated["D"], word["v"], word["R"])
    need(n != base_n, "body mutation did not change N")
    rejected.append("mutated_body_changes_N")

    # Positive control: target-temp +2 wrap remains H2-legal and costs +2.
    legal = copy.deepcopy(word)
    helper = matching[0][1]
    legal["D"] = [[0, target, [helper]]] + [list(g) for g in word["D"]] + [[0, target, [helper]]]
    need(semantic_n(legal["D"], word["v"], word["R"]) == base_n, "target-temp changed N")
    need(sum(len(g[2]) for g in legal["D"]) - sum(len(g[2]) for g in word["D"]) == 2,
         "target-temp cost is not +2")
    hyp = mod.Word(legal).interface()[0]
    need(hyp["H2_D_frame0_targets_from_helpers"] is True, "target-temp lost syntactic H2")
    rejected.append("target_temp_plus2_positive")

    need(len(rejected) == 7, "expected seven controls")
    return rejected


def main():
    check_pins()
    word = load_word()
    mod = load_checker()

    # Baseline must pass the inherited interface completely.
    _w, _g, _f, hyp0, con0, _p = mod.check(word)
    need(all(hyp0.values()) and all(con0.values()), "baseline H1-H5 / U-J-K-C failed")

    matching, census = nominate_d(word, SEED)
    need(census["operands"] == 430, "operand census drift")
    need(census["oriented_pairs"] == 184470, "oriented-pair census drift")
    need(census["positive_pairs"] == 41404, "positive-pair census drift")
    need(census["best_pair"] == [277, 434] and census["best_saving"] == 65, "best pair drift")
    need(census["matching_pairs"] == 205 and census["matching_saving"] == 6231, "matching drift")

    single = construct_d(word, [census["best_pair"]])
    full = construct_d(word, matching)

    base_n = semantic_n(word["D"], word["v"], word["R"])
    single_n = semantic_n(single["D"], word["v"], word["R"])
    full_n = semantic_n(full["D"], word["v"], word["R"])
    need(single_n == base_n and full_n == base_n, "semantic N changed")
    need(sum(bin(x).count("1") for x in base_n) == 18085, "baseline N weight drift")

    h2sem_shape(word)
    h2sem_shape(single)
    h2sem_shape(full)

    base_paths = frame_paths(word)
    need(frame_paths(single) == base_paths and frame_paths(full) == base_paths,
         "frame paths changed")

    want = [{i, i - word["v"]} if word["v"] <= i < 2 * word["v"] else {i}
            for i in range(2 * word["v"] + word["R"])]
    for name, w in (("base", word), ("single", single), ("match", full)):
        for reverse in (False, True):
            need(literal_rows(w, reverse) == want,
                 "%s complete boundary (%s)" % (name, "reverse" if reverse else "forward"))

    bills = {}
    for name, w, expected in (
        ("base", word, BASE_BILL),
        ("single", single, SINGLE_BILL),
        ("match", full, MATCH_BILL),
    ):
        bill = literal_bounds(w)
        need(bill == expected, name + " bill mismatch: " + json.dumps(bill))
        need(bill["local_bits"] <= 104 and bill["nine_stage_bits"] <= 192,
             name + " precision guard failed")
        bills[name] = bill

    need(bills["single"]["native_ADDs"] - bills["base"]["native_ADDs"] == -65, "single ADD delta")
    need(bills["match"]["native_ADDs"] - bills["base"]["native_ADDs"] == -6231, "match ADD delta")

    profiles = {}
    for name, w, expect_h2, expect_k in (
        ("base", word, True, True),
        ("single", single, False, False),
        ("match", full, False, False),
    ):
        own = paid_profile(mod, w)
        need(own["profile"] == PROFILE, name + " paid profile changed")
        need(sum(r * c for r, c in own["profile"].items()) == 5129, name + " rank mass")
        need(own["copy_ranks"] == [7] * 9, name + " COPY ranks")
        need(own["hypotheses"]["H2_D_frame0_targets_from_helpers"] is expect_h2, name + " H2")
        need(own["conclusions"]["K_equals_D"] is expect_k, name + " K")
        for key in ("H1_no_target_feeds_z", "H3_A_z_only_scatter_targets_B_split",
                    "H4_C_literal_reverse_at_full", "H5_V_identity"):
            need(own["hypotheses"][key] is True, name + " " + key)
        for key in ("U_block_form", "J_identity", "C_is_U_inverse"):
            need(own["conclusions"][key] is True, name + " " + key)
        profiles[name] = own["profile"]

    # Non-D fields unchanged.
    for w in (single, full):
        for key in word:
            if key != "D":
                need(w[key] == word[key], "non-D field changed: " + key)

    rejected = controls(word, single, matching, base_n, mod)

    report = {
        "status": "PASS_H2SEM_COPYSHARE_PRICED",
        "assignment_seed": SEED,
        "task_id": "bit-helper-contract",
        "base_commit": "0b1cccf86e2f5132ed286a26ef0a681a495740ea",
        "columns": 2 * word["v"] + word["R"],
        "census": census,
        "bills": bills,
        "paid_profile": {str(k): PROFILE[k] for k in sorted(PROFILE)},
        "rank_mass": 5129,
        "h2sem": {
            "shape": True,
            "semantic_N_equals_baseline": True,
            "syntactic_H2_K": {
                "base": {"H2": True, "K_equals_D": True},
                "single": {"H2": False, "K_equals_D": False},
                "match": {"H2": False, "K_equals_D": False},
            },
        },
        "controls": rejected,
        "kappa_claim": "none",
        "new_kappa": False,
    }
    certificate = HERE / "CERTIFICATE.json"
    if certificate.exists():
        need(report == json.loads(certificate.read_text(encoding="utf-8")),
             "certificate mismatch")
    else:
        certificate.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(
        "PASS_H2SEM_COPYSHARE_PRICED "
        "single=277->434 adds=24305->24240 "
        "matching_pairs=205 adds=24305->18074 "
        "profile_mass=5129 columns=%d controls=%d no_new_kappa"
        % (report["columns"], len(rejected))
    )
    return report


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001 - surface exact verifier failure
        print("FAIL_H2SEM_COPYSHARE_PRICED:", exc, file=sys.stderr)
        raise
