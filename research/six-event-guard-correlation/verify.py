"""Exact six-event full-guard product inequality over GL_m(F_2)."""

import json
import subprocess
import tempfile
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
SOURCE = PACKAGE / "spectrum.c"
K3 = {27: 1, 21: -6, 19: 6, 17: -6, 15: 16, 13: -18, 11: 9, 9: -2}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def subset_character(rows):
    width = len(rows)
    full = (1 << width) - 1
    total = 0
    for left in range(1 << width):
        folded = 0
        for index, row in enumerate(rows):
            if left >> index & 1:
                folded ^= row
        if folded & (full ^ left) == 0:
            total += 1 << (width - left.bit_count())
    return total


def literal_character(rows):
    width = len(rows)
    total = 0
    state_count = 3 ** width
    for code in range(state_count):
        states = []
        parity = 0
        for index in range(width):
            state = code % 3
            code //= 3
            states.append(state)
        right = 0
        for index, state in enumerate(states):
            if state == 2:
                right |= 1 << index
        for index, state in enumerate(states):
            if state == 1:
                parity += (rows[index] & right).bit_count()
        total += 1 if parity % 2 == 0 else -1
    return total


def rows_of(width, mask):
    rows = [0] * width
    bit = 0
    for tail in range(width):
        for head in range(width):
            if tail == head:
                continue
            if mask >> bit & 1:
                rows[tail] |= 1 << head
            bit += 1
    return rows


def signed_spectrum(width):
    spectrum = {}
    edge_count = width * (width - 1)
    for mask in range(1 << edge_count):
        value = subset_character(rows_of(width, mask))
        sign = -1 if mask.bit_count() % 2 else 1
        spectrum[value] = spectrum.get(value, 0) + sign
    return {value: coeff for value, coeff in spectrum.items() if coeff}


def compile_spectrum(directory):
    binary = Path(directory) / "spectrum"
    compiled = subprocess.run(
        ["gcc", "-O3", "-std=c11", "-o", str(binary), str(SOURCE)],
        check=False, capture_output=True, text=True)
    need(compiled.returncode == 0, "gcc failed: " + compiled.stderr[-500:])
    return binary


def run_spectrum(binary, width):
    ran = subprocess.run(
        [str(binary), str(width)],
        check=False, capture_output=True, text=True)
    need(ran.returncode == 0, "spectrum failed: " + ran.stderr[-500:])
    spectrum = {}
    for line in ran.stdout.splitlines():
        value, coeff = line.split()
        spectrum[int(value)] = int(coeff)
    return spectrum


def gl_product(dimension):
    order = 1 << (dimension + 1)
    numerator = (order - 1) ** 5
    denominator = 1
    for shift in range(1, 6):
        denominator *= order - (1 << shift)
    return numerator, denominator


def difference_polynomial(order):
    """(X-1)^5 - product_{j=1..5}(X-2^j), expanded once from its coefficients."""
    return (57 * order ** 4 - 1230 * order ** 3 + 9910 * order ** 2
            - 31739 * order + 32767)


def exact_numerator(spectrum, power):
    return sum(coeff * pow(value, power) for value, coeff in spectrum.items())


def edge_index(width):
    index = {}
    bit = 0
    for tail in range(width):
        for head in range(width):
            if tail == head:
                continue
            index[(tail, head)] = bit
            bit += 1
    return index


def combinations(width, count):
    chosen = []

    def walk(start, rest):
        if rest == 0:
            yield tuple(chosen)
            return
        for vertex in range(start, width):
            chosen.append(vertex)
            yield from walk(vertex + 1, rest - 1)
            chosen.pop()

    yield from walk(0, count)


def identify_leading(width):
    """Evaluate every single arc and every two-arrow star at this width."""
    index = edge_index(width)
    arc_value = 7 * 3 ** (width - 2)
    star_value = 19 * 3 ** (width - 3)
    for edge, bit in index.items():
        mask = 1 << bit
        rows = rows_of(width, mask)
        need(literal_character(rows) == subset_character(rows) == arc_value,
             "single-arc character moved")
        need(mask.bit_count() % 2 == 1, "single arc is not odd weight")
    stars = set()
    for triple in combinations(width, 3):
        first, second, third = triple
        patterns = (
            ((first, second), (first, third)),
            ((second, first), (third, first)),
            ((second, first), (second, third)),
            ((first, second), (third, second)),
            ((third, first), (third, second)),
            ((first, third), (second, third)),
        )
        for pattern in patterns:
            mask = 0
            for edge in pattern:
                mask |= 1 << index[edge]
            rows = rows_of(width, mask)
            need(literal_character(rows) == subset_character(rows) == star_value,
                 "two-arrow star character moved")
            need(mask.bit_count() == 2, "two-arrow star does not have weight 2")
            stars.add(mask)
    need(len(index) == width * (width - 1), "arc count")
    need(len(stars) == width * (width - 1) * (width - 2), "star count")


