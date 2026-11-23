"""Exact generators connected to the retained compensated gate program.

Jose Manuel (jmbarrancoml), with substantial OpenAI Codex assistance.
Apache-2.0. Macro/compiler: Vlado/PR1673; certified phases: Chafik/PR628.
"""
import ast
import copy
from fractions import Fraction as Q
from hashlib import sha256
import json

from exact import C, Mat, Vec, ceil_log2, component_l1, inverse_gate, need, norm2
from engine import Builder, Phases, split_kernel
from triangular import Triangle, allocation as triangle_allocation

SOURCE = "research/capped-phase-fusion/evidence/inplace_algebra_ultra/"
PRODUCER = "research/rational-unitary-fft/vendor/stein_rational.py"
PROVENANCE = "research/rational-unitary-fft/vendor/STEIN-PROVENANCE.json"
ORACLE = "research/cubic-cyclic-inverse/vendor/interval_kernel.py"


def load_producer(raw):
    record = json.loads(raw[PROVENANCE])
    need(record["source_commit"] == "e457d5e912a27307d725827aeca7198169320b84"
         and record["source_git_blob"] == "71b240a460a185ee2fe926cd189b56aeac6f997f"
         and sha256(raw[PRODUCER]).hexdigest() == record["sha256"],
         "original producer identity and retained bytes")
    namespace = {"__name__": "_frozen_rational_stein"}
    exec(compile(raw[PRODUCER], "<authenticated rational producer>", "exec", optimize=0), namespace)
    return namespace


def lower(vector):
    return Mat([[vector[i - j] if i >= j else C() for j in range(len(vector))]
                for i in range(len(vector))])


def prepare(matrix, producer):
    matrix = Mat(matrix)
    m = len(matrix)
    need(m > 0 and m & (m - 1) == 0 and matrix.shape == (m, m), "dyadic generator matrix")
    displacement = Mat([[matrix[i][j] - (matrix[i - 1][j - 1] if i and j else C())
                         for j in range(m)] for i in range(m)])
    old_c = producer["C"]
    old_e = producer["Matrix"]([[old_c(x.re, x.im) for x in row] for row in displacement])
    old_items, heights = producer["generators"](old_e)
    items = [dict(column=item["column"], gamma=item["gamma"],
                  scale=item["scale"], scale_exponent=item["scale_exponent"],
                  g=Vec(C(x.re, x.im) for x in item["g"]),
                  row=Vec(C(x.re, x.im) for x in item["row"])) for item in old_items]
    bound_e = max(max(component_l1(row) for row in displacement),
                  max(component_l1(column) for column in zip(*displacement)))
    need(all(norm2(item["g"]) <= 1 and norm2(item["row"]) < 4 * bound_e ** 2
             and 2 * component_l1(item["row"]) <= item["gamma"] for item in items),
         "actual bounded rational generator output")
    return items, displacement, bound_e, heights


