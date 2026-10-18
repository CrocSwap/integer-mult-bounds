#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Verify a two-output temporary-sum anchor with arbitrary dirty targets."""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
import gzip
import json
from pathlib import Path
import sys
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = "research/community-frontier1094-audit/selected-replay.tar.gz"
ARCHIVE_MEMBER = "candidate/strict/global/base/providers/gauge44/LOCAL-PROGRAMS.json.gz"
ARCHIVE_MEMBER_SHA256 = "241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a"
RANKS = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2) + "\n").encode()


def load_sources():
    pins = json.loads((HERE / "SOURCES.json").read_bytes())
    for item in pins["files"]:
        raw = (ROOT / item["path"]).read_bytes()
        need(sha256(raw).hexdigest() == item["sha256"], "source pin: " + item["path"])
    with tarfile.open(ROOT / ARCHIVE, "r:gz") as archive:
        matches = [m for m in archive.getmembers() if m.name == ARCHIVE_MEMBER]
        need(len(matches) == 1 and matches[0].isfile(), "unique selected local-program member")
        raw = archive.extractfile(matches[0]).read()
    need(sha256(raw).hexdigest() == ARCHIVE_MEMBER_SHA256, "selected local-program member digest")
    return json.loads(gzip.decompress(raw))


def selected_target_dirt(programs):
    """Use the retained exact scalar replay to bind the selected dirty-output boundary."""
    replay_path = ROOT / "research/centre-owner-observation-floor/verify.py"
    spec = spec_from_file_location("selected_centre_scalar_replay", replay_path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    _, end = module.replay(programs["forward"])
    for p in range(112):
        need(end[("L", 112 + p)] == {112 + p: Q(1), p: Q(1)},
             "selected forward target must retain arbitrary entry dirt")
    return 112


def selected_source_structure(programs):
    """Pin the structural surfaces inspected in the bounded source-block attempt."""
    with tarfile.open(ROOT / ARCHIVE, "r:gz") as archive:
        def member(name):
            matches = [m for m in archive.getmembers() if m.name == name]
            need(len(matches) == 1 and matches[0].isfile(), "unique source member: " + name)
            raw = archive.extractfile(matches[0]).read()
            return json.loads(gzip.decompress(raw) if name.endswith(".gz") else raw)

        word = member("candidate/strict/global/base/providers/gauge44/CANONICAL-WORD.json.gz")
        full = member("candidate/strict/global/base/providers/gauge44/FULL-WORD.json.gz")
        recipes = member("candidate/strict/global/base/providers/gauge44/CLIFFORD-RECIPES.json")
    need(len(word["ports"]) == 112, "selected provider ports")
    need(len(word["edges"]) == len(recipes["children"]) == 2896,
         "selected frame-transition recipe count")
    need(len(full["root_lines"]) == len(full["scatter"]) == 112,
         "selected root/scatter row count")
    need(all(len(row) == 8 for row in full["root_lines"] + full["scatter"]),
         "selected root/scatter row width")
    need(len(programs["forward"]) == 24767, "selected scalar event count")
    return {
        "ports": len(word["ports"]),
        "frame_transition_recipes": len(recipes["children"]),
        "root_rows": len(full["root_lines"]),
        "scatter_rows": len(full["scatter"]),
        "root_and_scatter_width": 8,
        "forward_scalar_events": len(programs["forward"]),
        "extracted_112_output_product_group": False,
        "scope": "Inspected artifact shape only; not a proof that no product grouping exists.",
    }


def add_poly(dst, src, coefficient):
    out = dict(dst)
    for monomial, value in src.items():
        total = out.get(monomial, Q(0)) + coefficient * value
        if total:
            out[monomial] = total
        else:
            out.pop(monomial, None)
    return out


def program(q, omit_dirty_compensation=False, omit_pre_temp_restore=False,
            omit_temp_restore=False, omit_fanout=False, wrong_q_product=False):
    """Operations on q dirty output registers, plus q rank-one product shears."""
    ops = []
    # Temporarily form d0+d1 in A0, so each other target needs one dirt
    # compensation shear instead of separately subtracting both anchors.
    ops.append(("add", 0, 1, 1))
    for i in range(2, q):
        if not omit_dirty_compensation:
            ops.append(("add", i, 0, -1))
    if not omit_pre_temp_restore:
        ops.append(("add", 0, 1, -1))
    # Product P into A0 and Q into A1.  A child product is one recursive call.
    ops.append(("child", 0, 0, 1))
    ops.append(("child", 1, (0, 1) if wrong_q_product else 1, 1))
    ops.append(("add", 0, 1, 1))  # temporary P+Q anchor, contaminated by d0+d1
    for i in range(2, q):
        if not omit_fanout:
            ops.append(("add", i, 0, 1))
        ops.append(("child", i, i, 1))
    if not omit_temp_restore:
        ops.append(("add", 0, 1, -1))
    return ops


def product_monomial(q, product_index):
    if isinstance(product_index, tuple):
        i, j = product_index
    else:
        i = j = product_index
    return (1 << i) | (1 << (q + j))


def run_symbolic(q, ops, initial=None):
    if initial is None:
        initial = [{1 << (2*q + i): Q(1)} for i in range(q)]
    regs = [dict(row) for row in initial]
    for kind, dst, src, coefficient in ops:
        if kind == "add":
            regs[dst] = add_poly(regs[dst], regs[src], Q(coefficient))
        else:
            monomial = product_monomial(q, src)
            regs[dst] = add_poly(regs[dst], {monomial: Q(1)}, Q(coefficient))
    return regs


def inverse_program(ops):
    return [(kind, dst, src, -coefficient)
            for kind, dst, src, coefficient in reversed(ops)]


def expected_symbolic(q):
    expected = []
    expected.append({1 << (2*q): Q(1), product_monomial(q, 0): Q(1)})
    expected.append({1 << (2*q + 1): Q(1), product_monomial(q, 1): Q(1)})
    for i in range(2, q):
        expected.append({1 << (2*q + i): Q(1), product_monomial(q, 0): Q(1),
                         product_monomial(q, 1): Q(1), product_monomial(q, i): Q(1)})
    return expected


def slice_rank(q):
    # Columns are P,Q,R_2,...,R_(q-1); rows are the output slices.
    matrix = [[Q(0) for _ in range(q)] for _ in range(q)]
    matrix[0][0] = matrix[1][1] = Q(1)
    for i in range(2, q):
        matrix[i][0] = matrix[i][1] = matrix[i][i] = Q(1)
    rank, col = 0, 0
    while rank < q and col < q:
        pivot = next((r for r in range(rank, q) if matrix[r][col]), None)
        if pivot is None:
            col += 1
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        value = matrix[rank][col]
        matrix[rank] = [x / value for x in matrix[rank]]
        for r in range(q):
            if r != rank and matrix[r][col]:
                value = matrix[r][col]
                matrix[r] = [x - value*y for x, y in zip(matrix[r], matrix[rank])]
        rank += 1
        col += 1
    return rank


def eval_program(q, ops, values, modulus):
    x = values[:q]
    y = values[q:2*q]
    out = list(values[2*q:])
    for kind, dst, src, coefficient in ops:
        if kind == "add":
            out[dst] = (out[dst] + coefficient*out[src]) % modulus
        else:
            i, j = src if isinstance(src, tuple) else (src, src)
            out[dst] = (out[dst] + coefficient*x[i]*y[j]) % modulus
    return out


def expected_numeric(q, values, modulus):
    x, y, dirty = values[:q], values[q:2*q], values[2*q:]
    products = [(x[i]*y[i]) % modulus for i in range(q)]
    return [
        (dirty[0] + products[0]) % modulus,
        (dirty[1] + products[1]) % modulus,
        *[(dirty[i] + products[0] + products[1] + products[i]) % modulus
          for i in range(2, q)],
    ]


def exhaustive(q, modulus):
    ops = program(q)
    checked = 0
    for values in product(range(modulus), repeat=3*q):
        values = list(values)
        forward = eval_program(q, ops, values, modulus)
        need(forward == expected_numeric(q, values, modulus), "finite forward mismatch")
        restored = eval_program(q, inverse_program(ops),
                                values[:2*q] + forward, modulus)
        need(restored == values[2*q:], "finite inverse mismatch")
        checked += 1
    return checked


def exact_budget():
    selected = json.loads((ROOT / "certificates/selected-result.json").read_bytes())
    assembly = json.loads((ROOT / "research/community-frontier1094-audit/ASSEMBLY.json").read_bytes())
    ceiling_result = json.loads((ROOT / "research/complex-local-word-ceiling/RESULT.json").read_bytes())
    scalar = json.loads((ROOT / "research/centre-sharing-overhead-budget/RESULT.json").read_bytes())["scalar_overhead"]
    need(selected["kappa"] == ceiling_result["selected"]["kappa"], "selected record / ceiling pin")
    need(ceiling_result["selected"]["local_profile_per_call"] == {str(k): v for k, v in RANKS.items()},
         "selected per-call child profile")
    q = 112
    direct, anchored = 3*q - 4, q
    blocks = RANKS[1] // direct
    need(blocks == 7 and (blocks + 1)*direct > RANKS[1], "seven direct blocks fit exactly")
    changed = dict(RANKS)
    changed[1] -= blocks * (direct - anchored)
    need(changed[1] == 872, "changed rank-one profile")
    sys.path.insert(0, str(ROOT / "research/complex-local-word-ceiling"))
    import ceiling  # noqa: E402
    lo, hi = ceiling.ceiling(changed, 73, 896, 9, 64, grid=Q(1, 10**12))
    kappa_hi = hi / (1 + hi)

    added_macros = blocks * (2*q)
    per_macro = scalar["adapter_growth_per_extra_macro"]
    own_primitive_upper = added_macros * 8  # 4 per real component, two components
    new_bound = scalar["local_primitive_bound"] + added_macros*per_macro + own_primitive_upper
    guard = 1 << 48
    need(added_macros < scalar["extra_macros_per_call_upper_bound"], "scalar macro allowance")
    need(new_bound < guard, "complete local scalar guard")
    bit_endpoint = Q(assembly["bit_lower"])
    return {
        "selected_kappa": selected["kappa"],
        "selected_local_profile_per_call": {str(k): v for k, v in RANKS.items()},
        "q112_direct_children": direct,
        "q112_dirty_anchor_children": anchored,
        "q112_affine_additions": 2*q,
        "children_saved_per_block": direct - anchored,
        "direct_blocks_in_selected_rank_one_count": blocks,
        "hypothetical_profile_after_seven_blocks": {str(k): v for k, v in changed.items()},
        "local_complex_ceiling": {
            "a_interval": [str(lo), str(hi)],
            "kappa_upper": str(kappa_hi),
            "kappa_upper_decimal": float(kappa_hi),
            "above_unchanged_bit_endpoint": kappa_hi > bit_endpoint,
            "unchanged_bit_endpoint": str(bit_endpoint),
            "unchanged_bit_endpoint_decimal": assembly["bit_decimal"],
        },
        "separate_scalar_invoice": {
            "added_unit_addition_macros_per_call": added_macros,
            "macro_allowance_upper_bound_per_call": scalar["extra_macros_per_call_upper_bound"],
            "adapter_growth_per_macro": per_macro,
            "own_primitive_upper_per_macro": 8,
            "old_local_primitive_bound": scalar["local_primitive_bound"],
            "new_local_primitive_bound_upper": new_bound,
            "guard": str(guard),
            "remaining_guard_slack": guard-new_bound,
            "scope": "Conservative scalar-envelope screen only; selected product-map placement and full supplier replay are not established.",
        },
    }


def build():
    widths = list(range(3, 113))
    symbolic_count = 0
    for q in widths:
        ops = program(q)
        need(sum(op[0] == "child" for op in ops) == q, "child count")
        need(sum(op[0] == "add" for op in ops) == 2*q, "affine-add count")
        need(slice_rank(q) == q, "output slice rank")
        initial = [{1 << (2*q+i): Q(1)} for i in range(q)]
        result = run_symbolic(q, ops, initial)
        need(result == expected_symbolic(q), "symbolic forward map")
        need(run_symbolic(q, inverse_program(ops), result) == initial, "symbolic inverse")
        symbolic_count += 1

    finite = {"F2_q3": exhaustive(3, 2), "F2_q4": exhaustive(4, 2),
              "F2_q5": exhaustive(5, 2), "F3_q3": exhaustive(3, 3),
              "F3_q4": exhaustive(4, 3)}

    controls = {}
    q = 3
    target = expected_symbolic(q)
    controls["missing_dirty_precompensation_rejected"] = run_symbolic(
        q, program(q, omit_dirty_compensation=True)) != target
    controls["missing_pre_anchor_restore_rejected"] = run_symbolic(
        q, program(q, omit_pre_temp_restore=True)) != target
    controls["missing_final_anchor_restore_rejected"] = run_symbolic(
        q, program(q, omit_temp_restore=True)) != target
    controls["missing_target_fanout_rejected"] = run_symbolic(
        q, program(q, omit_fanout=True)) != target
    controls["wrong_second_common_product_rejected"] = run_symbolic(
        q, program(q, wrong_q_product=True)) != target
    need(all(controls.values()), "semantic mutation controls")

    programs = load_sources()
    dirty_targets = selected_target_dirt(programs)
    source_structure = selected_source_structure(programs)
    budget = exact_budget()
    return {
        "status": "PASS_DIRTY_OUTPUT_TEMPORARY_SUM_ANCHOR",
        "contract": "For arbitrary dirty targets A_i, compute A_0+=P; A_1+=Q; A_i+=P+Q+R_i for i>=2, with all sources unchanged.",
        "widths_symbolically_checked": symbolic_count,
        "finite_assignments_checked": finite,
        "selected_provider_dirty_target_coordinates": dirty_targets,
        "selected_source_structure": source_structure,
        "controls": controls,
        "q112": {
            "children": 112,
            "affine_additions": 224,
            "direct_children": 332,
            "children_saved": 220,
            "scratch_helpers": 0,
            "frames_changed": 0,
            "sources_changed": 0,
        },
        "budget": budget,
        "claim_boundary": "This contribution does not improve the selected kappa, which remains 0.001672660197076918. It proves an exact local construction and conditional profile screen only; no selected operand-group placement or supplier is established. This is not a claim that no future implementation can improve kappa.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path)
    parser.add_argument("--receipt", type=Path, default=HERE / "RESULT.json")
    args = parser.parse_args()
    result = build()
    if args.write:
        with args.write.open("xb") as stream:
            stream.write(canonical(result))
    else:
        need(canonical(result) == canonical(json.loads(args.receipt.read_bytes())), "receipt mismatch")
    print("PASS_DIRTY_OUTPUT_TEMPORARY_SUM_ANCHOR q=3..112 q112_children=112 adds=224 blocks=7 rank1=872 selected_targets=dirty local_only")


if __name__ == "__main__":
    main()
