#!/usr/bin/env python3
"""Exact scalar controls for reducing the three tensor-stage exchange.

New scalar identities are not rank-saving networks: endpoint/frame obligations
are recorded separately in docs/research/ternary-depth.md.  Optional PR7 checks
load an explicitly supplied checkout without modifying it or writing bytecode.
Prepared with assistance from OpenAI Codex; not formal verification.
"""
from argparse import ArgumentParser
from itertools import product
from pathlib import Path
import json
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]


def eye(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def mul(a, b, p):
    return [[sum(x * y for x, y in zip(row, col)) % p
             for col in zip(*b)] for row in a]


def rank(a, p):
    a = [list(row) for row in a]
    if not a:
        return 0
    r = 0
    for col in range(len(a[0])):
        pivot = next((i for i in range(r, len(a)) if a[i][col] % p), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        inv = pow(a[r][col], -1, p)
        a[r] = [(x * inv) % p for x in a[r]]
        for i in range(len(a)):
            if i != r and a[i][col] % p:
                factor = a[i][col] % p
                a[i] = [(x - factor * y) % p for x, y in zip(a[i], a[r])]
        r += 1
        if r == len(a):
            break
    return r


def add_row(target, source, coefficient, p):
    for i, value in enumerate(source):
        target[i] = (target[i] + coefficient * value) % p


def structured_fixture(p):
    """JV=I with two independent dirty columns, over every tested prime."""
    v = [[1, 0], [0, 1], [0, 0], [0, 0]]
    j = [[1, 0, 1, 1], [0, 1, 1, 2 % p]]
    assert mul(j, v, p) == eye(2)
    return v, j


def operate(p, mode):
    vmap, jmap = structured_fixture(p)
    v, r, n = 2, 4, 8
    state = eye(n)

    def load(sign, difference):
        for a in range(r):
            for i in range(v):
                add_row(state[2 * v + a], state[i], sign * vmap[a][i], p)
                add_row(state[2 * v + a], state[v + i],
                        sign * (-1 if difference else 1) * vmap[a][i], p)

    def inject(sign, opposite):
        for i in range(v):
            for a in range(r):
                value = jmap[i][a]
                add_row(state[i], state[2 * v + a], sign * value, p)
                add_row(state[v + i], state[2 * v + a], -sign * value, p)

    if mode == "merged-final-stages":
        # I + [I;-I][I I], followed by a minus sign on each data bank.
        load(1, False)
        inject(1, True)
        load(-1, False)
        inject(-1, True)
        for row in state[:2 * v]:
            for k in range(n):
                row[k] = -row[k] % p
        expected = eye(n)
        for i in range(v):
            expected[i] = [0] * n
            expected[i][i] = 1
            expected[i][v + i] = -1 % p
            expected[v + i] = [0] * n
            expected[v + i][i] = 1
        return state == expected

    assert mode == "exchange-with-reflection"
    # B=[I,-I], C=[-I;I], BC=-2I: V,J,V,J swaps data.
    load(1, True)
    inject(-1, True)
    load(1, True)
    inject(-1, True)
    projection = mul(vmap, jmap, p)
    reflection = [[(int(i == k) - 2 * projection[i][k]) % p
                   for k in range(r)] for i in range(r)]
    assert mul(reflection, reflection, p) == eye(r)
    expected = eye(n)
    expected[:v], expected[v:2 * v] = eye(n)[v:2 * v], eye(n)[:v]
    assert state[:2 * v] == expected[:2 * v]
    assert state[2 * v:] == [[0] * (2 * v) + row for row in reflection]
    # This correction is scalar arithmetic on auxiliary roles; a proposed
    # network must actually bring every touched role to the common full frame.
    state[2 * v:] = mul(reflection, state[2 * v:], p)
    assert state == expected
    return dict(field=p, all_basis_inputs=n, exact_exchange=True,
                dirty_reflection_involution=True, scratch_restored=True,
                reflection_is_identity=reflection == eye(r))


def one_pass_and_basis_controls():
    p = 3
    v, a = structured_fixture(p)
    s = [[1, 0, 0, 0], [0, 1, 0, 0]]
    vs = mul(v, s, p)
    complement = [[(int(i == j) - vs[i][j]) % p for j in range(4)] for i in range(4)]
    noise = mul(a, complement, p)
    assert rank(noise, p) == 2
    # An arbitrary target-side coefficient D cannot remove the independent
    # noise block, and right multiplication by invertible early E preserves rank.
    for coefficients in product(range(p), repeat=4):
        d = [list(coefficients[:2]), list(coefficients[2:])]
        assert rank([d[i] + noise[i] for i in range(2)], p) == 2
    # Noise rank is NOT basis-invariant.  U fixes V and makes AU=S.
    u = eye(4)
    for i in range(2):
        for j in range(2, 4):
            u[i][j] = -a[i][j] % p
    assert mul(a, u, p) == s
    assert mul(u, v, p) == v
    assert mul(s, u, p) != s  # source extraction, unlike source addition, changes
    assert rank(mul(noise, u, p), p) == 2
    return dict(field=3, source_dimension=2, noise_rank=2,
                arbitrary_target_blocks_checked=81,
                basis_can_zero_decoder_noise=True,
                basis_fixes_additive_embedding=True,
                basis_changes_source_extraction=True,
                early_basis_does_not_fix_post_swap_noise=True)


def ternary_bitplane_rank(rows):
    """Exact elimination over F3; disjoint bitplanes encode coefficients 1,2."""
    pivots = {}
    for ones, twos in rows:
        while ones | twos:
            bit = (ones | twos) & -(ones | twos)
            if bit not in pivots:
                pivots[bit] = (ones, twos) if ones & bit else (twos, ones)
                break
            p1, p2 = pivots[bit]
            # Add -factor times the normalized pivot.
            b1, b2 = (p2, p1) if ones & bit else (p1, p2)
            a0, b0 = ~(ones | twos), ~(b1 | b2)
            ones, twos = ((a0 & b1) | (ones & b0) | (twos & b2),
                          (a0 & b2) | (twos & b0) | (ones & b1))
    return len(pivots)


def producer_noise_rank(c, code):
    """Pull each decoder row backwards through L, then remove source columns."""
    output_rows = [[] for _ in c.inputs]
    for output, target in c.side:
        output_rows[target].append((code["outputs"][output], -1))
    for output, common_pair in c.totals:
        for target, source_set in enumerate(c.inputs):
            if set(common_pair) <= set(source_set):
                output_rows[target].append((code["outputs"][output], 1))
    rows = []
    for target, output_row in enumerate(output_rows):
        coefficients = [0] * c.roles
        for slot, value in output_row:
            coefficients[slot] = (coefficients[slot] + value) % 3
        for _, ins, outs in reversed(code["gates"]):
            pivot = ins[0]
            coefficients[pivot] = (coefficients[pivot] + sum(coefficients[o] for o in outs[1:])) % 3
            for other in ins[1:]:
                coefficients[other] = (coefficients[other] + coefficients[pivot]) % 3
        for source, slot in code["sources"].items():
            assert coefficients[slot] == int(c.variables[source] - 1 == target)
            coefficients[slot] = 0
        ones = twos = 0
        for slot, value in enumerate(coefficients):
            if value == 1:
                ones |= 1 << slot
            elif value == 2:
                twos |= 1 << slot
        rows.append((ones, twos))
    return ternary_bitplane_rank(rows)


def private_output_controls(pr7_dir, ground_sizes=(8, 10)):
    sys.path[:0] = [str(pr7_dir / "scripts"), str(ROOT / "scripts")]
    from prime_field_checks import SmallProducer
    results = []
    for h in ground_sizes:
        c = SmallProducer(h)
        code = c.compile()
        created = {}
        last_use = {}
        for k, (_, ins, outs) in enumerate(code["gates"]):
            for slot in outs[1:]:
                created[slot] = k
            for slot in set(ins + outs):
                last_use[slot] = k
        source_slots = set(code["sources"].values())
        target_witness = {}
        for output, target in c.side:
            slot = code["outputs"][output]
            if slot in created and last_use[slot] == created[slot]:
                assert slot not in source_slots
                target_witness.setdefault(target, slot)
        assert len(set(target_witness.values())) == len(target_witness)
        # An initial basis vector at one such role is unchanged by L: no
        # gate touches it before its sole output += pivot use, and it is
        # never a source afterwards. The decoder column is therefore -e_T.
        if h == min(ground_sizes):
            for target, slot in target_witness.items():
                z = [0] * c.roles
                z[slot] = 1
                for _, ins, outs in code["gates"]:
                    for other in ins[1:]:
                        z[ins[0]] = (z[ins[0]] + z[other]) % 3
                    for other in outs[1:]:
                        z[other] = (z[other] + z[ins[0]]) % 3
                assert sum(value != 0 for value in z) == 1 and z[slot] == 1
        noise_rank = producer_noise_rank(c, code)
        assert noise_rank == len(c.inputs)
        results.append(dict(h=h, inputs=len(c.inputs), roles=c.roles,
                            private_noise_columns=len(target_witness),
                            noise_block_rank=noise_rank,
                            source_block_identity_checked=True,
                            basis_vectors_simulated=len(target_witness) if h == min(ground_sizes) else 0))
    return results


def certificate(pr7_dir=None):
    merged = {str(p): operate(p, "merged-final-stages") for p in (2, 3, 5, 7)}
    assert merged == {"2": False, "3": True, "5": False, "7": False}
    result = dict(status="SCALAR IDENTITIES AND SCOPED OBSTRUCTIONS; NO NEW RANK-SAVING NETWORK",
                  merged_two_stage_identity_by_field=merged,
                  direct_exchange=[operate(p, "exchange-with-reflection") for p in (2, 3, 5, 7)],
                  one_pass_and_basis=one_pass_and_basis_controls())
    if pr7_dir:
        result["pr7_private_output_controls"] = private_output_controls(pr7_dir)
    return result


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--pr7-dir", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = certificate(args.pr7_dir)
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(encoded)
        print("PASS ternary two-stage scalar identity, dirty exchange/reflection, and scoped one-pass controls; no rank-saving network claimed")
    else:
        print(encoded, end="")


if __name__ == "__main__":
    main()
