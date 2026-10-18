#!/usr/bin/env python3
"""Exhaust the dirty-boundary pair and explicit F2 gate schedules."""

from itertools import product


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def matrices(n):
    ones = (1 << n) - 1
    b = tuple(ones for _ in range(n))
    r = (1,) + (0,) * (n - 1)
    bp = tuple(x ^ y for x, y in zip(b, r))
    c = 0b11
    identity = tuple(1 << i for i in range(n))
    return b, r, bp, c, identity


def matvec(rows, x):
    result = 0
    for i, row in enumerate(rows):
        result |= ((row & x).bit_count() & 1) << i
    return result


def expected(n, x, u, z, y1, y2):
    b, _, bp, c, _ = matrices(n)
    xp = x ^ (c if u else 0)
    return (xp, u, z, y1 ^ matvec(b, x), y2 ^ matvec(bp, xp))


def paired(n, x, u, z, y1, y2, fault=None):
    b, r, bp, c, _ = matrices(n)

    # First complete readout, but retain the dirty connector for the pair.
    y1 ^= z
    z ^= matvec(b, x)
    y1 ^= z

    # Change the source and shift the connector map by the rank-one delta.
    x ^= c if u else 0
    if fault != "omit_patch":
        old_x = x ^ (c if u else 0)
        z ^= matvec(r, old_x if fault == "stale_patch" else x)

    # Second complete readout and exact restoration to the entry connector.
    y2 ^= z
    z ^= matvec(b if fault == "wrong_undo" else bp, x)
    y2 ^= z
    return (x, u, z, y1, y2)


def paired_inverse(n, x, u, z, y1, y2):
    """Undo paired() by reversing its eight self-inverse shears."""
    b, r, bp, c, _ = matrices(n)
    y2 ^= z
    z ^= matvec(bp, x)
    y2 ^= z
    z ^= matvec(r, x)
    x ^= c if u else 0
    y1 ^= z
    z ^= matvec(b, x)
    y1 ^= z
    return (x, u, z, y1, y2)


def restored_baseline(n, x, u, z, y1, y2):
    b, _, bp, c, _ = matrices(n)

    # First call: y1 += Bx and restore arbitrary connector z.
    y1 ^= z
    z ^= matvec(b, x)
    y1 ^= z
    z ^= matvec(b, x)

    x ^= c if u else 0

    # Second call: y2 += B'x and restore arbitrary connector z.
    y2 ^= z
    z ^= matvec(bp, x)
    y2 ^= z
    z ^= matvec(bp, x)
    return (x, u, z, y1, y2)


def parity(x):
    return x.bit_count() & 1


def factored_paired(n, x, u, z, y1, y2, t=0):
    """Use one clean parity bit and keep it live across the source mutation."""
    require(t == 0, "factored pair requires its declared clean scratch input")
    ones = (1 << n) - 1
    y1 ^= z
    t ^= parity(x)  # n scalar ADDs: t += x_j
    if t:
        z ^= ones     # n scalar ADDs: z_i += t
    y1 ^= z

    x ^= 0b11 if u else 0
    z ^= x & 1       # rank-one patch R x'

    y2 ^= z
    if t:
        z ^= ones     # B x' (parity unchanged by C)
    z ^= x & 1       # extra E_00 term in B' x'
    y2 ^= z
    t ^= parity(x)   # uncompute against changed source; parity is preserved
    return (x, u, z, y1, y2, t)


def factored_shared_scratch_baseline(n, x, u, z, y1, y2, t=0):
    """Close z after each call but retain common parity scratch across calls."""
    require(t == 0, "factored baseline requires its declared clean scratch input")
    ones = (1 << n) - 1

    y1 ^= z
    t ^= parity(x)
    if t:
        z ^= ones
    y1 ^= z
    if t:
        z ^= ones  # close the B connector, leave t live

    x ^= 0b11 if u else 0

    y2 ^= z
    if t:
        z ^= ones
    z ^= x & 1
    y2 ^= z
    if t:
        z ^= ones
    z ^= x & 1  # close the B' connector
    t ^= parity(x)
    return (x, u, z, y1, y2, t)


