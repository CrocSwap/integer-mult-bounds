#!/usr/bin/env python3
"""Verify a reversible two-clean-output sum-anchor block and exact cost screen."""
import argparse
import importlib.util
import json
from fractions import Fraction as Q
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
RESULT = PACKAGE / "RESULT.json"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def operations(q):
    """Forward recipe: two products, one temporary shear, fanouts/products, restore."""
    out = [("child", 0, 0), ("child", 1, 1), ("xor", 0, 1)]
    for i in range(2, q):
        out.extend((("xor", i, 0), ("child", i, i)))
    out.append(("xor", 0, 1))
    return out


def direct_operations(q):
    out = [("child", 0, 0), ("child", 1, 1)]
    for i in range(2, q):
        out.extend((("child", i, 0), ("child", i, 1), ("child", i, i)))
    return out


def joint_shared_operations(q):
    """Joint rank-q schedule with separate anchor fanouts to each target."""
    out = [("child", 0, 0), ("child", 1, 1)]
    for i in range(2, q):
        out.extend((("xor", i, 0), ("xor", i, 1), ("child", i, i)))
    return out


def apply_symbolic(q, ops, initial_dirty, initial_poly=None):
    products = [1 << i for i in range(q)]
    poly = [0] * q if initial_poly is None else list(initial_poly)
    dirty = list(initial_dirty)
    for kind, dest, arg in ops:
        if kind == "child":
            poly[dest] ^= products[arg]
        elif kind == "xor":
            poly[dest] ^= poly[arg]
            dirty[dest] ^= dirty[arg]
        else:
            raise ValueError("unknown operation")
    return poly, dirty


def expected_symbolic(q, dirty):
    poly = [1, 2] + [3 | (1 << i) for i in range(2, q)]
    return poly, list(dirty)


def apply_boolean(q, ops, products, initial):
    values = list(initial)
    for kind, dest, arg in ops:
        if kind == "child":
            values[dest] ^= products[arg]
        elif kind == "xor":
            values[dest] ^= values[arg]
        else:
            raise ValueError("unknown operation")
    return values


def exact_boolean_map(q, x, y, dirty):
    products = [((x >> i) & 1) & ((y >> i) & 1) for i in range(q)]
    expected = [products[0], products[1]]
    expected.extend(dirty[i - 2] ^ products[0] ^ products[1] ^ products[i]
                    for i in range(2, q))
    return products, expected


def gf2_rank(rows):
    pivots = {}
    for value in rows:
        x = int(value)
        while x:
            p = x.bit_length() - 1
            if p in pivots:
                x ^= pivots[p]
            else:
                for q, y in tuple(pivots.items()):
                    if (y >> p) & 1:
                        pivots[q] = y ^ x
                pivots[p] = x
                break
    return len(pivots)


