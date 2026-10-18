"""Exact meet-in-the-middle search over F2[UT3(F3)]."""

from hashlib import sha256
import json
from pathlib import Path

# H=UT3(F3), encoded by (a,b,c) -> 9*a+3*b+c.  Multiplication is
# (a,b,c)(a',b',c')=(a+a', b+b', c+c'+a*b') over F3.
def elem(a, b, c):
    return (a % 3) * 9 + (b % 3) * 3 + (c % 3)


def decode(g):
    return g // 9, (g // 3) % 3, g % 3


def group_mul(g, h):
    a, b, c = decode(g)
    ap, bp, cp = decode(h)
    return elem(a + ap, b + bp, c + cp + a * bp)


def group_inverse(g):
    a, b, c = decode(g)
    return elem(-a, -b, -c + a * b)


def group_pow(g, n):
    out = 0
    for _ in range(n):
        out = group_mul(out, g)
    return out


IDENTITY = elem(0, 0, 0)
X = elem(1, 0, 0)
X_INV = elem(2, 0, 0)
Y = elem(0, 1, 0)
Y_INV = elem(0, 2, 0)
Z = elem(0, 0, 1)
Z_INV = elem(0, 0, 2)
LABELS = (X, X_INV, Y, Y_INV)
LABEL_INVERSE = {g: group_inverse(g) for g in LABELS}
COMMUTATOR_WORD = (X, Y, X_INV, Y_INV)
REVERSE_COMMUTATOR_WORD = (Y, X, Y_INV, X_INV)


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def group_ring_mul(a, b):
    """Multiply F2[H] elements encoded as 27-bit coefficient masks."""
    result = 0
    left = a
    while left:
        low_left = left & -left
        i = low_left.bit_length() - 1
        right = b
        while right:
            low_right = right & -right
            j = low_right.bit_length() - 1
            result ^= 1 << group_mul(i, j)
            right ^= low_right
        left ^= low_left
    return result


def matrix_multiply(a, b):
    """Ordinary 2x2 matrix multiplication over the noncommutative group ring."""
    return tuple(
        group_ring_mul(a[2 * i], b[j]) ^ group_ring_mul(a[2 * i + 1], b[2 + j])
        for i in range(2) for j in range(2)
    )


MATRIX_ID = (1, 0, 0, 1)
TARGET = (1 << Z, 0, 0, 1 << Z)
TARGET_ONE = (1 << Z, 0, 0, 1)


def idempotents():
    result = []
    for u in range(1, 4):
        for v in range(1, 4):
            if ((u & v).bit_count() & 1) == 1:
                result.append((u, v))
    require(len(result) == 6, "wrong number of rank-one idempotents")
    return tuple(result)


IDEMPOTENTS = idempotents()
OPERATIONS = tuple((n, g) for n in IDEMPOTENTS for g in LABELS)


def factor(n, g):
    u, v = n
    delta = (1 << g) ^ 1  # [g] + [e] over F2.
    entries = []
    for i in range(2):
        for j in range(2):
            value = 1 if i == j else 0
            if ((u >> i) & 1) and ((v >> j) & 1):
                value ^= delta
            entries.append(value)
    return tuple(entries)


FACTORS = {op: factor(*op) for op in OPERATIONS}


def matrix_right_factor(matrix, op):
    """Right-multiply by D_N(g)=I+([g]+[e])N, using N=u v^T."""
    u, v = op[0]
    delta = (1 << op[1]) ^ 1
    out = []
    for i in range(2):
        added = 0
        if u & 1:
            added ^= group_ring_mul(matrix[2 * i], delta)
        if u & 2:
            added ^= group_ring_mul(matrix[2 * i + 1], delta)
        for j in range(2):
            value = matrix[2 * i + j]
            if (v >> j) & 1:
                value ^= added
            out.append(value)
    return tuple(out)


def product_of(word):
    result = MATRIX_ID
    for op in word:
        result = matrix_right_factor(result, op)
    return result


def inverse_word(word):
    return tuple((n, LABEL_INVERSE[g]) for n, g in reversed(word))


def state_bytes(matrix):
    return b"".join(value.to_bytes(4, "little") for value in matrix)


def build_layers(max_depth):
    """Exhaustive product states; one representative word per equal state."""
    layers = [{MATRIX_ID: ()}]
    for _depth in range(1, max_depth + 1):
        current = {}
        for matrix, word in layers[-1].items():
            for op in OPERATIONS:
                current.setdefault(matrix_right_factor(matrix, op), word + (op,))
        layers.append(current)
    return layers


def layer_receipts(layers):
    receipts = []
    for depth, layer in enumerate(layers):
        digest = sha256(b"".join(state_bytes(state) for state in sorted(layer))).hexdigest()
        receipts.append((depth, 24 ** depth, len(layer), digest))
    return receipts


def search_upto(layers, maximum, target=TARGET):
    # For a split P S=T, all paid factors are invertible, so S=P^-1 T.
    # Exhaustive reachable-state layers therefore decide every word at each length.
    splits = []
    for length in range(maximum + 1):
        left_len = length // 2
        right_len = length - left_len
        left_layer, right_layer = layers[left_len], layers[right_len]
        checked_prefixes = 0
        for prefix_state, prefix_word in left_layer.items():
            checked_prefixes += 1
            inverse_state = product_of(inverse_word(prefix_word))
            required_suffix = matrix_multiply(inverse_state, target)
            suffix_word = right_layer.get(required_suffix)
            if suffix_word is not None:
                witness = prefix_word + suffix_word
                require(product_of(witness) == target,
                        "meet-in-the-middle witness fails literal product replay")
                splits.append((length, left_len, right_len, len(left_layer), len(right_layer), checked_prefixes, True))
                return witness, splits
        splits.append((length, left_len, right_len, len(left_layer), len(right_layer), checked_prefixes, False))
    return None, splits


