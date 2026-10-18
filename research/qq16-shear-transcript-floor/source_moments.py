"""Independent exact QQ16 source-geometry and fourth-moment calculation.

Apache-2.0. Prepared with OpenAI Codex assistance. The fourth-moment
argument and spectral polynomial are credited to commdata2338, PR #2189,
following Nick Petalas's PR #2181 and the retained Ali Romman QQ16 work.
This module independently implements the arithmetic; it imports none of
those checkers. Native root coordinates are reconstructed from the credited
icekylinx / DreamingOfClouds / PR635 source lineage described below.

This is a text-source replay. The constructor and transport define R; the
native verifier defines the owner chart swaps. Equality to the compressed
QQ16 packet, its map registry, scalar programs, phases, and complete
controller execution is NOT checked here. The package driver pins the
source files. The interpretation as the retained QQ16 operators inherits
those source definitions and the witness's native-interface interpretation.
"""

from copy import deepcopy
from fractions import Fraction as Q
from itertools import groupby, permutations, product
import json
from pathlib import Path


PROTOTYPE = "research/direct-delivery504-global/inputs/hamming/PROTOTYPE.json"
PHASES = ("research/direct-delivery504-global/inputs/data-base/work/"
          "complex-nine-native/DATA-PHASES.json")
WITNESS = "research/joint-query/evidence/QQ16-SELECTED-WITNESS.json"
CONSTRUCTOR = "research/gauge44-slots-t16/construction/leaver/cgx_leaver.py"
TRANSPORT = ("research/complex-sw4-frame8/vendor/pr635/research/"
             "complex-571-cold14-st2/code/hpe_audit_and_transport.py")
NATIVE_DEFINITION = "research/joint-query/verify_native.py"
SOURCE_PATHS = (PROTOTYPE, PHASES, WITNESS, CONSTRUCTOR, TRANSPORT,
                NATIVE_DEFINITION)

AXES = 73
ACTIVE = 25
I73 = tuple(1 << i for i in range(AXES))
I25 = I73[:ACTIVE]


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def parity(value):
    return value.bit_count() & 1


def apply_columns(columns, vector):
    answer = 0
    while vector:
        bit = vector & -vector
        answer ^= columns[bit.bit_length() - 1]
        vector ^= bit
    return answer


def compose(left, right):
    """Literal binary matrix product, represented by complete columns."""
    return tuple(apply_columns(left, column) for column in right)


def transpose(columns):
    return tuple(sum(((column >> i) & 1) << j
                     for j, column in enumerate(columns))
                 for i in range(len(columns)))


def gram(columns, ports):
    return [[sum(columns[p][i] * columns[p][j] for p in ports)
             for j in range(8)] for i in range(8)]


def scalar_identity(value):
    return [[value * int(i == j) for j in range(8)] for i in range(8)]


def check_roots(columns, selected_a, selected_t, ordinary):
    need(len(columns) == 112 and all(len(c) == 8 for c in columns),
         "root dimensions")
    need(all(type(x) is int for c in columns for x in c), "integer roots")
    need(all(sum(x*x for x in c) == 4 for c in columns), "root norm four")
    need(gram(columns, range(112)) == scalar_identity(56), "full Gram 56I")
    need(gram(columns, selected_a) == scalar_identity(4), "A Gram 4I")
    need(gram(columns, selected_t) == scalar_identity(4), "T Gram 4I")
    need(gram(columns, ordinary) == scalar_identity(48), "ordinary Gram 48I")


def check_route(columns):
    need(len(columns) == AXES and all(type(c) is int and 0 <= c < 1 << AXES
                                      for c in columns), "73-column route")
    need(compose(transpose(columns), columns) == I73, "orthogonal route")
    need(compose(columns, columns) == I73, "involutive route")
    need(columns[ACTIVE:] == I73[ACTIVE:] and
         all(c < 1 << ACTIVE for c in columns[:ACTIVE]),
         "48 spectators fixed with no active mixing")


