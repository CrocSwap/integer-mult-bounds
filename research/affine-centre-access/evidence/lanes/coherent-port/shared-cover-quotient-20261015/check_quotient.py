#!/usr/bin/env python3
"""Check the actual cover quotient and its native phase conditions."""

from collections import Counter
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import json
import tarfile


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
REPO = LANES.parents[2]
ARCHIVE = REPO / "worktrees/k5-persistent-cleanup/research/community-frontier1094-audit/selected-replay.tar.gz"
PHASE_MEMBER = "candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json"
PHASE_PIN = "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa"
PINS = {
    "circuit-interface/INTERFACE.json":
        "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3",
    "source-domain/augmented-mode-lift/LIFT.json":
        "fe0feecc0f0924d78326f82e961fcb2eae44bfcb8cea34b8724b128cff98a927",
    "portable-source-codes/upstream-echo-20261015/COVER-QUOTIENT.md":
        "741bbd322ee89a0864e238db02ca8a44c26d2ab856e7c83f7b6bd36a03008a23",
}


def need(test, message):
    if not test:
        raise RuntimeError(message)


def bits(value):
    while value:
        bit = value & -value
        yield bit.bit_length() - 1
        value ^= bit


def apply(columns, value):
    result = 0
    for j in bits(value):
        result ^= columns[j]
    return result


def compose(a, b):
    return tuple(apply(a, v) for v in b)


def rank(columns):
    rows = {}
    for value in columns:
        while value:
            j = value.bit_length() - 1
            if j in rows:
                value ^= rows[j]
            else:
                rows[j] = value
                break
    return len(rows)


