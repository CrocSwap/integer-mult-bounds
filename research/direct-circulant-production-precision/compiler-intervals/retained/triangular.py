"""Source-bound rational parity recursion with a common precision allocation.

Jose Manuel (jmbarrancoml), with substantial OpenAI Codex assistance.
Apache-2.0. Parity recursion and its stability premise: Vlado/PR1673.
"""
import ast
import copy
from fractions import Fraction as Q
from hashlib import sha256
from types import SimpleNamespace

from exact import (C, Mat, Vec, ceil_log2, component_l1, inverse_gate, need,
                   rounded)
from engine import Builder, Phases, split_kernel


def allocation(n, radius, target, incoming=0):
    need(type(n) is int and n > 0 and n & (n - 1) == 0, "dyadic triangle size")
    need(type(radius) in (int, Q) and radius >= 1, "exact triangle radius")
    need(type(target) is int and target >= 1, "positive triangle target")
    need(type(incoming) is int and incoming >= 0, "incoming triangle grid")
    d = n.bit_length() - 1
    q, depth, bound = 2 * d + 1, 4 * d * d + 12 * d + 1, 100 * n ** 3
    s = target + ceil_log2(4 * q * bound ** 3 * (radius + 1))
    p = s + ceil_log2(48 * (d + 1))
    multiplier = s + 2
    data = max(incoming, target + ceil_log2(64 * depth * bound * n))
    epsilon, u = Q(1, 1 << s), Q(1, 1 << data)
    theta = q * bound ** 2 * epsilon
    coefficient = 2 * q * bound ** 3 * epsilon
    rounding = 32 * depth * bound * n * u
    need(theta <= Q(1, 4) and coefficient * radius + rounding <= Q(1, 1 << target),
         "complete triangular error allocation")
    amplitude = 32 * bound * radius + 1024 * depth * bound ** 2 * n * u
    integer = max(1, ceil_log2(max(Q(1), amplitude))) + 2
    height = max(4 * p + 24, multiplier + 5, 2 * s + 16)
    return dict(n=n, radius=radius, target_bits=target, incoming_bits=incoming,
                ideal_bound=bound, macro_layers=q, layer_bound=depth,
                gate_bound=n * (2 * d * d + 8 * d + 1),
                leaf_bits=s, phase_bits=p, multiplier_bits=multiplier,
                data_bits=data, epsilon=epsilon, theta=theta,
                coefficient_error=coefficient, rounding_error=rounding,
                total_error=coefficient * radius + rounding,
                physical_prefix_suffix_bound=32 * bound,
                segment_bound=1024 * bound ** 2, amplitude_bound=amplitude,
                integer_bits=integer, coefficient_height_bound=height,
                temporary_bits=2 * data + 8 * height + 2 * integer + 32)


class Plan(list):
    """Actual layers plus consecutive, disjoint-support macro partitions."""
    def __init__(self, layers, blocks):
        super().__init__(layers)
        self.blocks = blocks

    def __add__(self, other):
        need(isinstance(other, Plan), "typed triangular composition")
        offset = len(self)
        blocks = [dict(block) for block in self.blocks]
        blocks += [dict(start=b["start"] + offset, stop=b["stop"] + offset,
                        pieces=list(b["pieces"])) for b in other.blocks]
        return Plan(list(self) + list(other), blocks)


class Concatenate:
    def __getitem__(self, parts):
        values = []
        for part in parts:
            values.extend(part if isinstance(part, (list, tuple)) else [part])
        return Vec(values)


def convolution(a, b):
    return Vec(sum((a[j] * b[k - j] for j in range(len(a))
                    if 0 <= k - j < len(b)), C())
               for k in range(len(a) + len(b) - 1))


class AdaptTriangle(ast.NodeTransformer):
    def __init__(self):
        self.changes = []

    def visit_Assign(self, node):
        if (len(node.targets) == 1 and isinstance(node.targets[0], ast.Subscript)
                and isinstance(node.targets[0].slice, ast.Constant)
                and node.targets[0].slice.value == "max_triangle_coefficient"):
            self.changes.append("exact-component-diagnostic")
            node.value = ast.parse(
                "max(STATS['max_triangle_coefficient'], component_l1(f))",
                mode="eval").body
            return node
        return self.generic_visit(node)

    def visit_Return(self, node):
        if (isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name)
                and node.value.func.id == "diag"):
            self.changes.append("stored-rounded-leaf")
            node.value.func.id = "leaf_diag"
        return self.generic_visit(node)


