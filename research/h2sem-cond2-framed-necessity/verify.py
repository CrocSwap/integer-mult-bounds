#!/usr/bin/env python3
"""Framed necessity probe for H2-sem condition 2 on the F4 target-feed wrap.

Complements open PR1782 (admission + F4 boundary probe) and PR1805 (priced
admitted wraps). This package answers whether condition 2 is required for the
framed dirty endpoint on that exact F4 instance.

No new kappa. Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

import copy
import gzip
import hashlib
import importlib.util
import itertools
import json
import random
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD_PATH = ROOT / "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
XCHECK_PATH = ROOT / "research/e8-bit-p111-tuned/code/xcheck_p.py"
SEED = 42
PAIR = [277, 434]
PASS = (
    "PASS_H2SEM_COND2_FRAMED_NECESSITY "
    "pair=277->434 cond2=false endpoint=exact "
    "profile_mass=5129 adds=24305->24374 no_new_kappa"
)


def need(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check_pins() -> dict:
    pins = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    need(pins["base_commit"], "missing base_commit")
    for entry in pins["files"]:
        if entry["usage"] != "input":
            continue
        data = (ROOT / entry["path"]).read_bytes()
        need(sha256(data) == entry["sha256"], "source pin mismatch: " + entry["path"])
    return pins


def load_checker():
    spec = importlib.util.spec_from_file_location("r439_xcheck_p", XCHECK_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def nominate_d(word, seed: int):
    """PR848 oriented-pair census and seed-42 greedy matching."""
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


def construct_c1(word, pairs):
    """PR848 helper-temp wrap (admitted contrast)."""
    pre = [[0, a, [b]] for a, b in pairs]
    back = [[0, a, [b]] for a, b in pairs]
    body = []
    for frame, dst, srcs in word["D"]:
        row = set(srcs)
        for a, b in pairs:
            if a in row:
                row.symmetric_difference_update({b})
        body.append([frame, dst, sorted(row)])
    out = copy.deepcopy(word)
    out["D"] = pre + body + list(reversed(back))
    return out


def construct_f4(word, pair):
    """PR1782 F4: target-feeding-helper wrap closed before the fed target's write."""
    a, _b = pair
    t_reg = word["D"][-1][1]
    k = len(word["D"]) - 1
    need(sum(1 for g in word["D"] if g[1] == t_reg) == 1, "fed target not written exactly once")
    body = []
    for i, g in enumerate(word["D"]):
        row = set(g[2])
        if i < k and a in row:
            row.symmetric_difference_update({t_reg})
        body.append([g[0], g[1], sorted(row)])
    out = copy.deepcopy(word)
    out["D"] = [[0, a, [t_reg]]] + body[:k] + [[0, a, [t_reg]]] + body[k:]
    return out, {"helper": a, "fed_target": t_reg, "close_before_index": k}


def construct_f4_unrestored(word, pair):
    feed, meta = construct_f4(word, pair)
    # Drop the closing restore (second a += t), leaving the prep gate.
    a, t_reg, k = meta["helper"], meta["fed_target"], meta["close_before_index"]
    body = []
    for i, g in enumerate(word["D"]):
        row = set(g[2])
        if i < k and a in row:
            row.symmetric_difference_update({t_reg})
        body.append([g[0], g[1], sorted(row)])
    out = copy.deepcopy(word)
    out["D"] = [[0, a, [t_reg]]] + body
    return out


def construct_f4_late(word, pair):
    """Close the conjugation after the target's own write (breaks condition 3)."""
    a, _b = pair
    t_reg = word["D"][-1][1]
    k = len(word["D"]) - 1
    body = []
    for i, g in enumerate(word["D"]):
        row = set(g[2])
        if i < k and a in row:
            row.symmetric_difference_update({t_reg})
        body.append([g[0], g[1], sorted(row)])
    out = copy.deepcopy(word)
    out["D"] = [[0, a, [t_reg]]] + body + [[0, a, [t_reg]]]
    return out


