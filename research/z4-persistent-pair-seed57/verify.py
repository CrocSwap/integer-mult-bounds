#!/usr/bin/env python3
"""Check whether two order-four root echoes can share their middle restoration."""

import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "bce54fb3f895cbe5cd4c0eb477c3afeed100190f"
PREDECESSOR_HEAD = "6ce8017e4c27c8b220b6c3a27a53bb18f138212a"
PREDECESSOR_CERT_SHA256 = "2a6ac306ddc6f58514b89f680d8ff3027b4195e2754574f8f04ac1f17785c9d3"
PREDECESSOR_CERT_BLOB = "0132b117d90f1a7a97c40af3e38503c117604e00"
PREDECESSOR_CODE_SHA256 = "c3d8e76dad9b3cc159affa5e56dbf73612eab0c0ce4a4464f523d4cf47669c05"
PREDECESSOR_CODE_BLOB = "9d866bbf57a6d1f012a21687bde2e231c90efd14"
CERT_PATH = HERE / "inputs/PR1391-CERTIFICATE.json"
CODE_PATH = HERE / "inputs/PR1391-verify.py"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def load_legacy():
    cert_raw = CERT_PATH.read_bytes()
    code_raw = CODE_PATH.read_bytes()
    require(hashlib.sha256(cert_raw).hexdigest() == PREDECESSOR_CERT_SHA256, "PR1391 certificate SHA")
    require(hashlib.sha256(code_raw).hexdigest() == PREDECESSOR_CODE_SHA256, "PR1391 verifier SHA")
    cert_blob = subprocess.run(["git", "hash-object", str(CERT_PATH)], cwd=ROOT,
                               check=True, capture_output=True, text=True).stdout.strip()
    code_blob = subprocess.run(["git", "hash-object", str(CODE_PATH)], cwd=ROOT,
                               check=True, capture_output=True, text=True).stdout.strip()
    require(cert_blob == PREDECESSOR_CERT_BLOB and code_blob == PREDECESSOR_CODE_BLOB,
            "PR1391 Git blob pins")
    spec = importlib.util.spec_from_file_location("pr1391_pinned", CODE_PATH)
    legacy = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(legacy)
    cert = json.loads(cert_raw)
    require(cert["base_commit"] == BASE and cert["assignment"]["os_seed"] == 56,
            "PR1391 base/assignment pin")
    for path, digest in cert["source_pins"].items():
        pinned = subprocess.run(["git", "show", BASE + ":" + path], cwd=ROOT,
                                check=True, capture_output=True).stdout
        require(hashlib.sha256(pinned).hexdigest() == digest, "PR1391 inherited source pin " + path)
    require(cert["boundary"]["dynamic_program_total"] == 140
            and cert["boundary"]["exhaustive_path_count"] == 1024,
            "PR1391 five-child control")
    return legacy, cert


def addv(a, b):
    return tuple(x + y for x, y in zip(a, b))


def total(v):
    return sum(v)


def phase_vectors(legacy, cert):
    per_octet = [legacy.word_counts(legacy.octet_word(p)) for p in range(4)]
    recorded = [(row["ADD"], row["NEG"]) for row in cert["frame"]["phase_costs_per_octet"]]
    require(per_octet == recorded == [(0, 0), (18, 2), (12, 4), (18, 2)], "phase gate costs")
    return [tuple(3 * x for x in v) for v in per_octet], per_octet


def step_vector(old, new, work, output):
    return addv(work[(new - old - 1) % 4], output[(new - old) % 4])


def path_vector(states, work, output):
    v = addv(work[states[0]], output[states[0]])
    for old, new in zip(states, states[1:]):
        v = addv(v, step_vector(old, new, work, output))
    return v


def optimize(k, work, output):
    # F_0(t)=A(t)+B(t); each step completes one child and aligns at s.
    f = [total(addv(work[t], output[t])) for t in range(4)]
    parents = []
    for _ in range(k):
        nxt, pred = [0] * 4, [0] * 4
        for s in range(4):
            nxt[s], pred[s] = min((f[t] + total(step_vector(t, s, work, output)), t)
                                   for t in range(4))
        f = nxt
        parents.append(pred)
    state = 0
    reverse = [state]
    for pred in reversed(parents):
        state = pred[state]
        reverse.append(state)
    states = list(reversed(reverse))
    v = path_vector(states, work, output)
    require(total(v) == f[0], "recurrence path vector")
    return states, v


def exhaustive(k, work, output):
    best = None
    checked = 0
    for prefix in itertools.product(range(4), repeat=k):
        states = prefix + (0,)
        v = path_vector(states, work, output)
        candidate = (total(v), states, v)
        if best is None or candidate < best:
            best = candidate
        checked += 1
    return best, checked


