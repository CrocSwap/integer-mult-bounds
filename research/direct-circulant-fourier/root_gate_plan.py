"""Compile a padded circulant root into source-bound one- and two-wire layers."""

from fractions import Fraction
from hashlib import sha256
from importlib import import_module
from pathlib import Path
from types import SimpleNamespace
import sys


SOURCES = {
    "research/rational-unitary-fft/exact.py": "c9b89d7357210af69865690ba12e695366961f8b501a8fab9d0fefe3fb30c479",
    "research/rational-unitary-fft/engine.py": "9e36aee0835e6b1b62997433581f88b5a434ccab8ae43e5c25d1deaaf1ebf653",
    "research/rational-unitary-fft/triangular.py": "46780d95ddebfed22e8f0c18565fe2e768250afa5beeb31f450292cc06f7ec11",
    "research/rational-unitary-fft/generator.py": "827ef9fe1bd664859995892b59843c390f7969c938fb7e1e6dc585c31a54b555",
    "research/rational-unitary-fft/full.py": "1f42d5f2858564ffb320e54ba6aa29651025491569823e25006bf5862457b803",
    "research/rational-unitary-fft/vendor/stein_rational.py": "3065fc5d6d22ec44de533b08fb0c639603449456383668e561dc46629e641502",
    "research/rational-unitary-fft/vendor/STEIN-PROVENANCE.json": "e7f0e8dc517387e302b1e8bf5dff7e12b29da8aa91abc6ea597f33c1ac08ba62",
    "research/cubic-cyclic-inverse/vendor/interval_kernel.py": "9b7bb24640a9a7d3f83c7951dfef483ec933db4c50de6c0130b85f450eeddfbe",
    "research/capped-phase-fusion/evidence/inplace_algebra_ultra/check_circuits.py": "06d1861bfe8af543908e26557ffda7e451ff176bceb9bacfaf0f04f234b336d5"
}


def load_compiler(root):
    """Authenticate the retained modules and the four inputs used by the builder."""
    root = Path(root).resolve()
    raw = {}
    for relative, expected in SOURCES.items():
        data = (root / relative).read_bytes()
        if sha256(data).hexdigest() != expected:
            raise ValueError(f"Source differs at {relative}")
        raw[relative] = data
    package = root / "research/rational-unitary-fft"
    sys.path.insert(0, str(package))
    try:
        modules = {}
        for name in ("exact", "engine", "triangular", "generator", "full"):
            module = import_module(name)
            if Path(module.__file__).resolve() != package / (name + ".py"):
                raise ValueError(f"Foreign compiler module {name}")
            modules[name] = module
    finally:
        sys.path.remove(str(package))
    return SimpleNamespace(raw=raw, **modules)


def certify_accretivity(column, margin):
    """Certify strict accretivity of the stored circulant at a named margin."""
    if type(margin) not in (int, Fraction) or margin <= 0:
        raise ValueError("The accretivity margin must be a positive rational")
    n = len(column)
    hermitian = [(column[i] + column[-i % n].conjugate()) / 2
                 - margin * int(i == 0) for i in range(n)]
    matrix = [[hermitian[(i-j) % n] for j in range(n)] for i in range(n)]
    for j in range(n):
        pivot = matrix[j][j]
        if pivot.im != 0 or pivot.re <= 0:
            raise ValueError("Circulant root fails the strict accretivity test")
        for i in range(j+1, n):
            multiplier = matrix[i][j] / pivot
            for k in range(j+1, n):
                matrix[i][k] = matrix[i][k] - multiplier * matrix[j][k]


def padded_matrix(compiler, column, n):
    r = len(column)
    if not 1 <= r <= n or n & (n-1):
        raise ValueError("The dyadic wire count must contain the source")
    C = compiler.exact.C
    col = [C(real, imag) for real, imag in column]
    if any(part.denominator & (part.denominator - 1)
           for z in col for part in (z.re, z.im)):
        raise ValueError("A column entry is outside the dyadic grid")
    return col, compiler.full.Matrix([
        [col[(i-j) % r] if i < r and j < r else C(int(i == j)) for j in range(n)]
        for i in range(n)
    ])


def compile_padded_root(compiler, column, target_width, grid_bits, radius=1, incoming=0,
                        margin=Fraction(1, 4)):
    """Compile a rational column. The plan acts on all target_width data wires."""
    col, matrix = padded_matrix(compiler, column, target_width)
    certify_accretivity(col, margin)
    size_bound = max(Fraction(1), compiler.full.norm_upper(matrix))
    inverse_bound = Fraction(2 * target_width) / min(Fraction(1), margin)
    budget = compiler.full.allocation(target_width, size_bound, inverse_bound,
                                      radius, grid_bits, incoming)
    builder = compiler.full.Full(budget, compiler.raw)
    return builder.plan(matrix), builder


def diagonal_product(left, right):
    return left[0] * right[0], left[1] * right[1]


def chain(first, second):
    """Join two alternating diagonal-H words in execution order."""
    return first[:-1] + [diagonal_product(first[-1], second[0])] + second[1:]


def swap_word(active):
    return [(1, 1), (1, -1 if active else 1), (Fraction(1, 2), Fraction(1, 2))]


def upper_three(t):
    a = 4 * t / 5
    return [(1/a, 1), (-3, 1), (2, 1), (-a/8, Fraction(-1, 6))]


def upper_six(t):
    # In the pivoted matrix each shear multiplier has modulus at most one.
    return chain(upper_three(Fraction(-3)), upper_three(t+3))


def lower_pair(gate):
    """Express an invertible rational two-wire gate with exactly sixteen H gates."""
    i, j = max(((i, j) for i in range(2) for j in range(2)),
               key=lambda ij: gate[ij[0]][ij[1]].norm2())
    a, b = gate[i][j], gate[i][1-j]
    c, d = gate[1-i][j], gate[1-i][1-j]
    if a == 0 or a*d == b*c:
        raise ValueError("Singular two-wire gate")
    result = chain(swap_word(j != 0), upper_six(b/a))
    result = chain(result, [(a, d-c*b/a)])
    result = chain(result, list(reversed(upper_six(c/a))))
    return chain(result, swap_word(i != 0))


def paired_layer(layer, n, exact):
    """Keep the original pairs and pair each remaining scalar or idle wire."""
    if n < 2 or n & 1:
        raise ValueError("Pair lowering requires a positive even number of wires")
    occupied = set()
    singles = {}
    pairs = []
    for ids, gate in layer:
        if len(ids) not in (1, 2) or len(set(ids)) != len(ids):
            raise ValueError("Bad matching gate")
        if any(i in occupied or not 0 <= i < n for i in ids):
            raise ValueError("Matching overlap or wire outside the array")
        occupied.update(ids)
        if len(ids) == 2:
            pairs.append((tuple(ids), gate))
        else:
            singles[ids[0]] = gate[0][0]
    reserved = {i for ids, _ in pairs for i in ids}
    rest = [i for i in range(n) if i not in reserved]
    for a, b in zip(rest[::2], rest[1::2], strict=True):
        pairs.append(((a, b), exact.Mat([[singles.get(a, 1), 0], [0, singles.get(b, 1)]])))
    return pairs
