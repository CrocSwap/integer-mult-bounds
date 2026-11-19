"""Certify finite Walsh corners using binary vector spaces, without Clifford data."""
from itertools import combinations


def require(test, why):
    if not test:
        raise ValueError(why)


def span(basis):
    values = [0]
    for vector in basis:
        values += [v ^ vector for v in values]
    return values


def pairs(n):
    return list(combinations(range(n), 2))


def make_form(n, edges):
    rows = [0] * n
    for i, j in edges:
        rows[i] ^= 1 << j
        rows[j] ^= 1 << i
    return rows


def polar_functionals(rows):
    table = [0]
    for row in rows:
        table += [a ^ row for a in table]
    return table


def independent_extension(candidates, size, orthogonal, first=()):
    basis = list(first)
    current = set(span(basis))
    for v in candidates:
        if len(basis) == size:
            break
        if v not in current and all(not orthogonal(v, u) for u in basis):
            basis.append(v)
            current |= {u ^ v for u in current}
    require(len(basis) == size, "isotropic extension")
    return basis


def pure_corner(n, s, dual):
    def polar(u, v):
        return (dual[u] & v).bit_count() % 2

    basis = independent_extension(range(1, 1 << n), s, polar)
    require(len(set(span(basis))) == 1 << s, "dimension")
    require(all(not polar(u, v) for u, v in combinations(basis, 2)), "pure pair shear")


def binary_quadratic(n, edges):
    edge_masks = [(1 << i) | (1 << j) for i, j in edges]
    return [sum((v & mask) == mask for mask in edge_masks) % 2 for v in range(1 << n)]


def mixed_corner(n, s, dual, q):
    def polar(u, v):
        return (dual[u] & v).bit_count() % 2

    r = next(v for v in range(1, 1 << n) if q[v] == 0)
    hyperplane = [u for u in range(1 << n) if not polar(u, r)]
    outside = next(u for u in range(1 << n) if polar(u, r))
    basis = independent_extension(hyperplane, s - 1, polar, first=[r])
    require(len(hyperplane) == 1 << (n - 1), "mixed hyperplane")
    require(all(not polar(u, v) for u, v in combinations(basis, 2)), "pure kernel signs")
    # T_p fixes the hyperplane and translates its other coset by p.
    # Test by comparing actual values of Q on the whole coset, without
    # consulting the radical or assuming the character changes.
    fixed = [p for p in span(basis)
             if all(q[outside ^ y] == q[outside ^ y ^ p] for y in hyperplane)]
    require(fixed == [0], "mixed character stabilizer")
    return len(span(basis)) - 1


def main():
    pure_forms = mixed_forms = moved = represented = 0
    for n in (1, 2, 3, 4, 5):
        s = 1 if n == 2 else n // 2 + 1
        all_edges = pairs(n)
        for bits in range(1 << len(all_edges)):
            edges = [edge for j, edge in enumerate(all_edges) if bits >> j & 1]
            dual = polar_functionals(make_form(n, edges))
            if n == 4 and len(set(dual)) == 1 << n:
                q0 = binary_quadratic(n, edges)
                for linear in range(1 << n):
                    q = [a ^ ((linear & v).bit_count() % 2) for v, a in enumerate(q0)]
                    moved += mixed_corner(n, s, dual, q)
                    mixed_forms += 1
            else:
                pure_corner(n, s, dual)
                pure_forms += 1
            represented += 1 << n

    # For n=6..9 check all possible alternating ranks in the usual symplectic
    # basis. Every linear part is inspected on each full-rank polar form.
    # For lower ranks a pure witness works for all linear parts at once.
    ranks = 0
    for n in range(6, 10):
        for rank in range(0, n + 1, 2):
            edges = [(i, i + 1) for i in range(0, rank, 2)]
            dual = polar_functionals(make_form(n, edges))
            require(len(set(dual)) == 1 << rank, "symplectic block rank")
            ranks += 1
            if rank != n:
                pure_corner(n, n // 2 + 1, dual)
                continue
            q0 = binary_quadratic(n, edges)
            for linear in range(1 << n):
                q = [a ^ ((linear & v).bit_count() % 2) for v, a in enumerate(q0)]
                moved += mixed_corner(n, n // 2 + 1, dual, q)
                mixed_forms += 1

    # In a hyperbolic pair, choosing Q(r)=1 instead of 0 leaves T_r
    # invisible; the mixed corner's stabilizer count would be wrong.
    q_bad = [((v & 1) > 0) ^ ((v & 3) == 3) ^ ((v & 12) == 12) for v in range(16)]
    require(all(q_bad[v] == q_bad[v ^ 1] for v in range(16) if v & 2), "wrong r control")
    # The anisotropic binary plane really has no nonzero singular vector.
    require(all(((v & 1) ^ ((v >> 1) & 1) ^ (v == 3)) == 1 for v in (1, 2, 3)),
            "two-dimensional exception")
    print(f"PASS exhaustive n<=5 characters={represented} pure_polar_checks={pure_forms}")
    print(f"PASS n=6..9 canonical polar ranks={ranks}; combined mixed corners={mixed_forms}, "
          f"nontrivial character moves={moved}; two controls")


if __name__ == "__main__":
    main()
