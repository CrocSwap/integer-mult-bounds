#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Emit the source-bound PR2339 initial prefix in the retained native vocabulary.

The K_G convention and warp/add/unwarp expansion are PR2226 / PR2269 work.
This instantiates the previously unlowered PR2339 initial terms, retains exact
Gaussian phases, and exports their scalar and monomial operation bills.
Prepared for commdata2338 with substantial OpenAI Codex assistance.
"""
import argparse
import gzip
import hashlib
import json
import sys
import types
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
COMPILER = 'research/frame-sa504/vendor/clifford/clifford_exact.py'


def load_compiler():
    # The retained compiler uses asserts: preserve its guards even under -O.
    module = types.ModuleType('_t74_prefix_clifford')
    sys.modules[module.__name__] = module
    exec(compile((ROOT / COMPILER).read_bytes(), COMPILER, 'exec', optimize=0), module.__dict__)
    return module


def conjugate(c, op):
    """All K circuits here contain only permutations and Gaussian diagonals."""
    out = c.Op(op.n, c.identity(op.n), [])
    for e in op.circuit:
        if e[0] == 'P':
            gate = c.perm(op.n, e[1])
        elif e[0] == 'D':
            gate = c.diag(op.n, e[1], tuple((-a) % 4 for a in e[2]))
        else:
            raise ValueError('unexpected gate in K_G')
        out = out.then(gate)
    return out


def make_k(c, columns, n):
    # Exact PR2269 bw_adapters.Kop convention, credited rather than new.
    rows = c.transpose(tuple(columns), n)
    gi_cols = c.transpose(c.inv(rows, n), n)
    q = tuple((1 << i) ^ sum(c.parity(a & b) << j for j, b in enumerate(gi_cols))
              for i, a in enumerate(gi_cols))
    return c.perm(n, rows).then(c.diag(n, q))


def primitive_bound(q):
    """Inherited real-component Horner bound, including private-stream clearing."""
    a, b = abs(q.numerator), q.denominator
    if a == 0 or b & (b - 1):
        raise ValueError('nonzero dyadic coefficient required')
    return 3 + a.bit_length() - 1 + a.bit_count() + b.bit_length() - 1


def address_gates(rec):
    """Concrete CNOT / Gaussian-unit-phase decomposition, no Fourier calls."""
    rows = list(rec['matrix_rows'])
    n = len(rows)
    elimination = []
    for j in range(n):
        pivot = next(i for i in range(j, n) if rows[i] >> j & 1)
        if pivot != j:
            # An address SWAP is explicitly three coordinate XORs.
            for target, source in [(j, pivot), (pivot, j), (j, pivot)]:
                rows[target] ^= rows[source]
                elimination.append(['cnot', target, source])
        for i in range(n):
            if i != j and rows[i] >> j & 1:
                rows[i] ^= rows[j]
                elimination.append(['cnot', i, j])
    if rows != [1 << j for j in range(n)]:
        raise ValueError('singular address map')
    gates = [['z4', j, a] for j, a in enumerate(rec['linear_Z4']) if a]
    gates += [['cz', i, j] for i in range(n) for j in range(i + 1, n)
              if rec['quadratic_rows'][i] >> j & 1]
    gates += list(reversed(elimination))
    gates += [['x', j] for j in range(n) if rec['offset'] >> j & 1]
    if rec['phase']:
        gates.append(['phase', rec['phase']])
    return gates


def build():
    c = load_compiler()
    result = {'schema_version': 1, 'kind': 'PR2339_NATIVE_INITIAL_PREFIX', 'providers': {}}
    for provider in ('base', 'extra'):
        path = HERE / 'inputs' / f'BORROW-WORD-80{provider}.json.gz'
        raw = path.read_bytes()
        w = json.loads(gzip.decompress(raw))
        n = w['report']['h']
        terms = w['initial_corrections']
        operators = sorted({x['operator_word'][0] for x in terms})
        recipes = {}
        for op in operators:
            k = make_k(c, w['warps'][op - 1][2], n)
            ck = conjugate(c, k)
            for name, physical in [('K', k), ('inverse', k.adjoint()),
                                   ('conjugate', ck), ('transpose', ck.adjoint())]:
                rec, _ = c.lower_child(physical)
                if rec['rank'] != 0 or rec['right'] is not None:
                    raise ValueError('initial compensation needs a positive-rank child')
                recipes[f'{op}:{name}'] = {
                    'monomial': rec['left'],
                    'address_gates': address_gates(rec['left']),
                }
        programs = {}
        for backward in (False, True):
            stream = []
            for op in operators:
                group = [term for term in terms if term['operator_word'] == [op]]
                source, = {term['source'] for term in group}
                before, after = ('conjugate', 'transpose') if backward else ('K', 'inverse')
                stream.append(['monomial', source, f'{op}:{before}'])
                for term in group:
                    t, s, q = term['target'], source, Fraction(term['coefficient'])
                    if backward:
                        t, s, q = s, t, -q
                    stream.append(['scalar', ['add', ['L', t], ['L', s], q.numerator, q.denominator], 0])
                stream.append(['monomial', source, f'{op}:{after}'])
            programs['backward' if backward else 'forward'] = stream
        result['providers'][provider] = {
            'word_sha256': hashlib.sha256(raw).hexdigest(),
            'address_bits': n, 'operators': operators, 'recipes': recipes,
            'programs': programs,
            'scalar_lowerings': {
                str(q): ([['clear'], ['read_source']] + ([['half']] if q.denominator == 2 else [])
                         + [['write_target', 1 if q > 0 else -1], ['clear']])
                for q in (Fraction(1), Fraction(-1), Fraction(1, 2), Fraction(-1, 2))
            },
            'bill_per_orientation': {
                'positive_recursive_children': 0,
                'scalar_add_macros': len(terms),
                'monomial_applications': 2 * len(operators),
                'ungrouped_monomial_applications': 2 * len(terms),
                'real_component_scalar_primitive_bound': 2 * sum(primitive_bound(Fraction(t['coefficient'])) for t in terms),
                'scalar_bound_excludes_monomial_routing': True,
                'coefficient_streams_peak': 1,
            },
        }
    return result


def encoded(data):
    return json.dumps(data, sort_keys=True, separators=(',', ':')).encode() + b'\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, help='write exclusively to a new file')
    args = parser.parse_args()
    data = encoded(build())
    if args.out:
        with args.out.open('xb') as f:
            f.write(gzip.compress(data, mtime=0) if args.out.suffix == '.gz' else data)
    else:
        expected = gzip.decompress((HERE / 'PREFIX.json.gz').read_bytes())
        if json.loads(data) != json.loads(expected):
            raise ValueError('regenerated prefix differs from the complete certificate')
    print('PASS_T74_PREFIX_REGEN providers=2 programs=4 terms_per_program=64')


if __name__ == '__main__':
    main()