class Triangle:
    def __init__(self, bound, circuit_source, oracle_source, phase_oracle=None):
        self.bound, self.circuit_source = bound, circuit_source
        self.phases = phase_oracle if phase_oracle is not None else Phases(bound["phase_bits"], oracle_source)
        need(self.phases.bits == bound["phase_bits"], "common triangular phase precision")
        base = Builder(self.phases, bound["multiplier_bits"], circuit_source)
        self.source_parallel = base.namespace["parallel"]
        self.source_inverse = base.namespace["inverse"]
        self.children, self.leaves = [], []
        selected = {"toep", "lower", "invseries", "conv", "triangle_plan"}
        tree = ast.parse(circuit_source)
        tree.body = [copy.deepcopy(node) for node in tree.body
                     if isinstance(node, ast.FunctionDef) and node.name in selected]
        need({node.name for node in tree.body} == selected, "complete parity source")
        self.original_ast = sha256(ast.dump(tree).encode()).hexdigest()
        adapter = AdaptTriangle()
        tree = ast.fix_missing_locations(adapter.visit(tree))
        need(adapter.changes == ["exact-component-diagnostic", "stored-rounded-leaf"],
             "exact declared parity adaptations")
        self.adapted_ast = sha256(ast.dump(tree).encode()).hexdigest()
        facade = SimpleNamespace(asarray=lambda a, dtype=None: Vec(a),
                                 array=lambda a, dtype=None: Mat(a),
                                 zeros=lambda n, dtype=None: Vec([0] * n),
                                 convolve=convolution, r_=Concatenate())
        self.stats = {"triangle_nodes": 0, "max_triangle_coefficient": Q(0)}
        self.namespace = dict(np=facade, STATS=self.stats, component_l1=component_l1,
                              leaf_diag=self.leaf, parallel=self.parallel,
                              toeplitz_shear=self.shear)
        exec(compile(tree, "<authenticated parity recursion>", "exec", optimize=0),
             self.namespace)

    def leaf(self, indices, values):
        need(len(indices) == len(values) == 1, "scalar triangular leaf")
        wanted = values[0]
        stored = rounded(wanted, self.bound["leaf_bits"])
        epsilon = self.bound["epsilon"]
        need(Q(1, 4) <= wanted.norm2() <= 4, "ideal scalar leaf margin")
        need((stored - wanted).norm2() <= epsilon ** 2
             and stored.norm2() >= Q(1, 16), "stored scalar leaf margin")
        gate = Mat([[stored]])
        inverse = inverse_gate(gate)
        need(stored * inverse[0][0] == 1, "same stored scalar reciprocal")
        piece = dict(kind="leaf", ids=list(indices), ideal=Mat([[wanted]]),
                     error=epsilon, stored=stored, reciprocal=inverse[0][0])
        self.leaves.append(piece)
        return Plan([[(tuple(indices), gate)]],
                    [dict(start=0, stop=1, pieces=[piece])])

    def shear(self, target, source, matrix):
        n = len(source)
        need(len(set(source + target)) == 2 * n, "owned disjoint parity banks")
        child = Builder(self.phases, self.bound["multiplier_bits"], self.circuit_source)
        local = child.plan(matrix)
        g, h = split_kernel(matrix)
        envelope = component_l1(g) + component_l1(h)
        v = Q(1, 1 << self.bound["multiplier_bits"])
        defect = 4 * (n.bit_length()) * envelope * self.phases.nu + 2 * v
        need(envelope + 2 * v <= 6 and defect <= self.bound["epsilon"],
             "bounded parity child and allocated operator defect")
        mapping = source + target
        layers = [[(tuple(mapping[i] for i in ids), gate) for ids, gate in layer]
                  for layer in local]
        piece = dict(kind="shear", ids=list(mapping), ideal=matrix, error=defect,
                     envelope=envelope, source_ast=child.original_ast,
                     adapted_ast=child.adapted_ast, local_layers=len(local))
        self.children.append(piece)
        return Plan(layers, [dict(start=0, stop=len(layers), pieces=[piece])])

    def parallel(self, left, right):
        need([(b["start"], b["stop"]) for b in left.blocks]
             == [(b["start"], b["stop"]) for b in right.blocks],
             "equal sibling macro boundary partitions")
        blocks = []
        for a, b in zip(left.blocks, right.blocks):
            pieces = a["pieces"] + b["pieces"]
            ids = [i for piece in pieces for i in piece["ids"]]
            need(len(ids) == len(set(ids)), "disjoint sibling macro supports")
            blocks.append(dict(start=a["start"], stop=a["stop"], pieces=pieces))
        return Plan(self.source_parallel(left, right), blocks)

    def plan(self, symbol, indices=None):
        symbol = Vec(symbol)
        n = len(symbol)
        need(n == self.bound["n"], "allocated triangle dimension")
        need(component_l1(symbol - Vec([1] + [0] * (n - 1))) <= Q(1, 2),
             "component-l1 near-identity admission")
        indices = list(range(n)) if indices is None else list(indices)
        need(len(indices) == n and sorted(indices) == list(range(n)), "triangle wire permutation")
        result = self.namespace["triangle_plan"](indices, symbol)
        need(self.stats["triangle_nodes"] == 2 * n - 1, "complete parity recursion tree")
        need(len(result.blocks) == self.bound["macro_layers"]
             and len(result) <= self.bound["layer_bound"]
             and sum(map(len, result)) <= self.bound["gate_bound"], "complete schedule bounds")
        return result

    def inverse(self, plan):
        # Forward pieces certify forward defects. Inverse endpoint bounds use
        # the inverse-product proof, not relabelled forward macro certificates.
        return self.source_inverse(plan)
