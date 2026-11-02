"""Finite corroboration of the separated circular Schur ordering theorem."""

from fractions import Fraction
from hashlib import sha256
from itertools import permutations
import json
from pathlib import Path


MAX_N = 256


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def runs(n, mask):
    """Maximal cyclic runs, beginning immediately after an absent vertex."""
    start = next(i for i in range(n) if mask >> i & 1 and not mask >> ((i - 1) % n) & 1)
    result = []
    current = []
    for offset in range(n):
        i = (start + offset) % n
        if mask >> i & 1:
            current.append(i)
        elif current:
            result.append(tuple(current))
            current = []
    if current:
        result.append(tuple(current))
    require(sum(map(len, result)) == mask.bit_count(), "run partition")
    return tuple(result)


def validate(n, w, mask):
    if type(n) is not int or not 3 <= n <= MAX_N:
        raise ValueError("cycle size outside verifier capacity")
    if type(w) is not int or not 1 <= w <= n // 2:
        raise ValueError("invalid radius")
    if type(mask) is not int or not 0 < mask < (1 << n) - 1:
        raise ValueError("survivors must be a nonempty proper subset")
    blocks = runs(n, mask)
    if len(blocks) < 2 or min(map(len, blocks)) < w:
        raise ValueError("at least two surviving runs, each of length at least w, required")
    return blocks


def circle_graph(n, w):
    return [sum(1 << j for j in range(n) if i != j and min((i - j) % n, (j - i) % n) <= w)
            for i in range(n)]


def fill_graph(n, w, survivors):
    """Literal vertex elimination; no component or rim formula is used."""
    graph = circle_graph(n, w)
    active = (1 << n) - 1
    for k in range(n):
        if survivors >> k & 1:
            continue
        neighbors = graph[k] & active & ~(1 << k)
        for i in range(n):
            if neighbors >> i & 1:
                graph[i] |= neighbors & ~(1 << i)
        active &= ~(1 << k)
    return tuple(graph[i] & survivors if survivors >> i & 1 else 0 for i in range(n))


def rim_graph(n, w, survivors):
    """Original survivor edges plus the neighborhood clique of each deleted arc."""
    original = circle_graph(n, w)
    graph = [row & survivors if survivors >> i & 1 else 0 for i, row in enumerate(original)]
    for arc in runs(n, ((1 << n) - 1) ^ survivors):
        touching = 0
        for i in arc:
            touching |= original[i] & survivors
        require(touching.bit_count() <= 2 * w, "rim size")
        for i in range(n):
            if touching >> i & 1:
                graph[i] |= touching & ~(1 << i)
    return tuple(graph)


