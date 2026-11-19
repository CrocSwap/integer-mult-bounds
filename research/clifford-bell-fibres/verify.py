"""Check the width-13 group algebra certificate over Z[1/2].

All maps below are actual binary linear maps on four Z and four X bits.
apoursh, with substantial OpenAI Codex assistance. Apache-2.0.
"""

from collections import Counter
from fractions import Fraction
from functools import cache
from itertools import combinations, combinations_with_replacement


STANDARD = tuple(1 << i for i in range(8))
PAIRS = tuple(combinations_with_replacement(range(4), 2))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def parity(value):
    return value.bit_count() % 2


def symp(a, b):
    return parity((a & (b >> 4)) ^ ((a >> 4) & b))


def q0(a):
    return parity((a & 15) & (a >> 4))


def linear(columns, mask):
    image = 0
    while mask:
        bit = mask & -mask
        image ^= columns[bit.bit_length() - 1]
        mask ^= bit
    return image


def compose(a, b):
    return tuple(linear(a, x) for x in b)


def span(rows):
    return {linear(rows, mask) for mask in range(1 << len(rows))}


def shear(u, v):
    return tuple(x ^ (symp(v, x) * u) ^ (symp(u, x) * v) for x in STANDARD)


def rank_one(u):
    return tuple(x ^ (symp(u, x) * u) for x in STANDARD)


def commuting_group(generators):
    members = [STANDARD]
    for g in generators:
        require(compose(g, g) == STANDARD, "generator is not an involution")
        require(all(compose(e, g) == compose(g, e) for e in members), "nonabelian generators")
        members.extend([compose(g, e) for e in members])
    require(len(set(members)) == len(members), "dependent group generators")
    return tuple(members)


def alt_group(w):
    require(len(span(w)) == 8 and all(symp(u, v) == 0 for u, v in combinations(w, 2)),
            "W must be an isotropic three-plane")
    return commuting_group([shear(u, v) for u, v in combinations(w, 2)])


def seed_stabilizer():
    # Fixing D pointwise leaves only symmetric shears on its three dual axes.
    generators = [rank_one(1 << i) for i in range(3)]
    seed = (1, 2, 4)
    candidates = commuting_group(generators + [shear(i, j) for i, j in combinations(seed, 2)])
    d = (*seed, 8, 128)
    require(all(all(linear(g, b) == b for b in d) for g in candidates), "D moved")
    fixed = {g for g in candidates if all(q0(linear(g, v)) == q0(v) for v in range(256))}
    require(fixed == set(alt_group(seed)), "incorrect affine Bell tuple stabilizer")
    return len(candidates), len(fixed)


def symmetric_data():
    generators = tuple(rank_one(1 << i) if i == j else shear(1 << i, 1 << j)
                       for i, j in PAIRS)
    # Enumeration in bit-mask order, so each group member has its character address.
    members = commuting_group(generators)
    return generators, {g: mask for mask, g in enumerate(members)}


def quadratic_mask(vector):
    # Address of the symmetric rank-one matrix vector * vector^T.
    return sum(1 << k for k, (i, j) in enumerate(PAIRS)
               if vector & (1 << i) and vector & (1 << j))


def select_plane(values):
    def polar(u, v):
        return values[u ^ v] ^ values[u] ^ values[v]

    radical = [u for u in range(16) if all(not polar(u, v) for v in (1, 2, 4, 8))]
    if len(radical) > 1:
        for plane in combinations(range(1, 16), 3):
            if len(span(plane)) == 8 and all(not polar(u, v) for u, v in combinations(plane, 2)):
                return plane, len(radical)
        raise ValueError("missing isotropic three-plane")

    r = next(v for v in range(1, 16) if values[v] == 0)
    h = {v for v in range(16) if not polar(r, v)}
    z2 = min(h - {0, r})
    # x4 is the covector killing H (nonzero on the fourth basis direction).
    x4 = next(x for x in range(1, 16) if all(not parity(x & z) for z in h))
    return (r, z2, x4 << 4), 1


def extend_basis(w):
    # Produce a full symplectic change of coordinates carrying the seed to W.
    z = list(w)
    z.append(next(v for v in range(1, 256) if v not in span(z) and all(not symp(v, u) for u in z)))
    x = []
    for k in range(4):
        x.append(next(v for v in range(1, 256)
                      if all(symp(v, u) == int(k == j) for j, u in enumerate(z))
                      and all(not symp(v, u) for u in x)))
    columns = tuple(z + x)
    require(len(span(columns)) == 256, "singular change of basis")
    require(all(symp(columns[i], columns[j]) == symp(STANDARD[i], STANDARD[j])
                for i in range(8) for j in range(8)), "basis does not preserve the pairing")
    return columns


