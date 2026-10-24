"""Portable exact typed quotient checker. Apache-2.0; substantial AI assistance."""
from pathlib import Path
from collections import Counter
from hashlib import sha256
import json, gzip, sys, time
import argparse
_parser = argparse.ArgumentParser()
_parser.add_argument('--source-root', required=True, type=Path)
_args = _parser.parse_args()
H = Path(__file__).resolve().parent
R = _args.source_root.resolve()
_manifest = json.loads((H / 'SOURCE-CLOSURE.json').read_text(encoding='utf-8'))
for _row in _manifest['files']:
    if not sha256((R / _row['path']).read_bytes()).hexdigest() == _row['sha256']:
        raise ValueError('Changed source: ' + _row['path'])
for _name, _hash in _manifest['owned_inputs'].items():
    if not sha256((H / _name).read_bytes()).hexdigest() == _hash:
        raise ValueError('Changed quotient artifact: ' + _name)
sys.path.insert(0, str(R / 'research/joint-helper-lattice'))
import native_joint as J
F = J.F
ce = F.load(R / 'research/t74-native-fast/vendor/native/new/code/borrow/vendor/clifford/clifford_exact.py', 'typed_nf_ce')
P = F.load(R / 'research/kappa-function-composition/complex/prune_native.py', 'typed_nf_decode')
X = F.load(R / 'research/kappa-rebuild/complex/native_extensions.py', 'typed_nf_lower')
_repaired_raw = gzip.decompress((H / 'REPAIRED-WARP-WORD.json.gz').read_bytes())
if not sha256(_repaired_raw).hexdigest() == _manifest['repaired_payload_sha256']:
    raise ValueError('Exact check failed at original source line 20')
z = json.loads(_repaired_raw)
c = z['canonical']
cache = {}

def frame(i):
    if i not in cache:
        cache[i] = ce.canonical_frame(9, c['frames'][i])
    return cache[i]

def sp(b):
    s = {0}
    for v in b:
        s |= {x ^ v for x in tuple(s)}
    return frozenset(s)

def basis(s):
    b = []
    cur = {0}
    for v in sorted(s):
        if v not in cur:
            b.append(v)
            cur |= {x ^ v for x in tuple(cur)}
    return b

def extend(B, more):
    for v in more:
        if ce.rank(B + [v]) > len(B):
            B.append(v)
    return B

def Kop(cols):
    G = ce.transpose(tuple(cols), 9)
    gi = ce.inv(G, 9)
    tr = ce.transpose(gi, 9)
    quad = tuple((1 << i ^ sum((ce.parity(a & b) << j for j, b in enumerate(tr))) for i, a in enumerate(tr)))
    return ce.perm(9, G).then(ce.diag(9, quad))

def equal(a, b):
    return a.tab == b.tab and a.zero_state() == b.zero_state()
D = ce.fourier(9, range(1, 8))
Q = ce.cgate(9, 1)
out = []
st = time.monotonic()
kinds = Counter()
for port in range(112):
    sx, sy = (c['start'][port], c['start'][112 + port])
    hy, ax = (c['final'][port], c['final'][112 + port])
    if not (not c['frames'][sy] and len(c['frames'][sx]) == 1):
        raise ValueError('Exact check failed at original source line 43')
    cvec = c['frames'][sx][0]
    AA = sp(c['frames'][ax])
    HH = sp(c['frames'][hy])
    if not (len(HH) == 256 and cvec in HH):
        raise ValueError('Exact check failed at original source line 44')
    if len(AA) == 128:
        kind = 'A'
        if not (cvec not in AA and AA < HH):
            raise ValueError('Exact check failed at original source line 46')
        cols = [cvec] + basis(AA)
        TY = D
    else:
        kind = 'B'
        if not AA == HH:
            raise ValueError('Exact check failed at original source line 48')
        cols = extend([cvec], basis(HH))
        TY = D.then(Q)
    cols = extend(cols, [1 << i for i in range(9)])
    if not len(cols) == 9:
        raise ValueError('Exact check failed at original source line 49')
    MY = Kop(cols)
    Cc, CA, CH = (frame(sx), frame(ax), frame(hy))
    AX = Cc.adjoint().then(CH)
    MX = Q.adjoint().then(MY).then(Cc)
    OX = CH.adjoint().then(MY.adjoint()).then(Q).then(D)
    OY = CA.adjoint().then(MY.adjoint()).then(TY)
    wrappers = {}
    for name, op in [('input_X', MX), ('input_Y', MY), ('output_X', OX), ('output_Y', OY)]:
        rec = X.N.lower_exact(P, ce, op)
        if not (rec['rank'] == 0 and rec['right'] is None):
            raise ValueError('Exact check failed at original source line 56')
        wrappers[name] = rec
    if not equal(MX.then(AX).then(OX), D):
        raise ValueError('Exact check failed at original source line 57')
    if not equal(MY.then(CA).then(OY), TY):
        raise ValueError('Exact check failed at original source line 58')
    if not equal(MX.then(Cc.adjoint()).then(CA).then(OY), Q.adjoint().then(TY)):
        raise ValueError('Exact check failed at original source line 59')
    kinds[kind] += 1
    out.append(dict(port=port, kind=kind, center_vector=cvec, frames=dict(start_X=sx, start_Y=sy, final_X=hy, final_Y=ax), address_map_columns=cols, wrappers=wrappers, exact_diagonal_X=True, exact_diagonal_Y=True, exact_shear_coefficient=True))
    if port % 16 == 0:
        print('PAIR', port, '/', 112, flush=True)
payload = json.dumps(out, sort_keys=True, separators=(',', ':')).encode()
(H / 'TYPED-PAIR-NORMALIZERS.json.gz').write_bytes(gzip.compress(payload, mtime=0))
receipt = dict(status='PASS_EXACT_TYPED_QUOTIENT_PAIR_NORMAL_FORM', port_types=dict(kinds), ports=112, exact_monomial_normalizers=448, exact_block_identities=336, absolute_phases=True, source_word_payload_sha256=sha256(gzip.decompress((H / 'REPAIRED-WARP-WORD.json.gz').read_bytes())).hexdigest(), normalizers_payload_sha256=sha256(payload).hexdigest(), seconds=time.monotonic() - st, forward_type_A='D S_y(Q^-1)', forward_type_B='diag(D,QD) S_y(Q^-1)', D_rank=7, Q_rank=1, Q_squared='monomial', scope='Typed local supplier, not old rank-eight interface or a completed multiplication theorem')
(H / 'TYPED-PAIR-RECEIPT.json').write_text(json.dumps(receipt, indent=2))
print(json.dumps(receipt, indent=2))
