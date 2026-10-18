#!/usr/bin/env python3
"""Independent exact tests of the two scoped controller obstructions.

No producer or predecessor executable is imported.  All controller operations
are multiplied as dense rational matrices.  The cyclotomic determinant is
extracted only after that multiplication, from the resulting 2 by 2 blocks.
"""

from fractions import Fraction as Q
from itertools import permutations
from contextlib import contextmanager
import json
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import unittest


def zero(rows, cols):
    return [[Q(0) for _ in range(cols)] for _ in range(rows)]


def eye(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def add(a, b, sign=1):
    return [[x + sign * y for x, y in zip(ar, br)]
            for ar, br in zip(a, b)]


def mul(a, b):
    return [[sum((x * y for x, y in zip(row, col)), Q(0))
             for col in zip(*b)] for row in a]


def inverse(a):
    n = len(a)
    x = [list(row) + erow for row, erow in zip(a, eye(n))]
    for j in range(n):
        pivot = next((i for i in range(j, n) if x[i][j]), None)
        if pivot is None:
            raise ValueError("singular rational matrix")
        x[j], x[pivot] = x[pivot], x[j]
        scale = x[j][j]
        x[j] = [v / scale for v in x[j]]
        for i in range(n):
            if i != j:
                scale = x[i][j]
                x[i] = [u - scale * v for u, v in zip(x[i], x[j])]
    return [row[n:] for row in x]


def rank(a):
    x = [list(row) for row in a]
    r = 0
    for j in range(len(x[0])):
        pivot = next((i for i in range(r, len(x)) if x[i][j]), None)
        if pivot is None:
            continue
        x[r], x[pivot] = x[pivot], x[r]
        scale = x[r][j]
        x[r] = [v / scale for v in x[r]]
        for i in range(r + 1, len(x)):
            scale = x[i][j]
            x[i] = [u - scale * v for u, v in zip(x[i], x[r])]
        r += 1
    return r


def block(a, b, c, d):
    return [x + y for x, y in zip(a, b)] + [x + y for x, y in zip(c, d)]


def determinant(a):
    n = len(a)
    total = Q(0)
    for p in permutations(range(n)):
        inversions = sum(p[i] > p[j] for i in range(n) for j in range(i + 1, n))
        value = Q((-1) ** inversions)
        for i, j in enumerate(p):
            value *= a[i][j]
        total += value
    return total


def cmul(x, y):
    """Multiply a+b*t with t^2=t-1, using rational pairs."""
    a, b = x
    c, d = y
    return (a * c - b * d, a * d + b * c + b * d)


def cpower(exponent):
    out = (Q(1), Q(0))
    for _ in range(exponent % 6):
        out = cmul(out, (Q(0), Q(1)))
    return out


def cdeterminant(a):
    n = len(a)
    total = (Q(0), Q(0))
    for p in permutations(range(n)):
        inversions = sum(p[i] > p[j] for i in range(n) for j in range(i + 1, n))
        value = (Q((-1) ** inversions), Q(0))
        for i, j in enumerate(p):
            value = cmul(value, a[i][j])
        total = tuple(x + y for x, y in zip(total, value))
    return total


G = [[Q(1), Q(0), Q(0)],
     [Q(0), Q(0), Q(-1)],
     [Q(0), Q(1), Q(1)]]


def scalar_operation(s):
    """A whole-bank scalar operation, repeated on all three sections."""
    banks = len(s)
    result = zero(3 * banks, 3 * banks)
    for i in range(banks):
        for j in range(banks):
            for k in range(3):
                result[3 * i + k][3 * j + k] = Q(s[i][j])
    return result


def macro(banks, first, second, kind, reverse=False):
    i3, z3 = eye(3), zero(3, 3)
    gi = inverse(G)
    local = (block(i3, add(z3, i3, -1), z3, G) if kind == "B"
             else block(gi, z3, gi, i3))
    if reverse:
        local = inverse(local)
    result = eye(3 * banks)
    indices = list(range(3 * first, 3 * first + 3)) + list(range(3 * second, 3 * second + 3))
    for i, ri in enumerate(indices):
        for j, rj in enumerate(indices):
            result[ri][rj] = local[i][j]
    charge = (1 if kind == "B" else -1) * (-1 if reverse else 1)
    return result, charge


def section_determinants(a):
    banks = len(a) // 3
    complement = [[a[3 * i][3 * j] for j in range(banks)] for i in range(banks)]
    active = []
    for i in range(banks):
        row = []
        for j in range(banks):
            aa, bb = a[3 * i + 1][3 * j + 1], a[3 * i + 2][3 * j + 1]
            if (a[3 * i + 1][3 * j + 2] != -bb
                    or a[3 * i + 2][3 * j + 2] != aa + bb):
                raise ValueError("operation leaves the common-chart commutant")
            for u, v in ((0, 1), (0, 2), (1, 0), (2, 0)):
                if a[3 * i + u][3 * j + v]:
                    raise ValueError("operation mixes the fixed and active sections")
            row.append((aa, bb))
        active.append(row)
    return determinant(complement), cdeterminant(active)


def source_chart(r, k, p, ell):
    n = len(k)
    query = len(r)
    if mul(r, p) != eye(query) or mul(ell, k) != eye(query) or mul(ell, p) != zero(query, query):
        raise ValueError("chart hypotheses fail")
    m = mul(r, k)
    z = add(k, mul(p, add(m, eye(query), -1)), -1)
    q = add(r, ell, -1)
    g = mul(add(eye(n), mul(p, ell), -1), add(eye(n), mul(z, q)))
    return g


class IndependentControllerTests(unittest.TestCase):
    def assert_charge(self, matrix, charge):
        fixed, active = section_determinants(matrix)
        self.assertNotEqual(fixed, 0)
        self.assertEqual(active, tuple(fixed * c for c in cpower(charge)))

    def test_dense_random_interleavings_and_inverses(self):
        rng = random.Random(1862)
        for banks in (2, 3, 4):
            out, charge = eye(3 * banks), 0
            for _ in range(36):
                first, second = rng.sample(range(banks), 2)
                kind, reverse = rng.choice(("B", "F")), bool(rng.randrange(2))
                op, delta = macro(banks, first, second, kind, reverse)
                out, charge = mul(op, out), charge + delta
                scalar = eye(banks)
                scalar[first][second] = rng.choice((Q(-2), Q(-1, 2), Q(1, 2), Q(1)))
                if rng.randrange(2):
                    scalar[second][second] = -1
                out = mul(scalar_operation(scalar), out)
                self.assert_charge(out, charge)

    def test_native_nine_call_charge_and_signs(self):
        out, charge = eye(12), 0
        for j, kind in enumerate("FBFBFBFBF"):
            op, delta = macro(4, j % 4, (j + 1) % 4, kind)
            out, charge = mul(op, out), charge + delta
            bridge = eye(4)
            bridge[(j + 2) % 4][j % 4] = Q(-1, 2)
            out = mul(scalar_operation(bridge), out)
        sign = eye(4)
        sign[0][0] = -1
        out = mul(scalar_operation(sign), out)
        self.assertEqual(charge, -1)
        self.assert_charge(out, charge)
        fixed, active = section_determinants(out)
        self.assertNotEqual(active, (fixed, 0))
        # This is the charge pattern, not a replay of the native controller.

    def test_odd_count_is_obstructed_but_neutral_is_not_sufficient(self):
        for charge in range(-15, 16, 2):
            self.assertNotEqual(cpower(charge), (1, 0))
        out = eye(6)
        op, _ = macro(2, 0, 1, "B")
        for _ in range(6):
            out = mul(op, out)
        self.assert_charge(out, 6)
        self.assertNotEqual(out, eye(6))
        self.assertNotEqual(out[0][3], out[1][4])

    def test_section_dependent_and_noncommuting_controls_rejected(self):
        # An uncharged G on one bank would repair the scalar determinant
        # ratio.  It is outside the scalar-operation alphabet.
        out = eye(6)
        for i in range(3):
            for j in range(3):
                out[i][j] = G[i][j]
        with self.assertRaises(AssertionError):
            self.assert_charge(out, 0)
        bad = eye(6)
        bad[1][1] = -1
        with self.assertRaises(ValueError):
            section_determinants(bad)
        bad = eye(6)
        bad[0][1] = 1
        with self.assertRaises(ValueError):
            section_determinants(bad)

    def test_sign_enabled_two_call_shear_is_allowed(self):
        b, _ = macro(2, 0, 1, "B")
        sign = scalar_operation([[Q(-1), Q(0)], [Q(0), Q(1)]])
        out = mul(mul(mul(sign, inverse(b)), sign), b)
        self.assertEqual(out, scalar_operation([[1, -2], [0, 1]]))
        self.assert_charge(out, 0)

    def test_six_call_algebraic_exchange_is_a_positive_control(self):
        # Each scaled macro is conjugate by a legal rational whole-bank
        # diagonal map.  This checks the algebra only: native inverse frame
        # progress and the complete physical invoice are separate questions.
        b, _ = macro(2, 0, 1, "B")
        f, _ = macro(2, 0, 1, "F")
        def scale_conjugate(op, first, second):
            s = scalar_operation([[Q(first), Q(0)], [Q(0), Q(second)]])
            return mul(s, mul(op, inverse(s)))
        b1, b2 = scale_conjugate(b, -1, 1), scale_conjugate(b, -2, 1)
        f1, f2 = f, scale_conjugate(f, 1, 2)
        upper = mul(inverse(b1), b2)
        lower = mul(f1, inverse(f2))
        self.assertEqual(upper, scalar_operation([[1, 1], [0, 1]]))
        self.assertEqual(lower, scalar_operation([[1, 0], [-1, 1]]))
        out = mul(upper, mul(lower, upper))
        self.assertEqual(out, scalar_operation([[0, 1], [-1, 0]]))
        self.assert_charge(out, 0)

    def test_varying_chart_triple_noncentral_and_selected_m(self):
        for m in ([[Q(2), Q(1)], [Q(0), Q(3)]],
                  [[Q(14), Q(0)], [Q(0), Q(14)]]):
            i, z = eye(2), zero(2, 2)
            r = [ir + zr + zr for ir, zr in zip(i, z)]
            k = [list(row) for row in m] + i + z
            p0 = i + z + z
            l0 = [zr + ir + zr for zr, ir in zip(z, i)]
            h = [[Q(0), Q(1)], [Q(-1), Q(0)]]
            v = [[Q(1), Q(1)], [Q(0), Q(1)]]
            pb = i + z + h
            lc = [zr + ir + vr for zr, ir, vr in zip(z, i, v)]
            ga = source_chart(r, k, p0, l0)
            gb = source_chart(r, k, pb, l0)
            gc = source_chart(r, k, p0, lc)
            n = len(k)
            fa = block(inverse(ga), zero(n, n), inverse(ga), eye(n))
            bb = block(eye(n), add(zero(n, n), eye(n), -1), zero(n, n), gb)
            fc = block(inverse(gc), zero(n, n), inverse(gc), eye(n))
            product = mul(fc, mul(bb, fa))
            expected_defect = add(gb, inverse(gc), -1)
            self.assertEqual(product, block(zero(n, n), add(zero(n, n), inverse(gc), -1),
                                            mul(gb, inverse(ga)), expected_defect))
            self.assertEqual(mul(r, mul(expected_defect, k)), add(m, [[2, 0], [0, 2]], -1))
            self.assertGreaterEqual(rank(expected_defect), rank(add(m, [[2, 0], [0, 2]], -1)))
            # Arbitrary invertible endpoint gauges cannot erase this block.
            left, right = eye(n), eye(n)
            left[0][1], right[2][3] = Q(1, 2), Q(-2)
            self.assertEqual(rank(mul(left, mul(expected_defect, right))), rank(expected_defect))

    def test_each_chart_hypothesis_is_checked(self):
        r, k = [[Q(1), Q(0), Q(0)]], [[Q(14)], [Q(1)], [Q(0)]]
        p, ell = [[Q(1)], [Q(0)], [Q(0)]], [[Q(0), Q(1), Q(0)]]
        source_chart(r, k, p, ell)
        for rr, kk, pp, ll in (
            (r, k, [[Q(2)], [Q(0)], [Q(0)]], ell),
            (r, [[Q(14)], [Q(2)], [Q(0)]], p, ell),
            (r, k, [[Q(1)], [Q(1)], [Q(0)]], ell),
        ):
            with self.assertRaises(ValueError):
                source_chart(rr, kk, pp, ll)

    def test_selected_query_rank_eight_projection(self):
        # A fresh canonical realization of RK=14I, not the pinned source
        # matrices: the producer separately binds the actual 112-port data.
        i, z = eye(8), zero(8, 8)
        m = [[14 * x for x in row] for row in i]
        r = [ir + zr + zr for ir, zr in zip(i, z)]
        k = m + i + z
        p = i + z + z
        ell = [zr + ir + zr for zr, ir in zip(z, i)]
        g = source_chart(r, k, p, ell)
        defect = add(g, inverse(g), -1)
        projection = mul(r, mul(defect, k))
        self.assertEqual(projection, [[12 * x for x in row] for row in i])
        self.assertEqual(rank(projection), 8)
        self.assertGreaterEqual(rank(defect), 8)


class ReplayIntegrityTests(unittest.TestCase):
    """Exercise the CLI trust boundary in disposable copies, never --write."""

    @contextmanager
    def isolated_package(self):
        source = Path(__file__).resolve().parent
        root = source.parents[1]
        pins = json.loads((source / "ARCHIVE.json").read_text())
        predecessor = json.loads((source / "PREDECESSOR.json").read_text())
        with tempfile.TemporaryDirectory(prefix="native-controller-integrity-") as tmp:
            tmp_root = Path(tmp)
            package = tmp_root / "research" / source.name
            package.mkdir(parents=True)
            local_files = ["verify.py", "ARCHIVE.json", "PREDECESSOR.json", "RESULT.json"]
            local_files += [item["local_path"] for item in predecessor["sources"]]
            for name in local_files:
                target = package / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source / name, target)
            archive = tmp_root / pins["path"]
            archive.parent.mkdir(parents=True, exist_ok=True)
            archive.symlink_to(root / pins["path"])
            yield package

    def replay(self, package):
        return subprocess.run([sys.executable, "-I", "-O", "-B", str(package / "verify.py")],
                              cwd=package, capture_output=True, text=True,
                              timeout=120, check=False)

    def test_entrypoint_positive_and_corrupted_result_controls(self):
        with self.isolated_package() as package:
            clean = self.replay(package)
            self.assertEqual(clean.returncode, 0, clean.stderr)
            result = json.loads(clean.stdout)
            self.assertEqual(result["status"], "PASS_NATIVE_CONTROLLER_CONGRUENCE")
            result["signed_winding"] = 0
            (package / "RESULT.json").write_text(json.dumps(result))
            corrupted = self.replay(package)
            self.assertNotEqual(corrupted.returncode, 0)
            self.assertIn("recorded result mismatch", corrupted.stderr)
            (package / "RESULT.json").write_text("{broken-json")
            malformed = self.replay(package)
            self.assertNotEqual(malformed.returncode, 0)
            self.assertIn("JSONDecodeError", malformed.stderr)

    def test_archive_binding_control(self):
        with self.isolated_package() as package:
            pins_path = package / "ARCHIVE.json"
            pins = json.loads(pins_path.read_text())
            pins["sha256"] = "0" * 64
            pins_path.write_text(json.dumps(pins))
            corrupted = self.replay(package)
            self.assertNotEqual(corrupted.returncode, 0)
            self.assertIn("archive pin", corrupted.stderr)

    def test_predecessor_text_binding_control(self):
        with self.isolated_package() as package:
            predecessor = json.loads((package / "PREDECESSOR.json").read_text())
            text = package / predecessor["sources"][0]["local_path"]
            text.write_bytes(text.read_bytes() + b"\nChanged claim, same alleged source.\n")
            corrupted = self.replay(package)
            self.assertNotEqual(corrupted.returncode, 0)
            self.assertIn("predecessor text pin", corrupted.stderr)


if __name__ == "__main__":
    unittest.main()
