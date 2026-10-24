"""Portable exact orthogonal-restriction builder. Apache-2.0; AI assistance."""
from pathlib import Path
from collections import Counter
import json, gzip, sys, time, hashlib
import argparse, hashlib
_parser = argparse.ArgumentParser()
_parser.add_argument('--source-root', required=True, type=Path)
_parser.add_argument('--mains-only', action='store_true')
_args = _parser.parse_args()
H = Path(__file__).resolve().parent
R = _args.source_root.resolve()
_manifest = json.loads((H / 'SOURCE-CLOSURE-ROUND3.json').read_text(encoding='utf-8'))
for _row in _manifest['files']:
    if not hashlib.sha256((R / _row['path']).read_bytes()).hexdigest() == _row['sha256']:
        raise ValueError('Changed source: ' + _row['path'])
for _name, _hash in _manifest['owned_modules'].items():
    if not hashlib.sha256((H / _name).read_bytes()).hexdigest() == _hash:
        raise ValueError('Changed owned module: ' + _name)
sys.path.insert(0, str(H))
from synthesis import synthesize as _resynthesize
sys.path.insert(0, str(R / 'research/joint-helper-lattice'))
import native_joint as J
F = J.F
ce = F.load(R / 'research/t74-native-fast/vendor/native/new/code/borrow/vendor/clifford/clifford_exact.py', 'h153nf_ce')
P = F.load(R / 'research/kappa-function-composition/complex/prune_native.py', 'h153nf_decode')
X = F.load(R / 'research/kappa-rebuild/complex/native_extensions.py', 'h153nf_lower')
_actual = gzip.decompress((H / 'INTERSECTION153-ROUND3-ACTUAL-WORD.json.gz').read_bytes())
if not hashlib.sha256(_actual).hexdigest() == _manifest['actual_payload_sha256']:
    raise ValueError('Exact check failed at original source line 20')
z = json.loads(_actual)
c = z['canonical']
fc = {}

def frame(i):
    if i not in fc:
        fc[i] = ce.canonical_frame(9, c['frames'][i])
    return fc[i]

def sp(b):
    s = {0}
    for v in b:
        s |= {x ^ v for x in tuple(s)}
    return s

def basis(s):
    b = []
    cur = {0}
    for v in sorted(s):
        if v not in cur:
            b.append(v)
            cur |= {x ^ v for x in tuple(cur)}
    return b

def extend(b, ss):
    for v in ss:
        if ce.rank(b + [v]) > len(b):
            b.append(v)
    return b

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
kinds = Counter()
st = time.monotonic()
for port in range(112):
    sx, sy = (c['start'][port], c['start'][112 + port])
    hx, ay = (c['final'][port], c['final'][112 + port])
    HH, AA = (sp(c['frames'][hx]), sp(c['frames'][ay]))
    if not (len(HH) == 256 and len(AA) == 128 and (AA < HH) and (not c['frames'][sy])):
        raise ValueError('Exact check failed at original source line 42')
    if len(c['frames'][sx]) == 1:
        kind = 'A'
        cv = c['frames'][sx][0]
        if not (cv not in AA and cv in HH):
            raise ValueError('Exact check failed at original source line 44')
        cols = [cv] + basis(AA)
        TY = D
        TX = D
    else:
        kind = 'C'
        if not not c['frames'][sx]:
            raise ValueError('Exact check failed at original source line 46')
        cv = next((v for v in sorted(HH) if v not in AA))
        cols = [cv] + basis(AA)
        TY = D
        TX = D.then(Q)
    cols = extend(cols, [1 << i for i in range(9)])
    MY = Kop(cols)
    CA, CH = (frame(ay), frame(hx))
    if kind == 'A':
        Cc = frame(sx)
        MX = Q.adjoint().then(MY).then(Cc)
        AX = Cc.adjoint().then(CH)
        BX = Cc.adjoint().then(CA)
        OX = CH.adjoint().then(MY.adjoint()).then(Q).then(D)
        expected_B = Q.adjoint().then(D)
    else:
        MX = MY
        AX = CH
        BX = CA
        OX = CH.adjoint().then(MY.adjoint()).then(TX)
        expected_B = D
    OY = CA.adjoint().then(MY.adjoint()).then(D)
    wrappers = {}
    for name, op in [('input_X', MX), ('input_Y', MY), ('output_X', OX), ('output_Y', OY)]:
        rec = X.N.lower_exact(P, ce, op)
        if not rec['rank'] == 0:
            raise ValueError('Exact check failed at original source line 54')
        wrappers[name] = rec
    if not equal(MX.then(AX).then(OX), TX):
        raise ValueError('Exact check failed at original source line 55')
    if not equal(MY.then(CA).then(OY), TY):
        raise ValueError('Exact check failed at original source line 55')
    if not equal(MX.then(BX).then(OY), expected_B):
        raise ValueError('Exact check failed at original source line 55')
    kinds[kind] += 1
    out.append(dict(port=port, kind=kind, chosen_central_vector=cv, input_X=sx, input_Y=sy, final_X=hx, final_Y=ay, wrappers=wrappers))
    if port % 16 == 0:
        print('MAIN', port, '/', 112, flush=True)
