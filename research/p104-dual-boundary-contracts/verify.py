"""Read-only boundary-contract witness, not a replay of any full dual word."""
from pathlib import Path
from fractions import Fraction as Q
from itertools import combinations, product
import argparse
import gzip
import hashlib
import json
import types

P = Path(__file__).resolve().parent
R = P.parents[1]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    manifest = json.loads((P / 'SOURCES.json').read_text())
    for item in manifest['files']:
        if item['usage'] == 'input':
            raw = (R / item['path']).read_bytes()
            need(hashlib.sha256(raw).hexdigest() == item['sha256'], 'source SHA256: ' + item['path'])
            need(hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == item['git_blob'], 'source Git blob: ' + item['path'])
    for item in manifest['retained_proof_sources']:
        raw = (P / item['path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == item['sha256'], 'retained proof SHA256: ' + item['path'])
        need(hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == item['git_blob'], 'retained proof Git blob: ' + item['path'])
    # Never execute a dependency before the complete input set is authenticated.
    path = R / 'research/p104-native-channel/vendor/native_verify.py'
    module = types.ModuleType('bound_native')
    module.__file__ = str(path)
    # Compile the authenticated bytes rather than consulting timestamp bytecode.
    # See the concurrent source-cache finding on PR2522; no runner fix here.
    raw = path.read_bytes()
    pin = next(x for x in manifest['files'] if x['path'].endswith('/vendor/native_verify.py'))
    need(hashlib.sha256(raw).hexdigest() == pin['sha256'], 'native bytes immediately before compile')
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


def roots():
    out = set()
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            out.add(tuple(row))
    for tail in product((-1, 1), repeat=7):
        if tail.count(-1) % 2 == 0:
            out.add((1, *tail))
    need(len(out) == 120, 'E8 root-line count')
    return sorted(out)


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def mul(a, b):
    return a[0]*b[0] - a[1]*b[1], a[0]*b[1] + a[1]*b[0]


def power(a, n):
    out = (Q(1), Q(0))
    for _ in range(n):
        out = mul(out, a)
    return out


def direct_column(circuit):
    """Separate Fraction implementation of P/D/C/X/phase on one 512-column.

    Credit the retained PR1862 interpreter for the gate semantics. This uses
    neither its state/action routine nor its common-denominator implementation.
    It is a corroboration of this column, not an independent whole-word proof.
    """
    vec = [(Q(0), Q(0)) for _ in range(512)]
    vec[0] = (Q(1), Q(0))
    for gate in circuit:
        out = [(Q(0), Q(0)) for _ in range(512)]
        kind = gate[0]
        for x, value in enumerate(vec):
            if value == (0, 0):
                continue
            if kind == 'C':
                a, b = (Q(1, 2), Q(gate[2], 2)), (Q(1, 2), Q(-gate[2], 2))
                out[x] = add(out[x], mul(a, value))
                out[x ^ gate[1]] = add(out[x ^ gate[1]], mul(b, value))
                continue
            y, phase = x, 0
            if kind == 'P':
                y = sum(((row & x).bit_count() % 2) << j for j, row in enumerate(gate[1]))
            elif kind == 'X':
                y ^= gate[1]
            elif kind == 'D':
                matrix, linear = gate[1:]
                phase = sum(linear[i] for i in range(9) if x & (1 << i))
                phase += 2 * sum((matrix[i] >> j) & 1 for i in range(9) for j in range(i+1, 9) if x & (1 << i) and x & (1 << j))
            else:
                need(kind == 'phase', 'direct gate type')
                phase = gate[1]
            out[y] = add(out[y], mul(power((Q(0), Q(1)), phase % 4), value))
        vec = out
    return vec


def native_column(N, circuit):
    values, exponent = N.state(circuit)
    return [(Q(values.get(x, (0, 0))[0], 1 << exponent), Q(values.get(x, (0, 0))[1], 1 << exponent)) for x in range(512)]


def compute():
    N = authenticate()
    base = R / 'research/p104-native-channel'
    certificate = json.loads(gzip.decompress((base / 'NATIVE-RECIPES.json.gz').read_bytes()))
    word = json.loads((base / 'inputs/LOWRANK-WITNESS.json').read_text())
    fixture = json.loads((base / 'inputs/P104-FIXTURE.json').read_text())['section4_explicit_P104']
    rr = roots()
    removed = {tuple(row) for row in fixture['F0'] + fixture['C']}
    ports = [row for row in rr if row not in removed]
    need(len(ports) == 104, 'port ordering')
    coefficient = Q(sum(a*b for a, b in zip(ports[2], ports[0])), 8)
    need(coefficient == Q(1, 2), 'shared unchanged row coefficient')

    # Reconstruct the complete physical label isometry, not just literal q IDs.
    iso = certificate['label_isometry']
    inner = lambda a, b: sum(x*y for x, y in zip(a, b)) // 4
    binary = [sum(((inner(a, b)+1) & 1) << j for j, b in enumerate(rr)) for a in rr]
    pivots = iso['pivot_root_indices']
    compressed = [sum(((row >> j) & 1) << k for k, j in enumerate(pivots)) for row in binary]
    gram = [compressed[i] for i in pivots]
    need(gram == iso['compressed_gram'], 'compressed Gram')
    dual = N.inverse(tuple(gram))
    need(list(dual) == iso['compressed_dual_gram'], 'dual Gram')
    dot = lambda a, b: (a & N.mul(dual, b)).bit_count() % 2
    orth = iso['orthonormal_basis_compressed']
    need(len(orth) == 9 and all(dot(a, b) == int(i == j) for i, a in enumerate(orth) for j, b in enumerate(orth)), 'physical orthonormality')
    convert = lambda value: sum(dot(value, b) << i for i, b in enumerate(orth))
    labels = [convert(value) for value in compressed]
    need(labels == iso['physical_root_labels'], 'physical root labels')
    need(all(((a & b).bit_count() & 1) == ((binary[i] >> j) & 1) for i, a in enumerate(labels) for j, b in enumerate(labels)), 'all physical pairings')
    label = dict(zip(rr, labels))
    adapters = {(x['position'], x['register']): x for x in certificate['endpoint_adapters']}
    xrec, yrec = adapters['entry', 'X0'], adapters['exit', 'Y2']
    xframe, yframe = tuple(xrec['frame']), tuple(yrec['frame'])
    qx, qy = label[ports[0]], label[ports[2]]
    need((qx, qy) == (386, 405), 'witness physical root IDs')
    need((xrec['normal'], yrec['normal']) == (qx, qy), 'adapter root binding')
    def span(values):
        out = {0}
        for v in values:
            out |= {x ^ v for x in tuple(out)}
        return out
    need(span(xframe) == span(map(convert, word['initial_frames']['X0'])), 'X0 initial frame binding')
    need(span(yframe) == span(map(convert, word['final_frames']['Y2'])), 'Y2 final frame binding')
    need(len(word['final_frames']['X0']) == 9 and word['initial_frames']['Y2'] == [], 'unmodified opposite endpoints')
    need(xframe == (386,) and yframe == (257,129,64,32,17,8,5,2), 'literal canonical chart representatives')
    F = N.fourier(9)
    X, Y = N.frame(xframe, 9), N.frame(yframe, 9)
    Xi, Yi = (('C', qx, 1),), (('C', qy, -1),) + F
    N.equal(N.recipe(xrec['recipe']), N.adjoint(Xi) + X, 'X intrinsic-to-canonical adapter')
    N.equal(N.recipe(yrec['recipe']), N.adjoint(Y) + Yi, 'Y canonical-to-intrinsic adapter')
    expected = N.adjoint(F)
    need(native_column(N, expected)[0] == (Q(1,32), Q(-1,32)), 'ordinary F inverse entry')
    variants, columns = {}, {}
    controls = []
    for name, gx, gy in [('canonical', X, Y), ('intrinsic', Xi, Yi)]:
        raw = N.adjoint(gy) + gx
        direct = direct_column(raw)
        need(direct == native_column(N, raw), name + ' separate Fraction column')
        physical = direct_column(expected)
        need(physical == native_column(N, expected), 'physical Fraction column')
        need(direct[0] == (0,0) and direct != physical, name + ' physical distinction')
        need(N.tableau(raw) != N.tableau(expected), name + ' distinction beyond global phase')
        # Gate arrays are chronological: right wrapper B, operator R, left A.
        right = gy
        left = N.adjoint(gx) + N.adjoint(F)
        N.equal(right + raw + left, expected, name + ' both-sided rewrapping')
        for tag, wrong in [('missing-input-wrapper', raw + left), ('missing-output-wrapper', right + raw), ('adjoint-confused-with-transpose', F), ('global-phase', right + raw + left + (('phase',1),))]:
            differs = N.tableau(wrong) != N.tableau(expected) or N.state(wrong) != N.state(expected)
            need(differs, name + ' rejecting control ' + tag)
            controls.append(name + ':' + tag)
        columns[name] = direct
        variants[name] = dict(raw_support=sum(v != (0,0) for v in direct),raw_address0=[str(v) for v in direct[0]],X0_address0=['0','0'],ordinary_physical_X0_address0=['-1/64','1/64'],two_sided_wrapping='exact full Clifford identity',full_column_sha256=hashlib.sha256(json.dumps([[str(a),str(b)] for a,b in direct],separators=(',',':')).encode()).hexdigest())
    # A closed four-term calculation corroborates the intrinsic witness without
    # frame construction, native state code, or the second column interpreter.
    a, b = (Q(1,2),Q(1,2)), (Q(1,2),Q(-1,2))
    f = lambda x: mul(power(b,9-x.bit_count()),power(a,x.bit_count()))
    four_terms = [mul(mul(a,a),f(0)),mul(mul(a,b),f(qx)),mul(mul(a,b),f(qy)),mul(mul(b,b),f(qx^qy))]
    total = (Q(0),Q(0))
    for term in four_terms:
        total = add(total,term)
    need(total == (0,0), 'intrinsic four-term cancellation')
    need(Q(sum(a*b for a,b in zip(ports[0],ports[0])),8) == 1, 'corrected-row positive control')
    return dict(schema_version=1,status='PASS',scope='Boundary contract distinction, no full word replay or priced wrappers',source_port=0,target_port=2,logical_coefficient='1/2',physical_input='Y2=delta_0; all other persistent inputs zero',canonical_frames=dict(X0_entry=list(xframe),Y2_exit=list(yframe)),intrinsic_normals=dict(X0=qx,Y2=qy),variants=variants,canonical_and_intrinsic_columns_equal=columns['canonical']==columns['intrinsic'],intrinsic_four_terms=[[str(a),str(b)] for a,b in four_terms],ordinary_unit_support=512,rejecting_controls=controls,physical_pairings_checked=14400,no_new_kappa=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, help='Write recomputed receipt to a new path')
    args = ap.parse_args()
    result = compute()
    if args.out:
        with args.out.open('x', encoding='utf-8', newline='\n') as out:
            out.write(json.dumps(result,indent=2)+'\n')
    else:
        need(json.loads((P/'RESULT.json').read_text()) == result, 'complete retained RESULT equality')
    print('PASS_P104_DUAL_BOUNDARY_CONTRACTS variants=2 physical_pairings=14400 controls=8 no_new_kappa')


if __name__ == '__main__':
    main()