def d_shape(word, checker):
    w = checker.Word(word)
    val, cur, _ = w.replay(sections=("D",), frames_on=True)
    v, R = w.v, w.R
    smask = ((1 << R) - 1) << (2 * v)
    ymask = ((1 << v) - 1) << v
    xmask = (1 << v) - 1
    shape_ok = (
        all(val[s] == 1 << s for s in range(v))
        and all(val[r] == 1 << r for r in range(2 * v, 2 * v + R))
        and all(val[v + t] & (ymask | xmask) == 1 << (v + t) for t in range(v))
    )
    N = [val[v + t] & smask for t in range(v)]
    return val, cur, shape_ok, N


def h2sem_conditions(word):
    v, n = word["v"], 2 * word["v"] + word["R"]
    is_y = lambda r: v <= r < 2 * v
    cond1 = all(
        g[0] == 0
        and v <= g[1] < n
        and g[1] not in g[2]
        and len(set(g[2])) == len(g[2])
        and all(v <= s < n for s in g[2])
        for g in word["D"]
    )
    cond2 = not any(not is_y(g[1]) and any(is_y(s) for s in g[2]) for g in word["D"])
    return cond1, cond2


def raw_K(word, checker):
    w = checker.Word(word)
    raw, _, _ = w.replay(sections=("A", "scatter", "B"), frames_on=False)
    smask = ((1 << w.R) - 1) << (2 * w.v)
    return [raw[w.v + t] & smask for t in range(w.v)]


def stream(w):
    out = [("add", d, s) for sec in ("D", "A") for _, d, ss in w[sec] for s in ss]
    tmp = 2 * w["v"] + w["R"]
    for j, h in enumerate(w["ret"]):
        out.append(("copy", tmp, h))
        out.extend(("add", w["v"] + t, tmp) for t, ss in enumerate(w["scatter"]) if j in ss)
        out.append(("erase", tmp, h))
    out.extend(("add", d, s) for sec in ("B", "C") for _, d, ss in w[sec] for s in ss)
    return out


def literal(w, reverse=False):
    n = 2 * w["v"] + w["R"]
    rows = [1 << i for i in range(n)] + [0]
    ops = stream(w)
    for kind, d, s in reversed(ops) if reverse else ops:
        if reverse:
            kind = {"copy": "erase", "erase": "copy"}.get(kind, kind)
        if kind == "add":
            rows[d] ^= rows[s]
        elif kind == "copy":
            need(rows[d] == 0, "live copy temporary")
            rows[d] = rows[s]
        else:
            need(rows[d] == rows[s], "changed copy before erasure")
            rows[d] = 0
    need(rows[-1] == 0, "copy temporary remains")
    return rows[:-1]


def desired_endpoint(w):
    n = 2 * w["v"] + w["R"]
    return [
        (1 << r) ^ (1 << (r - w["v"])) if w["v"] <= r < 2 * w["v"] else 1 << r
        for r in range(n)
    ]


def bill(w, W):
    paths = [[f] for f in w["start"]]
    for sec in "DABC":
        for f, d, ss in w[sec]:
            for r in [d] + ss:
                if paths[r][-1] != f:
                    need(W.nested(paths[r][-1], f) and W.fdim[paths[r][-1]] < W.fdim[f], "frame climb")
                    paths[r].append(f)
    for r, f in enumerate(w["final"]):
        if paths[r][-1] != f:
            need(W.nested(paths[r][-1], f) and W.fdim[paths[r][-1]] < W.fdim[f], "final frame climb")
            paths[r].append(f)
    profile = Counter(W.fdim[b] - W.fdim[a] for p in paths for a, b in zip(p, p[1:]))
    copy_ranks = [t["rank"] for t in W.totals()]
    profile.update(copy_ranks)
    peaks = []
    for reverse in (False, True):
        vals = [1] * (2 * w["v"] + w["R"]) + [0]
        peak = 1
        for kind, d, s in reversed(stream(w)) if reverse else stream(w):
            if reverse:
                kind = {"copy": "erase", "erase": "copy"}.get(kind, kind)
            vals[d] = vals[d] + vals[s] if kind == "add" else (vals[s] if kind == "copy" else 0)
            peak = max(peak, vals[d])
        peaks.append(peak)
    F, B = peaks
    local = 64 * F**3 * B**2
    nine = (1 << 18) * F**5 * B**4
    need(local < 1 << 104 and nine < 1 << 192, "positive precision guard failed")
    return {
        "profile": {str(k): v for k, v in sorted(profile.items())},
        "rank_mass": sum(k * v for k, v in profile.items()),
        "ADDS": sum(kind == "add" for kind, _, _ in stream(w)),
        "D_ADDS": sum(len(ss) for _, _, ss in w["D"]),
        "D_gates": len(w["D"]),
        "F": F,
        "B": B,
        "local_integer": local,
        "nine_stage_integer": nine,
        "local_bits": local.bit_length(),
        "nine_stage_bits": nine.bit_length(),
    }


