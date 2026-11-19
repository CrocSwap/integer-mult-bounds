"""Run the complete sparse decoder against independently formed Bell observations.

The fixture operators are literal monomial 16-by-16 Clifford matrices. All
entries and mixtures are Gaussian integers, with powers of i stored exactly.
apoursh with substantial OpenAI Codex and separate agent assistance. Apache-2.0.
"""
from functools import reduce
from operator import xor
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bell_reads import iter_reads
from compile_row import DENOMINATOR, IDENTITY


def require(condition, msg):
    if not condition:
        raise ValueError(msg)


def parity(x):
    return x.bit_count() % 2


def rotate(z, exponent):
    a, b = z
    return ((a, b), (-b, a), (-a, -b), (b, -a))[exponent % 4]


def add(z, w):
    return z[0]+w[0], z[1]+w[1]


def scale(z, w):
    return z[0]*w, z[1]*w


def make_section(kind):
    """Specify the matrix by (row, quarter-phase exponent) in each column."""
    sections = []
    for j in range(16):
        quarter = int(bool(kind & 1)) * (j & 1)
        cz12 = (j & 1) * ((j >> 1) & 1)
        cz13 = (j & 1) * ((j >> 2) & 1)
        quarter += 2 * (int(bool(kind & 2))*cz12 + int(bool(kind & 4))*cz13)
        # For kinds 8..15 add CNOT from qubit two to one after the phases.
        row = j ^ ((j >> 1) & 1) if kind & 8 else j
        sections.append((row, quarter % 4))
    return tuple(sections)


def representative(section, kind, p):
    z, x = p & 15, p >> 4
    # An arbitrary but reproducible projective representative for each column.
    gauge = (kind + 3*p + p.bit_count()) % 4
    return tuple((row ^ x, (phase + gauge + 2*parity(row & z)) % 4)
                 for row, phase in section)


def literal_bell(u, t):
    """Apply U x U to all 16 entries of vec(X^x Z^z), then identify the output."""
    z, x = t & 15, t >> 4
    destination = [0]*16
    phases = [0]*16
    for k in range(16):
        row, a = u[k ^ x]
        col, b = u[k]
        destination[col] = row
        phases[col] = (a+b+2*parity(k & z)) % 4
    shift = destination[0]
    theta = phases[0]
    fourier = sum(1 << i for i in range(4) if (phases[1 << i]-theta) % 4 == 2)
    require(all(destination[j] == (j ^ shift)
                and phases[j] == (theta+2*parity(j & fourier)) % 4 for j in range(16)),
            "literal Bell output was not a single signed label")
    return (shift << 4) | fourier, theta


def materialize_fixture():
    operators = []
    sections = [make_section(k) for k in range(16)]
    for kind, section in enumerate(sections):
        for p in (0, 1, 18, 37):
            u = representative(section, kind, p)
            amplitude = ((kind+p) % 5-2, 1+(kind+2*p) % 3)
            table = tuple(literal_bell(u, t) for t in range(256))
            operators.append((kind, p, u, amplitude, table))
    return sections, operators


def record(d, key, value):
    d[key] = add(d.get(key, (0, 0)), value)


def test_fibre(kind, sections, operators):
    reference = operators[4*kind][4]
    offset = reference[0][0]
    target = tuple(reference[t][0] ^ offset for t in IDENTITY)
    recovered = {}
    raw_terms = 0
    contributors = set()
    nontrivial_phases = set()
    reads = 0
    for read in iter_reads(target):
        reads += 1
        xi, zi = reduce(xor, read.input_labels) >> 4, reduce(xor, read.input_labels) & 15
        xo, zo = reduce(xor, read.output_labels) >> 4, reduce(xor, read.output_labels) & 15
        observed = {}
        # Form the raw singleton Y between the two compiled Bell tuples. Each
        # matching column of U^(tensor 13) contributes i^beta U. Restoring
        # the known 4^13 from normalized observations has been done here.
        for source, p, u, amplitude, table in operators:
            entries = [table[t] for t in read.input_labels]
            if tuple(label for label, _ in entries) != read.output_labels:
                continue
            contributors.add(source)
            beta = sum(theta for _, theta in entries)
            raw_terms += 1
            for col, (row, phase) in enumerate(u):
                record(observed, (row, col), rotate(amplitude, beta + phase))
        # Apply W_out Y W_in^{-1} literally to individual raw entries. The
        # signs are evaluated before the output and input X permutations.
        for (row, col), z in observed.items():
            if z == (0, 0):
                continue
            exponent = read.correction_i + 2*(parity(row & zo) + parity(col & zi))
            nontrivial_phases.add(exponent % 4)
            record(recovered, (row ^ xo, col ^ xi), scale(rotate(z, exponent), read.numerator))

    expected = {p: a for s, p, _, a, _ in operators if s == kind}
    for p in range(256):
        coefficient = (0, 0)
        for col, (row, phase) in enumerate(representative(sections[kind], kind, p)):
            coefficient = add(coefficient, rotate(recovered.get((row, col), (0, 0)), -phase))
        require(coefficient == scale(expected.get(p, (0, 0)), 16*DENOMINATOR),
                f"bad output coefficient for shape {kind}, Pauli {p}")
    require(reads == 4265 and kind in contributors and len(contributors) > 1,
            "fixture did not exercise undesired coset contributions")
    require(any(nontrivial_phases), "phase corrections were vacuous")
    return reads, raw_terms, len(contributors)


if __name__ == "__main__":
    sections, fixture = materialize_fixture()
    runs = [test_fibre(k, sections, fixture) for k in (0, 1)]
    print("PASS_COMPILED_BELL_MIXTURE",
          f"terms={sum(n for n, _, _ in runs)} operators={len(fixture)} coefficients=512",
          f"column_block_contributions={sum(n for _, n, _ in runs)}",
          f"contributing_shapes={','.join(str(n) for _, _, n in runs)}")
