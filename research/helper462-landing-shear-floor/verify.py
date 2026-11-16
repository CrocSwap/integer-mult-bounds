#!/usr/bin/env python3
"""Odd-denominator shear length of the helper-462 landing permutation.

The prose argument is PROOF.md. This script checks the finite parts: the pinned
matcher and cleanup, the explicit 18-shear word, the 16-row river-parity table,
the link/middle/cut split of that word, and failure controls. It also reruns
the same one-step predicates on every CNOT in GL(3, F2). That census is a
control on the predicates, not the proof for n = 8.

Standard library only. No new kappa.
"""

from collections import Counter
from fractions import Fraction
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "research/bit-completed-backend-api/science/RESULT.json"
SELECTED = ROOT / "certificates/selected-result.json"
N = 8

# Seven integer shears and five scales from the open 25-shear route. They take
# the pinned matcher to P. The halves are outside the odd-denominator class;
# this package does not treat the cleanup as a word for P.
CLEANUP = (
    ("add", 2, 1, Fraction(-1)),
    ("scale", 2, Fraction(1, 2)),
    ("add", 1, 2, Fraction(1)),
    ("add", 4, 7, Fraction(1)),
    ("scale", 4, Fraction(1, 2)),
    ("add", 7, 4, Fraction(-1)),
    ("scale", 7, Fraction(-1)),
    ("add", 1, 7, Fraction(-1)),
    ("add", 5, 1, Fraction(-1)),
    ("scale", 5, Fraction(1, 2)),
    ("add", 6, 1, Fraction(-1)),
    ("scale", 6, Fraction(1, 2)),
)
LANDING = (4, 3, 5, 6, 7, 0, 1, 2)
EXCHANGES = ((0, 5), (1, 6), (2, 7), (3, 6), (4, 5), (5, 7))


def need(condition, message):
    if not condition:
        raise SystemExit("FAIL: " + message)


def eye(size=N):
    return [[Fraction(int(row == column)) for column in range(size)] for row in range(size)]


def rows_of(raw):
    return [[Fraction(entry) for entry in row] for row in raw]


def apply(op, matrix):
    out = [row[:] for row in matrix]
    kind = op[0]
    if kind == "add":
        target, source, coefficient = op[1:]
        need(target != source and coefficient != 0, "shear letter is not elementary")
        for column in range(len(out)):
            out[target][column] += coefficient * out[source][column]
    elif kind == "scale":
        target, coefficient = op[1:]
        need(coefficient not in (0, 1), "scale letter is not a non-identity scale")
        for column in range(len(out)):
            out[target][column] *= coefficient
    elif kind == "swap":
        left, right = op[1], op[2]
        out[left], out[right] = out[right], out[left]
    else:
        raise AssertionError(kind)
    return out


def product(ops, matrix=None):
    if matrix is None:
        matrix = eye()
    for op in ops:
        matrix = apply(op, matrix)
    return matrix


def determinant(matrix):
    size = len(matrix)
    work = [row[:] for row in matrix]
    det = Fraction(1)
    sign = 1
    for column in range(size):
        pivot = next((row for row in range(column, size) if work[row][column] != 0), None)
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            sign = -sign
        pivot_value = work[column][column]
        det *= pivot_value
        for row in range(column + 1, size):
            if work[row][column] == 0:
                continue
            factor = work[row][column] / pivot_value
            for index in range(column, size):
                work[row][index] -= factor * work[column][index]
    return sign * det


def odd_denominator(value):
    """True when value is a rational whose lowest-terms denominator is odd."""
    return value.denominator % 2 == 1


def content_swap(left, right):
    """Exchange two row contents. Three shears send (A, B) to (B, -A)."""
    return (
        ("add", left, right, Fraction(1)),
        ("add", right, left, Fraction(-1)),
        ("add", left, right, Fraction(1)),
        ("scale", right, Fraction(-1)),
    )


def invert(op):
    if op[0] == "add":
        return ("add", op[1], op[2], -op[3])
    if op[0] == "scale":
        return ("scale", op[1], 1 / op[2])
    raise AssertionError(op)


def landing_reduction():
    ops = []
    for left, right in EXCHANGES:
        ops.extend(content_swap(left, right))
    return ops


def landing_word():
    """Swap-free word in the odd-denominator alphabet whose product is P."""
    return [invert(op) for op in reversed(landing_reduction())]


def basis_column(row):
    nonzero = [(column, value) for column, value in enumerate(row) if value != 0]
    need(len(nonzero) == 1 and nonzero[0][1] == 1, "row is not a positive basis vector")
    return nonzero[0][0]


