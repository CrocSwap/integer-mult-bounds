#!/usr/bin/env python3
"""Separate exact oracle: direct published-group averaging and literal forms.

No primary verifier, quotient table, or predecessor executable is imported.
The published character-table identification remains a cited premise.
Prepared for alephnan with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def parity(x):
    return x.bit_count() & 1


def table_oracle(data):
    rows = data['characters']
    group_order = 92897280
    require(data['order'] == group_order, 'projective group order')
    require(data['adjoint_character_rows'] == [1, 10], 'adjoint identification')
    require(data['pauli_nonidentity_class'] == 2, 'Pauli class identification')
    require(len(rows) == 67 and all(len(r) == 67 for r in rows), '67-square table')
    require(all(type(v) is int for r in rows for v in r), 'integer table')
    columns = list(zip(*rows))
    sizes = []
    for col in columns:
        centralizer = sum(x*x for x in col)
        size, remainder = divmod(group_order, centralizer)
        require(remainder == 0, 'integral conjugacy size')
        sizes.append(size)
    require(sum(sizes) == group_order and sizes[:2] == [1, 63], 'class mass')
    # Column orthogonality, rather than the primary's row-orthogonality loop.
    for j, col in enumerate(columns):
        for other in columns[:j]:
            require(sum(x*y for x, y in zip(col, other)) == 0, 'column orthogonality')
    require(sum(r[0]**2 for r in rows) == group_order, 'degree squares')
    inflated = [(i+1, r) for i, r in enumerate(rows) if r[0] == r[1]]
    require(len(inflated) == 30, 'thirty quotient characters')
    require(sum(r[0]**2 for _, r in inflated) == 1451520, 'quotient degree squares')
    adjoint = [1+x for x in rows[9]]
    require(all(a == 0 or a in (1, 2, 4, 8, 16, 32, 64) for a in adjoint),
            'adjoint trace alphabet')
    # For a symplectic element with d fixed dimensions, its 64 projective
    # Pauli lifts have averaged Ad^5 = 2^(-d) * (2^d)^5 = 2^(4d).
    # Thus full 67-class inner products directly give W_9, without forming
    # the 30-class quotient or reconstructing its fixed-dimension list.
    multiplicities = []
    for source_row, character in inflated:
        numerator = sum(size*a**5*c for size, a, c in zip(sizes, adjoint, character))
        value, remainder = divmod(numerator, group_order)
        require(remainder == 0 and value >= 0, 'direct width-nine multiplicity')
        multiplicities.append((source_row, character[0], value))
    require(sum(degree*m for _, degree, m in multiplicities) == 8**8,
            'width-nine multiplicity-space dimension')
    missing = [(row, degree) for row, degree, m in multiplicities if m == 0]
    require(missing == [(2, 7)], 'unique missing degree-seven character')
    require(sum((8*degree)**2 for _, degree, m in multiplicities if m) == 92894144,
            'rank at width nine')
    ratios = [Fraction(m, degree) for _, degree, m in multiplicities if m]
    require((min(ratios), max(ratios)) == (Fraction(1, 2), Fraction(269)),
            'multiplicity ratio bounds')
    # The S gate has adjoint trace 32, hence symplectic fixed dimension 5.
    # Every rank-one symplectic displacement is a transvection. The unique
    # published source class at this trace pins its degree-seven value.
    transvection_columns = [j for j, a in enumerate(adjoint) if a == 32]
    require(transvection_columns == [31], 'literal S trace class')
    require(rows[1][31] == -5 and sizes[31] == 126, 'transvection character value')
    # Width one is the positive control: the multiplicity space is trivial.
    one = [Fraction(sum(s*a*c for s, a, c in zip(sizes, adjoint, r)), group_order)
           for _, r in inflated]
    require(one == [1] + [0]*29, 'natural Pauli multiplicity positive control')
    return multiplicities


def form_oracle(n):
    """Act on full truth tables, without using the fixed-form shortcut Q(v)=1."""
    half, mask = 1 << n, (1 << n)-1
    labels = range(half*half)
    forms = {}
    for alpha in range(half):
        for beta in range(half):
            truth = tuple(parity((x & mask) & (x >> n))
                          ^ parity(alpha & (x & mask)) ^ parity(beta & (x >> n))
                          for x in labels)
            # Distinguish the two orbits by their truth-table zero count,
            # independently of computing alpha.beta as the Arf formula.
            zeros = truth.count(0)
            forms[truth] = zeros
    zero_counts = sorted(set(forms.values()))
    require(zero_counts == [2**(2*n-1)-2**(n-1), 2**(2*n-1)+2**(n-1)],
            'quadratic zero counts')
    orbit_sizes = [sum(k == z for k in forms.values()) for z in zero_counts]
    require(orbit_sizes == zero_counts, 'quadratic orbit cardinalities')
    neighbors = {q: set() for q in forms}
    for v in range(1, half*half):
        a, b = v & mask, v >> n
        permutation = [x ^ (v if parity((x & mask) & b) ^ parity((x >> n) & a) else 0)
                       for x in labels]
        require(len(set(permutation)) == half*half, 'transvection bijection')
        fixed = {z: 0 for z in zero_counts}
        for q, z in forms.items():
            transformed = tuple(q[x] for x in permutation)
            require(transformed in forms and forms[transformed] == z, 'form action')
            neighbors[q].add(transformed)
            fixed[z] += transformed == q
        require(list(fixed.values()) == [2**(2*n-2)]*2, 'literal transvection fixed counts')
    for z in zero_counts:
        start = next(q for q in forms if forms[q] == z)
        seen, pending = {start}, [start]
        while pending:
            for q in neighbors[pending.pop()] - seen:
                seen.add(q)
                pending.append(q)
        require(len(seen) == z, 'two actual transvection orbits')
    return {'axes': n, 'forms': len(forms), 'orbits': orbit_sizes,
            'transvections': half*half-1, 'fixed_per_orbit': 2**(2*n-2)}


def pauli_and_phase_oracle():
    """Literal signed permutation matrices for all 64 three-qubit Paulis."""
    paulis = []
    for v in range(64):
        a, b = v & 7, v >> 3
        paulis.append(tuple((x ^ a, ((a & b).bit_count()+2*parity(b & x)) % 4)
                            for x in range(8)))
    for v in range(64):
        for w in range(64):
            product = tuple((paulis[v][paulis[w][x][0]][0],
                             (paulis[w][x][1]+paulis[v][paulis[w][x][0]][1]) % 4)
                            for x in range(8))
            phase = (product[0][1]-paulis[v ^ w][0][1]) % 4
            require(all(y == z and (p-q) % 4 == phase
                        for (y, p), (z, q) in zip(product, paulis[v ^ w])), 'Pauli multiplication')
            av, bv, aw, bw = v & 7, v >> 3, w & 7, w >> 3
            require(phase % 2 == (parity(av & bw) ^ parity(bv & aw)), 'Pauli polar cocycle')
    # S on the first qubit is diagonal with exponents x_0. Conjugate every
    # literal Pauli and identify its signed Pauli label and native phase.
    fixed_labels = 0
    for v, matrix in enumerate(paulis):
        conjugate = tuple((y, (p+(y & 1)-(x & 1)) % 4)
                          for x, (y, p) in enumerate(matrix))
        expected = v ^ (8 if v & 1 else 0)
        phase = (conjugate[0][1]-paulis[expected][0][1]) % 4
        require(phase in (0, 2), 'Hermitian Pauli sign')
        require(all(y == z and (p-q) % 4 == phase
                    for (y, p), (z, q) in zip(conjugate, paulis[expected])), 'literal S conjugation')
        fixed_labels += expected == v
    require(fixed_labels == 32, 'S fixed-label space')
    trace_real = sum((1, 0, -1, 0)[x & 1] for x in range(8))
    trace_imag = sum((0, 1, 0, -1)[x & 1] for x in range(8))
    require((trace_real, trace_imag) == (4, 4), 'native S trace with phase')
    for orbit in (28, 36):
        require(Fraction(5*orbit, 7) > 16, 'strict width-ten contradiction')
    return {'pauli_products': 4096, 'S_conjugations': 64,
            'S_trace': [trace_real, trace_imag], 'fixed_pauli_labels': fixed_labels}


def main():
    raw = (HERE/'table.json').read_bytes()
    declared = json.loads((HERE/'EXTERNAL.json').read_text(encoding='utf8'))
    require(sha256(raw).hexdigest() == declared['table_sha256'], 'published table pin')
    data = json.loads(raw)
    multiplicities = table_oracle(data)
    forms = [form_oracle(n) for n in (1, 2, 3)]
    pauli = pauli_and_phase_oracle()
    changed = json.loads(raw)
    changed['characters'][1][31] += 1
    try:
        table_oracle(changed)
    except ValueError:
        pass
    else:
        raise ValueError('changed transvection character escaped independent oracle')
    print(json.dumps({'status': 'PASS_INDEPENDENT_CLIFFORD_THRESHOLD_TEN',
                      'direct_67_class_width_nine': multiplicities,
                      'literal_quadratic_forms': forms, 'literal_paulis': pauli,
                      'rejected_control': 'changed published transvection character',
                      'scope': 'Separate arithmetic and literal finite oracle; cited character-table group identification retained.'}, indent=2))


if __name__ == '__main__':
    main()
