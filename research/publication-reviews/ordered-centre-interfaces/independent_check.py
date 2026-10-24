"""Check ordered identities, line flags, and the data-only invoice."""

from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
from pathlib import Path
import argparse
import gzip
import json


def need(value, message):
    if not value:
        raise ValueError(message)


def mm(a, b):
    return [[sum(x * y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def eye(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def inverse(a):
    n = len(a)
    rows = [[F(x) for x in row] + unit for row, unit in zip(a, eye(n))]
    for i in range(n):
        j = next(j for j in range(i, n) if rows[j][i])
        rows[i], rows[j] = rows[j], rows[i]
        scale = rows[i][i]
        rows[i] = [x / scale for x in rows[i]]
        for j in range(n):
            if j != i:
                scale = rows[j][i]
                rows[j] = [x - scale * y for x, y in zip(rows[j], rows[i])]
    return [r[n:] for r in rows]


def block(a, b, c, d):
    return [x + y for x, y in zip(a, b)] + [x + y for x, y in zip(c, d)]


def chronological(operations):
    result = eye(len(operations[0]))
    for operation in operations:
        result = mm(operation, result)
    return result


def binary_rank(a):
    rows = list(a)
    pivots = {}
    for x in rows:
        while x:
            bit = x.bit_length() - 1
            if bit in pivots:
                x ^= pivots[bit]
            else:
                pivots[bit] = x
                break
    return len(pivots)


def bm(a, b):
    result = []
    for row in a:
        value = 0
        for j, source in enumerate(b):
            if row >> j & 1:
                value ^= source
        result.append(value)
    return result


def bt(a):
    return [sum(((row >> i) & 1) << j for j, row in enumerate(a)) for i in range(len(a))]


def bi(a):
    n = len(a)
    rows = [row | (1 << (i + n)) for i, row in enumerate(a)]
    for i in range(n):
        j = next(j for j in range(i, n) if rows[j] >> i & 1)
        rows[i], rows[j] = rows[j], rows[i]
        for j in range(n):
            if j != i and rows[j] >> i & 1:
                rows[j] ^= rows[i]
    need([x & ((1 << n) - 1) for x in rows] == [1 << i for i in range(n)], "Binary inverse")
    return [x >> n for x in rows]


def bb(a, b, c, d):
    n = len(a)
    return [x | (y << n) for x, y in zip(a, b)] + [x | (y << n) for x, y in zip(c, d)]


def line_hadamard(a, n):
    pa = [a if (a >> i) & 1 else 0 for i in range(n)]
    complement = [row ^ (1 << i) for i, row in enumerate(pa)]
    return bb(complement, pa, pa, complement)


def matvec(a, x):
    return sum(((row & x).bit_count() % 2) << i for i, row in enumerate(a))


def check(args):
    i = eye(2)
    z = [[F(0)] * 2 for _ in range(2)]
    neg = [[-x for x in row] for row in i]
    e0 = [[F(1), F(1)], [F(0), F(1)]]
    g1 = [[F(1), F(0)], [F(1), F(1)]]
    e2 = [[F(2), F(1)], [F(1), F(1)]]
    q = [[F(1), F(2)], [F(1), F(3)]]
    gi, qi = inverse(g1), inverse(q)
    need(mm(e0, g1) != mm(g1, e0), "Noncommuting test source")
    operations = [block(i, z, e0, i), block(e0, z, z, i), block(i, z, z, gi),
                  block(i, [[-x for x in r] for r in g1], z, i),
                  block(gi, z, z, i), block(i, z, z, e2), block(i, z, e2, i),
                  block(g1, z, z, i)]
    t = mm(e2, mm(gi, e0))
    endpoint = block(z, neg, t, z)
    need(chronological(operations) == endpoint, "General-unit ordered endpoint")
    for omitted in (1, 2, 4, 5, 7):
        need(chronological(operations[:omitted] + operations[omitted + 1:]) != endpoint,
             "Omitted code must change the endpoint")
    exchange = block(z, mm(q, q), neg, z)
    physical = mm(exchange, mm(block(i, z, z, qi), mm(endpoint, block(qi, z, z, i))))
    residual = mm(q, mm(t, qi))
    need(physical == block(residual, z, z, i), "Physical Q conjugation")
    decoder = chronological([qi, inverse(e2), g1, inverse(e0), q])
    need(mm(decoder, residual) == i, "Chronological terminal inverse")
    wrong = chronological([qi, inverse(e0), g1, inverse(e2), q])
    need(mm(wrong, residual) != i, "Wrong terminal order must fail")

    h = [[[F(0), F(1)], [F(1), F(0)]], [[F(1), F(0)], [F(0), F(-1)]],
         [[F(0), F(-1)], [F(1), F(0)]]]
    c, physical_word = i, i
    bad_c, bad_word = i, i
    for gate, error in zip((e0, g1, e2), h):
        replacement = mm(error, gate)
        physical_word = mm(mm(c, mm(replacement, inverse(c))), physical_word)
        c = mm(c, error)
        bad_word = mm(mm(bad_c, mm(replacement, inverse(bad_c))), bad_word)
        bad_c = mm(error, bad_c)
    old_word = chronological([e0, g1, e2])
    need(mm(inverse(c), physical_word) == old_word, "Complete-state code order")
    need(mm(inverse(bad_c), bad_word) != old_word, "Reversed code order must fail")

    n = 3
    units, zero = [1 << j for j in range(n)], [0] * n
    full = bb(zero, units, units, zero)
    odd = [a for a in range(1, 1 << n) if a.bit_count() % 2]
    gl_count = cases = orthogonal = zero_cases = 0
    for g in product(range(1, 1 << n), repeat=n):
        if binary_rank(g) != n:
            continue
        gl_count += 1
        address = bb(g, zero, zero, bt(bi(g)))
        for a, b in product(odd, repeat=2):
            composed = bm(full, bm(line_hadamard(b, n), bm(address, line_hadamard(a, n))))
            first_rank = binary_rank([row >> n for row in composed[:n]])
            terminal = bm(composed, full)
            terminal_rank = binary_rank([row >> n for row in terminal[:n]])
            flag = ((b & matvec(g, a)).bit_count() % 2) == 0
            zero_flag = matvec(bt(g), b) == a
            need((terminal_rank == 0) == zero_flag, "Exact zero-rank flag")
            if flag:
                need((first_rank, terminal_rank) == (n - 2, 2), "Orthogonal line ranks")
                orthogonal += 1
            zero_cases += zero_flag
            cases += 1
    need((gl_count, cases, orthogonal) == (168, 2688, 1152), "Complete three-bit family")

    path = args.package / 'frozen/work/centre-encoding-campaign-20261014/lanes/oblique-native-20261017/matched-native-involution/MATCHED-NATIVE-PROGRAM.json.gz'
    raw = path.read_bytes()
    data = json.loads(gzip.decompress(raw))
    response = [{int(k): F(v) for k, v in row.items()} for row in data['response']]
    inventory = []
    for provider, programs in data['providers'].items():
        for direction, word in programs.items():
            profile, progress = Counter(), Counter()
            rows = [{j: F(1)} for j in range(224)]
            for event in word['events']:
                if event[0] == 'native':
                    _, target, before, after, rank, recipe = event
                    need(0 <= target < 224 and rank > 0, "Native data role")
                    profile[rank] += 1
                    progress[target] += rank
                else:
                    need(event[0] == 'scalar', "Only scalar or native events")
                    gate = event[1]
                    target = gate[1]
                    need(0 <= target < 224, "Scalar data target")
                    if gate[0] == 'scale':
                        rows[target] = {j: F(gate[2], gate[3]) * v for j, v in rows[target].items()}
                    else:
                        need(gate[0] == 'add' and 0 <= gate[2] < 224, "Scalar data source")
                        for j, v in list(rows[gate[2]].items()):
                            value = rows[target].get(j, F(0)) + F(gate[3], gate[4]) * v
                            if value:
                                rows[target][j] = value
                            else:
                                rows[target].pop(j, None)
            need(word['start'][224:] == word['final'][224:], "Unused helper frames")
            need(set(progress) == set(range(224)) and set(progress.values()) == {8}, "Every field has rank mass eight")
            need(dict(profile) == {1:160, 2:48, 5:48, 7:112, 8:64}, "Local profile")
            expected = [{j: F(1)} for j in range(224)]
            for port, row in enumerate(response):
                target = 112 + port if direction == 'forward' else port
                offset = 0 if direction == 'forward' else 112
                sign = 1 if direction == 'forward' else -1
                expected[target].update({offset + j: sign * value for j, value in row.items()})
            need(rows == expected, "Full scalar endpoint on 224 columns")
            inventory.append({'provider': provider, 'direction': direction, 'children': sum(profile.values()),
                              'rank_mass': sum(r * v for r, v in profile.items()), 'data_columns': 224})
    base = Counter({1:480, 2:144, 5:144, 7:336, 8:192})
    complete = []
    for name, terminal in [('separated', Counter({1:224})), ('mixed', Counter({1:96, 2:64}))]:
        profile = base + terminal
        mass = sum(r * count for r, count in profile.items())
        need(mass == 224 * 25 and all(0 < r < 25 for r in profile), "Strict moment premises")
        complete.append({'terminal': name, 'terminal_rank_mass': sum(r * count for r, count in terminal.items()),
                         'complete_profile': dict(profile), 'complete_rank_mass': mass})
    need(3 * 3032 + 8 * 2396 == 28264, "Separated scalar subtotal")
    need(3 * 3032 + 5 * 2396 + 3 * 1564 + 128 == 25896, "Mixed scalar subtotal")
    result = {'status':'PASS_INDEPENDENT_ORDERED_INTERFACE_CHECK', 'imports_package_code': False,
              'ordered_unit_endpoint': True, 'complete_state_compiler_order': True,
              'negative_controls': 7, 'symplectic_composition_cases': cases,
              'invertible_three_bit_maps': gl_count, 'orthogonal_line_cases': orthogonal,
              'zero_rank_flag_cases': zero_cases, 'native_payload_sha256': sha256(raw).hexdigest(),
              'native_payload_decompressed_sha256': sha256(gzip.decompress(raw)).hexdigest(),
              'native_data_checks': inventory, 'complete_profiles': complete,
              'moment_argument': 'For b>0 and each 0<r<25, r^(1-b)>r*25^(-b). The verified total mass 5600 gives strict failure for both specified completions.',
              'scope': 'Exact rational counterchecks and finite binary identities support the separately read algebraic proof. Source native phases and all-size contracts remain inherited.'}
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(result['status'])


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    check(parser.parse_args())
