"""Exact affine certificates for the cited three-qubit multiplicity data.

This reads predecessor data, never its verifier or character-decomposition code.
All acceptance checks remain enabled under optimized Python.
"""

from fractions import Fraction
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE_DIGESTS = {
    "pr6714-result.json": "308b8dee094eb5481565ea89698ed5df69edeeecd4b63b4d78cb9cecdbe71c27",
    "pr6714-table.json": "388d617a76e345774a8768f32a6a9bc6e94b87f9c8a5cf6712a95a5a3a945fcd",
}
MAX_FILE_BYTES = 262144
PACKAGE_FILES = (
    "README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json",
    "ORIGIN.json", "VALIDATION.md", "verify.py", "source/pr6714-result.json",
    "source/pr6714-table.json",
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def bounded_bytes(path):
    with path.open("rb") as stream:
        payload = stream.read(MAX_FILE_BYTES + 1)
    require(len(payload) <= MAX_FILE_BYTES, "file exceeds declared replay bound")
    return payload


def source_points():
    sources = {}
    for name, digest in SOURCE_DIGESTS.items():
        payload = bounded_bytes(HERE / "source" / name)
        require(sha256(payload).hexdigest() == digest, "source hash: " + name)
        sources[name] = json.loads(payload)
    result = sources["pr6714-result.json"]
    table = sources["pr6714-table.json"]["characters"]
    indices = result["quotient_source_rows"]
    multiplicities = result["odd_tensor_multiplicities"]["9"]
    require(len(indices) == len(multiplicities) == 30, "thirty cited types")
    require(len(set(indices)) == 30, "distinct source row indices")
    column = result["transvection_column_one_based"] - 1
    fibre = result["quotient_source_classes"][column]
    require(fibre == [31, 32, 33], "cited transvection fibre")
    require(len(table) == 67, "cited table row count")
    points = []
    for index, multiplicity in zip(indices, multiplicities):
        require(type(index) is int and 1 <= index <= 67, "source row index")
        row = table[index - 1]
        require(len(row) == 67, "cited table column count")
        degree, trace = row[0], row[fibre[0] - 1]
        require(all(row[j - 1] == trace for j in fibre), "fibre identification")
        points.append((index, degree, trace, multiplicity))
    validate_points(points)
    require(result["projective_order"] == 92897280, "cited group order")
    return tuple(points), Fraction(result["projective_order"], 8**10)


def validate_points(points):
    require(len(points) == 30, "complete cited type list")
    for index, degree, trace, multiplicity in points:
        require(all(type(x) is int for x in (index, degree, trace, multiplicity)),
                "integer character data")
        require(degree > 0 and multiplicity >= 0, "positive degree and multiplicity")
        require(abs(trace) <= degree, "character trace bound")


def affine_slacks(points, lower=(Fraction(5, 4), Fraction(7, 4)),
                  upper=(Fraction(1345, 12), Fraction(1883, 12))):
    """An affine inequality at every type holds for every nonnegative mixture."""
    validate_points(points)
    answer = []
    for index, degree, trace, multiplicity in points:
        low = multiplicity - lower[0] * degree - lower[1] * trace
        high = upper[0] * degree + upper[1] * trace - multiplicity
        require(low >= 0, "lower affine certificate at row " + str(index))
        require(high >= 0, "upper affine certificate at row " + str(index))
        answer.append((index, str(low), str(high)))
    return answer


def vertices(points, orbit_size):
    """Enumerate all vertices of simplex intersected with one trace slab."""
    require(orbit_size in (28, 36), "the two cited Pauli orbit sizes")
    cap = Fraction(16, orbit_size)
    values = []
    for index, degree, trace, multiplicity in points:
        if abs(Fraction(trace, degree)) <= cap:
            values.append((Fraction(multiplicity, degree), index, index,
                           Fraction(1), Fraction(trace, degree)))
    for first, second in combinations(points, 2):
        i, degree_i, trace_i, multiplicity_i = first
        j, degree_j, trace_j, multiplicity_j = second
        x_i, x_j = Fraction(trace_i, degree_i), Fraction(trace_j, degree_j)
        if x_i == x_j:
            continue
        for endpoint in (-cap, cap):
            weight = (endpoint - x_j) / (x_i - x_j)
            if 0 <= weight <= 1:
                objective = (weight * Fraction(multiplicity_i, degree_i)
                             + (1 - weight) * Fraction(multiplicity_j, degree_j))
                values.append((objective, i, j, weight, endpoint))
    require(bool(values), "nonempty relaxed feasible region")
    return values


def bounds(points, normalization):
    expected = {28: (Fraction(1, 4), Fraction(807, 4)),
                36: (Fraction(17, 36), Fraction(19637, 108))}
    answer = []
    for orbit_size in (28, 36):
        cap = Fraction(16, orbit_size)
        lower = Fraction(5, 4) - Fraction(7, 4) * cap
        upper = Fraction(1345, 12) + Fraction(1883, 12) * cap
        candidates = vertices(points, orbit_size)
        minimum, maximum = min(candidates), max(candidates)
        require((lower, upper) == expected[orbit_size], "derived orbit bounds")
        require((minimum[0], maximum[0]) == (lower, upper), "primal/dual equality")
        answer.append({"orbit": orbit_size, "vertices": len(candidates),
                       "multiplicity_bounds": [str(lower), str(upper)],
                       "gram_bounds": [str(normalization * lower),
                                       str(normalization * upper)],
                       "minimizer": [str(x) for x in minimum[1:]],
                       "maximizer": [str(x) for x in maximum[1:]]})
    low, high = normalization / 4, normalization * Fraction(807, 4)
    require(low == Fraction(2835, 131072), "uniform lower bound")
    require(high == Fraction(2287845, 131072), "uniform upper bound")
    require(high / low == 807, "uniform condition bound")
    require(low == 6 * Fraction(945, 262144), "strict lower improvement")
    require(high == Fraction(3, 4) * Fraction(762615, 32768),
            "strict upper improvement")
    return answer


def rejection_controls(points):
    """Change a tight row or certificate; acceptance must fail at the real gate."""
    rejected = []
    for kind in ("low-row", "high-row", "missing-row", "low-line", "high-line",
                 "wrong-trace", "invalid-orbit"):
        altered = list(points)
        lower = (Fraction(5, 4), Fraction(7, 4))
        upper = (Fraction(1345, 12), Fraction(1883, 12))
        if kind == "low-row":
            pos = next(i for i, row in enumerate(altered) if row[0] == 9)
            index, degree, trace, multiplicity = altered[pos]
            altered[pos] = (index, degree, trace, multiplicity - 1)
        elif kind == "high-row":
            index, degree, trace, multiplicity = altered[0]
            altered[0] = (index, degree, trace, multiplicity + 1)
        elif kind == "missing-row":
            altered = [row for row in altered if row[0] != 2]
        elif kind == "low-line":
            lower = (lower[0] + Fraction(1, 10000), lower[1])
        elif kind == "high-line":
            upper = (upper[0] - Fraction(1, 10000), upper[1])
        elif kind == "wrong-trace":
            index, degree, trace, multiplicity = altered[1]
            altered[1] = (index, degree, -trace, multiplicity)
        try:
            if kind == "invalid-orbit":
                vertices(altered, 64)
            else:
                affine_slacks(altered, lower, upper)
        except ValueError:
            rejected.append(kind)
        else:
            raise ValueError("accepted mathematical mutation: " + kind)
    return rejected


def package_hashes():
    return {name: sha256(bounded_bytes(HERE / name)).hexdigest()
            for name in PACKAGE_FILES}


def main():
    points, normalization = source_points()
    slacks = affine_slacks(points)
    orbit_bounds = bounds(points, normalization)
    controls = rejection_controls(points)
    receipt = {"status": "PASS_CLIFFORD_TRANSVECTION_CONDITIONING",
               "claim_type": "scoped proof with exact finite corroboration",
               "type_count": len(points), "affine_slacks": slacks,
               "orbit_bounds": orbit_bounds, "normalization": str(normalization),
               "uniform_gram_bounds": ["2835/131072", "2287845/131072"],
               "uniform_condition_bound": 807, "rejected_controls": controls,
               "package_sha256": package_hashes()}
    print(json.dumps(receipt, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
