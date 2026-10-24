"""Check the A8 rational normalization and its exact record arithmetic."""

import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
INTERFACE = LANES / 'new-core-transfer-20261017/INTERFACE.json'
INTERFACE_PIN = 'c6ca09711622ce4ad236f78cc28c03b6c46808a9d91cfc1722ff4fe371f38746'
A = [0, 7, 20, 27, 36, 46, 57, 111]
U = [p for p in range(112) if p not in A]
C = 112


def need(ok, label):
    if not ok:
        raise ValueError(label)


def add(dst, src, coefficient=F(1)):
    for j, value in src.items():
        value = dst.get(j, F(0)) + coefficient * value
        if value:
            dst[j] = value
        else:
            dst.pop(j, None)


def product(a, b):
    out = []
    for row in a:
        result = {}
        for j, value in row.items():
            add(result, b[j], value)
        out.append(result)
    return out


def odd_height(value):
    denominator = value.denominator
    two, three = 0, 0
    while denominator % 2 == 0:
        denominator //= 2
        two += 1
    while denominator % 3 == 0:
        denominator //= 3
        three += 1
    need(denominator == 1, 'Only binary and ternary denominators')
    return two, three


def old_price(event):
    if event[0] == 'clear':
        return 2
    if event[0] == 'divide_odd':
        return 0
    value = F(event[-1])
    n, d = abs(value.numerator), value.denominator
    need(n > 0 and not d & (d - 1), 'Old primitive has a dyadic coefficient')
    if event[0] == 'scale':
        need(not n & (n - 1), 'Old SCALE is a signed binary unit')
        return 2 * (abs(n.bit_length() - d.bit_length()) + int(value < 0))
    need(event[0] == 'add', 'Old primitive grammar')
    return 2 * (1 + n.bit_length() + n.bit_count() + d.bit_length())


def word(r, inverse=False, fused=False):
    need(not fused or inverse, 'Only the inverse has a fused upper shear')
    out = []
    for row in r:
        out.append(['clear', C])
        for p in U:
            if p in row:
                out.append(['add', C, p, str(row[p])])
        out.append(['scale', C, '1/16' if inverse else '1/4'])
        if inverse:
            out.append(['divide_odd', C, 3])
        for p in (range(112) if fused else U):
            if p in row:
                out.append(['add', p, C, str(-row[p])])
        out.append(['clear', C])
    return out


def replay(events):
    rows = [{p: F(1)} for p in range(113)]
    maximum_norm, binary, ternary = F(1), 0, 0
    peak = None
    query_heights = []
    grid_checks = 0
    for index, event in enumerate(events):
        kind, target = event[:2]
        if kind == 'clear':
            need(target == C, 'Only allocated C0 is cleared')
            rows[target] = {}
        elif kind == 'add':
            need(target != event[2], 'Distinct ADD fields')
            add(rows[target], rows[event[2]], F(event[3]))
        else:
            if kind == 'divide_odd':
                need(target == C and event[2] == 3, 'Only C0 has odd division')
                query_heights.append(max((odd_height(value)[1] for value in rows[target].values()), default=0))
                coefficient = F(1, 3)
            else:
                need(kind == 'scale' and target == C, 'Only C0 is scaled')
                coefficient = F(event[2])
            rows[target] = {j: coefficient * value for j, value in rows[target].items()}
        for value in rows[target].values():
            two, three = odd_height(value)
            binary, ternary = max(binary, two), max(ternary, three)
            need((48 * value).denominator == 1, 'Every prefix is integral on the common 1/48 grid')
            grid_checks += 1
        norm = sum(map(abs, rows[target].values()), F(0))
        if norm > maximum_norm:
            maximum_norm, peak = norm, index
    need(not rows[C], 'C0 is zero at exit')
    need(all(C not in row for row in rows), 'Arbitrary initial C0 has no output effect')
    return rows, {'max_coefficient_row_l1': str(maximum_norm), 'first_peak_event': peak,
                  'binary_height': binary, 'odd3_height': ternary,
                  'pre_odd_division_heights': query_heights, 'integral_prefix_coefficient_checks': grid_checks,
                  'old_real_primitives': sum(map(old_price, events)),
                  'real_division_by_3_scans': 2 * sum(e[0] == 'divide_odd' for e in events),
                  'event_counts': dict(Counter(e[0] for e in events)), 'literal_events': len(events)}