def controls(binary):
    for width in (3, 4):
        edge_count = width * (width - 1)
        for mask in range(1 << edge_count):
            rows = rows_of(width, mask)
            need(literal_character(rows) == subset_character(rows),
                 "three-state sum disagrees with the subset form")
    python_three = signed_spectrum(3)
    need(python_three == K3, "k=3 subset spectrum is not the published law")
    c_three = run_spectrum(binary, 3)
    c_four = run_spectrum(binary, 4)
    c_five = run_spectrum(binary, 5)
    need(c_three == K3, "C spectrum missed the k=3 law")
    need(signed_spectrum(4) == c_four, "C spectrum missed the k=4 recount")
    need(c_five[243] == 1 and c_five[189] == -20 and c_five[171] == 60,
         "k=5 leading coefficients moved")
    need(c_four[81] == 1 and c_four[63] == -12, "k=4 empty or single-edge multiplicity moved")
    identify_leading(6)
    return c_five


def tail_bound(absolute_rest):
    """Integer tail for every n >= 129.

    At the threshold the remainder exceeds 26 single-arc modes and fits under
    27, leaving 3 modes to absorb the degree-four GL gap.
    """
    threshold = 129
    cover = 27
    deficit = 3
    need(cover + deficit == 30, "arc modes were not split")
    remainder = (120 * pow(513, threshold)
                 + absolute_rest * pow(495, threshold))
    base_gap = cover * pow(567, threshold) - remainder
    need(base_gap > 0, "remainder did not fall below 27 single-edge modes")
    need((cover - 1) * pow(567, threshold) < remainder,
         "26 modes already covered the remainder; the split moved")
    step_gap = (cover * pow(567, threshold + 1) - 120 * pow(513, threshold + 1)
                - absolute_rest * pow(495, threshold + 1))
    need(step_gap > 567 * base_gap, "tail recurrence failed one step")
    order = 1 << (threshold + 1)
    positive = deficit * pow(567, threshold) * pow(order - 1, 5)
    negative = 59 * pow(order, 4) * pow(729, threshold)
    need(positive > negative, "finite-GL factor was not absorbed at n=129")
    need(pow(729, threshold) > deficit * pow(567, threshold),
         "3-mode upper bound is negative")
    need(9910 * 128 ** 2 <= 128 ** 4 and 32767 <= 128 ** 4,
         "degree-four majorization failed at X=128")
    sample = difference_polynomial(order)
    expanded = ((1 << (threshold + 1)) - 1) ** 5
    product = 1
    for shift in range(1, 6):
        product *= order - (1 << shift)
    need(expanded - product == sample, "GL polynomial identity failed")
    need(sample <= 59 * order ** 4, "GL difference exceeded 59 X^4")


def illustrated_ratio(spectrum, power):
    numerator, denominator = gl_product(power)
    return exact_numerator(spectrum, power) * numerator / (pow(729, power) * denominator)


def main():
    with tempfile.TemporaryDirectory() as directory:
        binary = compile_spectrum(directory)
        controls(binary)
        spectrum = run_spectrum(binary, 6)
    need(spectrum[729] == 1, "empty character multiplicity")
    need(spectrum[567] == -30, "single-edge multiplicity")
    need(spectrum[513] == 120, "two-star multiplicity")
    need(max(spectrum) == 729, "character above the empty matrix")
    allowed = {729, 567, 513}
    unexpected = [value for value in spectrum if value > 495 and value not in allowed]
    need(not unexpected, "character between the separated levels: " + str(unexpected[:6]))
    below = [value for value in spectrum if value < 513]
    need(below and max(below) == 495, "unexpected character above 495 and below 513")
    absolute_rest = sum(abs(spectrum[value]) for value in below)
    need(sum(abs(coeff) for coeff in spectrum.values()) == 1 << 30,
         "signed spectrum is not a partition of the 2^30 masks")
    for power in range(0, 6):
        need(exact_numerator(spectrum, power) == 0, "walk count before the threshold")
    count = exact_numerator(spectrum, 6) >> 30
    need(count == 23040, "m=7 header count changed")
    for power in range(6, 130):
        numerator, denominator = gl_product(power)
        slack = denominator * pow(729, power) - exact_numerator(spectrum, power) * numerator
        need(slack > 0, "ratio reached 1 at n=" + str(power))
    shifted = dict(spectrum)
    shifted[567] = spectrum[567] + 1
    need(exact_numerator(shifted, 5) != 0, "n=5 vanishing ignored a multiplicity change")
    tail_bound(absolute_rest)
    samples = {str(power): illustrated_ratio(spectrum, power) for power in (6, 7, 12, 20, 40)}
    print(json.dumps({
        "status": "PASS_SIX_EVENT_GUARD_CORRELATION",
        "terms": len(spectrum),
        "m7_headers": count,
        "remainder_mass": absolute_rest,
        "exact_through_n": 129,
        "analytic_from_n": 129,
        "sample_ratios": samples,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
