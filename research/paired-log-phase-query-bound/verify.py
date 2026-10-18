"""Exact premises for the averaged-rank phase-query bound.

Jose Manuel (@jmbarrancoml), with substantial OpenAI Codex assistance.
Apache-2.0. Source geometry: Ali Romman and the retained supplier lineage.
The causal/character rank method follows eumemic PR288 and Ali Romman PR468.
"""

from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
from random import Random

ROOT = Path(__file__).resolve().parents[2]
A_PORTS = [0, 7, 20, 23, 86, 93, 108, 111]
SOURCE_PATH = "research/native-source-codes/source_data.py"
COST_PATH = "research/complex-local-word-ceiling/ceiling.py"
IMPORT_PINS = {
    SOURCE_PATH: "d23924511e3aed41e5e64511ca70126a636d91c8aa02e656cb61d6ceca1fe0a0",
    COST_PATH: "86a1432870b3b21d8454106ec9162fddc0471472d9214c590a1420f2426cedfc",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(path, name):
    require(sha256((ROOT / path).read_bytes()).hexdigest() == IMPORT_PINS[path], "import source pin")
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def zeros(n, m):
    return [[0] * m for _ in range(n)]


def eye(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def transpose(a):
    return [list(x) for x in zip(*a)]


def multiply(a, b):
    if not a:
        return []
    require(len(a[0]) == len(b), "matrix dimensions")
    out = zeros(len(a), len(b[0]))
    for i, row in enumerate(a):
        for k, x in enumerate(row):
            if x:
                for j, y in enumerate(b[k]):
                    if y:
                        out[i][j] += x * y
    return out


def difference(a, b):
    return [[x - y for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]


def rank(rows, prime=None):
    if not rows or not rows[0]:
        return 0
    a = [[int(x) % prime if prime else F(x) for x in row] for row in rows]
    pivot = 0
    for col in range(len(a[0])):
        found = next((i for i in range(pivot, len(a)) if a[i][col]), None)
        if found is None:
            continue
        a[pivot], a[found] = a[found], a[pivot]
        scale = pow(a[pivot][col], -1, prime) if prime else 1 / a[pivot][col]
        a[pivot] = [(x * scale) % prime if prime else x * scale for x in a[pivot]]
        for i in range(pivot + 1, len(a)):
            c = a[i][col]
            if c:
                a[i] = [(x - c * y) % prime if prime else x - c * y
                        for x, y in zip(a[i], a[pivot])]
        pivot += 1
        if pivot == len(a):
            break
    return pivot


def expect_rejection(call, label):
    try:
        call()
    except ValueError:
        return label
    raise ValueError("negative control accepted: " + label)


def causal_checks():
    """Compare a direct program with the causal expansion, including singular maps."""
    rng = Random(20261014)
    examples, characters, singular_steps, causal_control = 12, 8, 0, False
    for fixture in range(examples):
        n, inputs, outputs, k = 6, (4 if fixture % 2 else 6), (4 if fixture % 2 else 6), 6
        entry = [row[:inputs] for row in eye(n)]
        exit_map = eye(n)[:outputs]
        coordinates = [rng.randrange(n) for _ in range(k)]
        labels = [1 + rng.randrange(7) for _ in range(k)]
        maps = []
        for j in range(k):
            a = eye(n)
            for _ in range(5):
                target, source = rng.sample(range(n), 2)
                c = rng.choice([-2, -1, 1, 2])
                a[target] = [x + c * y for x, y in zip(a[target], a[source])]
            if j % 3 == 1:
                target, source = rng.sample(range(n), 2)
                a[target] = a[source][:]  # singular COPY
                singular_steps += 1
            if j % 3 == 2:
                a[rng.randrange(n)] = [0] * n  # CLEAR
                singular_steps += 1
            maps.append(a)
        prefix = entry
        v = []
        for j in range(k):
            v.append(prefix[coordinates[j]][:])
            prefix = multiply(maps[j], prefix)
        baseline = multiply(exit_map, prefix)
        suffix, u = exit_map, zeros(outputs, k)
        for j in range(k - 1, -1, -1):
            suffix = multiply(suffix, maps[j])
            for i in range(outputs):
                u[i][j] = suffix[i][coordinates[j]]
        h = zeros(k, k)
        for earlier in range(k):
            propagation = eye(n)
            for later in range(earlier + 1, k):
                propagation = multiply(maps[later - 1], propagation)
                h[later][earlier] = propagation[coordinates[later]][coordinates[earlier]]
        differences, defects, active_counts = [], [], []
        for character in range(characters):
            alpha = [-2 if (character & label).bit_count() % 2 else 0 for label in labels]
            direct = [row[:] for row in entry]
            for j in range(k):
                direct[coordinates[j]] = [(1 + alpha[j]) * x for x in direct[coordinates[j]]]
                direct = multiply(maps[j], direct)
            actual = difference(multiply(exit_map, direct), baseline)
            injection = zeros(k, inputs)
            for j in range(k):
                for t in range(inputs):
                    injection[j][t] = alpha[j] * (v[j][t] + sum(h[j][i] * injection[i][t] for i in range(j)))
            require(multiply(u, injection) == actual, "causal expansion")
            diagonal_only = [[alpha[j] * x for x in v[j]] for j in range(k)]
            causal_control |= multiply(u, diagonal_only) != actual
            active = [j for j in range(k) if alpha[j]]
            us = [[row[j] for j in active] for row in u]
            vs = [v[j] for j in active]
            defect = rank(actual)
            require(defect >= rank(us) + rank(vs) - len(active), "active-set Sylvester bound")
            differences.append(actual)
            defects.append(defect)
            active_counts.append(len(active))
        du = rank([row for delta in differences for row in transpose(delta)])
        dv = rank([row for delta in differences for row in delta])
        require(sum(active_counts) == characters * k // 2, "half-active nonzero queries")
        for defect, active in zip(defects, active_counts):
            require(defect >= du + dv - 2 * k + active, "global span deletion bound")
        require(3 * k * characters >= 2 * ((du + dv) * characters - sum(defects)), "averaged-rank bound")
    require(causal_control, "causal omission control was not exercised")
    return {"programs": examples, "character_maps": examples * characters, "singular_free_steps": singular_steps,
            "omitting_causal_propagation_changes_a_checked_map": causal_control}


def quadratic_pairs(m):
    return [(i, j) for i in range(m) for j in range(i, m)]


def polar(q, m):
    return sum(((q >> i) & 1) * ((q >> j) & 1) << k for k, (i, j) in enumerate(quadratic_pairs(m)))


def frequency_tuple(form, m):
    pairs, degrees, linear, frequencies = quadratic_pairs(m), [0] * m, [0] * m, []
    for k, (i, j) in enumerate(pairs):
        if not ((form >> k) & 1):
            continue
        if i == j:
            linear[i] = 1
        else:
            frequencies.append((1 << i) | (1 << j))
            degrees[i] += 1
            degrees[j] += 1
    for i in range(m):
        frequencies += [1 << i] * ((2 * linear[i] - degrees[i]) % 4)
    length = 4 * ((m * (m - 1) // 2 + 3 * m + 3) // 4)
    require(len(frequencies) <= length, "common tensor length")
    frequencies += [0] * (length - len(frequencies))
    return frequencies


def sector_checks():
    checks = 0
    for form in range(64):
        frequencies = frequency_tuple(form, 3)
        require(len(frequencies) == 12, "small common tensor length")
        for shift in range(8):
            shifted = [x ^ shift for x in frequencies]
            xor = 0
            for x in shifted:
                xor ^= x
            require(xor == 0, "uniform X stabilizer")
            for q in range(1, 8):
                phase = sum((q & x).bit_count() % 2 for x in shifted) % 4
                wanted = 2 * ((form & polar(q, 3)).bit_count() % 2)
                require(phase == wanted, "Pauli-trivial character witness")
                checks += 1
    # Uniform Z permutes the eight shifted tuples; the equal-weight orbit sum
    # is nonzero and fixed. These checks distinguish free Pauli translations
    # from unconstrained character sectors, where the theorem would not apply.
    bad = frequency_tuple(0, 3)
    bad[0] ^= 1
    bad_x_phase = sum((1 & x).bit_count() % 2 for x in bad) % 2
    require(bad_x_phase == 1, "nontrivial Pauli control")
    control = expect_rejection(lambda: require(bad_x_phase == 0, "uniform X is not trivial"),
                               "unqualified free-Pauli sector")
    return {"characters": 64, "tensor_length": 12, "exact_phase_checks": checks, "control": control}


def target_checks():
    source = load(SOURCE_PATH, "pinned_native_source")
    data = source.load_local(ROOT)
    word, program = data["CANONICAL-WORD.json.gz"], data["LOCAL-PROGRAMS.json.gz"]["forward"]
    boundary = source.replay(program, 704, program.index(["phase", "centers"]))
    r = [[boundary[c].get(j, 0) for j in range(112)] for c in word["centers"]]
    a = [[row[j] for j in A_PORTS] for row in r]
    ordinary = [j for j in range(112) if j not in A_PORTS]
    require(multiply(transpose(a), a) == [[4 * x for x in row] for row in eye(8)], "selected minor")
    # B=R_A^-1 R_B; store 2B as small integers.
    b2 = multiply(transpose(a), [[row[j] for j in ordinary] for row in r])
    b2 = [[F(x) / 2 for x in row] for row in b2]
    require(all(x.denominator == 1 and x in (-1, 0, 1) for row in b2 for x in row), "twice-B coefficients")
    b2 = [[int(x) for x in row] for row in b2]
    require(multiply(b2, transpose(b2)) == [[52 * x for x in row] for row in eye(8)], "B B^T=13I")
    require(all(any(row) for row in b2) and all(any(col) for col in zip(*b2)), "nonzero rows and columns")
    labels = word["ports"]
    require(len(set(labels)) == 112 and all(q.bit_count() % 2 for q in labels), "distinct odd hole labels")
    polars = [polar(q, 9) for q in labels]
    pair_keys = [polars[i] ^ polars[j] for i in range(112) for j in range(i)]
    require(len(set(pair_keys)) == 6216 and 0 not in pair_keys, "unique pair characters")
    wrong_polars = polars[:]
    wrong_polars[1] = wrong_polars[0]
    pair_control = expect_rejection(lambda: require(
        len({wrong_polars[i] ^ wrong_polars[j] for i in range(112) for j in range(i)}) == 6216,
        "duplicate hole label"), "duplicate hole character")
    n, v, selected, ordinary_count = 120, 112, 8, 104
    t4 = zeros(n, n)
    bb = multiply(transpose(b2), b2)
    for i in range(8):
        t4[i][i], t4[i][112+i], t4[112+i][i] = 52, 4, 4
        for j in range(104):
            t4[i][8+j], t4[112+i][8+j], t4[8+j][i] = 24*b2[i][j], 2*b2[i][j], -2*b2[i][j]
    for i in range(104):
        for j in range(104):
            t4[8+i][8+j] = 4 * int(i == j) - bb[i][j]
    images, rows = [], []
    for j in range(104):
        e = [0] * n
        e[8+j] = 1
        images.append(e)
        rows.append(e[:])
    for i in range(8):
        image, row = [0] * n, [0] * n
        image[i], image[112+i], row[i] = 12, 1, 1
        images.append(image)
        rows.append(row)
    require(rank(images, 1009) == rank(rows, 1009) == v, "union-span certificate")
    rng = Random(1128)
    forms = [1 << i for i in range(45)] + [rng.getrandbits(45) for _ in range(12)]
    ranks = Counter()
    order = A_PORTS + ordinary + A_PORTS
    log_control = False
    for form in forms:
        signs = [1 - 2 * ((form & polars[p]).bit_count() % 2) for p in order]
        actual = [[(signs[i] * signs[j] - 1) * t4[i][j] for j in range(n)] for i in range(n)]
        bp = [[signs[i] * signs[8+j] * b2[i][j] for j in range(104)] for i in range(8)]
        e = difference(bp, b2)
        formula = zeros(n, n)
        bb_delta = difference(multiply(transpose(bp), bp), bb)
        for i in range(8):
            for j in range(104):
                formula[i][8+j], formula[112+i][8+j], formula[8+j][i] = 24*e[i][j], 2*e[i][j], -2*e[i][j]
        for i in range(104):
            for j in range(104):
                formula[8+i][8+j] = -bb_delta[i][j]
        require(formula == actual, "exact target block identity")
        wrong_signs = signs[:]
        wrong_signs[112] *= -1
        wrong_target = [[(wrong_signs[i] * wrong_signs[j] - 1) * t4[i][j]
                         for j in range(n)] for i in range(n)]
        require(wrong_target != formula, "unmatched-log control did not fail")
        log_control = True
        erank = rank(e)
        require(rank(actual, 1009) == 2 * erank, "rank identity corroboration")
        ranks[2 * erank] += 1
    require((4 * (v - selected) + 2) // 3 == 139, "one-bank floor")
    require((4 * 4 * (v - selected) + 2) // 3 == 555, "joint four-bank floor")
    return {"ports": v, "selected_ports": A_PORTS, "B_nonzeros": sum(bool(x) for row in b2 for x in row),
            "pair_characters": len(pair_keys), "union_image_dimension": v, "union_row_dimension": v,
            "target_sign_cases": len(forms), "defect_rank_histogram": dict(sorted(ranks.items())),
            "rank_bound_per_character": 16, "one_bank_floor": 139, "joint_four_bank_floor": 555,
            "pair_control": pair_control, "unmatched_log_gauge_rejected": log_control}


def budget_check():
    cost = load(COST_PATH, "pinned_interval_cost")
    profile = {1:21204, 2:4500, 3:3744, 4:1170, 5:738, 8:16, 9:40,
               16:32, 17:16, 24:8, 32:16, 33:8, 40:8, 48:48, 49:8, 51:F(14778,51)}
    q, m, roles = F(67018507072324140917,40000000000000000000000), 73, 968
    require(sum(r*n for r,n in profile.items()) == 69840, "conditional rank mass")
    lo = hi = F(0)
    for r, count in profile.items():
        a, b = cost.child_cost(r, m, q)
        lo += count * m * a
        hi += count * m * b
    allowance = (m*roles-hi, m*roles-lo)
    require(F(50073765694042,10**11) < allowance[0] <= allowance[1] < F(50073765694043,10**11),
            "certified favorable allowance")
    one = tuple(m*x for x in cost.child_cost(1,m,q))
    require(497*one[1] < allowance[0] and 498*one[0] > allowance[1], "integer rank-one budget")
    require(F(555) > allowance[1], "even rank-mass price misses budget")
    return {"q": str(q), "conditional_fixed_width": m, "conditional_roles": roles,
            "allowance_decimal_bracket": ["500.73765694042", "500.73765694043"],
            "rank1_budget": 497, "phase_event_floor": 555}


def main():
    controls = []
    causal = causal_checks()
    sector = sector_checks()
    target = target_checks()
    budget = budget_check()
    controls.append(expect_rejection(lambda: require(3*554 >= 2*(896-64), "understated query count"), "554-call claim"))
    controls.append(expect_rejection(lambda: require(555 <= F(50073765694043,10**11), "underpriced phase events"), "decoder budget claim"))
    controls += ["omitted causal propagation", sector["control"], target["pair_control"], "unmatched log gauge"]
    controls.append(expect_rejection(lambda: require(
        sum((x & 0).bit_count() % 2 for x in range(8)) == 4, "neutral query is not half-active"),
        "counting a neutral query as nontrivial"))
    print(json.dumps({"status": "PASS_PAIRED_LOG_PHASE_QUERY_BOUND", "causal_programs": causal,
                      "pauli_trivial_sector": sector, "matched_target": target,
                      "conditional_budget": budget, "negative_controls": controls,
                      "scope": "Fixed role-linear schedules with single-array commuting phase queries; see README for tensor, cover and billing boundaries."}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
