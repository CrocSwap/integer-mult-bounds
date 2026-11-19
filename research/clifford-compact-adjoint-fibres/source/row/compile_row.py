"""Compile the shear-character certificate in PR7799 into signed Bell reads.

Binary vectors have four low Z bits and four high X bits, least significant
bit for qubit one. A matrix is the tuple of images of the standard basis.
apoursh, with substantial OpenAI Codex and separate agent assistance.
Apache-2.0. The seed, character cases and plane selection are from PR7799.
"""
import argparse
from collections import Counter, defaultdict
from functools import cache
from itertools import combinations, combinations_with_replacement
import json
from typing import NamedTuple


IDENTITY = tuple(1 << i for i in range(8))
DENOMINATOR = 1024
SEED = (0, 1, 2, 4, 8, 128)
UPPER = tuple(combinations_with_replacement(range(4), 2))


class Term(NamedTuple):
    numerator: int
    input_map: tuple[int, ...]
    output_map: tuple[int, ...]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def apply(columns, vector):
    result = 0
    while vector:
        bit = vector & -vector
        result ^= columns[bit.bit_length() - 1]
        vector ^= bit
    return result


def compose(left, right):
    return tuple(apply(left, v) for v in right)


def pairing(u, v):
    return (((u >> 4) & v) ^ ((v >> 4) & u)).bit_count() % 2


def span(basis):
    points = [0]
    for v in basis:
        points += [u ^ v for u in points]
    return points


def is_symplectic(matrix):
    return (len(matrix) == 8 and all(isinstance(v, int) and 0 <= v < 256 for v in matrix)
            and all(pairing(matrix[i], matrix[j]) == pairing(IDENTITY[i], IDENTITY[j])
                    for i, j in combinations(range(8), 2)))


@cache
def shear(mask):
    """Send (z,x) to (z+B x,x), with B's upper triangle given by mask."""
    result = list(IDENTITY)
    for index, (i, j) in enumerate(UPPER):
        if mask & (1 << index):
            result[4 + i] ^= 1 << j
            if i != j:
                result[4 + j] ^= 1 << i
    return tuple(result)


def pair_mask(u, v):
    return sum(((((u >> i) & (v >> j)) ^ ((u >> j) & (v >> i))) & 1) << k
               for k, (i, j) in enumerate(UPPER))


def quadratic_address(v):
    return sum(1 << k for k, (i, j) in enumerate(UPPER) if v & (1 << i) and v & (1 << j))


def select_plane(ch):
    # Match the deterministic binary ordering used by the PR7799 verifier.
    values = tuple((ch & quadratic_address(v)).bit_count() % 2 for v in range(16))

    def polar(u, v):
        return values[u] ^ values[v] ^ values[u ^ v]

    if any(all(polar(v, b) == 0 for b in (1, 2, 4, 8)) for v in range(1, 16)):
        return next(w for w in combinations(range(1, 16), 3)
                    if len(set(span(w))) == 8 and all(polar(i, j) == 0 for i, j in combinations(w, 2)))
    r = next(v for v in range(1, 16) if values[v] == 0)
    hyperplane = [u for u in range(16) if polar(r, u) == 0]
    z2 = next(v for v in hyperplane if v not in (0, r))
    dual = next(x for x in range(1, 16) if all((x & v).bit_count() % 2 == 0 for v in hyperplane))
    return r, z2, dual << 4


def canonical_basis(points):
    basis = []
    for v in sorted(points):
        if v not in span(basis):
            basis.append(v)
    return tuple(basis)


def extend_basis(w):
    z = list(w)
    z.append(next(v for v in range(1, 256) if v not in span(z) and all(pairing(v, u) == 0 for u in z)))
    x = []
    for i in range(4):
        x.append(next(v for v in range(1, 256)
                      if all(pairing(v, u) == int(i == j) for j, u in enumerate(z))
                      and all(pairing(v, b) == 0 for b in x)))
    matrix = tuple(z + x)
    require(is_symplectic(matrix), "plane transporter is not symplectic")
    return matrix


def walsh(characters):
    values = [0] * 1024
    for ch in characters:
        values[ch] = 1
    step = 1
    while step < len(values):
        for start in range(0, len(values), 2 * step):
            for i in range(start, start + step):
                j = i + step
                values[i], values[j] = values[i] + values[j], values[i] - values[j]
        step *= 2
    return values