def permutation_matrix(images):
    size = len(images)
    need(sorted(images) == list(range(size)), "images are not a permutation")
    return [[Fraction(int(images[row] == column)) for column in range(size)] for row in range(size)]


def cycle_count(images):
    size = len(images)
    seen = [False] * size
    count = 0
    for start in range(size):
        if seen[start]:
            continue
        count += 1
        cursor = start
        while not seen[cursor]:
            seen[cursor] = True
            cursor = images[cursor]
    return count


def mod2(matrix):
    return [[int(entry) % 2 for entry in row] for row in matrix]


def cnot(matrix, target, source):
    out = [row[:] for row in matrix]
    for column in range(len(out)):
        out[target][column] ^= matrix[source][column]
    return out


def f2_word():
    """The 18 odd shears of the landing word, read as CNOTs."""
    letters = []
    for op in landing_word():
        if op[0] != "add":
            continue
        need(odd_denominator(op[3]) and op[3].numerator % 2 == 1, "landing shear is not odd")
        letters.append((op[1], op[2]))
    return letters


def apply_f2(letters, matrix):
    current = [row[:] for row in matrix]
    for target, source in letters:
        current = cnot(current, target, source)
    return current


def components(vertex_count, edges):
    parent = list(range(vertex_count))

    def find(vertex):
        while parent[vertex] != vertex:
            parent[vertex] = parent[parent[vertex]]
            vertex = parent[vertex]
        return vertex

    for left, right in edges:
        root_left, root_right = find(left), find(right)
        if root_left != root_right:
            parent[root_left] = root_right
    return len({find(vertex) for vertex in range(vertex_count)})


def graph_counts(matrix):
    size = len(matrix)
    undirected = []
    bipartite = []
    for row in range(size):
        for column in range(size):
            if matrix[row][column]:
                bipartite.append((row, size + column))
            if column > row and (matrix[row][column] or matrix[column][row]):
                undirected.append((row, column))
    return components(size, undirected), components(2 * size, bipartite)


def rivers(matrix):
    size = len(matrix)
    found = []

    def walk(used, images, row):
        if row == size:
            found.append(tuple(images))
            return
        for column in range(size):
            if not used[column] and matrix[row][column]:
                used[column] = True
                images.append(column)
                walk(used, images, row + 1)
                images.pop()
                used[column] = False

    walk([False] * size, [], 0)
    return set(found)


def gate_kind(before, after):
    vertices_before, edges_before = graph_counts(before)
    vertices_after, edges_after = graph_counts(after)
    labels = set()
    if vertices_after < vertices_before:
        labels.add("link")
    if edges_after > edges_before:
        labels.add("cut")
    if rivers(before) != rivers(after):
        labels.add("middle")
    return labels, (vertices_before, edges_before, vertices_after, edges_after)


def parity_holds(bits):
    """One transposition pair, assuming the other rows already match."""
    source_source, source_target, target_source, target_target = bits
    before = int(source_source and target_target) + int(source_target and target_source)
    after = int(source_source and ((target_target + source_target) % 2 == 1))
    after += int(source_target and ((target_source + source_source) % 2 == 1))
    return before % 2 == after % 2


def check_parity_table():
    failures = []
    for pattern in range(16):
        bits = ((pattern >> 3) & 1, (pattern >> 2) & 1, (pattern >> 1) & 1, pattern & 1)
        if not parity_holds(bits):
            failures.append(bits)
    need(failures == [], "river parity failed on %s" % (failures,))


def classify_matrix(factor):
    matrix = rows_of(factor)
    diffs = []
    for row in range(N):
        for column in range(N):
            if matrix[row][column] != int(row == column):
                diffs.append((row, column, matrix[row][column]))
    if len(diffs) == 1:
        row, column, value = diffs[0]
        if row == column:
            return ("scale", row, value)
        return ("add", row, column, value)
    need(len(diffs) == 4, "published factor is not elementary")
    off = [(row, column) for row, column, _value in diffs if row != column]
    need(len(off) == 2, "published factor is not a swap")
    left_row, left_column = off[0]
    right_row, right_column = off[1]
    need(left_row == right_column and left_column == right_row, "published factor is not a swap")
    need(matrix[left_row][left_column] == 1 and matrix[right_row][right_column] == 1, "swap entries")
    need(matrix[left_row][left_row] == 0 and matrix[right_row][right_row] == 0, "swap diagonal")
    return ("swap", left_row, right_row)


