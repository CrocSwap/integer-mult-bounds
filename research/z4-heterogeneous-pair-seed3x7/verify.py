#!/usr/bin/env python3
"""Verify a heterogeneous 3+7 root-echo composition in the pinned Z4 macro model."""
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BASE = "0b1cccf86e2f5132ed286a26ef0a681a495740ea"
PREDECESSOR = ROOT / "research/z4-persistent-pair-seed57/verify.py"
CERTIFICATE = HERE / "CERTIFICATE.json"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def load_pair_module():
    spec = importlib.util.spec_from_file_location("pinned_z4_pair_seed57", PREDECESSOR)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def vec_add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def vec_scale(a, n):
    return tuple(n * x for x in a)


def vec_total(a):
    return sum(a)


def costs(legacy):
    output = [legacy.word_counts(legacy.octet_word(p)) for p in range(4)]
    work = [vec_scale(v, legacy.WORK_OCTETS) for v in output]
    require(output == [(0, 0), (18, 2), (12, 4), (18, 2)], "pinned output phase costs")
    require(legacy.WORK_OCTETS == 3, "pinned three-octet work frame")
    return work, output


def phase_step(old, new, work, output):
    return vec_add(work[(new - old - 1) % 4], output[(new - old) % 4])


def path_invoice(states, work, output):
    invoice = vec_add(work[states[0]], output[states[0]])
    for old, new in zip(states, states[1:]):
        invoice = vec_add(invoice, phase_step(old, new, work, output))
    return invoice


def dynamic_plan(k, work, output):
    # Initial state pays A(t)+B(t); each child transition pays the two frame changes.
    dp = [vec_total(vec_add(work[t], output[t])) for t in range(4)]
    parents = []
    for _ in range(k):
        next_dp, pred = [0] * 4, [0] * 4
        for new in range(4):
            next_dp[new], pred[new] = min(
                (dp[old] + vec_total(phase_step(old, new, work, output)), old)
                for old in range(4))
        dp = next_dp
        parents.append(pred)
    state = 0
    reverse = [state]
    for pred in reversed(parents):
        state = pred[state]
        reverse.append(state)
    states = tuple(reversed(reverse))
    invoice = path_invoice(states, work, output)
    require(vec_total(invoice) == dp[0], "dynamic program path invoice")
    return states, invoice


def exhaustive_plan(k, work, output):
    best = None
    checked = 0
    for prefix in itertools.product(range(4), repeat=k):
        states = tuple(prefix) + (0,)
        invoice = path_invoice(states, work, output)
        candidate = (vec_total(invoice), states, invoice)
        if best is None or candidate < best:
            best = candidate
        checked += 1
    return best, checked


def expected_reader_map(legacy, blocks):
    # Exact pinned interface: one output octet, three source octets, three work octets.
    rows = legacy.identity(legacy.ECHO_WIDTH)
    for block in blocks:
        for coordinate in range(legacy.OUTPUT_WIDTH):
            rows[coordinate][legacy.OUTPUT_WIDTH + 8 * block + coordinate] += 1
    return rows


def complete_root_invoice(k, boundary, leaf, wrapper):
    # Both forward and literal-inverse leaves, root copy/restoration wrapper,
    # and both traversals of the boundary path.
    return vec_add(vec_add(vec_scale(leaf, 2 * k), wrapper), vec_scale(boundary, 2))