def fold(items):
    return tuple(items[i // 2] if i % 2 == 0 else items[-1 - i // 2] for i in range(len(items)))


def bandwidth(graph, order):
    positions = {v: i for i, v in enumerate(order)}
    require(len(positions) == len(order), "repeated order vertex")
    return max((abs(positions[i] - positions[j]) for i in order for j in order
                if graph[i] >> j & 1), default=0)


def negative_host(n, w):
    graph = circle_graph(n, w)
    return [[Fraction(1) if i == j else Fraction(-1, 4 * w) if graph[i] >> j & 1 else Fraction(0)
             for j in range(n)] for i in range(n)]


def schur_support(matrix, survivors):
    """Exact scalar Schur elimination, independent of the graph routines."""
    n = len(matrix)
    require(n <= 9 and all(len(row) == n for row in matrix), "rational matrix capacity")
    a = [row[:] for row in matrix]
    active = list(range(n))
    for k in range(n):
        if survivors >> k & 1:
            continue
        pivot = a[k][k]
        if not pivot:
            raise ArithmeticError("zero scalar pivot")
        remaining = [i for i in active if i != k]
        for i in remaining:
            for j in remaining:
                a[i][j] -= a[i][k] * a[k][j] / pivot
        active = remaining
    return tuple(sum(1 << j for j in active if i != j and a[i][j]) if i in active else 0
                 for i in range(n))


def layout_checks():
    graphs = rational = 0
    for n in range(4, 13):
        for w in range(1, min(3, n // 2) + 1):
            for mask in range(1, (1 << n) - 1):
                blocks = runs(n, mask)
                if len(blocks) < 2 or min(map(len, blocks)) < w:
                    continue
                validate(n, w, mask)
                graph = fill_graph(n, w, mask)
                require(graph == rim_graph(n, w, mask), "arc support versus literal elimination")
                ids = tuple(i for i in range(n) if mask >> i & 1)
                r = 2 * w - 1
                for i, a in enumerate(ids):
                    for j, b in enumerate(ids):
                        if graph[a] >> b & 1:
                            require(min((i - j) % len(ids), (j - i) % len(ids)) <= r,
                                    "compressed circular radius")
                require(bandwidth(graph, fold(ids)) <= min(len(ids) - 1, 4 * w - 2), "folded upper bound")
                graphs += 1
                if n <= 9:
                    actual = schur_support(negative_host(n, w), mask)
                    require(actual == graph, "exact negative-host support")
                    rational += 1
    return {"separated_layouts": graphs, "exact_rational_layouts": rational}


def necklace_graph(t, w):
    return tuple(sum(1 << j for j in range(t * w) if i != j and
                     (i // w == j // w or (i // w - j // w) % t in (1, t - 1)))
                 for i in range(t * w))


def necklace_checks():
    constructions = orders = brute_cases = 0
    for t in range(3, 21):
        for w in range(1, 9):
            graph = necklace_graph(t, w)
            order = tuple(v for b in fold(tuple(range(t))) for v in range(b * w, (b + 1) * w))
            require(bandwidth(graph, order) == 3 * w - 1, "necklace attaining order")
            require(min(row.bit_count() for row in graph) == 3 * w - 1, "necklace degree lower bound")
            n = 0
            ids = []
            for block in range(t):
                ids.extend(range(n, n + w))
                n += w + 1 + block % 3
            mask = sum(1 << i for i in ids)
            validate(n, w, mask)
            filled = fill_graph(n, w, mask)
            compressed = tuple(sum(1 << j for j, b in enumerate(ids) if filled[a] >> b & 1) for a in ids)
            require(compressed == graph, "literal necklace elimination")
            constructions += 1
            if t * w <= 8:
                best = t * w
                for candidate in permutations(range(t * w)):
                    best = min(best, bandwidth(graph, candidate))
                    orders += 1
                require(best == 3 * w - 1, "complete permutation optimum")
                brute_cases += 1
    return {"necklace_layouts": constructions, "exhaustive_necklace_cases": brute_cases,
            "permutations": orders}


def rejection_checks():
    invalid = [(2, 1, 1), (257, 1, 1), (6, 0, 5), (6, 4, 5), (6, 1, 0),
               (6, 1, 63), (6, 1, 64), (True, 1, 5), (6, 1, 7), (16, 2, 0x5555)]
    for args in invalid:
        try:
            validate(*args)
        except ValueError:
            continue
        raise AssertionError(f"invalid layout accepted: {args}")
    # Without the separation premise, this literal graph exceeds 4w-2.
    graph = fill_graph(16, 2, 0x5555)
    ids = tuple(range(0, 16, 2))
    degree = min(graph[i].bit_count() for i in ids)
    require(degree == 7 and degree > 4 * 2 - 2, "separation control must refute the upper bound")
    graph = necklace_graph(4, 2)
    require(min(row.bit_count() for row in graph) > 2 * 2, "one-arc constant must fail")
    require(bandwidth(graph, tuple(range(8))) > 5, "unfolded order must fail")
    matrix = negative_host(6, 1)
    mask = (1 << 6) - 1 - (1 << 0) - (1 << 3)
    matrix[1][0] = Fraction(0)
    require(schur_support(matrix, mask) != fill_graph(6, 1, mask), "missing-coupling control")
    matrix = negative_host(6, 1)
    matrix[0][0] = Fraction(0)
    try:
        schur_support(matrix, mask)
    except ArithmeticError:
        pass
    else:
        raise AssertionError("zero pivot accepted")
    return {"invalid_input_rejections": len(invalid), "semantic_controls": 5}


def main():
    result = {"status": "PASS_SEPARATED_CYCLE_SCHUR", "claim_type": "scoped proof; finite corroboration"}
    result.update(layout_checks())
    result.update(necklace_checks())
    result.update(rejection_checks())
    package = Path(__file__).resolve().parent
    names = ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    result["sha256"] = {name: sha256((package / name).read_bytes()).hexdigest() for name in names}
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
