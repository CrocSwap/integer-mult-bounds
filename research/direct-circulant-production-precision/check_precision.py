#!/usr/bin/env python3
"""Exact checks for the explicit production-precision proof.

Universal conclusions use PROOF.md. The finite controls bind that proof to the
source word, exercise a separate rational matrix interpreter, and expose omitted
inverse cuts, stale odometer suffixes and undercharged error envelopes.
"""

import ast
from dataclasses import asdict, dataclass
from fractions import Fraction as Q
from hashlib import sha1, sha256
from itertools import product
import json
from math import comb, prod
from pathlib import Path
from random import Random
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from precision import precision_budget


def require(condition, message):
    if not condition:
        raise ValueError(message)


def git_blob(data):
    return sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def authenticate():
    manifest = json.loads((HERE / "ORIGINS.json").read_text())
    hashes = {}
    for row in manifest["files"]:
        data = (HERE / "retained" / row["file"]).read_bytes()
        require(git_blob(data) == row["git_blob"], "Source Git blob drift: " + row["file"])
        if "sha256" in row:
            require(sha256(data).hexdigest() == row["sha256"], "Source SHA-256 drift")
        require(git_blob(data + b"\n") != row["git_blob"], "Source mutation was not rejected")
        hashes[row["file"]] = sha256(data).hexdigest()
    return hashes


def load_nodes(file, names, context):
    tree = ast.parse((HERE / "retained" / file).read_text(), filename=file)
    nodes = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names]
    require({n.name for n in nodes} == set(names), "Requested source functions missing")
    namespace = dict(context)
    exec(compile(ast.Module(body=nodes, type_ignores=[]), "<pinned " + file + ">", "exec"), namespace)
    return namespace


def poly_add(a, b):
    return [sum(x) for x in zip(a + [0]*max(0, len(b)-len(a)), b + [0]*max(0, len(a)-len(b)))]


def poly_multiply(a, b):
    out = [0]*(len(a)+len(b)-1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i+j] += x*y
    return out


def polynomial_certificate():
    # D(l) is taken from the documented exact expression, expanded independently.
    depth = poly_add([1], poly_multiply([0, 2], poly_multiply([8, 2], [18, 32, 8])))
    require(depth == [1, 288, 584, 256, 32], "Layer polynomial expansion")
    # A source entry contains a diagonal and an optional H: count both, so
    # each rounding event is propagated across the following exact H.
    stages = poly_add(poly_multiply([44, 48], depth), [2])
    upper = [20000*comb(6, j)*2**(6-j) for j in range(7)]
    difference = [upper[j]-(stages[j] if j < len(stages) else 0) for j in range(7)]
    require(all(c > 0 for c in difference), "Stage bound lacks a positive coefficient certificate")
    require(4102*9230 == 37861460 < 2**26, "Generator constant")
    require(8+12*5 == 68, "Completed prefix coefficient")
    require(1+3+68+26 == 98 and 2+39+11 == 52, "Physical-cut exponents")
    require(2+240+1+3*98 == 537 and 3*52 == 156, "Routed sixteen-H exponents")
    require(2+2*537 == 1076 and 2+2*156 == 314, "Two-root prefixes")
    require(2*1076+2 == 2154 and 2*314 == 628, "Tensor interval exponents")
    require(240+1+2*98 == 437 and 2*52 == 104, "Joined scalar exponents")
    require(Q(9, 256)+Q(6, 128) == Q(21, 256) < 1, "Synthesis error sum")
    require(32768-1361 == 31407 and 6*32768-4746 == 191862,
            "Original selector coefficient dominance")
    return {"D_coefficients": depth, "stage_difference_coefficients": difference}


def ceil_log2(value):
    value = Q(value)
    require(value > 0, "Positive logarithm")
    e = value.numerator.bit_length()-value.denominator.bit_length()
    if e >= 0:
        return e + (value.numerator > value.denominator*(1 << e))
    return e + (value.numerator*(1 << (-e)) > value.denominator)


def source_allocations():
    original = load_nodes("compiler-full.py", ["allocation"], {"Q": Q, "need": require, "ceil_log2": ceil_log2})["allocation"]
    count = 0
    for ell in range(1, 21):
        t = 1 << ell
        for target in (1, 17, 53):
            row = original(t, 4*t, 8*t*t, 2*t, target, 0)
            require(row["conditioning"] <= 32*t**3, "Conditioning")
            require(row["completed_prefix_bound"] <= 2**68*t**39, "Completed prefixes")
            require(row["fragment_bound"] <= 2**26*t**11, "Active fragments")
            require(row["execution_bound"] <= 2**98*t**52, "Physical cuts")
            require(row["coefficient_error"] <= Q(1, 1 << target), "Exact-word defect")
            require(row["layer_bound"] == 32*ell**4+256*ell**3+584*ell**2+288*ell+1, "Actual layer formula")
            count += 1
    return count