def emit_echo(legacy, states, blocks, wrong_first_output_phase=False, require_terminal=True):
    require(len(states) == len(blocks) + 1, "echo path length")
    if require_terminal:
        require(states[-1] == 0, "root echo must restore canonical terminal frame")
    body_local = legacy.batch_word(states, blocks=blocks,
                                   wrong_first_output_phase=wrong_first_output_phase)
    mapping = list(range(legacy.OUTPUT_WIDTH)) + [
        legacy.OUTPUT_WIDTH + legacy.WORK_WIDTH + i for i in range(legacy.WORK_WIDTH)]
    body = legacy.lift_word(body_local, mapping)
    word = [legacy.add(legacy.OUTPUT_WIDTH + legacy.WORK_WIDTH + i,
                       legacy.OUTPUT_WIDTH + i)
            for i in range(legacy.WORK_WIDTH)]
    word += body
    word += [legacy.add(legacy.OUTPUT_WIDTH + legacy.WORK_WIDTH + i,
                        legacy.OUTPUT_WIDTH + i, -1)
             for i in range(legacy.WORK_WIDTH)]
    word += legacy.inverse_word(body)
    return word


def expected_double_echo(legacy, blocks):
    width = legacy.ECHO_WIDTH
    rows = legacy.identity(width)
    for block in blocks:
        for j in range(legacy.OUTPUT_WIDTH):
            rows[j][legacy.OUTPUT_WIDTH + 8 * block + j] += 1
    return rows


def path_rows(states):
    return [{"after_child": i, "phase": s} for i, s in enumerate(states)]


