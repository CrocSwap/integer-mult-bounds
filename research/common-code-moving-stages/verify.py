#!/usr/bin/env python3
"""Exact moving-coordinate fixtures; universal claims are in PROOF.md.

Cinna Davis, with substantial OpenAI Codex assistance. Apache-2.0.
No predecessor executable, optimizer or numerical library is imported.
"""
import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def apply(rows, x):
    return sum(((r & x).bit_count() & 1) << i for i, r in enumerate(rows))


def row_product(mask, rows):
    out = 0
    for i, r in enumerate(rows):
        if mask >> i & 1:
            out ^= r
    return out


def compose(a, b):
    """Signed monomials: |x> -> (-1)^(p.x) |Gx>; rightmost first."""
    ga, pa = a
    gb, pb = b
    return tuple(row_product(r, gb) for r in ga), pb ^ row_product(pa, gb)


def inverse(a):
    rows, phase = a
    n = len(rows)
    aug = [r | (1 << (n + i)) for i, r in enumerate(rows)]
    for j in range(n):
        pivot = next((i for i in range(j, n) if aug[i] >> j & 1), None)
        require(pivot is not None, "singular label map")
        aug[j], aug[pivot] = aug[pivot], aug[j]
        for i in range(n):
            if i != j and aug[i] >> j & 1:
                aug[i] ^= aug[j]
    inv = tuple(r >> n for r in aug)
    return inv, row_product(phase, inv)


def identity(n):
    return tuple(1 << i for i in range(n)), 0


def embed(a, block, blocks=2):
    rows, phase = a
    sites = [0] + list(range(1 + 8 * block, 9 + 8 * block))
    result, outphase = list(identity(1 + 8 * blocks)[0]), 0
    for i, gi in enumerate(sites):
        result[gi] = sum(((rows[i] >> j) & 1) << gj for j, gj in enumerate(sites))
        outphase |= ((phase >> i) & 1) << gi
    return tuple(result), outphase


def swap_blocks(s, t, blocks):
    rows = list(identity(1 + 8 * blocks)[0])
    for j in range(8):
        a, b = 1 + 8 * s + j, 1 + 8 * t + j
        rows[a], rows[b] = rows[b], rows[a]
    return tuple(rows), 0


def load_inputs():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    for row in manifest["files"]:
        if row.get("usage") == "input":
            data = (ROOT / row["path"]).read_bytes()
            require(hashlib.sha256(data).hexdigest() == row["sha256"], "source SHA256 mismatch")
    normal = json.loads((ROOT / "research/coded-native-caller/NORMALIZERS.json").read_text())
    code = json.loads((ROOT / "research/native-center-free-code/CODE.json").read_text())
    return normal["ports"], [[Fraction(x) for x in r] for r in code["A"]]


def word_state(word, blocks):
    """P_perm times product D_b^exponent; each D_b has eight Gaussian axes."""
    perm, exponents = list(range(blocks)), [0] * blocks
    for s in word:
        # E_s=P_(0,s) D_0 on the left. D_0 passes through the current
        # P_perm to add one D at perm^-1(0).
        exponents[perm.index(0)] += 1
        perm = [s if x == 0 else 0 if x == s else x for x in perm]
    return tuple(perm), tuple(exponents)


def direct_word_checks():
    """Independent address-array execution of the one-axis/block skeleton.

    F_65537 contains i=256. No binary-matrix normal-form routine is used.
    This finite check corroborates the universal block/tensor proof.
    """
    prime = 65537
    a, b = 257 * 32769 % prime, -255 * 32769 % prime

    def gaussian(values, axis):
        out = [0] * len(values)
        bit = 1 << axis
        for x in range(len(values)):
            if not x & bit:
                y = x | bit
                out[x] = (a * values[x] + b * values[y]) % prime
                out[y] = (b * values[x] + a * values[y]) % prime
        return out

    def swap(values, stage):
        out = [0] * len(values)
        for x, value in enumerate(values):
            y = x ^ ((1 << stage) | 1) if (x & 1) != ((x >> stage) & 1) else x
            out[y] = value
        return out

    require((256 * 256) % prime == prime - 1, "finite-field imaginary unit")
    comparisons = 0
    for seed in (7, 19):
        initial = [(x * x * seed + 3 * x + 11) % prime for x in range(128)]
        executions = {(): initial}
        for k in range(1, 7):
            for word in itertools.permutations(range(1, 7), k):
                actual = swap(gaussian(executions[word[:-1]], 0), word[-1])
                executions[word] = actual
                expected = initial
                for axis in (0, *word[:-1]):
                    expected = gaussian(expected, axis)
                for stage in word:
                    expected = swap(expected, stage)
                require(actual == expected, "direct Gaussian/permutation normal form")
                comparisons += 1
        require(executions[(1, 2)] != executions[(2, 1)], "direct order mutation")
    return comparisons


