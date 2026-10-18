#!/usr/bin/env python3
"""Independent exact audit of discussion 1636's inherited-cover obstruction.

The five-call candidate itself is provisional Discussion text, not a source
package. This checker proves a conditional obstruction for its stated route.
Apache-2.0. Josie Elliston, with substantial AI assistance (OpenAI Codex draft; Claude review and fixes).
"""
import ast
import hashlib
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
ROUTE = 'research/direct-delivery504-global/inputs/data-base/work/complex-nine-native/DATA-PHASES.json'
MANIFEST = 'research/community-frontier1094-audit/SELECTED-SOURCE.json'
PROOF = 'research/split-centres-global/proofs/INHERITED-COMPLEX-GEOMETRY.txt'
ROOT_PROOF = 'research/split-centres-global/proofs/PR425-COMPLEX.txt'
MASK9 = (1 << 9) - 1
PIN = 'DISCUSSION-1636-PIN.json'
# The word this checker was written against: (orientation, M coefficient, K coefficient).
FIVE_CALL = (('L', Q(1, 12), Q(0)), ('U', Q(-12, 13), Q(0)), ('L', Q(143, 144), Q(131, 144)),
             ('U', Q(-12, 13), Q(0)), ('L', Q(1, 12), Q(0)))


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads((ROOT/path).read_bytes())


def sources():
    for pin in read(HERE.relative_to(ROOT)/'SOURCES.json')['files']:
        if pin['usage'] == 'input':
            need(sha((ROOT/pin['path']).read_bytes()) == pin['sha256'], 'source drift: '+pin['path'])
    selected = read('certificates/selected-result.json')
    need(selected['source_manifest'] == MANIFEST, 'selected manifest changed')
    need(read(MANIFEST)['files'][ROUTE] == sha((ROOT/ROUTE).read_bytes()), 'port route not selected-pinned')
    proof = (ROOT/PROOF).read_text()
    need('rho_s,q exchanges that complement' in proof and 'g=d*rho_s,q' in proof,
         'historical route statement changed')
    roots_proof = (ROOT/ROOT_PROOF).read_text()
    need('112 sign lines on the 14 weight-four Hamming' in roots_proof,
         'historical sign-line statement changed')
    data = read(ROUTE)
    need(data['m'] == 73 and data['ports'] == 112 and len(data['recipes']) == 112,
         'route geometry changed')
    ports = [recipe['q'] for recipe in data['recipes']]
    validate_ports(ports)
    return ports


def linear_coefficients(text):
    """Parse a Discussion pulse argument such as (143M + 131K)/144 into (c, d)."""
    source = ''
    for i, ch in enumerate(text):
        if ch in 'MK' and i and (text[i-1].isdigit() or text[i-1] == ')'):
            source += '*'
        source += ch
    allowed = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Add, ast.Sub, ast.Mult, ast.Div,
               ast.USub, ast.Constant, ast.Name, ast.Load)
    tree = ast.parse(source, mode='eval')
    need(all(isinstance(node, allowed) for node in ast.walk(tree)), 'pinned word syntax')
    def value(node, m, k):
        if isinstance(node, ast.Expression):
            return value(node.body, m, k)
        if isinstance(node, ast.Constant):
            need(type(node.value) is int, 'pinned word constant')
            return Q(node.value)
        if isinstance(node, ast.Name):
            need(node.id in ('M', 'K'), 'pinned word symbol')
            return m if node.id == 'M' else k
        if isinstance(node, ast.UnaryOp):
            return -value(node.operand, m, k)
        a, b = value(node.left, m, k), value(node.right, m, k)
        return {ast.Add: a+b, ast.Sub: a-b, ast.Mult: a*b}.get(type(node.op)) if \
            not isinstance(node.op, ast.Div) else a/b
    c, d = value(tree, Q(1), Q(0)), value(tree, Q(0), Q(1))
    for m, k in ((Q(2), Q(3)), (Q(-5), Q(7))):
        need(value(tree, m, k) == c*m + d*k and value(tree, Q(0), Q(0)) == 0, 'pinned word not linear')
    return c, d