def determinant(matrix):
    rows = [list(map(Fraction, row)) for row in matrix]
    result = Fraction(1)
    for i in range(len(rows)):
        pivot = next((j for j in range(i, len(rows)) if rows[j][i]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != i:
            rows[i], rows[pivot] = rows[pivot], rows[i]
            result = -result
        value = rows[i][i]
        result *= value
        rows[i] = [x / value for x in rows[i]]
        for j in range(i + 1, len(rows)):
            value = rows[j][i]
            rows[j] = [x - value * y for x, y in zip(rows[j], rows[i])]
    return result


def port_basis(q):
    zero = next(j for j in range(9) if not (q >> j) & 1)
    even = q ^ (1 << zero)
    order = list(range(9))
    order[0], order[zero] = order[zero], order[0]
    return tuple((1 << j) ^ (even if (even >> j) & 1 else 0) for j in order)


def rho(q, stage):
    identity = tuple(1 << j for j in range(73))
    if stage == 0:
        return identity
    basis = port_basis(q)
    swaps = tuple(zip(basis[1:], identity[8 * stage + 1:8 * stage + 9]))
    columns = []
    for value in identity:
        result = value
        for a, b in swaps:
            if ((value & a).bit_count() ^ (value & b).bit_count()) & 1:
                result ^= a ^ b
        columns.append(result)
    return tuple(columns)


def plus(a, b):
    """Add two vectors over Z/4, stored as two binary masks."""
    return a[0] ^ b[0], a[1] ^ b[1] ^ (a[0] & b[0])


def minus(a):
    return a[0], a[1] ^ a[0]


def times(c, a):
    return (0, 0) if c == 0 else a if c == 1 else (0, a[0]) if c == 2 else minus(a)


def row_basis(rows):
    """Use unit pivots, then binary pivots on the remaining even rows."""
    work = list(rows)
    result = []
    while True:
        index = next((i for i, row in enumerate(work) if row[0]), None)
        if index is None:
            break
        row = work.pop(index)
        pivot = row[0] & -row[0]
        if row[1] & pivot:
            row = minus(row)
        reduced = []
        for other in work:
            coefficient = int(bool(other[0] & pivot)) + 2 * int(bool(other[1] & pivot))
            value = plus(other, times((-coefficient) % 4, row)) if coefficient else other
            if value != (0, 0):
                reduced.append(value)
        result.append(row)
        work = reduced
    units = len(result)
    even = {}
    for low, high in work:
        need(low == 0, "The second reduction must contain only even rows")
        while high:
            pivot = high & -high
            if pivot in even:
                high ^= even[pivot]
            else:
                even[pivot] = high
                break
    result.extend((0, value) for value in even.values())
    return result, units, len(even)


class Signatures:
    def __init__(self, dimension, generators):
        self.dimension = dimension
        self.pairs = tuple((i, j) for i in range(dimension) for j in range(i + 1, dimension))
        self.size = dimension + len(self.pairs)
        self.constraints = [(0, 1 << j) for j in range(dimension, self.size)]
        self.actions = []
        for g in generators:
            rows = [self.feature(v) for v in g]
            rows.extend(plus(plus(self.feature(g[i] ^ g[j]), minus(self.feature(g[i]))),
                             minus(self.feature(g[j]))) for i, j in self.pairs)
            self.actions.append(rows)

    def feature(self, value):
        low = value
        for k, (i, j) in enumerate(self.pairs, self.dimension):
            if value >> i & 1 and value >> j & 1:
                low |= 1 << k
        return low, 0

    def transform(self, row, action):
        result = (0, 0)
        for i in bits(row[0]):
            result = plus(result, action[i])
        for i in bits(row[1]):
            result = result[0], result[1] ^ action[i][0]
        return result

    def close_frames(self, dimensions):
        rows = list(self.constraints)
        for dimension in dimensions:
            form = ((1 << dimension) - 1, 0)
            rows.extend(plus(self.transform(form, a), minus(form)) for a in self.actions)
        stages = []
        for iteration in range(2 * self.size + 1):
            basis, units, evens = row_basis(rows)
            stages.append(dict(iteration=iteration, unit_rows=units, even_rows=evens,
                               solution_log2=2 * self.size - 2 * units - evens))
            rows = basis + [self.transform(r, a) for a in self.actions for r in basis]
            next_basis, next_units, next_evens = row_basis(rows)
            if (next_units, next_evens) == (units, evens):
                return basis, stages
            rows = next_basis
        raise RuntimeError("The finite module closure did not stop")


def dot4(row, column):
    return ((row[0] & column[0]).bit_count()
            + 2 * (row[0] & column[1]).bit_count()
            + 2 * (row[1] & column[0]).bit_count()) % 4


def odd_constant(signature, d, b):
    n = signature.dimension
    low = (1 << n) - 1 if d & 1 else 0
    high = (1 << n) - 1 if d & 2 else 0
    for k, (i, j) in enumerate(signature.pairs, n):
        if (d + (b >> i) + (b >> j)) & 1:
            high |= 1 << k
    return low, high


def signature_value(columns, value):
    return sum((x & value).bit_count() & 1 for x in columns) % 4


def alternating_count(dimension, half_rank):
    numerator = 1
    for j in range(2 * half_rank):
        numerator *= (1 << dimension) - (1 << j)
    denominator = 1 << (half_rank * half_rank)
    for j in range(1, half_rank + 1):
        denominator *= (1 << (2 * j)) - 1
    need(numerator % denominator == 0, "The alternating-matrix count must be integral")
    return numerator // denominator


def boolean_spectrum(dimension):
    result = Counter()
    for r in range(dimension // 2 + 1):
        count = alternating_count(dimension, r)
        positive = ((1 << (2 * r)) + (1 << r)) // 2
        negative = ((1 << (2 * r)) - (1 << r)) // 2
        result[Fraction(1, 1 << r)] += count * positive
        if negative:
            result[Fraction(-1, 1 << r)] += count * negative
        result[Fraction(0)] += count * ((1 << dimension) - (1 << (2 * r)))
    return +result


def quotient_spectrum(dimension):
    result = boolean_spectrum(dimension)
    factor = ((1 << dimension) - 1) * (1 << dimension)
    for eigenvalue, count in boolean_spectrum(dimension - 1).items():
        result[eigenvalue / 2] += factor * count
    order = 1 << (dimension * (dimension + 3) // 2)
    need(sum(result.values()) == order, "The spectrum must count every dual character")
    need(result[Fraction(1)] == 1, "The walk must have one stationary character")
    need(all(abs(x) <= Fraction(1, 2) for x in result if x != 1),
         "Every nontrivial eigenvalue must have modulus at most one half")
    return result


def return_ratio(dimension, width):
    """Return the probability divided by its uniform limit. Width is positive."""
    need(width >= 1, "The finite return formula requires positive width")
    power = width - 2 + (width & 1)
    first = sum((Fraction(alternating_count(dimension, r), 1 << (r * power))
                 for r in range(dimension // 2 + 1)), Fraction())
    second = sum((Fraction(alternating_count(dimension - 1, r), 1 << (r * power))
                  for r in range((dimension - 1) // 2 + 1)), Fraction())
    return first + Fraction(((1 << dimension) - 1) * (1 << dimension), 1 << width) * second


def check_small_spectra():
    receipts = []
    for dimension in range(1, 5):
        pairs = tuple((i, j) for i in range(dimension) for j in range(i + 1, dimension))
        observed = Counter()
        for linear in range(1 << (2 * dimension)):
            alpha = [(linear >> (2 * j)) & 3 for j in range(dimension)]
            for mixed in range(1 << len(pairs)):
                total = 0
                for x in range(1 << dimension):
                    value = sum(alpha[j] for j in bits(x))
                    value += 2 * sum((mixed >> k) & 1 for k, (i, j) in enumerate(pairs)
                                     if x >> i & 1 and x >> j & 1)
                    total += (1, 0, -1, 0)[value % 4]
                observed[Fraction(total, 1 << dimension)] += 1
        expected = quotient_spectrum(dimension)
        need(observed == expected, "Direct cosine sums must give the rank-count spectrum")
        receipts.append(dict(dimension=dimension, dual_characters=sum(observed.values()),
                             distinct_eigenvalues=len(observed)))
    return receipts


def check_small_walks():
    receipts = []
    for dimension in range(1, 4):
        pairs = tuple((i, j) for i in range(dimension) for j in range(i + 1, dimension))
        steps = []
        for y in range(1 << dimension):
            mixed = sum(1 << k for k, (i, j) in enumerate(pairs)
                        if y >> i & 1 and y >> j & 1)
            steps.extend(((y, 0, mixed), (y, y, mixed)))
        counts = Counter({(0, 0, 0): 1})
        order = 1 << (dimension * (dimension + 3) // 2)
        for width in range(1, 7):
            next_counts = Counter()
            for (low, high, mixed), count in counts.items():
                for a, b, c in steps:
                    next_counts[(low ^ a, high ^ b ^ (low & a), mixed ^ c)] += count
            counts = next_counts
            actual = Fraction(counts[(0, 0, 0)], 1 << ((dimension + 1) * width))
            expected = return_ratio(dimension, width) / order
            need(actual == expected, "The literal finite walk must give the return formula")
        receipts.append(dict(dimension=dimension, widths=6, final_states=len(counts)))
    return receipts


def fraction_record(value):
    return dict(numerator=value.numerator, denominator=value.denominator)


def distribution_record(n):
    m = n - 1
    spectrum = quotient_spectrum(m)
    samples = []
    for width in (1, 2, 4, 2 * m, 2 * m + 2, 2 * m + 8, 2 * m + 10):
        ratio = return_ratio(m, width)
        spectral = sum((count * eigenvalue ** width for eigenvalue, count in spectrum.items()),
                       Fraction())
        need(ratio == spectral, "The two exact return formulas must agree")
        samples.append(dict(width=width, ratio_to_limit=fraction_record(ratio)))
    need(return_ratio(m, 2 * m + 8) < Fraction(101, 100),
         "The stated large-width sample must be within one percent of the limit")
    return dict(ambient_dimension=n, signature_log2=n * (n + 3) // 2,
                odd_constant_log2=n + 1, quotient_log2=m * (m + 3) // 2,
                alternating_matrix_counts={str(d): [alternating_count(d, r)
                    for r in range(d // 2 + 1)] for d in (m, m - 1)},
                eigenvalues=[dict(value=fraction_record(value), multiplicity=count)
                             for value, count in sorted(spectrum.items())], samples=samples)


def main():
    sources = {}
    for name, pin in PINS.items():
        raw = (LANES / name).read_bytes()
        need(sha256(raw).hexdigest() == pin, "Source pin: " + name)
        if name.endswith(".json"):
            sources[name] = json.loads(raw)
    interface = sources["circuit-interface/INTERFACE.json"]
    lift = sources["source-domain/augmented-mode-lift/LIFT.json"]
    with tarfile.open(ARCHIVE, "r:gz") as archive:
        raw = archive.extractfile(PHASE_MEMBER).read()
    need(sha256(raw).hexdigest() == PHASE_PIN, "The original native phase source must be pinned")
    phases = json.loads(raw)
    need(len(interface["ports"]) == 112, "There must be 112 actual ports")
    for recipe, q in zip(phases["recipes"], interface["ports"]):
        need(recipe["q"] == q, "The actual port order must agree")
        need(tuple(recipe["idle_children"][0]["orthogonal_axes"][:8]) == port_basis(q)[1:],
             "The reconstructed port basis must agree with the original phase source")
    matrix = [[int(row.get(str(p), "0")) for p in range(112)] for row in interface["R"]]
    need([[sum(a * b for a, b in zip(x, y)) for y in matrix] for x in matrix]
         == [[56 * int(i == j) for j in range(8)] for i in range(8)], "The actual Gram is 56 I")
    sigma = [tuple(row["sigma_columns"]) for row in lift["mode_chart_recipes"]]
    identity = tuple(1 << j for j in range(73))
    for s in range(9):
        order = list(range(8 * s, 8 * s + 9)) + list(range(8 * s)) + list(range(8 * s + 9, 73))
        need(sigma[s] == tuple(identity[j] for j in order), "The fixed-owner sigma order must agree")
    routes = [[compose(sigma[s], rho(q, s)) for q in interface["ports"]] for s in range(9)]
    for s, stage in enumerate(routes):
        for q, route in zip(interface["ports"], stage):
            need(all(((a & b).bit_count() & 1) == int(i == j)
                     for i, a in enumerate(route) for j, b in enumerate(route)),
                 "Every actual route must be orthogonal")
            need(all(route[j] == identity[j] for j in range(8 * s + 9, 73)),
                 "Every route must fix the unused suffix")
            need(apply(rho(q, s), q) == q, "The original chart route must fix its port line")
    distinct_pairs = sum(all(routes[s][p] != routes[t][p] for p in range(112))
                         for s in range(9) for t in range(s + 1, 9))
    need(distinct_pairs == 36, "Every distinct stage pair must differ at every port")
    minor_ports = [0, 1, 2, 3, 4, 5, 6, 12]
    minor = [[row[p] for p in minor_ports] for row in matrix]
    need(determinant(minor) == 32, "The scalar-mode obstruction minor must have determinant 32")
    need(all(interface["ports"][p] & 1 for p in minor_ports), "The chosen character must be odd on the minor")
    generators = [r[:17] for r in routes[1][:8]]
    reached = {3}
    queue = [3]
    for value in queue:
        for generator in generators:
            image = apply(generator, value)
            if image not in reached:
                reached.add(image)
                queue.append(image)
    need(reached == {x for x in range(1, 1 << 17) if x.bit_count() % 2 == 0},
         "The actual generator orbit must contain every nonzero even vector")
    witness = generators[0]
    frame = identity[:8]
    moved_frame = witness[:8]
    char = 1 << 7
    old_phase = sum((v & char).bit_count() & 1 for v in frame) % 4
    new_phase = sum((v & char).bit_count() & 1 for v in moved_frame) % 4
    need((old_phase, new_phase) == (1, 0), "A cover-only frame commutation must fail")
    q = interface["ports"][0]
    need((q & 1, apply(witness, q) & 1) == (1, 0), "The cover-only Q commutation must fail")
    signatures = Signatures(17, generators)
    full = list(signatures.constraints)
    for action in signatures.actions:
        full.extend(plus(action[j], minus((1 << j, 0))) for j in range(signatures.size))
    full_basis, units, evens = row_basis(full)
    need((units, evens) == (152, 0), "The fully invariant signature space must have order four")
    need(all(dot4(row, odd_constant(signatures, 1, 0)) == 0 for row in full_basis),
         "The parity signature must be invariant")
    closure = []
    for dimensions in ([8], [9], [17], [8, 9, 17]):
        basis, stages = signatures.close_frames(dimensions)
        expected_log = 154 if dimensions == [17] else 18
        need(stages[-1]["solution_log2"] == expected_log, "The exact frame-signature count must agree")
        family_generators = [odd_constant(signatures, 1, 0)]
        family_generators += [odd_constant(signatures, 0, 1 << j) for j in range(16)]
        need(all(dot4(row, value) == 0 for row in basis for value in family_generators),
             "Every odd-constant signature must satisfy every closed frame constraint")
        closure.append(dict(frame_ranks=dimensions, closure=stages))
    omega = (1 << 17) - 1
    b = 3
    correlated = [b, omega ^ b, omega, omega, omega]
    need(all(signature_value(correlated, v) ==
             (0 if v.bit_count() & 1 else 2 * ((b & v).bit_count() & 1))
             for v in range(1 << 17)), "The correlated five-column construction must be exact")
    need(all(signature_value([1] * 4, v) == 0 for v in range(1 << 17)),
         "Four equal columns must give the zero signature")
    need(all(x not in (0, omega) for x in correlated[:2]), "The correlated control must leave the product sector")
    small_spectra = check_small_spectra()
    small_walks = check_small_walks()
    receipt = dict(
        status="PASS", checker_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        proof_sha256=sha256((HERE / "QUOTIENT.md").read_bytes()).hexdigest(),
        source_pins=PINS, original_phase_member=PHASE_MEMBER, original_phase_sha256=PHASE_PIN,
        actual_routes=dict(count=1008, distinct_stage_pairs=distinct_pairs, minor_ports=minor_ports,
                           minor_determinant=32, generator_ports=interface["ports"][:8],
                           generators=generators, nonzero_even_orbit=len(reached)),
        failed_commutations=dict(port=q, old_frame_phase=old_phase, new_frame_phase=new_phase,
                                 frame_character=char, old_line=q, moved_line=apply(witness, q)),
        full_invariant_signature_log2=2, frame_signature_closures=closure,
        correlated_control=dict(columns=correlated, four_equal_column=1),
        direct_small_spectra=small_spectra, literal_small_walks=small_walks,
        distributions=[distribution_record(17), distribution_record(73)],
        limits=["No projector or encoder is emitted.", "No all-size cover-mask access is admitted.",
                "The 73-dimensional odd-constant sector is sufficient; maximality is not claimed.",
                "The frame result is for complete orthogonal owner frames, not arbitrary internal cuts.",
                "No supplier, recurrence, precision, or kappa improvement is claimed."])
    (HERE / "QUOTIENT.json").write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print("PASS: 1008 routes; exact 17-dimensional phase sector; exact correlated-width distribution")


if __name__ == "__main__":
    main()
