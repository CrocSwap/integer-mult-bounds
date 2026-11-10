"""Exact check of the degree-three star-pattern floors.  Standard library only.

For each listed graph Gamma on n points the script proves, in exact rational
arithmetic, that every function f on vertex sets of G_Gamma satisfying the
block-pattern rank laws (README, section 2) has f(empty) >= n + 1, and that an
integer pattern of rank at most n + 1 exists.  It then runs rejecting controls.
"""
import json
import sys
from fractions import Fraction
from itertools import combinations, permutations
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import star_graphs as sg  # noqa: E402

GRAPHS = {
    "wheel-W4": (5, [[0, 1], [0, 2], [0, 3], [0, 4], [1, 2], [2, 3], [3, 4], [4, 1]]),
    "K33": (6, [[a, b] for a in range(3) for b in range(3, 6)]),
}
CYCLE_LENGTHS = (3, 4, 5, 6)


def degrees(n, edges):
    """Degree of every point of Gamma."""
    count = [0] * n
    for a, b in edges:
        count[a] += 1
        count[b] += 1
    return count


def has_k4(n, edges):
    """True if four points of Gamma are pairwise joined."""
    joined = {frozenset(e) for e in edges}
    for quad in combinations(range(n), 4):
        if all(frozenset(p) in joined for p in combinations(quad, 2)):
            return True
    return False


def rejected(action):
    """True if action raises CheckError."""
    try:
        action()
    except sg.CheckError:
        return True
    return False


def check_graph(name, record):
    """Lower bound, upper bound and hypotheses for one graph; return counts."""
    n, edges = GRAPHS[name]
    sg.require(record["points"] == n and record["edges"] == edges, name)
    certificate = record["certificate"]
    sg.require(min(degrees(n, edges)) == 3, (name, "minimum degree"))
    sg.require(not has_k4(n, edges), (name, "contains K4"))
    bound = sg.certified_bound(n, edges, certificate)
    sg.require(bound == n + 1, (name, bound))
    sg.require(Fraction(record["lower_bound"]) == bound, (name, "stored bound"))
    nbrs = sg.neighbour_masks(n, edges)
    sg.require(sg.is_pattern(sg.gram_pattern(n, edges), nbrs), (name, "Gram pattern"))
    return n, len(nbrs), len(sg.vertex_permutations(n, edges)), len(certificate)


def certificate_controls(name, record):
    """Each damaged certificate or graph must be rejected; return the count."""
    n, edges = GRAPHS[name]
    certificate = record["certificate"]
    first_entry, first_weight = certificate[0]
    doubled = [[first_entry, str(2 * Fraction(first_weight))]] + certificate[1:]
    negated = [[first_entry, str(-Fraction(first_weight))]] + certificate[1:]
    joined = {frozenset(e) for e in edges}
    spare = next(list(p) for p in combinations(range(n), 2) if frozenset(p) not in joined)
    damaged = [
        lambda: sg.certified_bound(n, edges, certificate[1:]),
        lambda: sg.certified_bound(n, edges, certificate[:-1]),
        lambda: sg.certified_bound(n, edges, doubled),
        lambda: sg.certified_bound(n, edges, negated),
        lambda: sg.certified_bound(n, edges[:-1], certificate),
        lambda: sg.certified_bound(n, edges[:-1] + [spare], certificate),
    ]
    for index, action in enumerate(damaged):
        sg.require(rejected(action), (name, "control accepted", index))
    return len(damaged)


def pattern_control(name):
    """Dropping one adjacency between disjoint pairs must break the Gram pattern."""
    n, edges = GRAPHS[name]
    nbrs = sg.neighbour_masks(n, edges)
    matrix = sg.gram_pattern(n, edges)
    for a in range(n, len(nbrs)):
        for b in range(a + 1, len(nbrs)):
            if (nbrs[a] >> b) & 1:
                cut = list(nbrs)
                cut[a] &= ~(1 << b)
                cut[b] &= ~(1 << a)
                sg.require(not sg.is_pattern(matrix, cut), (name, "pattern control"))
                return 1
    raise sg.CheckError((name, "no adjacent pairs"))


def cycle_pattern_rank(length):
    """Rank-n integer pattern on G_{C_n}: one point-pair clique per point."""
    edges = [[i, (i + 1) % length] for i in range(length)]
    nbrs = sg.neighbour_masks(length, edges)
    sg.require(min(degrees(length, edges)) == 2, length)
    total = len(nbrs)
    matrix = [[0] * total for _ in range(total)]
    for c in range(length):
        clique = (c, length + c)
        sg.require((nbrs[c] >> (length + c)) & 1, (length, c))
        for a in clique:
            for b in clique:
                matrix[a][b] += 1
    sg.require(sg.is_pattern(matrix, nbrs), (length, "cycle pattern"))
    points = range(length)
    sg.require(all(not (nbrs[a] >> b) & 1 for a in points for b in points), length)
    return length


def contains(n, joined, pattern_points, pattern_edges):
    """True if the pattern graph embeds in the graph with edge set joined."""
    for chosen in permutations(range(n), pattern_points):
        if all(frozenset((chosen[a], chosen[b])) in joined for a, b in pattern_edges):
            return True
    return False


def small_graph_census(n):
    """Labelled graphs on n points of minimum degree >= 3: all contain K4 or W4.

    Returns (number of such graphs, number containing K4, number containing W4).
    """
    slots = list(combinations(range(n), 2))
    wheel_points, wheel_edges = GRAPHS["wheel-W4"]
    k4_edges = list(combinations(range(4), 2))
    found = with_k4 = with_wheel = 0
    for code in range(1 << len(slots)):
        edges = [slots[i] for i in range(len(slots)) if (code >> i) & 1]
        if min(degrees(n, edges)) < 3:
            continue
        joined = {frozenset(e) for e in edges}
        k4 = contains(n, joined, 4, k4_edges)
        wheel = n >= wheel_points and contains(n, joined, wheel_points, wheel_edges)
        sg.require(k4 or wheel, (n, edges))
        found += 1
        with_k4 += k4
        with_wheel += wheel
    return found, with_k4, with_wheel


def main():
    data = json.loads((HERE / "certificates.json").read_text())
    sg.require(data["schema_version"] == 1, "schema")
    records = {record["name"]: record for record in data["graphs"]}
    sg.require(set(records) == set(GRAPHS), sorted(records))
    controls = 0
    for name in GRAPHS:
        n, total, group, entries = check_graph(name, records[name])
        controls += certificate_controls(name, records[name]) + pattern_control(name)
        print(f"PASS {name}: n={n} vertices={total} automorphisms={group} "
              f"entries={entries} lower={n + 1} upper={n + 1}")
    cycles = [cycle_pattern_rank(length) for length in CYCLE_LENGTHS]
    print(f"PASS cycles {cycles}: rank-n patterns at minimum degree 2")
    census = {n: small_graph_census(n) for n in (4, 5)}
    sg.require(census == {4: (1, 1, 0), 5: (26, 11, 26)}, census)
    print(f"PASS census (graphs, with K4, with W4) of minimum degree >= 3: {census}")
    print(f"PASS_STAR_PATTERN_DEGREE_THREE_FLOOR graphs={len(GRAPHS)} "
          f"controls={controls} cycles={len(cycles)} census={census[4][0] + census[5][0]} "
          f"no_new_kappa")


if __name__ == "__main__":
    main()