def divide3(n, width):
    unsigned = n % (1 << width)
    carry, output = 0, 0
    for i in range(width):
        bit = (unsigned >> i) & 1
        quotient_bit = (bit - carry) % 2
        carry = (carry + 3 * quotient_bit - bit) // 2
        need(0 <= carry < 3, 'Division carry range')
        output |= quotient_bit << i
    source_sign = (unsigned >> (width - 1)) & 1
    result_sign = (output >> (width - 1)) & 1
    valid = carry == 3 * result_sign - source_sign
    return valid, output - (1 << width) * result_sign


def multiply3(n, width):
    unsigned = n % (1 << width)
    carry, output = 0, 0
    for i in range(width):
        bit = (unsigned >> i) & 1
        total = 3 * bit + carry
        output |= (total % 2) << i
        carry = total // 2
        need(0 <= carry < 3, 'Multiplication carry range')
    source_sign = (unsigned >> (width - 1)) & 1
    result_sign = (output >> (width - 1)) & 1
    valid = carry == 3 * source_sign - result_sign
    return valid, output - (1 << width) * result_sign


def record_checks():
    for c in range(3):
        for b in (0, 1):
            a = (b - c) % 2
            next_c = (c + 3 * a - b) // 2
            need(0 <= next_c < 3 and 2 * next_c == c + 3 * a - b, 'All division transitions')
    cases, rejected = 0, 0
    for width in range(1, 13):
        lo, hi = -(1 << (width - 1)), 1 << (width - 1)
        for n in range(lo, hi):
            valid, q = divide3(n, width)
            need(valid == (n % 3 == 0), 'Signed divisibility test')
            need(not valid or q * 3 == n, 'Exact signed quotient')
            rejected += not valid
            valid, p = multiply3(n, width)
            need(valid == (lo <= 3 * n < hi), 'Exact multiplication overflow test')
            need(not valid or p == 3 * n, 'Exact signed product')
            cases += 1
    need(not divide3(1, 8)[0], 'Unscaled borrowed numerator control')
    need(F(1, 3**3).denominator > 3**2, 'Completed rational children need a stronger height bound')
    return {'division_transition_cases': 6, 'signed_inputs': cases, 'nonmultiple_rejections': rejected,
            'arithmetic_head_steps_per_real_scan': 'at most 4*(w_g+1)',
            'descriptor_counter_steps': 'additional retained O(w_g+1) work per record'}


