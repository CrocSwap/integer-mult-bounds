#!/usr/bin/env python3
"""KB1b: the COPY/ERASE window question of the fused z4 typed-echo pair.

Object: the single named obstruction of PR #2464 (research/
z4-typed-echo-supplier-instance): the fused pair defers the first wrapper's
ERASE across the second call's window (exact k=2 witness: 24 dirty work rows
at block-2 entry) while the pinned contract (research/split-centres-global/
proofs/PR386-BIT-GEOMETRY.txt) keeps COPY/ERASE windows sequential and
immutable and delivers totals per call.  This package decides the question in
both directions: it constructs legal realizations of the pair with per-call
sequential immutable windows and per-call totals delivery (schedule, window
row selection, and one bounded typed-window extension whose cost is priced),
prices every charged quantity of PR #2464's declared tape model, and isolates
the exact residual fusion item (window row-sharing on overlapping pairs) with
a scoped record-count lower bound.

Declared schedule family: words over the pinned PR #1391 alphabet (ADD/NEG
records) built from the certified child words C_b (fixed readers) or the
phase-indexed children C_(b,t) of research/z4-distinct-source-seed55 (its
declared contract change), per-octet work-frame words P^u, and window
COPY/ERASE records (one independent source row per work row, optionally
relabelled by the typed frame).  Call regions are sandwiches COPY + body +
ERASE + literal inverse(body); a fused pair is one sandwich spanning both
calls (the ERASE deferral) and a legal pair is two sandwiches (per-call
windows).  Every schedule is checked as an exact integer map on all 56 basis
columns (every dirty state of (D, X, W)) with its literal inverse.

Smallest falsifying instance first: the k=2 pair (two one-child echoes on
disjoint work octets, one shared source).  One bounded pivot: the k=5+5
persistent pair, whose two calls share all three work octets.

Exact integer arithmetic and certified rational ln/exp enclosures only.
Standard library only.  Prepared by Aaron Wang with help from opencode.
Apache-2.0.
"""

import hashlib
import importlib.util
import itertools
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2"

# Pinned predecessor emitter (PR #1391), byte-for-byte as carried by the
# PR #1410 package (research/z4-persistent-pair-seed57/inputs).  Hashes are
# the PR #1410 package's own pins, re-checked here before import.
PRE_DIR = ROOT / "research" / "z4-persistent-pair-seed57" / "inputs"
CERT_PATH = PRE_DIR / "PR1391-CERTIFICATE.json"
CODE_PATH = PRE_DIR / "PR1391-verify.py"
PREDECESSOR_CERT_SHA256 = "2a6ac306ddc6f58514b89f680d8ff3027b4195e2754574f8f04ac1f17785c9d3"
PREDECESSOR_CODE_SHA256 = "c3d8e76dad9b3cc159affa5e56dbf73612eab0c0ce4a4464f523d4cf47669c05"

OW = 8          # output D rows
WW = 24         # source X rows and work W rows (3 octets of 8)
ECHO_WIDTH = OW + WW + WW   # 56: D rows 0..8, X rows 8..32, W rows 32..56
MAPPING = list(range(OW)) + [OW + WW + i for i in range(WW)]
OCT_COST = [0, 20, 16, 20]   # octet_word(u) records per work octet

CONTROLS = []


def require(ok, message):
    if not ok:
        raise ValueError(message)


def control(name, ok, detail):
    require(ok, "control failed: " + name + ": " + detail)
    CONTROLS.append(name)


# --------------------------------------------------------------------------
# S0.  Pinned predecessor emitter
# --------------------------------------------------------------------------


def load_legacy():
    cert_raw = CERT_PATH.read_bytes()
    code_raw = CODE_PATH.read_bytes()
    require(hashlib.sha256(cert_raw).hexdigest() == PREDECESSOR_CERT_SHA256,
            "PR1391 certificate SHA")
    require(hashlib.sha256(code_raw).hexdigest() == PREDECESSOR_CODE_SHA256,
            "PR1391 verifier SHA")
    spec = importlib.util.spec_from_file_location("pr1391_pinned", CODE_PATH)
    legacy = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(legacy)
    return legacy, json.loads(cert_raw)


# --------------------------------------------------------------------------
# S1.  Window records and typed-frame relabeling.
#
# A window is a set of work octets; COPY installs one independent source row
# per work row and ERASE removes exactly the installed content.  Typed
# windows (the one bounded contract extension priced here) allow the COPY and
# ERASE source rows to be relabelled by the typed frame P^s; literal windows
# fix both to row alignment (the ERASE must then run at frame 0 on its
# octets, which forces the boundary frame-restoration words).
# --------------------------------------------------------------------------


def frame_pre(power):
    """Row map of P^power on one octet: (P^s X)[base+j] = X[base+pre[j]].
    P is two disjoint 4-cycles (0,1,2,3) and (4,5,6,7), each (a,b,c,d)->(d,a,b,c)."""
    four = [(0, 1, 2, 3), (3, 0, 1, 2), (2, 3, 0, 1), (1, 2, 3, 0)][power % 4]
    return four + tuple(4 + x for x in four)


def copy_window(legacy, sigma):
    """COPY records: W[32+8o+j] += X[8o+pre_{sigma[o]}(j)].  sigma: octet -> s."""
    recs = []
    for o, s in sorted(sigma.items()):
        pre = frame_pre(s)
        for j in range(8):
            recs.append(legacy.add(OW + WW + 8 * o + j, OW + 8 * o + pre[j]))
    return recs


