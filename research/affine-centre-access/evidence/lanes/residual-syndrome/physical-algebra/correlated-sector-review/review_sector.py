"""Review the correlated phase sector without producer imports."""

from collections import Counter
from fractions import Fraction as F
from functools import lru_cache
from hashlib import sha256
from itertools import product as tuples
from pathlib import Path
import json
import tarfile


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[2]
ROOT = LANES.parents[2]
PACKET = LANES / "coherent-port/shared-cover-quotient-20261015"
PINS = {
    "proof": (PACKET / "QUOTIENT.md", "0e16a12d172ba215041c1096627772262863beca0c2296c8d773bdbac2d6c3d0"),
    "producer": (PACKET / "check_quotient.py", "ecfbbe9f2a30af0a281a257ac6d47c4aaf77761d7af60bbcad43e9949f3f34eb"),
    "receipt": (PACKET / "QUOTIENT.json", "b6d92578b2f7faff291855a92b7d5fa0570d0da9999cb11981333a0bc36d213d"),
    "interface": (LANES / "circuit-interface/INTERFACE.json", "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3"),
    "lift": (LANES / "source-domain/augmented-mode-lift/LIFT.json", "fe0feecc0f0924d78326f82e961fcb2eae44bfcb8cea34b8724b128cff98a927"),
    "predecessor": (LANES / "portable-source-codes/upstream-echo-20261015/COVER-QUOTIENT.md", "741bbd322ee89a0864e238db02ca8a44c26d2ab856e7c83f7b6bd36a03008a23"),
}
ARCHIVE = ROOT / "worktrees/k5-persistent-cleanup/research/community-frontier1094-audit/selected-replay.tar.gz"
ARCHIVE_PIN = "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"
PHASE_MEMBER = "candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json"
PHASE_PIN = "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa"


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def load():
    source = {}
    for key, (path, pin) in PINS.items():
        raw = path.read_bytes()
        need(sha256(raw).hexdigest() == pin, "Frozen source: " + key)
        if path.suffix == ".json":
            source[key] = json.loads(raw)
    need(sha256(ARCHIVE.read_bytes()).hexdigest() == ARCHIVE_PIN, "Selected source archive")
    with tarfile.open(ARCHIVE) as archive:
        raw = archive.extractfile(PHASE_MEMBER).read()
    need(sha256(raw).hexdigest() == PHASE_PIN, "Original exact phase member")
    source["phases"] = json.loads(raw)
    return source


def act(columns, x):
    result = 0
    while x:
        bit = x & -x
        result ^= columns[bit.bit_length() - 1]
        x -= bit
    return result


def transpose(columns):
    return tuple(sum(1 << j for j, value in enumerate(columns) if (value >> i) & 1)
                 for i in range(len(columns)))


def compose(left, right):
    return tuple(act(left, v) for v in right)


def binary_rank(rows):
    basis = {}
    for x in rows:
        while x:
            j = x.bit_length() - 1
            if j in basis:
                x ^= basis[j]
            else:
                basis[j] = x
                break
    return len(basis)