def main():
    task = json.loads((HERE / "TASK.json").read_text())
    sources = json.loads((HERE / "SOURCES.json").read_text())
    require(task["base_commit"] == BASE == sources["base_commit"], "base commit pin")
    require(task["assignment_seed"] == "65562f37d3a7a48fc2f959e36d6e638c", "seed pin")
    for row in sources["files"]:
        path = ROOT / row["path"]
        data = path.read_bytes()
        require(hashlib.sha256(data).hexdigest() == row["sha256"], "input SHA-256 drift: " + row["path"])
        blob = subprocess.run(["git", "hash-object", str(path)], cwd=ROOT, check=True,
                              capture_output=True, text=True).stdout.strip()
        require(blob == row["git_blob"], "input Git blob drift: " + row["path"])

    pair = load_pair_module()
    legacy, predecessor_cert = pair.load_legacy()
    work, output = costs(legacy)
    leaf = tuple(predecessor_cert["recursive_interface_cost"]["leaf_forward"][k]
                 for k in ("ADD", "NEG"))
    wrapper = (2 * legacy.WORK_WIDTH, 0)
    require(leaf == (62, 6) and wrapper == (48, 0), "pinned leaf and root wrapper prices")
    blocks_a = (0, 1, 2)
    blocks_b = (2, 1, 0, 2, 1, 0, 2)
    blocks_joint = blocks_a + blocks_b
    require(len(blocks_a) == 3 and len(blocks_b) == 7, "typed arities")
    require(blocks_a != blocks_b[:3] and set(blocks_joint) == {0, 1, 2}, "distinct reader types")
    require(legacy.ECHO_WIDTH == 56 and legacy.OUTPUT_WIDTH == 8, "full dirty interface width")

    plans = {}
    path_counts = {}
    for k in (3, 7, 10):
        plan, invoice = dynamic_plan(k, work, output)
        brute, checked = exhaustive_plan(k, work, output)
        require(vec_total(invoice) == brute[0], f"exhaustive phase minimum k={k}")
        require(invoice == brute[2], f"ADD/NEG tie-break invoice k={k}")
        plans[k] = (plan, invoice)
        path_counts[k] = checked
    states_a, boundary_a = plans[3]
    states_b, boundary_b = plans[7]
    states_joint, boundary_joint = plans[10]
    require(states_a[0] == states_a[-1] == 0 and states_b[0] == states_b[-1] == 0
            and states_joint[0] == states_joint[-1] == 0, "canonical entry and exit frames")

    word_a = pair.emit_echo(legacy, list(states_a), blocks_a)
    word_b = pair.emit_echo(legacy, list(states_b), blocks_b)
    separate = word_a + word_b
    word_joint = pair.emit_echo(legacy, list(states_joint), blocks_joint)
    map_a = expected_reader_map(legacy, blocks_a)
    map_b = expected_reader_map(legacy, blocks_b)
    map_joint = expected_reader_map(legacy, blocks_joint)
    require(map_a != map_b, "A and B must be distinct call types")
    require(legacy.apply_word_matrix(word_a, legacy.ECHO_WIDTH) == map_a, "A dirty map")
    require(legacy.apply_word_matrix(word_b, legacy.ECHO_WIDTH) == map_b, "B dirty map")
    require(legacy.apply_word_matrix(separate, legacy.ECHO_WIDTH) == map_joint,
            "separate A then B composition map")
    require(legacy.apply_word_matrix(word_joint, legacy.ECHO_WIDTH) == map_joint,
            "joint ten-child composition map")

    # Failure controls: omitting B, changing a B reader, the initial output phase,
    # or the terminal restoration must all fail exact full-matrix equality.
    require(legacy.apply_word_matrix(word_a, legacy.ECHO_WIDTH) != map_joint, "omitted B control")
    wrong_blocks = blocks_a + blocks_b[:-1] + (1,)
    wrong_word = pair.emit_echo(legacy, list(states_joint), wrong_blocks)
    require(legacy.apply_word_matrix(wrong_word, legacy.ECHO_WIDTH) != map_joint,
            "wrong B-reader control")
    wrong_phase = pair.emit_echo(legacy, list(states_joint), blocks_joint,
                                 wrong_first_output_phase=True)
    require(legacy.apply_word_matrix(wrong_phase, legacy.ECHO_WIDTH) != map_joint,
            "wrong output-phase control")
    bad_terminal = list(states_joint)
    bad_terminal[-1] = 1
    missing_restore = pair.emit_echo(legacy, bad_terminal, blocks_joint, require_terminal=False)
    require(legacy.apply_word_matrix(missing_restore, legacy.ECHO_WIDTH) != map_joint,
            "missing terminal restoration control")

    invoice_a = complete_root_invoice(3, boundary_a, leaf, wrapper)
    invoice_b = complete_root_invoice(7, boundary_b, leaf, wrapper)
    invoice_joint = complete_root_invoice(10, boundary_joint, leaf, wrapper)
    measured_a = legacy.word_counts(word_a)
    measured_b = legacy.word_counts(word_b)
    measured_separate = legacy.word_counts(separate)
    measured_joint = legacy.word_counts(word_joint)
    require(measured_a == invoice_a and measured_b == invoice_b, "separate complete invoices")
    require(measured_joint == invoice_joint, "joint complete invoice")
    require(measured_separate == vec_add(invoice_a, invoice_b), "separate complete sum")
    require((invoice_a, invoice_b, invoice_joint) == ((624, 64), (1264, 128), (1720, 184)),
            "recorded typed ADD/NEG invoices")
    total_separate = vec_add(invoice_a, invoice_b)
    saving = vec_add(total_separate, vec_scale(invoice_joint, -1))
    require(saving == (168, 8) and sum(saving) == 176, "exact saving")

    def access_counts(v):
        adds, negs = v
        return {"ADD": adds, "NEG": negs, "primitive_writes": adds + negs,
                "primitive_reads": 2 * adds + negs}

    prefix_separate = legacy.prefix_row_l1_peak(separate, legacy.ECHO_WIDTH)
    prefix_joint = legacy.prefix_row_l1_peak(word_joint, legacy.ECHO_WIDTH)
    require((prefix_separate, prefix_joint) == (36, 42), "prefix row-L1 invoices")
    for word in (word_a, word_b, separate, word_joint):
        require(all(kind in ("ADD", "NEG") and 0 <= target < legacy.ECHO_WIDTH
                    and (source is None or 0 <= source < legacy.ECHO_WIDTH)
                    for kind, target, source, sign in word), "word escaped the 56-coordinate dirty interface")

    result = {
        "result": "HETEROGENEOUS_3_PLUS_7_COMPOSITION_VERIFIED",
        "base_commit": BASE,
        "assignment_seed": task["assignment_seed"],
        "selected_record_sha256": task["selected_record_sha256"],
        "predecessor": {"package": "research/z4-persistent-pair-seed57",
                        "pr1391_base": pair.BASE,
                        "pr1391_head": pair.PREDECESSOR_HEAD,
                        "certificate_sha256": pair.PREDECESSOR_CERT_SHA256,
                        "verifier_sha256": pair.PREDECESSOR_CODE_SHA256},
        "interface": {"phase_group": "Z/4Z", "echo_width": legacy.ECHO_WIDTH,
                      "output_width": legacy.OUTPUT_WIDTH, "workspace_octets": legacy.WORK_OCTETS,
                      "leaf_forward_ADD_NEG": list(leaf), "root_wrapper_ADD_NEG": list(wrapper),
                      "arbitrary_dirty_coordinates": legacy.ECHO_WIDTH,
                      "type_A_source_blocks": list(blocks_a),
                      "type_B_source_blocks": list(blocks_b),
                      "joint_source_blocks": list(blocks_joint)},
        "phase_search": {str(k): {"paths_checked": path_counts[k],
                                   "states": list(plans[k][0]),
                                   "boundary_ADD_NEG": list(plans[k][1]),
                                   "boundary_total": vec_total(plans[k][1])}
                         for k in (3, 7, 10)},
        "invoices": {
            "type_A": {**access_counts(invoice_a), "total_primitives": sum(invoice_a),
                       "prefix_row_l1": legacy.prefix_row_l1_peak(word_a, legacy.ECHO_WIDTH)},
            "type_B": {**access_counts(invoice_b), "total_primitives": sum(invoice_b),
                       "prefix_row_l1": legacy.prefix_row_l1_peak(word_b, legacy.ECHO_WIDTH)},
            "separate_A_then_B": {**access_counts(total_separate),
                                   "total_primitives": sum(total_separate),
                                   "prefix_row_l1": prefix_separate},
            "joint": {**access_counts(invoice_joint), "total_primitives": sum(invoice_joint),
                      "prefix_row_l1": prefix_joint},
            "saving_separate_minus_joint": {"ADD": saving[0], "NEG": saving[1],
                                            "total_primitives": sum(saving),
                                            "fraction": "11/130"}
        },
        "dirty_map_checks": {"type_A": "PASS", "type_B": "PASS",
                             "separate_composition": "PASS", "joint_composition": "PASS",
                             "basis_columns_checked_per_map": legacy.ECHO_WIDTH},
        "negative_controls": ["omit type B", "alter final B reader", "wrong initial output phase",
                              "omit terminal restoration"],
        "limits": ["No physical supplier, tape, coefficient-access or fixed-precision admission is proved.",
                   "Peak row-L1 rises from 36 to 42, so no precision improvement is claimed.",
                   "No new kappa or multiplication exponent follows from this macro-interface experiment."]
    }
    CERTIFICATE.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(result["result"], "saving", saving, "total", sum(saving))
    print("phase_paths", path_counts, "dirty_width", legacy.ECHO_WIDTH,
          "prefix_l1", prefix_separate, "->", prefix_joint)
    print("certificate", CERTIFICATE)


if __name__ == "__main__":
    main()