(H / 'INTERSECTION153-ROUND3-MAIN-NORMALIZERS.json.gz').write_bytes(gzip.compress(json.dumps(out, sort_keys=True).encode(), mtime=0))
receipt = dict(status='PASS_H153_EXACT_TYPED_MAINS', ports=112, types=dict(kinds), monomial_normalizers=448, exact_block_identities=336, seconds=time.monotonic() - st)
(H / ('INTERSECTION153-ROUND3-MAIN-RECEIPT-PORTABLE.json' if _args.mains_only else 'INTERSECTION153-ROUND3-MAIN-RECEIPT.json')).write_text(json.dumps(receipt, indent=2))
print(json.dumps(receipt), flush=True)
if _args.mains_only:
    sys.exit(0)
pairs = {(e[3], e[4], e[5]) for p in z['programs'].values() for e in p if e[0] == 'climb'}
pairs |= {(e[2], e[3], e[4]) for p in z['programs'].values() for e in p if e[0] == 'center'}
pairs |= {(a, b, len(c['frames'][b]) - len(c['frames'][a])) for a, b in zip(c['start'][224:], c['final'][224:])}
pp = []
st2 = time.monotonic()
for i, (a, b, r) in enumerate(sorted(pairs)):
    physical = frame(a).adjoint().then(frame(b))
    ds = {}
    for d in ('forward', 'backward'):
        actual = P.conjugate(ce, physical) if d == 'backward' else physical
        rec = X.N.lower_exact(P, ce, actual)
        if not rec['rank'] == r:
            raise ValueError('Exact check failed at original source line 64')
        ds[d] = rec
    pp.append(dict(input=a, output=b, rank=r, recipes=ds))
    if i % 100 == 0:
        print('PAID_HELPER', i + 1, '/', len(pairs), flush=True)
(H / 'INTERSECTION153-ROUND3-PAID-HELPER-PHASES.json.gz').write_bytes(gzip.compress(json.dumps(pp, sort_keys=True).encode(), mtime=0))
receipt['status'] = 'PASS_H153_EXACT_TYPED_MAINS_AND_ALL_PAID_HELPER_PHASES'
receipt['paid_center_helper_pairs'] = len(pairs)
receipt['paid_helper_seconds'] = time.monotonic() - st2
(H / ('INTERSECTION153-ROUND3-MAIN-RECEIPT-PORTABLE.json' if _args.mains_only else 'INTERSECTION153-ROUND3-MAIN-RECEIPT.json')).write_text(json.dumps(receipt, indent=2))
print(json.dumps(receipt), flush=True)
