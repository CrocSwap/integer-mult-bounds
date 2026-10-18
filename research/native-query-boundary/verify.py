"""Check the full native-query boundary and a paid two-block escape.

Use exact binary columns. Do not import a predecessor implementation.
"""
from array import array
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from math import gcd
from pathlib import Path
import argparse
import json

ROOT = Path(__file__).resolve().parent
BASE = "abdc6a7002abdbcd9e21bfc5e1a795784deacfdf"
FULL_MODULI = (3, 5, 7, 9)
POWER_CASES = ((3, 1), (3, 2), (3, 3), (3, 4), (3, 5),
               (5, 1), (5, 2), (5, 3), (7, 1), (7, 2), (7, 3),
               (11, 1), (13, 1))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return sha256(canonical(value)).hexdigest()


def source_check():
    manifest = json.loads((ROOT / "SOURCES.json").read_text())
    require(manifest["base"] == BASE, "wrong source base")
    checked = []
    for item in manifest["sources"]:
        data = (ROOT / item["local"]).read_bytes()
        require(sha256(data).hexdigest() == item["sha256"],
                "source hash: " + item["local"])
        checked.append(item["local"])
    selected = json.loads((ROOT / "vendor/selected-result.json").read_text())
    require(selected["kappa"] == "1661960547713947/1000000000000000000",
            "wrong selected comparison")
    return checked


def coordinates(index, m, dimension=6):
    result = [0] * dimension
    for j in range(dimension - 1, -1, -1):
        index, result[j] = divmod(index, m)
    return result


def index_of(point, m):
    result = 0
    for x in point:
        result = result * m + x % m
    return result


def native(point, m, power=1):
    a, b, c, d, e, f = point
    step = power * pow(4, -1, m) * (a - c - d + f) % m
    return ((a + step) % m, b, (c + step) % m,
            (d - step) % m, e, (f - step) % m)


def swap_banks(point):
    return tuple(point[3:] + point[:3])


def permutations(m):
    h, z = array("I"), array("I")
    for i in range(m ** 6):
        point = coordinates(i, m)
        h.append(index_of(native(point, m), m))
        z.append(index_of(swap_banks(point), m))
    return h, z


def cycle_data(perm):
    unset = 2 ** 32 - 1
    labels = array("I", [unset]) * len(perm)
    representatives, histogram = [], Counter()
    for start in range(len(perm)):
        if labels[start] != unset:
            continue
        orbit = len(representatives)
        representatives.append(start)
        at, length = start, 0
        while labels[at] == unset:
            labels[at] = orbit
            length += 1
            at = perm[at]
        require(at == start, "map is not a permutation")
        histogram[length] += 1
    return labels, representatives, dict(sorted(histogram.items()))


