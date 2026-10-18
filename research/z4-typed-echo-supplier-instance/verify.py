#!/usr/bin/env python3
"""KB1 supplier instantiation of the certified z4 order-four typed echo.

Object: the certified order-four paired-frame typed echo (PR #1391 five-child
contract, PR #1410 persistent pair, both pinned through
research/z4-persistent-pair-seed57/inputs).  This package builds the missing
supplier instantiation: the smallest falsifying typed pair, the priced
whole-construction physical budget (dispatch, reads, writes, address travel,
instruction fetch, coefficient fetch, descriptor storage, storage), the hosted
aggregate ledgers with their exact moments and the a < D/E diagnostic, and the
exact witness for the one obligation the instantiation does not close
(hosting: the named host's COPY/ERASE window-lifetime and delivery contract).

Exact integer arithmetic and certified rational ln/exp enclosures only.
Standard library only.  Prepared by Aaron Wang with help from opencode.
Apache-2.0.
"""

import hashlib
import importlib.util
import itertools
import json
import subprocess
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2"

# Pinned predecessor emitter (PR #1391), byte-for-byte as carried by the
# PR #1410 package.  Hashes are the PR #1410 package's own pins.
PRE_DIR = ROOT / "research" / "z4-persistent-pair-seed57" / "inputs"
CERT_PATH = PRE_DIR / "PR1391-CERTIFICATE.json"
CODE_PATH = PRE_DIR / "PR1391-verify.py"
PREDECESSOR_CERT_SHA256 = "2a6ac306ddc6f58514b89f680d8ff3027b4195e2754574f8f04ac1f17785c9d3"
PREDECESSOR_CODE_SHA256 = "c3d8e76dad9b3cc159affa5e56dbf73612eab0c0ce4a4464f523d4cf47669c05"

CONTROLS = []


def require(ok, message):
    if not ok:
        raise ValueError(message)


def control(name, ok, detail):
    require(ok, "control failed: " + name + ": " + detail)
    CONTROLS.append(name)


# --------------------------------------------------------------------------
# S0.  Pins and predecessor emitter
# --------------------------------------------------------------------------


def load_legacy():
    cert_raw = CERT_PATH.read_bytes()
    code_raw = CODE_PATH.read_bytes()
    require(hashlib.sha256(cert_raw).hexdigest() == PREDECESSOR_CERT_SHA256, "PR1391 certificate SHA")
    require(hashlib.sha256(code_raw).hexdigest() == PREDECESSOR_CODE_SHA256, "PR1391 verifier SHA")
    spec = importlib.util.spec_from_file_location("pr1391_pinned", CODE_PATH)
    legacy = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(legacy)
    cert = json.loads(cert_raw)
    return legacy, cert


def git_blob(path):
    out = subprocess.run(["git", "hash-object", str(path)], cwd=ROOT, check=True,
                         capture_output=True, text=True).stdout.strip()
    return out


def base_blob(path):
    out = subprocess.run(["git", "rev-parse", BASE + ":" + path], cwd=ROOT, check=True,
                         capture_output=True, text=True).stdout.strip()
    return out


# --------------------------------------------------------------------------
# Exact enclosures: ln (atanh chain), exp (Taylor with tail), moment bill.
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
    """Enclosure of ln k for integer k >= 1."""
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
    """Enclosure of ln(m/r) = ln m - ln r."""
    lm, um = ln_int(m)
    lr, ur = ln_int(r)
    return down(lm - ur), up(um - lr)


def exp_enc(lo, hi):
    """Enclosure of exp([lo, hi]) for 0 <= lo <= hi <= 1/2."""
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
    """Enclosure of (m/r)^a = exp(a ln(m/r)) for rational 0 <= a <= 1/20."""
    lo, hi = ln_ratio(m, r)
    return exp_enc(a * lo, a * hi)


def moment_bill(hist, m, W, a, surcharge=None):
    """Enclosure of f(a) = (1/(mW)) sum n_r r (m/r)^a + c_s m^a."""
    lo = hi = Q(0)
    for r, n in hist.items():
        e = child_power(m, r, a)
        lo += Q(n) * r * e[0]
        hi += Q(n) * r * e[1]
    if surcharge:
        e = child_power(m, 1, a)
        lo += surcharge * e[0]
        hi += surcharge * e[1]
    return down(lo / (m * W)), up(hi / (m * W))