def x_content_map(legacy, word):
    """X-content of every work row from the exact state: [(x_index, sign), ...]."""
    state = legacy.apply_word_matrix(word, ECHO_WIDTH)
    out = []
    for i in range(WW):
        row = state[OW + WW + i]
        nz = [(OW + j, row[OW + j]) for j in range(WW) if row[OW + j] != 0]
        out.append(nz)
    return out


def erase_window(legacy, prefix, octets):
    """ERASE records: remove exactly the X-content the typed frame leaves in W."""
    content = x_content_map(legacy, prefix)
    recs = []
    for o in sorted(octets):
        for j in range(8):
            r = 8 * o + j
            nz = content[r]
            require(len(nz) == 1 and nz[0][1] in (-1, 1),
                    "window row must carry one signed source row")
            x_index, sign = nz[0]
            recs.append(legacy.add(OW + WW + r, x_index, -sign))
    return recs


def gap_word(legacy, gap):
    """Per-octet work-frame words: P^u on work octet o for each (o, u)."""
    recs = []
    for o, u in sorted(gap.items()):
        if u:
            recs += list(legacy.lift_word(legacy.octet_word(u),
                                          [OW + WW + 8 * o + j for j in range(8)]))
    return recs


def child(legacy, block):
    return list(legacy.lift_word(legacy.child_word(block), MAPPING))


def child_typed(legacy, block, t):
    """Phase-indexed child (research/z4-distinct-source-seed55's declared
    family): (D, W) -> (D + Q^(-t) R_block W, P W).  Retargeted output rows
    only; the child keeps its eight ADDs and 24-coordinate P update."""
    p1 = legacy.expected_octet_frame()
    target = legacy.matmul(legacy.matrix_power(p1, (-t) % 4),
                           legacy.reader_matrix(block))
    recs = []
    for j in range(OW):
        hits = [k for k in range(WW) if target[j][k] != 0]
        require(len(hits) == 1 and target[j][hits[0]] == 1,
                "typed reader must be a selector")
        recs.append(legacy.add(j, OW + WW + hits[0]))
    recs += list(legacy.lift_word(legacy.workspace_word(1), MAPPING[OW:]))
    return recs


def inverse_of(legacy, word):
    return list(legacy.inverse_word(word))


# --------------------------------------------------------------------------
# S2.  Schedules: per-call windows (legal) versus one window spanning the
# pair (the ERASE deferral), and the per-octet gap programs.
# --------------------------------------------------------------------------


def expected_echo_map(legacy, blocks):
    """(D, X, W) -> (D + sum_b R_b X, X, W) as exact integer rows."""
    rows = legacy.identity(ECHO_WIDTH)
    for block in blocks:
        for j in range(OW):
            rows[j][OW + 8 * block + j] += 1
    return rows


def call_map_ok(legacy, word, blocks, label):
    got = legacy.apply_word_matrix(word, ECHO_WIDTH)
    want = expected_echo_map(legacy, blocks)
    control("exact_map_" + label, got == want, "map differs on 56 basis columns")
    inv = inverse_of(legacy, word)
    control("literal_inverse_" + label,
            legacy.matmul(legacy.apply_word_matrix(inv, ECHO_WIDTH), got)
            == legacy.identity(ECHO_WIDTH), "inverse does not restore")
    return got


def x_carrying_rows(legacy, word):
    return sum(1 for nz in x_content_map(legacy, word) if nz)


def dirty_rows(legacy, word):
    """PR #2464's witness measure: work rows differing from the identity state."""
    state = legacy.apply_word_matrix(word, ECHO_WIDTH)
    return sum(1 for r in range(OW + WW, ECHO_WIDTH)
               if any(state[r][c] != (1 if r == c else 0) for c in range(ECHO_WIDTH)))


def typed_call(legacy, blocks, octets, sigma, gaps, terminal=None, phase_indexed=False):
    """One region: COPY + body + ERASE + literal inverse of the body.

    gaps[i] = {octet: u} frame words between child i and i+1; terminal =
    {octet: u} trailing frame word inside the body (literal windows use it to
    restore frame 0 before the ERASE).  The ERASE is generated from the exact
    typed frame at the body exit, so the window always closes inside the
    region and the temporary is restored exactly; sigma is the COPY
    relabeling.
    """
    body = []
    frame = [0, 0, 0]
    for i, block in enumerate(blocks):
        body += child_typed(legacy, block, frame[block]) if phase_indexed \
            else child(legacy, block)
        frame = [f + 1 for f in frame]
        if i < len(blocks) - 1:
            gap = gaps[i] if i < len(gaps) else {}
            body += gap_word(legacy, gap)
            for o, u in gap.items():
                frame[o] += u
    if terminal:
        body += gap_word(legacy, terminal)
    word = copy_window(legacy, sigma) + body
    word += erase_window(legacy, word, octets)
    word += inverse_of(legacy, body)
    return word