def full_census(m):
    h, z = permutations(m)
    labels, representatives, histogram = cycle_data(h)
    require(all(z[h[i]] == h[z[i]] for i in range(len(h))),
            "interchange does not commute with native map")
    fixed_orbits = sum(labels[z[i]] == labels[i] for i in representatives)
    fixed_addresses = sum(i == z[i] for i in range(len(z)))
    expected = m ** 4 * sum(gcd(m, i) for i in range(m))
    require(len(representatives) == expected, "full orbit count")
    require(fixed_orbits == m ** 3, "fixed orbit count")
    require(fixed_addresses == m ** 3, "interchange fixed addresses")
    e_h1 = index_of((0, 1, 0, 0, 0, 0), m)
    e_d1 = index_of((0, 0, 0, 0, 1, 0), m)
    require(h[e_h1] == e_h1 and h[e_d1] == e_d1,
            "fixed-point witness")
    require(z[e_h1] == e_d1 and labels[e_h1] != labels[e_d1],
            "orbit boundary witness")
    return {"modulus": m, "addresses": len(h), "orbits": len(representatives),
            "orbit_lengths": {str(k): v for k, v in histogram.items()},
            "fixed_interchange_orbits": fixed_orbits,
            "centered_rank": len(h) - len(representatives),
            "ordinary_rank_one_row": (len(h) - fixed_addresses) // 2,
            "orbit_quotient_rank_three_rows": 3 * (expected - m ** 3) // 2}, h, z


def rank_formula(p, b, spectators=1):
    m = p ** b
    u = spectators * m ** 6
    k = spectators * m ** 4 * (m + b * (m - m // p))
    r = u - k
    t = spectators * (m ** 6 - m ** 3) // 2
    require(0 < r < t if m == 3 else t < r < 2 * t,
            "single-block rank interval")
    return {"prime": p, "width": b, "modulus": m, "spectators": spectators,
            "volume_per_row": u, "orbits": k, "centered_rank": r,
            "ordinary_rank_one_row": t,
            "minimum_blocks_for_three_rows_by_rank": (3 * t + r - 1) // r,
            "orbit_quotient_rank_three_rows": 3 * (k - spectators * m ** 3) // 2}


def reduced_census(p, b):
    m = p ** b
    perm = array("I", ((x + d) % m * m + d for x in range(m) for d in range(m)))
    _, representatives, histogram = cycle_data(perm)
    formula = rank_formula(p, b)
    require(len(representatives) * m ** 4 == formula["orbits"],
            "reduced orbit count")
    require(sum(n * count for n, count in histogram.items()) == m * m,
            "reduced full coverage")
    return formula | {"two_coordinate_orbit_lengths":
                      {str(k): v for k, v in histogram.items()}}


def apply_columns(columns, vector):
    result = 0
    while vector:
        low = vector & -vector
        result ^= columns[low.bit_length() - 1]
        vector ^= low
    return result


def column_rank(columns):
    basis = {}
    for vector in columns:
        while vector:
            pivot = vector.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = vector
                break
            vector ^= basis[pivot]
    return len(basis)


def matrix_rows(columns):
    rows = [0] * len(columns)
    for j, column in enumerate(columns):
        while column:
            low = column & -column
            rows[low.bit_length() - 1] |= 1 << j
            column ^= low
    return rows


def invert_and_compile(columns):
    """Return the inverse and a literal XOR circuit for that inverse."""
    n = len(columns)
    rows = matrix_rows(columns)
    inverse_rows = [1 << i for i in range(n)]
    gates = []

    def add(target, source):
        rows[target] ^= rows[source]
        inverse_rows[target] ^= inverse_rows[source]
        gates.append((target, source))

    for i in range(n):
        mask = 1 << i
        if not rows[i] & mask:
            pivot = next((j for j in range(i + 1, n) if rows[j] & mask), None)
            require(pivot is not None, "singular encoder")
            add(i, pivot)
            add(pivot, i)
            add(i, pivot)
        for j in range(n):
            if j != i and rows[j] & mask:
                add(j, i)
    require(rows == [1 << i for i in range(n)], "encoder elimination")
    inverse = matrix_rows(inverse_rows)
    require(all(apply_columns(columns, inverse[i]) == 1 << i for i in range(n)),
            "encoder inverse")
    return inverse, gates


def jordan_basis(nilpotent):
    """Build a basis with N(w_i)=v_i and N(v_i)=0."""
    n = len(nilpotent)
    pivots, images, preimages, kernel = {}, [], [], []
    for i, original in enumerate(nilpotent):
        vector, relation = original, 1 << i
        while vector:
            pivot = vector.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = (vector, relation)
                images.append(original)
                preimages.append(1 << i)
                break
            image, preimage = pivots[pivot]
            vector ^= image
            relation ^= preimage
        if not vector:
            kernel.append(relation)
    columns = images + preimages
    basis = {}

    def extend(vector):
        residual = vector
        while residual:
            pivot = residual.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = residual
                return True
            residual ^= basis[pivot]
        return False

    for vector in columns:
        require(extend(vector), "dependent Jordan pair")
    for vector in kernel:
        if extend(vector):
            columns.append(vector)
    r = len(images)
    require(len(columns) == n, "incomplete Jordan basis")
    for i, vector in enumerate(columns):
        expected = images[i - r] if r <= i < 2 * r else 0
        require(apply_columns(nilpotent, vector) == expected, "Jordan equation")
    inverse, _ = invert_and_compile(columns)
    return columns, inverse


def irreducible_blocks(n):
    """Return C with C and I+C invertible, for n >= 2."""
    require(n >= 2, "one-dimensional complementary factor is unavailable")
    columns, offset = [], 0
    if n % 2:
        columns.extend((2, 4, 3))
        offset = 3
    while offset < n:
        columns.extend((1 << (offset + 1), 3 << offset))
        offset += 2
    require(column_rank(columns) == n, "singular factor C")
    require(column_rank([c ^ (1 << i) for i, c in enumerate(columns)]) == n,
            "singular factor I+C")
    return columns


def native_difference(h):
    u = len(h)
    inverse = [0] * u
    for i, image in enumerate(h):
        inverse[image] = i
    return [0] * u + [(1 << h[i]) ^ (1 << inverse[i]) for i in range(u)] + [0] * u


def target_difference(z, genuine_rows=1):
    u = len(z)
    require(genuine_rows in (1, 2, 3), "one to three genuine rows")
    return [((1 << (role * u + i)) ^ (1 << (role * u + z[i])))
            if role < genuine_rows else 0 for role in range(3) for i in range(u)]


def two_block_encoders(h, z, genuine_rows=1):
    u, n = len(h), 3 * len(h)
    native_n, target_n = native_difference(h), target_difference(z, genuine_rows)
    r, t = column_rank(native_n), column_rank(target_n)
    native_basis, _ = jordan_basis(native_n)
    target_basis, target_inverse = jordan_basis(target_n)
    first, second = [0] * n, [0] * n
    if r < t:
        zero_size, core_size = t - r, 2 * r - t
        core = irreducible_blocks(core_size)
        for i in range(zero_size, 2 * zero_size):
            first[t + i] = 1 << i
        for i, column in enumerate(core):
            first[t + 2 * zero_size + i] = column << (2 * zero_size)
        for i in range(t):
            second[t + i] = first[t + i] ^ (1 << i)
    else:
        core = irreducible_blocks(t)
        for i, column in enumerate(core):
            first[t + i] = column
            second[t + i] = column ^ (1 << i)
        extra = r - t
        require(2 * t + 2 * extra <= n, "insufficient dirty helper capacity")
        for i in range(extra):
            first[2 * t + extra + i] = 1 << (2 * t + i)
            second[2 * t + extra + i] = 1 << (2 * t + i)
    require(column_rank(first) == r and column_rank(second) == r,
            "factor ranks")
    require(all(apply_columns(first, c) == 0 for c in second), "factor product")
    encoders, metadata = [], []
    for factor in (first, second):
        physical = [apply_columns(target_basis, apply_columns(factor, c))
                    for c in target_inverse]
        _, factor_inverse = jordan_basis(physical)
        encoding = [apply_columns(native_basis, c) for c in factor_inverse]
        inverse_encoding, inverse_gates = invert_and_compile(encoding)
        for i, column in enumerate(encoding):
            left = apply_columns(native_n, column)
            right = apply_columns(encoding, physical[i])
            require(left == right, "encoder intertwining equation")
        encoders.append((list(reversed(inverse_gates)), inverse_gates))
        metadata.append({"encode_xor_transfers": len(inverse_gates),
                         "decode_xor_transfers": len(inverse_gates),
                         "encoder_columns_sha256": digest(encoding),
                         "inverse_columns_sha256": digest(inverse_encoding)})
    require(all((a ^ b) == (1 << (i - t) if t <= i < 2 * t else 0)
                for i, (a, b) in enumerate(zip(first, second))), "factor sum")
    return encoders, {"bits": n, "data_volume": genuine_rows * u,
                      "dirty_helper_volume": (3 - genuine_rows) * u,
                      "native_rank": r, "target_rank": t, "encoders": metadata}


def query_events(k):
    c = Fraction(k, 4)
    return [("affine", 2, Fraction(1), ((0, Fraction(-1)),)),
            ("affine", 3, Fraction(1), ((0, Fraction(1)),)),
            ("affine", 5, c, ((0, 1 + c), (2, -c), (3, -c))),
            ("child", 0, 5),
            ("affine", 2, Fraction(1), ((0, Fraction(1)),)),
            ("affine", 3, Fraction(1), ((0, Fraction(-1)),)),
            ("affine", 5, -1 / c, ((0, 1 / c - 1), (2, Fraction(1)),
                                    (3, Fraction(1))))]


def inverse_event(event):
    if event[0] != "affine":
        return event
    _, target, diagonal, controls = event
    return ("affine", target, 1 / diagonal,
            tuple((i, -coefficient / diagonal) for i, coefficient in controls))


def event_permutation(event, m, spectators=1):
    result = array("I")

    def residue(value):
        value = Fraction(value)
        return value.numerator * pow(value.denominator, -1, m) % m

    for index in range(m ** 6):
        point = coordinates(index, m)
        if event[0] == "child":
            _, a, b = event
            point[a], point[b] = point[b], point[a]
        else:
            _, target, diagonal, controls = event
            point[target] = (residue(diagonal) * point[target] + sum(
                residue(c) * point[i] for i, c in controls)) % m
        result.append(index_of(point, m))
    one = result[:]
    for spectator in range(1, spectators):
        result.extend(spectator * m ** 6 + i for i in one)
    return result


def fused_events():
    return query_events(-1) + [("row_xor", 0, 1)] + query_events(2) + [
        ("row_xor", 0, 1)] + query_events(-1)


def run_word(word, m, cache, state=None, spectators=1):
    u = spectators * m ** 6
    if state is None:
        state = [1 << i for i in range(3 * u)]
    else:
        state = state.copy()
    for event in word:
        if event[0] == "bit_xor":
            _, target, source = event
            state[target] ^= state[source]
        elif event[0] == "row_xor":
            _, target, source = event
            for i in range(u):
                state[target * u + i] ^= state[source * u + i]
        else:
            if event not in cache:
                cache[event] = event_permutation(event, m, spectators)
            incoming = state[:u]
            for old, new in enumerate(cache[event]):
                state[new] = incoming[old]
    return state


def word_json(word):
    return [[event[0], *([str(x) if isinstance(x, Fraction) else x for x in event[1:]])]
            if event[0] != "affine" else
            ["affine", event[1], str(event[2]), [[i, str(c)] for i, c in event[3]]]
            for event in word]


def escape_check(h, z):
    encoders, result = two_block_encoders(h, z)
    word = []
    for encoding, decoding in encoders:
        word.extend(("bit_xor", *gate) for gate in encoding)
        word.extend(fused_events())
        word.extend(("bit_xor", *gate) for gate in decoding)
    cache = {}
    actual = run_word(word, 3, cache)
    u = len(h)
    expected = [1 << z[i] for i in range(u)] + [1 << i for i in range(u, 3 * u)]
    require(actual == expected, "complete two-block DATA/helper boundary")
    inverse = [inverse_event(event) for event in reversed(word)]
    require(run_word(inverse, 3, cache, actual) == [1 << i for i in range(3 * u)],
            "complete literal inverse")
    child_at = next(i for i, event in enumerate(word) if event[0] == "child")
    row_at = next(i for i, event in enumerate(word) if event[0] == "row_xor")
    mutants = {
        "omit_ordinary_child": word[:child_at] + word[child_at + 1:],
        "omit_full_row_xor": word[:row_at] + word[row_at + 1:],
        "omit_final_decoder_transfer": word[:-1],
        "dirty_helper_not_restored": word + [("bit_xor", 3 * u - 1, 0)],
    }
    controls = []
    for name, mutant in mutants.items():
        require(run_word(mutant, 3, cache) != expected, "accepted bad word: " + name)
        controls.append(name)
    counts = Counter(event[0] for event in word)
    require(counts["child"] == 6 and counts["affine"] == 36,
            "complete ordinary-child invoice")
    require(counts["row_xor"] == 4, "complete row-XOR invoice")
    result.update({"modulus": 3, "width": 1, "genuine_rows": 1,
                   "restored_dirty_rows": 2, "full_input_columns": 3 * u,
                   "forward_and_inverse": True, "counts": dict(sorted(counts.items())),
                   "word_sha256": digest(word_json(word)),
                   "child_volume_per_call": "V", "child_width_per_call": "N/3",
                   "normalized_recursive_coefficient": 6,
                   "controls": controls})
    lifted = []
    for event in word:
        if event[0] == "bit_xor":
            _, target, source = event
            tr, ta = divmod(target, u)
            sr, sa = divmod(source, u)
            for spectator in range(2):
                lifted.append(("bit_xor", tr * 2 * u + spectator * u + ta,
                               sr * 2 * u + spectator * u + sa))
        else:
            lifted.append(event)
    lifted_expected = [1 << (spectator * u + z[i])
                       for spectator in range(2) for i in range(u)]
    lifted_expected += [1 << i for i in range(2 * u, 6 * u)]
    lifted_cache = {}
    require(run_word(lifted, 3, lifted_cache, spectators=2) == lifted_expected,
            "complete spectator lift")
    require(run_word([inverse_event(e) for e in reversed(lifted)], 3,
                     lifted_cache, lifted_expected, spectators=2)
            == [1 << i for i in range(6 * u)], "spectator literal inverse")
    child = next(e for e in lifted if e[0] == "child")
    bad_cache = dict(lifted_cache)
    bad_cache[child] = array("I", list(lifted_cache[child][:u]) + list(range(u, 2 * u)))
    require(run_word(lifted, 3, bad_cache, spectators=2) != lifted_expected,
            "child lost a spectator fiber")
    result["spectator_lift"] = {"spectators": 2, "full_input_columns": 6 * u,
                                "child_volume_per_call": 2 * u,
                                "forward_and_inverse": True,
                                "word_sha256": digest(word_json(lifted)),
                                "control": "child_lost_spectator_fiber"}
    return result, word


def rational_lowering_check():
    checked = []
    s, r = (1, 0, 1, -1, 0, -1), (1, 0, -1, -1, 0, 1)
    for k in (-2 ** 54, -4, -1, 1, 2, 2 ** 54):
        for j in range(6):
            point = [Fraction(i == j) for i in range(6)]
            for event in query_events(k):
                if event[0] == "child":
                    _, a, b = event
                    point[a], point[b] = point[b], point[a]
                else:
                    _, target, diagonal, controls = event
                    point[target] = diagonal * point[target] + sum(c * point[i] for i, c in controls)
            require(point == [Fraction(i == j) + Fraction(k, 4) * s[i] * r[j]
                              for i in range(6)], "rational native lowering")
        checked.append(k)
    return checked


def three_row_templates():
    checked_blocks = []
    for size in (2, 3):
        c = irreducible_blocks(size)
        a = [0] * size + c
        b = [0] * size + [column ^ (1 << i) for i, column in enumerate(c)]
        require(column_rank(a) == size and column_rank(b) == size,
                "complementary block ranks")
        require(all(apply_columns(a, v) == 0 and apply_columns(b, u) == 0
                    for u, v in zip(a, b)), "complementary block product")
        require([u ^ v for u, v in zip(a, b)]
                == [0] * size + [1 << i for i in range(size)],
                "complementary block sum")
        checked_blocks.append({"size": size, "columns": c})
    cases = []
    for p, b in POWER_CASES:
        if p ** b < 11:
            continue
        f = rank_formula(p, b)
        r, t = f["centered_rank"], 3 * f["ordinary_rank_one_row"]
        zero, core = t - r, 2 * r - t
        require(zero >= 0 and core >= 2, "three-row template domain")
        threes = core % 2
        twos = (core - 3 * threes) // 2
        require(2 * twos + 3 * threes == core, "template block coverage")
        require(zero + core == r and 2 * zero + core == t,
                "template exact ranks")
        require(2 * t <= 3 * f["volume_per_row"], "template ambient dimension")
        cases.append({"prime": p, "width": b, "modulus": p ** b,
                      "fused_rank": r, "target_rank": t, "zero_and_identity_size": zero,
                      "core_size": core, "two_dimensional_blocks": twos,
                      "three_dimensional_blocks": threes,
                      "ordinary_children": 6, "child_volume_each": "V/3",
                      "child_width_each": "N/3", "normalized_child_coefficient": 2})
    return {"scope": "constructive direct-sum proof; no full large-domain encoder replay",
            "minimum_complete_blocks": 2, "small_blocks": checked_blocks, "cases": cases}


def build_receipt():
    sources = source_check()
    full, small_h, small_z = [], None, None
    for m in FULL_MODULI:
        item, h, z = full_census(m)
        full.append(item)
        if m == 3:
            small_h, small_z = h, z
    reduced = [reduced_census(p, b) for p, b in POWER_CASES]
    spectators = [rank_formula(3, 2, s) for s in (1, 2, 7)]
    require(spectators[2]["centered_rank"] == 7 * spectators[0]["centered_rank"],
            "spectator volume was lost")
    require(full[-1]["orbits"] != 9 ** 5 + (9 ** 6 - 9 ** 5) // 9,
            "short prime-power orbit control")
    even_cycle = (1, 0)
    even_inverse = [even_cycle.index(i) for i in range(2)]
    even_centered = [(1 << even_cycle[i]) ^ (1 << even_inverse[i]) for i in range(2)]
    odd_formula_on_even_cycle = 2 - len(cycle_data(even_cycle)[1])
    require(column_rank(even_centered) == 0 and odd_formula_on_even_cycle == 1,
            "even two-cycle scope control")
    m = 9
    one = array("I", ((x + d) % m * m + d for x in range(m) for d in range(m)))
    three = array("I", ((x + 3 * d) % m * m + d for x in range(m) for d in range(m)))
    require(len(cycle_data(three)[1]) > len(cycle_data(one)[1]), "nonunit-power scope control")
    escape, word = escape_check(small_h, small_z)
    require(escape["native_rank"] != escape["target_rank"], "single-block control")
    return {"status": "PASS_NATIVE_QUERY_BOUNDARY", "base": BASE,
            "classification": "scoped obstruction, constructive encoding theorem, and exact finite paid escape",
            "no_new_kappa": True, "checked_sources": sources,
            "source_manifest_sha256": sha256((ROOT / "SOURCES.json").read_bytes()).hexdigest(),
            "full_domain": full, "prime_power_cases": reduced,
            "spectator_cases": spectators, "rational_query_powers": rational_lowering_check(),
            "two_block_escape": escape, "three_genuine_row_construction": three_row_templates(),
            "scope_controls": ["short_prime_power_orbits", "spectator_volume",
                               "even_orbit", "nonunit_power", "one_block_rank"],
            "search": {"randomness": None, "stopping_rule": "complete fixed coverage",
                       "full_moduli": list(FULL_MODULI), "prime_power_cases": len(POWER_CASES)}}, word


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", type=Path, help="Write a new receipt; do not overwrite a file.")
    parser.add_argument("--emit-word", type=Path, help="Write the literal escape word to a new file.")
    args = parser.parse_args()
    receipt, word = build_receipt()
    if args.emit:
        with args.emit.open("x") as out:
            json.dump(receipt, out, indent=2, sort_keys=True)
            out.write("\n")
    else:
        expected = json.loads((ROOT / "CERTIFICATE.json").read_text())
        require(canonical(expected) == canonical(receipt), "certificate does not match exact replay")
    if args.emit_word:
        with args.emit_word.open("x") as out:
            json.dump(word_json(word), out, separators=(",", ":"))
            out.write("\n")
    escape = receipt["two_block_escape"]
    print("PASS_NATIVE_QUERY_BOUNDARY full_addresses=" + str(sum(x["addresses"] for x in receipt["full_domain"]))
          + " prime_power_cases=" + str(len(POWER_CASES)) + " dirty_columns=" + str(escape["full_input_columns"])
          + " escape_children=6 no_new_kappa")


if __name__ == "__main__":
    main()