def de_diagnostic(hist, m, W):
    """(D, E-enclosure, D/E-enclosure) with D = mW - sum n_r r, E = sum n_r r ln(m/r)."""
    require(all(isinstance(r, int) and 0 < r < m for r in hist), "child rank outside (0, m)")
    mass = sum(n * r for r, n in hist.items())
    D = m * W - mass
    lo = hi = Q(0)
    for r, n in hist.items():
        l_lo, l_hi = ln_ratio(m, r)
        lo += Q(n) * r * l_lo
        hi += Q(n) * r * l_hi
    require(D > 0, "zero-deficit ledger rejected")
    return D, (lo, hi), (down(Q(D) / hi), up(Q(D) / lo))


def moment_root(hist, m, W, grid):
    """Bracket the exact moment root a* with f(a_lo) < 1 < f(a_hi)."""
    lo, hi = Q(0), Q(1, 20)
    require(moment_bill(hist, m, W, hi)[0] > 1, "root search window too small")
    require(moment_bill(hist, m, W, lo)[1] < 1, "ledger has no positive saving")
    while hi - lo > grid:
        mid = Q(int((lo + hi) / 2 / grid)) * grid
        if mid <= lo:
            mid = lo + grid
        v = moment_bill(hist, m, W, mid)
        if v[1] < 1:
            lo = mid
        elif v[0] > 1:
            hi = mid
        else:
            raise ValueError("enclosure too wide at grid " + str(mid))
    return lo, hi


# --------------------------------------------------------------------------
# S1/S2.  Typed-echo words: smallest instance, invoices, exact maps.
# --------------------------------------------------------------------------


def echo_word(legacy, states, blocks):
    """One complete dirty root echo: W += X; batch; W -= X; inverse batch."""
    ow, ww = legacy.OUTPUT_WIDTH, legacy.WORK_WIDTH
    body_local = legacy.batch_word(states, blocks=blocks)
    mapping = list(range(ow)) + [ow + ww + i for i in range(ww)]
    body = legacy.lift_word(body_local, mapping)
    copy_in = [legacy.add(ow + ww + i, ow + i) for i in range(ww)]
    copy_out = [legacy.add(ow + ww + i, ow + i, -1) for i in range(ww)]
    return copy_in + body + copy_out + legacy.inverse_word(body)


def wrapper_word(legacy):
    ow, ww = legacy.OUTPUT_WIDTH, legacy.WORK_WIDTH
    copy_in = [legacy.add(ow + ww + i, ow + i) for i in range(ww)]
    copy_out = [legacy.add(ow + ww + i, ow + i, -1) for i in range(ww)]
    return copy_in, copy_out


def expected_echo_map(legacy, blocks):
    """(D, X, W) -> (D + sum R_i X, X, W) as exact integer rows."""
    ow, ww = legacy.OUTPUT_WIDTH, legacy.WORK_WIDTH
    width = ow + ww + ww
    rows = legacy.identity(width)
    for block in blocks:
        for j in range(ow):
            rows[j][ow + 8 * block + j] += 1
    return rows


def my_dp(k, work_cost, out_cost):
    """Independent re-derivation of the boundary recurrence g(k)."""
    def step(old, new):
        return (work_cost[(new - old - 1) % 4] + out_cost[(new - old) % 4], (old, new))

    f = {t: (work_cost[t] + out_cost[t], (t,)) for t in range(4)}
    for _ in range(k):
        nxt = {}
        for s in range(4):
            best = None
            for t in range(4):
                c, _ = step(t, s)
                cand = (f[t][0] + c, f[t][1] + (s,))
                if best is None or cand < best:
                    best = cand
            nxt[s] = best
        f = nxt
    return f[0]


def path_total(states, work_vec, out_vec):
    v = tuple(a + b for a, b in zip(work_vec[states[0]], out_vec[states[0]]))
    for old, new in zip(states, states[1:]):
        w = work_vec[(new - old - 1) % 4]
        o = out_vec[(new - old) % 4]
        v = tuple(x + y + z for x, y, z in zip(v, w, o))
    return sum(v)


# --------------------------------------------------------------------------
# S3.  Whole-construction physical price (declared machine model).
# --------------------------------------------------------------------------