def load_ceiling():
    path = ROOT / "research/complex-local-word-ceiling/ceiling.py"
    spec = importlib.util.spec_from_file_location("pinned_complex_ceiling", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def profile(blocks, extra_per_block=0):
    return {1: Q(2412 - 220 * blocks + extra_per_block * blocks),
            2: Q(418), 3: Q(432), 4: Q(142), 5: Q(82), 8: Q(8)}


def cost_screen():
    c = load_ceiling()
    selected = json.loads((ROOT / "research/complex-local-word-ceiling/RESULT.json")
                          .read_text(encoding="utf-8"))
    base = {int(r): int(n)
            for r, n in selected["selected"]["local_profile_per_call"].items()}
    need(base == {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8},
         "selected profile changed")
    base_bracket = c.ceiling(base, 73, 896, 9, 64)
    need(base_bracket[1] == Q(selected["ceiling"]["a_ceiling"]),
         "selected ceiling replay mismatch")
    target = base_bracket[1] * Q(105, 100)
    need(target == Q(35491136290869, 20000000000000000),
         "5-percent target changed")

    q = 112
    direct = 3 * q - 4
    anchored = q
    saving = direct - anchored
    adds = q
    ordinary_joint_adds = 2 * (q - 2)
    shear_adds_saved = ordinary_joint_adds - adds
    max_blocks = base[1] // direct
    need((direct, anchored, saving, adds, ordinary_joint_adds, shear_adds_saved,
          max_blocks) == (332, 112, 220, 112, 220, 108, 7),
         "q=112 local invoice or block cap changed")
    need(8 * direct > base[1] and 7 * direct <= base[1],
         "seven-block direct budget boundary changed")

    brackets = {}
    target_relaxations = {}
    for e in (0, 112, 183, 184, 220):
        p = profile(7, e)
        brackets[str(e)] = [str(z) for z in c.ceiling(p, 73, 896, 9, 64)]
        target_relaxations[str(e)] = [str(z) for z in c.relax(p, 73, 896, 9, 64, target)]
    need(Q(brackets["0"][0]) > target,
         "zero-tariff seven-block profile does not beat 5-percent target")
    need(Q(brackets["112"][0]) > target,
         "one rank-one-equivalent unit per affine ADD misses the target")
    need(Q(brackets["183"][0]) > target,
         "e=183 boundary should pass")
    need(Q(brackets["184"][1]) < target,
         "e=184 boundary should fail")
    need(Q(target_relaxations["183"][1]) < 1
         and Q(target_relaxations["184"][0]) > 1,
         "exact moment boundary signs changed")
    need(brackets["220"] == [str(z) for z in base_bracket]
         and Q(target_relaxations["220"][0]) > 1,
         "unit tariff on every ordinary joint fanout should return to the selected profile")
    return {
        "selected_profile": {str(r): n for r, n in sorted(base.items())},
        "selected_ceiling_bracket": [str(z) for z in base_bracket],
        "five_percent_target_a": str(target),
        "block_width_q": q,
        "direct_rank_one_children_per_block": direct,
        "anchored_rank_one_children_per_block": anchored,
        "rank_one_children_saved_per_block": saving,
        "affine_additions_per_block": adds,
        "ordinary_joint_separate_anchor_fanout_additions": ordinary_joint_adds,
        "temporary_shear_additions_saved": shear_adds_saved,
        "max_direct_blocks_in_rank_one_profile": max_blocks,
        "seven_block_profile_e0": {str(r): str(n) for r, n in sorted(profile(7).items())},
        "seven_block_profile_e183": {str(r): str(n) for r, n in sorted(profile(7, 183).items())},
        "seven_block_profile_e184": {str(r): str(n) for r, n in sorted(profile(7, 184).items())},
        "ceiling_brackets_by_extra_tariff": brackets,
        "target_relaxation_intervals_by_extra_tariff": target_relaxations,
        "interpretation": "e is the total additional rank-one-equivalent price per block, including the q affine additions and any clean-output/interface costs; the 112 affine additions are separately counted and are not asserted to cost 112 rank-one children.",
    }


def build_result():
    q_values = list(range(3, 113))
    symbolic_cases = 0
    for q in q_values:
        dirty = [0, 0] + [((i * 7 + 3) & 1) for i in range(2, q)]
        want = expected_symbolic(q, dirty)
        ops = operations(q)
        got = apply_symbolic(q, ops, dirty)
        need(got == want, f"symbolic forward map failed at q={q}")
        joint = apply_symbolic(q, joint_shared_operations(q), dirty)
        need(joint == want, f"separate-anchor joint schedule failed at q={q}")
        restored = apply_symbolic(q, list(reversed(ops)), got[1], got[0])
        need(restored == ([0] * q, dirty), f"symbolic inverse failed at q={q}")
        need(len(ops) == q + q, f"forward invoice failed at q={q}")
        slices = [1, 2] + [3 | (1 << i) for i in range(2, q)]
        need(gf2_rank(slices) == q, f"output slice rank failed at q={q}")
        symbolic_cases += 1

    # The Boolean interpreter checks concrete inputs, all dirty targets, and
    # exact inverse restoration for the smallest nontrivial widths.
    exhaustive = {}
    for q in (3, 4, 5):
        cases = 0
        for x in range(1 << q):
            for y in range(1 << q):
                for d in range(1 << (q - 2)):
                    dirty_targets = [(d >> i) & 1 for i in range(q - 2)]
                    initial = [0, 0, *dirty_targets]
                    products, expected = exact_boolean_map(q, x, y, dirty_targets)
                    forward_ops = operations(q)
                    actual = apply_boolean(q, forward_ops, products, initial)
                    direct = apply_boolean(q, direct_operations(q), products, initial)
                    joint = apply_boolean(q, joint_shared_operations(q), products, initial)
                    need(actual == expected == direct == joint,
                         f"Boolean forward identity failed at q={q}, x={x}, y={y}, d={d}")
                    restored = apply_boolean(q, list(reversed(forward_ops)), products, actual)
                    need(restored == initial,
                         f"Boolean inverse failed at q={q}, x={x}, y={y}, d={d}")
                    cases += 1
        exhaustive[str(q)] = cases

    # Four semantic mutations must be detected.
    q = 4
    dirty = [0] * q
    correct = expected_symbolic(q, dirty)
    base_ops = operations(q)
    missing_restore = apply_symbolic(q, base_ops[:-1], dirty)
    missing_fanout_ops = [op for op in base_ops if op != ("xor", 2, 0)]
    missing_fanout = apply_symbolic(q, missing_fanout_ops, dirty)
    dirty_anchor = [1, 0, 0, 0]
    dirty_anchor_out = apply_symbolic(q, base_ops, dirty_anchor)
    wrong_q_ops = list(base_ops)
    wrong_q_ops[1] = ("child", 1, 0)
    wrong_product = apply_symbolic(q, wrong_q_ops, dirty)
    controls = {
        "missing_final_anchor_restore_rejected": missing_restore != correct,
        "missing_target_fanout_rejected": missing_fanout != correct,
        "dirty_anchor_entry_rejected": dirty_anchor_out != correct,
        "wrong_second_common_product_rejected": wrong_product != correct,
    }
    need(all(controls.values()), "a semantic negative control was missed")

    cost = cost_screen()
    return {
        "status": "PASS_TWO_OUTPUT_TEMPORARY_SUM_ANCHOR",
        "domain": {"q": [3, 112], "exact_symbolic_widths": symbolic_cases,
                   "exhaustive_boolean_cases_by_q": exhaustive},
        "mathematics": {
            "field": "F_2",
            "products": "P=x0*y0; Q=x1*y1; R_i=x_i*y_i for 2<=i<q",
            "outputs": "F0=P; F1=Q; F_i=P+Q+R_i for 2<=i<q",
            "tensor_rank": "exactly q: q explicit rank-one products attain q, and the q output-slice matrices are linearly independent",
            "entry_contract": "A0=A1=0; A2..A(q-1) arbitrary dirty accumulators; all sources immutable",
            "forward_schedule": "compute P into A0 and Q into A1; XOR A1 into A0; for each i>=2 XOR A0 into Ai then compute Ri into Ai; XOR A1 into A0 to restore F0=P",
            "children_per_forward": "q rank-one products",
            "affine_additions_per_forward": "q",
            "helpers_copies_frame_changes": "0, 0, 0",
            "inverse": "reverse schedule restores all target inputs and dirty accumulators; its separate invoice is q rank-one inverses and q affine additions",
        },
        "controls": controls,
        "cost_screen": cost,
        "limitations": [
            "The two clean result outputs and common input-pair occurrences are a changed local interface; no selected-provider placement is supplied.",
            "The exact affine-add count is itemized. Its conversion to rank-one-equivalent price is only the explicit e tariff in the moment screen.",
            "No selected supplier, outer interface, precision admission, conditional bound, or kappa change is claimed.",
        ],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write-result", action="store_true")
    args = ap.parse_args()
    result = build_result()
    if args.write_result:
        RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                          encoding="utf-8")
        print("WROTE", RESULT.relative_to(ROOT))
        return
    expected = json.loads(RESULT.read_text(encoding="utf-8"))
    need(result == expected, "recomputed construction/cost evidence differs from RESULT.json")
    print("PASS_TWO_OUTPUT_TEMPORARY_SUM_ANCHOR q=3..112 q112_children=112 q112_adds=112 blocks=7 tariff=183/184 local_only")


if __name__ == "__main__":
    main()
