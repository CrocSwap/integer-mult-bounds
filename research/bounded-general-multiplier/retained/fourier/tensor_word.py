"""Execute the simultaneous diagonal and Hadamard word on a full dyadic tensor."""

from fractions import Fraction
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from math import prod

from root_gate_plan import lower_pair, paired_layer
from word_product import word_product


def load_routes(root):
    source = root / "research/unconditional-batched-crt/check_batched_crt.py"
    if sha256(source.read_bytes()).hexdigest() != "681e2e3d71fa74c8b9b326f3860104fd9d89590a222e26ae6ee718d1fd40ff2e":
        raise ValueError("Retained CRT and Beneš source differs")
    spec = spec_from_file_location("retained_balanced_crt", source)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Grid:
    """Use a common denominator for real and imaginary component words."""

    def __init__(self, bits, scalar_product=word_product):
        if bits < 1:
            raise ValueError("The grid must have at least one fractional bit")
        self.bits = bits
        self.unit = 1 << bits
        self.one = (self.unit, 0)
        self.scalar_product = scalar_product

    def word(self, z):
        a, b = (z.re, z.im) if hasattr(z, "re") else (Fraction(z), 0)
        return round(a*self.unit), round(b*self.unit)

    def multiply(self, u, v):
        if u == self.one:
            return v
        if v == self.one:
            return u
        a, b = u
        c, d = v
        half = self.unit >> 1
        return ((self.scalar_product(a,c)-self.scalar_product(b,d)+half) >> self.bits,
                (self.scalar_product(a,d)+self.scalar_product(b,c)+half) >> self.bits)


def local_schedule(axis, layers, compiler, routes, grid):
    n = axis.width
    ones = tuple([grid.one] * n)
    halves = tuple([(grid.unit//2, 0)] * n)
    words = {}
    route_cache = {}
    emitted = []
    for i in range(layers):
        gates = axis.layers[i] if i < len(axis.layers) else ()
        pairs = paired_layer(gates, n, compiler.exact)
        permutation = [0] * n
        tables = [[] for _ in range(17)]
        for j, ((x, y), gate) in enumerate(pairs):
            permutation[x], permutation[y] = 2*j, 2*j+1
            key = tuple((z.re, z.im) for row in gate for z in row)
            if key not in words:
                words[key] = tuple(tuple(map(grid.word, diag)) for diag in lower_pair(gate))
            for table, diag in zip(tables, words[key], strict=True):
                table.extend(diag)
        perm = tuple(permutation)
        if perm not in route_cache:
            switches = []
            for bit, mask in routes.benes(perm):
                signs = tuple((-grid.unit if mask[k] and (k >> bit) & 1 else grid.unit, 0)
                              for k in range(n))
                switches.append(((bit, ones), (bit, signs), (None, halves)))
            route_cache[perm] = switches
        switches = route_cache[perm]
        for switch in switches:
            emitted.extend(switch)
        emitted.extend((0 if j < 16 else None, tuple(table))
                       for j, table in enumerate(tables))
        for switch in reversed(switches):
            emitted.extend(switch)
    return emitted


def product_diagonal(data, tables, grid):
    """Apply a tensor diagonal with suffix products and a mixed-radix counter."""
    sides = [len(row) for row in tables]
    if prod(sides) != len(data):
        raise ValueError("The diagonal must cover the whole field")
    position = [0] * len(sides)
    suffix = [grid.one] * (len(sides)+1)
    for j in range(len(sides)-1, 0, -1):
        suffix[j] = grid.multiply(tables[j][0], suffix[j+1])
    for index, x in enumerate(data):
        diagonal = grid.multiply(tables[0][position[0]], suffix[1])
        data[index] = grid.multiply(diagonal, x)
        if index+1 == len(data):
            break
        j = 0
        while position[j]+1 == sides[j]:
            position[j] = 0
            j += 1
        position[j] += 1
        for k in range(j, 0, -1):
            suffix[k] = grid.multiply(tables[k][position[k]], suffix[k+1])


def hadamard(data, strides):
    """Elementary exact realization of one simultaneous public H call."""
    for stride in strides:
        for start in range(0, len(data), 2*stride):
            for lo in range(start, start+stride):
                hi = lo+stride
                a, b = data[lo]
                c, d = data[hi]
                data[lo], data[hi] = (a+c, b+d), (a-c, b-d)


def axis_packs(sides, public_bits):
    """Keep an untouched reservoir for a large simultaneous H."""
    d = len(sides)
    s = (public_bits+1).bit_length()
    limit = d if d <= s*s else max(1, d//s)
    for width in sorted(set(sides)):
        indices = [i for i, t in enumerate(sides) if t == width]
        for start in range(0, len(indices), limit):
            yield indices[start:start+limit]


class TensorWord:
    def __init__(self, axes, compiler, routes, grid, public_bits=None):
        self.grid = grid
        self.sides = tuple(a.width for a in axes)
        self.entrance = [tuple(map(grid.word, a.entrance)) for a in axes]
        self.exit = [tuple(map(grid.word, a.exit)) for a in axes]
        self.jobs = []
        self.h_calls = 0
        self.idles = [tuple([grid.one]*t) for t in self.sides]
        strides = [prod(self.sides[:j]) for j in range(len(axes))]
        for active in axis_packs(self.sides, public_bits or grid.bits):
            depth = max(len(axes[i].layers) for i in active)
            programs = [local_schedule(axes[i], depth, compiler, routes, grid) for i in active]
            schedule = []
            for stage in zip(*programs, strict=True):
                bit = stage[0][0]
                if any(other_bit != bit for other_bit, _ in stage):
                    raise ValueError("Different local H targets in one physical call")
                tables = self.idles.copy()
                for i, (_, table) in zip(active, stage, strict=True):
                    tables[i] = table
                target = () if bit is None else tuple(strides[i] << bit for i in active)
                schedule.append((tables, target))
                self.h_calls += 2*bool(target)
            self.jobs.append(schedule)

    def apply(self, values, opposite=False):
        if len(values) != prod(self.sides):
            raise ValueError("The signal must contain every physical record")
        data = [(a,-b) for a,b in values] if opposite else list(values)
        product_diagonal(data, self.entrance, self.grid)
        for schedule in self.jobs:
            for _ in range(2):
                for tables, target in schedule:
                    product_diagonal(data, tables, self.grid)
                    if target:
                        hadamard(data, target)
        product_diagonal(data, self.exit, self.grid)
        return [(a,-b) for a,b in data] if opposite else data
