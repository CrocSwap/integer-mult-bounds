"""Certified phases and an authenticated rational adaptation of the FFT child.

Jose Manuel (jmbarrancoml), with substantial OpenAI Codex assistance.
Apache-2.0. Phase projection follows Chafik/PR628; the schedule is Vlado/PR1673.
"""
import ast
import copy
from fractions import Fraction as Q
from hashlib import sha256
from math import gcd, isqrt
from types import SimpleNamespace

from exact import (C, Mat, Vec, adjoint, ceil_log2, component_l1, inverse_gate,
                   need, qheight, round_q, rounded)


class Phases:
    def __init__(self, bits, source):
        need(type(bits) is int and bits >= 1, "positive phase precision")
        self.bits, self.nu = bits, Q(1, 1 << bits)
        self.working_bits = 2 * (bits + 32)
        self.oracle = {"__name__": "_authenticated_phase_oracle"}
        exec(compile(source, "<authenticated PR628 interval oracle>", "exec", optimize=0), self.oracle)
        need(self.oracle["pi_interval"].cache_info().currsize == 0
             and self.oracle["kernel"].cache_info().currsize == 0, "fresh precision namespace")
        self.oracle["BITS"] = self.working_bits
        self.oracle["SCALE"] = 1 << self.working_bits
        self.values, self.boxes, self.certificates = {}, {}, {}

    @staticmethod
    def key(denominator, numerator):
        need(type(denominator) is int and denominator > 0 and type(numerator) is int,
             "integer phase description")
        numerator %= denominator
        divisor = gcd(denominator, numerator)
        return denominator // divisor, numerator // divisor

    def box(self, denominator, numerator):
        key = self.key(denominator, numerator)
        if key not in self.boxes:
            exact = {(1, 0): C(1), (2, 1): C(-1), (4, 1): C(0, 1), (4, 3): C(0, -1)}
            if key in exact:
                z = exact[key]
                self.boxes[key] = ((z.re, z.re), (z.im, z.im))
            else:
                self.boxes[key] = self.oracle["root_interval"](*key)
        return self.boxes[key]

    def phase(self, denominator, numerator):
        key = self.key(denominator, numerator)
        if key in self.values:
            return self.values[key]
        box = self.box(*key)
        if box[0][0] == box[0][1] and box[1][0] == box[1][1]:
            sigma, error, parameter = C(box[0][0], box[1][0]), Q(0), None
        else:
            choices = []
            for center in (C(1), C(-1), C(0, 1), C(0, -1)):
                conjugate = center.conjugate()
                point = self.oracle["point"]
                rotated = self.oracle["cmul"](box, (point(conjugate.re), point(conjugate.im)))
                choices.append((rotated[0][0], center, rotated))
            _, center, rotated = max(choices, key=lambda item: item[0])
            need(rotated[0][0] >= Q(1, 2), "certified unit-phase chart")
            parameters = [imag / (1 + real) for imag in rotated[1] for real in rotated[0]]
            parameter = round_q((min(parameters) + max(parameters)) / 2, self.bits + 4)
            need(abs(parameter) < 1, "bounded stereographic parameter")
            sigma = center * C((1 - parameter ** 2) / (1 + parameter ** 2),
                               2 * parameter / (1 + parameter ** 2))
            # Maximum endpoint distance, not minimum distance to a rectangle.
            error = sum(max(abs(endpoint - value) for endpoint in interval)
                        for interval, value in zip(box, (sigma.re, sigma.im)))
        need(sigma.norm2() == 1 and error <= self.nu, "certified exact rational unit phase")
        need(max(qheight(sigma.re), qheight(sigma.im)) <= 2 * self.bits + 12,
             "unit-phase representation bound")
        self.values[key] = sigma
        self.certificates[key] = {"denominator": key[0], "numerator": key[1],
            "unit": sigma.record(), "error_bound": str(error),
            "parameter": None if parameter is None else str(parameter)}
        return sigma

    def record(self):
        return {"phase_bits": self.bits, "oracle_bits": self.working_bits,
                "certificates": [self.certificates[key] for key in sorted(self.certificates)]}


def split_kernel(matrix):
    n = len(matrix)
    need(n > 0 and n & (n - 1) == 0 and matrix.shape == (n, n), "square dyadic tile")
    column, row = matrix[:, 0], matrix[0, :]
    need(all(matrix[i][j] == (column[i - j] if i >= j else row[j - i])
             for i in range(n) for j in range(n)), "Toeplitz input")
    g, h = Vec([0] * n), Vec([0] * n)
    g[0] = h[0] = column[0] / 2
    for j in range(1, n):
        g[j] = (column[j] + row[n - j]) / 2
        h[j] = (column[j] - row[n - j]) / 2
    return g, h


