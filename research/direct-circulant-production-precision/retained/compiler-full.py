"""Retained full Toeplitz recursion under leading-section conditioning.

Jose Manuel (jmbarrancoml), with substantial OpenAI Codex assistance.
Apache-2.0. Recursive source and displacement identities: Vlado/PR1673.
"""
import ast
import copy
from fractions import Fraction as Q
from hashlib import sha256
from types import SimpleNamespace

from exact import (C, Mat, Vec, ceil_log2, component_l1, eye, inverse_gate,
                   multiply, need, rounded)
from engine import Phases
from generator import (ORACLE, SOURCE, Program, allocation as generator_allocation,
                       load_producer, prepare)


class Matrix(Mat):
    @property
    def T(self):
        return Matrix(zip(*self))

    def __getitem__(self, key):
        value = super().__getitem__(key)
        return Matrix(value) if isinstance(value, Mat) else value

    def __sub__(self, other):
        need(self.shape == other.shape, "full matrix subtraction shape")
        return Matrix([[x - y for x, y in zip(a, b)] for a, b in zip(self, other)])

    def __matmul__(self, other):
        return Matrix(multiply(self, other))


def solve(left, right):
    n = len(left)
    need(left.shape == (n, n) and len(right) == n, "exact solve shapes")
    width = len(right[0])
    rows = [list(a) + list(b) for a, b in zip(left, right)]
    for j in range(n):
        pivot = next((i for i in range(j, n) if rows[i][j] != 0), None)
        need(pivot is not None, "singular leading/Schur section")
        rows[j], rows[pivot] = rows[pivot], rows[j]
        divisor = rows[j][j]
        rows[j] = [x / divisor for x in rows[j]]
        for i in range(n):
            if i != j:
                factor = rows[i][j]
                rows[i] = [x - factor * y for x, y in zip(rows[i], rows[j])]
    need(all(rows[i][j] == int(i == j) for i in range(n) for j in range(n)),
         "exact solve elimination")
    return Matrix([row[n:n + width] for row in rows])


def norm_upper(matrix):
    return max(max(component_l1(row) for row in matrix),
               max(component_l1(column) for column in zip(*matrix)))


def admission(matrix):
    matrix = Matrix(matrix)
    n = len(matrix)
    need(n > 0 and n & (n - 1) == 0 and matrix.shape == (n, n), "dyadic full Toeplitz shape")
    need(all(matrix[i][j] == (matrix[i - j][0] if i >= j else matrix[0][j - i])
             for i in range(n) for j in range(n)), "exact full Toeplitz admission")
    leading = []
    for b in range(1, n + 1):
        inverse = solve(matrix[:b, :b], Matrix(eye(b)))
        leading.append((b, norm_upper(inverse)))
    return max(Q(1), norm_upper(matrix)), max(Q(1), *(v for _, v in leading)), leading