def mod4_kernel_log2(rows, width):
    """Use dense unit elimination, then a binary residual rank."""
    work = [row.copy() for row in rows if any(row)]
    units = 0
    for col in range(width - 1, -1, -1):
        pivot_index = next((i for i in range(units, len(work)) if work[i][col] & 1), None)
        if pivot_index is None:
            continue
        work[units], work[pivot_index] = work[pivot_index], work[units]
        pivot = work[units]
        if pivot[col] == 3:
            pivot[:] = [(-a) % 4 for a in pivot]
        for i in range(len(work)):
            if i != units and work[i][col]:
                coefficient = work[i][col]
                work[i] = [(a - coefficient * b) % 4 for a, b in zip(work[i], pivot)]
        units += 1
    residual = []
    for row in work[units:]:
        need(not any(a & 1 for a in row), "All non-unit constraints are even")
        residual.append(sum((a // 2) << j for j, a in enumerate(row)))
    evens = binary_rank(residual)
    return 2 * width - 2 * units - evens, units, evens


def routes(source):
    identity = tuple(1 << j for j in range(73))
    result = []
    for s in range(9):
        sigma = identity[8 * s:8 * s + 9] + identity[:8 * s] + identity[8 * s + 9:]
        need(list(sigma) == source["lift"]["mode_chart_recipes"][s]["sigma_columns"], "Actual fixed-owner sigma")
        stage = []
        for p, q in enumerate(source["interface"]["ports"]):
            absent = next(i for i in range(9) if not (q >> i) & 1)
            v = q ^ (1 << absent)
            order = list(range(9))
            order[0], order[absent] = order[absent], order[0]
            basis = tuple((1 << i) ^ (v if (v >> i) & 1 else 0) for i in order) + identity[9:]
            need(basis[0] == q and compose(basis, transpose(basis)) == identity, "Original orthogonal port basis")
            need(list(basis[1:9]) == source["phases"]["recipes"][p]["idle_children"][0]["orthogonal_axes"][:8], "Source basis binding")
            swap = list(identity)
            if s:
                for j in range(1, 9):
                    swap[j], swap[8 * s + j] = swap[8 * s + j], swap[j]
            rho = compose(basis, compose(swap, transpose(basis)))
            need(act(rho, q) == q and compose(rho, rho) == identity, "Port line and inverse route")
            matrix = compose(sigma, rho)
            need(compose(matrix, transpose(matrix)) == identity, "Ordered query route is orthogonal")
            need(matrix[8 * s + 9:] == identity[8 * s + 9:], "Unused axes are fixed")
            stage.append(matrix)
        result.append(stage)
    need(sum(all(result[s][p] != result[t][p] for p in range(112))
             for s in range(9) for t in range(s + 1, 9)) == 36, "All actual stage pairs differ")
    generators = [g[:17] for g in result[1][:8]]
    need([list(g) for g in generators] == source["receipt"]["actual_routes"]["generators"], "Actual 17-axis generators")
    reached, queue = {3}, [3]
    for x in queue:
        for g in generators:
            y = act(g, x)
            if y not in reached:
                reached.add(y)
                queue.append(y)
    need(len(reached) == 65535 and all(x and not x.bit_count() % 2 for x in reached), "All nonzero even vectors form this orbit")
    return generators


def pairs(n):
    return tuple((i, j) for i in range(n) for j in range(i + 1, n))


@lru_cache(maxsize=8192)
def features(n, v):
    return tuple((v >> i) & 1 for i in range(n)) + tuple(((v >> i) & (v >> j)) & 1 for i, j in pairs(n))


def frame_row(n, axes):
    width = n * (n + 1) // 2
    out = [0] * width
    for v in axes:
        for j, a in enumerate(features(n, v)):
            out[j] = (out[j] + a) % 4
    return out


def mixed_constraints(n):
    width = n * (n + 1) // 2
    return [[2 * int(i == j) for i in range(width)] for j in range(n, width)]


def odd_constant(n, d, b):
    return [d] * n + [2 * ((d + (b >> i) + (b >> j)) & 1) for i, j in pairs(n)]


def actual_frame_sector(generators):
    n, width = 17, 153
    outcomes = []
    family = [odd_constant(n, 1, 0)] + [odd_constant(n, 0, 1 << j) for j in range(16)]
    for r in (8, 9, 17):
        axes = [1 << j for j in range(r)]
        baseline = frame_row(n, axes)
        rows = mixed_constraints(n)
        words = []
        for k in range(600):
            index = sha256(("frame-rank=%d;step=%d" % (r, k)).encode()).digest()[0] % 8
            words.append(index)
            axes = [act(generators[index], v) for v in axes]
            row = [(a - b) % 4 for a, b in zip(frame_row(n, axes), baseline)]
            if r == n:
                need(all(a % 2 == 0 for a in row) and sum(row[:n]) % 4 == 0,
                     "Full-frame constraints depend only on the even translation and linear parity")
            rows.append(row)
        need(all(sum(a * b for a, b in zip(row, value)) % 4 == 0 for row in rows for value in family), "All proposed S17 generators satisfy the exact constraints")
        log2, units, evens = mod4_kernel_log2(rows, width)
        need(log2 == (154 if r == 17 else 18), "Independent finite-word frame bound")
        outcomes.append({"frame_rank": r, "generator_word_length": 600,
                         "word_sha256": sha256(bytes(words)).hexdigest(),
                         "unit_pivots": units, "even_pivots": evens, "solution_log2": log2})
    # Evaluation at coordinate vectors and pairs determines the polynomial.
    rows = mixed_constraints(n)
    sample_points = [1 << j for j in range(n)] + [(1 << i) ^ (1 << j) for i, j in pairs(n)]
    for g in generators:
        for v in sample_points:
            rows.append([(a - b) % 4 for a, b in zip(features(n, act(g, v)), features(n, v))])
    invariant, units, evens = mod4_kernel_log2(rows, width)
    need(invariant == 2 and all(sum(a * b for a, b in zip(row, family[0])) % 4 == 0 for row in rows), "Only four individually invariant signatures")
    return outcomes, {"solution_log2": invariant, "unit_pivots": units, "even_pivots": evens}


def value(alpha, beta, v):
    n = len(alpha)
    return (sum(alpha[i] for i in range(n) if (v >> i) & 1) +
            2 * sum((beta >> k) & 1 for k, (i, j) in enumerate(pairs(n)) if (v >> i) & (v >> j) & 1)) % 4


def small_quotients():
    results = []
    for n in range(1, 5):
        images, survivors = Counter(), 0
        for alpha in tuples(range(4), repeat=n):
            for beta in range(1 << (n * (n - 1) // 2)):
                data = [value(alpha, beta, v) for v in range(1 << n)]
                odd = [data[v] for v in range(1 << n) if v.bit_count() & 1]
                survivor = len(set(odd)) == 1
                survivors += survivor
                if survivor:
                    d = alpha[0]
                    b = sum((((beta >> (j - 1)) & 1) ^ (d & 1)) << j for j in range(1, n))
                    need(list(alpha) + [2 * ((beta >> k) & 1) for k in range(n * (n - 1) // 2)]
                         == odd_constant(n, d, b), "Direct odd-constant classification")
                image = tuple((data[t | ((1 ^ (t.bit_count() & 1)) << (n - 1))] - data[1 << (n - 1)]) % 4
                              for t in range(1 << (n - 1)))
                need(survivor == (not any(image)), "Direct odd-hyperplane kernel")
                images[image] += 1
        need(survivors == 1 << (n + 1), "Direct S_n count")
        need(len(images) == 1 << ((n - 1) * (n + 2) // 2) and set(images.values()) == {1 << (n + 1)}, "Direct quotient surjection and fibres")
        results.append({"ambient_dimension": n, "signatures": sum(images.values()),
                        "quotient_images": len(images), "kernel_order": survivors})
    for n in range(2, 7):
        for x in range(1 << n):
            epsilon = (x >> (n - 1)) & 1
            y = (x & ((1 << (n - 1)) - 1)) ^ (((1 << (n - 1)) - 1) if epsilon else 0)
            for t in range(1 << (n - 1)):
                v = t | ((1 ^ (t.bit_count() & 1)) << (n - 1))
                lhs = (((x & v).bit_count() & 1) - epsilon) % 4
                rhs = ((-1) ** epsilon * ((y & t).bit_count() & 1)) % 4
                need(lhs == rhs, "Actual signed walk step")
    return results


def check_small_mod4_elimination():
    count = 0
    for n in range(1, 4):
        width = n * (n + 1) // 2
        first = [sha256(("row-a-%d-%d" % (n, i)).encode()).digest()[0] % 4 for i in range(width)]
        second = [sha256(("row-b-%d-%d" % (n, i)).encode()).digest()[0] % 4 for i in range(width)]
        rows = mixed_constraints(n)
        for next_row in (first, [(2 * a) % 4 for a in first], second):
            rows.append(next_row)
            observed = 0
            for alpha in tuples(range(4), repeat=n):
                for beta in range(1 << (n * (n - 1) // 2)):
                    signature = list(alpha) + [2 * ((beta >> k) & 1) for k in range(n * (n - 1) // 2)]
                    observed += all(sum(a * b for a, b in zip(row, signature)) % 4 == 0 for row in rows)
            log2, _, _ = mod4_kernel_log2(rows, width)
            need(observed == 1 << log2, "Dense mod4 elimination versus every small signature")
            count += 1
    return count


@lru_cache(maxsize=None)
def alternating_counts(d):
    """Append one row and column; image vectors keep the old rank."""
    counts = [1]
    for size in range(1, d + 1):
        new = [0] * (size // 2 + 1)
        for r, number in enumerate(counts):
            new[r] += number * (1 << (2 * r))
            if r + 1 < len(new):
                new[r + 1] += number * ((1 << (size - 1)) - (1 << (2 * r)))
        counts = new
    need(sum(counts) == 1 << (d * (d - 1) // 2), "All alternating forms counted")
    return tuple(counts)


def closed_count(d, r):
    numerator, denominator = 1, 1 << (r * r)
    for j in range(2 * r):
        numerator *= (1 << d) - (1 << j)
    for j in range(1, r + 1):
        denominator *= (1 << (2 * j)) - 1
    quotient, remainder = divmod(numerator, denominator)
    need(remainder == 0, "Closed count is integral")
    return quotient


def boolean_spectrum(d):
    result = Counter()
    for r, number in enumerate(alternating_counts(d)):
        result[F(1, 1 << r)] += number * ((1 << (2 * r)) + (1 << r)) // 2
        result[F(-1, 1 << r)] += number * ((1 << (2 * r)) - (1 << r)) // 2
        result[F(0)] += number * ((1 << d) - (1 << (2 * r)))
    return +result


def spectrum(m):
    result = boolean_spectrum(m)
    for eigenvalue, number in boolean_spectrum(m - 1).items():
        result[eigenvalue / 2] += ((1 << m) - 1) * (1 << m) * number
    need(sum(result.values()) == 1 << (m * (m + 3) // 2), "Full dual multiplicity")
    need(result[F(1)] == 1 and all(abs(x) <= F(1, 2) for x in result if x != 1), "Unique stationary value and spectral gap")
    return result


def small_gauss_sums():
    results = []
    for d in range(6):
        observed, ranks = Counter(), Counter()
        for beta in range(1 << (d * (d - 1) // 2)):
            rows = [0] * d
            for k, (i, j) in enumerate(pairs(d)):
                if (beta >> k) & 1:
                    rows[i] |= 1 << j
                    rows[j] |= 1 << i
            rank = binary_rank(rows)
            need(rank % 2 == 0, "Alternating rank is even")
            ranks[rank // 2] += 1
            quadratic = [sum((beta >> k) & 1 for k, (i, j) in enumerate(pairs(d)) if (x >> i) & (x >> j) & 1) % 2
                         for x in range(1 << d)]
            for linear in range(1 << d):
                total = sum(1 if ((linear & x).bit_count() + quadratic[x]) % 2 == 0 else -1 for x in range(1 << d))
                observed[F(total, 1 << d)] += 1
        need([ranks[r] for r in range(d // 2 + 1)] == list(alternating_counts(d)), "Literal alternating matrices versus recurrence")
        need(observed == boolean_spectrum(d), "Literal binary Gauss multiplicities")
        results.append({"dimension": d, "alternating_forms": sum(ranks.values()), "quadratic_forms": sum(observed.values())})
    for m in range(1, 5):
        observed = Counter()
        for alpha in tuples(range(4), repeat=m):
            for beta in range(1 << (m * (m - 1) // 2)):
                cosine_sum = sum((1, 0, -1, 0)[value(alpha, beta, y)] for y in range(1 << m))
                observed[F(cosine_sum, 1 << m)] += 1
        need(observed == spectrum(m), "Literal Z4 cosine spectrum")
    return results


def ratio(n, width):
    m = n - 1
    need(width >= 1 and m >= 1, "Positive width and nontrivial quotient")
    exponent = width - 2 + width % 2
    first = sum((F(a, 1 << (r * exponent)) for r, a in enumerate(alternating_counts(m))), F())
    second = sum((F(a, 1 << (r * exponent)) for r, a in enumerate(alternating_counts(m - 1))), F())
    return first + F(((1 << m) - 1) * (1 << m), 1 << width) * second


def small_walks():
    records = []
    for n in range(2, 5):
        m = n - 1
        # Store the full quotient function on its nonzero arguments.
        steps = []
        for x in range(1 << n):
            epsilon = (x >> m) & 1
            steps.append(tuple((((x & (t | ((1 ^ (t.bit_count() & 1)) << m))).bit_count() & 1) - epsilon) % 4
                               for t in range(1, 1 << m)))
        zero = (0,) * ((1 << m) - 1)
        counts = {zero: 1}
        values = []
        for width in range(1, 7):
            new = Counter()
            for old, number in counts.items():
                for step in steps:
                    new[tuple((a + b) % 4 for a, b in zip(old, step))] += number
            counts = new
            probability = F(counts[zero], 1 << (n * width))
            need(probability == ratio(n, width) / (1 << (m * (m + 3) // 2)), "Literal original-column return probability")
            values.append({"width": width, "numerator": probability.numerator, "denominator": probability.denominator})
        records.append({"ambient_dimension": n, "final_function_states": len(counts), "probabilities": values})
    return records


def exact_record(x):
    return {"numerator": x.numerator, "denominator": x.denominator}


def distributions(source):
    for d in range(73):
        need(list(alternating_counts(d)) == [closed_count(d, r) for r in range(d // 2 + 1)], "Independent recurrence agrees with closed count at every required dimension")
    outputs = []
    for n, threshold in ((17, 40), (73, 152)):
        m, index_log = n - 1, (n - 1) * (n + 2) // 2
        dual = spectrum(m)
        original = next(r for r in source["receipt"]["distributions"] if r["ambient_dimension"] == n)
        need(original["quotient_log2"] == index_log, "Uniform-limit exponent")
        emitted = {F(r["value"]["numerator"], r["value"]["denominator"]): r["multiplicity"] for r in original["eigenvalues"]}
        need(emitted == dict(dual), "Every emitted exact dual multiplicity")
        for row in original["samples"]:
            width = row["width"]
            actual = ratio(n, width)
            need(actual == F(row["ratio_to_limit"]["numerator"], row["ratio_to_limit"]["denominator"]), "Every emitted finite-width value")
            need(actual == sum((count * value ** width for value, count in dual.items()), F()), "Independent spectrum and closed return formula")
        before, at, after = (ratio(n, width) for width in (threshold - 1, threshold, threshold + 1))
        need(before > F(101, 100) and F(1) < after < at < F(101, 100), "Sharp one-percent threshold")
        # The closed expression proves monotonicity at all later widths.
        outputs.append({"ambient_dimension": n, "limit_exponent": -index_log,
                        "fixed_d_limit_exponent": -index_log - 2,
                        "least_width_with_ratio_below_101_over_100": threshold,
                        "ratio_previous": exact_record(before), "ratio_at_threshold": exact_record(at),
                        "ratio_next": exact_record(after), "density_at_threshold": exact_record(at / (1 << index_log))})
    return outputs


def main():
    source = load()
    generators = routes(source)
    mod4_tests = check_small_mod4_elimination()
    frame, fixed = actual_frame_sector(generators)
    print("PASS independent finite-word frame ranks", flush=True)
    quotient = small_quotients()
    gauss = small_gauss_sums()
    walks = small_walks()
    distribution = distributions(source)
    omega, b = (1 << 17) - 1, 3
    correlated = [b, omega ^ b, omega, omega, omega]
    need(all(sum((x & v).bit_count() & 1 for x in correlated) % 4 ==
             (0 if v.bit_count() & 1 else 2 * ((b & v).bit_count() & 1)) for v in range(1 << 17)), "All five-column correlated control values")
    output = {
        "status": "PASS_INDEPENDENT_CORRELATED_SECTOR",
        "source_pins": {k: {"path": str(p.relative_to(ROOT)), "sha256": h} for k, (p, h) in PINS.items()},
        "archive_sha256": ARCHIVE_PIN, "phase_member_sha256": PHASE_PIN,
        "producer_imported": False, "producer_run": False,
        "actual_routes": 1008, "nonzero_even_vector_orbit": 65535,
        "finite_word_frame_constraints": frame, "pointwise_invariant_signatures": fixed,
        "exhaustive_small_mod4_solver_checks": mod4_tests,
        "small_quotients": quotient, "small_binary_gauss_counts": gauss,
        "literal_original_character_walks": walks, "exact_distributions": distribution,
        "alternating_count_recurrence_dimensions": list(range(73)),
        "scope": "The correlated-signature sector, actual 17-axis maximal frame sector, exact all-width density formula, and exact large-width thresholds.",
        "not_claimed": ["Maximality for the 73-axis actual group", "A physical sector projector or encoding", "Internal-canonical-frame invariance", "Native source access or an implementation invoice", "A supplier or kappa improvement"],
    }
    output["checker_sha256"] = sha256(Path(__file__).read_bytes()).hexdigest()
    (HERE / "REVIEW.json").write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(output["status"], flush=True)


if __name__ == "__main__":
    main()
