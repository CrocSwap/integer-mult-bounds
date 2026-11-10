#!/usr/bin/env python3
"""Exact checks for the count-profile symmetry of the three-frame character test.

Addresses are rational symmetric 2-by-2 matrices, stored as (x, y, z) for
[[x, y], [y, z]].  Every check raises SystemExit, so python -O keeps them.
Standard library only.
"""

from __future__ import annotations

from fractions import Fraction as Fr
from itertools import combinations, permutations, product
from math import gcd

Sym = tuple[Fr, Fr, Fr]
Profile = tuple[int, int, int, int]
LinearMap = tuple[Sym, Sym, Sym]  # images of the unit vectors of (x, y, z)

A: Sym = (Fr(1), Fr(0), Fr(0))
B: Sym = (Fr(0), Fr(0), Fr(1))
P: Sym = (Fr(1, 2), Fr(1, 2), Fr(1, 2))
Q: Sym = (Fr(1, 2), Fr(-1, 2), Fr(1, 2))
IDENTITY: Sym = (Fr(1), Fr(0), Fr(1))
LABELS: tuple[Sym, Sym, Sym, Sym] = (A, B, P, Q)
LABEL_NAMES = "ABPQ"

CENSUS_FOUR_OLD: tuple[Profile, ...] = (
    (0, 1, 1, 2), (0, 1, 2, 1), (0, 2, 1, 1), (1, 0, 1, 2),
    (1, 0, 2, 1), (1, 1, 0, 2), (1, 1, 2, 0), (1, 2, 0, 1),
    (1, 2, 1, 0), (2, 0, 1, 1), (2, 1, 0, 1), (2, 1, 1, 0),
)
CENSUS_THREE_OLD: tuple[Profile, ...] = (
    (0, 1, 1, 1), (1, 0, 1, 1), (1, 1, 0, 1), (1, 1, 1, 0),
)
ONCE = (1, 1, 1)
TWICE = (1, 1, 2)
# Settled before this package: #6942, #7013, #7035, #7051 (all multiplicity (1,1,1)).
SETTLED_BEFORE: frozenset[Profile] = frozenset(
    {(1, 1, 1, 1), (0, 2, 1, 1), (2, 0, 1, 1), (1, 1, 0, 2)}
)
NEW_PROFILE: Profile = (1, 1, 2, 0)
BOX = 4
SMALL_BOX = 2
EUCLID_CAP = 4096