def check_fourier_blocks():
    generators, addresses = symmetric_data()
    seed = alt_group((1, 2, 4))

    @cache
    def checked_action(w):
        g = extend_basis(w)
        subgroup = alt_group(w)
        require({compose(c, g) for c in subgroup} == {compose(g, c) for c in seed},
                "subgroup is not the asserted conjugate")
        # Every element here is an involution. Compute all induced generator
        # images by literal 8x8 composition, independent of the Q-selection rule.
        return tuple((addresses.get(c), tuple(addresses[compose(compose(c, a), c)] for a in generators))
                     for c in subgroup)

    by_radical = Counter()
    stabilizer_sizes = Counter()
    moved_characters = 0
    for character in range(1024):
        values = tuple(parity(character & quadratic_mask(v)) for v in range(16))
        w, radical_size = select_plane(values)
        weight = 0
        for address, induced in checked_action(w):
            new_character = sum(parity(character & mask) << j for j, mask in enumerate(induced))
            if new_character != character:
                moved_characters += 1
                continue
            require(address is not None, "non-shear survived the Fourier sandwich")
            weight += (-1) ** parity(address & character)
        require(weight == (2 if radical_size == 1 else 8), "wrong subgroup average")
        by_radical[radical_size] += 1
        stabilizer_sizes[weight] += 1
    require(by_radical == {16: 16, 4: 560, 1: 448}, "quadratic character census")
    require(stabilizer_sizes == {8: 576, 2: 448} and moved_characters == 2688,
            "incomplete sandwich coverage")
    # Completeness of the actual Fourier masks and their inverse over the dyadics.
    for address in range(1024):
        weight = sum((-1) ** parity(address & ch) for ch in range(1024))
        require(weight == (1024 if address == 0 else 0), "Fourier resolution")
    return moved_characters


def controls():
    # On a nonsingular alternating character every three-plane of L fails.
    def hyperbolic(v):
        return parity((v & 3) & (v >> 2))

    for normal in range(1, 16):
        plane = [v for v in range(16) if not parity(normal & v)]
        require(any(hyperbolic(u ^ v) != (hyperbolic(u) ^ hyperbolic(v))
                    for u, v in combinations(plane, 2)), "all-Z plane control")
    # A nonsingular r with Q(r)=1 gives a transvection preserving Q,
    # so the step discarding all off-diagonal terms would be false.
    r = 5
    require(hyperbolic(r) == 1 and all(hyperbolic(v) == hyperbolic(
        v ^ (r if hyperbolic(v ^ r) ^ hyperbolic(v) ^ hyperbolic(r) else 0))
        for v in range(16)), "anisotropic-r control")
    # Removing one term from the normalized average produces an odd numerator.
    require(sum((-1)**parity(ch) for ch in range(1023)) != 0, "missing character control")


def check_stability_bounds():
    # Apply the quoted PR7772 spectral enclosure; identification of its
    # eigenvalues and all-width propagation are external mathematical inputs.
    low = Fraction(470624175, 2**32)
    high = Fraction(7841980575, 2**30)
    translate_mass = Fraction(576 + 4 * 448, 8)
    require(translate_mass == 296 and 4**12 * translate_mass < 2**33, "row norm")
    n = 12128668876800
    require(n * (2**33)**2 < (2**55)**2, "matrix norm")
    require(max(abs(1-low/4), abs(1-high/4)) < Fraction(63, 64), "contraction")
    require(Fraction(63, 64)**64 < Fraction(1, 2), "iteration rate")
    canonical_bound = Fraction(302095, 100000)
    require(low * canonical_bound**2 > 1, "canonical norm")
    require(8192 // 64 - 56 == 72 and canonical_bound + Fraction(1, 2**72) < Fraction(3021, 1000),
            "noise margin")


if __name__ == "__main__":
    count, fixed = seed_stabilizer()
    moved = check_fourier_blocks()
    controls()
    check_stability_bounds()
    print(f"PASS_CLIFFORD_BELL_FIBRES candidates={count} seed_stabilizer={fixed}"
          f" characters=1024 full_sandwiches=576 quarter_sandwiches=448 moved_pairs={moved}")
