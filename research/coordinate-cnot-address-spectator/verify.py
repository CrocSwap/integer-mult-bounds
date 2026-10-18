#!/usr/bin/env python3
"""Exact two-SWAP lower bound with a third address coordinate.

Prepared for commdata2338, with substantial OpenAI Codex assistance.
Apache-2.0. No predecessor implementation is imported.

The natural representation is used ONLY to reject short formal words.
The attaining word is checked separately in the formal group algebra.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ADDRESS_DIMENSION = 3


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identity(n):
    """Binary n-by-n matrix, consecutive n-bit rows, row zero first."""
    return sum(1 << (i * n + i) for i in range(n))


def matrix_product(left, right, n):
    result = 0
    mask = (1 << n) - 1
    for i in range(n):
        selectors = (left >> (i * n)) & mask
        row = 0
        while selectors:
            bit = selectors & -selectors
            row ^= (right >> ((bit.bit_length() - 1) * n)) & mask
            selectors ^= bit
        result |= row << (i * n)
    return result


def projectors(r):
    """All binary rank-one idempotents, with their unique binary u,v."""
    return [
        (u, v, sum(v << (k * r) for k in range(r) if u >> k & 1))
        for u in range(1, 1 << r)
        for v in range(1, 1 << r)
        if (u & v).bit_count() % 2 == 1
    ]


def generators(r):
    n = r * ADDRESS_DIMENSION
    return [
        {
            "u": u, "v": v, "projector": p, "i": i, "j": j,
            "source_shifts": tuple(n * (k * 3 + j) for k in range(r) if v >> k & 1),
            "scatter": sum(1 << (n * (k * 3 + i)) for k in range(r) if u >> k & 1),
        }
        for u, v, p in projectors(r)
        for i in range(3) for j in range(3) if i != j
    ]


def step(state, gate, n):
    """Left multiply by I + (uv^T) tensor E_ij, without a dense multiply."""
    row = 0
    for shift in gate["source_shifts"]:
        row ^= state >> shift
    # The repeated n-bit blocks do not overlap, so multiplication is XOR here.
    return state ^ ((row & ((1 << n) - 1)) * gate["scatter"])


def target_left(state, r, active=2):
    """Left multiply by diag(s12,...,s12,I,...,I)."""
    n = 3 * r
    mask = (1 << n) - 1
    for k in range(active):
        a, b = n * (3 * k), n * (3 * k + 1)
        delta = ((state >> a) ^ (state >> b)) & mask
        state ^= (delta << a) ^ (delta << b)
    return state


def ball_two(r, gates):
    n = 3 * r
    seen = {identity(n)}
    frontier = set(seen)
    layers = [1]
    for _ in range(2):
        new = {step(state, gate, n) for state in frontier for gate in gates} - seen
        layers.append(len(new))
        seen.update(new)
        frontier = new
    return seen, layers


def intersection_scan(r, gates, ball, active=2):
    """Stream every B2 -> B3 edge; no truncation, sampling or heuristic pruning."""
    shifted = {target_left(state, r, active) for state in ball}
    base_hits = len(ball & shifted)
    edge_hits = 0
    for state in ball:
        for gate in gates:
            if step(state, gate, 3 * r) in shifted:
                edge_hits += 1
    return base_hits, edge_hits


def digest_states(states, n):
    width = (n * n + 7) // 8
    h = hashlib.sha256()
    for state in sorted(states):
        h.update(state.to_bytes(width, "little"))
    return h.hexdigest()


def formal_step(state, gate, r):
    """Full F2[GL3(F2)] coefficients: group-matrix label -> scalar matrix."""
    g = identity(3) ^ (1 << (gate["i"] * 3 + gate["j"]))
    out = dict(state)
    for label, coefficient in state.items():
        delta = matrix_product(gate["projector"], coefficient, r)
        for new_label in (label, matrix_product(g, label, 3)):
            out[new_label] = out.get(new_label, 0) ^ delta
    return {label: coefficient for label, coefficient in out.items() if coefficient}


def direct_word(r):
    gates = generators(r)
    return [next(g for g in gates if g["u"] == g["v"] == 1 << k
                 and (g["i"], g["j"]) == pair)
            for k in range(2) for pair in ((0, 1), (1, 0), (0, 1))]


def formal_target(r, active=2):
    p = sum(1 << (k * r + k) for k in range(active))
    s = (1 << 1) | (1 << 3) | (1 << 8)
    result = {s: p, identity(3): identity(r) ^ p}
    return {g: c for g, c in result.items() if c}


def formal_evaluate(word, r):
    state = {identity(3): identity(r)}
    for gate in word:
        state = formal_step(state, gate, r)
    return state


def natural_image(formal, r):
    n = 3 * r
    out = 0
    for label, coefficient in formal.items():
        for row in range(r):
            for col in range(r):
                if coefficient >> (row * r + col) & 1:
                    for i in range(3):
                        for j in range(3):
                            if label >> (i * 3 + j) & 1:
                                out ^= 1 << ((row * 3 + i) * n + col * 3 + j)
    return out


def check_sources():
    source = json.loads((HERE / "SOURCES.json").read_text())
    for item in source["files"]:
        if item["usage"] == "input":
            require(hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest()
                    == item["sha256"], "source pin mismatch: " + item["path"])


def load_independent():
    spec = importlib.util.spec_from_file_location("spectator_independent", HERE / "independent.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def controls(r, ball, gates):
    """Boundary and model controls, not tests of implementation spelling."""
    n = 3 * r
    word = direct_word(r)
    target = formal_target(r)
    names = []
    for k in range(6):
        require(formal_evaluate(word[:k] + word[k + 1:], r) != target,
                "omitted call was not rejected")
        names.append("omit_call_" + str(k))
    bad = list(word)
    bad[0] = next(g for g in gates if g["u"] == g["v"] == 1 and (g["i"], g["j"]) == (0, 2))
    require(formal_evaluate(bad, r) != target, "spectator substitution was not rejected")
    names.append("wrong_spectator_label")

    # Forgetting the spectator's restoration would accept this altered endpoint.
    spectator = next(g for g in gates if g["u"] == g["v"] == 1 and (g["i"], g["j"]) == (2, 0))
    bad_endpoint = formal_evaluate(word + [spectator], r)
    require(bad_endpoint != target, "unrestored address coordinate accepted")
    mask = sum(((1 << n) - 1) << (row * n) for row in range(n) if row % 3 != 2)
    require((natural_image(bad_endpoint, r) ^ natural_image(target, r)) & mask == 0,
            "spectator control does not preserve visible rows")
    names.append("unrestored_address_spectator")

    if r == 3:
        dirty_gate = next(g for g in gates if g["u"] == g["v"] == 4 and (g["i"], g["j"]) == (0, 1))
        leak = formal_evaluate(word + [dirty_gate], r)
        require(leak != target, "dirty register not restored")
        clean_columns = sum(1 << (row * n + col) for row in range(n) for col in range(6))
        require((natural_image(leak, r) ^ natural_image(target, r)) & clean_columns == 0,
                "clean-only control fixture is invalid")
        names.append("clean_only_dirty_register_fault")

    # A natural representation is not faithful on the group algebra.
    a = identity(3) ^ (1 << 1)
    b = identity(3) ^ (1 << 3)
    group = {identity(3), a, b, matrix_product(a, b, 3), matrix_product(b, a, 3),
             matrix_product(matrix_product(a, b, 3), a, 3)}
    kernel = {g: 1 for g in group}
    require(len(group) == 6 and kernel and natural_image(kernel, r) == 0,
            "nonfaithfulness control is invalid")
    altered = dict(target)
    for label in kernel:
        altered[label] = altered.get(label, 0) ^ 1
    altered = {g: c for g, c in altered.items() if c}
    require(altered != target and natural_image(altered, r) == natural_image(target, r),
            "natural equality incorrectly accepted as formal equality")
    names.append("nonfaithful_natural_representation")

    one = target_left(identity(n), r, active=1)
    require(one not in ball, "one swap incorrectly found within two calls")
    p, q = intersection_scan(r, gates, ball, active=1)
    require(p + q > 0, "positive one-swap endpoint not recovered")
    require(identity(n) in ball, "identity missing from ball")
    names.extend(["one_swap_positive", "identity_positive"])

    p2 = sum(1 << (k * r + k) for k in range(2))
    enlarged = [dict(word[k], projector=p2) for k in range(3)]
    require(formal_evaluate(enlarged, r) == target, "rank-two alphabet control invalid")
    require(all(g["projector"] != p2 for g in gates), "rank-two projector admitted")
    names.append("rank_two_unit_price_outside_alphabet")
    return names


def compute_receipt():
    independent = load_independent()
    rows = []
    for r in (2, 3):
        gates = generators(r)
        expected_projectors = (1 << (r - 1)) * ((1 << r) - 1)
        require(len(projectors(r)) == expected_projectors, "incomplete projector domain")
        require(len(gates) == 6 * expected_projectors, "incomplete gate domain")
        for g in gates:
            require(matrix_product(g["projector"], g["projector"], r) == g["projector"],
                    "non-idempotent paid projector")
            require(step(step(identity(3 * r), g, 3 * r), g, 3 * r) == identity(3 * r),
                    "paid gate is not an involution")
        ball, layers = ball_two(r, gates)
        base_hits, edge_hits = intersection_scan(r, gates, ball)
        require(base_hits == edge_hits == 0, "a natural-image short candidate exists; formal check required")
        other_ball, other_layers, other_generators, other_hits = independent.census(r)
        require(other_ball == ball and other_layers == layers, "independent complete ball mismatch")
        require(other_generators == {step(identity(3 * r), g, 3 * r) for g in gates},
                "independent alphabet mismatch")
        require(other_hits == (0, 0), "independent intersection mismatch")
        target = formal_target(r)
        require(formal_evaluate(direct_word(r), r) == target, "formal six-call witness failed")
        require(natural_image(target, r) == target_left(identity(3 * r), r), "target representation mismatch")
        control_names = controls(r, ball, gates)
        rows.append({
            "registers": r, "address_dimension": 3, "projectors": expected_projectors,
            "generators": len(gates), "exact_distance_layers_0_1_2": layers,
            "ball_2_size": len(ball), "ball_2_sha256": digest_states(ball, 3 * r),
            "shifted_ball_2_sha256": digest_states({target_left(s, r) for s in ball}, 3 * r),
            "base_intersection": base_hits, "edge_intersection": edge_hits,
            "edge_attempts_per_engine": len(ball) * len(gates),
            "independent_complete_ball_and_alphabet_equal": True,
            "formal_upper_bound": 6, "minimum_paid_calls": 6,
            "controls": control_names,
        })
    return {"schema_version": 1, "result": "finite_lower_bound_plus_formal_upper_bound",
            "model": "M_r(F2[GL_3(F2)]); all six coordinate CNOTs; r=2,3",
            "no_new_kappa": True, "cases": rows}


def check_receipt(actual, expected):
    require(actual == expected, "receipt mismatch")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print recomputed receipt, do not write it")
    args = parser.parse_args()
    check_sources()
    receipt = compute_receipt()
    if args.emit:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    else:
        check_receipt(receipt, json.loads((HERE / "EXPECTED.json").read_text()))
        count = sum(len(case["controls"]) for case in receipt["cases"])
        print("PASS_COORDINATE_CNOT_ADDRESS_SPECTATOR minimum=6 registers=2,3 "
              f"address_dimension=3 controls={count} no_new_kappa")


if __name__ == "__main__":
    main()