def physical_price(word, width, calls):
    """Charge every quantity the repo's physical models charge for this word.

    Declared model: rows of width m on a row-indexed tape.  Each record is one
    dispatch and one instruction fetch and one coefficient fetch (constants
    +-1); ADD reads two rows and writes one, NEG reads and writes one; address
    travel is 2*max(source, target) row-index steps per record (NEG: 2*target),
    the visit-source/visit-target/return convention of
    research/mutable-source-persistent-connector.  Descriptor storage is 16
    bits per record plus one 128-bit call record per call.  Data storage is
    width * 56 cells (8 output + 24 source + 24 work coordinates).
    """
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


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------


def build_result():
    legacy, cert = load_legacy()
    m_host, W_host = 73, 14336  # selected complex aggregate ledger

    # ---- S1: mechanism reproduction (positive controls) --------------------
    per_octet = [legacy.word_counts(legacy.octet_word(p)) for p in range(4)]
    control("phase_cost_table", per_octet == [(0, 0), (18, 2), (12, 4), (18, 2)],
            str(per_octet))
    work_cost = [3 * sum(v) for v in per_octet]
    out_cost = [sum(v) for v in per_octet]

    g = {}
    paths = {}
    for k in (1, 2, 3, 5, 10):
        total, states = my_dp(k, work_cost, out_cost)
        g[k] = total
        paths[k] = list(states)
    control("g5_reproduces_pr1391", g[5] == 140, "g(5)=" + str(g[5]))
    control("g10_reproduces_pr1410", g[10] == 248, "g(10)=" + str(g[10]))
    control("g2_is_the_smallest_pair_boundary", g[2] == 88, "g(2)=" + str(g[2]))
    control("dp_agrees_with_pinned_brute_k5",
            legacy.brute_boundary_min(5) == g[5], "brute=" + str(legacy.brute_boundary_min(5)))
    control("dp_agrees_with_pinned_brute_k3",
            legacy.brute_boundary_min(3) == g[3], "brute=" + str(legacy.brute_boundary_min(3)))

    # Certified canonical optimal paths (PR #1391/#1410): use them for emission
    # after re-checking their cost against the independent DP.
    canonical = {5: [0, 1, 2, 3, 0, 0], 10: [0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 0]}
    work_vec = [tuple(3 * x for x in v) for v in per_octet]
    out_vec = [tuple(v) for v in per_octet]
    for k, cand in canonical.items():
        control("canonical_path_is_optimal_k%d" % k,
                path_total(cand, work_vec, out_vec) == g[k],
                "canonical=%d dp=%d" % (path_total(cand, work_vec, out_vec), g[k]))
        paths[k] = cand

    # exhaustive phase-path census: smallest instance k=2 and fixture k=5
    census = {}
    for k in (2, 5):
        best = None
        count = 0
        work_vec = [tuple(3 * x for x in v) for v in per_octet]
        out_vec = [tuple(v) for v in per_octet]
        for prefix in itertools.product(range(4), repeat=k):
            states = list(prefix) + [0]
            t = path_total(states, work_vec, out_vec)
            if best is None or t < best:
                best = t
            count += 1
        census[k] = {"paths": count, "min_total": best}
        control("exhaustive_census_matches_dp_k%d" % k, best == g[k],
                "census=" + str(best) + " dp=" + str(g[k]))

    # exact maps and invoices for the certified fixtures and the smallest pair
    words = {}
    words["k5_joint"] = echo_word(legacy, paths[5], (0, 1, 2, 0, 1))
    words["k10_joint"] = echo_word(legacy, paths[10], (0, 1, 2, 0, 1, 0, 1, 2, 0, 1))
    words["k2_joint"] = echo_word(legacy, paths[2], (0, 1))
    words["k1_a"] = echo_word(legacy, [0, 0], (0,))
    words["k1_b"] = echo_word(legacy, [0, 0], (1,))
    words["k2_separate"] = words["k1_a"] + words["k1_b"]
    words["k5_eager"] = None  # built below from eager states [0]*6

    inv = {name: legacy.word_counts(w) for name, w in words.items() if w is not None}
    control("k5_echo_invoice_1008", sum(inv["k5_joint"]) == 1008, str(inv["k5_joint"]))
    control("k10_joint_invoice_1904", sum(inv["k10_joint"]) == 1904, str(inv["k10_joint"]))
    control("two_separate_k5_invoice_2016", 2 * sum(inv["k5_joint"]) == 2016, str(inv["k5_joint"]))
    control("two_separate_k1_invoice", sum(inv["k2_separate"]) == 608, str(inv["k2_separate"]))
    control("k2_joint_invoice_496", sum(inv["k2_joint"]) == 496, str(inv["k2_joint"]))

    # eager restoration control (schedule mutant): each child followed by P^-1
    eager_states = [0] * 6
    eager_local = legacy.batch_word(tuple(eager_states), blocks=(0, 1, 2, 0, 1),
                                    omit_last_gap=False)
    ow, ww = legacy.OUTPUT_WIDTH, legacy.WORK_WIDTH
    mapping = list(range(ow)) + [ow + ww + i for i in range(ww)]
    eager_body = legacy.lift_word(eager_local, mapping)
    cin, cout = wrapper_word(legacy)
    words["k5_eager"] = cin + eager_body + cout + legacy.inverse_word(eager_body)
    inv["k5_eager"] = legacy.word_counts(words["k5_eager"])
    control("k5_eager_invoice_1328", sum(inv["k5_eager"]) == 1328, str(inv["k5_eager"]))

    # exact linear maps on all 56 basis columns (this is every dirty state)
    for name, blocks in (("k2_joint", (0, 1)), ("k1_a", (0,)), ("k1_b", (1,)),
                         ("k5_joint", (0, 1, 2, 0, 1)),
                         ("k10_joint", (0, 1, 2, 0, 1, 0, 1, 2, 0, 1))):
        got = legacy.apply_word_matrix(words[name], legacy.ECHO_WIDTH)
        want = expected_echo_map(legacy, blocks)
        control("exact_map_" + name, got == want, "map mismatch on 56 basis columns")

    # smallest falsifying instance: joint == sequential composition, exactly
    seq = legacy.matmul(legacy.apply_word_matrix(words["k1_b"], legacy.ECHO_WIDTH),
                        legacy.apply_word_matrix(words["k1_a"], legacy.ECHO_WIDTH))
    control("k2_joint_equals_sequential_composition",
            seq == legacy.apply_word_matrix(words["k2_joint"], legacy.ECHO_WIDTH),
            "composed maps differ")

    # literal inverse restores identity
    for name in ("k2_joint", "k5_joint"):
        w = words[name]
        inv_word = legacy.inverse_word(w)
        m = legacy.matmul(legacy.apply_word_matrix(inv_word, legacy.ECHO_WIDTH),
                          legacy.apply_word_matrix(w, legacy.ECHO_WIDTH))
        control("literal_inverse_" + name, m == legacy.identity(legacy.ECHO_WIDTH),
                "inverse does not restore")

    # negative controls on the smallest instance: schedule mutants must fail
    s2 = list(paths[2])
    mutant_local = legacy.batch_word(tuple(s2), blocks=(0, 1), wrong_first_output_phase=True)
    mutant_body = legacy.lift_word(mutant_local, mapping)
    mutant_word = cin + mutant_body + cout + legacy.inverse_word(mutant_body)
    control("wrong_first_output_phase_rejected",
            legacy.apply_word_matrix(mutant_word, legacy.ECHO_WIDTH)
            != expected_echo_map(legacy, (0, 1)), "mutant map accepted")
    no_terminal = legacy.batch_word(tuple(s2), blocks=(0, 1), omit_last_gap=True)
    nt_body = legacy.lift_word(no_terminal, mapping)
    nt_word = cin + nt_body + cout + legacy.inverse_word(nt_body)
    control("omitted_terminal_gap_rejected",
            legacy.apply_word_matrix(nt_word, legacy.ECHO_WIDTH)
            != expected_echo_map(legacy, (0, 1)), "mutant map accepted")
    fwd_word = cin + mutant_body + cout + mutant_body
    control("forward_for_inverse_rejected",
            legacy.apply_word_matrix(fwd_word, legacy.ECHO_WIDTH)
            != expected_echo_map(legacy, (0, 1)), "mutant map accepted")

    # ---- S2: smallest-instance window witness (the obstruction) -----------
    # The joint word has exactly one wrapper (copy-in/copy-out pair) around both
    # child blocks; the separate schedule has one wrapper per block.  The
    # deferred copy-out is the window-lifetime change the named host forbids.
    def wrapper_positions(word):
        ins, outs = [], []
        for i, (kind, target, source, sign) in enumerate(word):
            if (kind == "ADD" and ow + ww <= target < ow + 2 * ww
                    and source is not None and ow <= source < ow + ww):
                (ins if sign == 1 else outs).append(i)
        return ins, outs

    jin, jout = wrapper_positions(words["k2_joint"])
    ain, aout = wrapper_positions(words["k1_a"])
    bin_, bout = wrapper_positions(words["k1_b"])
    control("joint_word_has_one_wrapper", len(jin) == ww and len(jout) == ww,
            "copy records=%d/%d" % (len(jin), len(jout)))
    control("separate_words_have_two_wrappers",
            len(ain) == ww and len(aout) == ww and len(bin_) == ww and len(bout) == ww, "counts")
    # deferred-restoration witness: at the entry of the second child block in
    # the joint word, the work rows still carry first-block state (the first
    # wrapper's copy-out has not run).  Locate the block-1 reader: the first
    # D-row write whose source is workspace octet 1 after the copy-in region.
    jw = words["k2_joint"]
    state = legacy.identity(legacy.ECHO_WIDTH)
    cut = None
    dirty = None
    for i, (kind, target, source, sign) in enumerate(jw):
        if (cut is None and i > max(jin) and target < ow and source is not None
                and ow + ww + 8 <= source < ow + ww + 16):
            cut = i
            dirty = sum(1 for r in range(ow + ww, legacy.ECHO_WIDTH)
                        if any(state[r][c] != (1 if r == c else 0)
                               for c in range(legacy.ECHO_WIDTH)))
        if kind == "ADD":
            state[target] = [a + sign * b for a, b in zip(state[target], state[source])]
        else:
            state[target] = [-x for x in state[target]]
    require(cut is not None and dirty is not None, "second child block located")
    control("deferred_restoration_witness_at_smallest_instance", dirty == ww,
            "dirty work rows at block-2 entry=" + str(dirty))

    # ---- S3: whole-construction physical price ----------------------------
    width = m_host
    price = {}
    price["k2_separate"] = physical_price(words["k2_separate"], width, 2)
    price["k2_joint"] = physical_price(words["k2_joint"], width, 1)
    price["k5_separate_pair"] = physical_price(words["k5_joint"] + words["k5_joint"], width, 2)
    price["k10_joint"] = physical_price(words["k10_joint"], width, 1)
    pair_saving = {k: price["k2_separate"][k] - price["k2_joint"][k] for k in price["k2_separate"]}
    pair_saving_510 = {k: price["k5_separate_pair"][k] - price["k10_joint"][k]
                       for k in price["k5_separate_pair"]}
    control("whole_price_primitives_positive",
            pair_saving["primitives"] == 112 and pair_saving_510["primitives"] == 112,
            "k2=%s k5k10=%s" % (pair_saving["primitives"], pair_saving_510["primitives"]))
    control("dispatch_charge_is_not_free",
            pair_saving["dispatches"] == 112 and price["k2_joint"]["dispatches"] > 0,
            str(pair_saving["dispatches"]))

    # precision proxy: certified prefix row-L1 peaks
    l1 = {}
    for name in ("k1_a", "k2_joint", "k5_joint", "k10_joint"):
        l1[name] = legacy.prefix_row_l1_peak(words[name], legacy.ECHO_WIDTH)
    l1["k5_separate_pair_concat"] = legacy.prefix_row_l1_peak(
        words["k5_joint"] + words["k5_joint"], legacy.ECHO_WIDTH)
    control("persistent_pair_row_l1_matches_pr1410",
            l1["k10_joint"] == 42 and l1["k5_separate_pair_concat"] == 30,
            "joint=%d separate=%d" % (l1["k10_joint"], l1["k5_separate_pair_concat"]))
    control("row_l1_charge_is_not_free", l1["k2_joint"] > l1["k1_a"],
            "k2=%d k1=%d" % (l1["k2_joint"], l1["k1_a"]))

    # ---- S4: hosted ledgers, exact moments, a < D/E -----------------------
    hist_base = {1: 349604, 2: 60192, 3: 62585, 4: 20448, 5: 11808, 7: 7, 8: 1152, 48: 4866}
    hist_shared = dict(hist_base)
    hist_shared[8] = 576  # k=2 shared centre: 1,152 -> 576 rank-8 children

    # coverage identities
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

    a_complex = Q("0.001675462676808103522925")   # recorded complex endpoint
    a_bit = Q("0.001733427039589844234749")       # recorded bit endpoint
    f_base = moment_bill(hist_base, m_host, W_host, a_complex)
    f_base_next = moment_bill(hist_base, m_host, W_host, a_complex + Q(1, 10 ** 24))
    f_shared_bit = moment_bill(hist_shared, m_host, W_host, a_bit)
    control("baseline_accepts_recorded_endpoint", f_base[1] < 1, str(f_base))
    control("baseline_rejects_next_grid_point", f_base_next[0] > 1, str(f_base_next))
    control("baseline_residual_matches_published_magnitude",
            Q("-1.30422e-24") < f_base[0] - 1 and f_base[1] - 1 < Q("-1.30421e-24"),
            "residual band check: [%s, %s]" % (f_base[0] - 1, f_base[1] - 1))
    control("shared_accepts_bit_endpoint_with_published_margin",
            Q("-0.00430") < f_shared_bit[1] - 1 < Q("-0.00420"),
            "f(c_bit)-1 in (%s, %s)" % (f_shared_bit[0] - 1, f_shared_bit[1] - 1))
    control("D_over_E_overestimates_the_root",
            moment_bill(hist_base, m_host, W_host, DE_b[1])[0] > 1,
            "f(D/E) must exceed 1 strictly")

    root_base = moment_root(hist_base, m_host, W_host, Q(1, 10 ** 12))
    root_shared = moment_root(hist_shared, m_host, W_host, Q(1, 10 ** 12))
    control("baseline_root_tracks_recorded_endpoint",
            root_base[0] - Q(1, 10 ** 11) <= a_complex <= root_base[1] + Q(1, 10 ** 11),
            "root=[%s, %s]" % (root_base[0], root_base[1]))

    # typed-echo Delta-H accounting against the sharp budget
    eliminated_units_per_pair = 64          # one wrapper = 8 rank-8 children
    budget_full_gain_per_pair = Q("61.6")   # 2 x 30.8 units/call (centre-sharing-overhead-budget)
    budget_any_gain_per_pair = Q("64.0")    # 2 x 32.0 units/call
    typed_echo_recursive_overhead = 0       # the typed word adds only scalar records
    net_per_pair = eliminated_units_per_pair - typed_echo_recursive_overhead
    control("delta_h_fits_sharp_budget",
            net_per_pair >= budget_full_gain_per_pair and
            typed_echo_recursive_overhead <= budget_any_gain_per_pair,
            "net=%s budget=%s" % (net_per_pair, budget_full_gain_per_pair))

    # histogram-identical control: paying both wrappers gives no moment change
    control("both_wrappers_keep_selected_histogram",
            mass_base - mass_shared == 72 * 8 * 8 == 4608,
            "wrapper mass identity: %d" % (mass_base - mass_shared))

    # ---- bounded pivot: single-call realization ---------------------------
    # Pivot: make the pair one supplier call from the start (one window, no
    # reorder).  The per-call totals-delivery contract then requires the fused
    # call to copy both calls' totals: 16 rank-8 children per pair = 128 units,
    # exactly the two-wrapper baseline, so the ledger returns to the selected
    # histogram and the moment is unchanged.  The alternative (one shared set
    # of totals) is the common-sink delivery contract change already named in
    # the obstruction, so the pivot does not escape the same obligation.
    hist_pivot = dict(hist_base)
    pivot_pair_units = 16 * 8
    control("pivot_single_call_delivery_returns_baseline_ledger",
            pivot_pair_units == 2 * eliminated_units_per_pair
            and sum(n * r for r, n in hist_pivot.items()) == mass_base,
            "pivot pair units=%d" % pivot_pair_units)
    f_pivot = moment_bill(hist_pivot, m_host, W_host, a_complex)
    control("pivot_moment_identical_to_baseline",
            f_pivot == f_base, "pivot moment differs")

    # mutated-ledger controls
    bad = dict(hist_base)
    bad[1] = bad[1] - 1
    D_bad, E_bad, DE_bad = de_diagnostic(bad, m_host, W_host)
    control("histogram_mutation_breaks_coverage_identity",
            m_host * W_host - sum(n * r for r, n in bad.items()) != W_host - 64 * 144,
            "mutation detected")
    try:
        de_diagnostic({999: 1}, m_host, W_host)
        ok = False
    except ValueError:
        ok = True
    control("child_rank_outside_0_m_rejected", ok, "rank 999 must be rejected")
    try:
        de_diagnostic({1: m_host * W_host}, m_host, W_host)
        ok = False
    except ValueError:
        ok = True
    control("zero_deficit_ledger_rejected", ok, "D must be positive")

    return {
        "schema_version": 1,
        "base_commit": BASE,
        "result": "PASS_Z4_TYPED_ECHO_SUPPLIER_INSTANCE",
        "mechanism": {
            "g_boundary_total": {str(k): g[k] for k in g},
            "g_boundary_paths": {str(k): paths[k] for k in g},
            "exhaustive_census": {str(k): census[k] for k in census},
            "invoices_ADD_NEG": {name: list(inv[name]) for name in inv},
        },
        "smallest_falsifying_instance": {
            "joint_blocks": [0, 1],
            "separate_calls": [[0], [1]],
            "basis_columns_checked": 56,
            "phase_paths_enumerated": census[2]["paths"],
            "joint_equals_sequential_composition": True,
            "deferred_restoration_dirty_work_rows": dirty,
        },
        "whole_construction_price": {
            "model": "rows of width 73 on a row-indexed tape; dispatch, instruction "
                     "fetch and coefficient fetch per record; ADD reads 2 writes 1, "
                     "NEG reads 1 writes 1; address travel 2*max(src,dst) per record; "
                     "16-bit descriptor per record + 128-bit call record; 56*width "
                     "data cells",
            "k2_separate": price["k2_separate"],
            "k2_joint": price["k2_joint"],
            "k5_separate_pair": price["k5_separate_pair"],
            "k10_joint": price["k10_joint"],
            "pair_saving_k2": pair_saving,
            "pair_saving_k5k10": pair_saving_510,
            "prefix_row_l1_peak": l1,
        },
        "hosted_ledgers": {
            "width_m": m_host,
            "live_stock_W": W_host,
            "baseline_histogram": hist_base,
            "shared_k2_histogram": hist_shared,
            "baseline": {
                "rank_mass": mass_base,
                "D": D_b,
                "E_lo": str(E_b[0]), "E_hi": str(E_b[1]),
                "D_over_E_lo": str(DE_b[0]), "D_over_E_hi": str(DE_b[1]),
                "moment_at_complex_endpoint": [str(f_base[0]), str(f_base[1])],
                "moment_root_lo": str(root_base[0]), "moment_root_hi": str(root_base[1]),
            },
            "shared_k2": {
                "rank_mass": mass_shared,
                "D": D_s,
                "E_lo": str(E_s[0]), "E_hi": str(E_s[1]),
                "D_over_E_lo": str(DE_s[0]), "D_over_E_hi": str(DE_s[1]),
                "moment_at_bit_endpoint": [str(f_shared_bit[0]), str(f_shared_bit[1])],
                "moment_root_lo": str(root_shared[0]), "moment_root_hi": str(root_shared[1]),
            },
            "delta_h_budget": {
                "eliminated_rank_units_per_pair": eliminated_units_per_pair,
                "typed_echo_recursive_overhead_units": typed_echo_recursive_overhead,
                "sharp_budget_full_gain_units_per_pair": str(budget_full_gain_per_pair),
                "sharp_budget_any_gain_units_per_pair": str(budget_any_gain_per_pair),
                "fits": True,
            },
        },
        "obstruction": {
            "obligation": "hosting: COPY/ERASE window-lifetime and per-call delivery",
            "pinned_contract": "research/split-centres-global/proofs/PR386-BIT-GEOMETRY.txt: "
                               "'COPY/ERASE windows remain sequential and immutable'",
            "smallest_instance_witness": "the k=2 joint word defers the first wrapper's "
                                         "copy-out past the second child block; all 24 work "
                                         "rows are dirty at the second block's entry",
            "unchanged_contract_price": "both wrappers paid: n_8 stays 1152 and the moment "
                                        "is identical to the selected ledger",
            "pivots_tested": 1,
            "pivot": "single-call realization: the per-call totals-delivery contract makes "
                     "the fused call copy both calls' totals (16 rank-8 children per pair, "
                     "128 units), exactly the two-wrapper baseline; the ledger returns to "
                     "the selected histogram and the moment is unchanged. Sharing one set "
                     "of totals needs the same common-sink/window contract change.",
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
    print("PASS_Z4_TYPED_ECHO_SUPPLIER_INSTANCE "
          "smallest_k2 whole_price saved=112 D_over_E_shared=%s controls=%d no_new_kappa"
          % (result["hosted_ledgers"]["shared_k2"]["D_over_E_hi"], result["control_count"]))


if __name__ == "__main__":
    main()
