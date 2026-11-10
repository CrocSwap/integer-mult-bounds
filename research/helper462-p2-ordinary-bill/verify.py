#!/usr/bin/env python3
"""Compare two helper-462 words under the inherited P2 ordinary-call tariff.

The published five-swap schedule and the zero-swap 7-scale 27-shear schedule
are priced by the same rules read from the pinned sources. No new kappa.
Standard library only.
"""
from collections import Counter
from fractions import Fraction
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "research/bit-completed-backend-api/science/RESULT.json"
STREAMS = ROOT / "research/selected-bit-stream-routes/qadic_streams.py"
GENERATOR = ROOT / "research/bit-row-route-generator/generator.py"
SCALING = ROOT / "research/signed-dyadic-scaling/README.md"
INPLACE = ROOT / "research/inplace-runtime-affine/README.md"
AFFINE = ROOT / "research/fixed-tape-affine-shear/README.md"
EARLIER = ROOT / "research/earlier-target-shift-gap/PROOF.md"
N = 8


def need(condition, message):
    if not condition:
        raise SystemExit("FAIL: " + message)


def eye():
    return [[Fraction(int(i == j)) for j in range(N)] for i in range(N)]


def rows_of(raw):
    return [[Fraction(entry) for entry in row] for row in raw]


def matmul(left, right):
    return [
        [sum(left[i][k] * right[k][j] for k in range(N)) for j in range(N)]
        for i in range(N)
    ]


def inverse(matrix):
    work = [row[:] + [Fraction(int(i == j)) for j in range(N)] for i, row in enumerate(matrix)]
    for column in range(N):
        pivot = next(row for row in range(column, N) if work[row][column] != 0)
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
        pivot_value = work[column][column]
        work[column] = [entry / pivot_value for entry in work[column]]
        for row in range(N):
            if row == column or work[row][column] == 0:
                continue
            factor = work[row][column]
            work[row] = [entry - factor * base for entry, base in zip(work[row], work[column])]
    return [row[N:] for row in work]


def elementary(kind, source, target, coefficient):
    """Right action used by the route interpreter on one cover row.

    ordered_shift(target, source, coefficient) does column_target += coefficient * column_source.
    A swap exchanges those two columns. A scale multiplies one column.
    """
    matrix = eye()
    if kind == "swap":
        matrix[source][source] = 0
        matrix[target][target] = 0
        matrix[source][target] = 1
        matrix[target][source] = 1
    elif kind == "scale":
        matrix[source][source] = coefficient
    elif kind == "add":
        matrix[source][target] = coefficient
    else:
        raise AssertionError(kind)
    return matrix


def product(operations):
    matrix = eye()
    for kind, source, target, coefficient in operations:
        matrix = matmul(matrix, elementary(kind, source, target, coefficient))
    return matrix


def published_factors(matcher):
    """Same elimination as research/bit-row-route-generator/generator.py:factors."""
    matrix = [row[:] for row in matcher]
    result = []
    for column in range(N):
        pivot = next(row for row in range(column, N) if matrix[row][column] != 0)
        if pivot != column:
            matrix[column], matrix[pivot] = matrix[pivot], matrix[column]
            result.append(("swap", column, pivot, Fraction(1)))
        pivot_value = matrix[column][column]
        if pivot_value != 1:
            matrix[column] = [entry / pivot_value for entry in matrix[column]]
            result.append(("scale", column, column, pivot_value))
        for row in range(N):
            if row == column or matrix[row][column] == 0:
                continue
            coefficient = matrix[row][column]
            matrix[row] = [
                entry - coefficient * base for entry, base in zip(matrix[row], matrix[column])
            ]
            result.append(("add", row, column, coefficient))
    need(matrix == eye(), "published elimination did not reach I")
    return tuple(result)


def inverse_operations(operations):
    inverted = []
    for kind, source, target, coefficient in reversed(operations):
        if kind == "scale":
            coefficient = 1 / coefficient
        elif kind == "add":
            coefficient = -coefficient
        inverted.append((kind, source, target, coefficient))
    return tuple(inverted)