def pinned_word(pin=None):
    """Bind FIVE_CALL to the verbatim word pinned from discussion 1636."""
    if pin is None:
        pin = json.loads((HERE/PIN).read_bytes())
    need(pin['discussion'].endswith('/discussions/1636'), 'pin discussion')
    comments = {c['id']: c for c in pin['comments']}
    need(set(comments) == {18915216, 18915408}, 'pinned comment ids')
    text = comments[18915216]['excerpt']
    word = []
    for item in text.split('), '):
        item = item.strip()
        item = item if item.endswith(')') else item + ')'
        need(item[0] in 'LU' and item[1] == '(' and item[-1] == ')', 'pinned pulse form')
        word.append((item[0],) + linear_coefficients(item[2:-1]))
    need(tuple(word) == FIVE_CALL, 'pinned discussion word differs from checked word')
    route = comments[18915408]['excerpt']
    need('rho_(s,p) rho_(s,q)' in route and '[[1,0],[131/144,1]]' in route,
         'pinned route statement')
    return pin


def validate_ports(ports):
    need(len(ports) == len(set(ports)) == 112 and
         all(0 < q < 512 and q.bit_count()%2 == 1 and q.bit_count() < 9 for q in ports),
         'port labels')


def dot(x, y):
    return (x & y).bit_count() & 1


def u_columns(q):
    """Independently implement the historical swap + even transvection U_q."""
    need(0 < q < 512 and q.bit_count()%2 == 1 and q.bit_count() < 9, 'q domain')
    j = next(k for k in range(9) if not ((q >> k) & 1))
    v = q ^ (1 << j)
    need(v.bit_count()%2 == 0, 'transvection vector parity')
    columns = []
    for i in range(9):
        x = 1 << (j if i == 0 else 0 if i == j else i)
        if dot(x, v):
            x ^= v
        columns.append(x)
    validate_columns(q, columns)
    return columns


def validate_columns(q, columns):
    need(len(columns) == 9 and all(0 < x < 512 for x in columns), 'invalid U_q columns')
    need(columns[0] == q, 'U_q does not map e0 to q')
    need(all(dot(columns[i], columns[k]) == int(i == k)
             for i in range(9) for k in range(9)), 'U_q not orthogonal')


def rho(q, state, stage, columns=None):
    """GF(2) cover permutation on F2^9 plus four fresh F2^8 blocks."""
    need(1 <= stage <= 4 and 0 <= state < (1 << 41), 'rho domain')
    if columns is None:
        columns = u_columns(q)
    shift = 9 + 8*(stage-1)
    local = state & MASK9
    fresh = (state >> shift) & 255
    outside = state & ~(MASK9 | (255 << shift))
    new_local = q if dot(local, q) else 0
    for i in range(8):
        if (fresh >> i) & 1:
            new_local ^= columns[i+1]
    new_fresh = sum(dot(local, columns[i+1]) << i for i in range(8))
    return outside | new_local | (new_fresh << shift)


def route_census(ports):
    columns = {q: u_columns(q) for q in ports}
    for q in ports:
        for stage in range(1, 5):
            for i in range(41):
                basis = 1 << i
                need(rho(q, rho(q, basis, stage, columns[q]), stage, columns[q]) == basis,
                     'rho not involutive')
            if stage == 1:
                block_basis = list(range(9)) + list(range(9, 17))
                images = [rho(q, 1 << i, stage, columns[q]) for i in block_basis]
                need(all(dot(images[i], images[j]) == int(i == j)
                         for i in range(17) for j in range(17)), 'rho not orthogonal')
    matched = mismatched = 0
    witness = None
    for stage in range(1, 5):
        shift = 9+8*(stage-1)
        for p in ports:
            for q in ports:
                # Product order is immaterial for this preservation criterion.
                local_images = [rho(p, rho(q, 1 << (shift+i), stage, columns[q]),
                                    stage, columns[p]) & MASK9 for i in range(8)]
                preserves_fresh = not any(local_images)
                need(preserves_fresh == (p == q), 'fresh-space iff same-port claim')
                if p == q:
                    matched += 1
                else:
                    mismatched += 1
                    if witness is None:
                        i = next(i for i, value in enumerate(local_images) if value)
                        witness = {'stage': stage, 'p': p, 'q': q,
                                   'fresh_basis_index': i, 'nonzero_local_image': local_images[i]}
    need((matched, mismatched) == (448, 49728), 'route census cardinality')
    return matched, mismatched, witness


def multiply(a, b):
    return [[sum(a[i][k]*b[k][j] for k in range(2)) for j in range(2)]
            for i in range(2)]


