"""Exact finite corroboration of the balanced-cycle theorem, not its full cycle."""

import hashlib
import itertools
import json
from pathlib import Path

from cycle import D, E, LAMBDA, N, PERIOD, apply_frame, frame_vector, load_basis

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def check(condition, message):
    if not condition:
        raise ValueError(message)


def parity(value):
    return value.bit_count() & 1


def codeword(label):
    """The [8,4,4] weight model, in an independent RM(1,3) chart."""
    return sum((parity((label >> 1) & point) ^ (label & 1)) << point
               for point in range(8))


def evaluate(cols, q):
    value = 0
    for i in range(4):
        if q >> i & 1:
            value ^= cols[i]
    return value


def rank(vectors):
    pivots = [0] * 112
    for vector in vectors:
        for bit in range(111, -1, -1):
            if vector >> bit & 1:
                if pivots[bit]:
                    vector ^= pivots[bit]
                else:
                    pivots[bit] = vector
                    break
    return sum(bool(pivot) for pivot in pivots)


def character_weights(maps, dimension):
    """Literal adjoints for arbitrary Q -> R maps, including non-rank-one maps."""
    check(1 <= dimension <= 8 and 1 <= len(maps) <= 256, "toy domain")
    check(all(len(cols) == 4 and all(0 <= x < 1 << dimension for x in cols)
              for cols in maps), "toy map shape")
    result = []
    weights = [codeword(c).bit_count() for c in range(16)]
    for b in range(1 << dimension):
        offsets = [sum(parity(b & col) << i for i, col in enumerate(cols))
                   for cols in maps]
        for c in range(16):
            if b or c:
                result.append(sum(weights[c ^ offset] for offset in offsets))
    return result


def scaled_gap(maps, dimension):
    """13**(8t) times S minus the proposed lower bound; integer arithmetic."""
    t = len(maps)
    values = character_weights(maps, dimension)
    lhs = sum(13 ** (8 * t - weight) for weight in values)
    rhs = ((1 << (dimension + 4)) - 2) * 13 ** (4 * t) + 1
    return lhs - rhs


def finite_cycles():
    cases = characters = 0
    for dimension in range(1, 9):
        size = 1 << dimension
        maps = [(a ^ (a >> 1), 0, 0, 0) for a in range(size)]
        values = character_weights(maps, dimension)
        check(values.count(4 * size) == (1 << (dimension + 4)) - 2,
              "balanced spectrum at dimension " + str(dimension))
        check(values.count(8 * size) == 1, "unique weight-eight character")
        check(scaled_gap(maps, dimension) == 0, "exact cycle lower bound")
        if dimension <= 5:
            check(scaled_gap(maps + maps, dimension) == 0, "repeated cycle")
        mutant = maps.copy()
        mutant[-1] = mutant[0]
        check(scaled_gap(mutant, dimension) > 0, "omitted-vector control")
        for q in range(1, 16, 2):
            evaluations = [evaluate(cols, q) for cols in maps]
            check(len(set(evaluations)) == size, "Fourier equality marginal")
        characters += len(values)
        cases += 1
    return cases, characters


def arbitrary_map_census():
    cases = equalities = 0
    for dimension, largest_t in ((1, 4), (2, 2)):
        alphabet = tuple(itertools.product(range(1 << dimension), repeat=4))
        for t in range(1, largest_t + 1):
            for suffix in itertools.product(alphabet, repeat=t - 1):
                gap = scaled_gap(((0, 0, 0, 0),) + suffix, dimension)
                check(gap >= 0, "affine lower bound")
                if gap == 0:
                    check(t % (1 << dimension) == 0, "equality divisibility")
                    equalities += 1
                cases += 1
    return cases, equalities