def budget(matrix, radius, target, input_fractional_bits=0):
    g, h = split_kernel(matrix)
    n, depth = len(matrix), len(matrix).bit_length() - 1
    mg, mh = component_l1(g), component_l1(h)
    total = mg + mh
    need(type(target) is int and target >= 1 and type(radius) in (int, Q) and radius >= 1,
         "target and exact input radius")
    need(type(input_fractional_bits) is int and input_fractional_bits >= 0,
         "declared incoming fractional precision")
    layers = 4 * depth + 8
    phase_bits = target + ceil_log2(16 * (depth + 1) * (total + 1) * (radius + 1))
    multiplier_bits = target + ceil_log2(8 * (radius + 1))
    data_bits = max(input_fractional_bits, target + ceil_log2(2 * layers * n * (total + 2)))
    return certificate(n, mg, mh, radius, target, phase_bits, multiplier_bits, data_bits,
                       input_fractional_bits)


def certificate(n, mg, mh, radius, target, phase_bits, multiplier_bits, data_bits,
                input_fractional_bits=0):
    need(type(n) is int and n > 0 and n & (n - 1) == 0, "dyadic certificate dimension")
    need(all(type(x) is int for x in (target, phase_bits, multiplier_bits, data_bits))
         and all(type(x) in (int, Q) for x in (mg, mh, radius)), "exact budget fields")
    need(type(input_fractional_bits) is int and 0 <= input_fractional_bits <= data_bits,
         "preserve incoming data grid")
    need(min(phase_bits, multiplier_bits, data_bits, target) >= 1 and min(mg, mh) >= 0
         and radius >= 1, "positive precisions and valid envelopes")
    depth, layers = n.bit_length() - 1, 4 * (n.bit_length() - 1) + 8
    nu, v, u = (Q(1, 1 << b) for b in (phase_bits, multiplier_bits, data_bits))
    total = mg + mh
    coefficient_error = 4 * (depth + 1) * total * nu + 2 * v
    prefix_bound = 1 + total + 2 * v
    rounding_error = layers * prefix_bound * n * u
    error = coefficient_error * radius + rounding_error
    need(error <= Q(1, 1 << target), "complete target error budget")
    need(layers * n * u <= 1, "bounded rounding accumulation")
    amplitude = prefix_bound * (radius + layers * n * u)
    integer_bits = max(1, ceil_log2(max(Q(1), amplitude))) + 2
    coefficient_height = max(4 * phase_bits + 24,
                             multiplier_bits + ceil_log2(total + 2) + 2)
    temporary_bits = 2 * data_bits + 8 * coefficient_height + 2 * integer_bits + 32
    return dict(n=n, depth=depth, layer_bound=layers, mg=mg, mh=mh, radius=radius,
                target_bits=target, phase_bits=phase_bits, multiplier_bits=multiplier_bits,
                data_bits=data_bits, input_fractional_bits=input_fractional_bits,
                coefficient_error=coefficient_error, prefix_bound=prefix_bound,
                rounding_error=rounding_error, total_error=error, amplitude_bound=amplitude,
                integer_bits=integer_bits, coefficient_height_bound=coefficient_height,
                temporary_bits=temporary_bits)


class Adapt(ast.NodeTransformer):
    def __init__(self):
        self.function = None
        self.changes = []

    def visit_FunctionDef(self, node):
        old = self.function
        self.function = node.name
        result = self.generic_visit(node)
        self.function = old
        return result

    def visit_Assign(self, node):
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if self.function == "fft" and name == "w":
                self.changes.append("fft-twiddle")
                node.value = ast.Call(func=ast.Name(id="phase", ctx=ast.Load()),
                    args=[ast.Name(id="size", ctx=ast.Load()),
                          ast.UnaryOp(op=ast.USub(), operand=ast.Name(id="j", ctx=ast.Load()))],
                    keywords=[])
                return node
            if self.function == "toeplitz_shear" and name == "gamma":
                self.changes.append("independent-twist-coefficients")
                return ast.Pass()
            if self.function == "toeplitz_shear" and name == "d":
                self.changes.append("twist-vector")
                node.value = ast.Call(func=ast.Name(id="certified_twist_vector", ctx=ast.Load()),
                                     args=[ast.Name(id="n", ctx=ast.Load())], keywords=[])
                return node
        return self.generic_visit(node)

    def visit_BinOp(self, node):
        if (self.function == "fft" and isinstance(node.op, ast.Div)
                and isinstance(node.right, ast.Call) and isinstance(node.right.func, ast.Attribute)
                and node.right.func.attr == "sqrt"):
            self.changes.append("unitary-splitter")
            return ast.Call(func=ast.Name(id="butterfly", ctx=ast.Load()),
                            args=[ast.Name(id="w", ctx=ast.Load())], keywords=[])
        return self.generic_visit(node)