def factored_strict_baseline(n, x, u, z, y1, y2, t=0):
    """Close both z and t after each complete call."""
    require(t == 0, "factored baseline requires its declared clean scratch input")
    ones = (1 << n) - 1

    y1 ^= z
    t ^= parity(x)
    if t:
        z ^= ones
    y1 ^= z
    if t:
        z ^= ones
    t ^= parity(x)  # t=0 at first call boundary

    x ^= 0b11 if u else 0

    y2 ^= z
    t ^= parity(x)
    if t:
        z ^= ones
    z ^= x & 1
    y2 ^= z
    if t:
        z ^= ones
    z ^= x & 1
    t ^= parity(x)
    return (x, u, z, y1, y2, t)


def factored_inverse(n, x, u, z, y1, y2, t=0):
    """Reverse the factored pair, restoring the clean parity scratch."""
    require(t == 0, "factored inverse requires its declared clean scratch boundary")
    ones = (1 << n) - 1
    t ^= parity(x)
    y2 ^= z
    if t:
        z ^= ones
    z ^= x & 1
    y2 ^= z
    z ^= x & 1
    x ^= 0b11 if u else 0
    y1 ^= z
    if t:
        z ^= ones
    t ^= parity(x)
    y1 ^= z
    return (x, u, z, y1, y2, t)


def explicit_gates(n, schedule):
    """Return literal CNOTs as (source_bit, target_bit) index pairs."""
    x0 = 0
    u = n
    z0 = n + 1
    y10 = 2 * n + 1
    y20 = 3 * n + 1
    t = 4 * n + 1
    gates = []
    add = gates.append

    def readout(ybase):
        for i in range(n):
            add((z0 + i, ybase + i))

    def parity():
        for j in range(n):
            add((j, t))

    def b_update():
        for i in range(n):
            add((t, z0 + i))

    def bp_update():
        b_update()
        add((x0, z0))

    def source_change():
        add((u, x0))
        add((u, x0 + 1))

    if schedule == "paired":
        readout(y10)
        parity()
        b_update()
        readout(y10)
        source_change()
        add((x0, z0))
        readout(y20)
        bp_update()
        readout(y20)
        parity()
    elif schedule == "shared_scratch_baseline":
        readout(y10)
        parity()
        b_update()
        readout(y10)
        b_update()
        source_change()
        readout(y20)
        bp_update()
        readout(y20)
        bp_update()
        parity()
    elif schedule == "strict_baseline":
        readout(y10)
        parity()
        b_update()
        readout(y10)
        b_update()
        parity()
        source_change()
        readout(y20)
        parity()
        bp_update()
        readout(y20)
        bp_update()
        parity()
    else:
        raise ValueError(f"unknown schedule: {schedule}")
    return gates


def pack_state(n, x, u, z, y1, y2, t=0):
    return (x | (u << n) | (z << (n + 1)) | (y1 << (2 * n + 1))
            | (y2 << (3 * n + 1)) | (t << (4 * n + 1)))


def unpack_state(n, state):
    mask = (1 << n) - 1
    return (state & mask,
            (state >> n) & 1,
            (state >> (n + 1)) & mask,
            (state >> (2 * n + 1)) & mask,
            (state >> (3 * n + 1)) & mask,
            (state >> (4 * n + 1)) & 1)


def apply_gate_list(state, gates):
    for source, target in gates:
        state ^= ((state >> source) & 1) << target
    return state


def check_explicit_gate_schedules(n):
    schedules = {
        "paired": 8 * n + 4,
        "shared_scratch_baseline": 10 * n + 4,
        "strict_baseline": 12 * n + 4,
    }
    columns = 0
    for name, expected_cost in schedules.items():
        gates = explicit_gates(n, name)
        require(len(gates) == expected_cost,
                f"n={n}: {name} gate count {len(gates)} != {expected_cost}")
        for source, target in gates:
            require(source != target and 0 <= source <= 4 * n + 1
                    and 0 <= target <= 4 * n + 1,
                    f"n={n}: invalid gate in {name}: {(source,target)}")
        for column in range(4 * n + 1):  # x,u,z,y1,y2; t enters clean at zero
            x = (1 << column) if column < n else 0
            u = 1 if column == n else 0
            z = (1 << (column - n - 1)) if n + 1 <= column < 2 * n + 1 else 0
            y1 = (1 << (column - 2 * n - 1)) if 2 * n + 1 <= column < 3 * n + 1 else 0
            y2 = (1 << (column - 3 * n - 1)) if 3 * n + 1 <= column < 4 * n + 1 else 0
            start = pack_state(n, x, u, z, y1, y2, 0)
            want = pack_state(n, *expected(n, x, u, z, y1, y2), 0)
            got = apply_gate_list(start, gates)
            require(got == want, f"n={n}: {name} gate mismatch on basis column {column}")
            require(apply_gate_list(got, reversed(gates)) == start,
                    f"n={n}: {name} reverse gate word failed on column {column}")
            require(unpack_state(n, got)[-1] == 0,
                    f"n={n}: {name} did not restore clean scratch")
            columns += 1
    return columns