def optimal_gaps(blocks, literal):
    """Exact per-octet gap optimum in the declared family.

    Read i sees work octet b at frame i + sum_{j<i} u_j^{(b)}.  Fixed readers
    need one COPY relabeling per octet, so typed windows only constrain equal
    frames at the octet's reads; literal windows need frame 0 at every read
    and at the ERASE (the body exit).  Returns (gaps, terminal, cost).
    """
    k = len(blocks)
    gaps = [dict() for _ in range(max(k - 1, 0))]
    terminal = {}
    total = 0
    for b in sorted(set(blocks)):
        idxs = [i for i, x in enumerate(blocks) if x == b]
        best = None
        for us in itertools.product(range(4), repeat=k - 1):
            fr = [(i + sum(us[:i])) % 4 for i in range(k)]
            if literal:
                if any(fr[i] != 0 for i in idxs):
                    continue
                t = (-(k + sum(us))) % 4
                cost = sum(OCT_COST[u] for u in us) + OCT_COST[t]
                cand = (cost, us, t)
            else:
                if any(fr[i] != fr[idxs[0]] for i in idxs):
                    continue
                cost = sum(OCT_COST[u] for u in us)
                cand = (cost, us, None)
            if best is None or cand[0] < best[0]:
                best = cand
        cost, us, t = best
        for j, u in enumerate(us):
            if u:
                gaps[j][b] = u
        if t:
            terminal[b] = t
        total += cost
    return gaps, terminal, total


def sigma_from_gaps(blocks, gaps):
    """COPY relabeling sigma|octet b = P^{-f_first(b)} for fixed-reader bodies."""
    sigma = {}
    for i, b in enumerate(blocks):
        if b not in sigma:
            f = (i + sum(gaps[j].get(b, 0) for j in range(i))) % 4
            sigma[b] = (-f) % 4
    return sigma


def pr2464_echo_word(legacy, states, blocks):
    """PR #2464's echo_word: 24-row literal wrapper around the pinned batch."""
    ow, ww = legacy.OUTPUT_WIDTH, legacy.WORK_WIDTH
    body_local = legacy.batch_word(states, blocks=blocks)
    mapping = list(range(ow)) + [ow + ww + i for i in range(ww)]
    body = legacy.lift_word(body_local, mapping)
    copy_in = [legacy.add(ow + ww + i, ow + i) for i in range(ww)]
    copy_out = [legacy.add(ow + ww + i, ow + i, -1) for i in range(ww)]
    return copy_in + body + copy_out + legacy.inverse_word(body)


# --------------------------------------------------------------------------
# S3.  Whole-construction physical price (PR #2464's declared tape model).
# --------------------------------------------------------------------------


def physical_price(word, width, calls):
    adds = negs = reads = writes = movement = 0
    for kind, target, source, sign in word:
        if kind == "ADD":
            adds += 1
            reads += 2
            movement += 2 * max(target, source)
        else:
            negs += 1
            reads += 1
            movement += 2 * target
        writes += 1
    records = len(word)
    return {
        "primitives": records,
        "ADD": adds,
        "NEG": negs,
        "dispatches": records,
        "instruction_fetches": records,
        "coefficient_fetches": records,
        "reads": reads,
        "writes": writes,
        "address_travel_row_steps": movement,
        "descriptor_bits": 16 * records + 128 * calls,
        "data_storage_cells": width * 56,
    }


def price_delta(base, other):
    return {k: base[k] - other[k] for k in base}


# --------------------------------------------------------------------------
# S4.  Exact rational ln/exp enclosures and hosted ledger diagnostics.
# Technique credited to research/complex-local-word-ceiling/ceiling.py and
# research/selected-suppliers-de-diagnostic/verify.py; re-implemented here so
# this package imports neither engine.
# --------------------------------------------------------------------------

PREC = 176