class Builder:
    def __init__(self, phase_oracle, multiplier_bits, circuit_source):
        self.phases, self.multiplier_bits = phase_oracle, multiplier_bits
        self.spectra, self.twist_vectors, self.bounds = [], [], []
        selected = {"diag", "inverse", "parallel", "fft", "circ_shear", "toeplitz_shear"}
        tree = ast.parse(circuit_source)
        tree.body = [copy.deepcopy(n) for n in tree.body
                     if isinstance(n, ast.FunctionDef) and n.name in selected]
        need({node.name for node in tree.body} == selected, "complete source function set")
        self.original_ast = sha256(ast.dump(tree).encode()).hexdigest()
        adapter = Adapt()
        tree = ast.fix_missing_locations(adapter.visit(tree))
        need(adapter.changes == ["fft-twiddle", "unitary-splitter",
                                 "independent-twist-coefficients", "twist-vector"],
             "exact declared coefficient adaptation")
        self.adapted_ast = sha256(ast.dump(tree).encode()).hexdigest()
        self.np = SimpleNamespace(array=lambda rows, dtype=None: Mat(rows),
                                  zeros=lambda n, dtype=None: Vec([0] * n),
                                  fft=SimpleNamespace(fft=self.spectrum),
                                  linalg=SimpleNamespace(inv=inverse_gate))
        self.namespace = {"np": self.np, "phase": self.phases.phase,
                          "butterfly": self.butterfly, "certified_twist_vector": self.twists}
        exec(compile(tree, "<authenticated FFT/shear schedule>", "exec", optimize=0), self.namespace)

    def butterfly(self, w):
        splitter = self.phases.phase(8, 1)
        a, b = splitter.re, splitter.im
        return Mat([[a, b * w], [b, -a * w]])

    def twists(self, n):
        result = Vec(self.phases.phase(2 * n, j) for j in range(n))
        self.twist_vectors.append(result)
        return result

    def spectrum(self, kernel):
        n = len(kernel)
        bound = self.bounds[len(self.spectra)]
        exact = Vec(sum((kernel[j] * self.phases.phase(n, -i * j) for j in range(n)), C())
                    for i in range(n))
        result = Vec(rounded(value, self.multiplier_bits) for value in exact)
        v = Q(1, 1 << self.multiplier_bits)
        need(all(value.norm2() <= bound ** 2 for value in exact), "unit-root multiplier bound")
        need(all(value.norm2() <= (bound + v) ** 2 for value in result), "rounded multiplier bound")
        need(all((x - y).norm2() <= v ** 2 for x, y in zip(result, exact)), "multiplier rounding")
        self.spectra.append({"kernel": Vec(kernel), "multipliers": result, "bound": bound})
        return result

    def plan(self, matrix):
        g, h = split_kernel(matrix)
        n = len(matrix)
        self.bounds = [component_l1(g), component_l1(h)]
        self.spectra, self.twist_vectors = [], []
        result = self.namespace["toeplitz_shear"](list(range(n, 2 * n)), list(range(n)), matrix)
        need(len(self.spectra) == 2 and len(self.twist_vectors) == 1, "two circulants and one twist table")
        need(self.spectra[0]["kernel"] == g, "first source kernel")
        need(self.spectra[1]["kernel"] == self.twist_vectors[0] * h, "twisted second source kernel")
        need(all(a.norm2() == b.norm2() for a, b in zip(self.spectra[1]["kernel"], h)),
             "twisting preserves kernel magnitudes")
        return result


def inverse_sqrt_box(n, bits):
    scale = 1 << bits
    lower = isqrt((1 << (2 * bits)) // n)
    if lower * lower * n == 1 << (2 * bits):
        return Q(lower, scale), Q(lower, scale)
    return Q(lower, scale), Q(lower + 1, scale)