def failed_flags(H, C):
    return sorted(k for k, v in list(H.items()) + list(C.items()) if not v)


def main() -> None:
    check_pins()
    word = json.loads(gzip.decompress(WORD_PATH.read_bytes()))
    checker = load_checker()
    controls = []

    _, _, _, H0, C0, _ = checker.check(word)
    need(all(H0.values()) and all(C0.values()), "baseline inherited flags failed")
    val0, cur0, shape0, N0 = d_shape(word, checker)
    need(shape0, "baseline D operator is not (x, y+N h, h)")
    K0 = raw_K(word, checker)
    need(N0 == K0, "baseline semantic N != raw K")
    want = desired_endpoint(word)
    need(literal(word) == want == literal(word, True), "baseline literal endpoint failed")
    W0, _, _, _, _, _ = checker.check(word)
    bill0 = bill(word, W0)
    need(bill0["rank_mass"] == 5129, "unexpected baseline rank mass")
    need(bill0["ADDS"] == 24305, "unexpected baseline ADD count")
    controls.append("baseline word: all inherited flags, D operator, literal endpoint, profile mass 5129")

    matching, census = nominate_d(word, SEED)
    need(census["best_pair"] == PAIR and census["best_saving"] == 65, "PR848 best pair moved")
    need(census["matching_pairs"] == 205 and census["matching_saving"] == 6231, "PR848 matching moved")
    pair = matching[0]
    need(pair == PAIR, "matching head is not 277->434")

    # Admitted contrast: C1 satisfies all three H2-sem conditions.
    c1 = construct_c1(word, [pair])
    c1_cond1, c1_cond2 = h2sem_conditions(c1)
    c1_val, c1_cur, c1_shape, c1_N = d_shape(c1, checker)
    need(c1_cond1 and c1_cond2 and c1_shape and c1_val == val0 and c1_cur == cur0 and c1_N == N0,
         "C1 contrast lost H2-sem admission")
    _, _, _, Hc1, Cc1, _ = checker.check(c1)
    need(failed_flags(Hc1, Cc1) == ["H2_D_frame0_targets_from_helpers", "K_equals_D"],
         "C1 unexpected inherited failures")
    controls.append("C1 helper-temp wrap on 277->434 admits H2-sem 1-3 (contrast)")

    # F4 necessity witness.
    feed, meta = construct_f4(word, pair)
    need(all(feed[k] == word[k] for k in word if k != "D"), "F4 moved a non-D section")
    cond1, cond2 = h2sem_conditions(feed)
    val, cur, shape, N = d_shape(feed, checker)
    need(cond1, "F4 unexpectedly fails condition 1")
    need(not cond2, "F4 unexpectedly passes condition 2")
    need(shape and val == val0 and cur == cur0 and N == N0 == K0,
         "F4 lost conditions 1/3, frames, or semantic K")
    _, _, _, Hf, Cf, _ = checker.check(feed)
    need("H1_no_target_feeds_z" in failed_flags(Hf, Cf), "F4 did not trip inherited H1")
    controls.append("F4: cond1/3 and frames hold; cond2 fails; inherited H1 fails")

    # Framed sectional + literal endpoints.
    Ww = checker.Word(feed)
    framed, framed_cur, _ = Ww.replay(sections=("D", "A", "scatter", "B", "C"), frames_on=True)
    need(framed == want, "F4 framed sectional endpoint is not (x,y+x,h)")
    need(framed_cur == feed["final"], "F4 final frames mismatch")
    need(literal(feed) == want == literal(feed, True), "F4 literal forward/reverse endpoint failed")
    controls.append("F4 framed+literal forward/reverse dirty endpoint exact on 661 columns")

    # Virtual original-D splice (chronological bridge premise).
    bridge = copy.deepcopy(feed)
    bridge["D"] = copy.deepcopy(word["D"])
    _, _, _, Hb, Cb, _ = checker.check(bridge)
    need(all(Hb.values()) and all(Cb.values()), "virtual original-D splice failed")
    controls.append("proof-only original-D splice passes every inherited flag")

    # Exact costs.
    Wf, _, _, _, _, _ = checker.check(feed)
    bill_f = bill(feed, Wf)
    need(bill_f["rank_mass"] == bill0["rank_mass"] == 5129, "paid profile mass moved")
    need(bill_f["profile"] == bill0["profile"], "paid profile histogram moved")
    need(bill_f["ADDS"] == 24374 and bill0["ADDS"] == 24305, "ADD counts drifted")
    need(bill_f["D_ADDS"] == 18154 and bill0["D_ADDS"] == 18085, "D ADD counts drifted")
    need(bill_f["D_gates"] == 113 and bill0["D_gates"] == 111, "D gate counts drifted")
    need(bill_f["F"] == 50535 and bill0["F"] == 49347, "F drifted")
    need(bill_f["B"] == 2995586 and bill0["B"] == 1113070, "B drifted")
    controls.append("exact costs: +69 ADDs, profile mass 5129 unchanged, guards strict")

    # Negative controls: restorations that break condition 3.
    unrestored = construct_f4_unrestored(word, pair)
    u_val, _, u_shape, _ = d_shape(unrestored, checker)
    need(not (u_shape and u_val == val0), "unrestored F4 preserved condition 3")
    controls.append("F4 unrestored feed breaks condition 3")

    late = construct_f4_late(word, pair)
    l_val, _, l_shape, _ = d_shape(late, checker)
    need(not (l_shape and l_val == val0), "late-restore F4 preserved condition 3")
    controls.append("F4 late restore (after target write) breaks condition 3")

    result = {
        "status": PASS,
        "new_kappa": False,
        "pair": PAIR,
        "f4_meta": meta,
        "census": census,
        "conditions": {
            "cond1_zero_frame_distinct_operands": cond1,
            "cond2_no_target_feeds_helper_or_source": cond2,
            "cond3_boundary_operator_exact": True,
            "frames_at_cut_equal": True,
            "semantic_N_equals_raw_K": True,
        },
        "inherited_flag_failures": failed_flags(Hf, Cf),
        "endpoint": {
            "framed_sectional_exact": True,
            "literal_forward_exact": True,
            "literal_reverse_exact": True,
            "columns": 2 * word["v"] + word["R"],
        },
        "virtual_original_D_splice_passes": True,
        "baseline_bill": bill0,
        "f4_bill": bill_f,
        "controls": controls,
        "claim": (
            "On this F4 instance, H2-sem condition 2 fails while the framed dirty "
            "endpoint (x,y,h)->(x,y+x,h) holds; condition 2 is not necessary for "
            "that endpoint conclusion. No general drop of condition 2 is claimed."
        ),
    }
    expected_path = HERE / "EXPECTED.json"
    payload = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if expected_path.exists():
        expected = expected_path.read_text(encoding="utf-8")
        need(payload == expected, "EXPECTED.json mismatch; inspect before rewriting")
    else:
        expected_path.write_text(payload, encoding="utf-8")
    print(PASS)


if __name__ == "__main__":
    main()
