#!/usr/bin/env python3
"""Invoice a seed-7 ADD-greedy H2-sem matching that dominates PR1805's seed-42 invoice.

Answers PR1805 open question 1: a different disjoint matching lowers F while
keeping (and slightly improving) the ADD saving. No new kappa. Apache-2.0.
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
SEED_BASELINE = 42
SEED_IMPROVED = 7
PROFILE = {1: 1323, 2: 1342, 3: 79, 4: 44, 5: 102, 6: 11, 7: 19}
BASE_BILL = {
    "native_ADDs": 24305,
    "D_adds": 18085,
    "F": 49347,
    "B": 1113070,
    "local_bits": 93,
    "nine_stage_bits": 177,
}
MATCH42_BILL = {
    "native_ADDs": 18074,
    "D_adds": 11854,
    "F": 75381,
    "B": 1196402,
    "local_bits": 95,
    "nine_stage_bits": 180,
}
MATCH7_BILL = {
    "native_ADDs": 18060,
    "D_adds": 11840,
    "F": 73805,
    "B": 1187790,
    "local_bits": 95,
    "nine_stage_bits": 180,
}
# First 50 pairs of the seed-7 matching.
PREFIX50_BILL = {
    "native_ADDs": 21556,
    "D_adds": 15336,
    "F": 56603,
    "B": 1113070,
    "local_bits": 94,
    "nine_stage_bits": 178,
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load_word():
    return json.loads(gzip.decompress(WORD.read_bytes()))


def load_checker():
    spec = importlib.util.spec_from_file_location("r439_xcheck_matching_f", CHECKER)
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
    """PR848 oriented-pair census and ADD-greedy matching with stated shuffle seed."""
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
        "seed": seed,
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


def invoice_word(name, w, expected):
    bill = literal_bounds(w)
    need(bill == expected, name + " bill mismatch: " + json.dumps(bill))
    need(bill["local_bits"] <= 104 and bill["nine_stage_bits"] <= 192,
         name + " precision guard failed")
    return bill


def check_profile(mod, name, w, expect_h2, expect_k):
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
    return own["profile"]


def main():
    write = "--write" in sys.argv
    check_pins()
    word = load_word()
    mod = load_checker()

    _w, _g, _f, hyp0, con0, _p = mod.check(word)
    need(all(hyp0.values()) and all(con0.values()), "baseline H1-H5 / U-J-K-C failed")

    pairs42, census42 = nominate_d(word, SEED_BASELINE)
    pairs7, census7 = nominate_d(word, SEED_IMPROVED)

    need(census42["operands"] == 430, "operand census drift")
    need(census42["oriented_pairs"] == 184470, "oriented-pair census drift")
    need(census42["positive_pairs"] == 41404, "positive-pair census drift")
    need(census42["best_pair"] == [277, 434] and census42["best_saving"] == 65, "best pair drift")
    need(census42["matching_pairs"] == 205 and census42["matching_saving"] == 6231,
         "seed-42 matching drift")
    need(census7["matching_pairs"] == 208 and census7["matching_saving"] == 6245,
         "seed-7 matching drift")
    need(census7["best_saving"] == 65, "seed-7 best saving drift")
    # Tie-break among saving=65 pairs is seed-dependent; require the PR848
    # champion pair is present in the seed-7 matching.
    need([277, 434] in pairs7, "seed-7 matching omits champion pair 277->434")

    set42 = {tuple(p) for p in pairs42}
    set7 = {tuple(p) for p in pairs7}
    need(set42 != set7, "seed-7 matching equals seed-42 pair set")
    need(len(set42 & set7) == 150, "unexpected pair-set overlap")

    wrap42 = construct_d(word, pairs42)
    wrap7 = construct_d(word, pairs7)
    prefix50 = construct_d(word, pairs7[:50])

    base_n = semantic_n(word["D"], word["v"], word["R"])
    need(semantic_n(wrap42["D"], word["v"], word["R"]) == base_n, "seed-42 semantic N changed")
    need(semantic_n(wrap7["D"], word["v"], word["R"]) == base_n, "seed-7 semantic N changed")
    need(sum(bin(x).count("1") for x in base_n) == 18085, "baseline N weight drift")

    h2sem_shape(word)
    h2sem_shape(wrap42)
    h2sem_shape(wrap7)

    base_paths = frame_paths(word)
    need(frame_paths(wrap42) == base_paths and frame_paths(wrap7) == base_paths,
         "frame paths changed")

    want = [{i, i - word["v"]} if word["v"] <= i < 2 * word["v"] else {i}
            for i in range(2 * word["v"] + word["R"])]
    for name, w in (("base", word), ("match42", wrap42), ("match7", wrap7)):
        for reverse in (False, True):
            need(literal_rows(w, reverse) == want,
                 "%s complete boundary (%s)" % (name, "reverse" if reverse else "forward"))

    prefix_bill = literal_bounds(prefix50)
    if write:
        print("PREFIX50_BILL =", json.dumps(prefix_bill))
    else:
        need(prefix_bill == PREFIX50_BILL, "prefix50 bill mismatch: " + json.dumps(prefix_bill))

    bills = {
        "base": invoice_word("base", word, BASE_BILL),
        "match42": invoice_word("match42", wrap42, MATCH42_BILL),
        "match7": invoice_word("match7", wrap7, MATCH7_BILL),
        "prefix50_seed7": prefix_bill,
    }
    need(prefix_bill["local_bits"] <= 104 and prefix_bill["nine_stage_bits"] <= 192,
         "prefix50 precision guard failed")

    need(bills["match42"]["native_ADDs"] - bills["base"]["native_ADDs"] == -6231,
         "seed-42 ADD delta")
    need(bills["match7"]["native_ADDs"] - bills["base"]["native_ADDs"] == -6245,
         "seed-7 ADD delta")
    need(bills["match7"]["native_ADDs"] < bills["match42"]["native_ADDs"],
         "seed-7 must strictly improve ADD count")
    need(bills["match7"]["F"] < bills["match42"]["F"],
         "seed-7 must strictly lower F")
    need(bills["match7"]["B"] < bills["match42"]["B"],
         "seed-7 must strictly lower B")
    need(bills["prefix50_seed7"]["native_ADDs"] > bills["match7"]["native_ADDs"],
         "prefix50 ADD not worse than full")
    need(bills["prefix50_seed7"]["F"] < bills["match7"]["F"],
         "prefix50 F not below full")

    for name, w, expect_h2, expect_k in (
        ("base", word, True, True),
        ("match42", wrap42, False, False),
        ("match7", wrap7, False, False),
    ):
        check_profile(mod, name, w, expect_h2, expect_k)

    for w in (wrap42, wrap7):
        for key in word:
            if key != "D":
                need(w[key] == word[key], "non-D field changed: " + key)

    rejected = []

    unrestored = copy.deepcopy(wrap7)
    del unrestored["D"][-1]
    try:
        semantic_n(unrestored["D"], word["v"], word["R"])
        raise ValueError("unrestored helper temp accepted")
    except ValueError as exc:
        need("helper restoration" in str(exc), "unexpected unrestored failure")
        rejected.append("unrestored_helper_temp")

    a = wrap7["D"][0][1]
    b = wrap7["D"][0][2][0]
    other = next(h for h in range(2 * word["v"], 2 * word["v"] + word["R"]) if h not in (a, b))
    wrong_restore = copy.deepcopy(wrap7)
    wrong_restore["D"][-1] = [0, a, [other]]
    failed = False
    try:
        semantic_n(wrong_restore["D"], word["v"], word["R"])
    except ValueError as exc:
        need("helper restoration" in str(exc), "unexpected wrong-restore failure")
        failed = True
    need(failed, "wrong restore operand accepted")
    rejected.append("wrong_restore_operand")

    target = word["D"][0][1]
    helper = wrap7["D"][0][2][0]
    feedback = copy.deepcopy(word)
    feedback["D"] = [[0, helper, [target]]] + [list(g) for g in word["D"]] + [[0, helper, [target]]]
    try:
        h2sem_shape(feedback)
        raise ValueError("target-feedback wrap accepted")
    except ValueError as exc:
        need("target feeds helper" in str(exc), "unexpected feedback failure")
        rejected.append("target_feeds_helper")

    source_read = copy.deepcopy(word)
    source_read["D"] = [[0, a, [0]]] + [list(g) for g in word["D"]] + [[0, a, [0]]]
    try:
        h2sem_shape(source_read)
        raise ValueError("source-read wrap accepted")
    except ValueError as exc:
        need("D reads a source" in str(exc), "unexpected source-read failure")
        rejected.append("source_reads_in_D")

    rejected.append("prefix50_not_dominating_full")
    rejected.append("seed42_ne_seed7_pairset")

    mutated = copy.deepcopy(wrap7)
    body_idx = 208
    dst, srcs = mutated["D"][body_idx][1], list(mutated["D"][body_idx][2])
    need(srcs, "empty body gate")
    if len(srcs) > 1:
        srcs = srcs[1:]
    else:
        srcs = srcs + [helper]
    mutated["D"][body_idx] = [0, dst, sorted(set(srcs))]
    need(semantic_n(mutated["D"], word["v"], word["R"]) != base_n, "body mutation did not change N")
    rejected.append("mutated_body_changes_N")
    need(len(rejected) == 7, "expected seven controls")

    deltas = {
        "add_saving_lift": MATCH7_BILL["native_ADDs"] - MATCH42_BILL["native_ADDs"],
        "F_lift": MATCH7_BILL["F"] - MATCH42_BILL["F"],
        "B_lift": MATCH7_BILL["B"] - MATCH42_BILL["B"],
        "pairs_lift": census7["matching_pairs"] - census42["matching_pairs"],
        "pair_overlap": len(set42 & set7),
    }
    need(deltas["add_saving_lift"] == -14, "ADD lift drift")
    need(deltas["F_lift"] == -1576, "F lift drift")
    need(deltas["B_lift"] == -8612, "B lift drift")
    need(deltas["pairs_lift"] == 3, "pair-count lift drift")

    matching_path = HERE / "MATCHING7.json"
    matching_blob = {
        "seed": SEED_IMPROVED,
        "pairs": pairs7,
        "saving": 6245,
        "pair_count": 208,
    }
    if write or not matching_path.exists():
        matching_path.write_text(json.dumps(matching_blob, indent=2) + "\n", encoding="utf-8")
    else:
        frozen_m = json.loads(matching_path.read_text(encoding="utf-8"))
        need(frozen_m == matching_blob, "MATCHING7.json mismatch")
    matching_sha = hashlib.sha256(matching_path.read_bytes()).hexdigest()

    report = {
        "status": "PASS_H2SEM_MATCHING_F_INVOICE",
        "task_id": "bit-helper-contract",
        "base_commit": "0b1cccf86e2f5132ed286a26ef0a681a495740ea",
        "columns": 2 * word["v"] + word["R"],
        "census42": census42,
        "census7": census7,
        "bills": bills,
        "deltas_7_minus_42": deltas,
        "paid_profile": {str(k): PROFILE[k] for k in sorted(PROFILE)},
        "rank_mass": 5129,
        "h2sem": {
            "shape": True,
            "semantic_N_equals_baseline": True,
            "syntactic_H2_K": {
                "base": {"H2": True, "K_equals_D": True},
                "match42": {"H2": False, "K_equals_D": False},
                "match7": {"H2": False, "K_equals_D": False},
            },
        },
        "controls": rejected,
        "kappa_claim": "none",
        "new_kappa": False,
        "matching7": {
            "path": "MATCHING7.json",
            "sha256": matching_sha,
            "pair_count": 208,
            "saving": 6245,
        },
    }

    certificate = HERE / "CERTIFICATE.json"
    if write or not certificate.exists():
        certificate.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        if write:
            print("WROTE_CERTIFICATE", certificate)
    else:
        frozen = json.loads(certificate.read_text(encoding="utf-8"))
        need(report == frozen, "certificate mismatch")

    print(
        "PASS_H2SEM_MATCHING_F_INVOICE "
        "seed42_pairs=205 adds=24305->18074 F=75381 "
        "seed7_pairs=208 adds=24305->18060 F=73805 "
        "delta_adds=-14 delta_F=-1576 "
        "profile_mass=5129 columns=%d controls=%d no_new_kappa"
        % (report["columns"], len(rejected))
    )
    return report


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001 - surface exact verifier failure
        print("FAIL_H2SEM_MATCHING_F_INVOICE:", exc, file=sys.stderr)
        raise
