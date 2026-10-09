"""Independent exact small-space checks of the changed phase identities.

Every address is enumerated. Arithmetic is over F2 and Z/4, so equal diagonal
phases imply equality of the full conjugated operators on all basis inputs.
This checks the finite identities, not the all-size fixed-tape theorem.
"""
from fractions import Fraction


def dot(a, b):
    return (a & b).bit_count() & 1


def span(basis):
    result = [0]
    for b in basis:
        result += [x ^ b for x in result]
    return result


def basis_of(vectors):
    pivots = {}
    for x in vectors:
        while x:
            p = x.bit_length() - 1
            if p in pivots:
                x ^= pivots[p]
            else:
                pivots[p] = x
                break
    return list(pivots.values())


def project(basis, x):
    r = len(basis)
    rows = [sum(dot(a, b) << j for j, b in enumerate(basis))
            | (dot(a, x) << r) for a in basis]
    for j in range(r):
        pivot = next((k for k in range(j, r) if rows[k] >> j & 1), None)
        if pivot is None:
            raise ValueError("degenerate frame")
        rows[j], rows[pivot] = rows[pivot], rows[j]
        for k in range(r):
            if k != j and rows[k] >> j & 1:
                rows[k] ^= rows[j]
    result = 0
    for j, b in enumerate(basis):
        if rows[j] >> r & 1:
            result ^= b
    return result


def q(basis, x):
    return project(basis, x).bit_count() % 4


def orthogonal_minus(large, small):
    return basis_of(x for x in span(large) if all(not dot(x, s) for s in small))


def phase_checks():
    count = 0
    for n in (3, 4, 5):
        full = [1 << j for j in range(n)]
        owner = full[:-1]
        owner_perp = orthogonal_minus(full, owner)
        # The plane <011,101> is alternating and nondegenerate.
        for sigma in ([], [1], [1, 2], [3, 5]):
            if len(sigma) >= len(owner):
                continue
            assert all(s in span(owner) for s in sigma)
            first = orthogonal_minus(owner, sigma)
            exterior = basis_of(owner_perp + sigma)
            sigma_perp = orthogonal_minus(full, sigma)
            assert len(exterior) == n - len(owner) + len(sigma) < n
            source_only_wrong = False
            for x in range(1 << n):
                assert (q(owner, x) - q(sigma, x) - q(first, x)) % 4 == 0
                assert (q(full, x) + q(sigma, x) - q(owner, x)
                        - q(exterior, x)) % 4 == 0
                assert (q(sigma_perp, x) + q(sigma, x) - q(full, x)) % 4 == 0
                source_only_wrong |= (q(full, x) - q(sigma, x)) % 4 != q(full, x)
                count += 3
            if sigma:
                assert source_only_wrong, "unpaired sink negative control passed"
    try:
        project([3], 1)  # isotropic one-dimensional frame
    except ValueError:
        pass
    else:
        raise AssertionError("degenerate-frame control passed")
    return count


def copied_output_control():
    n = 3
    full, line = [1, 2, 4], [7]
    complement = orthogonal_minus(full, line)
    for x in range(1 << n):
        assert (q(full, x) - q(line, x) - q(complement, x)) % 4 == 0
    # Without the paid copied-output correction, X=0,Y=delta_0 leaves C_E Y.
    # Compute it exactly by the conjugated Hadamard diagonal definition.
    units = ((1, 0), (0, 1), (-1, 0), (0, -1))
    residual = []
    for y in range(1 << n):
        re = im = 0
        for z in range(1 << n):
            a, b = units[q(complement, z)]
            sign = -1 if dot(y, z) else 1
            re += sign * a
            im += sign * b
        residual.append((Fraction(re, 1 << n), Fraction(im, 1 << n)))
    assert any(a or b for a, b in residual), "omitted-copy control passed"


if __name__ == "__main__":
    count = phase_checks()
    copied_output_control()
    print(f"PASS {count} exact phase identities; unpaired sink, degenerate frame, "
          "and omitted endpoint copy controls reject")
