"""Endpoint-support tradeoff and fixed-frame obstruction for complete queries.

Read frozen original inputs directly; import no pending PR implementation.
This is finite evidence for PROOF.md, not a complete supplier verification.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from io import BytesIO
from pathlib import Path
import argparse
import copy
import gzip
import json
import math
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = ROOT / 'research/community-frontier1042-audit/selected-replay.tar.gz'
ARCHIVE_SHA = '22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754'
MEMBERS = {
    'slots/local/CANONICAL-WORD.json.gz': ('16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219', '4ddb29fb9bc6f27e0c0fbfcf19a2a93a3496ad900d0f6d89059d0305c9576c0c'),
    'slots/local/LOCAL-PROGRAMS.json.gz': ('241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a', '9f41d53659e9be84e20c661560c5687abbf5cd0660cdecbe01ad5eb29e6b8ee3'),
    't16/global/base/work/complex-nine-native/DATA-PHASES.json': ('c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa', 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa'),
}
A = [0, 7, 20, 27, 36, 46, 57, 111]
T = [21, 37, 47, 76, 81, 87, 92, 110]


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def load(raw):
    need(sha256(raw).hexdigest() == ARCHIVE_SHA, 'frozen archive hash')
    data = {}
    with tarfile.open(fileobj=BytesIO(raw), mode='r:gz') as tf:
        for name, (packed_hash, payload_hash) in MEMBERS.items():
            matches = [m for m in tf.getmembers() if m.name == name]
            need(len(matches) == 1 and matches[0].isfile(), 'unique regular archive member')
            packed = tf.extractfile(matches[0]).read()
            need(sha256(packed).hexdigest() == packed_hash, 'archive member hash')
            payload = gzip.decompress(packed) if name.endswith('.gz') else packed
            need(sha256(payload).hexdigest() == payload_hash, 'decoded member hash')
            data[name.rsplit('/', 1)[1]] = json.loads(payload)
    return data


def query_rows(word, program):
    n = 2 * word['v'] + word['R']
    need((word['v'], word['R'], word['h']) == (112, 480, 9), 'source geometry')
    rows = [{i: Q(1)} for i in range(n + 8)]
    found = False
    def index(field):
        tag, i = field
        need(tag in ('L', 'C'), 'field namespace')
        return i + (n if tag == 'C' else 0)
    for event in program:
        if event == ['phase', 'centers']:
            found = True
            break
        if event[0] != 'scalar':
            continue
        op = event[1]
        dst = index(op[1])
        if op[0] == 'clear':
            rows[dst] = {}
        elif op[0] == 'copy':
            rows[dst] = rows[index(op[2])].copy()
        elif op[0] == 'scale':
            value = Q(op[2], op[3])
            rows[dst] = {j: value * x for j, x in rows[dst].items() if value * x}
        else:
            need(op[0] == 'add', 'scalar operation')
            value = Q(op[3], op[4])
            for j, x in list(rows[index(op[2])].items()):
                y = rows[dst].get(j, Q(0)) + value * x
                if y:
                    rows[dst][j] = y
                else:
                    rows[dst].pop(j, None)
    need(found and len(word['centers']) == 8, 'centre boundary')
    need(all(not any(112 <= j < 224 or j >= n for j in rows[c]) for c in word['centers']), 'source/helper-only query')
    return [[rows[c].get(j, Q(0)) for j in range(112)] for c in word['centers']]


def product(a, b):
    return [[sum(x * y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def determinant(a):
    a = [[Q(x) for x in row] for row in a]
    result = Q(1)
    for j in range(len(a)):
        p = next((i for i in range(j, len(a)) if a[i][j]), None)
        if p is None:
            return Q(0)
        if p != j:
            a[j], a[p] = a[p], a[j]
            result = -result
        pivot = a[j][j]
        result *= pivot
        for i in range(j + 1, len(a)):
            coefficient = a[i][j] / pivot
            a[i] = [x - coefficient * y for x, y in zip(a[i], a[j])]
    return result


def integer_row(row):
    denominator = math.lcm(*(x.denominator for x in row))
    values = [int(x * denominator) for x in row]
    divisor = math.gcd(*values)
    return [x // divisor for x in values] if divisor else values


def independent_ports(rows, ports):
    pivots, chosen = {}, []
    for port in ports:
        v = integer_row(rows[port])
        for j, b in sorted(pivots.items()):
            if v[j]:
                x, y = b[j], v[j]
                v = [x * a - y * c for a, c in zip(v, b)]
                divisor = math.gcd(*v)
                if divisor:
                    v = [a // divisor for a in v]
        if any(v):
            pivots[next(j for j, x in enumerate(v) if x)] = v
            chosen.append(port)
        if len(chosen) == 8:
            break
    return chosen


def validate_witness(witness, q, z):
    x = witness['character']
    for bit, ports in enumerate(witness['port_minors']):
        need(len(ports) == len(set(ports)) == 8, 'eight distinct minor rows')
        need(all(((q[i] & x).bit_count() & 1) != bit for i in ports), 'excluded eigenvalue rows')
        d = determinant([z[i] for i in ports])
        need(d != 0 and str(d) == witness['determinants'][bit], 'exact nonzero determinant')


def validate_selected_row(witness, q):
    i, j, x = (witness[key] for key in ('output_port', 'input_port', 'character'))
    coefficient = Q(witness['coefficient'])
    need(coefficient != 0, 'nonzero forced coefficient')
    bits = [(q[p] & x).bit_count() & 1 for p in (i, j)]
    need(bits[0] != bits[1], 'different line eigenvalues')
    need(witness['line_eigenbits'] == bits, 'line eigenbit receipt')
    phases = [(x.bit_count()-b) % 4 for b in bits]
    need(witness['output_frame_phases_mod4'] == phases and phases[0] != phases[1], 'different output-frame eigenvalues')


def rejected(fn):
    try:
        fn()
    except ValueError:
        return True
    return False


def endpoint_toy(k, ell, g):
    """Literal three-port examples exercise every support-cover premise."""
    r = [[1, 1, 1]]
    eye = [[int(i == j) for j in range(3)] for i in range(3)]
    delta = [[g[i][j] - eye[i][j] for j in range(3)] for i in range(3)]
    kr = product(k, r)
    jay = [[eye[i][j] - kr[i][j] for j in range(3)] for i in range(3)]
    h = product(jay, delta)
    source = [i for i, row in enumerate(delta) if any(row)]
    target = [i for i, row in enumerate(h) if any(row)]
    return dict(R=r, K=k, L=ell, G=g, logger=product(ell, g) == r, invertible=determinant(g) != 0, full_query_difference=any(a != b for a, b in zip(r[0], ell[0])), nonzero_K_rows=all(any(row) for row in k), invertible_J=determinant(jay) != 0, source_support=source, target_support=target, union=sorted(set(source) | set(target)))


def build():
    raw = ARCHIVE.read_bytes()
    data = load(raw)
    word = data['CANONICAL-WORD.json.gz']
    q = word['ports']
    physical_q = [row['q'] for row in sorted(data['DATA-PHASES.json']['recipes'], key=lambda r: r['port'])]
    need(q == physical_q and len(set(q)) == 112, 'physical input line labels')
    r = query_rows(word, data['LOCAL-PROGRAMS.json.gz']['forward'])
    rt = list(map(list, zip(*r)))
    ident = [[Q(i == j) for j in range(8)] for i in range(8)]
    need(product(r, rt) == [[56 * x for x in row] for row in ident], 'R R transpose')
    need(len(A) == len(T) == 8 and not set(A) & set(T), 'disjoint selected minors')
    for ports in (A, T):
        small = [[row[j] for j in ports] for row in r]
        need(product(small, list(map(list, zip(*small)))) == [[4 * x for x in row] for row in ident], 'dyadic coordinate minor')
    k = [[x / 4 for x in row] for row in rt]
    z = [[(-12 if i in A else 1) * x for x in row] for i, row in enumerate(k)]
    ell = [[x if j in T else Q(0) for j, x in enumerate(row)] for row in r]
    need(product(r, z) == product(ell, z) == ident, 'fixed-support response identities')
    # Every LG=R forces G_T=L_T^-1 R=K_T R, even for operator-valued G.
    kt = [k[i] for i in T]
    selected_rows = product(kt, r)
    need(product([[row[j] for j in T] for row in ell], kt) == ident, 'inverse selected read')
    selected_index, j, value = next((t, j, x) for t, row in enumerate(selected_rows) for j, x in enumerate(row) if j not in T and x)
    i = T[selected_index]
    character = (q[i] ^ q[j]) & -(q[i] ^ q[j])
    bits = [(q[p] & character).bit_count() & 1 for p in (i, j)]
    forced = dict(output_port=i, input_port=j, coefficient=str(value), character=character, line_eigenbits=bits, output_frame_phases_mod4=[(character.bit_count()-b) % 4 for b in bits])
    validate_selected_row(forced, q)
    # A sparse-source algebraic logger attains the cover in the actual 112-port instance.
    u = [[Q(0)]*8 for _ in range(112)]
    for p in T:
        u[p] = k[p][:]
    difference = [[x-y for x, y in zip(a, b)] for a, b in zip(r, ell)]
    need(product(r, u) == product(ell, u) == ident, 'sparse-source response')
    need(product(difference, u) == [[Q(0)]*8 for _ in range(8)], 'nilpotent sparse-source encoder')
    delta = product(u, difference)
    response = [[a-b for a, b in zip(ui, ki)] for ui, ki in zip(u, k)]
    correction = product(response, difference)
    source_support = [i for i, row in enumerate(delta) if any(row)]
    target_support = [i for i, row in enumerate(correction) if any(row)]
    need(source_support == T and len(target_support) == 104 and not set(source_support)&set(target_support), 'actual-instance sharp endpoint support')
    need(sorted(source_support+target_support) == list(range(112)), 'actual-instance cover')
    q_minor = determinant([[row[j] for j in A] for row in difference])
    need(q_minor != 0 and all(any(row) for row in k), 'support-cover hypotheses')
    need(product(r, k) == [[14*x for x in row] for row in ident], 'invertible J via RK=14I')
    good_g = [[1, 1, 1], [0, 1, 0], [0, 0, 1]]
    singular_g = [[1, 1, 1], [0, 1, 0], [0, -1, 0]]
    identity_g = [[int(i == j) for j in range(3)] for i in range(3)]
    positive = endpoint_toy([[1], [1], [1]], [[1, 0, 0]], good_g)
    need(positive['logger'] and positive['invertible'] and positive['union'] == [0, 1, 2], 'sharp support-cover toy')
    need(len(positive['source_support']) + len(positive['target_support']) == 3, 'sharp union budget')
    premise_examples = dict(no_invertibility=endpoint_toy([[1], [1], [1]], [[1, 0, 0]], singular_g), no_query_difference_rank=endpoint_toy([[1], [1], [1]], [[1, 1, 1]], identity_g), zero_K_row=endpoint_toy([[1], [0], [1]], [[1, 0, 0]], good_g))
    for name, example in premise_examples.items():
        need(example['logger'] and len(example['union']) < 3 and example['invertible_J'], 'genuine missing-premise counterexample '+name)
    need(not premise_examples['no_invertibility']['invertible'] and premise_examples['no_invertibility']['full_query_difference'] and premise_examples['no_invertibility']['nonzero_K_rows'], 'invertibility control isolates premise')
    need(premise_examples['no_query_difference_rank']['invertible'] and not premise_examples['no_query_difference_rank']['full_query_difference'] and premise_examples['no_query_difference_rank']['nonzero_K_rows'], 'query-difference control isolates premise')
    need(premise_examples['zero_K_row']['invertible'] and premise_examples['zero_K_row']['full_query_difference'] and not premise_examples['zero_K_row']['nonzero_K_rows'], 'K-row control isolates premise')
    census, witness = [], None
    for x in range(512):
        minors = [independent_ports(z, [i for i, qi in enumerate(q) if ((qi & x).bit_count() & 1) != bit]) for bit in (0, 1)]
        ranks = list(map(len, minors))
        census.append(ranks)
        if witness is None and ranks == [8, 8]:
            witness = dict(character=x, port_minors=minors, determinants=[str(determinant([z[i] for i in ps])) for ps in minors])
    need(witness is not None, 'full-rank character')
    validate_witness(witness, q, z)
    mismatch = next((i, j, str(r[i][j]), str(ell[i][j])) for i in range(8) for j in range(112) if r[i][j] != ell[i][j])
    bad_character = dict(witness, character=0)
    bad_z = copy.deepcopy(z)
    bad_z[witness['port_minors'][0][0]] = [Q(0)] * 8
    bad_det = dict(witness, determinants=['0', witness['determinants'][1]])
    mutated_raw = bytes([raw[0] ^ 1]) + raw[1:]
    controls = dict(constant_character=rejected(lambda: validate_witness(bad_character, q, z)), zeroed_matrix_row=rejected(lambda: validate_witness(witness, q, bad_z)), false_determinant=rejected(lambda: validate_witness(bad_det, q, z)), changed_source_archive=rejected(lambda: load(mutated_raw)))
    same_q = list(q)
    same_q[forced['input_port']] = same_q[forced['output_port']]
    controls.update(zero_forced_coefficient=rejected(lambda: validate_selected_row(dict(forced, coefficient='0'), q)), equal_line_labels=rejected(lambda: validate_selected_row(forced, same_q)), constant_forced_character=rejected(lambda: validate_selected_row(dict(forced, character=0), q)))
    need(all(controls.values()), 'mutation controls')
    counts = Counter(map(tuple, census))
    return dict(schema=3, status='PASS_SOURCECODE_SUPPORT_AND_FIXED_FRAME', source_archive_sha256=ARCHIVE_SHA, predecessor_pr=1862, predecessor_head='7649d9ceecec949541bec4bbde5929344166ba59', compensation_ports=A, query_ports=T, support_cover=dict(Q_minor_ports=A, Q_minor_determinant=str(q_minor), nonzero_K_rows=112, query_rank=8, minimum_source_support=8, minimum_target_support=8, minimum_endpoint_support_sum=112, conditional_rowwise_out_and_back_budget=120, sharp_actual_source_support=source_support, sharp_actual_target_support=target_support, sharp_example='G=I+U(R-L), U=K restricted to rows T. RU=LU=I and (R-L)U=0, so G^-1=I-U(R-L). Target correction=(U-K)(R-L). Algebraic example, no complete native invoice.', sharp_three_port_example=positive, missing_premise_counterexamples=premise_examples), forced_selected_row=forced, rank_census=[dict(ranks=list(rs), characters=n) for rs, n in sorted(counts.items())], full_rank_characters=counts[8, 8], witness=witness, R_L_mismatch=list(mismatch), controls=controls, scope='Every invertible full-query encoder has source-change and target-correction supports covering all 112 ports; an explicit algebraic encoder attains the cover with 8 changed source and 104 corrected target ports. Endpoint support is not a universal native-child charge. No logger with this fixed eight-port read L can commute with diag(C_q), or with the specified output frame diag(F C_q^-1), even allowing arbitrary address-linear G and positive tensor powers. The fixed-Z logger is unique; its separate two-minor test agrees. Does not exclude changed/conjugated operators, changed query reads, paid transitions or all zero-native circuits; no supplier or kappa claim.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record', action='store_true', help='regenerate the package EXPECTED.json during authoring')
    parser.add_argument('--out', type=Path, help='write a new replay receipt')
    args = parser.parse_args()
    result = build()
    raw = (json.dumps(result, indent=2, sort_keys=True) + '\n').encode()
    expected = HERE / 'EXPECTED.json'
    if args.record:
        with expected.open('wb') as f:
            f.write(raw)
    else:
        need(json.loads(expected.read_text(encoding='utf-8')) == result, 'expected exact certificate')
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open('xb') as f:
            f.write(raw)
    print('PASS_SOURCECODE_SUPPORT_AND_FRAME endpoint_support>=112 sharp=8+104 characters=512 full_rank=494 mutations=7 premise_controls=3 no_new_kappa')


if __name__ == '__main__':
    main()