def chart_route(chart, stage):
    """Conjugate a coordinate swap by the full orthonormal chart.

    This implementation applies C S C^T to every standard basis vector.
    It does not use a predecessor's rank-one update implementation.
    In chart coordinates S exchanges positions 1..8 with the eight stage
    slots; stage zero is the identity.
    """
    if stage == 0:
        return I73
    first = 9 + 8 * (stage - 1)
    answer = []
    for axis in range(AXES):
        coordinates = sum(((column >> axis) & 1) << j
                          for j, column in enumerate(chart))
        for k in range(8):
            left, right = k + 1, first + k
            if ((coordinates >> left) ^ (coordinates >> right)) & 1:
                coordinates ^= (1 << left) | (1 << right)
        answer.append(apply_columns(chart, coordinates))
    return tuple(answer)


def source_geometry(root):
    root = Path(root)
    for relative in SOURCE_PATHS:
        need((root / relative).is_file(), "missing pinned source: " + relative)
    prototype = json.loads((root / PROTOTYPE).read_text())
    phases = json.loads((root / PHASES).read_text())
    witness = json.loads((root / WITNESS).read_text())
    old_ports, old_roots = prototype["binary_ports"], prototype["root_lines"]
    need(len(old_ports) == len(old_roots) == 120, "prototype inventory")
    need(old_roots[:8] == [[2 * int(i == j) for j in range(8)]
                          for i in range(8)], "removed eight coordinate axes")
    need(phases["m"] == AXES and phases["ports"] == 112, "phase dimensions")
    recipes = phases["recipes"]
    need(len(recipes) == 112, "all native ports")
    native_labels = [record["q"] for record in recipes]
    transformed = [p ^ (43 if parity(p & 43) else 0) for p in old_ports[8:]]
    need(sorted(transformed) == sorted(native_labels) and
         len(set(native_labels)) == 112, "native label permutation")
    columns = [old_roots[8 + transformed.index(q)] for q in native_labels]
    selected_a, selected_t, ordinary = (witness[k] for k in ("A", "T", "U"))
    need(len(selected_a) == len(selected_t) == 8 and len(ordinary) == 96,
         "QQ16 partition sizes")
    need(sorted(selected_a + selected_t + ordinary) == list(range(112)),
         "QQ16 partition is disjoint and exhaustive")
    need(ordinary == [p for p in range(112) if p not in selected_a + selected_t],
         "ordered ordinary ports")
    check_roots(columns, selected_a, selected_t, ordinary)
    all_routes = [[], [], []]
    for p, record in enumerate(recipes):
        need(record["port"] == p, "phase recipe order")
        chart = (record["q"], *record["idle_children"][0]["orthogonal_axes"][:8],
                 *I73[9:])
        need(len(chart) == AXES and all(type(x) is int and 0 < x < 512
                                       for x in chart[:9]), "nine-axis chart")
        need(compose(transpose(chart), chart) == I73, "orthonormal source chart")
        beta = sum((((c.bit_count() - 1) // 2) & 1) << j
                   for j, c in enumerate(chart[1:9]))
        lift = apply_columns(chart[1:9], beta)
        for stage in range(3):
            route = chart_route(chart, stage)
            check_route(route)
            entry = (record["q"] ^ lift) if stage else 0
            leave = (lift ^ (beta << (9 + 8*(stage - 1)))) if stage else 0
            need(record["stage_alignment"][stage] ==
                 {"entry_X": entry, "entry_Y": entry,
                  "exit_X": leave, "exit_Y": leave},
                 "source stage alignment")
            all_routes[stage].append(route)
    return columns, (selected_a, selected_t, ordinary), all_routes


def relative_routes(routes, ordinary, s, t):
    result = [compose(routes[s][p][:ACTIVE],
                      transpose(routes[t][p][:ACTIVE])) for p in ordinary]
    ordered = sorted(result)
    need(all(a != b for a, b in zip(ordered, ordered[1:])),
         "96 distinct relative routes")
    return result


def exact_table(relative):
    """Sort complete matrices: no digest participates in equality."""
    records = [(compose(a, transpose(b)), p, q)
               for p, a in enumerate(relative) for q, b in enumerate(relative)]
    records.sort()
    image = []
    identity_pairs = 0
    singleton_pairs = 0
    for matrix, fibre in groupby(records, key=lambda item: item[0]):
        pairs = [(p, q) for _, p, q in fibre]
        image.append(matrix)
        if matrix == I25:
            need(pairs == [(p, p) for p in range(96)], "identity fibre is diagonal")
            identity_pairs = len(pairs)
        else:
            need(len(pairs) == 1 and pairs[0][0] != pairs[0][1],
                 "nonidentity fibre is singleton")
            singleton_pairs += 1
    need(len(image) == 9121 and identity_pairs == 96 and singleton_pairs == 9120,
         "complete ordered-product census")
    return image


def intersection(left, right):
    """Exact merge intersection of sorted complete binary matrices."""
    i = j = 0
    common = []
    while i < len(left) and j < len(right):
        if left[i] == right[j]:
            common.append(left[i])
            i += 1
            j += 1
        elif left[i] < right[j]:
            i += 1
        else:
            j += 1
    return common


def cyclic_reduce(word):
    word = list(word)
    while len(word) > 1:
        duplicate = next((i for i in range(len(word))
                          if word[i] == word[(i+1) % len(word)]), None)
        if duplicate is None:
            return tuple(word)
        del word[duplicate]
    return tuple(word)


def trace_moments(columns, ordinary):
    dots_square = sum(sum(x*y for x, y in zip(columns[p], columns[q]))**2
                      for p in ordinary for q in ordinary)
    diagonal = sum(sum(x*x for x in columns[p])**2 for p in ordinary)
    need((dots_square, diagonal) == (18432, 1536), "root Gram contractions")
    identity_coefficient = 4 * 48
    identity_norm = 8 * identity_coefficient**2
    values = {
        "one_stage": Q(8),
        "two_stages": Q(diagonal, 48**2),
        "three_distinct": Q(96 * 4**3, 48**3),
        "alternating_two": Q(identity_norm + 16*(dots_square-diagonal), 48**4),
        "repeated_among_three": Q(identity_norm, 48**4),
    }
    moments, counts = [], []
    for length in range(1, 5):
        tally = {key: 0 for key in values}
        for word in product(range(3), repeat=length):
            reduced = cyclic_reduce(word)
            if len(reduced) == 1:
                kind = "one_stage"
            elif len(reduced) == 2:
                kind = "two_stages"
            elif len(reduced) == 3:
                need(len(set(reduced)) == 3, "three-stage cyclic reduction")
                kind = "three_distinct"
            elif len(set(reduced)) == 2:
                kind = "alternating_two"
            else:
                need(len(reduced) == 4 and len(set(reduced)) == 3,
                     "four-stage cyclic reduction")
                kind = "repeated_among_three"
            tally[kind] += 1
        counts.append({key: value for key, value in tally.items() if value})
        moments.append(sum((values[key] * count for key, count in tally.items()), Q(0)))
    need(moments == [Q(24), Q(28), Q(109, 3), Q(1823, 36)], "four trace moments")
    a, b = Q(81, 40), Q(-9, 10)
    need(moments[1]*a + moments[2]*b == moments[0] and
         moments[2]*a + moments[3]*b == moments[1], "exact moment system")
    polynomial = [Q(1), -a, -b]
    square = [Q(0)] * 5
    for i, x in enumerate(polynomial):
        for j, y in enumerate(polynomial):
            square[i+j] += x*y
    certificate = [Q(int(i == 0)) - c for i, c in enumerate(square)]
    need(certificate == [Q(0), Q(81, 20), Q(-9441, 1600),
                         Q(729, 200), Q(-81, 100)], "square polynomial identity")
    rank = sum((c*m for c, m in zip(certificate[1:], moments)), Q(0))
    need(rank == Q(117, 5), "rational rank lower bound")
    return {"moments_per_owner": list(map(str, moments)),
            "stage_word_counts": counts,
            "reduced_trace_values": {k: str(v) for k, v in values.items()},
            "root_dot_square_sum": dots_square,
            "root_diagonal_dot_square_sum": diagonal,
            "identity_A_coefficient": identity_coefficient,
            "polynomial_coefficients_ascending": list(map(str, certificate)),
            "rank_lower_bound_per_owner": str(rank),
            "spectral_certificate": "p(t)=1-(1-81t/40+9t^2/10)^2; p(0)=0; p(t)<=1"}


def rejection_controls(columns, partition, routes):
    selected_a, selected_t, ordinary = partition
    controls = []

    def reject(name, action, expected):
        try:
            action()
        except ValueError as error:
            need(str(error) == expected, "wrong control rejection: " + name)
            controls.append({"mutation": name, "rejected_by": expected})
        else:
            raise ValueError("mutation accepted: " + name)

    corrupted = deepcopy(columns)
    corrupted[ordinary[0]][0] += 1
    reject("corrupt one root coordinate", lambda: check_roots(corrupted, *partition),
           "root norm four")
    corrupted_gram = deepcopy(columns)
    victim = ordinary[0]
    replacement = next(p for p in ordinary[1:]
                       if gram(columns, [p]) != gram(columns, [victim]))
    corrupted_gram[victim] = columns[replacement][:]
    reject("duplicate a norm-four root with different outer product",
           lambda: check_roots(corrupted_gram, *partition), "full Gram 56I")
    corrupted_route = list(routes[1][ordinary[0]])
    corrupted_route[0] ^= 1
    reject("corrupt one route matrix entry", lambda: check_route(tuple(corrupted_route)),
           "orthogonal route")
    spectator_route = list(routes[1][ordinary[0]])
    spectator_route[25], spectator_route[26] = spectator_route[26], spectator_route[25]
    reject("swap two spectators while preserving orthogonality and involution",
           lambda: check_route(tuple(spectator_route)),
           "48 spectators fixed with no active mixing")
    duplicate_routes = [list(stage) for stage in routes]
    duplicate_routes[1][ordinary[0]] = routes[1][ordinary[1]]
    reject("duplicate a valid ordinary owner route",
           lambda: relative_routes(duplicate_routes, ordinary, 0, 1),
           "96 distinct relative routes")
    return controls


def run(root):
    """Return a deterministic JSON-compatible exact finite receipt."""
    columns, partition, routes = source_geometry(root)
    ordinary = partition[2]
    tables, table_receipts = {}, {}
    for s, t in permutations(range(3), 2):
        relative = relative_routes(routes, ordinary, s, t)
        tables[s, t] = exact_table(relative)
        table_receipts[f"{s}{t}"] = {
            "relative_routes": len(relative), "ordered_pairs": len(relative)**2,
            "distinct_products": len(tables[s, t]), "identity_diagonal_pairs": 96,
            "nonidentity_singleton_fibres": 9120}
    intersections = {}
    for s in range(3):
        t, u = [v for v in range(3) if v != s]
        common = intersection(tables[s, t], tables[s, u])
        need(common == [I25], "same-first-stage product images meet only at identity")
        intersections[f"{s}{t}_{s}{u}"] = "identity only"
    return {
        "status": "PASS_QQ16_TEXT_SOURCE_FOURTH_MOMENTS",
        "source_paths": list(SOURCE_PATHS),
        "source_interpretation": {
            "R": "constructor coordinate totals, tau=43 transport, phase recipe port order",
            "routes": "C S C^T chart swaps from main verify_native definition",
            "partition": "retained QQ16-SELECTED-WITNESS A/T/U",
            "compressed_packet_comparison": "NOT RUN; no packet or scalar-program replay"},
        "credited_fourth_moment_argument": "commdata2338 PR2189, following Nick Petalas PR2181",
        "root_columns": 112, "ordinary_columns": 96,
        "gram_multiples": {"all": 56, "A": 4, "T": 4, "U": 48},
        "full_route_columns_checked": AXES, "native_routes_checked": 112*3,
        "active_axes": ACTIVE, "spectators_fixed": AXES-ACTIVE,
        "matrix_equality": "full exact active-column tuples; sorted fibre/intersection comparison",
        "ordered_product_tables": table_receipts,
        "product_intersections": intersections,
        "trace_certificate": trace_moments(columns, ordinary),
        "controls": rejection_controls(columns, partition, routes),
        "scope": "Finite source-matrix census and conditional regular-cover rank bound; no native packet, controller, supplier or kappa admission"}