def sign_line_gram():
    """Construct the 14 affine four-sets and 8 normalized sign lines on each."""
    blocks = []
    for normal in range(1, 8):
        for parity in range(2):
            block = tuple(i for i in range(8) if dot(i, normal) == parity)
            need(len(block) == 4, 'Hamming block size')
            blocks.append(block)
    need(len(set(blocks)) == 14, 'Hamming block uniqueness')
    lines = []
    for block in blocks:
        for signs in range(8):
            row = [0]*8
            for j, coordinate in enumerate(block):
                row[coordinate] = 1 if j == 0 or not ((signs >> (j-1)) & 1) else -1
            lines.append(tuple(row))
    need(len(lines) == len(set(lines)) == 112, 'sign-line uniqueness')
    need(all(sum(x*x for x in row) == 4 for row in lines), 'sign-line norm')
    gram = [[sum(row[i]*row[j] for row in lines) for j in range(8)] for i in range(8)]
    need(all(gram[i][j] == (56 if i == j else 0)
             for i in range(8) for j in range(8)), 'R transpose R differs from 14 I')
    return len(blocks), len(lines)


def two_pulse_floor():
    """Exact polynomial proof: <=2 arbitrary K shears cannot be exchange."""
    zero, one = {}, {(0, 0): 1}
    a, b = {(1, 0): 1}, {(0, 1): 1}
    def add(x, y):
        out = x.copy()
        for key, value in y.items():
            out[key] = out.get(key, 0) + value
        return {key: value for key, value in out.items() if value}
    def product(x, y):
        out = {}
        for (i, j), v in x.items():
            for (k, l), w in y.items():
                key = (i+k, j+l)
                out[key] = out.get(key, 0) + v*w
        return {key: value for key, value in out.items() if value}
    def times(x, y):
        return [[add(product(x[i][0], y[0][j]), product(x[i][1], y[1][j]))
                 for j in range(2)] for i in range(2)]
    def shear(kind, coefficient):
        return [[one, coefficient], [zero, one]] if kind == 'U' else \
               [[one, zero], [coefficient, one]]
    orientations = 0
    for first in ('L', 'U'):
        for second in ('L', 'U'):
            matrix = times(shear(second, b), shear(first, a))
            need(matrix[0][0] == one or matrix[1][1] == one,
                 'two center-bearing shears attain exchange')
            orientations += 1
    witness = [[Q(1), Q(0)], [Q(0), Q(1)]]
    for gate in ([[Q(1), Q(0)], [Q(1), Q(1)]],
                 [[Q(1), Q(-1)], [Q(0), Q(1)]],
                 [[Q(1), Q(0)], [Q(1), Q(1)]]):
        witness = multiply(gate, witness)
    need(witness == [[Q(0), Q(-1)], [Q(1), Q(0)]], 'three-pulse witness')
    return orientations


def stage_revisit_counterexample():
    """An off-diagonal port excursion makes same-port projection nonmultiplicative."""
    m = [[Q(0), Q(1)], [Q(1), Q(0)]]
    square = multiply(m, m)
    need(square == [[Q(1), Q(0)], [Q(0), Q(1)]], 'two-port return fixture')
    eye = lambda i, j: Q(i == j)
    upper = [[eye(i, j) if i//2 == j//2 else
              m[i%2][j%2] if i//2 == 0 else Q(0)
              for j in range(4)] for i in range(4)]
    lower = [[eye(i, j) if i//2 == j//2 else
              m[i%2][j%2] if i//2 == 1 else Q(0)
              for j in range(4)] for i in range(4)]
    product = [[sum(upper[i][k]*lower[k][j] for k in range(4))
                for j in range(4)] for i in range(4)]
    project = lambda a: [[a[i][j] for j in (0, 2)] for i in (0, 2)]
    projected_factors = multiply(project(upper), project(lower))
    need(m[0][0] == 0 and project(product)[0][0] == 2 and
         projected_factors[0][0] == 1 and project(product) != projected_factors,
         'projection limitation fixture')
    return 'M=[[0,1],[1,0]], (U(M)L(M))_same_port_upper_left=2'


def shear_word(m, word=FIVE_CALL):
    """Scalar word at M=m, K=1-m: an eigenvalue of M, or M_pp=0 for the
    multiplicative same-port projection (valid only without return paths)."""
    k = 1-m
    result = [[Q(1), Q(0)], [Q(0), Q(1)]]
    for kind, c, d in word:
        t = c*m + d*k
        gate = [[Q(1), Q(0)], [t, Q(1)]] if kind == 'L' else [[Q(1), t], [Q(0), Q(1)]]
        result = multiply(gate, result)
    return result


