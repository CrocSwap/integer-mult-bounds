"""Check the four-qubit nearest-neighbor bound in the Hermitian Pauli basis.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from itertools import product


def pauli_phase(left, right):
    """Return e for P_left P_right = i^e P_(left xor right)."""
    x, z = left % 16, left // 16
    a, b = right % 16, right // 16
    return ((x & z).bit_count() + (a & b).bit_count()
            + 2 * (z & a).bit_count() - ((x ^ a) & (z ^ b)).bit_count()) % 4


def two_steps(p, e, q, f):
    """Remove the common scalar from (I+i^e P)(I+i^f Q), with e,f odd."""
    if p == q:
        return ((p if e == f else 0, 0),)
    return tuple(sorted(((0, 0), (p, e), (q, f),
                         (p ^ q, (e + f + pauli_phase(p, q)) % 4))))


def check_nearest():
    rotations = tuple(product(range(1, 256), (1, 3)))
    paths = Counter(two_steps(p, e, q, f) for p, e in rotations for q, f in rotations)
    identity_paths = paths.pop(((0, 0),))
    counts = Counter(paths.values())
    if identity_paths != 510 or counts != {2: 64515, 3: 43520}:
        raise ValueError("Wrong number of nearest rotations or two-step paths")
    if any(len(key) == 2 for key in paths):
        raise ValueError("Three nearest rotations form a triangle")
    for size, expected in [(19, 114), (20, -138)]:
        margin = (72 - size) ** 2 - 49 * (3 * size - 2)
        if margin != expected:
            raise ValueError("Wrong width-six certificate")
    return counts


def check_diagonal():
    # The 32 affine characters exhaust all real signs of a Pauli with a
    # fixed X displacement. For a real diagonal W, every Z image is Z.
    affine = {sum((((mask & x).bit_count() + sign) % 2) << x for x in range(16))
              for mask in range(16) for sign in (0, 1)}

    def passes_image_tests(truth_table):
        for bit in (1, 2, 4, 8):
            difference = sum((((truth_table >> x) ^ (truth_table >> (x ^ bit))) & 1) << x
                             for x in range(16))
            if difference not in affine:
                return False
        return True

    def quadratic_tables():
        terms = [sum((int((x & m) == m) << x) for x in range(16))
                 for m in range(1, 16) if m.bit_count() <= 2]
        tables = {0}
        for term in terms:
            tables |= {table ^ term for table in tables}
        return tables

    # Fix the phase with W[0,0]=1. The other 15 signs are arbitrary.
    accepted = {table for table in range(0, 2**16, 2) if passes_image_tests(table)}
    if accepted != quadratic_tables() or len(accepted) != 1024:
        raise ValueError("Signed-Pauli conjugation differs from Boolean degree at most two")
    ccz = sum((int((x & 7) == 7) << x) for x in range(16))
    if ccz in accepted:
        raise ValueError("Three-qubit controlled-controlled Z passed the Clifford test")
    return len(accepted)


if __name__ == "__main__":
    print("Two-step product census", dict(sorted(check_nearest().items())))
    print("Normalized sign diagonals accepted", check_diagonal(), "of 32768")