def check_published(matcher, factors):
    word = [classify_matrix(factor) for factor in factors]
    counts = Counter(op[0] for op in word)
    need(counts == Counter({"swap": 5, "scale": 5, "add": 14}),
         "published elimination counts changed")
    # These factors are the elimination letters. Reversing them and applying
    # the letters to I multiplies back to S, as in the predecessor verifiers.
    need(product(list(reversed(word))) == matcher,
         "published factors do not multiply to the matcher")


def check_gl3_predicates():
    """Every CNOT on GL(3, F2) obeys the one-step disjointness lemmas.

    This is a finite control on the classifier. PROOF.md proves the same
    lemmas for every n, including n = 8, without this census.
    """
    identity = tuple(tuple(int(row == column) for column in range(3)) for row in range(3))
    generators = [(target, source) for target in range(3) for source in range(3) if target != source]
    seen = {identity}
    layer = [identity]
    while layer:
        nxt = []
        for matrix in layer:
            rows = [list(row) for row in matrix]
            for target, source in generators:
                image = tuple(
                    tuple(rows[row][column] ^ (rows[source][column] if row == target else 0)
                          for column in range(3))
                    for row in range(3)
                )
                if image not in seen:
                    seen.add(image)
                    nxt.append(image)
        layer = nxt
    need(len(seen) == 168, "GL(3, F2) census changed size")
    for matrix in seen:
        rows = [list(row) for row in matrix]
        for target, source in generators:
            image = [row[:] for row in rows]
            for column in range(3):
                image[target][column] ^= rows[source][column]
            labels, counts = gate_kind(rows, image)
            vertices_before, edges_before, vertices_after, edges_after = counts
            need(abs(vertices_after - vertices_before) <= 1, "GL(3) vertex jump")
            need(abs(edges_after - edges_before) <= 1, "GL(3) edge jump")
            if vertices_after < vertices_before:
                need(edges_after == edges_before - 1, "GL(3) link did not drop e")
            if edges_before != edges_after:
                need("middle" not in labels, "GL(3) edge change moved rivers")
            need(len(labels) <= 1, "GL(3) labels overlapped: %s" % (labels,))


def middle_components(pairs):
    return components(N, pairs)


def check_word_split(letters, target):
    current = [[int(row == column) for column in range(N)] for row in range(N)]
    counts = Counter()
    middle_pairs = []
    vertex_trace = [graph_counts(current)[0]]
    edge_trace = [graph_counts(current)[1]]
    for target_row, source_row in letters:
        nxt = cnot(current, target_row, source_row)
        labels, _counts = gate_kind(current, nxt)
        need(len(labels) == 1, "explicit gate was not exactly one class: %s" % (labels,))
        kind = next(iter(labels))
        counts[kind] += 1
        if kind == "middle":
            middle_pairs.append((min(target_row, source_row), max(target_row, source_row)))
        vertices_before, edges_before = graph_counts(current)
        vertices_after, edges_after = graph_counts(nxt)
        if kind == "link":
            need(vertices_after == vertices_before - 1 and edges_after == edges_before - 1,
                 "link step did not drop both counts")
        elif kind == "cut":
            need(edges_after == edges_before + 1 and vertices_after >= vertices_before,
                 "cut step did not raise the edge count")
        else:
            need(vertices_after == vertices_before and edges_after == edges_before,
                 "middle step changed a component count")
        current = nxt
        vertex_trace.append(vertices_after)
        edge_trace.append(edges_after)
    need(current == target, "classified word did not finish at P")
    need(counts == Counter({"link": 6, "middle": 6, "cut": 6}), "split changed: %s" % dict(counts))
    need(vertex_trace[0] == 8 and vertex_trace[-1] == 2, "vertex trace endpoints")
    need(edge_trace[0] == 8 and edge_trace[-1] == 8, "edge trace endpoints")
    decreases = sum(1 for earlier, later in zip(vertex_trace, vertex_trace[1:]) if later < earlier)
    increases = sum(1 for earlier, later in zip(edge_trace, edge_trace[1:]) if later > earlier)
    need(decreases == 6 and increases == 6, "trace counts")
    unique_pairs = set(middle_pairs)
    need(len(unique_pairs) == 6, "middle gates repeated an edge")
    need(middle_components(unique_pairs) == 2, "middle graph has the wrong number of components")
    # sigma preserves each component, so it lies in the group generated by them.
    parent = list(range(N))

    def find(vertex):
        while parent[vertex] != vertex:
            parent[vertex] = parent[parent[vertex]]
            vertex = parent[vertex]
        return vertex

    for left, right in unique_pairs:
        root_left, root_right = find(left), find(right)
        if root_left != root_right:
            parent[root_left] = root_right
    for row, image in enumerate(LANDING):
        need(find(row) == find(image), "landing permutation leaves a middle component")


