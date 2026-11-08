"""Input-independent source pages for the full periodic Reference inverse.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Exact setup is separately charged polynomial-time rational arithmetic. Online
right-hand sides never enter this module. Schur/q-LDU identities are inherited.
"""
from dataclasses import dataclass
from fractions import Fraction as Q
from hashlib import sha256
import json


def need(condition, message):
    if not condition:
        raise ValueError(message)


def ceiling(value):
    value = Q(value)
    return -((-value.numerator) // value.denominator)


def ceil_log2(value):
    value = Q(value)
    need(value > 0, "positive allocation logarithm")
    result = max(0, value.numerator.bit_length() - value.denominator.bit_length())
    while Q(1 << result) < value:
        result += 1
    return result


def trunc(value):
    value = Q(value)
    return (-1 if value < 0 else 1) * (abs(value.numerator) // value.denominator)


def norm(matrix):
    return max((sum(map(abs, row), Q()) for row in matrix), default=Q())


def gap(matrix):
    return min(matrix[i][i] - sum(abs(x) for j, x in enumerate(matrix[i])
                                 if j != i) for i in range(len(matrix)))


def frozen(matrix):
    return tuple(tuple(map(Q, row)) for row in matrix)


def encoded(value):
    if isinstance(value, Q):
        return [value.numerator, value.denominator]
    if isinstance(value, dict):
        return {key: encoded(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [encoded(item) for item in value]
    return value


def digest(value):
    return sha256(json.dumps(encoded(value), sort_keys=True,
                             separators=(",", ":")).encode("ascii")).hexdigest()


@dataclass(frozen=True)
class Plan:
    source_size: int
    target_size: int
    source_halfwidth: int
    boundary_size: int
    band: int
    radius: int
    target: int
    f: int
    W: int
    native_target: int
    run_radius: int
    schur_radius: int
    maximum_scalar_width: int
    delta: Q
    reference_error: Q
    real_tolerance: Q
    stage_allowance: Q
    first_radius: Q
    schur_input_radius: Q
    schur_output_radius: Q
    second_input_radius: Q
    run_error: Q
    schur_error: Q
    sb_error: Q
    k_error: Q
    complex_error: Q
    reference_to_ideal_error: Q
    ideal_complex_error: Q
    source_spec: tuple

    @property
    def precision(self):
        return self.f

    @property
    def width(self):
        return self.W

    def receipt(self):
        return encoded(vars(self))


@dataclass(frozen=True)
class Run:
    start: int
    native: object
    boundary_count: int

    @property
    def n(self):
        return self.native.plan.n

    @property
    def header(self):
        p = self.native.plan
        return (p.n, p.L, p.W, p.f)


@dataclass(frozen=True)
class Bundle:
    plan: Plan
    runs: tuple
    selected: tuple
    target_mask: tuple
    boundary_mask: tuple
    run_end_mask: tuple
    boundary_indices: tuple
    folded_plan: dict
    sb_coefficients: tuple
    k_coefficients: tuple
    exact: dict
    setup: dict

    def receipt(self):
        return {
            "plan": self.plan.receipt(),
            "source_hash": self.setup["source_hash"],
            "exact_matrices_sha256": digest(self.exact),
            "runs": [dict(start=run.start, n=run.n, header=run.header,
                          boundary_count=run.boundary_count,
                          coefficient_sha256=run.native.receipt()["stream_sha256"])
                     for run in self.runs],
            "masks_sha256": digest((self.target_mask, self.boundary_mask,
                                     self.run_end_mask)),
            "sb_sha256": digest(self.sb_coefficients),
            "k_sha256": digest(self.k_coefficients),
            "folded_pages_sha256": digest((self.folded_plan["lower"],
                                             self.folded_plan["upper"])),
            "setup": encoded(self.setup),
        }


def band_bank(matrix, permutation, band, precision, width):
    """Folded row order, offsets -band,...,+band, complete zero padding."""
    n, unit = len(matrix), 1 << precision
    need(sorted(permutation) == list(range(n)), "complete folded permutation")
    source = [[matrix[i][j] for j in permutation] for i in permutation]
    need(all(not source[i][j] for i in range(n) for j in range(n)
             if abs(i-j) > band), "source matrix has declared folded band")
    result = []
    for i in range(n):
        for offset in range(-band, band+1):
            j = i + offset
            exact = source[i][j] if 0 <= j < n else Q()
            value = trunc(exact * unit)
            rounded = Q(value, unit)
            need(abs(exact - rounded) <= Q(1, unit) and
                 abs(rounded) <= abs(exact), "inward rational matrix coefficient")
            need(abs(value) < 1 << (width-1), "common matrix coefficient carrier")
            result.append(value)
    return tuple(result)


def prepare(reference, radius, target, *, run_coefficients, folded_pages):
    """Prepare one fixed source; `radius`/`target` are scalar promises only.

    The two dependency modules must be the authenticated frozen producers.
    Matrices in `exact` are offline evidence, not online coefficient ports.
    """
    need(type(radius) is int and radius >= 1 and type(target) is int and target >= 0,
         "positive integer radius and nonnegative target")
    reference.require_narrow_gap()
    spec = reference.spec
    S, T, w = spec.source_size, reference.target_size, spec.source_halfwidth
    delta, source_error = Q(reference.narrow_gap), Q(reference.errors["narrow"])
    need(0 < delta <= 1 and 1 <= w and 2*w < S, "positive nonidentity source geometry")
    real_tolerance = Q(1, 1 << (target+1))
    allowance = real_tolerance * delta * delta / 16
    native_target = ceil_log2(4 / (allowance * delta))
    Y, Tin = Q(radius+1) / delta, Q(3*(radius+1)) / delta
    Z, Cin = Q(4*(radius+1)) / (delta*delta), Q(6*(radius+1)) / (delta*delta)
    run_radius, schur_radius = ceiling(Cin), ceiling(Tin)

    phases = tuple(reference.phases)
    selected = tuple(reference.selected)
    need(len(phases) == S and selected == tuple(i+phases[i] for i in range(S)),
         "original selected-coordinate geometry")
    need(selected[0] == 0 and all(selected[i] < selected[i+1] for i in range(S-1))
         and selected[-1] < T, "increasing original selected coordinates")
    intervals, start = [], 0
    for i in range(1, S+1):
        if i == S or phases[i] != phases[start]:
            intervals.append((start, i-start))
            start = i
    need(len(intervals) <= spec.excess+1, "ordinary phase-run count")
    boundary = tuple(sorted({i for start, n in intervals
                             for i in list(range(start, min(start+w, start+n)))
                             + list(range(max(start, start+n-w), start+n))}))
    boundary_set = set(boundary)
    interior = tuple(i for i in range(S) if i not in boundary_set)
    m = len(boundary)
    need(2 <= m <= 2*w*(spec.excess+1), "complete bounded boundary union")
    band = min(m-1, 4*w-2)
    selected_set = set(selected)
    target_mask = tuple(int(q in selected_set) for q in range(T))
    boundary_mask = tuple(int(i in boundary_set) for i in range(S))
    ends = {start+n-1 for start, n in intervals}
    run_end_mask = tuple(int(i in ends) for i in range(S))

    native_runs = tuple(Run(start, run_coefficients.prepare(
        reference, start, n, run_radius, native_target),
        sum(boundary_mask[start:start+n])) for start, n in intervals)
    need(all(run.native.plan.f >= native_target+1 for run in native_runs),
         "native run conversion precision")
    owner = [0] * S
    for group, (start, n) in enumerate(intervals):
        for i in range(start, start+n):
            owner[i] = group
    A = [[reference.entry("narrow", selected[i], selected[j]).value
          if min((j-i) % S, (i-j) % S) <= w else Q()
          for j in range(S)] for i in range(S)]
    need(all(A[i][i] == 1 for i in range(S)) and gap(A) >= delta and norm(A) <= 2,
         "actual source diagonal, gap and norm")
    B = [[A[i][j] if owner[i] == owner[j] else Q()
          for j in range(S)] for i in range(S)]
    need(all(A[i][j] == B[i][j] for i in range(S) for j in range(S)
             if i not in boundary_set or j not in boundary_set),
         "cross-run correction supported on boundary union")
    K = [[A[i][j]-B[i][j] for j in boundary] for i in boundary]
    SB = folded_pages.schur(B, list(interior), list(boundary))
    SA = [[SB[i][j]+K[i][j] for j in range(m)] for i in range(m)]
    need(gap(B) >= delta and gap(SB) >= delta and gap(SA) >= delta,
         "exact nonsymmetric row-gap inheritance")
    need(max(norm(B), norm(SB), norm(SA)) <= 2 and norm(K) <= 1,
         "source and Schur norm budgets")
    folded = folded_pages.prepare(SA, band, native_target, schur_radius)
    need(folded["precision"] >= native_target+1, "native folded conversion precision")

    terms = 2*band+1
    precision = max([run.native.plan.f for run in native_runs]
                    + [folded["precision"], ceil_log2((terms*ceiling(Z)+2)/allowance)])
    width = max(precision+ceil_log2(run_radius+1)+2,
                ceil_log2(T+1)+2, ceil_log2(band+1)+2)
    sb_bank = band_bank(SB, folded["permutation"], band, precision, width)
    k_bank = band_bank(K, folded["permutation"], band, precision, width)
    run_error = max(run.native.plan.total_error
                    + Q(2, 1 << run.native.plan.f)/delta for run in native_runs)
    schur_error = folded["error_bound"] + Q(2, 1 << folded["precision"])/delta
    sb_error, k_error = (terms*Y+2)/Q(1 << precision), (terms*Z+2)/Q(1 << precision)
    need(max(run_error, schur_error, sb_error, k_error) <= allowance,
         "every complete actual-input stage is funded")
    complex_error = 2*((2*run_error+sb_error)/(delta*delta)
                      + (schur_error+k_error)/delta + run_error)
    need(complex_error <= Q(1, 1 << target), "full complex source inverse budget")
    reference_to_ideal = 2*radius*source_error/(delta*(delta+source_error))
    ideal_error = complex_error + reference_to_ideal
    need(ideal_error <= Q(1, 1 << target), "full periodic ideal inverse budget")
    need(Q(radius)/delta + complex_error <= run_radius,
         "final common transport carrier")
    largest = max([width, folded["width"]] + [run.native.plan.W for run in native_runs])
    plan = Plan(S, T, w, m, band, radius, target, precision, width, native_target,
                run_radius, schur_radius, largest, delta, source_error,
                real_tolerance, allowance, Y, Tin, Z, Cin, run_error,
                schur_error, sb_error, k_error, complex_error,
                reference_to_ideal, ideal_error,
                tuple(getattr(spec, key) for key in spec.__dataclass_fields__))
    exact = {name: frozen(value) for name, value in
             (("A", A), ("B", B), ("SB", SB), ("SA", SA), ("K", K))}
    height = max(max(abs(x.numerator).bit_length(), x.denominator.bit_length())
                 for matrix in exact.values() for row in matrix for x in row)
    setup = dict(source_hash=reference.description_hash,
                 maximum_exact_matrix_height=height,
                 source_entry_queries=S*(2*w+1), run_count=len(native_runs),
                 native_coefficient_records=sum(sum(map(len, run.native.streams.values()))
                                                for run in native_runs),
                 matrix_coefficient_records=len(sb_bank)+len(k_bank),
                 folded_coefficient_records=len(folded["lower"])+len(folded["upper"]))
    return Bundle(plan, native_runs, selected, target_mask, boundary_mask,
                  run_end_mask, boundary, folded, sb_bank, k_bank, exact, setup)
