#!/usr/bin/env python3
"""Exact phase-indexed two-source echo construction and bounded recurrence."""
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
BASE = "4040a0f46d67b41c36a472a7cd4af791fd4c36cc"
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
    require("two identical five-child root echoes on the same source" in source_readme and "(D, X, W)" in source_readme,
            "PR1410 predecessor snapshot mismatch")

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
    for block in sorted(set(BLOCKS5)):
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


def lift_batch(legacy, states, blocks, source_switch=False, switch_phase_delta=0,
               bad_reader_index=None):
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
        if source_switch and i == 4:
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


def expected_two_source(legacy):
    out = identity(TOTAL)
    for j in range(D):
        for block in BLOCKS5:
            out[j][X + 8 * block + j] += 1
            out[j][Y + 8 * block + j] += 1
    return out


def make_naive_fixed_reader(legacy, states):
    """Control: try the midpoint handoff with the original common output frame."""
    blocks = BLOCKS10
    work_global = [W + j for j in range(BANK)]
    local_map = list(range(D)) + work_global
    body = legacy.lift_word(legacy.octet_word(states[0]), list(range(D)))
    body += legacy.lift_word(legacy.workspace_word(states[0]), work_global)
    for i, block in enumerate(blocks):
        body += legacy.lift_word(legacy.child_word(block), local_map)
        gap = (states[i + 1] - states[i] - 1) % 4
        out_phase = (states[i + 1] - states[i]) % 4
        body += legacy.lift_word(legacy.workspace_word(gap), work_global)
        body += legacy.lift_word(legacy.octet_word(out_phase), list(range(D)))
        if i == 4:
            t = states[i + 1]
            p = block_diag([matrix_power(legacy.expected_octet_frame(), t)] * 3)
            for j, row in enumerate(p):
                k, sign = next((k, v) for k, v in enumerate(row) if v)
                body.append(legacy.add(W + j, Y + k, sign))
                body.append(legacy.add(W + j, X + k, -sign))
    base = legacy.lift_word(
        legacy.batch_word(states, blocks=blocks),
        [*range(D), *[W + j for j in range(BANK)]],
    )
    return (source_wrapper(legacy, X, 1) + body + source_wrapper(legacy, Y, -1)
            + legacy.inverse_word(base))