def allocation(m, rank, bound_e, radius, target, incoming):
    need(type(m) is int and m > 0 and m & (m - 1) == 0, "dyadic macro size")
    need(type(rank) is int and 0 <= rank <= m and type(bound_e) in (int, Q)
         and bound_e >= 0, "generator count and exact displacement bound")
    need(type(radius) in (int, Q) and radius >= 1 and type(target) is int
         and target >= 1 and type(incoming) is int and incoming >= 0, "global generator input")
    d = m.bit_length() - 1
    kg, alpha = 2 * m + 16 * m * bound_e, 2 * rank * m * bound_e
    checkpoint = 10 + 4 * alpha + 2 * kg
    child = max(Q(3200 * m ** 3), 2 + 2 * kg)
    execution = child * checkpoint
    depth = rank * (8 * d * d + 32 * d + 18)
    gates = rank * m * (4 * d * d + 24 * d + 22)
    s = target + ceil_log2(4 * (rank + 1) * (kg + 1) * (radius + 1))
    eta = Q(1, 1 << s)
    triangle = triangle_allocation(m, 1, s)
    envelope = max(Q(6), 2 * kg)
    p = max(triangle["phase_bits"], s + ceil_log2(32 * (d + 1) * (envelope + 1)))
    mult = max(triangle["multiplier_bits"], s + 4)
    triangle = dict(triangle, phase_bits=p, multiplier_bits=mult,
                    coefficient_height_bound=max(4 * p + 24, mult + 5,
                                                 2 * triangle["leaf_bits"] + 16))
    data = max(incoming, target + ceil_log2(max(Q(1), 2 * depth * execution * m)))
    u = Q(1, 1 << data)
    defect = rank * (kg + 1) * eta
    rounding = depth * execution * m * u
    need(defect <= 1 and defect * radius + rounding <= Q(1, 1 << target),
         "complete compensated-generator target budget")
    amplitude = execution * radius + depth * execution ** 2 * m * u
    integer = max(1, ceil_log2(max(Q(1), amplitude))) + 2
    height = max(4 * p + 24, mult + ceil_log2(envelope + 2) + 2,
                 2 * triangle["leaf_bits"] + 16)
    return dict(m=m, rank=rank, displacement_bound=bound_e, radius=radius,
                target_bits=target, incoming_bits=incoming, kg=kg, alpha=alpha,
                checkpoint_bound=checkpoint, child_bound=child, execution_bound=execution,
                segment_bound=execution ** 2, layer_bound=depth, gate_bound=gates,
                child_target_bits=s, eta=eta, phase_bits=p, multiplier_bits=mult,
                leaf_bits=triangle["leaf_bits"], data_bits=data,
                multiplier_envelope=envelope, coefficient_error=defect,
                rounding_error=rounding, total_error=defect * radius + rounding,
                amplitude_bound=amplitude, integer_bits=integer,
                coefficient_height_bound=height,
                temporary_bits=2 * data + 8 * height + 2 * integer + 32), triangle


def macro_template(source):
    tree = ast.parse(source)
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                    and n.name == "lowdisp_shear")
    loop = next(n for n in function.body if isinstance(n, ast.For))
    start = next(i for i, n in enumerate(loop.body) if isinstance(n, ast.Assign)
                 and isinstance(n.targets[0], ast.Name) and n.targets[0].id == "p")
    tail = copy.deepcopy(loop.body[start:])
    need([type(n).__name__ for n in tail] ==
         ["Assign", "AugAssign", "Assign", "AugAssign", "AugAssign", "AugAssign", "AugAssign"],
         "retained seven-statement macro")
    identity = sha256(ast.dump(ast.Module(body=tail, type_ignores=[])).encode()).hexdigest()
    need(identity == "2a2e0f16a779597fa555857307451831bace11e66861fdc3caf26d2373a21210",
         "unchanged source macro identity")
    function = ast.FunctionDef(
        name="emit", args=ast.arguments(posonlyargs=[], args=[ast.arg(arg=n) for n in
        ("target", "source", "g", "h", "gamma")], vararg=None, kwonlyargs=[],
        kw_defaults=[], kwarg=None, defaults=[]),
        body=[ast.Assign(targets=[ast.Name(id="result", ctx=ast.Store())],
                         value=ast.List(elts=[], ctx=ast.Load()))] + tail +
             [ast.Return(value=ast.Name(id="result", ctx=ast.Load()))],
        decorator_list=[], type_params=[])
    module = ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[]))
    return compile(module, "<authenticated generator macro>", "exec", optimize=0), identity


class PairedNegative(Builder):
    def __init__(self, positive, source):
        super().__init__(positive.phases, positive.multiplier_bits, source)
        self.positive = positive

    def spectrum(self, kernel):
        row = self.positive.spectra[len(self.spectra)]
        need(Vec(kernel) == Vec(-x for x in row["kernel"]), "paired negative spectral kernel")
        result = Vec(-x for x in row["multipliers"])
        bound = self.bounds[len(self.spectra)]
        need(bound == row["bound"], "paired spectral envelope")
        v = Q(1, 1 << self.multiplier_bits)
        need(all(x.norm2() <= (bound + v) ** 2 for x in result), "negative stored multiplier bound")
        self.spectra.append(dict(kernel=Vec(kernel), multipliers=result, bound=bound))
        return result


