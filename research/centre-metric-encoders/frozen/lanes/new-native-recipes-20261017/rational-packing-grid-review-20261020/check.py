#!/usr/bin/env python3
"""Check the paid rational packing and its exact input domains."""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
from pathlib import Path
import argparse
import importlib.util
import json

HERE = Path(__file__).resolve().parent
HELPER = HERE.parent/'row-capture-native-review-20261020/check.py'
PIN = '5b8f2839db4fd4b0e4b24d5b8f8938c74a15497ae0e58f324896cf431d3ecb84'
if sha256(HELPER.read_bytes()).hexdigest() != PIN:
    raise ValueError('Independent arithmetic helper pin')
spec = importlib.util.spec_from_file_location('independent_real_rows', HELPER)
q = importlib.util.module_from_spec(spec)
spec.loader.exec_module(q)
q.read(HELPER, PIN)
need = q.need
SOURCE = q.LANES/'bridge-access-20261017/rational-unitary-packing-20261020'
MATRIX = q.LANES/'independent-review-20261017/odd-unitary-packing-20261020'
ZERO, ONE = (0, 0), (1, 0)


def realify(matrix, ncols):
    result = [{} for _ in range(2*len(matrix))]
    for i, row in enumerate(matrix):
        for key, pair in row.items():
            j, (a, b) = int(key), tuple(map(F, pair))
            need(0 <= j < ncols, 'Complex column')
            for target, source, value in ((2*i, 2*j, a), (2*i, 2*j+1, -b),
                                          (2*i+1, 2*j, b), (2*i+1, 2*j+1, a)):
                if value:
                    result[target][source] = value
    return result


def scale(rows, value):
    return [{j: value*x for j, x in row.items() if value*x} for row in rows]


def heights(rows):
    h2, h3 = 0, 0
    for row in rows:
        for value in row.values():
            d, a, b = value.denominator, 0, 0
            while d % 2 == 0:
                d, a = d//2, a+1
            while d % 3 == 0:
                d, b = d//3, b+1
            need(d == 1, 'Only the stated denominator primes')
            h2, h3 = max(h2, a), max(h3, b)
    return h2, h3


def inverse_word(word):
    return [[op, t, s, str(-F(value) if op == 'add' else 1/F(value))]
            for op, t, s, value in reversed(word)]


def ordinary(word):
    result = []
    for op, t, s, value in word:
        need(op in ('add', 'scale', 'odd'), 'Literal component grammar')
        if op == 'odd':
            need(s is None and F(value) in (F(3), F(1, 3)), 'Fixed odd scan')
        result.append(['scale' if op == 'odd' else op, t, s, value])
    return result


def check_word(word, expected, active, target_bill):
    gates = ordinary(word)
    need(q.reverse(gates, 1280) == q.transpose(expected, 1280), 'All1280 reverse input columns')
    state = q.unit(1280)
    peak, h2, h3 = F(1), 0, 0
    scans = Counter()
    before_division, after_division = [], []
    for (op, t, s, value), gate in zip(word, gates):
        value = F(value)
        need(0 <= t < active and (s is None or 0 <= s < active), 'Declared active real fields')
        if op == 'odd':
            scans[str(value)] += 1
        if op == 'odd' and value == F(1, 3):
            before_division.append(dict(state[t]))
        if op == 'add':
            need(s != t, 'Distinct ADD components')
            q.add(state[t], state[s], value)
        else:
            need(s is None, 'Scale has no source')
            state[t] = {j: value*x for j, x in state[t].items()}
        if op == 'odd' and value == F(1, 3):
            after_division.append(dict(state[t]))
        peak = max(peak, sum(map(abs, state[t].values()), F(0)))
        a, b = heights([state[t]])
        h2, h3 = max(h2, a), max(h3, b)
    need(state == expected, 'Separate forward prefix replay')
    need(state[active:] == q.unit(1280)[active:], 'Every outside field remains arbitrary')
    binary_gates = [gate for gate, old in zip(gates, word) if old[0] != 'odd']
    cost = q.price(binary_gates)//2
    need(cost == target_bill and scans == {'3': 16, '1/3': 16}, 'Separate binary and odd invoices')
    guard = 2**h2 * 3**h3
    for row in before_division:
        need(all((guard*x).denominator == 1 and int(guard*x) % 3 == 0 for x in row.values()),
             'Every division input is a multiple of three on the paid grid')
    need(all((guard*x).denominator == 1 for row in after_division for x in row.values()),
         'All postdivision columns are integral on the same grid')
    no_odd = 2**h2
    need(any((no_odd*x).denominator % 3 == 0 for row in after_division for x in row.values()),
         'The arbitrary unscaled dyadic-grid contract fails')
    return {
        'real_columns': 1280, 'untouched_complex_fields': (1280-active)//2,
        'old_real_scalar_units': cost, 'odd_scans': dict(scans), 'instructions': len(word),
        'prefix_real_row_one_norm': str(peak), 'binary_height': h2, 'odd_height': h3,
        'local_root_numerator_factor': guard, 'new_fields': 0, 'native_children': 0,
        'exact_division_on_all_scaled_columns': True,
    }, after_division