def run():
    legacy, cert = load_predecessor()
    check_typed_children(legacy)
    path5, g5 = best_phase_path(legacy, 5)
    path10, g10 = best_phase_path(legacy, 10)
    brute5, paths5 = exhaustive_phase_minimum(legacy, 5)
    brute10, paths10 = exhaustive_phase_minimum(legacy, 10)
    require((path5, g5, paths5, brute5[0]) ==
            ((0, 0, 1, 2, 3, 0), {"ADD": 54, "NEG": 6}, 1024, 60),
            "five-child phase recurrence and exhaustive minimum")
    require((brute5[1], brute5[2]) == (path5, g5),
            "five-child recurrence path matches exhaustive witness")
    require((path10, g10, paths10, brute10[0]) ==
            ((0, 1, 0, 1, 2, 3, 0, 1, 2, 3, 0),
             {"ADD": 36, "NEG": 12}, 1048576, 48),
            "ten-child phase recurrence and exhaustive minimum")
    require((brute10[1], brute10[2]) == (path10, g10),
            "ten-child recurrence path matches exhaustive witness")

    expected = expected_two_source(legacy)
    root_x = make_root(legacy, path5, BLOCKS5, X)
    root_y = make_root(legacy, path5, BLOCKS5, Y)
    separate = root_x + root_y
    plain_body = lift_batch(legacy, path10, BLOCKS10)
    switched_body = lift_batch(legacy, path10, BLOCKS10, source_switch=True)
    joint = (source_wrapper(legacy, X, 1) + switched_body + source_wrapper(legacy, Y, -1)
             + legacy.inverse_word(plain_body))
    separate_map = apply_word(separate, TOTAL)
    joint_map = apply_word(joint, TOTAL)
    require(separate_map == expected, "two separate arbitrary-dirty source calls")
    require(joint_map == expected, "joint distinct-source arbitrary-dirty map")

    leaf = cert["recursive_interface_cost"]["leaf_forward"]
    joint_vector = word_counts(joint)
    separate_vector = word_counts(separate)
    require(joint_vector == {"ADD": 1408, "NEG": 144}, "joint complete ADD/NEG invoice")
    require(separate_vector == {"ADD": 1552, "NEG": 144}, "separate complete ADD/NEG invoice")
    k = len(BLOCKS10)
    expected_joint_vector = {
        "ADD": 2 * k * leaf["ADD"] + 4 * BANK + 2 * g10["ADD"],
        "NEG": 2 * k * leaf["NEG"] + 2 * g10["NEG"],
    }
    expected_separate_vector = {
        "ADD": 2 * (2 * len(BLOCKS5) * leaf["ADD"] + 2 * BANK + 2 * g5["ADD"]),
        "NEG": 2 * (2 * len(BLOCKS5) * leaf["NEG"] + 2 * g5["NEG"]),
    }
    require(joint_vector == expected_joint_vector, "joint recurrence matches emitted word")
    require(separate_vector == expected_separate_vector, "separate recurrence matches emitted words")
    joint_total = sum(joint_vector.values())
    separate_total = sum(separate_vector.values())
    joint_reads = 2 * joint_vector["ADD"] + joint_vector["NEG"]
    separate_reads = 2 * separate_vector["ADD"] + separate_vector["NEG"]
    require((joint_total, separate_total, joint_reads, separate_reads) ==
            (1552, 1696, 2960, 3248), "complete operation/read comparison")

    # Same-reader two-source composition is the matched original-interface control.
    # Reuse the published PR1410 same-source optimum as the naive common-output
    # phase control; it has a different recurrence from the phase-typed variant.
    naive_path = (0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 0)
    fixed_reader_joint = make_naive_fixed_reader(legacy, naive_path)
    fixed_reader_joint_map = apply_word(fixed_reader_joint, TOTAL)
    require(fixed_reader_joint_map == expected, "fixed-reader two-source carry map")
    fixed_path5 = (0, 1, 2, 3, 0, 0)
    fixed_root_x = legacy.lift_word(
        legacy.echo_word(fixed_path5),
        [*range(D), *[X + j for j in range(BANK)], *[W + j for j in range(BANK)]],
    )
    fixed_root_y = legacy.lift_word(
        legacy.echo_word(fixed_path5),
        [*range(D), *[Y + j for j in range(BANK)], *[W + j for j in range(BANK)]],
    )
    fixed_reader_separate = fixed_root_x + fixed_root_y
    require(apply_word(fixed_reader_separate, TOTAL) == expected,
            "fixed-reader two-call baseline map")
    fixed_joint_vector = word_counts(fixed_reader_joint)
    fixed_separate_vector = word_counts(fixed_reader_separate)
    require(fixed_joint_vector == {"ADD": 1768, "NEG": 184},
            "fixed-reader joint invoice")
    require(fixed_separate_vector == {"ADD": 1840, "NEG": 176},
            "fixed-reader separate invoice")
    require(sum(fixed_separate_vector.values()) - sum(fixed_joint_vector.values()) == 64,
            "fixed-reader source-pair saving")

    no_handoff = (source_wrapper(legacy, X, 1) + plain_body + source_wrapper(legacy, Y, -1)
                  + legacy.inverse_word(plain_body))
    require(apply_word(no_handoff, TOTAL) != expected, "omitted source handoff control escaped")
    wrong_handoff = lift_batch(legacy, path10, BLOCKS10, source_switch=True,
                               switch_phase_delta=1)
    wrong_handoff_word = (source_wrapper(legacy, X, 1) + wrong_handoff
                          + source_wrapper(legacy, Y, -1) + legacy.inverse_word(plain_body))
    require(apply_word(wrong_handoff_word, TOTAL) != expected,
            "wrong handoff phase control escaped")
    wrong_reader = make_root(legacy, path5, BLOCKS5, X, phase_reader_mutation=2)
    require(apply_word(wrong_reader + root_y, TOTAL) != expected,
            "wrong reader-type control escaped")
    missing_restore = (source_wrapper(legacy, X, 1) + switched_body
                       + legacy.inverse_word(plain_body))
    require(apply_word(missing_restore, TOTAL) != expected,
            "missing final Y restoration control escaped")
    missing_inverse = (source_wrapper(legacy, X, 1) + switched_body
                       + source_wrapper(legacy, Y, -1))
    require(apply_word(missing_inverse, TOTAL) != expected,
            "missing literal inverse control escaped")
    # The selected phase type costs the same number of primitives as the old child;
    # this check records the gate-count premise used by the typed recurrence.
    require(all(word_counts(typed_child(legacy, q, b)) == word_counts(legacy.child_word(b))
                for q in range(4) for b in set(BLOCKS5)), "phase-type child gate census")

    return {
        "status": "PASS_Z4_DISTINCT_SOURCE_PHASE_TYPED_ECHO",
        "base_commit": BASE,
        "assignment_seed": 55,
        "predecessors": {
            "PR1391_head": PR1391_HEAD,
            "PR1410_head": PR1410_HEAD,
            "PR1391_certificate_sha256": PINS["inputs/PR1391/CERTIFICATE.json"][0],
            "PR1391_verifier_sha256": PINS["inputs/PR1391/verify.py"][0],
            "PR1410_readme_sha256": PINS["inputs/PR1410-README.md"][0],
        },
        "scope": "Exact phase-indexed typed child family for two distinct source banks and the pinned PR1391 five-child reader sequence; not an admitted selected supplier.",
        "dimensions": {"D": D, "X": BANK, "Y": BANK, "W": BANK, "total_basis_columns": TOTAL},
        "phase_reader": "C_(i,t): D += Q^(-t) R_i W; W += (P-I)W; type t has same ADD/NEG count as C_i.",
        "handoff": {
            "formula": "W += P^t (Y-X) at the 5|5 boundary, t=phase[5]",
            "ADDs": 2 * BANK,
            "selected_phase": path10[5],
        },
        "recurrence": {
            "workspace_phase_costs_ADD_NEG": phase_costs(legacy),
            "F0(t)": "A(t)",
            "Fnext(s)": "min_t F(t)+A((s-t-1) mod 4)",
            "terminal_phase": 0,
            "g5_path": list(path5),
            "g5_ADD_NEG": g5,
            "g5_total": sum(g5.values()),
            "g5_exhaustive_paths": paths5,
            "g10_path": list(path10),
            "g10_ADD_NEG": g10,
            "g10_total": sum(g10.values()),
            "g10_exhaustive_paths": paths10,
        },
        "complete_paid_cost_recurrence": {
            "child_forward_ADD_NEG": leaf,
            "single_source": "2*sum_i(T_i) + (2d,0) + 2*g(k)",
            "two_source_split": "2*sum_i(T_i) + (4d,0) + 2*g(k1+k2)",
            "d": BANK,
            "wrapper_accounting": "single: W+=X and W-=X; two-source: W+=X, two ADDs per coordinate for P^t(Y-X), and W-=Y",
            "literal_inverse": "counted by the factor 2 on every child and phase boundary; inverse leaves preserve ADD/NEG counts",
        },
        "separate_calls": {
            "ADD_NEG": separate_vector,
            "primitives": separate_total,
            "reads": separate_reads,
            "prefix_row_l1_peak": row_l1_peak(separate, TOTAL),
            "map": "PASS on all 80 basis columns",
        },
        "joint_distinct_sources": {
            "ADD_NEG": joint_vector,
            "primitives": joint_total,
            "reads": joint_reads,
            "prefix_row_l1_peak": row_l1_peak(joint, TOTAL),
            "map": "PASS on all 80 basis columns",
        },
        "same_reader_control": {
            "phase_path": list(naive_path),
            "separate_ADD_NEG": fixed_separate_vector,
            "separate_primitives": sum(fixed_separate_vector.values()),
            "joint_ADD_NEG": fixed_joint_vector,
            "joint_primitives": sum(fixed_joint_vector.values()),
            "joint_reads": 2 * fixed_joint_vector["ADD"] + fixed_joint_vector["NEG"],
            "separate_reads": 2 * fixed_separate_vector["ADD"] + fixed_separate_vector["NEG"],
            "joint_prefix_row_l1_peak": row_l1_peak(fixed_reader_joint, TOTAL),
            "separate_prefix_row_l1_peak": row_l1_peak(fixed_reader_separate, TOTAL),
            "map": "PASS on all 80 basis columns",
            "saving_primitives": sum(fixed_separate_vector.values()) - sum(fixed_joint_vector.values()),
        },
        "saving": {"primitives": separate_total - joint_total,
                   "reads": separate_reads - joint_reads},
        "controls": {
            "fixed_reader_midpoint_carry": "PASS",
            "omitted_source_handoff": "REJECTED",
            "wrong_handoff_phase": "REJECTED",
            "wrong_reader_type": "REJECTED",
            "missing_final_source_restore": "REJECTED",
            "typed_child_phase_identity_checks": "PASS for 12 (phase,reader) pairs",
            "missing_literal_inverse": "REJECTED",
        },
        "assumptions_and_limits": [
            "Output-row reindexing is part of the typed ADD target choice and has no additional scalar ADD/NEG instruction in this word model.",
            "Address, tape, source-hosting, precision admission, recursive assembly into a selected supplier and analytic transfer are not charged or proved.",
            "The finite state recurrence is exact only for the declared order-four phase-indexed child alphabet; it is not a lower bound for arbitrary words.",
            "No new kappa or selected-result change is claimed.",
        ],
    }


def main():
    result = run()
    certificate_path = PACKAGE / "RESULT.json"
    canonical = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if sys.argv[1:] == ["--write-result"]:
        certificate_path.write_text(canonical)
        print("WROTE_RESULT " + str(certificate_path.relative_to(ROOT)))
    else:
        require(certificate_path.is_file(), "missing RESULT.json; run --write-result once")
        require(certificate_path.read_text() == canonical,
                "RESULT.json differs from the recomputed exact evidence")
    print(result["status"] +
          f" g5={result['recurrence']['g5_total']} g10={result['recurrence']['g10_total']}"
          f" separate={result['separate_calls']['primitives']}"
          f" joint={result['joint_distinct_sources']['primitives']}"
          f" saved={result['saving']['primitives']} reads_saved={result['saving']['reads']}"
          f" paths=1024+1048576 basis=80 controls=5")


if __name__ == "__main__":
    main()