def compute():
    ports, code = load_inputs()
    require(len(ports) == len(code) == 112, "112 owner fixture")
    require(all(len(r) == 112 for r in code), "square code")
    require(len({p["q"] for p in ports}) == 112, "distinct port lines")
    normalizers = []
    for p in ports:
        rows, z = tuple(p["G_rows"]), p["Z_mask"]
        require(len(rows) == 9 and apply(rows, 1) == p["q"], "central-line image")
        require(all(((a & b).bit_count() & 1) == (i == j)
                    for i, a in enumerate(rows) for j, b in enumerate(rows)), "orthogonal normalizer")
        op = rows, row_product(z, rows)
        inv = inverse(op)
        require(compose(op, inv) == compose(inv, op) == identity(9), "two inverse orders")
        for d in range(512):
            require((apply(inv[0], d).bit_count() - d.bit_count()
                     - 2 * ((z & d).bit_count() & 1)) % 4 == 0, "Gaussian phase congruence")
        normalizers.append(op)

    swap = swap_blocks(0, 1, 2)
    local0 = [embed(k, 0) for k in normalizers]
    local1 = [embed(k, 1) for k in normalizers]
    global1 = [compose(swap, k) for k in local0]
    for i in range(112):
        require(local1[i] == compose(swap, compose(local0[i], swap)), "stage conjugation")
        require(apply(global1[i][0], 1) == apply(swap[0], ports[i]["q"]), "transported line")
        require(apply(global1[i][0], 1 << 9) != 1 << 9, "global escape moves spectator")

    edges, differing, global_equal, witness = 0, 0, 0, None
    for i, row in enumerate(code):
        require(row[i] == 0, "zero diagonal")
        for j, coefficient in enumerate(row):
            if not coefficient:
                continue
            require(code[j][i] == coefficient, "symmetric code")
            edges += 1
            r0 = compose(inverse(local0[i]), local0[j])
            r1 = compose(inverse(local1[i]), local1[j])
            require(r0[0] != r1[0], "stage-local common-code candidate unexpectedly survived")
            differing += 1
            require(compose(inverse(global1[i]), global1[j]) == r0, "global common-code equality")
            global_equal += 1
            if witness is None:
                x = next(1 << b for b in range(17) if apply(r0[0], 1 << b) != apply(r1[0], 1 << b))
                witness = {"owners": [i, j], "coefficient": str(coefficient), "input_label": x,
                           "anchor_output_label": apply(r0[0], x),
                           "fresh_output_label": apply(r1[0], x)}

    require(compose(inverse(local0[0]), local0[0]) ==
            compose(inverse(local1[0]), local1[0]), "equal-line positive control")
    require(local0[0] == compose(identity(17), local0[0]), "same-stage positive control")

    count = 0
    for k in range(1, 7):
        for word in itertools.permutations(range(1, 7), k):
            perm, exponents = word_state(word, 7)
            require({i for i, e in enumerate(exponents) if e} == {0, *word[:-1]}, "Gaussian support")
            require(all(e in (0, 1) for e in exponents), "distinct-stage exponent")
            require(8 * sum(e & 1 for e in exponents) == 8 * k, "rank after monomial removal")
            require(sorted(perm) == list(range(7)), "permutation bookkeeping")
            count += 1
    require(word_state((1, 2), 3) != word_state((2, 1), 3), "noncommuting stage control")
    require(8 * sum(e & 1 for e in word_state((1, 1, 1), 2)[1]) == 8, "repeated-stage rank control")
    # C_1=P C_0 P^-1 differs at every edge. Since [C_0,D_0 Q]=0,
    # this also rejects [C_0, E_1 Q]=0 for E_1=P D_0.
    require(edges == differing == global_equal == 5824, "complete nonzero block coverage")
    return {
        "status": "PASS_COMMON_CODE_MOVING_STAGES_NO_KAPPA",
        "ports": 112, "phase_congruences": 112 * 512,
        "nonzero_code_blocks": edges, "stage_local_binary_mismatches": differing,
        "global_common_code_exact_blocks": global_equal,
        "global_normalizers_moving_spectators": 112,
        "stage_local_witness": witness,
        "distinct_ordered_stage_words": count, "repeated_word_rank": 8,
        "independent_finite_field_vector_comparisons": direct_word_checks(),
        "transport_extra_main_permutations_per_full": 224,
        "transport_extra_anchor_axes": 8,
        "required_direct_controller_commutation": False,
        "scope": "Exact finite transcription checks of PROOF.md; no supplier admission or higher kappa."
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()
    result = compute()
    path = HERE / "RESULT.json"
    if args.write_result:
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        require(json.loads(path.read_text()) == result, "result receipt mismatch")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