def fadd(a, b):
    return ((a[0]+b[0]) % 3, (a[1]+b[1]) % 3)


def fneg(a):
    return (-a[0] % 3, -a[1] % 3)


def fmul(a, b):
    return ((a[0]*b[0]-a[1]*b[1]) % 3, (a[0]*b[1]+a[1]*b[0]) % 3)


def finv(a):
    norm = (a[0]*a[0]+a[1]*a[1]) % 3
    need(norm, 'A nonzero F9 element has nonzero norm')
    factor = pow(norm, -1, 3)
    return (a[0]*factor % 3, -a[1]*factor % 3)


def mod3(value):
    value = F(value)
    need(value.denominator % 3, 'A residue requires a denominator prime to three')
    return value.numerator*pow(value.denominator, -1, 3) % 3


def residue(matrix, multiplier=F(1)):
    return [{int(j): (mod3(multiplier*F(pair[0])), mod3(multiplier*F(pair[1])))
             for j, pair in row.items()
             if (mod3(multiplier*F(pair[0])), mod3(multiplier*F(pair[1]))) != ZERO}
            for row in matrix]


def frank(rows):
    pivots = {}
    for raw in rows:
        row = dict(raw)
        while row:
            j = min(row)
            if j not in pivots:
                inv = finv(row[j])
                pivots[j] = {k: fmul(v, inv) for k, v in row.items()}
                break
            factor = row[j]
            for k, value in pivots[j].items():
                entry = fadd(row.get(k, ZERO), fneg(fmul(factor, value)))
                if entry == ZERO:
                    row.pop(k, None)
                else:
                    row[k] = entry
    return len(pivots)


def ftrace(rows):
    value = ZERO
    for i, row in enumerate(rows):
        value = fadd(value, row.get(i, ZERO))
    return value


def block_domain(packing, numerator, word, inverse):
    mod = residue(packing, F(3))
    need(frank(mod) == 1, 'Packing numerator has Gaussian rank one modulo three')
    inv = finv(mod[0][0])
    normalized = [fmul(mod[0].get(j, ZERO), inv) for j in range(4)]
    need(normalized == [(1, 0), (2, 1), (2, 2), (2, 0)], 'Exact published Gaussian syndrome')
    # The first quartet in each word is complete; the other three are disjoint.
    first = [g for g in word if g[1] < 8]
    first_inverse = [g for g in inverse if g[1] < 8]
    outcomes = {}
    for name, gates, endpoint in [('R', first, realify(packing, 4)),
                                   ('Rstar', first_inverse, q.transpose(realify(packing, 4), 8))]:
        state = q.unit(8)
        rows = []
        for op, t, s, value in gates:
            value = F(value)
            if op == 'add':
                q.add(state[t], state[s], value)
            else:
                state[t] = {j: value*x for j, x in state[t].items()}
            if op == 'odd' and value == F(1, 3):
                rows.append(dict(state[t]))
        need(state == endpoint and len(rows) == 4, 'Complete literal quartet and four real divisions')
        accepted = 0
        for x in product(range(3), repeat=8):
            literal = all(sum((v*x[j] for j, v in row.items()), F(0)).denominator % 3
                          for row in rows)
            final = all(sum((v*x[j] for j, v in row.items()), F(0)).denominator % 3
                        for row in endpoint)
            need(literal == final, 'Literal division domain equals the exact dyadic endpoint domain')
            if name == 'R':
                syndrome = ZERO
                for j, coefficient in enumerate(normalized):
                    syndrome = fadd(syndrome, fmul(coefficient, (x[2*j], x[2*j+1])))
                need(literal == (syndrome == ZERO), 'Literal divisions equal the stated Gaussian congruence')
            accepted += literal
        need(accepted == 729, 'One Gaussian condition in four Gaussian variables')
        outcomes[name] = {'residue_inputs': 6561, 'accepted_residues': accepted,
                          'literal_division_domain_equals_dyadic_endpoint': True}
    real_rank = frank([{j: (mod3(value), 0) for j, value in row.items() if mod3(value)}
                       for row in numerator])
    need(real_rank == 2, 'Independent real residue rank')
    return {'gaussian_rank': 1, 'real_rank': real_rank,
            'normalized_syndrome_F9': normalized, 'exhaustive_domains': outcomes}