def down(x):
    return Q((x.numerator << PREC) // x.denominator, 1 << PREC)


def up(x):
    return -down(-x)


_ATANH = {}


def atanh(t):
    if t in _ATANH:
        return _ATANH[t]
    require(0 < t <= Q(1, 3), "atanh range")
    s, p, k = Q(0), t, 0
    while True:
        s += p / (2 * k + 1)
        p *= t * t
        k += 1
        tail = p / ((2 * k + 1) * (1 - t * t))
        if tail < Q(1, 1 << (PREC + 8)):
            out = (down(s), up(s + tail))
            _ATANH[t] = out
            return out


_LN = {}


def ln_int(k):
    if k in _LN:
        return _LN[k]
    require(isinstance(k, int) and k >= 1, "ln domain")
    if k == 1:
        out = (Q(0), Q(0))
    else:
        lo, hi = ln_int(k - 1)
        a, b = atanh(Q(1, 2 * k - 1))
        out = (down(lo + 2 * a), up(hi + 2 * b))
    _LN[k] = out
    return out


def ln_ratio(m, r):
    lm, um = ln_int(m)
    lr, ur = ln_int(r)
    return down(lm - ur), up(um - lr)


def exp_enc(lo, hi):
    require(0 <= lo <= hi <= Q(1, 2), "exp range")

    def series(y, upper):
        s, t, k = Q(1), Q(1), 0
        while True:
            k += 1
            t = t * y / k
            s += t
            if t * y < Q(1, 1 << (PREC + 8)):
                return up(s + 2 * t * y / (k + 1)) if upper else down(s)

    return series(lo, False), series(hi, True)


def child_power(m, r, a):
    lo, hi = ln_ratio(m, r)
    return exp_enc(a * lo, a * hi)


def moment_bill(hist, m, W, a):
    lo = hi = Q(0)
    for r, n in hist.items():
        e = child_power(m, r, a)
        lo += Q(n) * r * e[0]
        hi += Q(n) * r * e[1]
    return down(lo / (m * W)), up(hi / (m * W))


def de_diagnostic(hist, m, W):
    require(all(isinstance(r, int) and 0 < r < m for r in hist),
            "child rank outside (0, m)")
    mass = sum(n * r for r, n in hist.items())
    D = m * W - mass
    lo = hi = Q(0)
    for r, n in hist.items():
        l_lo, l_hi = ln_ratio(m, r)
        lo += Q(n) * r * l_lo
        hi += Q(n) * r * l_hi
    require(D > 0, "zero-deficit ledger rejected")
    return D, (lo, hi), (down(Q(D) / hi), up(Q(D) / lo))


# --------------------------------------------------------------------------
# S5.  research/z4-distinct-source-seed55 boundary recurrence and the
# decomposition of its 144-primitive saving.
# --------------------------------------------------------------------------


def g_literal(legacy, k):
    """seed55's recurrence: entry charge A(t), terminal phase fixed at 0."""
    A = [sum(legacy.word_counts(legacy.workspace_word(r))) for r in range(4)]
    f = {t: A[t] for t in range(4)}
    for _ in range(k):
        f = {s: min(f[t] + A[(s - t - 1) % 4] for t in range(4)) for s in range(4)}
    return f[0]


def g_typed(legacy, k):
    """Typed windows: entry and terminal frames are absorbed by window
    relabeling, so only inter-child transitions are charged."""
    A = [sum(legacy.word_counts(legacy.workspace_word(r))) for r in range(4)]
    f = {t: 0 for t in range(4)}
    for _ in range(k):
        f = {s: min(f[t] + A[(s - t - 1) % 4] for t in range(4)) for s in range(4)}
    return min(f.values())


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------


def build_result():
    legacy, cert = load_legacy()
    m_host, W_host = 73, 14336

    # ---- positive controls: pinned tables and PR #2464's words -----------
    per_octet = [legacy.word_counts(legacy.octet_word(p)) for p in range(4)]
    control("phase_cost_table", per_octet == [(0, 0), (18, 2), (12, 4), (18, 2)],
            str(per_octet))
    control("octet_frame_costs", [sum(v) for v in per_octet] == OCT_COST,
            str([sum(v) for v in per_octet]))

    p1 = legacy.expected_octet_frame()
    ws3 = legacy.block_diag([p1] * 3)
    for t in range(4):
        lhs = legacy.matmul(legacy.matrix_power(p1, (-t) % 4),
                            legacy.matmul(legacy.reader_matrix(0),
                                          legacy.matrix_power(ws3, t)))
        control("intertwiner_Qinv_t_R_P_t_%d" % t,
                lhs == legacy.reader_matrix(0), "Q^-t R P^t != R")

    words = {}
    words["pr2464_k1_a"] = pr2464_echo_word(legacy, [0, 0], (0,))
    words["pr2464_k2_separate"] = words["pr2464_k1_a"] + pr2464_echo_word(legacy, [0, 0], (1,))
    words["pr2464_k2_joint"] = pr2464_echo_word(legacy, [0, 3, 0], (0, 1))
    words["pr2464_k5"] = pr2464_echo_word(legacy, [0, 1, 2, 3, 0, 0], (0, 1, 2, 0, 1))
    words["pr2464_k5_pair"] = words["pr2464_k5"] + words["pr2464_k5"]
    words["pr2464_k10_joint"] = pr2464_echo_word(
        legacy, [0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 0], (0, 1, 2, 0, 1, 0, 1, 2, 0, 1))
    inv_counts = {n: legacy.word_counts(w) for n, w in words.items()}
    control("pr2464_k1_invoice_304", sum(inv_counts["pr2464_k1_a"]) == 304,
            str(inv_counts["pr2464_k1_a"]))
    control("pr2464_separate_invoice_608", sum(inv_counts["pr2464_k2_separate"]) == 608,
            str(inv_counts["pr2464_k2_separate"]))
    control("pr2464_joint_invoice_496", sum(inv_counts["pr2464_k2_joint"]) == 496,
            str(inv_counts["pr2464_k2_joint"]))
    control("pr2464_k5_invoice_1008", sum(inv_counts["pr2464_k5"]) == 1008,
            str(inv_counts["pr2464_k5"]))
    control("pr2464_k5_pair_invoice_2016", sum(inv_counts["pr2464_k5_pair"]) == 2016,
            str(inv_counts["pr2464_k5_pair"]))
    control("pr2464_k10_joint_invoice_1904", sum(inv_counts["pr2464_k10_joint"]) == 1904,
            str(inv_counts["pr2464_k10_joint"]))
    call_map_ok(legacy, words["pr2464_k2_joint"], (0, 1), "pr2464_k2_joint")
    call_map_ok(legacy, words["pr2464_k5_pair"],
                (0, 1, 2, 0, 1, 0, 1, 2, 0, 1), "pr2464_k5_pair")

    # ---- the k=2 legal realizations (smallest falsifying instance) -------
    gaps_l_a, term_l_a, cost_l_a = optimal_gaps((0,), True)
    gaps_l_ab, term_l_ab, cost_l_ab = optimal_gaps((0, 1), True)
    gaps_t_ab, term_t_ab, cost_t_ab = optimal_gaps((0, 1), False)
    control("k1_literal_gap_cost_20", cost_l_a == 20, str(cost_l_a))
    control("k2_literal_joint_gap_cost_56", cost_l_ab == 56, str(cost_l_ab))
    control("k2_typed_joint_gap_cost_0", cost_t_ab == 0, str(cost_t_ab))

    words["legal_typed_a"] = typed_call(legacy, (0,), {0}, {0: 0}, [])
    words["legal_typed_b"] = typed_call(legacy, (1,), {1}, {1: 0}, [])
    words["legal_typed_pair"] = words["legal_typed_a"] + words["legal_typed_b"]
    words["legal_min_literal_a"] = typed_call(legacy, (0,), {0}, {0: 0}, [],
                                              terminal=term_l_a)
    words["legal_min_literal_b"] = typed_call(legacy, (1,), {1}, {1: 0}, [],
                                              terminal={1: term_l_a[0]})
    words["legal_min_literal_pair"] = (words["legal_min_literal_a"]
                                       + words["legal_min_literal_b"])
    words["joint_typed_pair"] = typed_call(legacy, (0, 1), {0, 1}, {0: 0, 1: 3}, gaps_t_ab)
    words["joint_min_literal_pair"] = typed_call(
        legacy, (0, 1), {0, 1}, {0: 0, 1: 0}, gaps_l_ab, terminal=term_l_ab)

    call_map_ok(legacy, words["legal_typed_a"], (0,), "legal_typed_call_a")
    call_map_ok(legacy, words["legal_typed_b"], (1,), "legal_typed_call_b")
    call_map_ok(legacy, words["legal_typed_pair"], (0, 1), "legal_typed_pair")
    call_map_ok(legacy, words["legal_min_literal_a"], (0,), "legal_min_literal_call_a")
    call_map_ok(legacy, words["legal_min_literal_pair"], (0, 1), "legal_min_literal_pair")
    call_map_ok(legacy, words["joint_typed_pair"], (0, 1), "joint_typed_pair")
    call_map_ok(legacy, words["joint_min_literal_pair"], (0, 1), "joint_min_literal_pair")

    # per-call totals delivery: at call a's region end the state is exactly
    # call a's complete echo map (totals final in D, temporary restored).
    want_a = expected_echo_map(legacy, (0,))
    for name, prefix in (("legal_typed_pair", words["legal_typed_a"]),
                         ("legal_min_literal_pair", words["legal_min_literal_a"])):
        boundary = legacy.apply_word_matrix(prefix, ECHO_WIDTH)
        control("per_call_delivery_at_boundary_" + name, boundary == want_a,
                "boundary state differs from call a's echo map")

    # witness at block-2 entry (call b's entry state).
    witness = {}
    for name, prefix in (("legal_typed_pair", words["legal_typed_a"]),
                         ("legal_min_literal_pair", words["legal_min_literal_a"])):
        witness[name] = [x_carrying_rows(legacy, prefix), dirty_rows(legacy, prefix)]
    control("legal_witness_zero_rows", witness["legal_typed_pair"] == [0, 0]
            and witness["legal_min_literal_pair"] == [0, 0], str(witness))

    def block2_cut(word):
        ins = [i for i, (k2, t, s, sgn) in enumerate(word)
               if k2 == "ADD" and OW + WW <= t < OW + 2 * WW and s is not None
               and OW <= s < OW + WW and sgn == 1]
        c2 = None
        for i, (k2, t, s, sgn) in enumerate(word):
            if c2 is None and i > max(ins) and t < OW and s is not None \
                    and OW + WW + 8 <= s < OW + WW + 16:
                c2 = i
                break
        require(c2 is not None, "block-2 entry located")
        return c2

    for name in ("pr2464_k2_joint", "joint_typed_pair", "joint_min_literal_pair"):
        c2 = block2_cut(words[name])
        witness[name] = [x_carrying_rows(legacy, words[name][:c2]),
                         dirty_rows(legacy, words[name][:c2])]
    control("pr2464_witness_24_dirty_rows", witness["pr2464_k2_joint"][1] == WW,
            "dirty rows at block-2 entry=" + str(witness["pr2464_k2_joint"]))
    control("joint_typed_witness_16_x_rows",
            witness["joint_typed_pair"] == [2 * OW, WW],
            str(witness["joint_typed_pair"]))
    control("joint_literal_witness_16_x_rows",
            witness["joint_min_literal_pair"] == [2 * OW, WW],
            str(witness["joint_min_literal_pair"]))

    # negative controls: window mutants must fail
    body0 = child(legacy, 0)
    prefix0 = copy_window(legacy, {0: 0}) + body0
    wrong_p1 = prefix0 + [legacy.add(OW + WW + j, OW + j, -1) for j in range(8)] \
        + inverse_of(legacy, body0)
    control("wrong_erase_relabeling_rejected",
            legacy.apply_word_matrix(wrong_p1, ECHO_WIDTH)
            != expected_echo_map(legacy, (0,)), "row-aligned mid-frame erase accepted")
    wrong_p2 = prefix0 + [legacy.add(OW + WW + j, OW + (j + 2) % 8, -1) for j in range(8)] \
        + inverse_of(legacy, body0)
    control("wrong_erase_power_rejected",
            legacy.apply_word_matrix(wrong_p2, ECHO_WIDTH)
            != expected_echo_map(legacy, (0,)), "P^2 erase accepted at frame P")
    omit = prefix0 + inverse_of(legacy, body0)
    control("omitted_erase_rejected",
            legacy.apply_word_matrix(omit, ECHO_WIDTH)
            != expected_echo_map(legacy, (0,)), "omitted erase accepted")
    c2 = block2_cut(words["joint_typed_pair"])
    boundary_joint = legacy.apply_word_matrix(words["joint_typed_pair"][:c2], ECHO_WIDTH)
    control("deferral_breaks_per_call_delivery",
            boundary_joint != want_a,
            "the joint boundary state must not equal call a's map")

    # ---- whole-construction prices (the full priced budget) --------------
    width = m_host
    price = {}
    for name, calls in (("pr2464_k2_separate", 2), ("pr2464_k2_joint", 1),
                        ("legal_typed_pair", 2), ("legal_min_literal_pair", 2),
                        ("joint_typed_pair", 1), ("joint_min_literal_pair", 1)):
        price[name] = physical_price(words[name], width, calls)
    control("legal_literal_positive_saving",
            price["pr2464_k2_separate"]["primitives"]
            - price["legal_min_literal_pair"]["primitives"] == 224,
            str(price_delta(price["pr2464_k2_separate"],
                            price["legal_min_literal_pair"])["primitives"]))
    control("legal_typed_positive_saving",
            price["pr2464_k2_separate"]["primitives"]
            - price["legal_typed_pair"]["primitives"] == 304,
            str(price_delta(price["pr2464_k2_separate"],
                            price["legal_typed_pair"])["primitives"]))
    control("k2_deferral_residual_zero_typed",
            price["legal_typed_pair"]["primitives"]
            - price["joint_typed_pair"]["primitives"] == 0,
            "deferral buys nothing at equal typed windows")
    control("k2_deferral_pessimization_literal",
            price["legal_min_literal_pair"]["primitives"]
            - price["joint_min_literal_pair"]["primitives"] == -32,
            "at equal literal windows the deferral is more expensive")
    control("typed_extension_price_80",
            price["legal_typed_pair"]["primitives"] + 80
            == price["legal_min_literal_pair"]["primitives"],
            "typed windows cost 0 extra records; literal fallback pays the "
            "frame restorations")

    # ---- bounded pivot: the k=5+5 persistent pair (windows share rows) ---
    gaps5_t, term5_t, cost5_t = optimal_gaps((0, 1, 2, 0, 1), False)
    gaps10_t, term10_t, cost10_t = optimal_gaps((0, 1, 2, 0, 1, 0, 1, 2, 0, 1), False)
    gaps5_l, term5_l, cost5_l = optimal_gaps((0, 1, 2, 0, 1), True)
    sigma5 = sigma_from_gaps((0, 1, 2, 0, 1), gaps5_t)
    sigma10 = sigma_from_gaps((0, 1, 2, 0, 1, 0, 1, 2, 0, 1), gaps10_t)

    call5_fixed = typed_call(legacy, (0, 1, 2, 0, 1), {0, 1, 2}, sigma5, gaps5_t)
    words["pivot_separate5_typed_fixed"] = call5_fixed + call5_fixed
    words["pivot_joint10_typed_fixed"] = typed_call(
        legacy, (0, 1, 2, 0, 1, 0, 1, 2, 0, 1), {0, 1, 2}, sigma10, gaps10_t)
    call5_phase = typed_call(legacy, (0, 1, 2, 0, 1), {0, 1, 2}, {0: 0, 1: 0, 2: 0},
                             [], phase_indexed=True)
    words["pivot_separate5_typed_phase"] = call5_phase + call5_phase
    words["pivot_joint10_typed_phase"] = typed_call(
        legacy, (0, 1, 2, 0, 1, 0, 1, 2, 0, 1), {0, 1, 2}, {0: 0, 1: 0, 2: 0},
        [], phase_indexed=True)
    call5_lit = typed_call(legacy, (0, 1, 2, 0, 1), {0, 1, 2},
                           {0: 0, 1: 0, 2: 0}, gaps5_l, terminal=term5_l)
    words["pivot_separate5_min_literal"] = call5_lit + call5_lit
    for name in ("pivot_separate5_typed_fixed", "pivot_joint10_typed_fixed",
                 "pivot_separate5_typed_phase", "pivot_joint10_typed_phase",
                 "pivot_separate5_min_literal"):
        call_map_ok(legacy, words[name], (0, 1, 2, 0, 1, 0, 1, 2, 0, 1), name)

    price["pivot_pr2464_separate_full"] = physical_price(words["pr2464_k5_pair"], width, 2)
    price["pivot_pr2464_joint_full"] = physical_price(words["pr2464_k10_joint"], width, 1)
    for name, calls in (("pivot_separate5_typed_fixed", 2),
                        ("pivot_joint10_typed_fixed", 1),
                        ("pivot_separate5_typed_phase", 2),
                        ("pivot_joint10_typed_phase", 1),
                        ("pivot_separate5_min_literal", 2)):
        price[name] = physical_price(words[name], width, calls)
    control("pivot_window_sharing_residual_48_phase",
            price["pivot_separate5_typed_phase"]["primitives"]
            - price["pivot_joint10_typed_phase"]["primitives"] == 48,
            str(price["pivot_separate5_typed_phase"]["primitives"]
                - price["pivot_joint10_typed_phase"]["primitives"]))
    control("pivot_legal_beats_priced_baseline",
            price["pivot_pr2464_separate_full"]["primitives"]
            - price["pivot_separate5_typed_phase"]["primitives"] == 560,
            str(price["pivot_pr2464_separate_full"]["primitives"]
                - price["pivot_separate5_typed_phase"]["primitives"]))
    control("pivot_literal_also_beats_priced_baseline",
            price["pivot_pr2464_separate_full"]["primitives"]
            - price["pivot_separate5_min_literal"]["primitives"] > 0,
            str(price["pivot_pr2464_separate_full"]["primitives"]
                - price["pivot_separate5_min_literal"]["primitives"]))

    # Window record lower bound inside the X-reading window family: each call
    # of the persistent pair installs 24 independent source rows (>= 24
    # X-reading ADDs) and removes them (>= 24 ERASE ADDs), so per-call windows
    # pay >= 4d per pair while one window spanning the pair pays >= 2d.  The
    # gap 2d = 48 records is exactly the deferral-only saving measured above.
    window_lower_bound = {
        "per_call_windows_pair_records_min": 4 * WW,
        "single_window_pair_records_min": 2 * WW,
        "deferral_only_saving_records": 2 * WW,
        "scope": "X-reading COPY/ERASE window records with one independent "
                 "source row installed per work row; not a lower bound for "
                 "arbitrary ADD/NEG programs",
    }
    control("window_lower_bound_matches_measured_residual",
            window_lower_bound["deferral_only_saving_records"]
            == price["pivot_separate5_typed_phase"]["primitives"]
            - price["pivot_joint10_typed_phase"]["primitives"],
            "counting bound != measured residual")

    # ---- research/z4-distinct-source-seed55's 144, decomposed ------------
    gl5, gl10 = g_literal(legacy, 5), g_literal(legacy, 10)
    gt5, gt10 = g_typed(legacy, 5), g_typed(legacy, 10)
    control("seed55_g5_reproduced_60", gl5 == 60, str(gl5))
    control("seed55_g10_reproduced_48", gl10 == 48, str(gl10))
    T = 68
    e1_lit = 2 * 5 * T + 2 * WW + 2 * gl5
    e2_lit = 2 * 10 * T + 4 * WW + 2 * gl10
    e1_typ = 2 * 5 * T + 2 * WW + 2 * gt5
    e2_typ = 2 * 10 * T + 4 * WW + 2 * gt10
    control("seed55_invoices_reproduced", (e1_lit, e2_lit) == (848, 1552),
            "E1=%d E2=%d" % (e1_lit, e2_lit))
    control("seed55_144_is_endpoint_restoration",
            2 * e1_lit - e2_lit == 144 and 2 * e1_typ == e2_typ,
            "literal saving=%d typed E1=%d E2=%d" % (2 * e1_lit - e2_lit, e1_typ, e2_typ))
    seed55 = {
        "source": "research/z4-distinct-source-seed55 (phase-indexed children)",
        "g5_literal": gl5, "g10_literal": gl10,
        "g5_typed": gt5, "g10_typed": gt10,
        "E1_5_literal": e1_lit, "E2_5_5_literal": e2_lit,
        "E1_5_typed": e1_typ, "E2_5_5_typed": e2_typ,
        "saving_literal": 2 * e1_lit - e2_lit,
        "saving_typed": 2 * e1_typ - e2_typ,
        "decomposition": "2*g(5) - g(10) = 120 - 48 = 72 per direction, x2 = 144: "
                         "boundary endpoint restoration, not window lifetime; with "
                         "typed windows both sides reach 1456 and the saving is 0",
    }

    # ---- hosted ledgers: a < D/E diagnostics ------------------------------
    hist_base = {1: 349604, 2: 60192, 3: 62585, 4: 20448, 5: 11808, 7: 7, 8: 1152,
                 48: 4866}
    hist_shared = dict(hist_base)
    hist_shared[8] = 576
    mass_base = sum(n * r for r, n in hist_base.items())
    mass_shared = sum(n * r for r, n in hist_shared.items())
    control("baseline_coverage_identity", m_host * W_host - mass_base == W_host - 64 * 144,
            "D=%d" % (m_host * W_host - mass_base))
    control("shared_coverage_identity", m_host * W_host - mass_shared == W_host - 32 * 144,
            "D=%d" % (m_host * W_host - mass_shared))
    D_b, E_b, DE_b = de_diagnostic(hist_base, m_host, W_host)
    D_s, E_s, DE_s = de_diagnostic(hist_shared, m_host, W_host)
    published_de = Q("0.001680590709754321699421")
    control("baseline_D_over_E_matches_published",
            abs(DE_b[0] - published_de) < Q(1, 10 ** 24)
            and abs(DE_b[1] - published_de) < Q(1, 10 ** 24),
            "distance check: [%s, %s]" % (DE_b[0], DE_b[1]))
    control("shared_D_over_E_exceeds_baseline", DE_s[0] > DE_b[1],
            "shared=%s baseline=%s" % (DE_s[0], DE_b[1]))
    control("D_over_E_is_a_screen_not_acceptance",
            moment_bill(hist_base, m_host, W_host, DE_b[1])[0] > 1,
            "f(D/E) must exceed 1 strictly")

    for name in ("legal_typed_pair", "legal_min_literal_pair"):
        control("storage_unchanged_" + name,
                price[name]["data_storage_cells"]
                == price["pr2464_k2_separate"]["data_storage_cells"], "storage moved")

    l1 = {n: legacy.prefix_row_l1_peak(words[n], ECHO_WIDTH)
          for n in ("pr2464_k2_separate", "pr2464_k2_joint", "legal_typed_pair",
                    "legal_min_literal_pair", "pivot_separate5_typed_phase",
                    "pivot_joint10_typed_phase")}

    inv_all = {n: list(legacy.word_counts(w)) + [len(w)] for n, w in words.items()}

    return {
        "schema_version": 1,
        "base_commit": BASE,
        "result": "PASS_Z4_TYPED_WINDOW_SCHEDULE",
        "declared_family": "sandwiches COPY + body + ERASE + literal inverse(body) "
                           "over the pinned PR1391 children (or seed55's phase-indexed "
                           "children), per-octet work-frame words P^u, and window "
                           "COPY/ERASE records with optional typed-frame source "
                           "relabeling; per-call windows (two sandwiches) versus one "
                           "window spanning the pair (the ERASE deferral)",
        "k2_pair": {
            "blocks": {"call_a": [0], "call_b": [1]},
            "basis_columns_checked": ECHO_WIDTH,
            "gap_programs": {"k1_literal": [cost_l_a, term_l_a],
                             "k2_literal_joint": [cost_l_ab, gaps_l_ab, term_l_ab],
                             "k2_typed_joint": [cost_t_ab, gaps_t_ab]},
            "invoices_ADD_NEG_total": {n: inv_all[n] for n in inv_all
                                       if n.startswith(("pr2464_k2", "legal_", "joint_"))},
            "witness_at_block2_entry_x_carrying_and_dirty_rows": witness,
            "per_call_totals_delivery": "the state at call a's region end equals "
                                        "call a's complete echo map exactly (56 columns)",
            "price": {n: price[n] for n in price if not n.startswith("pivot_")},
            "saving_vs_pr2464_priced_baseline": {
                "legal_min_literal_pair": price_delta(price["pr2464_k2_separate"],
                                                      price["legal_min_literal_pair"]),
                "legal_typed_pair": price_delta(price["pr2464_k2_separate"],
                                                price["legal_typed_pair"]),
            },
            "deferral_residual_equal_windows": {
                "typed_records": price["legal_typed_pair"]["primitives"]
                - price["joint_typed_pair"]["primitives"],
                "literal_records": price["legal_min_literal_pair"]["primitives"]
                - price["joint_min_literal_pair"]["primitives"],
            },
            "prefix_row_l1_peak": l1,
        },
        "pivot_k5k10": {
            "gap_programs": {"k5_typed_fixed_reader": [cost5_t, gaps5_t, sigma5],
                             "k10_typed_fixed_reader": [cost10_t, gaps10_t, sigma10],
                             "k5_literal": [cost5_l, gaps5_l, term5_l]},
            "price": {n: price[n] for n in price if n.startswith("pivot_")},
            "window_lower_bound": window_lower_bound,
        },
        "distinct_source_144_decomposition": seed55,
        "hosted_ledgers": {
            "width_m": m_host, "live_stock_W": W_host,
            "baseline_histogram": hist_base, "shared_k2_histogram": hist_shared,
            "baseline": {
                "D": D_b,
                "D_over_E_lo": str(DE_b[0]), "D_over_E_hi": str(DE_b[1]),
                "E_lo": str(E_b[0]), "E_hi": str(E_b[1]),
            },
            "shared_widened_window": {
                "D": D_s,
                "D_over_E_lo": str(DE_s[0]), "D_over_E_hi": str(DE_s[1]),
                "E_lo": str(E_s[0]), "E_hi": str(E_s[1]),
            },
            "admitted_realization": "per-call sequential windows keep one centre path "
                                    "per call: n_8 stays 1152 and the ledger moment is "
                                    "the selected baseline (a < D/E above); the shared "
                                    "ledger needs the widened window",
        },
        "obstruction": {
            "named_obstruction": "PR 2464: the fused pair defers the first wrapper's "
                                 "ERASE across the second call's window",
            "outcome": "(a) realized: per-call sequential immutable windows with "
                       "per-call totals delivery keep a positive whole-construction "
                       "saving (224 records on the pinned literal reading, 304 with "
                       "the priced typed-window extension); the deferral is not "
                       "necessary for any saving",
            "deferral_residual": "at equal window width the deferral saves 0 records "
                                 "at k=2 typed (disjoint window octets) and is 32 "
                                 "records worse at k=2 literal; at k=5+5 typed it "
                                 "saves exactly 2d = 48 (shared window rows), "
                                 "matching the X-reading window record lower bound",
            "extension_priced": "typed windows (COPY/ERASE source rows relabelled by "
                                "the typed frame path) cost 0 extra records and 0 "
                                "extra descriptor bits; the literal fallback costs "
                                "+80 records per k=2 pair (frame restorations)",
            "demotion_exact_part": "the moment ledger: per-call windows imply per-call "
                                   "centre paths, so n_8 stays 1152 and no kappa "
                                   "change follows without the widened-window/"
                                   "common-sink change",
        },
        "controls": CONTROLS,
        "control_count": len(CONTROLS),
    }


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    result = build_result()
    out = HERE / "RESULT.json"
    if "--write" in sys.argv:
        out.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    else:
        require(out.exists(), "RESULT.json missing; run with --write first")
        stored = json.loads(out.read_text(encoding="utf-8"))
        require(stored == json.loads(json.dumps(result)),
                "RESULT.json drift: rerun --write after review")
    k2 = result["k2_pair"]
    print("PASS_Z4_TYPED_WINDOW_SCHEDULE kb1b "
          "legal_literal=%d legal_typed=%d baseline=%d joint=%d "
          "witness_x=%d_deferred_vs_0_legal pivot_residual=%d controls=%d no_new_kappa"
          % (k2["price"]["legal_min_literal_pair"]["primitives"],
             k2["price"]["legal_typed_pair"]["primitives"],
             k2["price"]["pr2464_k2_separate"]["primitives"],
             k2["price"]["pr2464_k2_joint"]["primitives"],
             k2["witness_at_block2_entry_x_carrying_and_dirty_rows"]
             ["pr2464_k2_joint"][0],
             result["pivot_k5k10"]["window_lower_bound"]["deferral_only_saving_records"],
             result["control_count"]))


if __name__ == "__main__":
    main()