def main():
    selected = json.loads(SELECTED.read_text(encoding="utf-8"))
    need(selected["kappa"] == "781451/250000000", "selected kappa pin changed")
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    matcher = rows_of(payload["matcher"])
    need(determinant(matcher) == Fraction(-16), "pinned determinant")
    check_published(matcher, payload["right_route_factors"])

    landing = permutation_matrix(LANDING)
    need(determinant(landing) == 1, "landing determinant")
    need(cycle_count(LANDING) == 2, "landing cycle count")
    need(graph_counts(mod2(landing)) == (2, 8), "landing graph counts")
    need(graph_counts(mod2(eye())) == (8, 8), "identity graph counts")
    need(rivers(mod2(landing)) == {LANDING}, "landing rivers")
    need(rivers(mod2(eye())) == {tuple(range(N))}, "identity rivers")

    current = [row[:] for row in matcher]
    for op in CLEANUP:
        current = apply(op, current)
    need(current == landing, "cleanup did not reach the landing permutation")
    cleanup_shears = [op for op in CLEANUP if op[0] == "add"]
    cleanup_scales = [op for op in CLEANUP if op[0] == "scale"]
    need(len(cleanup_shears) == 7 and len(cleanup_scales) == 5, "cleanup shape")
    need(all(op[3] in (Fraction(-1), Fraction(1)) for op in cleanup_shears),
         "cleanup shear left the integer units")
    need(any(not odd_denominator(op[2]) for op in cleanup_scales),
         "cleanup unexpectedly stayed inside the odd-denominator scale class")

    reduction = landing_reduction()
    need(product(reduction, [row[:] for row in landing]) == eye(),
         "landing reduction did not reach I")
    word = landing_word()
    counts = Counter(op[0] for op in word)
    need(counts == Counter({"add": 18, "scale": 6}), "landing word shape %s" % dict(counts))
    need(product(word) == landing, "landing word does not multiply to P")
    scales = [op[2] for op in word if op[0] == "scale"]
    shears = [op for op in word if op[0] == "add"]
    need(scales == [Fraction(-1)] * 6, "landing scales are not six factors of -1")
    need(all(odd_denominator(op[3]) and op[3].numerator % 2 == 1 for op in shears),
         "landing shear left the odd-numerator class")
    need(all(odd_denominator(value) and value.numerator % 2 == 1 for value in scales),
         "landing scale left the odd-denominator units")
    # Unreduced concatenation of the recorded blocks, before any cross-boundary
    # rewrite. This is a compatibility control, not a claim that 25 is minimal.
    need(len(cleanup_shears) + len(shears) == 25, "block shear total")
    need(product(list(CLEANUP) + reduction, [row[:] for row in matcher]) == eye(),
         "concatenated blocks did not reduce S")

    letters = f2_word()
    need(len(letters) == 18, "F2 word length")
    need(apply_f2(letters, mod2(eye())) == mod2(landing), "F2 word missed P")
    for index in range(len(letters)):
        shorter = letters[:index] + letters[index + 1:]
        need(apply_f2(shorter, mod2(eye())) != mod2(landing),
             "deleting CNOT %s still realized P" % (index,))
        mutated = list(word)
        op = mutated[index_of_shear(word, index)]
        mutated[index_of_shear(word, index)] = ("add", op[1], op[2], op[3] * 2)
        need(product(mutated) != landing, "an even shear replacement still realized P")
    scale_at = next(index for index, op in enumerate(word) if op[0] == "scale")
    scaled = list(word)
    scaled[scale_at] = ("scale", word[scale_at][1], Fraction(-3))
    need(product(scaled) != landing, "replacing one scale by -3 still realized P")
    need(product([]) == eye() and determinant(eye()) == 1, "identity control")

    check_parity_table()
    check_word_split(letters, mod2(landing))
    check_gl3_predicates()

    print(
        "PASS_HELPER462_LANDING_ODD_DENOMINATOR_SHEARS"
        " shears=18 scales=6 odd_denominator=1 f2_length=18"
        " link=6 middle=6 cut=6"
        " unreduced_cleanup_plus_landing_shears=25"
        " minimum_25_claimed=0 dyadic_coefficients_open=1"
        " other_routes_open=1"
        " gl3_predicate_control=1"
        " selected_kappa=781451/250000000 no_new_kappa=1"
    )


def index_of_shear(word, shear_index):
    seen = 0
    for index, op in enumerate(word):
        if op[0] != "add":
            continue
        if seen == shear_index:
            return index
        seen += 1
    raise AssertionError(shear_index)


if __name__ == "__main__":
    main()