def scan_checks():
    transitions = 0
    for carry in range(3):
        for bit in range(2):
            out = (bit-carry) % 2
            next_carry = (carry+3*out-bit)//2
            need(0 <= next_carry < 3 and 2*next_carry == carry+3*out-bit,
                 'Division finite-control invariant')
            out, next_carry = (3*bit+carry) % 2, (3*bit+carry)//2
            need(0 <= next_carry < 3 and 3*bit+carry == out+2*next_carry,
                 'Multiplication finite-control invariant')
            transitions += 2
    cases = 0
    for width in range(1, 13):
        modulus = 2**width
        for n in range(-modulus//2, modulus//2):
            unsigned = n % modulus
            quotient = unsigned*pow(3, -1, modulus) % modulus
            carry = (3*quotient-unsigned)//modulus
            sign_in, sign_out = int(n < 0), int(quotient >= modulus//2)
            valid = carry == 3*sign_out-sign_in
            need(valid == (n % 3 == 0), 'Independent modular-inverse quotient domain')
            if valid:
                need(quotient-sign_out*modulus == n//3, 'Exact signed quotient')
            product_unsigned = 3*unsigned % modulus
            carry = (3*unsigned-product_unsigned)//modulus
            sign_out = int(product_unsigned >= modulus//2)
            valid = carry == 3*sign_in-sign_out
            fits = -modulus//2 <= 3*n < modulus//2
            need(valid == fits, 'Independent multiplication overflow domain')
            if valid:
                need(product_unsigned-sign_out*modulus == 3*n, 'Exact signed product')
            cases += 2
    return {'finite_control_transitions': transitions, 'signed_cases': cases, 'max_width': 12}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    freeze = q.frozen(SOURCE, 'FREEZE.json',
                      '2db9b1d5425dea76345ecbfde9a601e47a620693fc5e58350d311db292fc5fdc')
    for path, digest in freeze['sources'].items():
        q.read(q.LANES/path, digest)
    q.frozen(MATRIX, 'FREEZE.json', '22769396f123964addb9024b2fda452148388c67868714b4121a8fe3bfb9d410')
    q.frozen(q.LANES/'bridge-review-20261017/odd-grid-a8-review-20261017', 'FREEZE.json',
             '81ebbea971c0902a80479f9af4c82e72c660093c9f712b537690293aaaf21d60')
    source = json.loads(q.read(MATRIX/'run-normal/PACKING.json.gz',
                               'b460c1b4603f4b75da5ca4bf1da4a642f2cc4d970599f9c1068832e7b230ac32', True))
    prior = json.loads(q.read(q.RAW/'metric-completion-20261020/twenty-four-v2-normal/UNITARY-24.json.gz',
                              '9be7deb70acfc20d98408c84d59a24dbd6e2eddaea408958ec64b6003eb75f8c', True))
    q.frozen(q.LANES/'independent-review-20261017/unitary-footprint-review-20261020', 'FREEZE.json',
             'c537f75e6b76397e8fa390cd03a01e8021b7e0e55ff6c8932c3cc439613d0a61')
    need(source['original_readers'] == prior['original_centre_readers'],
         'The reader is the accepted actual sixteen-row reader')
    packet = json.loads(q.read(SOURCE/'actual-normal/PACKING.json',
                               '1076d6e7b1c9d0fe1cf6c4d04130236ed8bed052b2f811c48f7e08b3ad7c11f5'))
    a = realify([{'0': ['1', '0'], '1': ['1', '1']},
                 {'0': ['-1', '1'], '1': ['1', '0']}], 2)
    b = realify([{'0': ['1', '-1'], '1': ['0', '-1']},
                 {'0': ['0', '-1'], '1': ['1', '1']}], 2)
    need(q.mul(q.transpose(a, 4), a) == scale(q.unit(4), F(3)) and
         q.mul(q.transpose(b, 4), b) == scale(q.unit(4), F(3)), 'Both norm-three identities')
    aa = q.transpose(a, 4)+[{j+4: x for j, x in row.items()} for row in q.transpose(a, 4)]
    bb = b+[{j+4: x for j, x in row.items()} for row in b]
    permutation = [0, 1, 4, 5, 2, 3, 6, 7]
    middle = [{j: F(1)} for j in permutation]
    numerator = q.mul(q.mul(aa, middle), bb)
    r = scale(numerator, F(1, 3))
    need(q.rows(packet['A_real']) == a and q.rows(packet['B_real']) == b and
         q.rows(packet['numerator_real']) == numerator and q.rows(packet['R_real']) == r,
         'Independent exact packing factors')
    need(realify(source['packing'], 4) == r and q.mul(q.transpose(r, 8), r) == q.unit(8)
         and q.mul(r, q.transpose(r, 8)) == q.unit(8), 'Actual packing and both unitary orders')
    words = packet['words']
    need(set(words) == {'packing', 'inverse'} and words['inverse'] == inverse_word(words['packing']),
         'Literal reverse inverse, including every odd opcode')
    rr = [{j+8*k: x for j, x in row.items()} for k in range(4) for row in r]+q.unit(1280)[32:]
    reports = {}
    reports['packing'], _ = check_word(words['packing'], rr, 32, 840)
    reports['inverse'], _ = check_word(words['inverse'], q.transpose(rr, 1280), 32, 840)
    need(reports['packing']['prefix_real_row_one_norm'] == '7' and
         reports['inverse']['prefix_real_row_one_norm'] == '6', 'Exact packing prefix norms')
    domains = block_domain(source['packing'], numerator, words['packing'], words['inverse'])
    cp, cpstar = (realify(source[key], 112) for key in ('precode', 'precode_adjoint'))
    c, cstar = (realify(source[key], 112) for key in ('code', 'code_adjoint'))
    need(cpstar == q.transpose(cp, 224) and cstar == q.transpose(c, 224), 'Both exact adjoints')
    need(q.mul(cp, cpstar) == q.unit(224) and q.mul(cpstar, cp) == q.unit(224),
         'The preliminary code is a dyadic unit')
    need(q.mul(c, cstar) == q.unit(224) and q.mul(cstar, c) == q.unit(224),
         'Both actual full unitary orders')
    ports = sum(source['packing_ports'], [])
    need(len(ports) == len(set(ports)) == 16 and
         packet['actual_code']['packing_ports'] == source['packing_ports'], 'Actual disjoint quartets')

    def placed(word):
        return [[op, 2*ports[t//2]+t % 2, None if s is None else 2*ports[s//2]+s % 2, value]
                for op, t, s, value in word]

    need(packet['actual_code']['words']['code'] ==
         source['precode_words']['precode']+placed(words['packing']), 'Complete forward join')
    need(packet['actual_code']['words']['adjoint'] ==
         placed(words['inverse'])+source['precode_words']['precode_adjoint'], 'Complete adjoint join')
    need(source['precode_words']['precode_adjoint'] == inverse_word(source['precode_words']['precode']) and
         packet['actual_code']['words']['adjoint'] == inverse_word(packet['actual_code']['words']['code']),
         'The complete adjoint word is the literal inverse word')
    for name, expected in [('code', c), ('adjoint', cstar)]:
        reports[name], _ = check_word(packet['actual_code']['words'][name],
                                     expected+q.unit(1280)[224:], 224, 5702)
        need((reports[name]['binary_height'], reports[name]['odd_height']) == (2, 1),
             'The complete local coefficient guard')
    need(reports['code']['prefix_real_row_one_norm'] == '17' and
         reports['adjoint']['prefix_real_row_one_norm'] == '28/3', 'Exact joined prefix norms')
    need(q.reverse(ordinary(packet['actual_code']['words']['code']+
                            packet['actual_code']['words']['adjoint']), 1280) == q.unit(1280) and
         q.reverse(ordinary(packet['actual_code']['words']['adjoint']+
                            packet['actual_code']['words']['code']), 1280) == q.unit(1280),
         'Both literal complete inverse orders')
    decoder = realify(source['decoder'], 112)
    readers = realify(source['original_readers'], 112)
    need(q.mul(decoder, c) == readers and q.mul(readers, cstar) == decoder, 'Actual full reader recovery')
    support = {j//2 for row in decoder for j in row}
    need(support == set(source['selected_ports']) and len(support) == 16, 'Sixteen actual output fields')
    need(q.rank(readers) == 32, 'The sixteen Gaussian reader rows are independent')
    response = realify(prior['response'], 112)
    coded = q.mul(c, response)
    need(coded == realify(source['coded_response'], 112), 'Actual coded response')
    rest = set(range(112))-support
    need(rest == set(source['ordinary_ports']) and len(rest) == 96, 'Actual ordinary coordinates')
    need(all(coded[2*p+b] == c[2*p+b] for p in rest for b in (0, 1)),
         'Every ordinary coded-response row equals the code row')
    need(all(source['code'][p].get(str(p), ['0', '0']) != ['0', '0'] for p in rest),
         'Every ordinary diagonal needs a changed native construction')
    trace = tuple(sum((F(row.get(str(i), ['0', '0'])[part])
                       for i, row in enumerate(source['code'])), F(0)) for part in (0, 1))
    need(trace == (F(11, 6), F(7, 6)), 'Trace of the complete actual C')
    mod_c, mod_star = residue(source['code'], F(3)), residue(source['code_adjoint'], F(3))
    need(ftrace(mod_c) == (1, 2) and ftrace(mod_star) == (1, 1), 'Nonzero residue traces exclude nilpotence')
    need(heights(c)[1] == heights(cstar)[1] == 1, 'Exact first odd height')
    powers = {}
    for name, base in [('C', c), ('Cstar', cstar)]:
        current, values = q.unit(224), []
        for m in range(1, 5):
            current = q.mul(base, current)
            need(heights(current)[1] == m, 'Finite control for the all-power theorem')
            values.append(m)
        powers[name] = values
    r2 = q.mul(r, r)
    need(q.mul(r2, r2) == q.unit(8) and r2 != q.unit(8), 'Packing has order exactly four')
    sign = q.unit(8)
    sign[0], sign[1] = {0: F(-1)}, {1: F(-1)}
    signed = q.mul(numerator, sign)
    signed_trace = (sum((signed[2*j].get(2*j, F(0)) for j in range(4)), F(0)),
                    sum((signed[2*j+1].get(2*j, F(0)) for j in range(4)), F(0)))
    need(signed_trace == (F(-2), F(2)) and tuple(map(mod3, signed_trace)) != ZERO,
         'Signed dyadic interleaving also has a nonnilpotent residue')
    damaged = list(words['packing'][1:])
    need(q.reverse(ordinary(damaged), 1280) != q.transpose(rr, 1280), 'Missing paid component control')
    result = {
        'status': 'PASS_INDEPENDENT_RATIONAL_PACKING_GRID',
        'words': reports, 'packing_divisibility_domain': domains,
        'signed_scans': scan_checks(), 'actual_trace': list(map(str, trace)),
        'residue_trace_C': ftrace(mod_c), 'residue_trace_Cstar': ftrace(mod_star),
        'actual_residue_rank_C': frank(mod_c), 'actual_residue_rank_Cstar': frank(mod_star),
        'power_controls': powers,
        'all_positive_power_proof': '3C and 3C* have nonzero trace over F9. Neither residue is nilpotent. Every positive power is nonzero modulo 3, so the exact odd height is m.',
        'packing_order': 4, 'signed_interleaving_trace': list(map(str, signed_trace)),
        'full_reader_output_coordinates': 16, 'new_fields': 0, 'native_children': 0,
        'actual_reader_real_rank': 32, 'ordinary_rows_CE_equal_C': 96,
        'nonzero_ordinary_diagonal_entries': 96,
        'matched_C_then_Cstar_pair_prefix_odd_height': 1,
        'matched_pair_proof': 'The second complete word is the literal reverse inverse. Its prefix states retrace the first word.',
        'scope': 'Paid scalar words at one common complex frame, exact divisibility domains, fixed-odd scans and conditional root-grid admission. No native response, mixed-hole access, unmatched recursive child or complete supplier is admitted.',
    }
    args.out.mkdir(parents=True, exist_ok=False)
    for name, obj in [('REVIEW.json', result), ('INPUTS.json', q.INPUTS)]:
        (args.out/name).write_text(json.dumps(obj, sort_keys=True, indent=2)+'\n')
    print(result['status'], flush=True)


if __name__ == '__main__':
    main()
