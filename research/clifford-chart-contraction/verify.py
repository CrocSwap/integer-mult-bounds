"""Exact tests for the compact width-13 identity-row consumer; Apache-2.0."""
import argparse
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path
from random import Random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cell_tape import MASKS, SHIFTS, SIGNATURE, Tape, evaluate, phase_mask_symbols
from contract import Q, Spectrum, apply, contract, one_cell, parity, read_plan
from raw_row import RAW_DENOMINATOR, coefficient_numerator, matrix_addresses, raw_plan


def require(ok, message):
    if not ok:
        raise ValueError(message)


def direct_spectrum(n, phase, w):
    counts = [0] * 4
    for x in range(1 << n):
        counts[(Q.value(phase, x) + 2 * parity(w & x)) % 4] += 1
    return counts[0] - counts[2], counts[1] - counts[3]


def spectrum_tests():
    cases = 0
    for n in range(4):
        pair_masks = [(1 << i) | (1 << j) for i, j in combinations(range(n), 2)]
        for linear in product(range(4), repeat=n):
            for edges in range(1 << len(pair_masks)):
                phase = {1 << i: a for i, a in enumerate(linear) if a}
                phase.update({term: 2 for j, term in enumerate(pair_masks) if edges >> j & 1})
                spectrum = Spectrum(n, phase)
                for w in range(1 << n):
                    angle = spectrum.rotation(w)
                    value = (0, 0) if angle is None else Q.multiply_i(spectrum.value, angle)
                    require(value == direct_spectrum(n, phase, w), "Fourier sign or radical")
                    cases += 1
    return cases


def raw_address(shifts, point):
    r, c = matrix_addresses(shifts, point)
    return (r << 52) | c


def literal(state, selected=None):
    _, origin, cols, terms, a, b, den = state
    total = [0, 0]
    for x in range(1 << len(cols)):
        address = origin ^ apply(cols, x)
        row, col = divmod(address, 1 << 52)
        if selected is not None and address not in selected:
            continue
        weight = coefficient_numerator(row, col)
        unit = Q.multiply_i((a, b), Q.value(dict(terms), x))
        for j in range(2):
            total[j] += weight * unit[j]
    return tuple(Fraction(z, RAW_DENOMINATOR << den) for z in total)


def small_circuits():
    rng = Random(7800)
    plan = raw_plan()
    count = nonzero = 0
    for ix, (shifts, bucket) in enumerate(plan.items()):
        sig = next(i for i, w in enumerate(bucket.numerators) if w)
        first = raw_address(shifts, bucket.point_at(sig, 0))
        varied = [raw_address(shifts, bucket.point_at(sig, 1 << j)) ^ first for j in range(4)]
        other = next((sig ^ (1 << j) for j in range(len(bucket.masks))), sig)
        if other != sig:
            varied.append(raw_address(shifts, bucket.point_at(other, 0)) ^ first)
        varied.extend([1, 1 << 38])  # change singleton XOR and a Bell shift
        circuit = [('C', d, rng.choice((-1, 1))) for d in varied]
        circuit.append(('phase', ix))
        # Apply a real quadratic coupling and arbitrary powers of i in raw coordinates.
        rows = [1 << j for j in range(104)]
        rows[32] ^= 1 << 65
        rows[65] ^= 1 << 32
        circuit.append(('D', rows, [rng.choice((1, 3)) for _ in rows]))
        state = Q.signature(104, circuit, initial=first)
        actual, _ = contract(state)
        require(actual == literal(state), "Small-support literal full contraction")
        valid = {raw_address(shifts, bucket.point_at(sig, j)) for j in range(16)}
        partial, _ = one_cell(state, shifts, bucket.masks, sig, bucket.numerators[sig])
        # Get the expected cell independently by filtering raw coordinates, including
        # cases in which a changed shift happens to remain in another active bucket.
        require(partial == literal(state, valid), "Single active cell")
        count += 1
        nonzero += actual != (0, 0)
    require(nonzero > 0, "Small fixtures must detect genuine outputs")
    return count, nonzero


def bell_column(extra=()):
    # Prepare the 52 equality pairs and cancel the translation roots' local phases.
    roots = [('C', (1 << j) | (1 << (j + 52)), 1) for j in range(52)]
    rows = [1 << j if j < 52 else 0 for j in range(104)]
    circuit = roots + [('D', rows, [1] * 52 + [0] * 52), ('phase', 2), *extra]
    return Q.signature(104, circuit)