def counterexample(n, fault):
    limit = 1 << n
    for x, u, z, y1, y2 in product(range(limit), range(2), range(limit), range(limit), range(limit)):
        if paired(n, x, u, z, y1, y2, fault) != expected(n, x, u, z, y1, y2):
            return (x, u, z, y1, y2)
    return None


def check_general_transition():
    """All 2x2 B1,B2,C and dirty inputs for the general correction formula."""
    n = 2
    possible_rows = range(1 << n)
    all_maps = tuple(product(possible_rows, repeat=n))
    cases = 0
    for b1 in all_maps:
        for b2 in all_maps:
            r = tuple(a ^ b for a, b in zip(b1, b2))
            for c in range(1 << n):
                bc = matvec(b1, c)
                for x, u, z in product(range(1 << n), range(2), range(1 << n)):
                    xp = x ^ (c if u else 0)
                    target = z ^ matvec(b2, xp)
                    corrected = z ^ matvec(b1, x) ^ matvec(r, xp) ^ (bc if u else 0)
                    require(corrected == target,
                            f"general transition mismatch at {(b1,b2,c,x,u,z)}")
                    cases += 1
    require(cases == 32768, f"general transition census incomplete: {cases}")
    return cases


def check_general_adapter_control():
    """The B1 C u term is necessary when B1 C is nonzero."""
    b1 = (0b01, 0b10)  # I_2
    b2 = (0, 0)
    r = tuple(a ^ b for a, b in zip(b1, b2))
    c, x, u, z = 0b01, 0, 1, 0
    xp = x ^ c
    target = z ^ matvec(b2, xp)
    full_patch = z ^ matvec(b1, x) ^ matvec(r, xp) ^ matvec(b1, c)
    omitted_source_term = z ^ matvec(b1, x) ^ matvec(r, xp)
    require(full_patch == target, "general source-term control: full patch failed")
    require(omitted_source_term != target,
            "general source-term control: omitted B1 C u unexpectedly survived")
    return (b1, b2, c, x, u, z, target, omitted_source_term)


def check_even_source_update_family():
    """Exhaust small even C and unit rank-one map deltas for B=J_n."""
    cases = 0
    for n in range(2, 6):
        ones = (1 << n) - 1
        b = tuple(ones for _ in range(n))
        for c in range(1, 1 << n):
            if c.bit_count() & 1:
                continue
            require(matvec(b, c) == 0, f"n={n}: even C did not lie in ker(J)")
            for j in range(n):
                if not ((c >> j) & 1):
                    continue
                for i in range(n):
                    r = tuple((1 << j) if row == i else 0 for row in range(n))
                    bp = tuple(a ^ d for a, d in zip(b, r))
                    require(matvec(r, c) == (1 << i),
                            f"n={n}: unit delta did not map C to e_i")
                    for x, u, z in product(range(1 << n), range(2), range(1 << n)):
                        xp = x ^ (c if u else 0)
                        target = z ^ matvec(bp, xp)
                        open_after_first = z ^ matvec(b, x)
                        patched = open_after_first ^ matvec(r, xp)
                        require(patched == target,
                                f"even-C transition mismatch at {(n,c,i,j,x,u,z)}")
                        cases += 1
    require(cases == 444800, f"even-C family census incomplete: {cases}")
    return cases


