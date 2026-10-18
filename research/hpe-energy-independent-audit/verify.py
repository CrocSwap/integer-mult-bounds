"""Independent direct realification audit of PR1906. Apache-2.0.

Prepared for Ross with OpenAI Codex assistance. No predecessor code is imported.
Matrices are sparse integer matrices on interleaved real/imaginary coordinates.
We do not use adjoints, packed vectors, or the predecessor's literal parser.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXACT = 'research/hyperplane-end-lean/HyperplaneEnd/Exact.lean'
CLIFFORD = 'research/hyperplane-end-lean/HyperplaneEnd/Clifford.lean'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique(pairs):
    out = {}
    for key, value in pairs:
        require(key not in out, 'duplicate JSON key: ' + key)
        out[key] = value
    return out


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def literals(source):
    """Parse only six closed List Gate definitions, consuming every token.

    No eval, AST conversion, imported parser, or Lean expression evaluation.
    The scientific input is separately authenticated before this is called.
    """
    found = {}
    pattern = r'^def ((?:lhs|rhs)Lit[123]) : List Gate :=\s*(.*?)\n\n'
    for match in re.finditer(pattern, source, re.M | re.S):
        name, body = match.groups()
        require(name not in found, 'duplicate literal definition')
        tokens = re.findall(r'\s+|\.(?:pm|dg|cg|xg|ph)\b|true\b|false\b|[0-9]+|[\[\],]|\S', body)
        tokens = [token for token in tokens if not token.isspace()]
        index = 0

        def take(expected=None):
            nonlocal index
            require(index < len(tokens), 'truncated literal')
            token = tokens[index]
            index += 1
            require(expected is None or token == expected, 'unexpected literal token')
            return token

        def peek():
            require(index < len(tokens), 'truncated literal')
            return tokens[index]

        def natural():
            token = take()
            require(re.fullmatch(r'[0-9]+', token) is not None, 'natural literal required')
            return int(token)

        def array():
            take('[')
            result = []
            if peek() != ']':
                result.append(natural())
                while peek() == ',':
                    take(',')
                    result.append(natural())
            take(']')
            return result

        gates = []
        take('[')
        while peek() != ']':
            tag = take()
            if tag in ('.pm', '.dg'):
                gate = [tag[1:], array(), array()]
            elif tag == '.cg':
                mask, sign = natural(), take()
                require(sign in ('true', 'false'), 'Boolean C sign required')
                gate = ['cg', mask, sign == 'true']
            else:
                require(tag in ('.xg', '.ph'), 'unknown gate literal')
                gate = [tag[1:], natural()]
            gates.append(gate)
            if peek() != ',':
                break
            take(',')
        take(']')
        require(index == len(tokens), 'unconsumed literal expression')
        found[name] = gates
    require(set(found) == {side + str(i) for side in ('lhsLit', 'rhsLit') for i in (1, 2, 3)},
            'six literal definitions required')
    return found


def binary_image(rows, address):
    # Explicit coordinate dot products, rather than bit_count/table parity.
    result = 0
    for index, row in enumerate(rows):
        bit = 0
        for column in range(len(rows)):
            bit ^= ((row >> column) & 1) * ((address >> column) & 1)
        result += bit << index
    return result


def phase_exponent(q, alpha, address):
    n = len(alpha)
    bits = [(address >> j) & 1 for j in range(n)]
    return (sum(alpha[j]*bits[j] for j in range(n)) +
            2*sum(((q[j] >> k) & 1)*bits[j]*bits[k]
                  for j in range(n) for k in range(j+1, n))) % 4


def validate(gates, n):
    require(type(n) is int and n >= 1, 'positive qubit count')
    size = 1 << n
    for g in gates:
        require(type(g) is list and g, 'gate shape')
        tag = g[0]
        if tag in ('pm', 'dg'):
            require(len(g) == 3 and all(type(v) is list and len(v) == n for v in g[1:]),
                    'matrix/diagonal shape')
            require(all(type(x) is int and x >= 0 for v in g[1:] for x in v),
                    'matrix/diagonal natural entries')
            if tag == 'pm':
                require(all(x < size for v in g[1:] for x in v), 'binary matrix domain')
                forward = [binary_image(g[1], x) for x in range(size)]
                backward = [binary_image(g[2], x) for x in range(size)]
                require(all(forward[backward[x]] == backward[forward[x]] == x
                            for x in range(size)), 'permutation inverse')
        elif tag in ('cg', 'xg'):
            require(len(g) == (3 if tag == 'cg' else 2) and
                    type(g[1]) is int and 0 <= g[1] < size, 'XOR domain')
            if tag == 'cg':
                require(type(g[2]) is bool, 'Boolean C sign')
        else:
            require(tag == 'ph' and len(g) == 2 and type(g[1]) is int and g[1] >= 0,
                    'phase or unknown gate')


def combine(*terms):
    out = {}
    for coefficient, row in terms:
        for column, value in row.items():
            out[column] = out.get(column, 0) + coefficient*value
    return {column: value for column, value in out.items() if value}


def rotate_rows(real, imag, phase):
    # Repeated exact multiplication by the integer matrix [[0,-1],[1,0]].
    for _ in range(phase % 4):
        real, imag = {j: -x for j, x in imag.items()}, real
    return real, imag


def matrix(gates, n=9):
    """Return the full realification of 2^k U and its omitted-half count k."""
    validate(gates, n)
    size = 1 << n
    rows = [{j: 1} for j in range(2*size)]
    count = 0
    for gate in gates:
        tag = gate[0]
        next_rows = []
        if tag == 'pm':
            for x in range(size):
                y = binary_image(gate[2], x)
                next_rows.extend((rows[2*y], rows[2*y+1]))
        elif tag in ('dg', 'ph'):
            for x in range(size):
                phase = phase_exponent(gate[1], gate[2], x) if tag == 'dg' else gate[1]
                next_rows.extend(rotate_rows(rows[2*x], rows[2*x+1], phase))
        elif tag == 'xg':
            for x in range(size):
                y = x ^ gate[1]
                next_rows.extend((rows[2*y], rows[2*y+1]))
        else:
            sign = 1 if gate[2] else -1
            for x in range(size):
                y = x ^ gate[1]
                real, imag, r_other, i_other = rows[2*x], rows[2*x+1], rows[2*y], rows[2*y+1]
                next_rows.append(combine((1, real), (-sign, imag), (1, r_other), (sign, i_other)))
                next_rows.append(combine((1, imag), (sign, real), (1, i_other), (-sign, r_other)))
            count += 1
        rows = next_rows
    return rows, count


def normalized_equal(left, right):
    a, ka = left
    b, kb = right
    if len(a) != len(b):
        return False
    for r, s in zip(a, b):
        if any((r.get(j, 0) << kb) != (s.get(j, 0) << ka) for j in r.keys() | s.keys()):
            return False
    return True


def gaussian_rows(rows, shift):
    size = len(rows)//2
    for x in range(size):
        real, imag = rows[2*x], rows[2*x+1]
        row = []
        for j in range(size):
            a, b = real.get(2*j, 0), imag.get(2*j, 0)
            require(real.get(2*j+1, 0) == -b and imag.get(2*j+1, 0) == a,
                    'complete complex-linear realification')
            row.append([a << shift, b << shift])
        yield row


def row_record(result, common):
    rows, count = result
    require(common >= count, 'common normalization')
    digest = hashlib.sha256()
    energies = set()
    for row in gaussian_rows(rows, common-count):
        energies.add(sum(a*a+b*b for a, b in row))
        digest.update((canonical(row)+'\n').encode())
    require(energies == {4**common}, 'scaled row energy')
    column_energies = [0]*len(rows)
    for row in rows:
        for j, x in row.items():
            column_energies[j] += x*x
    require(set(column_energies) == {4**count}, 'scaled column energy')
    return {'scaled_row_sha256': digest.hexdigest(), 'row_squared_energy': 4**common,
            'real_rows': len(rows), 'real_columns': len(rows),
            'nonzero_real_entries': sum(map(len, rows)), 'C_count': count}


def must_reject(operation, message):
    try:
        operation()
    except ValueError as error:
        require(message in str(error), 'wrong rejection reason: ' + str(error))
    else:
        raise ValueError('unexpected acceptance: ' + message)


def fixed_sources(root=ROOT):
    pins = read_json(HERE/'SOURCES.json')
    for row in pins['files']:
        if row['usage'] == 'input':
            require(hashlib.sha256((root/row['path']).read_bytes()).hexdigest() == row['sha256'],
                    'source drift: ' + row['path'])
    external = pins['external_result']
    require(hashlib.sha256((HERE/external['local_path']).read_bytes()).hexdigest() == external['sha256'],
            'predecessor receipt drift')
    return literals((root/EXACT).read_text(encoding='utf-8')), read_json(HERE/external['local_path'])


def bind_record(records, left_count, right_count, common, expected):
    """Compare the scientific receipt fields after computing the full matrices."""
    for record in records:
        require(record['scaled_row_sha256'] == expected['scaled_row_sha256'], 'predecessor row digest')
        require(record['row_squared_energy'] == expected['row_squared_energy'], 'predecessor energy')
    require([left_count, right_count] == [expected['C_left'], expected['C_right']], 'predecessor C counts')
    require(expected['radix_bits'] == common+1 and expected['radius'] == 1 << common,
            'predecessor radix binding')
    require(expected['largest_input_bits'] == 511*(common+1)+1, 'packed input length')


def run(root=ROOT):
    circuits, predecessor = fixed_sources(root)
    pairs = []
    for i in (1, 2, 3):
        lhs, rhs = circuits['lhsLit'+str(i)], circuits['rhsLit'+str(i)]
        left, right = matrix(lhs), matrix(rhs)
        require(normalized_equal(left, right), 'normalized matrix equality')
        common = max(left[1], right[1])
        records = [row_record(result, common) for result in (left, right)]
        expected = predecessor['source']['pairs'][i-1]
        bind_record(records, left[1], right[1], common, expected)
        # Operator controls are semantic: no source hash stands in for rejection.
        phase = matrix(rhs + [['ph', 1]])
        require(not normalized_equal(left, phase), 'phase defect accepted')
        character = matrix([['dg', [0]*9, [2]+[0]*8]] + rhs)
        require(not normalized_equal(left, character), 'input-character defect accepted')
        require(not normalized_equal((left[0], 0), (right[0], 0)), 'omitted scale accepted')
        # Harmless C C^-1 insertion changes the raw scale, but not the operator.
        gauge = matrix(rhs + [['cg', 1, True], ['cg', 1, False]])
        require(normalized_equal(left, gauge), 'equivalent normalized presentation')
        pairs.append({'pair': i, 'common_C': common, 'radix_bits': common+1,
                      'sides': records,
                      'controls': ['global_phase', 'input_character', 'omitted_normalization'],
                      'positive_control': 'C_inverse_pair_with_changed_raw_scale'})
    return {'status': 'PASS_INDEPENDENT_HPE_ENERGY_AUDIT',
            'predecessor_head': '788848032c16bbe0a543c1186c6691c66131c090',
            'pairs': pairs, 'complex_rows_checked': 3072,
            'real_matrix_entries_covered': 6*1024*1024,
            'new_lean_proof': False, 'new_kappa': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', type=Path, help='Explicit receipt generation; default is read-only')
    args = parser.parse_args()
    if not args.write:
        expected = read_json(HERE/'RESULT.json')  # Missing evidence fails before computation.
    result = run()
    if args.write:
        args.write.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8', newline='\n')
    else:
        require(canonical(result) == canonical(expected), 'audit receipt mismatch')
    print(result['status'], 'complex_rows=3072 real_entries=6291456 no_new_kappa')


if __name__ == '__main__':
    main()
