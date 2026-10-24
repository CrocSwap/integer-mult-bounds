"""Check a complete two-round encoded DIF word over Gaussian integers."""

from collections import Counter
from hashlib import sha256
from pathlib import Path
import json
import subprocess


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
LANES = HERE.parent
REVISION = "3ae9a6f3ac74ded022ab3b4872a7357a621af6fb"
SOURCE_PINS = {
    "upstream/build/sections/05-layers.tex": "20cfc8d12099d4e4ed9e3e7eeb6162edd9b6e0e076f24693364cd24377252594",
    "upstream/build/sections/06-transforms.tex": "924316e4bc905066281d8f9e8746a49d8829aeb393688608deb1e61c3c87853c",
}
R_PIN = "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3"
ZERO = (0, 0)
UNITS = ((1, 0), (0, 1), (-1, 0), (0, -1))
HIGH, LOW = (1, 3, 5), (0, 2, 4)
DIMENSION = 256


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def plus(a, b):
    return a[0] + b[0], a[1] + b[1]


def times(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def conjugate(a):
    return a[0], -a[1]


def square_norm(a):
    return a[0] * a[0] + a[1] * a[1]


def put(row, index, coefficient):
    value = plus(row.get(index, ZERO), coefficient)
    if value != ZERO:
        row[index] = value
    else:
        row.pop(index, None)


def butterfly(column, axes):
    result = {}
    mask = sum(1 << axis for axis in axes)
    for address, coefficient in column.items():
        current = sum(((address >> axis) & 1) << j for j, axis in enumerate(axes))
        for output in range(8):
            target = (address & ~mask) | sum(((output >> j) & 1) << axis for j, axis in enumerate(axes))
            sign = -1 if (current & output).bit_count() % 2 else 1
            put(result, target, (sign * coefficient[0], sign * coefficient[1]))
    return result


def output_code(column, axes):
    # This is twice S*T*S^-1. T sends z=0 through Q^-1 and z=1 through Q.
    result = {}
    mask = sum(1 << axis for axis in axes)
    for address, coefficient in column.items():
        inverse = ((address >> 6) & 1) == 0
        diagonal = (1, -1) if inverse else (1, 1)
        translated = (1, 1) if inverse else (1, -1)
        target = address ^ 64
        put(result, target, times(diagonal, coefficient))
        target ^= mask
        phase = UNITS[((target & mask).bit_count() - (address & mask).bit_count()) % 4]
        put(result, target, times(times(translated, phase), coefficient))
    return result


def twiddle(column):
    result = {}
    for address, coefficient in column.items():
        power = -sum(((address >> high) & 1) * ((address >> low) & 1)
                     for high, low in zip(HIGH, LOW))
        # The polynomial root theta is independent of the Gaussian unit i.
        # On the two coefficient positions, theta maps (a,b) to (-b,a).
        shifted = ((address >> 7) & 1) + power
        target = (address & 127) | ((shifted % 2) << 7)
        sign = -1 if (shifted // 2) % 2 else 1
        put(result, target, (sign * coefficient[0], sign * coefficient[1]))
    return result


def word(coded, use_twiddle=True):
    rows = [{} for _ in range(DIMENSION)]
    for source in range(DIMENSION):
        column = butterfly({source: (1, 0)}, HIGH)
        if coded:
            column = output_code(column, HIGH)
        if use_twiddle:
            column = twiddle(column)
        column = butterfly(column, LOW)
        if coded:
            column = output_code(column, LOW)
        for target, coefficient in column.items():
            rows[target][source] = coefficient
    # Two rounds give denominator 8 for raw H, and 32 with the two Q maps.
    return rows


def row_product(first, second):
    answer = []
    for right in second:
        value = ZERO
        for column, a in first.items():
            if column in right:
                value = plus(value, times(a, conjugate(right[column])))
        answer.append(value)
    return answer


def parity_class(address):
    return ((sum((address >> bit) & 1 for bit in HIGH) % 2),
            (sum((address >> bit) & 1 for bit in LOW) % 2), (address >> 6) & 1)


def main():
    for path, pin in SOURCE_PINS.items():
        raw = subprocess.check_output(["git", "-C", str(ROOT / "worktrees/k5-centre-sharing"),
                                       "show", REVISION + ":" + path])
        need(sha256(raw).hexdigest() == pin, "Physical source pin")
    raw = (LANES / "circuit-interface/INTERFACE.json").read_bytes()
    need(sha256(raw).hexdigest() == R_PIN, "Actual port pin")
    ports = json.loads(raw)["ports"]
    need(ports[0] == 11 and set(q.bit_count() for q in ports) == {3, 7}, "Actual odd port types")
    # 2*H0=(1-i) S C S holds entry by entry for the source C and S conventions.
    C = (((1, 1), (1, -1)), ((1, -1), (1, 1)))
    for target in range(2):
        for source in range(2):
            rhs = times((1, -1), times(UNITS[target], times(C[target][source], UNITS[source])))
            need(rhs == ((-2 if target and source else 2), 0), "H/S/C conversion side")

    ordinary, encoded = word(False), word(True)
    for target, row in enumerate(ordinary):
        expected = {}
        for source in range(DIMENSION):
            if ((source >> 6) & 1) != ((target >> 6) & 1):
                continue
            power = 0
            for low, high in zip(LOW, HIGH):
                x = ((source >> low) & 1) + 2 * ((source >> high) & 1)
                reversed_y = ((target >> high) & 1) + 2 * ((target >> low) & 1)
                power -= x * reversed_y
            shifted = ((source >> 7) & 1) + power
            if shifted % 2 == ((target >> 7) & 1):
                expected[source] = (-1 if (shifted // 2) % 2 else 1, 0)
        need(row == expected, "The ordinary word is not the unitary rescaling of the source DIF transform")
    for rows, denominator in ((ordinary, 8), (encoded, 32)):
        for index, row in enumerate(rows):
            gram = row_product(row, rows)
            need(gram == [(denominator * denominator, 0) if j == index else ZERO
                          for j in range(DIMENSION)], "Exact unitary normalization")
    encoded_classes = Counter(len({parity_class(source) for source in row}) for row in encoded)
    need(encoded_classes == {1: 256}, "The complete code mixes a parity class")
    # U_raw U_code^* is the terminal decoder, with common denominator 8*32.
    histograms, first_row = Counter(), None
    for index, row in enumerate(ordinary):
        decoder = row_product(row, encoded)
        histogram = Counter(square_norm(value) for value in decoder if value != ZERO)
        need(sum(map(square_norm, decoder)) == 256 ** 2, "Decoder row norm")
        need(histogram == {16384: 2, 4096: 8}, "Decoder support or magnitude pattern")
        need(all(value[1] == 0 for value in decoder), "The physical coefficient decoder has an imaginary part")
        classes = {parity_class(j)[:2] for j, value in enumerate(decoder) if value != ZERO}
        need(len(classes) == 4, "A required parity sector is missing")
        histograms[str(sorted(histogram.items()))] += 1
        if index == 0:
            first_row = [[j, value[0], value[1]] for j, value in enumerate(decoder) if value != ZERO]
    raw_without, encoded_without = word(False, False), word(True, False)
    for row in raw_without:
        control = row_product(row, encoded_without)
        need(Counter(square_norm(value) for value in control if value != ZERO) == {16384: 4},
             "The no-twiddle control does not reduce to four uniform entries")
    receipt = {
        "status": "PASS_EXACT_ACCUMULATED_TWIDDLE_CODE",
        "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "source_revision": REVISION, "source_pins": SOURCE_PINS, "actual_port_pin": R_PIN,
        "actual_port": 11, "active_source_coordinates": [0, 1, 3],
        "axes": 3, "bits_per_axis": 2, "arbitrary_replica_slices": 2,
        "polynomial_coefficient_positions": 2, "formal_Gaussian_columns": 256,
        "real_input_columns": 512,
        "arithmetic": "Exact Gaussian integer pairs; theta is a separate signed permutation on polynomial coefficients; unitary-rescaled word denominators 8,32 and decoder denominator 256",
        "source_H0_normalization": "Each literal H0 is H/2. Both complete source words equal one eighth of the unitary-rescaled word used here. This common factor cancels in U_raw U_code^-1.",
        "ordinary_DIF_entries_checked": 65536,
        "unitary_Gram_entries_checked": 131072,
        "encoded_parity_class_counts": dict(encoded_classes),
        "decoder_rows_checked": 256,
        "decoder_nonzero_entries_per_row": 10,
        "decoder_squared_magnitude_counts": {"1/4": 2, "1/16": 8},
        "decoder_first_row_numerators_over_256": first_row,
        "no_twiddle_control": "All 256 decoder rows have four entries of squared magnitude 1/4",
        "scope": "Stable port q, common exact T endpoint, current-bit H0 conversion, and the actual two-round length-four DIF twiddle. Other six local axes factor as the identity in the residual. This rejects one native C_r between monomial maps for this terminal residual. It does not bound arbitrary native-child words, changed layouts, changed endpoints, or a general multiplication algorithm.",
    }
    (HERE / "ACCUMULATED-TWIDDLE-CODE.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"])
    print("256 coefficient decoder rows: 10 nonzero entries each; the no-twiddle control has 4.")


if __name__ == "__main__":
    main()