def controls(ports):
    bad = ports.copy()
    bad[0] = bad[1]
    try:
        validate_ports(bad)
    except ValueError:
        pass
    else:
        raise ValueError('duplicate port accepted')
    q = ports[0]
    cols = u_columns(q)
    wrong = cols.copy()
    wrong[0] = 1 << 0  # omit the transvection after the swap
    try:
        validate_columns(q, wrong)
    except ValueError:
        pass
    else:
        raise ValueError('corrupted-frame control accepted')
    changed = list(FIVE_CALL)
    changed[2] = ('L', Q(143, 144), Q(130, 144))
    need(shear_word(Q(-13), tuple(changed)) != [[Q(0), Q(-1)], [Q(1), Q(0)]],
         'middle-coefficient control failed')
    need(shear_word(Q(0)) != [[Q(0), Q(-1)], [Q(1), Q(0)]],
         'off-spectrum control failed')
    tampered = json.loads((HERE/PIN).read_bytes())
    for comment in tampered['comments']:
        comment['excerpt'] = comment['excerpt'].replace('131K', '130K')
    try:
        pinned_word(tampered)
    except ValueError as exc:
        need('differs from checked word' in str(exc), 'pin control rejected for wrong reason')
    else:
        raise ValueError('tampered discussion pin accepted')


def main():
    need(not sys.flags.optimize, 'run without -O')
    ports = sources()
    pin = pinned_word()
    matched, mismatched, witness = route_census(ports)
    blocks, lines = sign_line_gram()
    pulse_patterns = two_pulse_floor()
    revisit = stage_revisit_counterexample()
    exchange = [[Q(0), Q(-1)], [Q(1), Q(0)]]
    need(shear_word(Q(1)) == exchange and shear_word(Q(-13)) == exchange,
         'five-call local spectral identity')
    same_port = shear_word(Q(0))
    need(same_port == [[Q(1), Q(0)], [Q(131, 144), Q(1)]],
         'same-port block')
    controls(ports)
    output = {
        'status': 'PASS_CENTRE_FIVECALL_COVER_AUDIT',
        'scope': 'Conditional on the inherited rho route, the five-call word pinned verbatim from discussion 1636 (DISCUSSION-1636-PIN.json; provisional Discussion text, no candidate package or head), and one transition per fresh stage with no returning port excursion, so that same-cover projection is multiplicative. Both the L(131/144) same-port block and the three-pulse floor need that premise; this package does not derive it for the five-call word. Port frames, the 50,176-pair census, the Hamming sign-line Gram and M_pp=0 are checked from repository sources. Not an audit of a candidate package or a supplier.',
        'discussion': 'https://github.com/CrocSwap/integer-mult-bounds/discussions/1636',
        'discussion_pin': {str(c['id']): c['body_sha256'] for c in pin['comments']},
        'base_commit': '1f7a934975e5eacaf83511c9ac870263bf095e05',
        'port_count': len(ports), 'fresh_stages': 4,
        'ordered_stage_port_pairs': matched+mismatched,
        'fresh_preserving_pairs': matched, 'fresh_nonpreserving_pairs': mismatched,
        'first_failure_witness': witness,
        'hamming_weight4_blocks': blocks, 'normalized_sign_lines': lines,
        'normalized_sign_line_gram': 'R^T R = 14 I_8',
        'normalized_sign_line_M_diagonal': 0,
        'two_center_pulse_orientation_patterns_checked': pulse_patterns,
        'minimum_center_bearing_shears_in_single_pass_projection': 3,
        'attaining_projection_word': ['L(1)', 'U(-1)', 'L(1)'],
        'stage_revisit_projection_counterexample': revisit,
        'local_spectral_eigenvalues': [1, -13],
        'local_spectral_block': [['0','-1'],['1','0']],
        'same_cover_same_port_block': [['1','0'],['131/144','1']],
        'required_bank_exchange_block': [['0','-1'],['1','0']],
    }
    encoded = (json.dumps(output, indent=2, sort_keys=True)+'\n').encode()
    result_path = HERE/'RESULT.json'
    if sys.argv[1:] == ['--write']:
        result_path.write_bytes(encoded)
    else:
        need(not sys.argv[1:], 'usage: verify.py [--write]')
        need(result_path.read_bytes() == encoded, 'RESULT.json differs from exact replay')
    print(output['status'], 'pairs=50176', 'preserving=448', 'same_port=131/144', 'controls=5')


if __name__ == '__main__':
    main()