class Program:
    def __init__(self, bound, triangle_bound, raw, phase_oracle=None):
        self.bound, self.triangle_bound, self.raw = bound, triangle_bound, raw
        self.phases = phase_oracle if phase_oracle is not None else Phases(bound["phase_bits"], raw[ORACLE])
        need(self.phases.bits == bound["phase_bits"], "common generator phase precision")
        self.source = list(range(bound["m"]))
        self.target = list(range(bound["m"], 2 * bound["m"]))
        self.stages, self.position, self.calls = [], 0, []
        self.pending = None
        self.last_triangle = None
        self.triangles, self.shears = [], []
        code, self.macro_ast = macro_template(raw[SOURCE + "check_circuits.py"])
        namespace = dict(triangle_plan=self.triangle, toeplitz_shear=self.shear,
                         inverse=self.inverse, lower=lower)
        exec(code, namespace)
        self.emit = namespace["emit"]

    def record(self, kind, plan, **details):
        self.calls.append(kind)
        self.stages.append(dict(kind=kind, start=self.position, stop=self.position + len(plan),
                                **details))
        self.position += len(plan)
        return plan

    def triangle(self, indices, coefficients):
        builder = Triangle(self.triangle_bound, self.raw[SOURCE + "check_circuits.py"],
                           self.raw[ORACLE], self.phases)
        local_indices = [self.source.index(i) for i in indices]
        local = builder.plan(coefficients, local_indices)
        plan = [[(tuple(self.source[i] for i in ids), gate) for ids, gate in layer] for layer in local]
        need(builder.bound["coefficient_error"] <= self.bound["eta"], "triangle operator allowance")
        self.last_triangle = plan
        self.triangles.append(builder)
        return self.record("triangle", plan, symbol=Vec(coefficients), indices=list(indices),
                           operator_error=builder.bound["coefficient_error"])

    def inverse(self, plan):
        need(plan is self.last_triangle, "inverse of the same stored triangle")
        result = [[(ids, inverse_gate(gate)) for ids, gate in layer] for layer in reversed(plan)]
        return self.record("inverse", result)

    def shear(self, target, source, matrix):
        need(target == self.target and source == self.source, "literal complete dirty banks")
        if self.pending is None:
            builder = Builder(self.phases, self.bound["multiplier_bits"],
                              self.raw[SOURCE + "check_circuits.py"])
            local = builder.plan(matrix)
            self.pending = (builder, matrix, local)
            kind = "positive"
        else:
            positive, original, positive_plan = self.pending
            need(matrix == -1 * original, "literal negative compensation matrix")
            builder = PairedNegative(positive, self.raw[SOURCE + "check_circuits.py"])
            local = builder.plan(matrix)
            m = len(source)
            need(len(local) == len(positive_plan), "same compensation layer schedule")
            for a, b in zip(positive_plan, local):
                need(len(a) == len(b), "same compensation gate schedule")
                for (ids, g), (other_ids, h) in zip(a, b):
                    crossing = len(ids) == 2 and ids[0] < m <= ids[1]
                    expected = Mat([[1, 0], [-g[1][0], 1]]) if crossing else g
                    need(ids == other_ids and h == expected, "paired coefficients preserve source order")
            self.pending = None
            kind = "compensation"
        g, h = split_kernel(matrix)
        envelope = component_l1(g) + component_l1(h)
        defect = (4 * len(source).bit_length() * envelope * self.phases.nu
                  + Q(2, 1 << self.bound["multiplier_bits"]))
        need(envelope <= self.bound["multiplier_envelope"] and defect <= self.bound["eta"],
             "scaled shear absolute operator allowance")
        self.shears.append(builder)
        mapping = source + target
        plan = [[(tuple(mapping[i] for i in ids), gate) for ids, gate in layer] for layer in local]
        return self.record(kind, plan, matrix=matrix, operator_error=defect, envelope=envelope)

    def plan(self, items):
        result = []
        for item in items:
            before = Vec(item["row"])
            result += self.emit(self.target, self.source, item["g"], item["row"], item["gamma"])
            need(before == item["row"], "fresh division preserves generator row")
        need(self.pending is None and self.calls ==
             ["triangle", "positive", "inverse", "compensation"] * len(items),
             "complete retained compensated call sequence")
        need(self.position == len(result) <= self.bound["layer_bound"]
             and sum(map(len, result)) <= self.bound["gate_bound"], "full program gate/layer budget")
        return result
