#!/usr/bin/env python3
"""Four-call compensated two-image interfaces on two arbitrary inputs.

Cinna Davis, with OpenAI Codex assistance. Apache-2.0. No new kappa.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


class Field:
    def __init__(self, modulus=None):
        self.p = modulus
        self.zero = 0 if modulus else (Q(0), Q(0))
        self.one = 1 if modulus else (Q(1), Q(0))
        self.i = 4 if modulus else (Q(0), Q(1))

    def scalar(self, n, d=1):
        return n*pow(d, -1, self.p) % self.p if self.p else (Q(n, d), Q(0))

    def add(self, a, b):
        return (a+b) % self.p if self.p else (a[0]+b[0], a[1]+b[1])

    def neg(self, a):
        return -a % self.p if self.p else (-a[0], -a[1])

    def mul(self, a, b):
        return a*b % self.p if self.p else (a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0])

    def div(self, a, b):
        if self.p:
            return a*pow(b, -1, self.p) % self.p
        d = b[0]*b[0]+b[1]*b[1]
        return ((a[0]*b[0]+a[1]*b[1])/d, (a[1]*b[0]-a[0]*b[1])/d)

    def phase(self, e):
        values = (self.one, self.i, self.neg(self.one), self.neg(self.i))
        return values[e % 4]


def inverse_word(word):
    return [('-'+a if not a.startswith('-') else a[1:])
            if a.lstrip('-').startswith('S') else a for a in reversed(word)]


def programs():
    ans = {}
    for repaired in (False, True):
        S, Sinv = ['S0', 'S1', 'S2'], ['-S0', '-S1', '-S2']
        A = S+['U']+S if repaired else ['U']
        B = S+['V']+S if repaired else ['V']
        inverse_terms = []
        for k, coefficient in enumerate((-1, 2, -4, 8)):
            word = ['U']+['V', 'U']*k
            if repaired:
                word = Sinv+word+Sinv
            inverse_terms.append((coefficient, 15, word))
        ir = []

        def address(bank, word, restore=False):
            ir.extend({'op': 'address', 'bank': bank, 'letter': a,
                       'restores_shear_source': restore} for a in word)

        def shear(destination, source, terms):
            for numerator, denominator, word in terms:
                address(source, word)
                c = Q(numerator, denominator)
                ir.append({'op': 'add', 'destination': destination, 'source': source,
                           'coefficient': [c.numerator, c.denominator]})
                address(source, inverse_word(word), restore=True)

        def boundary():
            ir.extend([{'op': 'paid_C', 'bank': 0}, {'op': 'paid_C', 'bank': 1}])
            address(1, ['X'])  # C^-1 = X C, at one paid-call charge.

        boundary()
        shear(0, 1, [(-1, 1, [])])
        shear(1, 0, [(1, 1, [])])
        shear(0, 1, [(-1, 1, [])])
        L = [(1, 1, A), (2, 1, B)]
        shear(0, 1, L)
        shear(1, 0, [(-n, d, w) for n, d, w in inverse_terms])
        shear(0, 1, L)
        boundary()
        ans['phase_repaired' if repaired else 'original'] = ir
    return ans


def address_vector(v, letter, width, field):
    out = [field.zero]*len(v)
    for x, value in enumerate(v):
        image, exponent = x, 0
        for column in range(width):
            offset = 3*column
            a, b = (x >> offset) & 1, (x >> (offset+1)) & 1
            if letter == 'U':
                image ^= a << (offset+2)
            elif letter == 'V':
                image ^= ((a ^ b) << offset) | ((a ^ b) << (offset+1))
            elif letter == 'X':
                image ^= 1 << offset
            else:
                j = int(letter[-1])
                exponent += (-1 if letter.startswith('-') else 1)*((x >> (offset+j)) & 1)
        out[image] = field.mul(field.phase(exponent), value)
    return out


def paid_vector(v, width, field):
    out = list(v)
    a = field.div(field.add(field.one, field.i), field.scalar(2))
    b = field.div(field.add(field.one, field.neg(field.i)), field.scalar(2))
    for column in range(width):
        bit = 1 << (3*column)
        for x in range(len(v)):
            if x & bit:
                continue
            y = x ^ bit; left, right = out[x], out[y]
            out[x] = field.add(field.mul(a, left), field.mul(b, right))
            out[y] = field.add(field.mul(b, left), field.mul(a, right))
    return out


def execute(ir, initial, width, field, inverse=False, fault=None):
    state = [list(v) for v in initial]
    if inverse:
        state.reverse()
    skipped = False
    for event in ir:
        kind = event['op']
        if kind == 'paid_C':
            state[event['bank']] = paid_vector(state[event['bank']], width, field)
        elif kind == 'address':
            if (fault == 'omit_source_restore' and event.get('restores_shear_source')
                    and event['letter'] == 'U' and not skipped):
                skipped = True
                continue
            state[event['bank']] = address_vector(state[event['bank']], event['letter'], width, field)
        else:
            c = field.scalar(*event['coefficient'])
            if fault == 'wrong_inverse_sign' and event['coefficient'] == [-2, 15]:
                c = field.neg(c)
            d, s = event['destination'], event['source']
            state[d] = [field.add(x, field.mul(c, y)) for x, y in zip(state[d], state[s])]
    if inverse:
        state.reverse()
    return state


def matmul(a, b, field):
    n = len(a); out = [[field.zero]*n for _ in range(n)]
    for i in range(n):
        for k in range(n):
            if a[i][k] == field.zero:
                continue
            for j in range(n):
                if b[k][j] != field.zero:
                    out[i][j] = field.add(out[i][j], field.mul(a[i][k], b[k][j]))
    return out


def matrix_inverse(a, field):
    n = len(a)
    rows = [list(row)+[field.one if i == j else field.zero for j in range(n)]
            for i, row in enumerate(a)]
    for k in range(n):
        pivot = next((i for i in range(k, n) if rows[i][k] != field.zero), None)
        need(pivot is not None, 'independent target matrix invertible')
        rows[k], rows[pivot] = rows[pivot], rows[k]
        lead = rows[k][k]
        rows[k] = [field.div(x, lead) for x in rows[k]]
        for i in range(n):
            if i == k or rows[i][k] == field.zero:
                continue
            c = rows[i][k]
            rows[i] = [field.add(x, field.neg(field.mul(c, y)))
                       for x, y in zip(rows[i], rows[k])]
    return [row[n:] for row in rows]


def oracle(width, repaired, field):
    # Direct tensor entries and dense inversion; no inverse polynomial or shear IR.
    n = 8**width; C = [[field.zero]*n for _ in range(n)]
    L = [[field.zero]*n for _ in range(n)]
    a = field.div(field.add(field.one, field.i), field.scalar(2))
    b = field.div(field.add(field.one, field.neg(field.i)), field.scalar(2))
    for x in range(n):
        for y in range(n):
            value = field.one
            for k in range(width):
                u, v = (x//8**k) % 8, (y//8**k) % 8
                value = field.mul(value, a if u == v else b if u == (v ^ 1) else field.zero)
            C[x][y] = value
        # Independent bit-list maps for the two monomial branches.
        bits = [(x >> j) & 1 for j in range(3*width)]
        for which, coefficient in [('U', 1), ('V', 2)]:
            output = list(bits)
            for k in range(width):
                j = 3*k
                if which == 'U':
                    output[j+2] = (bits[j+2]+bits[j]) % 2
                else:
                    output[j], output[j+1] = bits[j+1], bits[j]
            row = sum(bit*2**j for j, bit in enumerate(output))
            phase = sum(bits)+sum(output) if repaired else 0
            L[row][x] = field.add(L[row][x], field.mul(field.scalar(coefficient), field.phase(phase)))
    target = matmul(C, matmul(L, C, field), field)
    return target, matrix_inverse(target, field)


def apply_matrix(matrix, v, field):
    out = []
    for row in matrix:
        value = field.zero
        for a, b in zip(row, v):
            if a != field.zero and b != field.zero:
                value = field.add(value, field.mul(a, b))
        out.append(value)
    return out


def verify_all(ir, repaired, width, field):
    fwd, inv = oracle(width, repaired, field); n = len(fwd)
    columns = 0
    for bank in range(2):
        for column in range(n):
            x = [[field.zero]*n for _ in range(2)]; x[bank][column] = field.one
            y = execute(ir, x, width, field)
            expected = [apply_matrix(fwd, x[0], field), apply_matrix(inv, x[1], field)]
            need(y == expected, 'full independent target column')
            need(execute(ir, y, width, field, inverse=True) == x, 'two-sided full-column inverse')
            z = execute(ir, x, width, field, inverse=True)
            need(execute(ir, z, width, field) == x, 'inverse then forward column')
            columns += 1
    return columns


def calculate():
    pins = json.loads((HERE/'SOURCES.json').read_text()); sources = {}
    for row in pins['files']:
        if row['usage'] == 'input':
            raw = (ROOT/row['path']).read_bytes()
            need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source bytes')
            sources[row['path']] = row['sha256']
    # Corroborate the precise all-width algebraic premise independently of IR.
    polynomial = [Q(-1, 15), Q(2, 15), Q(-4, 15), Q(8, 15)]
    product = [Q(0)]*4
    for k, c in enumerate(polynomial):
        product[k] += c
        product[(k+1) % 4] += 2*c
    need(product == [1, 0, 0, 0], 'cyclic inverse polynomial')
    prog = programs(); results = {}
    for name, ir in prog.items():
        repaired = name == 'phase_repaired'
        field = Field()
        ratio_word = (['S0', 'S1', 'S2', 'V', 'U', '-S0', '-S1', '-S2']
                      if repaired else ['V', 'U'])
        for column in range(8):
            basis = [field.zero]*8; basis[column] = field.one
            value = list(basis)
            for _ in range(4):
                for letter in ratio_word:
                    value = address_vector(value, letter, 1, field)
            need(value == basis, 'actual absolute-phase ratio fourth power')
        counts = dict(sorted(Counter(e['op'] for e in ir).items()))
        need(counts == {'add': 11, 'address': 138 if repaired else 42, 'paid_C': 4}, 'complete literal invoice')
        exact = verify_all(ir, repaired, 1, Field())
        modular = verify_all(ir, repaired, 2, Field(17))
        field = Field(17); width = 3; n = 8**width
        dirty = [[(j*j+3*j+7*bank+1) % 17 for j in range(n)] for bank in range(2)]
        image = execute(ir, dirty, width, field)
        need(execute(ir, image, width, field, inverse=True) == dirty, 'width-three dirty round trip')
        controls = []
        fixture = [[field.scalar(j+1+3*bank) for j in range(8)] for bank in range(2)]
        ideal = execute(ir, fixture, 1, field)
        for fault in ('wrong_inverse_sign', 'omit_source_restore'):
            need(execute(ir, fixture, 1, field, fault=fault) != ideal, 'reject '+fault)
            controls.append(fault)
        need(ideal[1] != fixture[1], 'inverse-volume partner is transformed, not returned dirt')
        controls.append('cannot_label_partner_as_restored_dirt')
        paid_indices = [i for i, e in enumerate(ir) if e['op'] == 'paid_C']
        shortened = [e for i, e in enumerate(ir) if i != paid_indices[-1]]
        need(execute(shortened, fixture, 1, field) != ideal,
             'omitting fourth paid call changes intended map')
        controls.append('cannot_omit_fourth_paid_call')
        results[name] = {'instruction_counts': counts, 'exact_Qi_full_columns_width_one': exact,
                         'mod17_i4_full_columns_width_two': modular,
                         'mod17_width_three_independent_dirty_round_trip': True,
                         'inverse_uses_same_program_with_two_bank_swaps': True,
                         'controls': controls}
    payload = (json.dumps(prog, sort_keys=True, separators=(',', ':'))+'\n').encode()
    return prog, {'schema_version': 1, 'target': 'diag(F_f,F_f^-1), two arbitrary inputs',
                  'no_new_kappa': True, 'source_hashes': sources,
                  'cyclic_inverse_polynomial_product': [str(x) for x in product],
                  'program_payload_sha256': hashlib.sha256(payload).hexdigest(), 'variants': results}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write-result', type=Path)
    args = ap.parse_args(); prog, actual = calculate()
    if args.write_result:
        with args.write_result.with_name('PROGRAM.json').open('x') as stream:
            json.dump(prog, stream, indent=2, sort_keys=True); stream.write('\n')
        with args.write_result.open('x') as stream:
            json.dump(actual, stream, indent=2, sort_keys=True); stream.write('\n')
    else:
        need(json.loads((HERE/'PROGRAM.json').read_text()) == prog, 'literal program equality')
        need(json.loads((HERE/'RESULT.json').read_text()) == actual, 'receipt equality')
    print('PASS_TWO_IMAGE_COMPENSATED_PAIR variants=2 paid_calls=4 '
          'arbitrary_input_columns=288 no_new_kappa')


if __name__ == '__main__':
    main()