def full_columns():
    shift = sum(1 << (52 + 4*j) for j in range(13))
    cz = [0] * 104
    for j in range(13):
        a = 52 + 4*j
        cz[a] |= 1 << (a+1)
        cz[a+1] |= 1 << a
    observations = [
        (bell_column(), (1, 0)),
        (bell_column([('phase', 1)]), (0, 1)),
        (bell_column([('X', shift)]), (0, 0)),
        (bell_column([('D', cz, [0]*104)]), (0, 0)),
    ]
    counts = []
    for state, expected in observations:
        result, stats = contract(state)
        require(result == expected, "Literal normalized Clifford tensor column")
        counts.append(stats)
    return counts


def coupled_state(mask=0):
    # The address has 13 nibbles on each side. Couple corresponding second
    # nibbles in the six Bell pairs; the remaining singleton has no coupling.
    rows = [1 << j for j in range(104)]
    for pair in range(6):
        for bit in range(4):
            j = 4*(11-2*pair)+bit
            rows[j] |= 1 << (j+52)
            rows[j+52] |= 1 << j
    return Q.signature(104, [('C', 1 << j, 1) for j in range(104)] +
                       [('D', rows, [1+2*((mask >> j) & 1) for j in range(104)])])


def independent_coupled():
    # For frequency nibbles a,b the two 4-bit free words r,s have sum
    # of (-1)^(r.s+a.r+b.s) equal to 16*(-1)^(a.b). The singleton
    # contributes 16 or zero according to its four frequency bits.
    total = 0
    for terms in read_plan().values():
        for freq, weight in terms:
            if freq >> 48:
                continue
            left, right = (freq & ((1<<24)-1)), (freq >> 24) & ((1<<24)-1)
            total += weight * (-1)**parity(left & right)
    return Fraction(total * 16**7, RAW_DENOMINATOR << 52)


def tape_tests():
    bucket = raw_plan()[SHIFTS]
    weight = bucket.numerators[SIGNATURE]
    require(bucket.masks == MASKS and weight == 128, "Fixed cell must match the raw compiler")
    rng = Random(104)
    samples = [0, *[1 << j for j in range(104)], *(rng.getrandbits(104) for _ in range(32))]
    outputs = set()
    for mask in samples:
        symbols = phase_mask_symbols(mask)
        tape = Tape(symbols)
        received = evaluate(tape)
        if mask == 0:
            require(received == Fraction(1, 1 << 31), "Unmodulated exact cell")
        require((tape.reads, tape.moves, tape.position, tape.symbols) == (104, 208, 0, symbols),
                "One complete forward read and a restored input head")
        # Compare with the general chart algorithm on every phase mask sampled.
        got, _ = one_cell(coupled_state(mask), SHIFTS, MASKS, SIGNATURE, weight)
        require(got == (received, 0), "Tape consumer and the general chart contraction disagree")
        outputs.add(received)
    require(len(outputs) >= 3, "Cell controls need both signs and zero")
    return len(samples)


def main():
    import json
    request = json.loads((Path(__file__).parent / "INPUT.json").read_text())
    example = Q.signature(104, request["circuit"], initial=request["initial"])
    require(contract(example)[0] == (Fraction(-1, 32), 0), "Published circuit example")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tape", action="store_true", help="Run the independent input-tape checks")
    args = parser.parse_args()
    if args.tape:
        print(f"PASS_ACTIVE_CELL_TAPE masks={tape_tests()} reads=104 moves=208 "
              "restored_position=0 fixed_lookup_bytes=401")
        return
    cases = spectrum_tests()
    small, nonzero = small_circuits()
    stats = full_columns()
    tapes = tape_tests()
    state = coupled_state()
    require(len(state[2]) == 104, "Full-support fixture")
    # Swapping register 2 with the singleton exchanges these two inputs.
    first = (1 << 44) | (1 << 96)
    second = 1 | (1 << 52)
    require(Q.amplitude(state, first) == ((-1, 0), 52) and
            Q.amplitude(state, second) == ((1, 0), 52), "Off-image register-swap witness")
    coupled, counts = contract(state)
    analytic = independent_coupled()
    require(coupled == (analytic, 0) and analytic != 0, "104-bit Fourier pair factorization")
    require(counts['buckets'] == 22 and counts['gauss'] == 1 and counts['terms'] == 4265,
            "All buckets must share a single Gauss sum")
    print(f"PASS_CHART_CONTRACTION Fourier_values={cases} small_circuits={small} "
          f"small_nonzero={nonzero} normalized_columns={len(stats)} "
          f"tape_masks={tapes} tape_reads=104 tape_moves=208 full_support=2^104 output={analytic} counts={counts}")


if __name__ == '__main__':
    main()