def direct_eight_word():
    n00 = (1, 1)
    n11 = (2, 2)
    return tuple((n00, g) for g in COMMUTATOR_WORD) + tuple((n11, g) for g in COMMUTATOR_WORD)


def one_target_four_word():
    return tuple(((1, 1), g) for g in COMMUTATOR_WORD)


def verify_controls(layers):
    # Exact group structure and noncommuting label order.
    require(len({elem(a, b, c) for a in range(3) for b in range(3) for c in range(3)}) == 27,
            "group encoding is not bijective")
    require(group_pow(X, 3) == IDENTITY and group_pow(Y, 3) == IDENTITY,
            "x and y must have order three")
    require(group_pow(Z, 3) == IDENTITY and Z != IDENTITY, "z must have order three")
    comm = IDENTITY
    for g in COMMUTATOR_WORD:
        comm = group_mul(comm, g)
    require(comm == Z, "[x,y] != z")
    reverse = IDENTITY
    for g in REVERSE_COMMUTATOR_WORD:
        reverse = group_mul(reverse, g)
    require(reverse == Z_INV and Z_INV != Z, "reversed commutator did not invert z")
    require(group_mul(X, Y) != group_mul(Y, X), "group multiplication lost noncommutativity")
    require(Z not in LABELS and LABELS == (X, X_INV, Y, Y_INV),
            "the target address was accidentally admitted as a paid label")

    # Projector family and paid-call inverses.
    for u, v in IDEMPOTENTS:
        require((u & v).bit_count() & 1, "rank-one matrix is not idempotent")
        require(any(((u >> i) & 1) and ((v >> j) & 1) for i in range(2) for j in range(2)),
                "zero matrix entered the paid alphabet")
    for op in OPERATIONS:
        inverse = (op[0], LABEL_INVERSE[op[1]])
        require(matrix_multiply(FACTORS[op], FACTORS[inverse]) == MATRIX_ID,
                "paid factor inverse failed")

    # Independently compare the optimized update with full 2x2 matrix products.
    matrix_crosschecks = 0
    for a in OPERATIONS[:12]:
        for b in OPERATIONS[12:24]:
            require(matrix_right_factor(FACTORS[a], b) == matrix_multiply(FACTORS[a], FACTORS[b]),
                    "optimized update disagrees with literal matrix multiplication")
            matrix_crosschecks += 1

    direct = direct_eight_word()
    require(product_of(direct) == TARGET, "direct eight-call positive control failed")
    one_target = one_target_four_word()
    require(product_of(one_target) == TARGET_ONE, "single-target four-call control failed")
    one_target_witness, _ = search_upto(layers, 4, TARGET_ONE)
    require(one_target_witness is not None,
            "meet-in-the-middle missed the known one-target word")
    shortened = one_target[:-1]
    require(product_of(shortened) != TARGET_ONE, "omitted commutator letter control escaped")
    return 6, matrix_crosschecks


def main():
    layers = build_layers(4)
    controls, matrix_crosschecks = verify_controls(layers)
    witness, splits = search_upto(layers, 7)
    receipts = layer_receipts(layers)
    layer_rows = [
        {"depth": d, "raw_words": raw, "unique_states": unique, "sha256_sorted_states": digest}
        for d, raw, unique, digest in receipts
    ]
    split_rows = [
        {"length": n, "left_depth": a, "right_depth": b, "left_states": l,
         "right_states": r, "prefixes_checked": checked, "target_found": found}
        for n, a, b, l, r, checked, found in splits
    ]
    expected_path = Path(__file__).with_name("EXPECTED.json")
    expected = json.loads(expected_path.read_text())
    require(expected["group"] == "UT3(F3)" and expected["group_order"] == 27
            and expected["coefficient_field"] == "F2" and expected["registers"] == 2,
            "receipt model does not match this verifier")
    require(expected["paid_labels"] == ["x", "x^-1", "y", "y^-1"]
            and expected["rank_one_idempotents"] == 6,
            "receipt operation alphabet does not match this verifier")
    require(expected["target"] == "diag([z],[z]) where z=[x,y]"
            and expected["direct_calls"] == 8,
            "receipt target or direct bill does not match this verifier")
    require(expected["layers"] == layer_rows, "reachable-state receipt differs from EXPECTED.json")
    require(expected["length_splits"] == split_rows, "length-split receipt differs from EXPECTED.json")
    require(expected["minimum"] == 8 and expected["max_excluded_length"] == 7,
            "expected result is not the claimed eight-call boundary")
    require(expected["controls"] == {"construction_mutations": 2,
                                    "group_and_algebra_checks": 4,
                                    "matrix_update_crosschecks": 144},
            "receipt control coverage changed")
    if witness is not None:
        print("FOUND_HEISENBERG_WORD length=%d operations=%r" % (len(witness), witness))
        print("state_layers=%r controls=%d matrix_crosschecks=%d" % (receipts, controls, matrix_crosschecks))
        return 0
    require(product_of(direct_eight_word()) == TARGET, "direct upper bound missing")
    print("PASS_HEISENBERG_CENTRAL_PAIR minimum=8 excluded_lengths=0..7 group_order=27 characteristic=2 registers=2 generators=4 idempotents=6 controls=%d matrix_crosschecks=%d state_counts=%r" %
          (controls, matrix_crosschecks, [(r[0], r[2]) for r in receipts]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