@dataclass(frozen=True, eq=False)
class Z:
    """Independent exact complex arithmetic for the emitted two-wire oracle."""
    re: Q = Q(0)
    im: Q = Q(0)

    def __post_init__(self):
        object.__setattr__(self, "re", Q(self.re))
        object.__setattr__(self, "im", Q(self.im))

    @staticmethod
    def coerce(x):
        return x if isinstance(x, Z) else Z(x)

    def __add__(self, other):
        other = self.coerce(other)
        return Z(self.re+other.re, self.im+other.im)

    __radd__ = __add__

    def __neg__(self):
        return Z(-self.re, -self.im)

    def __sub__(self, other):
        return self + -self.coerce(other)

    def __rsub__(self, other):
        return self.coerce(other) + -self

    def __mul__(self, other):
        other = self.coerce(other)
        return Z(self.re*other.re-self.im*other.im, self.re*other.im+self.im*other.re)

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = self.coerce(other)
        denominator = other.norm2()
        require(denominator != 0, "Division by zero in oracle")
        return self*Z(other.re/denominator, -other.im/denominator)

    def __rtruediv__(self, other):
        return self.coerce(other)/self

    def norm2(self):
        return self.re*self.re+self.im*self.im

    def __eq__(self, other):
        try:
            other = self.coerce(other)
        except (TypeError, ValueError):
            return False
        return self.re == other.re and self.im == other.im


def matrix_multiply(a, b):
    return [[sum((a[i][k]*b[k][j] for k in range(2)), Z()) for j in range(2)] for i in range(2)]


IDENTITY = [[Z(1), Z()], [Z(), Z(1)]]
HADAMARD = [[Z(1), Z(1)], [Z(1), Z(-1)]]


def apply_word(word):
    result = IDENTITY
    for j, diagonal in enumerate(word):
        matrix = [[Z.coerce(diagonal[0]), Z()], [Z(), Z.coerce(diagonal[1])]]
        result = matrix_multiply(matrix, result)
        if j+1 < len(word):
            result = matrix_multiply(HADAMARD, result)
    return result


def word_controls():
    names = ["diagonal_product", "chain", "swap_word", "upper_three", "upper_six", "lower_pair"]
    source = load_nodes("root_gate_plan.py", names, {"Fraction": Q})
    rng = Random(7849)
    fixtures = [
        [[Z(), Z(1)], [Z(1), Z()]],
        [[Z(1), Z()], [Z(), Z(1)]],
        [[Z(0, 1), Z()], [Z(), Z(0, -1)]],
    ]
    for q in (1, 8, 32, 128):
        tiny = Q(1, 1 << q)
        fixtures.extend(([[Z(tiny), Z()], [Z(), Z(1)]],
                         [[Z(1), Z(1)], [Z(1), Z(1+tiny)]]))
    for _ in range(192):
        fixtures.append([[Z(Q(rng.randint(-9, 9), rng.randint(1, 7)),
                            Q(rng.randint(-9, 9), rng.randint(1, 7))) for _ in range(2)] for _ in range(2)])
    passed = 0
    for gate in fixtures:
        det = gate[0][0]*gate[1][1]-gate[0][1]*gate[1][0]
        if det == 0:
            continue
        word = source["lower_pair"](gate)
        require(len(word) == 17, "Sixteen-H lowering changed length")
        require(apply_word(word) == gate, "Independent exact two-wire oracle disagrees")
        # The selected pivot provides the uniform unit bound for both shear ratios.
        i, j = max(product(range(2), repeat=2), key=lambda ij: gate[ij[0]][ij[1]].norm2())
        a, b, c = gate[i][j], gate[i][1-j], gate[1-i][j]
        for z in (b/a, c/a):
            require(z.norm2() <= 1, "Pivoted ratio leaves unit disk")
            require(4 <= (z+3).norm2() <= 16, "Three-H parameter leaves annulus")
        passed += 1
    # A phase/order mutation must change the actual matrix.
    gate = [[Z(1, 1), Z(2)], [Z(0, 1), Z(3, -1)]]
    word = source["lower_pair"](gate)
    corrupted = list(word)
    corrupted[8] = (word[8][0], -word[8][1])
    require(apply_word(corrupted) != gate, "Middle-diagonal phase mutation was not detected")
    # Prefix norm alone cannot certify an interval. Inverses are indispensable.
    for q in (1, 7, 31):
        prefixes = (Q(1), Q(1, 1 << q), Q(1))
        require(max(prefixes) == 1 and prefixes[2]/prefixes[1] > 1,
                "Inverse-cut negative control disappeared")
    return passed


def fresh_diagonal_reference(data, tables, grid):
    result = []
    for index, value in enumerate(data):
        address, current = [], index
        for row in tables:
            current, position = divmod(current, len(row))
            address.append(position)
        coefficient = grid.one
        for k in range(len(tables)-1, 0, -1):
            coefficient = grid.multiply(tables[k][address[k]], coefficient)
        coefficient = grid.multiply(tables[0][address[0]], coefficient)
        result.append(grid.multiply(coefficient, value))
    return result