def main():
    state_count = 0
    gate_columns = 0
    for n in range(2, 6):
        b, r, bp, c, identity = matrices(n)
        require(matvec(b, c) == 0, f"n={n}: B C != 0")
        require(matvec(r, c) == 1, f"n={n}: R C != e0")
        require(sum(row.bit_count() for row in b) == n * n, f"n={n}: wrong wt(B)")
        require(sum(row.bit_count() for row in bp) == n * n - 1, f"n={n}: wrong wt(B')")
        require(sum(row.bit_count() for row in r) == 1, f"n={n}: wrong wt(R)")
        require(sum(row.bit_count() for row in identity) == n, f"n={n}: wrong wt(I)")
        require(c.bit_count() == 2, f"n={n}: wrong wt(C)")

        baseline_cost = 2 * (n * n) + 2 * (n * n - 1) + 4 * n + 2
        paired_cost = n * n + (n * n - 1) + 1 + 4 * n + 2
        require(baseline_cost == 4 * n * n + 4 * n, f"n={n}: baseline invoice mismatch")
        require(paired_cost == 2 * n * n + 4 * n + 2, f"n={n}: paired invoice mismatch")
        require(baseline_cost - paired_cost == 2 * n * n - 2, f"n={n}: saving mismatch")
        shared_scratch_cost = 10 * n + 4
        factored_cost = 8 * n + 4
        strict_scratch_cost = 12 * n + 4
        require(shared_scratch_cost - factored_cost == 2 * n,
                f"n={n}: factored saving against stronger baseline mismatch")
        require(strict_scratch_cost - factored_cost == 4 * n,
                f"n={n}: factored saving against strict baseline mismatch")
        gate_columns += check_explicit_gate_schedules(n)

        limit = 1 << n
        seen = 0
        for x, u, z, y1, y2 in product(range(limit), range(2), range(limit), range(limit), range(limit)):
            want = expected(n, x, u, z, y1, y2)
            got = paired(n, x, u, z, y1, y2)
            baseline = restored_baseline(n, x, u, z, y1, y2)
            factored_want = want + (0,)
            factored = factored_paired(n, x, u, z, y1, y2)
            shared_scratch_baseline = factored_shared_scratch_baseline(n, x, u, z, y1, y2)
            strict_scratch_baseline = factored_strict_baseline(n, x, u, z, y1, y2)
            require(got == want, f"n={n}: paired mismatch at {(x,u,z,y1,y2)}")
            require(baseline == want, f"n={n}: baseline mismatch at {(x,u,z,y1,y2)}")
            require(paired_inverse(n, *got) == (x, u, z, y1, y2), f"n={n}: inverse mismatch")
            require(factored == factored_want,
                    f"n={n}: factored pair mismatch at {(x,u,z,y1,y2)}")
            require(shared_scratch_baseline == factored_want,
                    f"n={n}: shared-scratch baseline mismatch at {(x,u,z,y1,y2)}")
            require(strict_scratch_baseline == factored_want,
                    f"n={n}: strict baseline mismatch at {(x,u,z,y1,y2)}")
            require(factored_inverse(n, *factored) == (x, u, z, y1, y2, 0),
                    f"n={n}: factored inverse mismatch")
            seen += 1
        require(seen == 1 << (4 * n + 1), f"n={n}: incomplete state census")
        state_count += seen

    for fault in ("omit_patch", "stale_patch", "wrong_undo"):
        witness = counterexample(4, fault)
        require(witness is not None, f"negative control survived: {fault}")
        print(f"REJECT_{fault} witness={witness}")

    general_cases = check_general_transition()
    source_term_witness = check_general_adapter_control()
    even_c_cases = check_even_source_update_family()
    print(f"REJECT_omit_B1C_u witness={source_term_witness}")

    # Closed-form example at n=4, written out to guard accidental drift.
    require((10 * 4 + 4, 8 * 4 + 4, 12 * 4 + 4) == (44, 36, 52),
            "n=4 factored invoice mismatch")
    require((2 * 16 + 2 * 15 + 4 * 4 + 2,
             16 + 15 + 1 + 4 * 4 + 2) == (80, 50),
            "n=4 direct row-add invoice mismatch")
    print(
        "PASS_RANK_ONE_CONNECTOR_DELTA "
        f"dimensions=2..5 dirty_inputs_each={state_count} "
        f"explicit_gate_columns={gate_columns} "
        f"general_2x2_transitions={general_cases} "
        f"even_C_unit_delta_transitions={even_c_cases} "
        "n4_factored_strong_baseline=44+p_t paired=36+p_t saved=8 "
        "strict_baseline=52+p_t direct_row_add=80->50"
    )


if __name__ == "__main__":
    main()