def allocation(n, lam, inverse_bound, radius, target, incoming):
    need(type(n) is int and n > 0 and n & (n - 1) == 0, "full dyadic dimension")
    need(all(type(x) in (int, Q) and x >= 1 for x in (lam, inverse_bound, radius)),
         "exact full conditioning and radius bounds")
    need(type(target) is int and target >= 1 and type(incoming) is int and incoming >= 0,
         "full target and incoming precision")
    lam, inverse_bound, radius = (Q(x) for x in (lam, inverse_bound, radius))
    d, chi = n.bit_length() - 1, lam * inverse_bound
    descendant = lam + lam ** 2 * inverse_bound
    b = 256 * n ** 3 * chi ** 12
    calls, rank = 3 * n - 2, 2 * d + 8
    alpha, kg = 8 * rank * n ** 2 * chi, 2 * n + 64 * n ** 2 * chi
    generator = max(Q(3200 * n ** 3), 2 + 2 * kg) * (10 + 4 * alpha + 2 * kg)
    fragment = max(generator, descendant + 1, 2 * inverse_bound)
    execution = 2 * max(Q(1), lam, inverse_bound) * b * fragment
    layers = 1 + 2 * d * rank * (8 * d * d + 32 * d + 18)
    gates = n * (1 + d * rank * (4 * d * d + 24 * d + 22))
    s = target + ceil_log2(4 * calls * b ** 3 * (radius + 1))
    eta = Q(1, 1 << s)
    theta = calls * b ** 2 * eta
    data = max(incoming, target + ceil_log2(2 * layers * execution * n))
    coefficient = 2 * calls * b ** 3 * eta
    rounding = layers * execution * n * Q(1, 1 << data)
    need(theta <= Q(1, 4) and eta <= 1 / (2 * inverse_bound)
         and coefficient * radius + rounding <= Q(1, 1 << target), "complete full precision budget")
    amplitude = execution * radius + layers * execution ** 2 * n * Q(1, 1 << data)
    integer = max(1, ceil_log2(max(Q(1), amplitude))) + 2
    scalar_height = 2 * s + 2 * ceil_log2(descendant + 2) + 8
    return dict(n=n, lam=lam, inverse_bound=inverse_bound, radius=radius,
                target_bits=target, incoming_bits=incoming, conditioning=chi,
                descendant_bound=descendant, completed_prefix_bound=b,
                atomic_calls=calls, rank_bound=rank, displacement_bound=4 * n * chi,
                generator_fragment_bound=generator, fragment_bound=fragment,
                execution_bound=execution, segment_bound=execution ** 2,
                layer_bound=layers, gate_bound=gates, child_target_bits=s, eta=eta,
                theta=theta, data_bits=data, coefficient_error=coefficient,
                rounding_error=rounding, total_error=coefficient * radius + rounding,
                amplitude_bound=amplitude, integer_bits=integer,
                scalar_height_bound=scalar_height, coefficient_height_bound=scalar_height)


class Plan(list):
    def __init__(self, layers, atoms):
        super().__init__(layers)
        self.atoms = atoms

    def __add__(self, other):
        need(isinstance(other, Plan), "typed full-plan composition")
        return Plan(list(self) + list(other), [dict(a) for a in self.atoms] +
                    [dict(a, start=a["start"] + len(self), stop=a["stop"] + len(self))
                     for a in other.atoms])