def build_result():
    legacy, predecessor = load_legacy()
    work, output = phase_vectors(legacy, predecessor)
    blocks5 = tuple(legacy.BLOCKS)
    blocks10 = blocks5 + blocks5
    states5, g5 = optimize(5, work, output)
    states10, g10 = optimize(10, work, output)
    brute5, paths5 = exhaustive(5, work, output)
    brute10, paths10 = exhaustive(10, work, output)
    require((states5, g5, paths5, brute5[0]) ==
            ([0, 1, 2, 3, 0, 0], (126, 14), 1024, 140), "five-child control")
    require((states10, g10, paths10, brute10[0]) ==
            ([0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 0], (216, 32), 1048576, 248),
            "ten-child exhaustive optimum")

    one = emit_echo(legacy, states5, blocks5)
    separate = one + one
    joint = emit_echo(legacy, states10, blocks10)
    eager_states = [0] * 11
    eager = emit_echo(legacy, eager_states, blocks10)
    expected_one = expected_double_echo(legacy, blocks5)
    expected_joint = expected_double_echo(legacy, blocks10)
    require(legacy.apply_word_matrix(one, legacy.ECHO_WIDTH) == expected_one,
            "five-child positive control map")
    require(legacy.apply_word_matrix(separate, legacy.ECHO_WIDTH) == expected_joint,
            "two successive calls do not compose to the doubled reader map")
    require(legacy.apply_word_matrix(joint, legacy.ECHO_WIDTH) == expected_joint,
            "joint ten-child word has the wrong dirty-state map")
    require(legacy.apply_word_matrix(eager, legacy.ECHO_WIDTH) == expected_joint,
            "eager ten-child control map")
    require(legacy.apply_word_matrix(one, legacy.ECHO_WIDTH) != expected_joint,
            "one-call omission control escaped")

    wrong_output_phase = emit_echo(legacy, states10, blocks10, wrong_first_output_phase=True)
    require(legacy.apply_word_matrix(wrong_output_phase, legacy.ECHO_WIDTH) != expected_joint,
            "wrong output phase control escaped")
    terminal_bad = list(states10)
    terminal_bad[-1] = 1
    terminal_word = emit_echo(legacy, terminal_bad, blocks10, require_terminal=False)
    require(legacy.apply_word_matrix(terminal_word, legacy.ECHO_WIDTH) != expected_joint,
            "missing terminal restoration control escaped")

    leaf = tuple(predecessor["recursive_interface_cost"]["leaf_forward"][k]
                 for k in ("ADD", "NEG"))
    require(leaf == (62, 6), "leaf vector")
    def root_invoice(k, boundary):
        return addv(addv(tuple(2 * k * x for x in leaf), (48, 0)),
                    tuple(2 * x for x in boundary))
    joint_vector = root_invoice(10, g10)
    single_vector = root_invoice(5, g5)
    separate_vector = tuple(2 * x for x in single_vector)
    eager_boundary = tuple(10 * x for x in work[3])
    eager_vector = root_invoice(10, eager_boundary)
    joint_counts = legacy.word_counts(joint)
    separate_counts = legacy.word_counts(separate)
    eager_counts = legacy.word_counts(eager)
    joint_prefix = legacy.prefix_row_l1_peak(joint, legacy.ECHO_WIDTH)
    separate_prefix = legacy.prefix_row_l1_peak(separate, legacy.ECHO_WIDTH)
    require(joint_counts == joint_vector and separate_counts == separate_vector
            and eager_counts == eager_vector, "complete vector invoice")
    require((total(joint_vector), total(separate_vector), total(eager_vector)) ==
            (1904, 2016, 2608), "complete primitive total")
    require(joint_vector == (1720, 184) and separate_vector == (1840, 176),
            "ADD/NEG component totals")
    require((joint_prefix, separate_prefix) == (42, 30), "complete echo prefix row-L1 peaks")

    result = {
        "schema_version": 1,
        "base_commit": BASE,
        "assignment_seed": 57,
        "predecessor": {"pr": 1391, "head": PREDECESSOR_HEAD,
                        "certificate_sha256": PREDECESSOR_CERT_SHA256,
                        "certificate_git_blob": PREDECESSOR_CERT_BLOB,
                        "verifier_sha256": PREDECESSOR_CODE_SHA256,
                        "verifier_git_blob": PREDECESSOR_CODE_BLOB,
                        "inherited_source_pin_count": len(predecessor["source_pins"])},
        "question": "carry the aligned P/Q frame across the middle of two identical five-child root echoes",
        "phase_costs": {"workspace_A_by_phase": [list(v) for v in work],
                        "output_B_by_phase": [list(v) for v in output]},
        "five_child_control": {"states": states5, "boundary_vector_ADD_NEG": list(g5),
                                "total": total(g5), "exhaustive_paths": paths5},
        "ten_child_joint": {"states": states10, "mid_call_phase": states10[5],
                            "boundary_vector_ADD_NEG": list(g10), "boundary_total": total(g10),
                            "exhaustive_paths": paths10, "exhaustive_minimum": brute10[0],
                            "complete_vector_ADD_NEG": list(joint_vector),
                            "complete_primitives": total(joint_vector),
                            "word_sha256": legacy.word_sha256(joint),
                            "reads": 2 * joint_vector[0] + joint_vector[1],
                            "writes": total(joint_vector),
                            "prefix_row_l1_peak": legacy.prefix_row_l1_peak(joint, legacy.ECHO_WIDTH)},
        "two_separate_calls": {"one_call_vector_ADD_NEG": list(single_vector),
                               "combined_vector_ADD_NEG": list(separate_vector),
                               "combined_primitives": total(separate_vector),
                               "word_sha256": legacy.word_sha256(separate),
                               "prefix_row_l1_peak": separate_prefix,
                               "reads": 2 * separate_vector[0] + separate_vector[1],
                               "writes": total(separate_vector)},
        "eager_ten_child_control": {"vector_ADD_NEG": list(eager_vector),
                                    "primitives": total(eager_vector)},
        "saving_joint_vs_separate": {"ADD": separate_vector[0] - joint_vector[0],
                                     "NEG": separate_vector[1] - joint_vector[1],
                                     "total_primitives": total(separate_vector) - total(joint_vector),
                                     "reads": 2 * separate_vector[0] + separate_vector[1]
                                             - (2 * joint_vector[0] + joint_vector[1]),
                                     "writes": total(separate_vector) - total(joint_vector)},
        "map": "(D,X,W)->(D + 2*sum_i R_i X, X, W)",
        "basis_columns": legacy.ECHO_WIDTH,
        "controls": {"one_call_omission": "REJECTED", "wrong_output_phase": "REJECTED",
                     "missing_terminal_restoration": "REJECTED", "two_call_map": "PASS",
                     "joint_word_map": "PASS", "eager_map": "PASS"},
        "scope": "Exact for two identical calls on the same source X, the pinned PR1391 child family, and the stated order-four macro alphabet. No supplier admission or kappa claim."
    }
    return result


def main():
    result = build_result()
    (HERE / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("PASS_Z4_PERSISTENT_PAIR")
    print("g5", result["five_child_control"]["total"],
          "g10", result["ten_child_joint"]["boundary_total"],
          "paths", result["ten_child_joint"]["exhaustive_paths"])
    print("two_calls", result["two_separate_calls"]["combined_primitives"],
          "joint", result["ten_child_joint"]["complete_primitives"],
          "saving", result["saving_joint_vs_separate"]["total_primitives"],
          "vector", result["ten_child_joint"]["complete_vector_ADD_NEG"],
          "basis_columns", result["basis_columns"], "negative_controls=3")


if __name__ == "__main__":
    main()