def normalizer_representatives(w, p_basis):
    if len(p_basis) == 3:
        return [0]
    dual = next(v for v in w if v >> 4)
    p = span(p_basis)
    representatives = {}
    for mask in range(1024):
        b_dual = apply(shear(mask), dual) ^ dual
        key = min(b_dual ^ u for u in p)
        representatives.setdefault(key, mask)
    require(len(representatives) == 4, "mixed-plane normalizer index")
    return sorted(representatives.values())


def iter_terms(target=IDENTITY):
    """Yield numerator / DENOMINATOR weights on transported coset *sums*.

    Apply the source and target transporters to SEED via the affine Bell
    action and undo the singleton/transport phases as specified in PROOF.md.
    The weighted sum of those 16-by-16 blocks is the target's fibre matrix
    on the image of the observation map. Target defaults to the identity.
    """
    require(is_symplectic(target), "invalid target symplectic matrix")
    by_plane = defaultdict(list)
    for ch in range(1024):
        by_plane[canonical_basis(span(select_plane(ch)))].append(ch)
    for w, chars in sorted(by_plane.items()):
        pure = tuple(z for z in w if z < 16)
        h = span(tuple(pair_mask(u, v) for u, v in combinations(pure, 2)))
        representatives = normalizer_representatives(w, pure)
        g = extend_basis(w)
        values = walsh(chars)
        divisor = 4 if len(pure) == 2 else 1
        for delta, value in enumerate(values):
            if not value or delta != min(delta ^ offset for offset in h):
                continue
            require(value % divisor == 0, "coefficient needs a finer denominator")
            for b in representatives:
                right = compose(shear(b), g)
                left = compose(target, compose(shear(delta ^ b), g))
                yield Term(value // divisor, right, left)


def seed_subgroup():
    hats = [pair_mask(1 << i, 1 << j) for i, j in combinations(range(3), 2)]
    return tuple(shear(mask) for mask in span(hats))


@cache
def inverse(matrix):
    # Binary symplectic inverse from the images of a paired basis.
    return tuple(sum(pairing(matrix[i ^ 4], u) << i for i in range(8)) for u in IDENTITY)


def bell_tuple(matrix):
    # q(L v)=q(v) gives <u,b> = q(u)+q(S^-1 u), hence b from the
    # images of basis vectors under the inverse. q(e_j)=0.
    inv = inverse(matrix)
    offset = 0
    for j in range(8):
        v = inv[j ^ 4]
        offset |= (((v >> 4) & v).bit_count() % 2) << j
    return tuple(apply(matrix, v) ^ offset for v in SEED)


def check(target):
    accum = Counter()
    seen = set()
    terms = list(iter_terms(target))
    subgroup = seed_subgroup()
    for weight, right, left in terms:
        products = {compose(left, compose(c, inverse(right))) for c in subgroup}
        key = frozenset(products)
        require(len(products) == 8 and key not in seen, "repeated or malformed coset")
        seen.add(key)
        for item in products:
            accum[item] += weight
    require({k: v for k, v in accum.items() if v} == {target: DENOMINATOR},
            "signed coset sum is not the single target")
    require(len(accum) == 8304, "expanded union size")
    mass_by_input = Counter()
    for term in terms:
        mass_by_input[bell_tuple(term.input_map)] += abs(term.numerator)
    require(Counter(mass_by_input.values()) == {128: 29, 192: 10, 224: 8, 240: 8, 288: 12},
            "absolute coefficient mass by input")
    require(8 * sum(m*m for m in mass_by_input.values()) * 64 == 1319 * DENOMINATOR**2,
            "simultaneous squared norm bound")
    numerators = [term.numerator for term in terms]
    require(len(terms) == 4265 and sum(abs(w) for w in numerators) == 12800,
            "row sparsity or absolute mass")
    require(sum(w*w for w in numerators) == DENOMINATOR**2 // 8, "squared row mass")
    require(any(w % 2 for w in numerators), "denominator 1024 not attained")
    return len(accum)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="emit the identity row as JSON lines")
    args = parser.parse_args()
    if args.emit:
        for term in iter_terms():
            print(json.dumps(term._asdict(), separators=(",", ":")))
        return
    covered = check(IDENTITY)
    # Hadamard on each qubit swaps the two coordinate registers.
    require(check(IDENTITY[4:] + IDENTITY[:4]) == covered, "translated support")
    print(f"PASS_COMPRESSED_CLIFFORD_ROW terms=4265 group_terms=34120 union={covered}"
          " denominator=1024 absolute_mass=25/2 squared_mass=1/8 row_norm_squared=2^45")


if __name__ == "__main__":
    main()