def main(out):
    need(sha256(INTERFACE.read_bytes()).hexdigest() == INTERFACE_PIN, 'Actual new interface pin')
    data = json.loads(INTERFACE.read_text())
    r = [{int(p): F(value) for p, value in row.items()} for row in data['R']]
    ru = [{p: value for p, value in row.items() if p in U} for row in r]
    need(all(len(row) == 52 and set(map(abs, row.values())) == {F(1)} for row in ru), 'Actual RU support and values')
    need(all(len(row) == 56 for row in r), 'Actual full R support')
    need(all(sum(ru[i].get(p, 0) * ru[j].get(p, 0) for p in U) == (52 if i == j else 0) for i in range(8) for j in range(8)), 'RU orthogonality')
    eye = [{p: F(1)} for p in range(112)]
    gram = [{q: sum(ru[i].get(p, 0) * ru[i].get(q, 0) for i in range(8)) for q in U} if p in U else {} for p in range(112)]
    gram = [{q: value for q, value in row.items() if value} for row in gram]
    h, hi, fused = deepcopy(eye), deepcopy(eye), deepcopy(eye)
    for p in range(112):
        add(h[p], gram[p], F(-1, 4))
        add(hi[p], gram[p], F(-1, 48))
        add(fused[p], {q: sum(r[i].get(p, 0) * ru[i].get(q, 0) for i in range(8)) for q in U}, F(-1, 48))
    need(product(h, hi) == product(hi, h) == eye, 'Both H inverse orders')
    upper = deepcopy(eye)
    for p in A:
        add(upper[p], {q: sum(r[i].get(p, 0) * ru[i].get(q, 0) for i in range(8)) for q in U}, F(1, 4))
    need(product(upper, hi) == fused, 'Fused postupper order')
    ek = [{i: F(-1 if p in A else 1, 4) * r[i].get(p, 0) for i in range(8)
           if r[i].get(p, 0)} for p in range(112)]
    need(product(r, ek) == [{i: F(12)} for i in range(8)], 'Actual R E K equals 12 I8')
    content = [{p: F(-1 if p in A else 1)} for p in range(112)]
    for p in range(112):
        add(content[p], {q: sum(r[i].get(p, 0) * r[i].get(q, 0) for i in range(8))
                         for q in range(112)}, F(-1, 48))
    need(product(content, ek) == [{} for _ in range(112)], 'The fused X-content map has eight kernel channels')
    reports, words = {}, {}
    for name, inverse, is_fused, target, price in [('H', False, False, h, 6720), ('H_inverse', True, False, hi, 6752), ('H_inverse_fused_upper', True, True, fused, 7008)]:
        events = word(r, inverse, is_fused)
        actual, receipt = replay(events)
        need(actual == target + [{}], 'Complete 113-column scalar factor: ' + name)
        need(receipt['old_real_primitives'] == price and receipt['real_division_by_3_scans'] == (16 if inverse else 0), 'Full factor invoice')
        need(receipt['binary_height'] == (4 if inverse else 2) and receipt['odd3_height'] == int(inverse), 'Every-prefix denominator bound')
        need(receipt['pre_odd_division_heights'] == ([0] * 8 if inverse else []), 'Every complete query clears prior odd denominators')
        reports[name], words[name] = receipt, events
    wrong = [e for e in words['H_inverse_fused_upper'] if e[0] != 'divide_odd']
    need(replay(wrong)[0] != fused + [{}], 'Omitted odd division control')
    alpha = F(85, 256)
    approximate = deepcopy(words['H_inverse'])
    for index, event in enumerate(approximate):
        if event[0] == 'divide_odd':
            approximate[index] = ['scale', C, str(alpha)]
    rows = [{p: F(1)} for p in range(113)]
    for e in approximate:
        if e[0] == 'clear': rows[e[1]] = {}
        elif e[0] == 'add': add(rows[e[1]], rows[e[2]], F(e[3]))
        else: rows[e[1]] = {j: F(e[2]) * v for j, v in rows[e[1]].items()}
    need(product(rows[:112], h) != eye, 'Dyadic approximation does not restore arbitrary borrowed inputs exactly')
    report = {'status': 'PASS_A8_EXACT_ODD_GRID_NORMALIZATION', 'interface_sha256': INTERFACE_PIN,
              'selected': A, 'ordinary_fields': len(U), 'RU_gram': '52 I8',
              'fused_X_content': {'matrix': 'E - K R/12', 'R_E_K': '12 I8',
                                  'kernel': 'image(E K)', 'nullity': 8,
                                  'limit': 'Only the borrowed-Y block is made invertible; selected Y retains the missing X content'},
              'local_factors': reports, 'record_arithmetic': record_checks(),
              'balanced_predicted_local_bills': {'forward': {'old_real_primitives': 164514 + 6720 + 416 + 14, 'odd_scans': 0, 'native_mass': 5073},
                                                'fused_backward': {'old_real_primitives': 164514 + 7008 + 208 + 14, 'odd_scans': 16, 'native_mass': 5073}},
              'grid_theorem': {'local_odd_height_per_inverse': 1, 'fixed_parent_inverse_count': 'M',
                               'root_grid_scale': '3^(M*(D+1))', 'depth_bound_73_48': 'D <= 2*ceil(log2(d+1))',
                               'extra_numerator_bits': 'at most 2*M*(D+1)',
                               'both_root_conversion_arithmetic_head_steps': 'at most 8*N*M*(D+1)*(w_g+1)',
                               'local_scan_arithmetic_head_steps_per_inverse': 'at most 64*n*(w_g+1), for n complex entries per field',
                               'required_completed_child_contract': 'exact Gaussian-dyadic on every data and arbitrary helper column',
                               'required_outer_contract': 'Gaussian-dyadic endpoint for final unscaling; separate semantic restoration proof'},
              'not_claimed': ['complete raw A8 event transfer', 'complete controller or native phase admission', 'owner and private hosting', 'new selected kappa']}
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    (out.parent / 'A8-ODD-GRID-WORDS.json').write_text(json.dumps(words, sort_keys=True, separators=(',', ':')) + '\n')
    print(report['status'], flush=True)
    print(json.dumps(reports, indent=2), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    main(parser.parse_args().out)
