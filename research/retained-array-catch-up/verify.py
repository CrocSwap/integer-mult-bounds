#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Primary verifier: retained-array coordinate catch-up in the scalar common-frame transport model.

Checks (exact arithmetic; standard library only):
 1. Source pins and verbatim premise lines.
 2. Level timeline of the pinned selected #1094 hosted GLOBAL-TEMPLATE (replica 0). Every local
    call advances its pair one level; idle sweeps advance their declared levels; one level is
    eight coordinates (base-template idle child rank = 8 x levels; hosted children never exceed it).
    Every bridge joins two pairs at equal levels.
 3. The catch-up law (PROOF.md Corollary 4) on controls: PR2540 128, PR2197 144, PR2678
    1792/3696, centre path 576 per replica.
 4. The #1166 routes under the stated observation contract (P_obs) and capture times:
    INIT64 + d_A = 3648 (end decoder, P_final) / 2496 (earliest timing the observed Y_(k,U) fields
    allow under the final-value read convention, P_Y: X_(k,U) is last written at events 6/27/26/25) /
    1344 (each bank after its last local call, P_early; a lower bound for decoders with the
    decoder-timing premise P_dec);
    d_A alone 960; the all-initial variant of #2074 c18950926 3456 / 2304 / 1152; Theorem B per cut:
    one consumer level (P_final) 1952 / 1824, own-bank premise 1344 / 1216 (P_Y) and 800 / 608
    (P_early), count-only deliveries 608 / 544 (P_Y) and 112 / 0 (P_early); (S)/(C) array-calls 464
    published / 456 uniform; the zero-advance window; the lagging-family example (the record
    duplicates an observed row, so the law charges 0). Without P_dec: 512 (decoders right after
    each bank's own last capture) and 640 (right after each backward call). Bank 0's INIT rows via
    f0: 3520 / 2368 / 1216 (all-initial 3328 / 2176 / 1024). Revival terms: d_A 960 / 576 / 192 and
    all-initial reads 768 / 384 / 0. Forward add-on f2..f8: 768-1024 / 384-640 / 0-256. Hosting (replica 0): every capture,
    consumer and read instant sits at an exact level, checked in both directions.
 5. Pricing with the pinned ceiling.py: exact 896 no-saving threshold, break-evens 573 / 71
    against PR2474 (reproducing the #1166 price gate and its PRICE-GATE.json storage ceiling),
    break-evens against other targets.
 6. Exact frame model: breadth-first minimum paid mass equals the per-cut rank bound (Lemma 1)
    and the meeting-level formula (Proposition 3) on complete finite domains; Lemma 1 is sound
    on general instances.
 7. Two-call rational tensor toy: omitting catch-up gives a wrong output; paid catch-up (or
    partner descent) repairs it.
 8. Negative controls: mutated levels, rows, windows, incidences, lifetimes, read levels,
    formulas, toy repairs and prices must fail.

Run from the repository root:  python3 -I -B research/retained-array-catch-up/verify.py
--write regenerates RESULT.json (refuses to replace a differing file unless --force is given).
Prepared by thakrarsagar with substantial AI assistance from Claude (Anthropic, Claude Opus 5.5).
"""
import gzip
import hashlib
import io
import itertools
import json
import math
import random
import sys
import tarfile
from collections import deque
from fractions import Fraction as Q
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]

PINS = {
    "research/complex-local-word-ceiling/ceiling.py":
        "86a1432870b3b21d8454106ec9162fddc0471472d9214c590a1420f2426cedfc",
    "research/complex-local-word-ceiling/README.md":
        "b60be039cb0e03e064a27407d0bce9e58908d793da5ee405c876de5aebfa5f81",
    "research/dirty-host-cutrank-audit/PROOF.md":
        "2921c2c741ab5086a87c53340f18180ecc55675ca7dadc49579da32aba71d2f5",
    "research/idle-axis-hosting/PROOF.md":
        "cfe34bf0b64259661312dae22c3a23adc5bf6f6326951eee5c1488ccfc347542",
    "research/qq16-complete-native-decoder/PROOF.md":
        "09d587f1d6bc250e90e29fa8751a40f45be79f1a8a56af0b645c144cefaefa46",
    "research/qq16-entry-frame-tariff/README.md":
        "cb0e658cfbdd3fb74a43b195665d3b13d5eb8e74294831daa05165128ad9ef5d",
    "research/qq16-private-da-frame-floor-seed81b017/README.md":
        "8e4c3f1d2e76b110ef47aecdce8098c84403b969f8d6e386b0ecabb8173f091b",
    "research/qq16-final-record-obstruction/PROOF.md":
        "109490f1d9c4288445e11e65e77616d84555ce9f212df97c81e6efde0c2ebf43",
    "research/selected-centre-quarter-native/README.md":
        "bfae0aff6aefc90b2afb8da76bc6d07b698deeabdbd758d01910d9fdb937ec72",
    "research/centre-owner-observation-floor/README.md":
        "5f9079af7f45bff8d0b0acc8366f9c0def90fad9c8a38bab772b0ef13e3d5be0",
    "research/selected-centre-chrono-source-census/README.md":
        "0db44f2ce702ee1e5b11c9f8cd05517593bd259f45ae897437c58a1bd81b2943",
    "research/joint-query/README.md":
        "419f076e46f5a6ce43efe30a608baed0a535034c388e1ac76a29a2026685ba77",
    "research/joint-query/evidence/CONSERVED-QQ16.md":
        "60f0de3a7205ba5046b5ae7ffa8bf2b1ea42ea46b498face0a77966b59e7f3fb",
    "research/community-frontier1094-audit/selected-replay.tar.gz":
        "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6",
    "certificates/selected-result.json":
        "bb2eaa58647b353f88d0aec2eafb9d30df1be53589231b23e12ceef3e4bad129",
    "research/qq16-cut-retention-census/README.md":
        "796636d4d9824bc4959b00d9d2cbbfafec07c14e6845a1e238fb668a2f3d8adf",
}
HOSTED_MEMBER = ("candidate/strict/global/hosted/GLOBAL-TEMPLATE.json.gz",
                 "2acf02b418078e37090495c601fe550448751d4f35912757b13a1f778efc7760")
BASE_MEMBER = ("candidate/strict/global/base/split-centres/GLOBAL-TEMPLATE.json.gz",
               "a179dad87651aba340a5a8ddbcd86a8e757cad87b8a1f8bad48106fbecd38518")

ANCHORS = {
    "research/dirty-host-cutrank-audit/PROOF.md": [
        "Its paid mass c is at least |nu(A)-nu(B)|.",
        "D_j\\ \\ge\\ \\dim(W_j^0+\\operatorname{span}Q_j)-\\dim W_j^0. \\tag{C-down}",
        "M\\ge\\sum_j(D_j+U_j). \\tag{A}",
        "The retained history is a mathematical device, not free physical storage.",
        "Any pre-existing side information belongs to the entry state.",
    ],
    "research/qq16-complete-native-decoder/PROOF.md": [
        "`F_L=product_(j=0,...,8) C_(d e_j)`",
        "`U1=<e0,...,e16>`",
        "This costs sixteen rank-eight children and puts x1_V in frame F_U1.",
    ],
    "research/qq16-entry-frame-tariff/README.md": [
        "| Common `F_L`, `F_L` | 224 H8 | 1,792 |",
        "| F0 gauges `F_L`, `F_L C_q^-1` | 112 H8 + 112 H9 | 1,904 |",
        "| Original entry gauges `C_q`, `I` | 112 H16 + 112 H17 | 3,696 |",
    ],
    "research/qq16-private-da-frame-floor-seed81b017/README.md": [
        "each differs from I in exactly 18 one-term Z4 entries.",
        "frames therefore needs at least 8 × 18 = 144 line calls.",
    ],
    "research/qq16-final-record-obstruction/PROOF.md": [
        "    0, 0, 0, 1, 1, 2, 2, 3, 3.",
        "Even stages are forward F_s; odd stages are backward B_(s,s+1).",
        "pair 0: B0 X_(0,U), B2 X_(0,U);",
        "pair 1: B3 X_(1,U), B4 X_(1,U);",
        "    X_j,U += c X_i,U;",
        "    Y_i,U -= c Y_j,U.",
        "base contract. The final ordinary terminal is `(X_U,Y_U) -> (Y_U,-X_U)`.",
        "2. Every final completed-X ordinary field, namely final Y_(k,U).",
        "former-Y ordinary endpoint, or additional ordinary read is observed.",
        "former-Y ordinary endpoints, final X_(0,U)=z0 and final X_(1,U)=z1.",
    ],
    "research/joint-query/evidence/CONSERVED-QQ16.md": [
        "    x'_U=x_U-y_U,",
        "    x'_U=x_U-K_(s,U)f,",
    ],
    "research/idle-axis-hosting/PROOF.md": [
        "1. ι is an invocation on another pair, and nothing touches F between ι and τ.",
    ],
    "research/complex-local-word-ceiling/README.md": [
        "`{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}`, local mass 5,586.",
    ],
    "research/joint-query/README.md": [
        "| B_s_t | 214986 | 24 | 5546 | 528 | 48 |",
        "| F_s, s > 0 | 211210 | 8 | 5530 | 288 | 16 |",
    ],
    "research/selected-centre-chrono-source-census/README.md": [
        "2. **Every dependent pair has rank 16 (1,539 pairs).**",
        "b5->f6, b7->f8 and f0->f2.",
        "projection. It is not a native obstruction, not a formal proof and not a new kappa. The selected frontier",
        "   - *First step:* for the 16 f0->f2 pairs (shared 88 destination owners), compute the output-increment",
    ],
    "research/selected-centre-quarter-native/README.md": [
        "nevertheless `1/4` at the identity owner.",
    ],
    "research/centre-owner-observation-floor/README.md": [
        "**104 additional scalar coordinates at every old cover owner**, if each extra",
    ],
    "research/qq16-cut-retention-census/README.md": [
        "| C=0, centre-like copy | 111 | 71 | 120 / 1688: no saving at either (L2 variant: 32) |",
    ],
}

COORDS_PER_LEVEL = 8
M, FAMILIES, STAGES = 73, 896, 9
SELECTED_KAPPA = Q("0.001672660197076918")       # #1094, selected-result.json
PR2474_KAPPA = Q("0.001703676387993676")         # pending (PR2474)
PR2843_KAPPA = Q("0.00171865827784172")          # pending (PR2843 title value)
PR2848_KAPPA = Q("0.00171865850830493")          # pending (PR2848 title value)
PR2857_KAPPA = Q("0.00172009662868483")          # pending (PR2857 title value; opened after the base)
BIT_ENDPOINT = Q("0.001733427039589844234749")   # PR589 bit supplier saving
GRID = Q(1, 10 ** 12)
SELECTED = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
# Philippe Van Velzen's price gate, read as data (never executed) from
# philippeVV/integer-mult-bounds@9fcd3d899cc5bad2e27ab1d3d64d241cbfe30793,
# research/joint-query-first-pair-catalogue/final-record/:
#   price_gate.py docstring: "bank k first call stage: 0, 3, 5, 7.  INIT records of bank k are read
#   just before that call."; constants INIT_AC = 16 * (9 + 6 + 4 + 2) and DA_AC = 8 * (8 + 5 + 3);
#   PRICE-GATE.json fields storage_readsFalse, breakeven_storage and breakeven_centre.
PRICE_GATE_INIT_LIFETIMES = (9, 6, 4, 2)
PRICE_GATE_DA_LIFETIMES = (8, 5, 3)
PRICE_GATE_STORAGE_READS_FALSE = Q(2285992139, 1002285992139)
PRICE_GATE_BREAKEVENS = (573, 71)


class CheckFailure(Exception):
    pass


def need(ok, message):
    if not ok:
        raise CheckFailure(message)


# ------------------------------------------------------------------ 1. sources
def check_sources():
    for rel, pin in PINS.items():
        need(hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == pin, "source hash mismatch: " + rel)
    for rel, lines in ANCHORS.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for line in lines:
            need(line in text, "premise anchor missing in %s: %r" % (rel, line))
    return {"pinned_files": len(PINS), "anchored_premise_lines": sum(len(v) for v in ANCHORS.values())}


def load_templates():
    raw = (ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz").read_bytes()
    out = []
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as archive:
        for name, pin in (HOSTED_MEMBER, BASE_MEMBER):
            found = [m for m in archive.getmembers() if m.name == name]
            need(len(found) == 1 and found[0].isfile(), "one regular member: " + name)
            data = archive.extractfile(found[0]).read()
            need(hashlib.sha256(data).hexdigest() == pin, "member hash: " + name)
            out.append(json.loads(gzip.decompress(data)))
    return out


# ------------------------------------------------------------------ 2. level timeline
def replica_events(hosted, base, replica=0):
    events = [e for e in hosted["execution_schedule"] if e.get("replica") == replica]
    need(len(events) == 30 and [e["source_event"] for e in events] == list(range(30)), "replica-0 events")
    need(hosted["live"] == 14336 and hosted["m"] == 73, "selected live families / width")
    need(all(b == 0 for b in hosted["hosting"]["banks"]), "selected template has no helper banks")
    strip = ("replica", "replicas", "source_event", "time", "provider_id", "entry_exit_phase_adapters")
    base_events = [{k: v for k, v in e.items() if k not in strip} for e in base["execution_schedule"][:30]]
    host_events = [{k: v for k, v in e.items() if k not in strip} for e in events]
    need(base_events == host_events, "hosted replica-0 schedule equals the base template schedule")
    return events


def level_timeline(hosted, base, events, mutate=None):
    """timeline[k] = (kind, source_event, levels of pairs 0..3 after it); timeline[0] = entry."""
    recipe = hosted["recipe"]
    local_pairs = [e["pair"] for e in recipe if e["kind"] == "local"]
    need(local_pairs == [0, 0, 0, 1, 1, 2, 2, 3, 3], "literal local pair binding (PR2346 recipe)")
    need(all(e["reverse"] == (e["stage"] % 2 == 1) for e in recipe if e["kind"] == "local"),
         "odd stages backward")
    stage_pair = dict(enumerate(local_pairs))
    base_rank = {c["child"]: c["rank"] for c in base["idle_children"] if c["port"] == 0}
    hosted_total = {}
    for c in hosted["idle_children"]:
        hosted_total.setdefault(c["child"], set()).add(c["hosted"] + c["rank"])
    level = [-1, -1, -1, -1]
    timeline = [("entry", None, tuple(level))]
    for e in events:
        if e["kind"] == "local_cover_sweep":
            p = stage_pair[e["stage"]]
            need(level[p] == e["stage"] - 1, "local stage %d starts one level below" % e["stage"])
            level[p] = e["stage"]
        elif e["kind"] == "idle_cover_sweep":
            p, frm, to = e["pair"], e["from_level"], e["to_level"]
            if mutate == "idle_to_level" and e["source_event"] == 5:
                to += 1
            need(level[p] == frm and to >= frm, "idle sweep continues the pair's level")
            if to > frm:
                want = COORDS_PER_LEVEL * (to - frm)
                need([base_rank[c] for c in e["child_indices"]] == [want, want],
                     "base idle children: eight coordinates per level (event %d)" % e["source_event"])
                for c in e["child_indices"]:
                    need(all(t <= want for t in hosted_total.get(c, {want})),
                         "hosted + remaining rank never exceeds the base child rank")
            level[p] = to
        elif e["kind"] == "bridge":
            need(level[e["src"]] == level[e["dst"]], "bridge %d joins two pairs at equal levels" % e["source_event"])
        timeline.append((e["kind"], e["source_event"], tuple(level)))
    need(level == [8, 8, 8, 8], "every pair ends at level 8 (nine levels = 72 paid coordinates)")
    return timeline, stage_pair


def lv_before(timeline, event):
    return timeline[event][2]


def lv_after(timeline, event):
    return timeline[event + 1][2]


def catch_up(cap, cons, pair, rows):
    gap = cons[pair] - cap[pair]
    need(gap >= 0, "consumer frame at or above the capture frame")
    return COORDS_PER_LEVEL * gap * rows


def routes(timeline, events, stage_pair, mutate=None):
    end = timeline[-1][2]
    locals_of = {k: [e["source_event"] for e in events if e["kind"] == "local_cover_sweep"
                     and stage_pair[e["stage"]] == k] for k in range(4)}
    out = {}
    rows = 15 if mutate == "pr2540_rows" else 16
    after_b1 = lv_after(timeline, 4 if mutate == "pr2540_incidence" else 1)
    out["PR2540_early_records"] = {"rows": 16, "capture": "after F0 (event 0)", "consumer": "F_U1 after B1 (event 1)",
                                   "capture_level": lv_after(timeline, 0)[0], "consumer_level": after_b1[0],
                                   "mass": catch_up(lv_after(timeline, 0), after_b1, 0, rows)}
    # Capture premise (PROOF.md section 7.2): X_(k,U) keeps its initial logical row until bank k's first
    # local call. Local calls overwrite X_U (CONSERVED-QQ16 (1) and (3)) and no bridge writes X_(k,U)
    # before that call, so the stated INIT capture just before it is the latest one without other reads.
    for k in range(4):
        need(not any(e["kind"] == "bridge" and e["dst"] == k for e in events[:locals_of[k][0]]),
             "no bridge writes X_(%d,U) before bank %d's first call" % (k, k))
    init = []
    for k in range(4):
        ev = locals_of[k][0]
        lv = list(lv_before(timeline, ev))
        if mutate == "init_capture_level" and k == 1:
            lv[1] = -1
        init.append({"bank": k, "capture_before_event": ev, "capture_level": lv[k], "rows": 16,
                     "consumer_level": end[k], "mass": catch_up(lv, end, k, 16)})
    da = []
    for k in range(3):
        ev = [x for x in locals_of[k] if events[x]["stage"] % 2 == 1][0]
        lv = lv_after(timeline, ev)
        da.append({"bank": k, "capture_after_event": ev, "capture_level": lv[k], "rows": 8,
                   "consumer_level": end[k], "mass": catch_up(lv, end, k, 8)})
    out["INIT64"], out["d_A"] = init, da
    out["INIT64_plus_dA_mass"] = sum(r["mass"] for r in init + da)
    out["d_A_only_mass"] = sum(r["mass"] for r in da)
    need(sum(r["rows"] for r in init + da) == 88, "88 stated arrays per owner per replica")
    # P_Y: the contract observes final Y_(k,U) = -final X_(k,U) (terminal relabel). Local calls on pair k
    # overwrite X_(k,U) and a bridge with dst = k adds into it, so no decoder of bank k can use its
    # observed field before the last such write (final-value read convention of P_obs). Its level there
    # lower-bounds every P_obs-admissible current-frame consumer of bank k that uses its own Y_(k,U)
    # (other observations can only delay the decoder).
    last_write = [max(e["source_event"] for e in events
                      if (e["kind"] == "local_cover_sweep" and stage_pair[e["stage"]] == k)
                      or (e["kind"] == "bridge" and e["dst"] == k)) for k in range(4)]
    out["x_last_write_event"] = last_write
    out["x_last_write_levels_all_pairs"] = [list(lv_before(timeline, ev)) for ev in last_write]
    y_levels = [lv_after(timeline, last_write[k])[k] for k in range(4)]
    out["y_consumer_levels"] = y_levels
    out["INIT64_plus_dA_y_mass"] = sum(catch_up([r["capture_level"]] * 4, y_levels, r["bank"], r["rows"])
                                       for r in init + da)
    # P_early: decode each bank at its own frame right after its last local call. Under P_obs with
    # final-value reads this is not attainable for banks 1-2 (their observed fields are final only at
    # level 8). Above the captures catch-up only grows with the consumer level, so it lower-bounds every
    # current-frame timing at or after each bank's last local call (the decoder-timing premise P_dec);
    # it does not bound earlier decoders (see without_decoder_timing_premise below). Favourable to the
    # route: the corrected fields are assumed to ride the inherited idle sweep to level 8 at no extra mass.
    early = []
    for r in init + da:
        k = r["bank"]
        last = lv_after(timeline, locals_of[k][-1])
        cap = [None] * 4
        cap[k] = r["capture_level"]
        early.append(catch_up(cap, last, k, r["rows"]))
    out["INIT64_plus_dA_early_consumer_mass"] = sum(early)
    out["early_consumer_levels"] = [lv_after(timeline, locals_of[k][-1])[k] for k in range(4)]
    out["early_consumer_after_events"] = [locals_of[k][-1] for k in range(4)]
    # All-initial variant (#2074 c18950926 item 2): the d_A records are swapped for the reads
    # B2 X_1U, B4 X_2U and B6 X_3U. X_(k+1,U) keeps its initial row until pair k+1's first local call,
    # so the read may be taken at any level pair k+1 holds before that call. Pairs at equal levels
    # share a frame (every bridge joins pairs at equal levels; checked in level_timeline).
    reads = []
    for k in range(3):
        src = k + 1
        first = locals_of[src][0]
        need(not any(e["kind"] == "bridge" and e["dst"] == src for e in events[:first]),
             "no bridge writes X_(%d,U) before its first call" % src)
        held = sorted({timeline[i][2][src] for i in range(first + 1)})     # entry .. just before the first call
        if mutate == "allinit_read_level" and k == 0:
            held = [h for h in held if h != out["early_consumer_levels"][0]]
        latest = lv_before(timeline, first)[src]
        cons = out["early_consumer_levels"][k]
        best = min(held, key=lambda h: abs(cons - h))
        reached = [e["source_event"] for e in events[:first]
                   if e["kind"] == "idle_cover_sweep" and e["pair"] == src and e["to_level"] == best]
        reads.append({"bank": k, "read": "B%d X_(%d,U)" % (2 * k + 2, src), "rows": 8,
                      "levels_held_while_initial": held, "latest_read_level": latest,
                      "final_mass": COORDS_PER_LEVEL * 8 * (end[k] - latest),
                      "early_consumer_level": cons, "early_read_level": best,
                      "early_read_after_event": reached[0] if reached else None,
                      "early_mass": COORDS_PER_LEVEL * 8 * abs(cons - best),
                      "y_mass": COORDS_PER_LEVEL * 8 * min(abs(y_levels[k] - h) for h in held)})
    init_early = early[:4]
    out["all_initial_variant"] = {
        "source": "#2074 c18950926 item 2: the d_A records swapped for the reads B2 X_1U, B4 X_2U and B6 X_3U",
        "reads": reads,
        "final_mass": sum(r["mass"] for r in init) + sum(x["final_mass"] for x in reads),
        "y_mass": sum(catch_up([r["capture_level"]] * 4, y_levels, r["bank"], 16) for r in init)
        + sum(x["y_mass"] for x in reads),
        "early_mass": sum(init_early) + sum(x["early_mass"] for x in reads)}
    # Theorem B (#2074 c18940190): any repair needs >= 62 independent rows per owner per replica. Restricted
    # to the stated captures (each array supplies at most one row per owner; P_obs; P4), see PROOF.md 7.2.
    original = [(r["bank"], r["rows"], [r["capture_level"]]) for r in init + da]
    variant = [(r["bank"], 16, [r["capture_level"]]) for r in init] + \
              [(x["bank"], 8, x["levels_held_while_initial"]) for x in reads]
    timings = {"P_final": list(end), "P_Y": y_levels, "P_early": out["early_consumer_levels"]}
    out["theorem_B"] = {name: {"original": theorem_b(original, cons), "all_initial": theorem_b(variant, cons)}
                        for name, cons in timings.items()}
    # Forward histories f2, f4, f6, f8 (the tail identity C_k = w_k + K_(2k+2) f_(2k+2) of #2074 c18950926 uses
    # f_(2k+2) for every bank, f8 for bank 3; not in the 464 array-calls). If each is retained as one 8-row array
    # captured at its forward call's output or input level, the law adds the following; the totals only grow.
    fwd = {"P_final": [], "P_Y": [], "P_early": []}
    for k in range(4):
        ev = [x for x in locals_of[k] if events[x]["stage"] == 2 * k + 2][0]
        lo, hi = lv_before(timeline, ev)[k], lv_after(timeline, ev)[k]
        for name, cons in (("P_final", end), ("P_Y", y_levels), ("P_early", out["early_consumer_levels"])):
            fwd[name].append((cons[k] - hi, cons[k] - lo))
    out["forward_histories_addon"] = {
        "histories": "f2, f4, f6, f8: one 8-row array each, captured at the forward call's output (low end) or input level",
        **{name.replace("P_final", "final").replace("P_Y", "y").replace("P_early", "early") + "_mass_range":
           [COORDS_PER_LEVEL * 8 * sum(a for a, _ in v), COORDS_PER_LEVEL * 8 * sum(b for _, b in v)]
           for name, v in fwd.items()},
        "f2_f4_f6_only": {name: [COORDS_PER_LEVEL * 8 * sum(a for a, _ in v[:3]), COORDS_PER_LEVEL * 8 * sum(b for _, b in v[:3])]
                          for name, v in fwd.items()}}
    # One P_rank law for any consumer vector (uncompressed delivery of every stated array to its own bank's
    # consumer; reads at their best held level, either direction). It must reproduce the totals above.
    def law_mass(cons, variant, init_levels=None):
        caps = init_levels or [r["capture_level"] for r in init]
        total = sum(catch_up([caps[k]] * 4, cons, k, 16) for k in range(4))
        if variant == "original":
            return total + sum(catch_up([r["capture_level"]] * 4, cons, r["bank"], 8) for r in da)
        return total + sum(COORDS_PER_LEVEL * 8 * min(abs(cons[x["bank"]] - h) for h in x["levels_held_while_initial"])
                           for x in reads)
    for name, cons in (timings.items() if mutate is None else ()):     # mutations are judged by their own checks
        need(law_mass(cons, "original") == {"P_final": out["INIT64_plus_dA_mass"], "P_Y": out["INIT64_plus_dA_y_mass"],
                                            "P_early": out["INIT64_plus_dA_early_consumer_mass"]}[name]
             and law_mass(cons, "all_initial") == {"P_final": out["all_initial_variant"]["final_mass"],
                                                   "P_Y": out["all_initial_variant"]["y_mass"],
                                                   "P_early": out["all_initial_variant"]["early_mass"]}[name],
             "one law_mass reproduces both variants at " + name)
    # Decoder-timing premise (P_dec) is load-bearing: decoders placed right after each bank's own last stated
    # capture, or right after each backward call, are current-frame consumers that P_obs alone does not exclude.
    own_last = [max([r["capture_level"] for r in init + da if r["bank"] == k]) for k in range(4)]
    after_back = [lv_after(timeline, [x for x in locals_of[k] if events[x]["stage"] % 2 == 1][0])[k] for k in range(4)]
    out["without_decoder_timing_premise"] = {
        "after_own_last_capture": {"consumer_levels": own_last, "original": law_mass(own_last, "original"),
                                   "all_initial": law_mass(own_last, "all_initial")},
        "after_backward_call": {"consumer_levels": after_back, "original": law_mass(after_back, "original"),
                                "all_initial": law_mass(after_back, "all_initial")}}
    # Bank 0's INIT rows via f0 (CONSERVED-QQ16 (3): z = w + K_(s,U) f, and f0 is an observation under P_obs):
    # B_t X_(0,U)(initial) = B_t X'_(0,U) + B_t K_(0,U) f0 can be formed at F0's output frame. Banks 1-3 start
    # with a backward call, whose inverse needs the transient y_U, so their stated captures stay the latest.
    f0_init = [lv_after(timeline, locals_of[0][0])[0]] + [r["capture_level"] for r in init[1:]]
    need(events[locals_of[0][0]]["stage"] == 0 and all(events[locals_of[k][0]]["stage"] % 2 == 1 for k in (1, 2, 3)),
         "bank 0 starts with forward F0; banks 1-3 start with a backward call")
    original_f0 = [(0, 16, [f0_init[0]])] + original[1:]
    variant_f0 = [(0, 16, [f0_init[0]])] + variant[1:]
    out["init0_via_f0"] = {
        "init_capture_levels": f0_init,
        "original": {name: law_mass(cons, "original", f0_init) for name, cons in timings.items()},
        "all_initial": {name: law_mass(cons, "all_initial", f0_init) for name, cons in timings.items()},
        "thmB_own_bank": {name: {"original": theorem_b(original_f0, cons)["own_bank"],
                                 "all_initial": theorem_b(variant_f0, cons)["own_bank"]} for name, cons in timings.items()},
        "thmB_one_level_end": {"original": theorem_b(original_f0, end)["one_level_cut_sum"],
                               "all_initial": theorem_b(variant_f0, end)["one_level_cut_sum"]}}
    # Revival terms: what remains if the INIT information were free.
    out["revival_terms"] = {
        "dA_term": {name: sum(catch_up([r["capture_level"]] * 4, cons, r["bank"], 8) for r in da)
                    for name, cons in timings.items()},
        "all_initial_reads_term": {name: sum(COORDS_PER_LEVEL * 8 * min(abs(cons[x["bank"]] - h)
                                                                        for h in x["levels_held_while_initial"])
                                             for x in reads) for name, cons in timings.items()}}
    touch = min(e["source_event"] for e in events
                if (e["kind"] == "local_cover_sweep" and stage_pair[e["stage"]] == 3)
                or (e["kind"] == "idle_cover_sweep" and e["pair"] == 3 and e["to_level"] > e["from_level"])
                or (e["kind"] == "bridge" and 3 in (e["src"], e["dst"])))
    if mutate == "witness_window":
        touch += 1
    calls = [e["stage"] for e in events if e["kind"] == "local_cover_sweep" and e["source_event"] < touch]
    out["zero_witness"] = {"pair": 3, "side": "Y (replica-0 families 784..895)", "capture": "entry",
                           "consumer_before_event": touch, "consumer_before_time": events[touch]["time"],
                           "calls_in_window": calls,
                           "levels_advanced": lv_before(timeline, touch)[3] - timeline[0][2][3],
                           "record_copies_an_untouched_stream": True,
                           "law_mass_per_array": catch_up(timeline[0][2], lv_before(timeline, touch), 3, 1),
                           "S_per_array": len(calls), "C_mass_per_array": 8 * len(calls)}
    # Lagging-pair records do not separate the law from (C): a pair-0 X_(0,U) record captured after event 13
    # and consumed at the end advances six levels in three calls, but X_(0,U) is last written at event 6; afterwards only
    # idle sweep 21 (a transport: the logical row is kept), bridge 27 with src = 0 (reads X_(0,U)) and
    # the terminals act on it. The record duplicates -final Y_(0,U), which the contract observes, so
    # rho_r = 0 and the law charges 0, not 48.
    x0_writes = [e["source_event"] for e in events
                 if (e["kind"] == "local_cover_sweep" and stage_pair[e["stage"]] == 0)
                 or (e["kind"] == "bridge" and e["dst"] == 0)]
    after = [e["kind"] + ("" if e["kind"] != "bridge" else " src=%d dst=%d" % (e["src"], e["dst"]))
             for e in events[14:]
             if (e["kind"] == "idle_cover_sweep" and e["pair"] == 0)
             or (e["kind"] == "bridge" and 0 in (e["src"], e["dst"])) or e["kind"].startswith("terminal")]
    out["lagging_record_example"] = {
        "record": "X_(0,U) captured after event 13, consumed at the end",
        "capture_level": lv_after(timeline, 13)[0], "levels_advanced": end[0] - lv_after(timeline, 13)[0],
        "calls_after_capture": sum(1 for e in events[14:] if e["kind"] == "local_cover_sweep"),
        "last_write_event_of_X0": max(x0_writes), "pair0_events_after_capture": after,
        "law_mass_if_independent_row": catch_up(lv_after(timeline, 13), end, 0, 1),
        "law_mass": 0, "C_mass": 8 * 3}
    return out


def theorem_b(captures, consumers, mutate=None, need_rows=62):
    """Theorem-B delivery floors (coordinates per owner per replica) for one consumer timing.

    captures: (bank, rows, admissible capture levels); consumers: consumer level of each bank.
    - one_level_cut_sum: Lemma 1 summed over the cuts, sum_j max(0, 62 - n+_j), with n+_j the stated rows
      captured at or above cut j (each capture at its most favourable admissible level). Valid only when every
      bank decodes at one level; None otherwise.
    - own_bank: each capture serves only the bank whose derived decoder uses it and the 62 rows split freely
      over the banks: the cheapest 62 own-bank climbs (equal to the minimum over splits, as each bank's
      cost is a sum of its cheapest rows).
    - count_only: no assignment premise; each row may go to any consumer in either direction (P_glob): the
      cheapest delivery of 62 rows that would meet Theorem B's count if the captures are independent. An
      argument using only the count and the capture heights cannot force more than this at that timing.
    """
    own, free = [], []
    for bank, rows, levels in captures:
        climbs = [consumers[bank] - h for h in levels if h <= consumers[bank]]
        need(climbs, "every stated capture has an admissible level at or below its own bank's consumer")
        own += [COORDS_PER_LEVEL * min(climbs)] * rows
        free += [COORDS_PER_LEVEL * min(abs(c - h) for c in consumers for h in levels)] * rows
    if mutate == "thmB_free_assignment":
        own = free
    own.sort()
    free.sort()
    need(len(own) == 88, "88 stated arrays per owner per replica")
    out = {"own_bank": sum(own[:need_rows]), "count_only": sum(free[:need_rows]), "one_level_cut_sum": None}
    if len(set(consumers)) == 1:
        top = COORDS_PER_LEVEL * (consumers[0] + 1)
        heights = [(rows, COORDS_PER_LEVEL * (max(h for h in levels if h <= consumers[0]) + 1))
                   for _, rows, levels in captures]
        out["one_level_cut_sum"] = sum(max(0, need_rows - sum(n for n, h in heights if h >= j))
                                       for j in range(1, top + 1))
    return out


def hosting_checks(hosted, r, mutate=None):
    """Hosted helper residuals also change idle frames (idle-axis hosting moves factors to their
    invocation time), so part of a later level can land on an idle family early. Every instant the
    routes use must sit at an exact level, checked in both directions (replica 0):
     - no overshoot: each residual hosted on the pair by then belongs to a sweep that has already
       reached that level;
     - no undershoot: each residual of a sweep that has already reached that level has landed.
    The witness streams host nothing in their window. independent_check.py replays per-family heights
    (both tie conventions, all 16 replicas) as a second method."""
    slots = [dict(x) for x in hosted["hosting"]["pooled_slots"] if x["owner_replica"] == 0]
    sweep_to = {}
    for e in hosted["execution_schedule"]:
        if e.get("replica") == 0 and e["kind"] == "idle_cover_sweep":
            for c in e["child_indices"]:
                sweep_to[c] = (e["pair"], e["from_level"], e["to_level"], e["source_event"])
    if mutate == "undershoot":         # delay one pair-1 residual of sweep 2 (levels -1 -> 1) to time 25
        x = next(x for x in slots if 224 <= x["family"] < 448 and sweep_to[x["child"]][3] == 2)
        x["time"] = 25
    idle = {(c["family"], c["child"]): c for c in hosted["idle_children"] if c["replica"] == 0}
    zw = r["zero_witness"]
    limit = zw["consumer_before_time"] + (17 if mutate == "hosting_window" else 0)
    y3 = range(784, 896)
    early_y3 = [x for x in slots if x["family"] in y3 and x["time"] < limit]
    need(not early_y3, "no hosted residual on pair-3 Y families before the witness consumer")
    need(all(idle[(f, 10)]["hosted"] == 0 and idle[(f, 10)]["rank"] == 48 for f in y3),
         "pair-3 Y sweep -1 -> 5 is an unhosted rank-48 idle child")
    early_x3 = [x for x in slots if 672 <= x["family"] <= 783 and x["time"] < limit]
    times = {e["source_event"]: e["time"] for e in hosted["execution_schedule"] if e.get("replica") == 0}
    instants = [("INIT capture", x["bank"], times[x["capture_before_event"]], x["capture_level"]) for x in r["INIT64"]]
    instants += [("d_A capture", x["bank"], times[x["capture_after_event"]], x["capture_level"]) for x in r["d_A"]]
    instants += [("P_early consumer", k, times[ev], lv)
                 for k, (ev, lv) in enumerate(zip(r["early_consumer_after_events"], r["early_consumer_levels"]))]
    for x in r["all_initial_variant"]["reads"]:
        t = times[x["early_read_after_event"]]
        instants.append(("all-initial read", x["bank"] + 1, t, x["early_read_level"]))
        instants.append(("all-initial consumer", x["bank"], t, x["early_consumer_level"]))
    instants += [("P_Y consumer", k, times[ev], lv)
                 for k, (ev, lv) in enumerate(zip(r["x_last_write_event"], r["y_consumer_levels"]))]
    over = under = 0
    distinct = set()
    for label, pair, t, level in instants:
        for i, x in enumerate(slots):
            if not 224 * pair <= x["family"] < 224 * (pair + 1):
                continue
            sp, frm, to, _ = sweep_to[x["child"]]
            if x["time"] <= t:
                need(sp == pair and to <= level, "hosted residual before a %s belongs to an already-reached level" % label)
                over += 1
                distinct.add(i)
            elif sp == pair and frm < to <= level:
                raise CheckFailure("hosted residual of an already-reached level lands after a %s (undershoot)" % label)
            else:
                under += 1
    return {"pair3_Y_hosted_slots_in_window": 0, "pair3_X_hosted_slots_in_window": len(early_x3),
            "instants_checked": len(instants), "slot_instant_checks": over, "undershoot_slot_checks": under,
            "distinct_slots_checked": len(distinct),
            "route_capture_slot_checks": sum(1 for label, pair, t, level in instants[:7] for x in slots
                                             if 224 * pair <= x["family"] < 224 * (pair + 1) and x["time"] <= t)}


def array_calls(dA_lifetimes=(8, 5, 3)):
    return 16 * (9 + 6 + 4 + 2) + 8 * sum(dA_lifetimes)


# ------------------------------------------------------------------ 5. pricing
def load_ceiling():
    sys.path.insert(0, str(ROOT / "research/complex-local-word-ceiling"))
    try:
        import ceiling
    finally:
        sys.path.pop(0)
    need(hashlib.sha256(Path(ceiling.__file__).read_bytes()).hexdigest() ==
         PINS["research/complex-local-word-ceiling/ceiling.py"], "imported ceiling.py is the pinned file")
    return ceiling


def qq16_profile():
    core = {r: n for r, n in SELECTED.items() if r != 8}
    need(sum(r * n for r, n in core.items()) == 5522, "retained QQ16 core mass 5522")
    back = dict(core)
    back[1] += 24
    fwd = dict(core)
    fwd[1] += 8
    need(sum(r * n for r, n in back.items()) == 5546 and sum(r * n for r, n in fwd.items()) == 5530,
         "QQ16 native masses 5546 (B) / 5530 (F)")
    return {r: Q(5 * fwd[r] + 4 * back[r], 9) for r in core}


def priced(units, pricing):
    local = dict(qq16_profile())
    n = Q(units, STAGES)
    if pricing == "rank8":
        local[8] = local.get(8, 0) + n / 8
    elif pricing != "idle":
        raise ValueError(pricing)
    return local, n


def kappa_cap(C, units, pricing):
    local, centre = priced(units, pricing)
    try:
        a = C.ceiling(local, M, FAMILIES, STAGES, centre, grid=GRID)[1]
    except ValueError:
        return None
    return a / (1 + a)


def beats(C, units, pricing, kappa):
    """Certified: does the stated relaxation exceed `kappa` (relax(a_t) < 1 at a_t = kappa/(1-kappa))?"""
    local, centre = priced(units, pricing)
    try:
        lo, hi = C.relax(local, M, FAMILIES, STAGES, centre, kappa / (1 - kappa))
    except ValueError:
        return False                   # local word pays more than the coverage law allows
    need(hi < 1 or lo > 1, "enclosure separates the comparison point")
    return hi < 1


def breakeven(C, pricing, kappa, step):
    lo, hi = 0, 1 << 13
    need(beats(C, 0, pricing, kappa) and not beats(C, hi * step, pricing, kappa), "bracket")
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if beats(C, mid * step, pricing, kappa):
            lo = mid
        else:
            hi = mid
    return lo


def pricing_checks(C, route_mass):
    out = {}
    free = kappa_cap(C, 0, "idle")
    need(abs(free - Q("0.0047020509675915")) < Q(1, 10 ** 13), "free-controller cap 0.0047020509675915")
    out["free_controller_C0_kappa_cap"] = "%.16f" % free
    need(kappa_cap(C, 895, "idle") is not None and kappa_cap(C, 896, "idle") is None, "896 threshold (idle)")
    # PR2470 (qq16-cut-retention-census) screened retained copies under the assumed centre-like convention: at C = 0
    # the last coordinate-call count with any positive saving is 111. Corollary 4 derives that convention for
    # current-frame consumers; 8 x 111 = 888 < 896 <= 8 x 112 is the same exact threshold.
    need(kappa_cap(C, 8 * 111, "rank8") is not None and kappa_cap(C, 8 * 112, "rank8") is None,
         "896 threshold (rank-8) = PR2470's C = 0 centre-like limit of 111 coordinate-calls")
    out["no_saving_threshold_units_per_replica"] = 896
    centre = kappa_cap(C, 576, "rank8")
    local, _ = priced(576, "rank8")
    need(local[8] == 8 and centre == (lambda a: a / (1 + a))(
        C.ceiling({**qq16_profile(), 8: Q(8)}, M, FAMILIES, STAGES, 64, grid=GRID)[1]),
        "576 rank-8 units per replica = eight rank-8 centre copies per call with C = 64")
    out["centre_path_576_kappa_cap"] = "%.16f" % centre
    be_s = breakeven(C, "idle", PR2474_KAPPA, 1)
    be_c = breakeven(C, "rank8", PR2474_KAPPA, 8)
    need((be_s, be_c) == PRICE_GATE_BREAKEVENS, "#1166 price-gate break-evens 573 (S) / 71 (C) reproduced")
    need(kappa_cap(C, sum(16 * x for x in PRICE_GATE_INIT_LIFETIMES) + sum(8 * x for x in PRICE_GATE_DA_LIFETIMES),
                   "idle") == PRICE_GATE_STORAGE_READS_FALSE,
         "S-priced 464 array-calls equals PRICE-GATE.json storage_readsFalse exactly")
    need(kappa_cap(C, 573, "idle") > PR2474_KAPPA >= kappa_cap(C, 574, "idle"), "ceiling agrees at 573/574")
    need(kappa_cap(C, 568, "rank8") > PR2474_KAPPA >= kappa_cap(C, 576, "rank8"), "ceiling agrees at 71/72")
    out["breakeven_vs_PR2474"] = {"S_array_calls": be_s, "C_array_calls": be_c}
    table = {}
    for name, kappa in (("selected_1094", SELECTED_KAPPA), ("PR2474", PR2474_KAPPA), ("PR2843", PR2843_KAPPA),
                        ("PR2848", PR2848_KAPPA), ("PR2857", PR2857_KAPPA), ("bit_endpoint_PR589", BIT_ENDPOINT)):
        table[name] = {"kappa": str(kappa), "idle_units": breakeven(C, "idle", kappa, 1),
                       "rank8_units": 8 * breakeven(C, "rank8", kappa, 8)}
    rows = sorted(table.values(), key=lambda v: Q(v["kappa"]))
    need(all(a["idle_units"] >= b["idle_units"] and a["rank8_units"] >= b["rank8_units"] for a, b in zip(rows, rows[1:])),
         "break-even mass is non-increasing in the comparison kappa")
    out["mass_breakeven_units_per_replica"] = table
    out["routes"] = {}
    for name, mass in route_mass.items():
        k_idle, k_r8 = kappa_cap(C, mass, "idle"), kappa_cap(C, mass, "rank8")
        out["routes"][name] = {"units_per_replica": mass,
                               "idle_priced_kappa_cap": None if k_idle is None else "%.16f" % k_idle,
                               "rank8_priced_kappa_cap": None if k_r8 is None else "%.16f" % k_r8}
    return out


# ------------------------------------------------------------------ 6. exact frame model
class Lattice:
    """Subspaces of GF(p)^n, indexed; join with one vector; membership."""

    def __init__(self, p, n):
        self.p, self.n = p, n
        self.vecs = list(itertools.product(range(p), repeat=n))
        self.zero = tuple([0] * n)
        self.subs, self.index = [], {}
        self._add(frozenset([self.zero]))
        frontier = [0]
        while frontier:
            nxt = []
            for s in frontier:
                for v in self.vecs:
                    t = self.close(self.subs[s] | {v})
                    if t not in self.index:
                        nxt.append(self._add(t))
            frontier = nxt
        self.join = [[self.index[self.close(s | {v})] for v in self.vecs] for s in self.subs]
        self.vid = {v: i for i, v in enumerate(self.vecs)}
        self.dim = [round(math.log(len(s), p)) for s in self.subs]

    def _add(self, s):
        self.index[s] = len(self.subs)
        self.subs.append(s)
        return self.index[s]

    def close(self, vectors):
        space = {self.zero}
        changed = True
        vectors = set(vectors)
        while changed:
            changed = False
            for a in list(space):
                for b in vectors:
                    for c in range(1, self.p):
                        w = tuple((x + c * y) % self.p for x, y in zip(a, b))
                        if w not in space:
                            space.add(w)
                            changed = True
        return frozenset(space)

    def span(self, vectors):
        return self.index[self.close(set(vectors))]


def bfs_all(L, start, H):
    dist = {start: 0}
    queue = deque([start])
    while queue:
        state = queue.popleft()
        d = dist[state]
        for h in range(H + 1):
            for v in L.subs[state[h]]:
                if v == L.zero:
                    continue
                vi = L.vid[v]
                for g in (h - 1, h + 1):
                    if 0 <= g <= H and v not in L.subs[state[g]]:
                        nxt = list(state)
                        nxt[g] = L.join[state[g]][vi]
                        nxt = tuple(nxt)
                        if nxt not in dist:
                            dist[nxt] = d + 1
                            queue.append(nxt)
    return dist


def min_mass(L, dist, demand):
    best = None
    for state, d in dist.items():
        if all(v in L.subs[state[h]] for v, h in demand) and (best is None or d < best):
            best = d
    need(best is not None, "demand unreachable")
    return best


def cut_bound(L, entry, demand, H, directions=("up", "down")):
    total = 0
    for j in range(1, H + 1):
        for side, keep in (("up", lambda h: h >= j), ("down", lambda h: h < j)):
            if side not in directions:
                continue
            e = [v for v, h in entry if keep(h)]
            d = [v for v, h in demand if keep(h)]
            total += L.dim[L.span(e + d)] - L.dim[L.span(e)]
    return total


def meeting_formula(L, R, P, O, hr, hp, hc):
    rho_r = L.dim[L.span(P + O)] - L.dim[L.span(P)]
    rho_p = L.dim[L.span(R + O)] - L.dim[L.span(R)]
    rho_o = L.dim[L.span(O)]
    return min(rho_r * abs(x - hr) + rho_p * abs(x - hp) + rho_o * abs(x - hc)
               for x in range(min(hr, hp, hc), max(hr, hp, hc) + 1))


def basis(L, s):
    out = []
    for v in sorted(L.subs[s]):
        if v != L.zero and v not in L.subs[L.span(out)]:
            out.append(v)
    return out


def frame_model_checks():
    stats = {"domains": [], "record_partner_instances": 0, "general_instances": 0,
             "general_tight": 0, "upward_only_failures": 0}
    for p, n, H in ((2, 2, 3), (3, 2, 2), (2, 3, 2)):
        L = Lattice(p, n)
        pairs = [(a, b) for a, b in itertools.product(range(len(L.subs)), repeat=2)
                 if len(L.subs[a] & L.subs[b]) == 1]
        stats["domains"].append({"field": "GF(%d)" % p, "dim": n, "levels": H + 1, "subspaces": len(L.subs),
                                 "independent_RP_pairs": len(pairs), "coverage": "complete"})
        before = stats["record_partner_instances"]
        for R_s, P_s in pairs:
            R, P = basis(L, R_s), basis(L, P_s)
            RP = L.subs[L.span(R + P)]
            outs = [o for o in range(len(L.subs)) if L.subs[o] <= RP and L.dim[o] > 0]
            for hr, hp in itertools.product(range(H + 1), repeat=2):
                st = [L.span([])] * (H + 1)
                st[hr] = L.span(R + (P if hp == hr else []))
                if hp != hr:
                    st[hp] = L.span(P)
                dist = bfs_all(L, tuple(st), H)
                entry = [(v, hr) for v in R] + [(v, hp) for v in P]
                for o in outs:
                    O = basis(L, o)
                    for hc in range(H + 1):
                        demand = [(v, hc) for v in O] + [(v, hp) for v in P]
                        opt = min_mass(L, dist, demand)
                        lb = cut_bound(L, entry, demand, H)
                        mf = meeting_formula(L, R, P, O, hr, hp, hc)
                        need(lb <= opt, "Lemma 1 soundness")
                        need(opt == lb == mf, "Proposition 3 exactness %s" % ((p, n, H, hr, hp, hc),))
                        if cut_bound(L, entry, demand, H, ("up",)) != opt:
                            stats["upward_only_failures"] += 1
                        stats["record_partner_instances"] += 1
        stats["domains"][-1]["record_partner_instances"] = stats["record_partner_instances"] - before
        if (p, n, H) == (2, 2, 3):
            placed = [(v, h) for v in L.vecs if v != L.zero for h in range(H + 1)]
            sets = list(itertools.chain(itertools.combinations(placed, 1), itertools.combinations(placed, 2)))
            for e_rows in sets:
                st = [L.span([])] * (H + 1)
                for v, h in e_rows:
                    st[h] = L.join[st[h]][L.vid[v]]
                dist = bfs_all(L, tuple(st), H)
                avail = L.subs[L.span([v for v, _ in e_rows])]
                for d_rows in sets:
                    if all(v in avail for v, _ in d_rows):
                        opt = min_mass(L, dist, list(d_rows))
                        lb = cut_bound(L, list(e_rows), list(d_rows), H)
                        need(lb <= opt, "Lemma 1 soundness (general)")
                        stats["general_instances"] += 1
                        stats["general_tight"] += int(lb == opt)
    need(stats["upward_only_failures"] > 0, "negative control: an upward-only bound must fail somewhere")
    return stats


# ------------------------------------------------------------------ 7. tensor toy
HAD = ((1, 1), (1, -1))


def apply_axis(x, axis, inverse=False):
    y = [Q(0)] * 4
    for i in range(4):
        bits = [i & 1, (i >> 1) & 1]
        for b in (0, 1):
            jb = list(bits)
            jb[axis] = b
            y[i] += Q(HAD[bits[axis]][b]) * (Q(1, 2) if inverse else 1) * x[jb[0] + 2 * jb[1]]
    return y


def in_frame(x, axes):
    for a in axes:
        x = apply_axis(x, a)
    return x


def add(*xs):
    return [sum(t) for t in zip(*xs)]


def tensor_toy():
    rng = random.Random(20261016)
    naive_wrong = wrong_axis = 0
    trials = 25
    for _ in range(trials):
        x = [Q(rng.randint(-9, 9), rng.randint(1, 5)) for _ in range(4)]
        dx = [Q(rng.randint(-9, 9), rng.randint(1, 5)) for _ in range(4)]
        record = in_frame(x, [0])                       # captured after call 1 (axis 0 advanced)
        current = in_frame(add(x, dx), [0, 1])          # after call 2 (axis 1 advanced)
        want = in_frame(add(x, x, dx), [0, 1])          # consumer: x + (x + dx) in the current frame
        naive_wrong += add(record, current) != want
        need(add(apply_axis(record, 1), current) == want, "paid axis-1 catch-up repairs the output")
        wrong_axis += add(apply_axis(record, 0), current) != want
        down = apply_axis(current, 1, inverse=True)     # partner descends to the record's frame
        need(apply_axis(add(record, down), 1) == want, "partner descent + output climb also repairs it")
        need(add(record, in_frame(x, [0])) == in_frame(add(x, x), [0]), "same-frame consumer needs no catch-up")
    need(naive_wrong == trials, "negative control: omitting catch-up must give a wrong output")
    need(wrong_axis == trials, "negative control: catch-up on the wrong axis must fail")
    return {"trials": trials, "naive_wrong": naive_wrong, "wrong_axis_wrong": wrong_axis, "repaired_correct": trials}


# ------------------------------------------------------------------ 8. negative controls
def expect_failure(label, fn, reason):
    """A negative control must fail, and for its stated reason (the message must contain `reason`)."""
    try:
        fn()
    except CheckFailure as exc:
        need(reason in str(exc), "negative control %r failed for another reason: %s" % (label, exc))
        return label
    raise CheckFailure("negative control unexpectedly passed: " + label)


def equal(name, got, want):
    need(got == want, "%s = %r (expected %r)" % (name, got, want))


def negative_controls(hosted, base, events, C):
    tl, sp = level_timeline(hosted, base, events)

    def mutated(kind):
        return routes(tl, events, sp, mutate=kind)

    r = routes(tl, events, sp)
    original = [(x["bank"], x["rows"], [x["capture_level"]]) for x in r["INIT64"] + r["d_A"]]
    reversed27 = [dict(e, src=1, dst=0) if e["source_event"] == 27 else e for e in events]
    out = [
        expect_failure("idle sweep to_level +1", lambda: level_timeline(hosted, base, events, "idle_to_level"),
                       "base idle children: eight coordinates per level (event 5)"),
        expect_failure("PR2540 rows 16 -> 15",
                       lambda: equal("PR2540 mass", mutated("pr2540_rows")["PR2540_early_records"]["mass"], 128),
                       "PR2540 mass = 120"),
        expect_failure("PR2540 two incidences",
                       lambda: equal("PR2540 mass", mutated("pr2540_incidence")["PR2540_early_records"]["mass"], 128),
                       "PR2540 mass = 256"),
        expect_failure("INIT bank-1 capture level -1",
                       lambda: equal("INIT64 + d_A mass", mutated("init_capture_level")["INIT64_plus_dA_mass"], 3648),
                       "INIT64 + d_A mass = 4032"),
        expect_failure("zero witness extended past first pair-3 touch",
                       lambda: equal("zero-advance law mass per array",
                                     mutated("witness_window")["zero_witness"]["law_mass_per_array"], 0),
                       "zero-advance law mass per array = 48"),
        expect_failure("uniform lifetimes give 464 array-calls", lambda: equal("array-calls", array_calls((7, 5, 3)), 464),
                       "array-calls = 456"),
        expect_failure("witness window stretched into pair-3 Y hosting (time + 17)",
                       lambda: hosting_checks(hosted, r, mutate="hosting_window"),
                       "no hosted residual on pair-3 Y families before the witness consumer"),
        expect_failure("hosted residual of sweep 2 delayed to time 25 (undershoot)",
                       lambda: hosting_checks(hosted, r, mutate="undershoot"),
                       "(undershoot)"),
        expect_failure("895 units/replica has no saving",
                       lambda: equal("no saving at 895 units", kappa_cap(C, 895, "idle") is None, True),
                       "no saving at 895 units = False"),
        expect_failure("break-even 574 (S) against PR2474",
                       lambda: equal("beats PR2474 at 574 idle units", beats(C, 574, "idle", PR2474_KAPPA), True),
                       "beats PR2474 at 574 idle units = False"),
        expect_failure("all-initial read of X_(1,U) barred from bank 0's consumer level",
                       lambda: equal("all-initial early mass",
                                     mutated("allinit_read_level")["all_initial_variant"]["early_mass"], 1152),
                       "all-initial early mass = 1216"),
        expect_failure("bridge 27 reversed (dst = 0): X_(0,U) written after the capture",
                       lambda: equal("last write of X_(0,U)",
                                     routes(tl, reversed27, sp)["lagging_record_example"]["last_write_event_of_X0"], 6),
                       "last write of X_(0,U) = 27"),
        expect_failure("Theorem B at P_early without the own-bank premise",
                       lambda: equal("Theorem B P_early floor",
                                     theorem_b(original, r["early_consumer_levels"], "thmB_free_assignment")["own_bank"], 800),
                       "Theorem B P_early floor = 112"),
        expect_failure("P_early as a floor for decoders without the decoder-timing premise",
                       lambda: need(r["without_decoder_timing_premise"]["after_own_last_capture"]["original"]
                                    >= r["INIT64_plus_dA_early_consumer_mass"],
                                    "P_early bounds decoders right after each bank's own last capture"),
                       "P_early bounds decoders right after each bank's own last capture"),
    ]
    return out


# ------------------------------------------------------------------ main
def main(argv):
    result = {"schema": "retained-array-catch-up/1", "sources": check_sources()}
    hosted, base = load_templates()
    events = replica_events(hosted, base)
    timeline, stage_pair = level_timeline(hosted, base, events)
    result["levels"] = [{"after": "entry" if s is None else "event %d %s" % (s, k), "pairs_0_3": list(lv)}
                        for k, s, lv in timeline]
    r = routes(timeline, events, stage_pair)
    need(r["PR2540_early_records"]["mass"] == 128, "PR2540: 16 records x one level = 128 (its 16 H8)")
    need([x["capture_level"] for x in r["INIT64"]] == [-1, 2, 4, 6], "INIT capture levels -1/2/4/6")
    need([x["mass"] for x in r["INIT64"]] == [1152, 768, 512, 256], "INIT climbs 72/48/32/16 per array")
    need([x["capture_level"] for x in r["d_A"]] == [1, 3, 5], "d_A capture levels 1/3/5")
    need([x["mass"] for x in r["d_A"]] == [448, 320, 192], "d_A climbs 56/40/24 per array")
    need(r["INIT64_plus_dA_mass"] == 3648 and r["d_A_only_mass"] == 960, "INIT64 + d_A 3648; d_A alone 960")
    need(r["x_last_write_event"] == [6, 27, 26, 25] and r["y_consumer_levels"] == [2, 8, 8, 8]
         and all(r["x_last_write_levels_all_pairs"][k] == [8, 8, 8, 8] for k in (1, 2, 3)),
         "X_(k,U) last written at events 6/27/26/25; bridges 25-27 run with every pair at level 8 (P_Y levels 2/8/8/8)")
    need(r["INIT64_plus_dA_y_mass"] == 2496, "earliest timing the observed Y fields allow (P_Y): 2496")
    need(r["early_consumer_levels"] == [2, 4, 6, 8] and r["INIT64_plus_dA_early_consumer_mass"] == 1344,
         "P_early (each bank after its last local call): 1344 = 8 per later data incidence")
    tb = r["theorem_B"]
    need(tb["P_final"]["original"] == {"one_level_cut_sum": 1952, "own_bank": 1952, "count_only": 1952}
         and tb["P_final"]["all_initial"] == {"one_level_cut_sum": 1824, "own_bank": 1824, "count_only": 1824},
         "Theorem B per cut with one consumer level (P_final): 1952 / 1824 (= cheapest 62 climbs)")
    need((tb["P_Y"]["original"]["own_bank"], tb["P_Y"]["all_initial"]["own_bank"],
          tb["P_early"]["original"]["own_bank"], tb["P_early"]["all_initial"]["own_bank"]) == (1344, 1216, 800, 608),
         "Theorem B with the own-bank premise: 1344 / 1216 (P_Y), 800 / 608 (P_early)")
    need((tb["P_Y"]["original"]["count_only"], tb["P_Y"]["all_initial"]["count_only"],
          tb["P_early"]["original"]["count_only"], tb["P_early"]["all_initial"]["count_only"]) == (608, 544, 112, 0),
         "Theorem B count-only deliveries: 608 / 544 (P_Y), 112 / 0 (P_early)")
    need(all(tb[t][v]["one_level_cut_sum"] is None for t in ("P_Y", "P_early") for v in ("original", "all_initial")),
         "the one-level cut sum is not applied to multi-level timings")
    zw = r["zero_witness"]
    need(zw["law_mass_per_array"] == 0 and zw["calls_in_window"] == [0, 1, 2, 3, 4, 5]
         and zw["consumer_before_event"] == 14, "zero witness: pair 3 untouched through stages 0..5")
    need(zw["levels_advanced"] == 0, "zero-advance window: pair 3 stays at level -1")
    lag = r["lagging_record_example"]
    need(lag["last_write_event_of_X0"] == 6 and lag["levels_advanced"] == 6 and lag["calls_after_capture"] == 3
         and lag["law_mass_if_independent_row"] == 48 and lag["C_mass"] == 24
         and lag["pair0_events_after_capture"] == ["idle_cover_sweep", "bridge src=0 dst=1",
                                                   "terminal_Y_translations", "terminal"],
         "lagging example: X_(0,U) last written at event 6, so the record duplicates an observed row")
    ai = r["all_initial_variant"]
    need([x["final_mass"] for x in ai["reads"]] == [384, 256, 128] and [x["early_mass"] for x in ai["reads"]] == [0, 0, 0]
         and [x["early_read_level"] for x in ai["reads"]] == [2, 4, 6]
         and [x["early_read_after_event"] for x in ai["reads"]] == [5, 11, 17],
         "all-initial reads: 384/256/128 at the end; 0 at P_early (pair k+1 reaches bank k's level first)")
    need((ai["final_mass"], ai["y_mass"], ai["early_mass"]) == (3456, 2304, 1152)
         and [x["y_mass"] for x in ai["reads"]] == [0, 256, 128], "all-initial variant 3456 / 2304 / 1152")
    fh = r["forward_histories_addon"]
    need(fh["final_mass_range"] == [768, 1024] and fh["y_mass_range"] == [384, 640] and fh["early_mass_range"] == [0, 256]
         and fh["f2_f4_f6_only"] == {"P_final": [768, 960], "P_Y": [384, 576], "P_early": [0, 192]},
         "forward histories f2/f4/f6/f8 would add 768..1024 (P_final), 384..640 (P_Y), 0..256 (P_early)")
    wo = r["without_decoder_timing_premise"]
    need(wo == {"after_own_last_capture": {"consumer_levels": [1, 3, 5, 6], "original": 512, "all_initial": 512},
                "after_backward_call": {"consumer_levels": [1, 3, 5, 7], "original": 640, "all_initial": 640}},
         "without the decoder-timing premise: 512 (after own last capture) / 640 (after each backward call)")
    f0 = r["init0_via_f0"]
    need(f0["init_capture_levels"] == [0, 2, 4, 6]
         and f0["original"] == {"P_final": 3520, "P_Y": 2368, "P_early": 1216}
         and f0["all_initial"] == {"P_final": 3328, "P_Y": 2176, "P_early": 1024}
         and f0["thmB_own_bank"]["P_Y"] == {"original": 1216, "all_initial": 1088}
         and f0["thmB_own_bank"]["P_early"] == {"original": 800, "all_initial": 608}
         and f0["thmB_one_level_end"] == {"original": 1952, "all_initial": 1824},
         "bank 0's INIT via f0: every P_rank total falls by 128; own-bank P_Y 1216 / 1088; others unchanged")
    rt = r["revival_terms"]
    need(rt == {"dA_term": {"P_final": 960, "P_Y": 576, "P_early": 192},
                "all_initial_reads_term": {"P_final": 768, "P_Y": 384, "P_early": 0}},
         "revival terms: d_A 960 / 576 / 192; all-initial reads 768 / 384 / 0")
    r["hosting"] = hosting_checks(hosted, r)
    need(r["hosting"]["pair3_X_hosted_slots_in_window"] == 160, "pair-3 X streams host 160 residuals in the window")
    need(r["hosting"]["route_capture_slot_checks"] == 4173 and r["hosting"]["instants_checked"] == 21,
         "hosting checked at 21 instants (4,173 slot checks at the seven route captures)")
    centre_path = 8 * 8 * STAGES
    pr2197 = 8 * 18
    h_U1, h_L, h_q, h_I = 17, 9, 1, 0
    need(centre_path == 576 and pr2197 == 144, "centre path 576 / PR2197 144")
    need(224 * (h_U1 - h_L) == 1792 and 112 * (h_U1 - h_q) + 112 * (h_U1 - h_I) == 3696, "PR2678 1792 / 3696")
    need(h_L == 9 and h_U1 - h_L == COORDS_PER_LEVEL, "PR2540 frames: F_L nine axes, F_U1 seventeen (one level)")
    published, uniform = array_calls(), array_calls((7, 5, 3))
    need(published == 464 and uniform == 456 and 8 * uniform == r["INIT64_plus_dA_mass"],
         "array-calls 464 published / 456 uniform; law = 8 x uniform array-calls")
    r["array_calls"] = {"published": published, "uniform_lifetime": uniform, "S_units_published": published,
                        "C_mass_published": 8 * published, "C_mass_uniform": 8 * uniform}
    r["controls"] = {"PR2540": 128, "PR2197": pr2197, "PR2678_common_FL": 1792, "PR2678_entry": 3696,
                     "centre_path_per_replica": centre_path}
    # Re-check only of #2707's own published comparison (research/qq16-line-normalized-decoder, incorporated on
    # main after this package's base): 336 H1 versus PR2540's 224 H1 + 16 H8 differ by 112 H1 - 16 H8, and
    # 16 * 8^(1-a) > 112 for 0 <= a <= 1/16 because 8^(15/16) > 7, i.e. 8^15 > 7^16 (exact integers).
    need(8 ** 15 > 7 ** 16 and 336 - 224 == 112 and 16 * 8 == 128, "PR2707 numerator sign: 8^15 > 7^16")
    r["qq16_gate"] = {"retained_caller_retention_mass": 128, "retained_caller_H8": 16,
                      "zero_retention_H1_minus_retained_H1": 112, "sign_certificate": "8^15 > 7^16"}
    result["routes"] = r
    C = load_ceiling()
    tb = r["theorem_B"]
    result["pricing"] = pricing_checks(C, {
        "INIT64_plus_dA_law": r["INIT64_plus_dA_mass"], "d_A_only_law": r["d_A_only_mass"],
        "INIT64_plus_dA_earliest_Y_law": r["INIT64_plus_dA_y_mass"],
        "INIT64_plus_dA_early_relaxation_law": r["INIT64_plus_dA_early_consumer_mass"],
        "INIT64_plus_dA_S_published": published, "INIT64_plus_dA_C_published": 8 * published,
        "all_initial_law": ai["final_mass"], "all_initial_earliest_Y_law": ai["y_mass"],
        "all_initial_early_relaxation_law": ai["early_mass"],
        "thmB_one_level_end": tb["P_final"]["original"]["one_level_cut_sum"],
        "all_initial_thmB_one_level_end": tb["P_final"]["all_initial"]["one_level_cut_sum"],
        "thmB_own_bank_earliest_Y": tb["P_Y"]["original"]["own_bank"],
        "all_initial_thmB_own_bank_earliest_Y": tb["P_Y"]["all_initial"]["own_bank"],
        "thmB_own_bank_early_relaxation": tb["P_early"]["original"]["own_bank"],
        "all_initial_thmB_own_bank_early_relaxation": tb["P_early"]["all_initial"]["own_bank"],
        "thmB_count_only_earliest_Y": tb["P_Y"]["original"]["count_only"],
        "all_initial_thmB_count_only_earliest_Y": tb["P_Y"]["all_initial"]["count_only"],
        "thmB_count_only_early_relaxation": tb["P_early"]["original"]["count_only"],
        "all_initial_thmB_count_only_early_relaxation": tb["P_early"]["all_initial"]["count_only"],
        "without_P_dec_after_own_last_capture": wo["after_own_last_capture"]["original"],
        "without_P_dec_after_backward_call": wo["after_backward_call"]["original"],
        "init0_via_f0_law": f0["original"]["P_final"], "init0_via_f0_earliest_Y_law": f0["original"]["P_Y"],
        "init0_via_f0_early_law": f0["original"]["P_early"],
        "all_initial_init0_via_f0_law": f0["all_initial"]["P_final"],
        "all_initial_init0_via_f0_earliest_Y_law": f0["all_initial"]["P_Y"],
        "all_initial_init0_via_f0_early_law": f0["all_initial"]["P_early"],
        "init0_via_f0_thmB_own_bank_earliest_Y": f0["thmB_own_bank"]["P_Y"]["original"],
        "all_initial_init0_via_f0_thmB_own_bank_earliest_Y": f0["thmB_own_bank"]["P_Y"]["all_initial"],
        "revival_dA_term_end": rt["dA_term"]["P_final"], "revival_dA_term_earliest_Y": rt["dA_term"]["P_Y"],
        "revival_all_initial_reads_end": rt["all_initial_reads_term"]["P_final"],
        "revival_all_initial_reads_earliest_Y": rt["all_initial_reads_term"]["P_Y"]})
    routes_priced = result["pricing"]["routes"]
    result_table = result["pricing"]["mass_breakeven_units_per_replica"]
    for name in ("INIT64_plus_dA_law", "d_A_only_law", "INIT64_plus_dA_earliest_Y_law", "INIT64_plus_dA_C_published",
                 "INIT64_plus_dA_early_relaxation_law", "all_initial_law", "all_initial_earliest_Y_law",
                 "all_initial_early_relaxation_law", "thmB_one_level_end", "all_initial_thmB_one_level_end",
                 "thmB_own_bank_earliest_Y", "all_initial_thmB_own_bank_earliest_Y", "init0_via_f0_law",
                 "init0_via_f0_earliest_Y_law", "init0_via_f0_early_law", "all_initial_init0_via_f0_law",
                 "all_initial_init0_via_f0_earliest_Y_law", "all_initial_init0_via_f0_early_law",
                 "init0_via_f0_thmB_own_bank_earliest_Y", "all_initial_init0_via_f0_thmB_own_bank_earliest_Y",
                 "revival_dA_term_end"):
        need(routes_priced[name]["idle_priced_kappa_cap"] is None and routes_priced[name]["rank8_priced_kappa_cap"] is None,
             name + ": no positive saving")
    for name in ("thmB_own_bank_early_relaxation", "all_initial_thmB_own_bank_early_relaxation", "thmB_count_only_earliest_Y",
                 "without_P_dec_after_backward_call", "revival_all_initial_reads_end"):
        cap = routes_priced[name]
        need(cap["idle_priced_kappa_cap"] is not None and Q(cap["idle_priced_kappa_cap"]) < SELECTED_KAPPA
             and Q(cap["rank8_priced_kappa_cap"]) < SELECTED_KAPPA,
             name + ": positive ceiling, but below the selected kappa (and hence every pending claim)")
    for name in ("all_initial_thmB_count_only_earliest_Y", "thmB_count_only_early_relaxation",
                 "all_initial_thmB_count_only_early_relaxation"):
        need(Q(routes_priced[name]["idle_priced_kappa_cap"]) > SELECTED_KAPPA
             and Q(routes_priced[name]["rank8_priced_kappa_cap"]) > SELECTED_KAPPA,
             name + ": a delivery meeting Theorem B's count alone stays above the selected kappa (count does not decide)")
    # The decoder-timing premise is load-bearing: decoders right after each bank's own last capture leave a cap
    # above the selected kappa and above PR2474.
    cap = routes_priced["without_P_dec_after_own_last_capture"]
    need(Q(cap["idle_priced_kappa_cap"]) > PR2474_KAPPA and Q(cap["rank8_priced_kappa_cap"]) > PR2474_KAPPA,
         "without P_dec, 512 units leave a cap above the selected kappa and PR2474 (the premise is load-bearing)")
    # Revival: the original variant's d_A term at P_Y (576) beats the selected record only, not PR2474 or any pending
    # claim; the all-initial variant at P_Y leaves the INIT information a budget of break-even - 384.
    need(beats(C, 576, "idle", SELECTED_KAPPA) and beats(C, 576, "rank8", SELECTED_KAPPA)
         and not beats(C, 576, "idle", PR2474_KAPPA) and not beats(C, 576, "rank8", PR2474_KAPPA),
         "d_A term at P_Y (576): beats the selected record (at its rank-8 break-even), not PR2474")
    be_sel, be_2474 = (result_table["selected_1094"]["idle_units"], result_table["PR2474"]["idle_units"])
    need((be_sel - 384, be_2474 - 384) == (195, 189), "all-initial at P_Y: INIT budget 195 (selected) / 189 (PR2474) units")
    result["frame_model"] = frame_model_checks()
    result["tensor_toy"] = tensor_toy()
    result["negative_controls_rejected"] = negative_controls(hosted, base, events, C)
    n_neg = len(result["negative_controls_rejected"]) + 3   # + upward-only bound + two toy controls
    fm = result["frame_model"]
    status = ("PASS_RETAINED_ARRAY_CATCH_UP pr2540=128 init64_dA=3648/2496/1344 all_initial=3456/2304/1152 dA_only=960 "
              "thmB_one_level=1952/1824 thmB_own_bank=1344/1216/800/608 thmB_count_only=608/544/112/0 "
              "without_P_dec=512/640 init0_via_f0=3520/2368/1216 "
              "array_calls=464/456 no_saving=896 breakeven_S=573 breakeven_C=71 zero_advance_calls=6 "
              "hosted_instants=%d frame_instances=%d/%d negative_controls=%d no_new_kappa"
              % (r["hosting"]["instants_checked"], fm["record_partner_instances"], fm["general_instances"], n_neg))
    result["status"] = status
    text = json.dumps(result, indent=1, sort_keys=True) + "\n"
    target = PACKAGE / "RESULT.json"
    if "--write" in argv:
        if target.exists() and target.read_text() != text and "--force" not in argv:
            raise CheckFailure("RESULT.json differs; use --write --force to replace it")
        target.write_text(text)
    elif target.exists():
        need(json.loads(target.read_text()) == json.loads(text), "RESULT.json matches the recomputation")
    print(status)


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except CheckFailure as exc:
        print("FAIL:", exc)
        sys.exit(1)