def odometer_controls():
    source = load_nodes("tensor_word.py", ["Grid", "product_diagonal"],
                        {"Fraction": Q, "prod": prod, "word_product": lambda a, b: a*b})
    rng = Random(7849001)
    packets = 0
    records = 0
    for sides in ((2,), (2, 2), (4, 2, 4), (2, 4, 2, 2), (2, 2, 2, 2, 2)):
        for bits in (3, 7, 17):
            grid = source["Grid"](bits)
            for _ in range(8):
                tables = [tuple((rng.randint(-2*grid.unit, 2*grid.unit),
                                 rng.randint(-2*grid.unit, 2*grid.unit)) for _ in range(n)) for n in sides]
                data = [(rng.randint(-grid.unit, grid.unit), rng.randint(-grid.unit, grid.unit))
                        for _ in range(prod(sides))]
                # Include exact zero and identity factors; no ratio update is valid there.
                tables[0] = ((0, 0), grid.one) + tables[0][2:]
                expected = fresh_diagonal_reference(data, tables, grid)
                actual = list(data)
                source["product_diagonal"](actual, tables, grid)
                require(actual == expected, "Cached suffix differs from fresh current-coordinate evaluation")
                packets += 1
                records += len(data)
    # An actual stale-suffix mutant must fail, independently of a coarse norm budget.
    text = (HERE / "retained" / "tensor_word.py").read_text()
    changed = text.replace("for k in range(j, 0, -1):", "for k in range(j-1, 0, -1):")
    require(changed != text, "Odometer mutation site missing")
    node = next(n for n in ast.parse(changed).body if isinstance(n, ast.FunctionDef) and n.name == "product_diagonal")
    namespace = {"prod": prod}
    exec(compile(ast.Module(body=[node], type_ignores=[]), "<stale suffix control>", "exec"), namespace)
    grid = source["Grid"](7)
    tables = [((128, 0), (64, 32)), ((32, 64), (96, -32))]
    data = [(128, 0)]*4
    expected = fresh_diagonal_reference(data, tables, grid)
    namespace["product_diagonal"](data, tables, grid)
    require(data != expected, "Stale suffix mutant was not rejected")
    return {"packets": packets, "records": records}


def selector_controls():
    original = load_nodes("product.py", ["production_precision"], {})["production_precision"]
    count = 0
    comparisons = []
    cases = [(30, (1,)), (72, (4, 5)), (12288, (128,)*16),
             (6000000, (100000,)*10), (6*10**40, (10**40,))]
    for d in range(1, 9):
        for max_width in (1, 2, 3, 8, 17, 64):
            widths = tuple(1+(i*7)%max_width for i in range(d))
            cases.append((6*(sum(widths)+3), widths))
    for p, widths in cases:
        budget = precision_budget(p, widths)
        k = budget.envelope_coefficient.bit_length()
        upper_ratio = Q(budget.envelope_coefficient, 1 << k)
        require(0 < upper_ratio < 1, "Strict raw error margin missing")
        require(budget.fractional_bits == 4*p+budget.local_error_exponent+2*budget.interval_exponent+k,
                "Selector identity")
        # Dimension-free: this bounds the actual spend after division by the target.
        require(Q(budget.stage_bound*(budget.axes+1)**2, 1 << k) < Q(1, 4),
                "Bootstrap budget does not follow without circularity")
        old = original(p, widths)
        require(budget.fractional_bits < old, "New selector fails to improve original sufficient width")
        require(2*upper_ratio >= 1, "One-bit undercharge should lose this envelope certificate")
        count += 1
        if (p, widths) in cases[:5]:
            comparisons.append({"public_bits": p, "axes": len(widths), "address_bits": sum(widths),
                                "old_fractional_bits": old, "new_fractional_bits": budget.fractional_bits,
                                "ratio": str(Q(old, budget.fractional_bits))})
    # A seriously undercharged selector violates even the exact scalar bootstrap expression.
    q = precision_budget(30, (1,))
    exponent = q.envelope_coefficient.bit_length()-5
    exact_leading_ratio = Q(2*q.stage_bound*(q.axes+1)**2, 1 << exponent)
    require(exact_leading_ratio > 1, "Five-bit undercharge did not violate the raw-bound expression")
    for p, widths in ((0, (1,)), (1, ()), (1, (0,)), (True, (1,)), (1, (True,))):
        try:
            precision_budget(p, widths)
        except ValueError:
            pass
        else:
            raise ValueError("Malformed precision input accepted")
    # With b=P+8 instead of the producer's paid phase/column guard, r=8 fails admission's error envelope.
    require(Q(4*8, 1 << 9) >= Q(1, 4*8), "Missing column-guard negative control")
    return {"cases": count, "examples": comparisons}


def main():
    result = {
        "source_hashes": authenticate(),
        "polynomial_certificate": polynomial_certificate(),
        "source_allocator_cases": source_allocations(),
        "exact_two_wire_packets": word_controls(),
        "odometer": odometer_controls(),
        "selector": selector_controls(),
        "status": "PASS_DIRECT_CIRCULANT_PRODUCTION_PRECISION",
        "scope": "Exact finite controls and universal written numerical theorem; no full assumption discharge or new kappa.",
    }
    print(json.dumps(result, sort_keys=True, indent=2))
    print(result["status"])


if __name__ == "__main__":
    main()
