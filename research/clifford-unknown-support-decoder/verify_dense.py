"""Check dense width-three tensors against every one- and two-label model."""

from fractions import Fraction
from itertools import combinations, product
from random import Random
from typing import NamedTuple

from decode import decode


class Z(NamedTuple):
    """A Gaussian integer."""

    real: int
    imag: int = 0

    def __bool__(self):
        return bool(self.real or self.imag)

    def __neg__(self):
        return Z(-self.real, -self.imag)

    def __add__(self, other):
        return Z(self.real + other.real, self.imag + other.imag)

    def __sub__(self, other):
        return self + (-other)

    def __mul__(self, other):
        return Z(self.real * other.real - self.imag * other.imag,
                 self.real * other.imag + self.imag * other.real)


ZERO = Z(0)
ONE = Z(1)
I = Z(0, 1)
UNITS = (ONE, I, -ONE, -I)
SYMBOL = dict(zip((ZERO, *UNITS), ".+i-j", strict=True))


def dictionary():
    """Generate the eight monomial and sixteen full one-qubit signatures."""
    labels = []
    for a in UNITS:
        labels.extend(((ONE, ZERO, ZERO, a), (ZERO, ONE, a, ZERO)))
        for b in UNITS:
            labels.append((ONE, a, b, -(a * b)))
    if len(set(labels)) != 24:
        raise ArithmeticError("the independent one-qubit dictionary is incomplete")
    return labels


def minor(a, b, c, d):
    return a * d - b * c


def pivot_pair(a, b):
    row = next(i for i, x in enumerate(a) if x)
    for j in range(len(a)):
        det = minor(a[row], b[row], a[j], b[j])
        if det:
            return row, j, det
    raise ArithmeticError("two distinct columns have zero minors")


def term(label, numerator, denominator):
    """Convert the raw weight to the public normalized Choi convention."""
    h = sum(bool(x) for x in label[:2]) - 1
    for _ in range(3 * (h + 1)):
        numerator = numerator * (ONE + I)
    z = numerator * Z(denominator.real, -denominator.imag)
    norm = denominator.real**2 + denominator.imag**2
    weight = (str(Fraction(z.real, norm)), str(Fraction(z.imag, norm)))
    return "".join(SYMBOL[x] for x in label), (h, weight)


def oracle(target, cap, labels, columns, pivots):
    if not any(target):
        return {}
    for label, a in zip(labels, columns, strict=True):
        r = next(i for i, x in enumerate(a) if x)
        x = target[r]
        if x and all(t * a[r] == x * v for t, v in zip(target, a, strict=True)):
            return dict([term(label, x, a[r])])
    if cap == 1:
        return None
    for (k, h), (r, s, det) in pivots.items():
        a, b = columns[k], columns[h]
        x = minor(target[r], b[r], target[s], b[s])
        y = minor(a[r], target[r], a[s], target[s])
        if x and y and all(t * det == x * v + y * z
                           for t, v, z in zip(target, a, b, strict=True)):
            return dict([term(labels[k], x, det), term(labels[h], y, det)])
    return None


def dense_train(values):
    # The boundary cores read one index each. The middle core stores the
    # observed tensor entries without a decomposition into Clifford terms.
    first = [[q, 0, q, 1, 0] for q in range(4)]
    last = [[q, q, 0, 1, 0] for q in range(4)]
    middle = []
    for i, q, j in product(range(4), repeat=3):
        z = values[16*i + 4*q + j]
        if z:
            middle.append([q, i, j, z.real, z.imag])
    cores = [dict(left=1, right=4, entries=first),
             dict(left=4, right=4, entries=middle),
             dict(left=4, right=1, entries=last)]
    return dict(format="clifford-tt/1", qubits=1, cores=cores, sites=[0, 1, 2])


def samples(columns):
    rng = Random(904723)
    yield "zero", (ZERO,) * 64
    for j in range(32):
        k, h = rng.sample(range(24), 2)
        x, y = Z(1 + j % 4, -1), Z((-1)**j, 1 + j % 3)
        pair = [x*a + y*b for a, b in zip(columns[k], columns[h], strict=True)]
        yield "pair", pair
        if j % 3 == 0:
            yield "single", [x*a for a in columns[h]]
        for _ in range(2):
            changed = pair.copy()
            q = rng.randrange(64)
            changed[q] = changed[q] + rng.choice(UNITS)
            yield "perturbed", changed
        yield "arbitrary", [rng.choice((ZERO, ZERO, ZERO, *UNITS)) for _ in range(64)]


def unpack(result):
    if result["status"] == "outside_model":
        return None
    if result["status"] != "member":
        raise ValueError("unknown decoder status")
    found = {row["signature"]: (row["h"], tuple(row["coefficient"]))
             for row in result["terms"]}
    if len(found) != len(result["terms"]):
        raise ValueError("duplicate output label")
    return found


def main():
    labels = dictionary()
    columns = [tuple(x*y*z for x, y, z in product(w, repeat=3)) for w in labels]
    pivots = {(k, h): pivot_pair(columns[k], columns[h])
              for k, h in combinations(range(24), 2)}
    cases = accepted = 0
    for kind, values in samples(columns):
        data = dense_train(values)
        for cap in (1, 2):
            wanted = oracle(values, cap, labels, columns, pivots)
            obtained = unpack(decode(data, max_terms=cap))
            if obtained != wanted:
                raise ArithmeticError(f"{kind} sample {cases} at support {cap} failed")
            accepted += wanted is not None
        cases += 1
    if (len(pivots), cases, accepted) != (276, 140, 56):
        raise ArithmeticError("independent oracle coverage changed")
    print("PASS_DENSE_CLIFFORD_ORACLE 140 tensors 280 decisions 56 members 224 exclusions")


if __name__ == "__main__":
    main()