# Finite box observations for the three orbits left open, as
# (triples, character-excluded, target-support passes, passes of both tests).
# They are counts of a bounded enumeration, not proofs; see PROOF.md section 6.
EXPECTED_OPEN_BOX: dict[str, tuple[int, int, int, int]] = {
    "(2,1,1,0)/(1,1,1)": (1936, 1854, 8, 0),
    "(0,1,1,1)/(1,1,2)": (5610, 5225, 41, 0),
    "(0,1,1,1)/(1,1,1)": (1870, 1870, 11, 0),
}
# Character tables of the two surviving witnesses of PROOF.md section 5.
SURVIVOR_TABLES: dict[str, list[tuple[int, int]]] = {
    "adjacent": [(0, 0), (2, 0), (4, 2), (4, 2), (4, 2), (4, 2), (4, 4), (6, 4)],
    "three-old-twice": [(0, 0), (2, 0), (2, 2), (2, 2), (4, 2), (4, 2), (4, 4), (6, 4)],
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def add(u: Sym, v: Sym) -> Sym:
    return (u[0] + v[0], u[1] + v[1], u[2] + v[2])


def scale(c: Fr | int, u: Sym) -> Sym:
    return (c * u[0], c * u[1], c * u[2])


def det(u: Sym) -> Fr:
    return u[0] * u[2] - u[1] * u[1]


def apply(g: LinearMap, u: Sym) -> Sym:
    out = (Fr(0), Fr(0), Fr(0))
    for coefficient, column in zip(u, g):
        out = add(out, scale(coefficient, column))
    return out


def compose(g: LinearMap, f: LinearMap) -> LinearMap:
    return (apply(g, f[0]), apply(g, f[1]), apply(g, f[2]))


def from_formula(formula) -> LinearMap:
    units = ((Fr(1), Fr(0), Fr(0)), (Fr(0), Fr(1), Fr(0)), (Fr(0), Fr(0), Fr(1)))
    return (formula(*units[0]), formula(*units[1]), formula(*units[2]))


# The three generators.  h is M -> W M W^T / 2 with the integer W = [[1,1],[1,-1]].
FLIP = from_formula(lambda x, y, z: (x, -y, z))
SWAP = from_formula(lambda x, y, z: (z, y, x))
HADAMARD = from_formula(
    lambda x, y, z: ((x + 2 * y + z) / 2, (x - z) / 2, (x - 2 * y + z) / 2)
)


def generate_group() -> list[LinearMap]:
    identity = from_formula(lambda x, y, z: (x, y, z))
    group = [identity]
    for _ in range(8):
        grown = list(group)
        for g, f in product(group, (FLIP, SWAP, HADAMARD)):
            candidate = compose(f, g)
            if candidate not in grown:
                grown.append(candidate)
        if len(grown) == len(group):
            return group
        group = grown
    raise SystemExit("FAIL: group closure did not stabilise")


def label_permutation(g: LinearMap) -> tuple[int, int, int, int] | None:
    images = []
    for label in LABELS:
        image = apply(g, label)
        if image not in LABELS:
            return None
        images.append(LABELS.index(image))
    if sorted(images) != [0, 1, 2, 3]:
        return None
    return (images[0], images[1], images[2], images[3])


def abc_coordinates(u: Sym) -> Sym:
    """Coefficients of u on the basis (A, B, P)."""
    return (u[0] - u[1], u[2] - u[1], 2 * u[1])


def preserves_determinant(g: LinearMap) -> bool:
    # Both sides have degree at most 2 in each variable, so a 3x3x3 grid decides.
    grid = [Fr(k) for k in range(3)]
    return all(det(apply(g, u)) == det(u) for u in product(grid, repeat=3))


def targets() -> list[Sym]:
    return [add(A, P), add(A, Q), add(B, P), add(B, Q)]


def check_symmetry(g: LinearMap) -> tuple[int, int, int, int]:
    """Lemma 1 for one map; returns its label permutation."""
    require(apply(g, IDENTITY) == IDENTITY, "identity matrix is not fixed")
    require(preserves_determinant(g), "determinant is not preserved")
    perm = label_permutation(g)
    require(perm is not None, "labels are not permuted")
    assert perm is not None
    rows = [abc_coordinates(apply(g, label)) for label in (A, B, P)]
    require(all(c.denominator == 1 for row in rows for c in row), "lattice not integral")
    d = (
        rows[0][0] * (rows[1][1] * rows[2][2] - rows[1][2] * rows[2][1])
        - rows[0][1] * (rows[1][0] * rows[2][2] - rows[1][2] * rows[2][0])
        + rows[0][2] * (rows[1][0] * rows[2][1] - rows[1][1] * rows[2][0])
    )
    require(d in (1, -1), "lattice map is not unimodular")
    moved = [apply(g, target) for target in targets()]
    require(sorted(moved) == sorted(targets()), "targets are not permuted")
    return perm


def move_profile(perm: tuple[int, int, int, int], profile: Profile) -> Profile:
    moved = [0, 0, 0, 0]
    for index, count in enumerate(profile):
        moved[perm[index]] = count
    return (moved[0], moved[1], moved[2], moved[3])


def residual(profile: Profile) -> Sym:
    out = scale(4, IDENTITY)
    for count, label in zip(profile, LABELS):
        out = add(out, scale(-count, label))
    return out


def linear_label_permutations() -> list[tuple[int, int, int, int]]:
    """Label permutations that extend to a linear map of the address space."""
    extending = []
    for perm in permutations(range(4)):
        # A, B, P is a basis and Q = A + B - P, so linearity is one equation.
        image_q = add(add(LABELS[perm[0]], LABELS[perm[1]]), scale(-1, LABELS[perm[2]]))
        if image_q == LABELS[perm[3]]:
            extending.append(perm)
    return extending


def lattice_basis(vectors: list[tuple[int, int, int]]) -> list[tuple[int, int, int]]:
    """Echelon basis of the rank-3 integer row lattice spanned by vectors."""
    rows = [list(v) for v in vectors]
    basis: list[tuple[int, int, int]] = []
    for column in range(3):
        for _ in range(EUCLID_CAP):
            live = sorted((r for r in rows if r[column] != 0), key=lambda r: abs(r[column]))
            if len(live) <= 1:
                break
            pivot = live[0]
            for row in live[1:]:
                factor = row[column] // pivot[column]
                for k in range(3):
                    row[k] -= factor * pivot[k]
        else:
            raise SystemExit("FAIL: Euclid cap reached")
        live = [r for r in rows if r[column] != 0]
        require(len(live) == 1, "lattice does not have rank 3")
        basis.append((live[0][0], live[0][1], live[0][2]))
        rows = [r for r in rows if r is not live[0]]
    require(all(not any(r) for r in rows), "lattice reduction left a remainder")
    return basis


def basis_parities(basis: list[tuple[int, int, int]], vector: tuple[int, int, int]) -> tuple[int, int, int]:
    """Coordinates of vector on the echelon basis, reduced modulo 2."""
    rest = list(vector)
    coords = []
    for index, row in enumerate(basis):
        quotient, remainder = divmod(rest[index], row[index])
        require(remainder == 0, "vector is outside the lattice")
        for k in range(3):
            rest[k] -= quotient * row[k]
        coords.append(quotient % 2)
    require(not any(rest), "vector is outside the lattice")
    return (coords[0], coords[1], coords[2])


def character_table(profile: Profile, multiplicity: tuple[int, ...], frames: tuple[Sym, ...]) -> list[tuple[int, int]]:
    """(calls detected, targets detected) for all 8 characters of the label lattice."""
    require(len(multiplicity) == len(frames), "multiplicity does not match frames")
    frame_coords = [abc_coordinates(f) for f in frames]
    denominator = 1
    for coords in frame_coords:
        for c in coords:
            denominator = denominator * c.denominator // gcd(denominator, c.denominator)

    def integral(u: Sym) -> tuple[int, int, int]:
        scaled = [c * denominator for c in abc_coordinates(u)]
        return (int(scaled[0]), int(scaled[1]), int(scaled[2]))

    generators = [integral(label) for label in (A, B, P)] + [integral(f) for f in frames]
    basis = lattice_basis(generators)
    call_bits = [(count, basis_parities(basis, integral(label))) for count, label in zip(profile, LABELS)]
    call_bits += [(m, basis_parities(basis, integral(f))) for m, f in zip(multiplicity, frames)]
    target_bits = [basis_parities(basis, integral(t)) for t in targets()]
    table = []
    for chi in product((0, 1), repeat=3):
        def value(bits: tuple[int, int, int]) -> int:
            return (chi[0] * bits[0] + chi[1] * bits[1] + chi[2] * bits[2]) % 2
        calls = sum(count * value(bits) for count, bits in call_bits)
        hit = sum(value(bits) for bits in target_bits)
        table.append((calls, hit))
    return sorted(table)


def excluded(table: list[tuple[int, int]]) -> bool:
    return any(calls < hit for calls, hit in table)


def support_ok(profile: Profile, multiplicity: tuple[int, ...], frames: tuple[Sym, ...]) -> bool:
    """Every target is a subset sum of the paid labels, each occurrence used once."""
    calls: list[Sym] = []
    for count, label in zip(profile, LABELS):
        calls += [label] * count
    for m, frame in zip(multiplicity, frames):
        calls += [frame] * m
    require(len(calls) <= 8, "support check is sized for at most eight calls")
    sums = {(Fr(0), Fr(0), Fr(0))}
    for call in calls:
        sums |= {add(partial, call) for partial in sums}
    return all(target in sums for target in targets())


def directions(bound: int) -> list[tuple[int, int]]:
    """Primitive integer directions in the box, one per line."""
    found = []
    for u1, u2 in product(range(-bound, bound + 1), repeat=2):
        if gcd(u1, u2) != 1:
            continue
        if u1 < 0 or (u1 == 0 and u2 < 0):
            continue
        found.append((u1, u2))
    return found


def outer(u: tuple[int, int]) -> Sym:
    return (Fr(u[0] * u[0]), Fr(u[0] * u[1]), Fr(u[1] * u[1]))


def solve_scales(columns: tuple[Sym, Sym, Sym], rhs: Sym) -> tuple[Fr, Fr, Fr] | None:
    """Cramer solution of c0*col0 + c1*col1 + c2*col2 = rhs, or None if singular."""
    def det3(c0: Sym, c1: Sym, c2: Sym) -> Fr:
        return (
            c0[0] * (c1[1] * c2[2] - c1[2] * c2[1])
            - c1[0] * (c0[1] * c2[2] - c0[2] * c2[1])
            + c2[0] * (c0[1] * c1[2] - c0[2] * c1[1])
        )
    d = det3(*columns)
    if d == 0:
        return None
    return (
        det3(rhs, columns[1], columns[2]) / d,
        det3(columns[0], rhs, columns[2]) / d,
        det3(columns[0], columns[1], rhs) / d,
    )


def box_decompositions(target: Sym, multiplicity: tuple[int, int, int], bound: int) -> list[tuple[Sym, Sym, Sym]]:
    """Three nonzero rank-one frames on distinct box lines with m.R = target."""
    found = []
    slots = sorted(set(permutations(multiplicity)))
    for triple in combinations(directions(bound), 3):
        outers = (outer(triple[0]), outer(triple[1]), outer(triple[2]))
        for slot in slots:
            columns = (scale(slot[0], outers[0]), scale(slot[1], outers[1]), scale(slot[2], outers[2]))
            scales = solve_scales(columns, target)
            if scales is None or 0 in scales:
                continue
            frames = [(m, scale(c, o)) for m, c, o in zip(slot, scales, outers)]
            frames.sort(key=lambda item: item[0])
            require(tuple(m for m, _ in frames) == multiplicity, "slot order")
            found.append((frames[0][1], frames[1][1], frames[2][1]))
    return found


def check_decomposition(target: Sym, multiplicity: tuple[int, ...], frames: tuple[Sym, ...]) -> None:
    total = (Fr(0), Fr(0), Fr(0))
    for m, frame in zip(multiplicity, frames):
        require(frame != (0, 0, 0) and det(frame) == 0, "frame is not nonzero rank one")
        total = add(total, scale(m, frame))
    require(total == target, "frames do not sum to the residual")


def check_group() -> dict[tuple[int, int, int, int], LinearMap]:
    group = generate_group()
    require(len(group) == 8, "group order is not 8")
    by_perm = {}
    for g in group:
        by_perm[check_symmetry(g)] = g
    require(len(by_perm) == 8, "label action is not faithful")
    require(sorted(by_perm) == sorted(linear_label_permutations()), "not every linear label permutation")
    require(len(linear_label_permutations()) == 8, "linear label permutations are not 8 of 24")
    require(label_permutation(FLIP) == (0, 1, 3, 2), "flip is not (P Q)")
    require(label_permutation(SWAP) == (1, 0, 2, 3), "swap is not (A B)")
    require(label_permutation(HADAMARD) == (2, 3, 0, 1), "Hadamard is not (A P)(B Q)")
    for u in product([Fr(k, 2) for k in range(-2, 3)], repeat=3):
        require(apply(HADAMARD, apply(HADAMARD, u)) == u, "Hadamard is not an involution")
    for u1, u2 in product(range(-3, 4), repeat=2):
        image = scale(Fr(1, 2), outer((u1 + u2, u1 - u2)))
        require(apply(HADAMARD, outer((u1, u2))) == image, "Hadamard rank-one formula")
    return by_perm


def check_residuals(by_perm: dict[tuple[int, int, int, int], LinearMap]) -> int:
    compositions = [p for p in product(range(5), repeat=4) if sum(p) == 4]
    require(len(compositions) == 35, "composition count")
    for perm, g in by_perm.items():
        for profile in compositions + list(CENSUS_THREE_OLD):
            require(apply(g, residual(profile)) == residual(move_profile(perm, profile)), "residual equivariance")
    return len(compositions)


def orbits(profiles: list[tuple[Profile, tuple[int, ...]]], perms: list[tuple[int, int, int, int]]) -> list[list[tuple[Profile, tuple[int, ...]]]]:
    remaining = list(profiles)
    found = []
    for _ in range(len(profiles)):
        if not remaining:
            break
        seed_profile, seed_mult = remaining[0]
        orbit = sorted({(move_profile(perm, seed_profile), seed_mult) for perm in perms})
        require(all(item in remaining for item in orbit), "census is not closed under the group")
        remaining = [item for item in remaining if item not in orbit]
        found.append(orbit)
    require(not remaining, "orbit enumeration incomplete")
    return found


def check_orbits(by_perm: dict[tuple[int, int, int, int], LinearMap]) -> dict[str, int]:
    census = [((1, 1, 1, 1), ONCE)]
    census += [(p, ONCE) for p in CENSUS_FOUR_OLD]
    census += [(p, TWICE) for p in CENSUS_THREE_OLD]
    census += [(p, ONCE) for p in CENSUS_THREE_OLD]
    require(len(census) == 21 and len(set(census)) == 21, "census size")
    perms = list(by_perm)
    classes = orbits(census, perms)
    require(sorted(len(c) for c in classes) == [1, 4, 4, 4, 8], "census orbit sizes")
    settled = {(p, ONCE) for p in SETTLED_BEFORE}
    require(len(census) - len(settled) == 17, "open count before transport")
    new_orbit = next(c for c in classes if (NEW_PROFILE, ONCE) in c)
    require(
        new_orbit == sorted([((0, 2, 1, 1), ONCE), ((1, 1, 0, 2), ONCE), ((1, 1, 2, 0), ONCE), ((2, 0, 1, 1), ONCE)]),
        "orbit of the new profile",
    )
    require(move_profile(label_permutation(HADAMARD), (2, 0, 1, 1)) == NEW_PROFILE, "Hadamard image of (2,0,1,1)")
    require(move_profile(label_permutation(FLIP), (1, 1, 0, 2)) == NEW_PROFILE, "flip image of (1,1,0,2)")
    transported = {item for c in classes if settled & set(c) for item in c}
    require(transported - settled == {(NEW_PROFILE, ONCE)}, "transport settles exactly one new profile")
    open_classes = [c for c in classes if not (settled & set(c))]
    require(sorted(len(c) for c in open_classes) == [4, 4, 8], "open orbit sizes")
    require(sum(len(c) for c in open_classes) == 16, "open count after transport")
    all_profiles = [(p, ONCE) for p in product(range(5), repeat=4) if sum(p) == 4]
    return {
        "census_orbits": len(classes),
        "open_orbits": len(open_classes),
        "open_profiles": sum(len(c) for c in open_classes),
        "all_four_call_orbits": len(orbits(all_profiles, perms)),
    }


def check_named_witness() -> None:
    """#7035's named solution 2B+P+Q and its Hadamard image A+B+2Q."""
    source = (scale(2, B), P, Q)
    check_decomposition(residual((2, 0, 1, 1)), ONCE, source)
    image = tuple(apply(HADAMARD, f) for f in source)
    require(image == (scale(2, Q), A, B), "image of the named solution")
    require(residual(NEW_PROFILE) == add(IDENTITY, scale(2, Q)), "residual of (1,1,2,0) is I+2Q")
    require(residual(NEW_PROFILE) == (Fr(2), Fr(-1), Fr(2)), "residual matrix [[2,-1],[-1,2]]")
    check_decomposition(residual(NEW_PROFILE), ONCE, image)
    source_table = character_table((2, 0, 1, 1), ONCE, source)
    image_table = character_table(NEW_PROFILE, ONCE, image)
    require(source_table == image_table, "named witness tables differ")
    require((2, 4) in image_table and excluded(image_table), "named witness is not excluded by 2 < 4")


def check_new_profile_box() -> int:
    """Direct finite corroboration on the new profile: every box triple is excluded."""
    found = box_decompositions(residual(NEW_PROFILE), ONCE, BOX)
    require(len(found) > 0, "empty box for the new profile")
    for frames in found:
        check_decomposition(residual(NEW_PROFILE), ONCE, frames)
        require(excluded(character_table(NEW_PROFILE, ONCE, frames)), "box triple of (1,1,2,0) is not excluded")
    return len(found)


def check_transport_box(by_perm: dict[tuple[int, int, int, int], LinearMap]) -> int:
    """Lemma 2 on a box: tables agree for every census profile and group element."""
    checked = 0
    census = [((1, 1, 1, 1), ONCE)]
    census += [(p, ONCE) for p in CENSUS_FOUR_OLD]
    census += [(p, TWICE) for p in CENSUS_THREE_OLD]
    census += [(p, ONCE) for p in CENSUS_THREE_OLD]
    for profile, multiplicity in census:
        found = box_decompositions(residual(profile), multiplicity, SMALL_BOX)
        tables = [character_table(profile, multiplicity, frames) for frames in found]
        for perm, g in by_perm.items():
            moved_profile = move_profile(perm, profile)
            for frames, table in zip(found, tables):
                moved = tuple(apply(g, f) for f in frames)
                check_decomposition(residual(moved_profile), multiplicity, moved)
                require(character_table(moved_profile, multiplicity, moved) == table, "transported table differs")
                checked += 1
    return checked


def check_survivors(by_perm: dict[tuple[int, int, int, int], LinearMap]) -> int:
    """Section 5: explicit triples that pass every character, on twelve profiles."""
    witnesses = (
        ("adjacent", (2, 1, 1, 0), ONCE, (scale(-1, B), scale(Fr(5, 2), Q), scale(Fr(1, 4), outer((1, 3))))),
        ("three-old-twice", (0, 1, 1, 1), TWICE, (scale(Fr(1, 2), B), scale(Fr(1, 2), outer((2, 1))), Q)),
    )
    reached = set()
    for name, profile, multiplicity, frames in witnesses:
        for perm, g in by_perm.items():
            moved_profile = move_profile(perm, profile)
            moved = tuple(apply(g, f) for f in frames)
            check_decomposition(residual(moved_profile), multiplicity, moved)
            table = character_table(moved_profile, multiplicity, moved)
            require(table == SURVIVOR_TABLES[name], f"survivor table changed for {name}")
            require(all(calls >= hit for calls, hit in table), "survivor is excluded by a character")
            require(not excluded(table), "survivor is excluded")
            require(not support_ok(moved_profile, multiplicity, moved), "survivor passes target support")
            reached.add((moved_profile, multiplicity))
    closed = SETTLED_BEFORE | {NEW_PROFILE}
    expected = {(p, ONCE) for p in CENSUS_FOUR_OLD if p not in closed}
    expected |= {(p, TWICE) for p in CENSUS_THREE_OLD}
    require(reached == expected and len(reached) == 12, "survivors do not cover the twelve profiles")
    return len(reached)


def open_orbit_box() -> dict[str, tuple[int, int, int, int]]:
    """Bounded observation on each open orbit: excluded, support and joint counts."""
    representatives = {
        "(2,1,1,0)/(1,1,1)": ((2, 1, 1, 0), ONCE),
        "(0,1,1,1)/(1,1,2)": ((0, 1, 1, 1), TWICE),
        "(0,1,1,1)/(1,1,1)": ((0, 1, 1, 1), ONCE),
    }
    observed = {}
    for name, (profile, multiplicity) in representatives.items():
        found = box_decompositions(residual(profile), multiplicity, BOX)
        hit = 0
        supported = 0
        both = 0
        for frames in found:
            is_excluded = excluded(character_table(profile, multiplicity, frames))
            is_supported = support_ok(profile, multiplicity, frames)
            hit += is_excluded
            supported += is_supported
            both += (not is_excluded) and is_supported
        observed[name] = (len(found), hit, supported, both)
    return observed


def check_controls(by_perm: dict[tuple[int, int, int, int], LinearMap]) -> int:
    controls = 0
    # A label permutation outside the eight does not extend linearly.
    require((2, 1, 0, 3) not in by_perm, "transposition (A P) wrongly accepted")
    controls += 1
    # A rescaling changes the determinant and is rejected.
    doubled = from_formula(lambda x, y, z: (2 * x, 2 * y, 2 * z))
    require(not preserves_determinant(doubled), "rescaling wrongly preserves det")
    controls += 1
    # Congruence by the shear [[1,0],[1,1]] keeps det but moves the labels off the set.
    shear = from_formula(lambda x, y, z: (x, y + x, z + 2 * y + x))
    require(preserves_determinant(shear), "congruence by a unimodular shear keeps det")
    require(label_permutation(shear) is None, "shear wrongly permutes labels")
    controls += 1
    # Pairing the Hadamard image with the wrong profile breaks the residual.
    image = tuple(apply(HADAMARD, f) for f in (scale(2, B), P, Q))
    total = add(add(image[0], image[1]), image[2])
    require(total != residual((1, 1, 0, 2)), "wrong profile wrongly matched")
    controls += 1
    # The character table is not trivially excluding: all-old twice passes, once fails.
    require(not excluded(character_table((2, 2, 2, 2), (), ())), "eight old calls wrongly excluded")
    require(excluded(character_table((1, 1, 1, 1), (), ())), "four old calls not excluded")
    controls += 1
    # A tampered frame is rejected by the decomposition check.
    try:
        check_decomposition(residual(NEW_PROFILE), ONCE, (scale(2, Q), A, add(B, A)))
    except SystemExit:
        controls += 1
    else:
        raise SystemExit("FAIL: tampered decomposition accepted")
    return controls


def main() -> None:
    by_perm = check_group()
    compositions = check_residuals(by_perm)
    summary = check_orbits(by_perm)
    check_named_witness()
    new_box = check_new_profile_box()
    transport_checks = check_transport_box(by_perm)
    survivor_profiles = check_survivors(by_perm)
    observed = open_orbit_box()
    require(observed == EXPECTED_OPEN_BOX, f"open-orbit box counts changed: {observed}")
    controls = check_controls(by_perm)
    for name, (total, hit, supported, both) in observed.items():
        print(
            f"OPEN_ORBIT_BOX {name} triples={total} character_excluded={hit}"
            f" character_surviving={total - hit} support_passing={supported} passing_both={both}"
        )
    print(
        "PASS_THREE_FRAME_PROFILE_ORBITS"
        f" group=8 compositions={compositions}"
        f" census_orbits={summary['census_orbits']}"
        f" open_profiles={summary['open_profiles']}"
        f" open_orbits={summary['open_orbits']}"
        f" four_call_orbits={summary['all_four_call_orbits']}"
        f" new_profile_box={new_box}"
        f" transport_checks={transport_checks}"
        f" survivor_profiles={survivor_profiles}"
        f" controls={controls}"
    )


if __name__ == "__main__":
    main()