def fourier_checks():
    cases = 0
    # Exhaust every occupancy vector of total at most six in dimensions 1..3.
    for dimension in range(1, 4):
        size = 1 << dimension
        for total in range(1, 7):
            for bars in itertools.combinations(range(total + size - 1), size - 1):
                ends = (-1,) + bars + (total + size - 1,)
                counts = tuple(ends[i + 1] - ends[i] - 1 for i in range(size))
                vanishes = all(sum(counts[a] * (-1) ** parity(a & b)
                                   for a in range(size)) == 0 for b in range(1, size))
                check(vanishes == (len(set(counts)) == 1), "Fourier inversion")
                if vanishes:
                    check(total % size == 0, "uniform multiset divisibility")
                cases += 1
    return cases


def actual_frames():
    fixture = json.loads((ROOT / "research/precision-state-frontier/FIXTURE.json").read_text())
    columns = fixture["mode_columns"]
    basis = load_basis(ROOT)
    check(all(sum(columns[k][i] for i in LAMBDA) & 1 for k in range(8)),
          "lambda M is the weight-eight codeword modulo two")
    check(all(v[i] == 0 for v in basis for i in E), "E kills lifts")
    indices = (0, 1, 2, 3, PERIOD - 1, PERIOD // 2) + tuple((1 << i) - 1 for i in range(D))
    samples = []
    for index in indices:
        v = frame_vector(index, basis)
        following = frame_vector((index + 1) % PERIOD, basis)
        delta = tuple(x - y for x, y in zip(v, following))
        check(delta in basis or tuple(-x for x in delta) in basis, "one-lift transition")
        state = tuple((17 * i + index) % 43 - 21 for i in range(N))
        changed = apply_frame(v, state)
        check(apply_frame(v, changed, -1) == state, "integer frame inverse")
        check(apply_frame(delta, changed) == apply_frame(v, apply_frame(following, changed, -1)),
              "literal transition composition")
        check(all(sum(columns[k][i] * v[i] for i in range(N)) == 0 for k in range(8)),
              "mode preservation of constructed frame")
        samples.append(sum((x & 1) << i for i, x in enumerate(v)))
    mode_vectors = [sum((x & 1) << i for i, x in enumerate(col)) for col in columns]
    check(rank(samples + mode_vectors) == 104, "rank-one cycle spans all 104 dimensions")
    return len(indices)


def rejection_controls():
    basis = load_basis(ROOT)
    rejected = 0
    for index in (-1, PERIOD, True, 0.5):
        try:
            frame_vector(index, basis)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid index accepted")
    try:
        frame_vector(0, basis[:-1])
    except ValueError:
        rejected += 1
    else:
        raise ValueError("invalid basis accepted")
    for state, sign in (((0,) * 111, 1), ((0,) * N, 0), ((1 << 4097,) * N, 1)):
        try:
            apply_frame((0,) * N, state, sign)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid action accepted")
    return rejected


def main():
    sources = json.loads((HERE / "SOURCES.json").read_text())["files"]
    check(len(sources) <= 16, "source inventory bound")
    hashes = {}
    for source in sources:
        if source["usage"] == "input":
            data = (ROOT / source["path"]).read_bytes()
            digest = hashlib.sha256(data).hexdigest()
            check(digest == source["sha256"], "source hash: " + source["path"])
            hashes[source["path"]] = digest
    cycles, characters = finite_cycles()
    maps, equalities = arbitrary_map_census()
    output = {"cycles": cycles, "cycle_characters": characters,
              "spectrum_rejection_controls": cycles,
              "arbitrary_map_sequences": maps, "equality_sequences": equalities,
              "fourier_multisets": fourier_checks(), "integer_frame_samples": actual_frames(),
              "rejection_controls": rejection_controls(), "sha256": hashes}
    entries = sorted(HERE.iterdir())
    check(len(entries) <= 16, "receipt inventory bound")
    for path in entries:
        if path.is_file():
            hashes[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    print(json.dumps(output, sort_keys=True))
    print("PASS_REFINED_RECOVERY_BALANCED_CYCLE")


if __name__ == "__main__":
    main()
