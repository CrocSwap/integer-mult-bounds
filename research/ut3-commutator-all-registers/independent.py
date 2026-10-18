#!/usr/bin/env python3
"""Code-disjoint finite checks using binary address matrices and regular action.

No group triples, formal group-algebra arithmetic, producer imports, or external
packages are used.  Finite success supports the fixtures, not the universal
rank proof.  Matrix products use the written left-to-right factor order.

steph4n-gh, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from dataclasses import dataclass
import hashlib
import json
import random


@dataclass(frozen=True)
class Matrix:
    """Exact GF(2) matrix, storing each row as a bitset (bit j = column j)."""

    rows: tuple
    width: int

    def __post_init__(self):
        if self.width < 0 or any(x < 0 or x >> self.width for x in self.rows):
            raise ValueError("invalid binary matrix")

    @property
    def height(self):
        return len(self.rows)

    def __xor__(self, other):
        require((self.height, self.width) == (other.height, other.width),
                "addition dimensions")
        return Matrix(tuple(a ^ b for a, b in zip(self.rows, other.rows)), self.width)

    def __matmul__(self, other):
        require(self.width == other.height, "product dimensions")
        result = []
        for row in self.rows:
            total = 0
            while row:
                bit = row & -row
                total ^= other.rows[bit.bit_length() - 1]
                row ^= bit
            result.append(total)
        return Matrix(tuple(result), other.width)

    def rank(self):
        pivots = {}
        for row in self.rows:
            while row:
                col = row.bit_length() - 1
                if col not in pivots:
                    pivots[col] = row
                    break
                row ^= pivots[col]
        return len(pivots)

    def transpose(self):
        return Matrix(tuple(sum(((row >> j) & 1) << i
                                for i, row in enumerate(self.rows))
                            for j in range(self.width)), self.height)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identity(n):
    return Matrix(tuple(1 << i for i in range(n)), n)


def zero(height, width):
    return Matrix((0,) * height, width)


def unit(n, i, j):
    return Matrix(tuple((1 << j) if row == i else 0 for row in range(n)), n)


def xor_sum(matrices, height, width):
    out = zero(height, width)
    for matrix in matrices:
        out = out ^ matrix
    return out


def kron(left, right):
    rows = []
    for outer in left.rows:
        for inner in right.rows:
            row = 0
            for j in range(left.width):
                if (outer >> j) & 1:
                    row ^= inner << (j * right.width)
            rows.append(row)
    return Matrix(tuple(rows), left.width * right.width)


def inverse(matrix):
    n = matrix.height
    require(n == matrix.width, "inverse needs a square matrix")
    rows = [row | (1 << (n + i)) for i, row in enumerate(matrix.rows)]
    for col in range(n):
        pivot = next((i for i in range(col, n) if (rows[i] >> col) & 1), None)
        require(pivot is not None, "singular scalar change of basis")
        rows[col], rows[pivot] = rows[pivot], rows[col]
        for i in range(n):
            if i != col and ((rows[i] >> col) & 1):
                rows[i] ^= rows[col]
    out = Matrix(tuple(row >> n for row in rows), n)
    require(matrix @ out == identity(n) and out @ matrix == identity(n),
            "inverse round trip")
    return out


def product(factors, n):
    out = identity(n)
    for factor in factors:
        out = out @ factor
    return out


def address_group():
    """Enumerate the group by closure of concrete three-by-three matrices."""
    eye = identity(3)
    generators = {"a": eye ^ unit(3, 0, 1), "b": eye ^ unit(3, 1, 2)}
    words = {eye: ""}
    queue = [eye]
    for element in queue:
        for label in ("a", "b"):
            new = element @ generators[label]
            if new not in words:
                words[new] = words[element] + label
                queue.append(new)
    require(len(queue) == 8, "UT3 order")
    natural = {element: product((generators[label] for label in word), 3)
               for element, word in words.items()}
    swapped = {element: product((generators[{"a": "b", "b": "a"}[label]]
                                for label in word), 3)
               for element, word in words.items()}
    indices = {element: index for index, element in enumerate(queue)}
    regular = {}
    for element in queue:
        rows = [0] * 8
        for column, basis in enumerate(queue):
            rows[indices[element @ basis]] |= 1 << column
        regular[element] = Matrix(tuple(rows), 8)
    require(len(set(regular.values())) == 8, "faithful regular representation")
    flattened = Matrix(tuple(sum(row << (8 * i) for i, row in enumerate(g.rows))
                             for g in regular.values()), 64)
    require(flattened.rank() == 8, "group-algebra regular map is not injective")
    for left in queue:
        for right in queue:
            composed = left @ right
            require(composed in indices, "group closure")
            require(swapped[composed] == swapped[left] @ swapped[right],
                    "swapped homomorphism")
            require(regular[composed] == regular[left] @ regular[right],
                    "regular homomorphism")
            require(natural[composed] == natural[left] @ natural[right],
                    "natural homomorphism from independently enumerated words")
    central = product((generators[x] for x in "abab"), 3)
    require(central == eye ^ unit(3, 0, 2), "natural central image")
    require(swapped[central] == eye ^ unit(3, 0, 2), "swapped central image")
    require(central != eye and central @ central == eye, "central involution")
    require(all(central @ g == g @ central for g in queue), "centrality")
    # A single flipped regular-action entry must violate a multiplication law.
    broken = dict(regular)
    original = broken[generators["a"]]
    changed_rows = list(original.rows)
    changed_rows[0] ^= 1
    broken[generators["a"]] = Matrix(tuple(changed_rows), 8)
    require(any(broken[x @ y] != broken[x] @ broken[y]
                for x in queue for y in queue), "corrupted regular matrix accepted")
    return generators, swapped, regular, central


def basis_change(n, variant):
    out = identity(n)
    if variant and n > 1:
        # Common public fixture: factors are multiplied in displayed order.
        for i in range(n):
            out = out @ (identity(n) ^ unit(n, i, (i + 1) % n))
    if variant == 2 and n > 1:
        for i in range(n - 1, 0, -1):
            out = out @ (identity(n) ^ unit(n, i, i - 1))
    return out


def projectors(change):
    n = change.height
    back = inverse(change)
    out = []
    for i in range(n):
        column = Matrix(tuple((row >> i) & 1 for row in change.rows), 1)
        row = Matrix((back.rows[i],), n)
        p = column @ row
        require(p.rank() == 1 and p @ p == p, "rank-one idempotent premise")
        require(row @ column == identity(1), "dual scalar vectors")
        require(p == change @ unit(n, i, i) @ back, "projector conjugation")
        out.append((p, column, row))
    require(xor_sum((p for p, _, _ in out), n, n) == identity(n),
            "projector resolution")
    return out


def lifted_word(word, representation, generators, roles):
    dimension = next(iter(representation.values())).height
    eye = identity(roles * dimension)
    return product((eye ^ kron(p, representation[generators[label]] ^ identity(dimension))
                    for label, p, _, _ in word), roles * dimension)


def block(matrix, address_row, address_col, roles):
    """Extract a role matrix from the role-major natural address operator."""
    return Matrix(tuple(sum(((matrix.rows[3 * i + address_row] >>
                              (3 * j + address_col)) & 1) << j
                            for j in range(roles))
                        for i in range(roles)), roles)


def rank_premises(word, generators, swapped, roles):
    natural = {g: g for g in swapped}
    full = lifted_word(word, natural, generators, roles)
    reverse = lifted_word(word, swapped, generators, roles)
    sums = {label: xor_sum((p for tag, p, _, _ in word if tag == label), roles, roles)
            for label in ("a", "b")}
    c = xor_sum((p @ q for i, (tag, p, _, _) in enumerate(word)
                 for label, q, _, _ in word[i + 1:] if tag == "a" and label == "b"),
                roles, roles)
    cp = xor_sum((p @ q for i, (tag, p, _, _) in enumerate(word)
                  for label, q, _, _ in word[i + 1:] if tag == "b" and label == "a"),
                 roles, roles)
    expected = [[identity(roles), sums["a"], c],
                [zero(roles, roles), identity(roles), sums["b"]],
                [zero(roles, roles), zero(roles, roles), identity(roles)]]
    reverse_expected = [[identity(roles), sums["b"], cp],
                        [zero(roles, roles), identity(roles), sums["a"]],
                        [zero(roles, roles), zero(roles, roles), identity(roles)]]
    for i in range(3):
        for j in range(3):
            require(block(full, i, j, roles) == expected[i][j],
                    "natural coefficient expansion")
            require(block(reverse, i, j, roles) == reverse_expected[i][j],
                    "swapped coefficient expansion")
    ranks = {}
    for label, column_target, row_target in (("a", c, cp), ("b", cp, c)):
        other = {"a": "b", "b": "a"}[label]
        selected = [(i, u, v) for i, (tag, _, u, v) in enumerate(word) if tag == label]
        count = len(selected)
        x = Matrix(tuple(sum(u.rows[row] << i for i, (_, u, _) in enumerate(selected))
                         for row in range(roles)), count)
        y = Matrix(tuple(v.rows[0] for _, _, v in selected), roles)
        right_rows = []
        left_columns = []
        for index, u, v in selected:
            suffix = xor_sum((p for tag, p, _, _ in word[index + 1:] if tag == other),
                             roles, roles)
            prefix = xor_sum((p for tag, p, _, _ in word[:index] if tag == other),
                             roles, roles)
            right_rows.append((v @ suffix).rows[0])
            left_columns.append(prefix @ u)
        right = Matrix(tuple(right_rows), roles)
        left = Matrix(tuple(sum(u.rows[row] << i for i, u in enumerate(left_columns))
                            for row in range(roles)), count)
        require(x @ y == sums[label], "rank-factorization zero-sum premise")
        require(x @ right == column_target, "column-span factorization")
        require(left @ y == row_target, "row-span factorization")
        xr, yr, sr = x.rank(), y.rank(), sums[label].rank()
        require(column_target.rank() <= xr and row_target.rank() <= yr,
                "rank monotonicity")
        require(xr + yr <= count + sr, "Sylvester rank inequality")
        if sums[label] == zero(roles, roles):
            require(xr + yr <= count, "zero-sum dimension premise")
        ranks[label] = {"calls": count, "column_rank": xr, "row_rank": yr}
    return sums, c, cp, ranks


def run():
    generators, swapped, regular, central = address_group()
    cases = []
    matrix_hash = hashlib.sha256()
    negatives = {"missing_call": 0, "wrong_label": 0, "extra_dirty_target": 0,
                 "corrupted_regular_matrix": 1, "representation_invisible_dirty_shear": 0}
    # Both small representations have a common kernel.  The regular one must
    # detect this nonzero group-algebra element, not certify its image as zero.
    regular_kernel = ((regular[generators["a"]] ^ identity(8)) @
                      (regular[central] ^ identity(8)))
    natural_kernel = ((generators["a"] ^ identity(3)) @ (central ^ identity(3)))
    swapped_kernel = ((swapped[generators["a"]] ^ identity(3)) @
                      (swapped[central] ^ identity(3)))
    require(regular_kernel != zero(8, 8), "formal kernel element vanished in regular action")
    require(natural_kernel == swapped_kernel == zero(3, 3), "common representation kernel")
    arbitrary_cases = 0
    rng = random.Random(14)
    for roles in range(1, 6):
        for variant in range(3):
            change = basis_change(roles, variant)
            ps = projectors(change)
            for targets in range(1, roles + 1):
                ptarget = xor_sum((p for p, _, _ in ps[:targets]), roles, roles)
                word = [(label, p, u, v) for p, u, v in ps[:targets] for label in "abab"]
                actual = lifted_word(word, regular, generators, roles)
                expected = identity(8 * roles) ^ kron(ptarget, regular[central] ^ identity(8))
                require(actual == expected, "faithful full operator endpoint")
                require(ptarget.rank() == targets, "target rank")
                # Conjugating back exposes every arbitrary dirty spectator as I_8.
                original_basis = kron(inverse(change), identity(8)) @ actual @ kron(change, identity(8))
                coordinate_target = xor_sum((unit(roles, i, i) for i in range(targets)), roles, roles)
                require(original_basis == identity(8 * roles) ^
                        kron(coordinate_target, regular[central] ^ identity(8)),
                        "dirty spectators not restored")
                sums, c, cp, ranks = rank_premises(word, generators, swapped, roles)
                require(sums["a"] == sums["b"] == zero(roles, roles), "endpoint zero sums")
                require(c == cp == ptarget, "both endpoint coefficients")
                for label in ("a", "b"):
                    require(ranks[label] == {"calls": 2 * targets, "column_rank": targets,
                                             "row_rank": targets}, "sharp witness ranks")
                require(lifted_word(word[:-1], regular, generators, roles) != expected,
                        "missing-call control accepted")
                negatives["missing_call"] += 1
                wrong = [("b", word[0][1], word[0][2], word[0][3])] + word[1:]
                require(lifted_word(wrong, regular, generators, roles) != expected,
                        "wrong-label control accepted")
                negatives["wrong_label"] += 1
                if targets < roles:
                    bad_target = expected ^ kron(ps[targets][0], regular[central] ^ identity(8))
                    require(actual != bad_target, "extra dirty target control accepted")
                    negatives["extra_dirty_target"] += 1
                    dirty_shear_role = change @ unit(roles, roles - 1, 0) @ inverse(change)
                    shear = identity(8 * roles) ^ kron(dirty_shear_role, regular_kernel)
                    require(shear @ shear == identity(8 * roles), "dirty shear involution")
                    mutant = actual @ shear
                    require(mutant != expected, "representation-invisible dirty shear accepted")
                    require(identity(3 * roles) ^ kron(dirty_shear_role, natural_kernel) ==
                            identity(3 * roles), "natural image should miss dirty shear")
                    require(identity(3 * roles) ^ kron(dirty_shear_role, swapped_kernel) ==
                            identity(3 * roles), "swapped image should miss dirty shear")
                    negatives["representation_invisible_dirty_shear"] += 1
                matrix_hash.update(json.dumps([roles, targets, variant, actual.rows],
                                              separators=(",", ":")).encode())
                cases.append({"roles": roles, "targets": targets, "basis_variant": variant,
                              "paid_calls": len(word), "a_calls": ranks["a"]["calls"],
                              "b_calls": ranks["b"]["calls"]})
            # These deliberately need not restore spectators or reach a target.
            # They check the expansion and factorization independently of abab.
            for length in range(13):
                pool = ps + projectors(basis_change(roles, (variant + 1) % 3))
                word = [(rng.choice(("a", "b")), *rng.choice(pool)) for _ in range(length)]
                rank_premises(word, generators, swapped, roles)
                arbitrary_cases += 1
    return {
        "schema": "ut3-independent-binary-matrix-check-v1",
        "arithmetic": "GF(2), exact integer bitsets",
        "group_elements": 8,
        "regular_group_algebra_basis_rank": 8,
        "homomorphism_products_per_representation": 64,
        "representations": ["natural 3x3", "generator-swapped 3x3", "faithful regular 8x8"],
        "natural_and_swapped_c": "I_3 + E_02",
        "attaining_operator_cases": len(cases),
        "arbitrary_word_factorization_cases": arbitrary_cases,
        "maximum_regular_operator_dimension": 40,
        "roles_checked": [1, 2, 3, 4, 5],
        "targets_checked": "every 1 <= k <= r",
        "scalar_basis_variants_per_pair": 3,
        "negative_controls_rejected": negatives,
        "exact_operators_sha256": matrix_hash.hexdigest(),
        "cases": cases,
        "scope": "Finite exact checks only; the all-register theorem requires the written proof."
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
