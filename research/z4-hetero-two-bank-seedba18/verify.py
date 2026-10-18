#!/usr/bin/env python3
"""Heterogeneous 3+7 root echoes on two distinct source banks (order-four typed boundary).

Model, child emitter and pin loader are copied from the pinned predecessor
research/z4-distinct-source-seed55/verify.py (itself built on the pinned
PR1391 child family and PR1410 same-source boundary), with attribution in
NOTICE.md. New here: asymmetric heterogeneous reader schedules across two
source banks, the handoff at the 3|7 boundary, the period-4 boundary law,
and the associated map and control checks.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import subprocess
import sys
import types
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
INPUTS = PACKAGE / "inputs"
BASE = "e112d71c8d7bb32435debcc54df932593dd8223a"
PR1391_HEAD = "6ce8017e4c27c8b220b6c3a27a53bb18f138212a"
PR1410_HEAD = "5b1c00b9f2770aabaa0085539405757f7818a14a"
PINS = {
    "inputs/PR1391/CERTIFICATE.json": (
        "2a6ac306ddc6f58514b89f680d8ff3027b4195e2754574f8f04ac1f17785c9d3",
        "0132b117d90f1a7a97c40af3e38503c117604e00",
    ),
    "inputs/PR1391/verify.py": (
        "c3d8e76dad9b3cc159affa5e56dbf73612eab0c0ce4a4464f523d4cf47669c05",
        "9d866bbf57a6d1f012a21687bde2e231c90efd14",
    ),
    "inputs/PR1410-README.md": (
        "6dda7d5b83b41c71d73711401edbc146271a546a518ef6b038b0bdbb6578d405",
        "001929a89cd64f4bbb0d4194c6bde96f45b7ded2",
    ),
}
D = 8
BANK = 24
X = D
Y = D + BANK
W = D + 2 * BANK
TOTAL = D + 3 * BANK
# Type A reads source octets [0,1,2] of bank X (three children).
BLOCKS_A = (0, 1, 2)
# Type B reads source octets [2,1,0,2,1,0,2] of bank Y (seven children).
BLOCKS_B = (2, 1, 0, 2, 1, 0, 2)
BLOCKS_AB = BLOCKS_A + BLOCKS_B
SWITCH_INDEX = len(BLOCKS_A) - 1  # handoff after child 2, at the 3|7 boundary
BLOCKS5 = (0, 1, 2, 0, 1)
BLOCKS10 = BLOCKS5 + BLOCKS5


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def git_blob(data: bytes) -> str:
    return subprocess.run(
        ["git", "hash-object", "--stdin"], input=data, cwd=ROOT,
        check=True, capture_output=True,
    ).stdout.decode().strip()


def load_predecessor():
    for rel, (sha, blob) in PINS.items():
        raw = (PACKAGE / rel).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == sha, "pinned input SHA drift: " + rel)
        require(git_blob(raw) == blob, "pinned input Git blob drift: " + rel)
    source_readme = (PACKAGE / "inputs/PR1410-README.md").read_text()
    require("two identical five-child root echoes on the same source" in source_readme
            and "(D, X, W)" in source_readme, "PR1410 predecessor snapshot mismatch")

    cert_path = INPUTS / "PR1391/CERTIFICATE.json"
    code_path = INPUTS / "PR1391/verify.py"
    legacy = types.ModuleType("pinned_pr1391")
    legacy.__file__ = str(code_path)
    exec(compile(code_path.read_bytes(), str(code_path), "exec"), legacy.__dict__)
    legacy.PKG = code_path.parent
    legacy.ROOT = ROOT
    legacy.CERT = cert_path
    cert = json.loads(cert_path.read_text())
    require(cert["base_commit"] == "bce54fb3f895cbe5cd4c0eb477c3afeed100190f",
            "PR1391 research base")
    require(cert["assignment"]["os_seed"] == 56 and cert["frame"]["order"] == 4,
            "PR1391 assignment/frame pin")
    require(cert["recursive_interface_cost"]["leaf_forward"] == {"ADD": 62, "NEG": 6},
            "PR1391 leaf cost pin")
    for path, digest in cert["source_pins"].items():
        raw = subprocess.run(["git", "show", cert["base_commit"] + ":" + path],
                             cwd=ROOT, check=True, capture_output=True).stdout
        require(hashlib.sha256(raw).hexdigest() == digest,
                "PR1391 inherited source pin: " + path)
    selected = subprocess.run(["git", "show", BASE + ":certificates/selected-result.json"],
                              cwd=ROOT, check=True, capture_output=True).stdout
    require(hashlib.sha256(selected).hexdigest() ==
            "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32",
            "selected record base pin")
    return legacy, cert


def plus_rows(target, source, sign=1):
    return [a + sign * b for a, b in zip(target, source)]


def matmul(a, b):
    require(bool(a) and bool(b) and len(a[0]) == len(b), "matrix dimensions")
    return [[sum(a[i][k] * b[k][j] for k in range(len(b)))
             for j in range(len(b[0]))] for i in range(len(a))]


def zero(n, m):
    return [[0] * m for _ in range(n)]


def identity(n):
    out = zero(n, n)
    for i in range(n):
        out[i][i] = 1
    return out


def block_diag(blocks):
    rows = sum(len(b) for b in blocks)
    cols = sum(len(b[0]) for b in blocks)
    out = zero(rows, cols)
    r0 = c0 = 0
    for b in blocks:
        for i, row in enumerate(b):
            out[r0 + i][c0:c0 + len(row)] = row[:]
        r0 += len(b)
        c0 += len(b[0])
    return out


def matrix_power(a, exponent):
    require(exponent >= 0, "negative matrix exponent")
    out = identity(len(a))
    for _ in range(exponent):
        out = matmul(out, a)
    return out


def apply_word(word, width):
    rows = identity(width)
    for kind, target, source, sign in word:
        if kind == "ADD":
            rows[target] = plus_rows(rows[target], rows[source], sign)
        elif kind == "NEG":
            rows[target] = [-v for v in rows[target]]
        else:
            raise ValueError("unknown operation kind")
    return rows


def word_counts(word):
    counts = {"ADD": 0, "NEG": 0}
    for op in word:
        counts[op[0]] += 1
    return counts


def row_l1_peak(word, width):
    rows = identity(width)
    peak = max(sum(abs(v) for v in row) for row in rows)
    for kind, target, source, sign in word:
        if kind == "ADD":
            rows[target] = plus_rows(rows[target], rows[source], sign)
        elif kind == "NEG":
            rows[target] = [-v for v in rows[target]]
        peak = max(peak, max(sum(abs(v) for v in row) for row in rows))
    return peak


def map_local(word, mapping, legacy):
    return legacy.lift_word(word, mapping)


def phase_reader(legacy, q, block):
    qmat = legacy.expected_octet_frame()
    r = legacy.reader_matrix(block)
    return matmul(matrix_power(qmat, (-q) % 4), r)


def typed_child(legacy, q, block):
    """C_(block,q): D += Q^-q R_block W; W += (P-I)W."""
    r = phase_reader(legacy, q, block)
    word = []
    for j, row in enumerate(r):
        nz = [(i, c) for i, c in enumerate(row) if c]
        require(len(nz) == 1 and nz[0][1] in (-1, 1), "typed reader is not signed selector")
        i, sign = nz[0]
        word.append(legacy.add(j, D + i, sign))
    word += legacy.lift_word(legacy.workspace_word(1), [D + i for i in range(BANK)])
    return word


def check_typed_children(legacy):
    q = legacy.expected_octet_frame()
    p = block_diag([q] * 3)
    for block in sorted(set(BLOCKS_AB)):
        r = legacy.reader_matrix(block)
        for phase in range(4):
            typed = phase_reader(legacy, phase, block)
            require(matmul(typed, matrix_power(p, phase)) == r,
                    "Q^-t R_i P^t identity")
            word = typed_child(legacy, phase, block)
            actual = apply_word(word, D + BANK)
            expected = identity(D + BANK)
            for i in range(D):
                expected[i][D:D + BANK] = typed[i][:]
            expected[D:] = [[0] * D + row for row in p]
            require(actual == expected, "typed child dirty-state map")
            require(word_counts(word) == word_counts(legacy.child_word(block)),
                    "phase type changed the child ADD/NEG invoice")


def phase_costs(legacy):
    return [word_counts(legacy.workspace_word(r)) for r in range(4)]


def cost_vector_add(a, b):
    return {"ADD": a["ADD"] + b["ADD"], "NEG": a["NEG"] + b["NEG"]}


def best_phase_path(legacy, children):
    """F_0(t)=A(t), F_(j+1)(s)=min_t F_j(t)+A(s-t-1), final s=0."""
    a = phase_costs(legacy)
    state = {t: (a[t].copy(), (t,)) for t in range(4)}
    for _ in range(children):
        nxt = {}
        for s in range(4):
            options = []
            for t, (v, path) in state.items():
                gap = a[(s - t - 1) % 4]
                nv = cost_vector_add(v, gap)
                options.append((nv["ADD"] + nv["NEG"], path + (s,), nv))
            _, path, v = min(options)
            nxt[s] = (v, path)
        state = nxt
    vector, path = state[0]
    return tuple(path), vector


def exhaustive_phase_minimum(legacy, children):
    a = phase_costs(legacy)
    best = None
    checked = 0
    for prefix in itertools.product(range(4), repeat=children):
        states = prefix + (0,)
        v = a[states[0]].copy()
        for old, new in zip(states, states[1:]):
            v = cost_vector_add(v, a[(new - old - 1) % 4])
        record = (v["ADD"] + v["NEG"], states, v)
        if best is None or record < best:
            best = record
        checked += 1
    return best, checked


def lift_batch(legacy, states, blocks, source_switch=False, switch_index=SWITCH_INDEX,
               switch_phase_delta=0, bad_reader_index=None):
    """Emit D/W body with phase-typed readers and optional X-to-Y handoff."""
    require(len(states) == len(blocks) + 1, "path/block count")
    require(states[-1] == 0, "terminal workspace phase")
    local_map = list(range(D)) + [W + i for i in range(BANK)]
    word = legacy.lift_word(legacy.workspace_word(states[0]), [W + i for i in range(BANK)])
    for i, block in enumerate(blocks):
        phase = states[i]
        if bad_reader_index == i:
            phase = (phase + 1) % 4
        word += map_local(typed_child(legacy, phase, block), local_map, legacy)
        gap = (states[i + 1] - states[i] - 1) % 4
        word += legacy.lift_word(legacy.workspace_word(gap), [W + j for j in range(BANK)])
        if source_switch and i == switch_index:
            t = (states[i + 1] + switch_phase_delta) % 4
            p = block_diag([matrix_power(legacy.expected_octet_frame(), t)] * 3)
            for j, row in enumerate(p):
                nz = [(k, sign) for k, sign in enumerate(row) if sign]
                require(len(nz) == 1 and nz[0][1] in (-1, 1), "handoff frame selector")
                k, sign = nz[0]
                word.append(legacy.add(W + j, Y + k, sign))
                word.append(legacy.add(W + j, X + k, -sign))
    return word


def source_wrapper(legacy, source, sign):
    return [legacy.add(W + i, source + i, sign) for i in range(BANK)]


def make_root(legacy, states, blocks, source, phase_reader_mutation=None):
    body = lift_batch(legacy, states, blocks, bad_reader_index=phase_reader_mutation)
    return (source_wrapper(legacy, source, 1) + body + source_wrapper(legacy, source, -1)
            + legacy.inverse_word(body))


def expected_map(legacy, pairs):
    """pairs is a list of (bank_offset, blocks); one +1 per block occurrence."""
    out = identity(TOTAL)
    for bank, blocks in pairs:
        for j in range(D):
            for block in blocks:
                out[j][bank + 8 * block + j] += 1
    return out


def vector_total(v):
    return v["ADD"] + v["NEG"]


def vector_reads(v):
    return 2 * v["ADD"] + v["NEG"]


def run():
    legacy, cert = load_predecessor()
    check_typed_children(legacy)
    leaf = cert["recursive_interface_cost"]["leaf_forward"]
    a_costs = phase_costs(legacy)

    # Phase recurrence: exact paths and exhaustive coverage at the three sizes used.
    path3, g3 = best_phase_path(legacy, 3)
    path5, g5 = best_phase_path(legacy, 5)
    path7, g7 = best_phase_path(legacy, 7)
    path10, g10 = best_phase_path(legacy, 10)
    brute3, paths3 = exhaustive_phase_minimum(legacy, 3)
    brute5, paths5 = exhaustive_phase_minimum(legacy, 5)
    brute7, paths7 = exhaustive_phase_minimum(legacy, 7)
    brute10, paths10 = exhaustive_phase_minimum(legacy, 10)
    require(brute3[2] == g3 and paths3 == 64, "three-child recurrence vs exhaustive")
    require(brute5[2] == g5 and paths5 == 1024, "five-child recurrence vs exhaustive")
    require(brute7[2] == g7 and paths7 == 16384, "seven-child recurrence vs exhaustive")
    require(brute10[2] == g10 and paths10 == 1048576, "ten-child recurrence vs exhaustive")

    # Period-4 boundary law of the fixed interface: g(k) depends only on k mod 4.
    law = {}
    for k in range(1, 17):
        _, gv = best_phase_path(legacy, k)
        require(gv == best_phase_path(legacy, k % 4)[1] if k % 4 else gv == a_costs[0],
                "period-4 boundary law at k=" + str(k))
        law[k] = gv
    require(g3 == {"ADD": 54, "NEG": 6} and g7 == {"ADD": 54, "NEG": 6}
            and g10 == {"ADD": 36, "NEG": 12}, "g3/g7/g10 exact vectors")

    # Positive control: reproduce the predecessor's published 5|5 two-bank figures.
    expected55 = expected_map(legacy, [(X, BLOCKS5), (Y, BLOCKS5)])
    root_x = make_root(legacy, path5, BLOCKS5, X)
    root_y = make_root(legacy, path5, BLOCKS5, Y)
    separate55 = root_x + root_y
    plain55 = lift_batch(legacy, path10, BLOCKS10)
    switched55 = lift_batch(legacy, path10, BLOCKS10, source_switch=True, switch_index=4)
    joint55 = (source_wrapper(legacy, X, 1) + switched55 + source_wrapper(legacy, Y, -1)
               + legacy.inverse_word(plain55))
    require(apply_word(separate55, TOTAL) == expected55, "5|5 separate map control")
    require(apply_word(joint55, TOTAL) == expected55, "5|5 joint map control")
    sep55_vec = word_counts(separate55)
    jnt55_vec = word_counts(joint55)
    require(sep55_vec == {"ADD": 1552, "NEG": 144}, "5|5 separate invoice control")
    require(jnt55_vec == {"ADD": 1408, "NEG": 144}, "5|5 joint invoice control")
    require((vector_total(sep55_vec), vector_total(jnt55_vec),
             vector_reads(sep55_vec), vector_reads(jnt55_vec)) ==
            (1696, 1552, 3248, 2960), "5|5 totals/reads control")
    require(g5 == {"ADD": 54, "NEG": 6} and path5 == (0, 0, 1, 2, 3, 0)
            and path10 == (0, 1, 0, 1, 2, 3, 0, 1, 2, 3, 0),
            "predecessor g5/g10 paths control")

    # New cell: heterogeneous 3|7 readers on two distinct source banks.
    expected37 = expected_map(legacy, [(X, BLOCKS_A), (Y, BLOCKS_B)])
    root_a = make_root(legacy, path3, BLOCKS_A, X)
    root_b = make_root(legacy, path7, BLOCKS_B, Y)
    separate37 = root_a + root_b
    plain37 = lift_batch(legacy, path10, BLOCKS_AB)
    switched37 = lift_batch(legacy, path10, BLOCKS_AB, source_switch=True,
                            switch_index=SWITCH_INDEX)
    joint37 = (source_wrapper(legacy, X, 1) + switched37 + source_wrapper(legacy, Y, -1)
               + legacy.inverse_word(plain37))
    require(apply_word(separate37, TOTAL) == expected37,
            "3|7 heterogeneous two-bank separate map")
    require(apply_word(joint37, TOTAL) == expected37,
            "3|7 heterogeneous two-bank joint map")

    sep37_vec = word_counts(separate37)
    jnt37_vec = word_counts(joint37)
    # Recurrence invoices: E_1(k) = 2k*leaf + (2d,0) + 2g(k); joint = 2k*leaf + (4d,0) + 2g(k).
    pred_a = cost_vector_add(
        cost_vector_add({"ADD": 2 * len(BLOCKS_A) * leaf["ADD"],
                         "NEG": 2 * len(BLOCKS_A) * leaf["NEG"]},
                        {"ADD": 2 * BANK, "NEG": 0}),
        {"ADD": 2 * g3["ADD"], "NEG": 2 * g3["NEG"]})
    pred_b = cost_vector_add(
        cost_vector_add({"ADD": 2 * len(BLOCKS_B) * leaf["ADD"],
                         "NEG": 2 * len(BLOCKS_B) * leaf["NEG"]},
                        {"ADD": 2 * BANK, "NEG": 0}),
        {"ADD": 2 * g7["ADD"], "NEG": 2 * g7["NEG"]})
    pred_sep = cost_vector_add(pred_a, pred_b)
    pred_jnt = cost_vector_add(
        cost_vector_add({"ADD": 2 * len(BLOCKS_AB) * leaf["ADD"],
                         "NEG": 2 * len(BLOCKS_AB) * leaf["NEG"]},
                        {"ADD": 4 * BANK, "NEG": 0}),
        {"ADD": 2 * g10["ADD"], "NEG": 2 * g10["NEG"]})
    require(sep37_vec == pred_sep == {"ADD": 1552, "NEG": 144},
            "3|7 separate invoice and recurrence agreement")
    require(jnt37_vec == pred_jnt == {"ADD": 1408, "NEG": 144},
            "3|7 joint invoice and recurrence agreement")
    require((vector_total(sep37_vec), vector_total(jnt37_vec),
             vector_reads(sep37_vec), vector_reads(jnt37_vec)) ==
            (1696, 1552, 3248, 2960), "3|7 totals/reads")
    saving = {"primitives": vector_total(sep37_vec) - vector_total(jnt37_vec),
              "reads": vector_reads(sep37_vec) - vector_reads(jnt37_vec)}
    require(saving == {"primitives": 144, "reads": 288}, "3|7 saving")

    # Invoice law across splits: separate - joint = 2*(g(k1)+g(k2)-g(k1+k2)).
    # With k1+k2 = 10 this is (144,0) exactly when both child counts are odd,
    # and (0,0) when both are even: g(1)=g(3)=(54,6), g(2)=(36,12), g(0)=(0,0).
    split_law = {}
    for k1 in range(1, 10):
        k2 = 10 - k1
        _, gk1 = best_phase_path(legacy, k1)
        _, gk2 = best_phase_path(legacy, k2)
        diff = cost_vector_add(cost_vector_add(
            {"ADD": 2 * gk1["ADD"], "NEG": 2 * gk1["NEG"]},
            {"ADD": 2 * gk2["ADD"], "NEG": 2 * gk2["NEG"]}),
            {"ADD": -2 * g10["ADD"], "NEG": -2 * g10["NEG"]})
        split_law[k1] = diff
        expected_diff = {"ADD": 144, "NEG": 0} if k1 % 2 else {"ADD": 0, "NEG": 0}
        require(diff == expected_diff, "split invoice law at " + str(k1))

    # Even-split instance (2|8): the joint word is legal but merges no boundary work.
    blocks_even = (0, 1) + (2, 1, 0, 2, 1, 0, 2, 2)
    path2, g2 = best_phase_path(legacy, 2)
    path8, g8 = best_phase_path(legacy, 8)
    require(g2 == {"ADD": 36, "NEG": 12} and g8 == {"ADD": 0, "NEG": 0}, "g2/g8 vectors")
    expected28 = expected_map(legacy, [(X, blocks_even[:2]), (Y, blocks_even[2:])])
    root_a2 = make_root(legacy, path2, blocks_even[:2], X)
    root_b2 = make_root(legacy, path8, blocks_even[2:], Y)
    separate28 = root_a2 + root_b2
    plain28 = lift_batch(legacy, path10, blocks_even)
    switched28 = lift_batch(legacy, path10, blocks_even, source_switch=True, switch_index=1)
    joint28 = (source_wrapper(legacy, X, 1) + switched28 + source_wrapper(legacy, Y, -1)
               + legacy.inverse_word(plain28))
    require(apply_word(separate28, TOTAL) == expected28, "2|8 separate map")
    require(apply_word(joint28, TOTAL) == expected28, "2|8 joint map")
    sep28_vec = word_counts(separate28)
    jnt28_vec = word_counts(joint28)
    require(vector_total(sep28_vec) == vector_total(jnt28_vec),
            "2|8 even split must merge no boundary work")
    require(sep28_vec == jnt28_vec, "2|8 even-split invoice equality")

    # Negative controls for the 3|7 cell.
    wrong_switch = lift_batch(legacy, path10, BLOCKS_AB, source_switch=True, switch_index=4)
    wrong_switch_word = (source_wrapper(legacy, X, 1) + wrong_switch
                         + source_wrapper(legacy, Y, -1) + legacy.inverse_word(plain37))
    require(apply_word(wrong_switch_word, TOTAL) != expected37,
            "midpoint-switch control escaped")
    wrong_phase = lift_batch(legacy, path10, BLOCKS_AB, source_switch=True,
                             switch_index=SWITCH_INDEX, switch_phase_delta=1)
    wrong_phase_word = (source_wrapper(legacy, X, 1) + wrong_phase
                        + source_wrapper(legacy, Y, -1) + legacy.inverse_word(plain37))
    require(apply_word(wrong_phase_word, TOTAL) != expected37,
            "wrong handoff phase control escaped")
    wrong_reader_root = make_root(legacy, path3, BLOCKS_A, X, phase_reader_mutation=2)
    require(apply_word(wrong_reader_root + root_b, TOTAL) != expected37,
            "mutated A reader control escaped")
    require(apply_word(root_a, TOTAL) != expected37, "omitted B call control escaped")
    missing_restore = (source_wrapper(legacy, X, 1) + switched37 + legacy.inverse_word(plain37))
    require(apply_word(missing_restore, TOTAL) != expected37,
            "missing final Y restoration control escaped")
    missing_inverse = (source_wrapper(legacy, X, 1) + switched37
                       + source_wrapper(legacy, Y, -1))
    require(apply_word(missing_inverse, TOTAL) != expected37,
            "missing literal inverse control escaped")

    return {
        "status": "PASS_Z4_HETERO_TWO_BANK_3_7",
        "base_commit": BASE,
        "assignment": {
            "track": "recursive-interfaces",
            "task_id": "persistent-boundary",
            "chooser_nonce": "ba18ac446df7d55ddc50d91395fd9a57",
            "scope_key": "026be4b6e61971d51838",
            "priority_revision": 3,
            "card_selection_note": "second-choice card after the centre-path-sharing pair collision",
        },
        "predecessors": {
            "PR1391_head": PR1391_HEAD,
            "PR1410_head": PR1410_HEAD,
            "PR1391_certificate_sha256": PINS["inputs/PR1391/CERTIFICATE.json"][0],
            "PR1391_verifier_sha256": PINS["inputs/PR1391/verify.py"][0],
            "PR1410_readme_sha256": PINS["inputs/PR1410-README.md"][0],
            "nearest_packages": [
                "research/z4-distinct-source-seed55 (typed two-bank 5|5, midpoint handoff)",
                "research/z4-heterogeneous-pair-seed3x7 (heterogeneous 3|7, one shared source, canonical phase path)",
            ],
        },
        "scope": "Exact phase-indexed typed child family with heterogeneous reader schedules on two distinct source banks; not an admitted selected supplier.",
        "dimensions": {"D": D, "X": BANK, "Y": BANK, "W": BANK, "total_basis_columns": TOTAL},
        "types": {
            "A_blocks": list(BLOCKS_A),
            "A_source": "X",
            "B_blocks": list(BLOCKS_B),
            "B_source": "Y",
            "handoff": "W += P^t (Y-X) after child 2, t = phase[3]; 48 ADDs",
            "handoff_phase": path10[SWITCH_INDEX + 1],
        },
        "phase_reader": "C_(i,t): D += Q^(-t) R_i W; W += (P-I)W; type t has same ADD/NEG count as C_i.",
        "recurrence": {
            "workspace_phase_costs_ADD_NEG": a_costs,
            "F0(t)": "A(t)",
            "Fnext(s)": "min_t F(t)+A((s-t-1) mod 4)",
            "terminal_phase": 0,
            "period_4_law": "g(k) = g(k mod 4) with g(0) = (0,0); checked for k = 1..16",
            "g3_path": list(path3), "g3_ADD_NEG": g3, "g3_exhaustive_paths": paths3,
            "g5_path": list(path5), "g5_ADD_NEG": g5, "g5_exhaustive_paths": paths5,
            "g7_path": list(path7), "g7_ADD_NEG": g7, "g7_exhaustive_paths": paths7,
            "g10_path": list(path10), "g10_ADD_NEG": g10, "g10_exhaustive_paths": paths10,
            "split_invoice_law": "separate(k1,k2) - joint(k1,k2) = 2*(g(k1)+g(k2)-g(10)); at total 10 this is 144 ADDs iff both child counts are odd and 0 when both are even",
            "split_law_vectors": {str(k): v for k, v in split_law.items()},
        },
        "predecessor_5_5_control": {
            "separate_ADD_NEG": sep55_vec,
            "joint_ADD_NEG": jnt55_vec,
            "separate_primitives": vector_total(sep55_vec),
            "joint_primitives": vector_total(jnt55_vec),
            "map": "PASS on all 80 basis columns",
            "matches_research/z4-distinct-source-seed55": True,
        },
        "separate_calls": {
            "ADD_NEG": sep37_vec,
            "primitives": vector_total(sep37_vec),
            "reads": vector_reads(sep37_vec),
            "prefix_row_l1_peak": row_l1_peak(separate37, TOTAL),
            "map": "PASS on all 80 basis columns",
        },
        "joint_3_7_two_banks": {
            "ADD_NEG": jnt37_vec,
            "primitives": vector_total(jnt37_vec),
            "reads": vector_reads(jnt37_vec),
            "prefix_row_l1_peak": row_l1_peak(joint37, TOTAL),
            "map": "PASS on all 80 basis columns",
        },
        "saving": saving,
        "even_split_2_8_control": {
            "A_blocks": list(blocks_even[:2]),
            "B_blocks": list(blocks_even[2:]),
            "separate_ADD_NEG": sep28_vec,
            "joint_ADD_NEG": jnt28_vec,
            "saving": {"primitives": vector_total(sep28_vec) - vector_total(jnt28_vec),
                       "reads": vector_reads(sep28_vec) - vector_reads(jnt28_vec)},
            "map": "PASS on all 80 basis columns for both words",
            "meaning": "even splits merge no boundary work; the 144 saving needs both child counts odd",
        },
        "controls": {
            "predecessor_5_5_invoices_and_maps": "PASS",
            "typed_child_phase_identity_checks": "PASS for 12 (phase,reader) pairs",
            "exhaustive_phase_coverage": "PASS at 64 + 1024 + 16384 + 1048576 paths",
            "midpoint_switch_instead_of_3_7_boundary": "REJECTED",
            "wrong_handoff_phase": "REJECTED",
            "mutated_A_reader": "REJECTED",
            "omitted_B_call": "REJECTED",
            "missing_final_Y_restoration": "REJECTED",
            "missing_literal_inverse": "REJECTED",
        },
        "assumptions_and_limits": [
            "Output-row reindexing is part of the typed ADD target choice and has no additional scalar ADD/NEG instruction in this word model.",
            "Address, tape, source-hosting, precision admission, recursive assembly into a selected supplier and analytic transfer are not charged or proved.",
            "The joint word raises the prefix row-L1 envelope; no precision improvement is claimed.",
            "The finite recurrence is exact only for the declared order-four phase-indexed child alphabet; it is not a lower bound for arbitrary words.",
            "No new kappa or selected-result change is claimed.",
        ],
    }


def main():
    result = run()
    certificate_path = PACKAGE / "RESULT.json"
    canonical = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if sys.argv[1:] == ["--write-result"]:
        certificate_path.write_text(canonical, encoding="utf-8", newline="\n")
        print("WROTE_RESULT " + str(certificate_path.relative_to(ROOT)))
    else:
        require(certificate_path.is_file(), "missing RESULT.json; run --write-result once")
        require(certificate_path.read_text(encoding="utf-8") == canonical,
                "RESULT.json differs from the recomputed exact evidence")
    print(result["status"] +
          f" g3={vector_total(result['recurrence']['g3_ADD_NEG'])}"
          f" g7={vector_total(result['recurrence']['g7_ADD_NEG'])}"
          f" g10={vector_total(result['recurrence']['g10_ADD_NEG'])}"
          f" separate={result['separate_calls']['primitives']}"
          f" joint={result['joint_3_7_two_banks']['primitives']}"
          f" saved={result['saving']['primitives']}"
          f" reads_saved={result['saving']['reads']}"
          f" law=odd_splits_only even28_saved={result['even_split_2_8_control']['saving']['primitives']}"
          f" paths=64+1024+16384+1048576 basis=80 controls=6")


if __name__ == "__main__":
    main()