class Full:
    def __init__(self, bound, raw):
        self.bound, self.raw = dict(bound), raw
        self.producer = load_producer(raw)
        self.phase_pool, self.nodes = {}, {}
        selected = {"full_plan", "parallel", "inverse"}
        tree = ast.parse(raw[SOURCE + "check_circuits.py"])
        tree.body = [copy.deepcopy(node) for node in tree.body
                     if isinstance(node, ast.FunctionDef) and node.name in selected]
        need({node.name for node in tree.body} == selected, "complete full source function set")
        self.source_ast = sha256(ast.dump(tree).encode()).hexdigest()
        self.stats = {"full_nodes": 0}
        self.namespace = dict(STATS=self.stats,
                              np=SimpleNamespace(linalg=SimpleNamespace(solve=solve, inv=inverse_gate)),
                              lowdisp_shear=self.shear, diag=self.leaf)
        exec(compile(tree, "<authenticated full Toeplitz schedule>", "exec", optimize=0),
             self.namespace)
        self.source_full = self.namespace["full_plan"]
        self.source_parallel = self.namespace["parallel"]
        self.source_inverse = self.namespace["inverse"]
        self.namespace["parallel"] = self.parallel
        self.namespace["full_plan"] = self.node

    def interval(self, indices):
        positions = [self.positions[i] for i in indices]
        a, b = min(positions), max(positions) + 1
        need(positions == list(range(a, b)), "ordered contiguous logical interval")
        return a, b

    def node(self, indices, matrix):
        interval = self.interval(indices)
        need(interval not in self.nodes, "one exact Schur reference per node")
        self.nodes[interval] = dict(indices=list(indices), matrix=Matrix(matrix))
        need(norm_upper(matrix) <= self.bound["descendant_bound"], "component descendant bound")
        result = self.source_full(indices, matrix)
        self.nodes[interval]["layers"] = len(result)
        return result

    def leaf(self, indices, values):
        need(len(indices) == len(values) == 1, "scalar full leaf")
        intended = values[0]
        need(intended.norm2() >= 1 / self.bound["inverse_bound"] ** 2
             and intended.norm2() <= self.bound["descendant_bound"] ** 2, "full pivot margins")
        stored = rounded(intended, self.bound["child_target_bits"])
        need((stored - intended).norm2() <= self.bound["eta"] ** 2
             and stored.norm2() >= 1 / (4 * self.bound["inverse_bound"] ** 2), "stored full pivot margin")
        gate = Mat([[stored]])
        need(stored * inverse_gate(gate)[0][0] == 1, "same stored full scalar inverse")
        a, b = self.interval(indices)
        atom = dict(id=f"D:{a}", kind="leaf", interval=(a, b), indices=list(indices),
                    start=0, stop=1, ideal=Mat([[intended]]),
                    local_plan=[[((0,), gate)]], error=self.bound["eta"],
                    coefficient_height=self.bound["scalar_height_bound"])
        return Plan([[(tuple(indices), gate)]], [atom])

    def shear(self, target, source, matrix):
        m = len(source)
        positions = sorted(self.positions[i] for i in source + target)
        a, b = min(positions), max(positions) + 1
        need(positions == list(range(a, b)) and b - a == 2 * m, "owned full shear interval")
        upper = self.positions[target[0]] < self.positions[source[0]]
        need([self.positions[i] for i in target] == list(range(a if upper else a + m,
                                                              a + m if upper else b))
             and [self.positions[i] for i in source] == list(range(a + m if upper else a,
                                                                  b if upper else a + m)),
             "source full shear orientation")
        need(norm_upper(matrix) <= self.bound["conditioning"], "full K/L conditioning")
        items, displacement, be, heights = prepare(matrix, self.producer)
        need(len(items) <= self.bound["rank_bound"] and be <= self.bound["displacement_bound"],
             "retained displacement rank and envelope")
        child, triangle = generator_allocation(m, len(items), be, 1,
                                               self.bound["child_target_bits"], 0)
        need(child["coefficient_error"] <= self.bound["eta"]
             and child["execution_bound"] <= self.bound["generator_fragment_bound"],
             "full atomic generator contract")
        p = child["phase_bits"]
        if p not in self.phase_pool:
            self.phase_pool[p] = Phases(p, self.raw[ORACLE])
        program = Program(child, triangle, self.raw, self.phase_pool[p])
        local = program.plan(items)
        mapping = source + target
        plan = [[(tuple(mapping[i] for i in ids), gate) for ids, gate in layer] for layer in local]
        kind = "upper" if upper else "lower"
        atom = dict(id=f"{'R' if upper else 'L'}:{a}:{b}", kind=kind,
                    interval=(a, b), indices=list(mapping), start=0, stop=len(plan),
                    ideal=Mat(matrix), local_plan=local, error=child["coefficient_error"],
                    coefficient_height=child["coefficient_height_bound"],
                    program=program, generator_items=items, displacement=displacement,
                    producer_heights=heights)
        return Plan(plan, [atom])

    def parallel(self, left, right):
        left_ids = {i for a in left.atoms for i in a["indices"]}
        right_ids = {i for a in right.atoms for i in a["indices"]}
        need(not left_ids.intersection(right_ids), "disjoint full sibling supports")
        return Plan(self.source_parallel(left, right),
                    [dict(a) for a in left.atoms] + [dict(a) for a in right.atoms])

    def plan(self, matrix, indices=None):
        n = len(matrix)
        need(n == self.bound["n"], "allocated full dimension")
        indices = list(range(n)) if indices is None else list(indices)
        need(all(type(i) is int for i in indices) and sorted(indices) == list(range(n)),
             "full root wire permutation")
        self.positions = {wire: pos for pos, wire in enumerate(indices)}
        result = self.node(indices, Matrix(matrix))
        need(self.stats["full_nodes"] == 2 * n - 1 and len(result.atoms) == 3 * n - 2
             and len({a["id"] for a in result.atoms}) == len(result.atoms), "complete full recursion")
        need(len(result) <= self.bound["layer_bound"]
             and sum(map(len, result)) <= self.bound["gate_bound"], "full source schedule bounds")
        self.bound["coefficient_height_bound"] = max(a["coefficient_height"] for a in result.atoms)
        self.bound["temporary_bits"] = (2 * self.bound["data_bits"]
            + 8 * self.bound["coefficient_height_bound"] + 2 * self.bound["integer_bits"] + 32)
        return result

    def inverse(self, plan):
        return self.source_inverse(plan)