def swap_free_right_word(matcher):
    """Zero-swap elimination, returned as chronological right factors.

    The left reduction clears S to I. Reversing those row operations and
    converting each left add (row_t += c row_s) into the column update
    (column_s += c column_t) is the right word whose product is S.
    """
    matrix = [row[:] for row in matcher]
    reduction = []
    for column in range(N):
        if matrix[column][column] == 0:
            donor = next(row for row in range(column + 1, N) if matrix[row][column] != 0)
            for index in range(N):
                matrix[column][index] += matrix[donor][index]
            reduction.append(("add", column, donor, Fraction(1)))
        if matrix[column][column] != 1:
            coefficient = 1 / matrix[column][column]
            for index in range(N):
                matrix[column][index] *= coefficient
            reduction.append(("scale", column, coefficient))
        for row in range(column + 1, N):
            if matrix[row][column] == 0:
                continue
            coefficient = -matrix[row][column]
            for index in range(N):
                matrix[row][index] += coefficient * matrix[column][index]
            reduction.append(("add", row, column, coefficient))
    for column in range(N - 1, -1, -1):
        for row in range(column):
            if matrix[row][column] == 0:
                continue
            coefficient = -matrix[row][column]
            for index in range(N):
                matrix[row][index] += coefficient * matrix[column][index]
            reduction.append(("add", row, column, coefficient))
    need(matrix == eye(), "swap-free reduction did not reach I")
    # Sequential left multiplication applies the inverse of the last reduction
    # step first. The right product that equals S applies that same inverse
    # last, so the returned word is the reverse of the left-operation order.
    left_word = []
    for operation in reversed(reduction):
        if operation[0] == "add":
            target, source, coefficient = operation[1:]
            # Left row_target += c row_source is the column update
            # column_source += c column_target.
            left_word.append(("add", target, source, -coefficient))
        else:
            target, coefficient = operation[1:]
            left_word.append(("scale", target, target, 1 / coefficient))
    return tuple(reversed(left_word))


def is_earlier(operation):
    kind, source, target, _coefficient = operation
    return kind == "add" and target < source


def letter_counts(operations):
    counts = Counter(operation[0] for operation in operations)
    early = sum(1 for operation in operations if is_earlier(operation))
    late = counts["add"] - early
    return counts, early, late


def function_body(source, name):
    marker = "def " + name + "("
    start = source.index(marker)
    nxt = source.find("\ndef ", start + 1)
    return source[start:] if nxt < 0 else source[start:nxt]


def inherited_oracle_multiplier(source):
    """Read add_high. Do not assume the two-oracle charge."""
    body = function_body(source, "add_high")
    early = body.index("if high==1:return source")
    calls = [line.strip() for line in body.splitlines() if "completed_swap_oracle(" in line]
    need(len(calls) == 2, "add_high oracle count changed: %s" % calls)
    need(all(line.startswith("if reversed_fields:") for line in calls),
         "an oracle call is not guarded by reversed_fields")
    need(body.index("completed_swap_oracle(") > early,
         "the high==1 return must precede the oracle calls")
    oracle = function_body(source, "completed_swap_oracle")
    need("charged as T_old, never as a linear stream primitive." in oracle,
         "oracle tariff sentence missing")
    need("meter.ordinary.append" in oracle, "oracle does not record an ordinary call")
    need("transitions" not in oracle, "oracle text now states a transition tariff")
    return len(calls)


def expand_ordinary_calls(swaps, early, multiplier, width):
    """Mirror the generator loops: two directions, n=8f rows, f lanes."""
    calls = 0
    dimension = 8 * width
    for _direction in (1, -1):
        for _letter in range(swaps):
            for _row in range(dimension):
                for _lane in range(width):
                    calls += 1
        for _letter in range(early):
            for _row in range(dimension):
                for _lane in range(width):
                    calls += multiplier
    return calls


def closed_ordinary_calls(swaps, early, multiplier, width):
    return (swaps + multiplier * early) * 16 * width * width


def main():
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    matcher = rows_of(payload["matcher"])
    streams = STREAMS.read_text(encoding="utf-8")
    generator = GENERATOR.read_text(encoding="utf-8")
    scaling = SCALING.read_text(encoding="utf-8")
    inplace = INPLACE.read_text(encoding="utf-8")
    affine = AFFINE.read_text(encoding="utf-8")
    earlier_proof = EARLIER.read_text(encoding="utf-8")

    multiplier = inherited_oracle_multiplier(streams)
    need(multiplier == 2, "inherited reversed-field charge is no longer two ordinary calls")
    need("a=row*n+i*f+lane;b=row*n+j*f+lane" in generator, "address formula changed")
    need("emit('ordered_shift',b,a,coefficient=z)" in generator,
         "ordered_shift target/source order changed")
    need("else:emit('older_full_swap',a,b)" in generator, "swap emission changed")
    need("elif kind=='scale':emit('unit_scale',a,coefficient=z)" in generator,
         "scale emission changed")
    need("1/z if kind=='scale' else -z if kind=='add'" in generator,
         "inverse no longer preserves the address pair")
    need("physical_tape_cost_closed=False" in generator,
         "generator now claims a closed tape tariff")
    need("physical preparation time and tape realization remain charged P2 obligations"
         in generator, "coefficient-preparation obligation missing")
    need("'older_full_swap':'P2 older completed ordinary interchange at e=w-1 radix-q digits'"
         in generator, "swap primitive is no longer the P2 ordinary interchange")

    family_text = "2,1/2,-1,-2,-1/2"
    need(family_text in scaling, "signed-dyadic coefficient family missing")
    need("2048V transitions and64V visited cells" in scaling, "scale transition bound missing")
    need("V=PQS" in scaling, "scale volume missing")
    priced = {Fraction(part) for part in family_text.split(",")}
    need("all0<=c,C<Q" in inplace, "in-place coefficient domain missing")
    need("1024V transitions" in inplace and "V=P Q^2 G S" in inplace,
         "in-place shear bound missing")
    need("1024V transitions and 64V visited cells" in affine, "affine shear bound missing")
    need("supplied descriptors; preparing other rational coefficients remains a caller"
         in affine, "descriptor-preparation gap missing")
    need("call records two `completed_swap_oracle` invocations. The forward shear"
         in earlier_proof, "published two-oracle sentence missing")
    need("records none. No fixed-tape transition bill for that oracle is claimed."
         in earlier_proof, "missing statement that T_old has no transition bill")
    need("earlier-target sites = 2 * 4 * 8 f² = 64 f²," in earlier_proof,
         "published earlier-site anchor missing")
    need("later-target sites   = 2 * 10 * 8 f² = 160 f²." in earlier_proof,
         "published later-site anchor missing")

    published = published_factors(matcher)
    published_counts, published_early, published_late = letter_counts(published)
    need(published_counts == Counter({"swap": 5, "scale": 5, "add": 14}),
         "published letter counts changed")
    need((published_early, published_late) == (4, 10),
         "published earlier/later split is not the anchored 4/10")
    need(product(published) == matcher, "published right word is not S")
    published_inverse = inverse_operations(published)
    need(product(published_inverse) == inverse(matcher), "published inverse is not S^-1")
    _, inverse_early, inverse_late = letter_counts(published_inverse)
    need((inverse_early, inverse_late) == (published_early, published_late),
         "inverse changed the published address comparison")

    swap_free = swap_free_right_word(matcher)
    swap_counts, swap_early, swap_late = letter_counts(swap_free)
    need(swap_counts == Counter({"swap": 0, "scale": 7, "add": 27}),
         "swap-free shape changed")
    need((swap_early, swap_late) == (10, 17), "swap-free earlier/later split changed")
    need(product(swap_free) == matcher, "swap-free right word is not S")
    swap_inverse = inverse_operations(swap_free)
    need(product(swap_inverse) == inverse(matcher), "swap-free inverse is not S^-1")
    _, swap_inverse_early, _swap_inverse_late = letter_counts(swap_inverse)
    need(swap_inverse_early == swap_early, "inverse changed the swap-free address comparison")

    def coefficients(operations, kind):
        return [coefficient for op_kind, _source, _target, coefficient in operations if op_kind == kind]

    for word in (published, published_inverse, swap_free, swap_inverse):
        need(set(coefficients(word, "scale")) <= priced,
             "a scale coefficient leaves the priced signed-dyadic family")
        shear_values = coefficients(word, "add")
        need(all(abs(value) in (1, 2, Fraction(1, 2)) for value in shear_values),
             "a shear coefficient leaves the checked residue family")

    ledger = payload["selected_route_pair_high_matrix_ledger"]
    need(ledger["ordinary_chunk_interchanges"] == 80, "pinned swap ledger changed")
    need(ledger["fixed_unit_scalings"] == 80, "pinned scale ledger changed")
    need(ledger["linear_ordered_shifts"] == 224, "pinned shift ledger changed")

    for width in (1, 2, 3):
        published_calls = expand_ordinary_calls(5, 4, multiplier, width)
        swap_calls = expand_ordinary_calls(0, 10, multiplier, width)
        need(published_calls == closed_ordinary_calls(5, 4, multiplier, width) == 208 * width * width,
             "published ordinary-call formula mismatch at f=%s" % width)
        need(swap_calls == closed_ordinary_calls(0, 10, multiplier, width) == 320 * width * width,
             "swap-free ordinary-call formula mismatch at f=%s" % width)
        published_swap_sites = 80 * width * width
        need(swap_calls > published_calls > published_swap_sites,
             "swap-free ordinary bill is no longer strictly worse")
        need(not swap_calls < 80, "swap-free bill beat the f=1 ledger value 80")
        naive_zero_swap_bill = expand_ordinary_calls(0, 10, 0, width)
        need(naive_zero_swap_bill == 0 < 80 <= swap_calls,
             "zero-oracle reading no longer differs from the inherited charge")

    # The reversed address test does not reproduce the anchored 4/10 split.
    reversed_early = sum(
        1 for kind, source, target, _coefficient in published
        if kind == "add" and target > source
    )
    need(reversed_early == 10, "reversed address test unexpectedly matched 4 early letters")

    dropped = swap_free[:-1]
    need(product(dropped) != matcher, "dropping the last factor still realized S")
    shear_at = next(index for index in range(len(swap_free) - 1, -1, -1) if swap_free[index][0] == "add")
    kind, source, target, coefficient = swap_free[shear_at]
    mutated = swap_free[:shear_at] + ((kind, source, target, coefficient + 1),) + swap_free[shear_at + 1:]
    need(product(mutated) != matcher, "a shear coefficient change still realized S")

    # One later shear has no ordinary call. One earlier shear has two per site.
    later = expand_ordinary_calls(0, 0, multiplier, 1)
    one_early = expand_ordinary_calls(0, 1, multiplier, 1)
    need(later == 0 and one_early == 32, "synthetic earlier/later charges changed")

    # Sufficient affine charges, kept in their own volume units. These are not
    # added to T_old: the oracle proof says that transition bill is unclaimed.
    scale_sites = {"published": 80, "swap_free": 112}
    shear_sites = {"published": 224, "swap_free": 432}
    need(5 * 16 == scale_sites["published"] and 7 * 16 == scale_sites["swap_free"],
         "scale site totals drifted")
    need(14 * 16 == shear_sites["published"] and 27 * 16 == shear_sites["swap_free"],
         "shear site totals drifted")
    scale_bound = {name: sites * 2048 for name, sites in scale_sites.items()}
    shear_bound = {name: sites * 1024 for name, sites in shear_sites.items()}
    need(scale_bound["swap_free"] > scale_bound["published"],
         "swap-free scale sufficient charge is not larger")
    need(shear_bound["swap_free"] > shear_bound["published"],
         "swap-free shear sufficient charge is not larger")
    need(scale_bound["published"] == 163840 and shear_bound["published"] == 229376,
         "published sufficient charges drifted")

    print(
        "PASS_HELPER462_P2_ORDINARY_BILL"
        " oracle_multiplier=2"
        " published_ordinary=208*f^2"
        " swap_free_ordinary=320*f^2"
        " published_swap_sites=80*f^2"
        " beats_published=0"
        " beats_80=0"
        " scale_sufficient_f1=163840:229376"
        " shear_sufficient_f1=229376:442368"
        " transition_bill_for_T_old=missing"
        " no_new_kappa=1"
    )


if __name__ == "__main__":
    main()
