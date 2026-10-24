"""Portable exact orthogonal-restriction builder. Apache-2.0; AI assistance."""
from pathlib import Path
from collections import Counter, defaultdict
from copy import deepcopy
import json, sys, ast, gzip, time, hashlib
import argparse, hashlib
_parser = argparse.ArgumentParser()
_parser.add_argument('--source-root', required=True, type=Path)
_args = _parser.parse_args()
H = Path(__file__).resolve().parent
R = _args.source_root.resolve()
_manifest = json.loads((H / 'SOURCE-CLOSURE-QUOTIENT-ROUND3.json').read_text(encoding='utf-8'))
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
ce = F.load(R / 'research/t74-native-fast/vendor/native/new/code/borrow/vendor/clifford/clifford_exact.py', 'h153ce')
P = F.load(R / 'research/kappa-function-composition/complex/prune_native.py', 'h153decode')
X = F.load(R / 'research/kappa-rebuild/complex/native_extensions.py', 'h153lower')
V = F.load(R / 'research/kappa-causal-continuation/buffer-borrowing/verify_buffers.py', 'h153rows')
_discovery = (H / 'QUOTIENT153-ROUND3-DISCOVERY-WORD.json').read_bytes()
if not hashlib.sha256(_discovery).hexdigest() == _manifest['discovery_sha256']:
    raise ValueError('Exact check failed at original source line 21')
z = json.loads(_discovery)
c = z['canonical']
pp = z['programs']
S = [F.span(b) for b in c['frames']]
pairs = defaultdict(set)

def basis(s):
    b = []
    cur = {0}
    for v in sorted(s):
        if v not in cur:
            b.append(v)
            cur |= {x ^ v for x in tuple(cur)}
    return b

def extend(b, s):
    for x in s:
        if ce.rank(b + [x]) > len(b):
            b.append(x)
    return b
for e in pp['forward']:
    if e[0] == 'warp':
        op, a, b = e[2:5]
        if op < 0:
            a, b = (b, a)
        pairs[abs(op)].add((a, b))
Gs = {}
newoutputs = {}
paid_retimings = []
allspace = set(range(512))
hh = next((s for s in S if len(s) == 256))
for op, ps in sorted(pairs.items()):
    small = sorted([(a, b) for a, b in ps if len(S[a]) < 256 or len(S[b]) < 256], key=lambda ab: len(S[ab[0]]))
    line = None
    if small and len(S[small[0][0]]) == len(S[small[0][1]]) == 2:
        line = small.pop(0)
    small = [(a, b) for a, b in small if len(S[a]) > 1 or len(S[b]) > 1]
    if not len(small) == 1:
        raise ValueError((op, small))
    a, b = small[0]
    A, B = (S[a], S[b])
    da, db = (len(c['frames'][a]), len(c['frames'][b]))
    if not da <= db:
        raise ValueError('Exact check failed at original source line 43')
    if da < db:
        if not (line is None and (db == da + 1)):
            raise ValueError(('retime',op,da,db,line))
        bb = basis(B)[:da]
        B = F.span(bb)
        labels = {s: i for i, s in enumerate(S)}
        if B not in labels:
            labels[B] = len(S)
            S.append(B)
            c['frames'].append(bb)
        newoutputs[op, a, b] = labels[B]
        paid_retimings.append(dict(operator=op, input=a, old_output=b, new_output=labels[B]))
    if line:
        av = next(iter(S[line[0]] - {0}))
        bv = next(iter(S[line[1]] - {0}))
        inside = av in A
        if not inside == (bv in B):
            raise ValueError((op, line, a, b))
        ib = [av] if inside else []
        ob = [bv] if inside else []
        extend(ib, basis(A))
        extend(ob, basis(B))
        if not inside:
            ib.append(av)
            ob.append(bv)
    else:
        ib = basis(A)
        ob = basis(B)
    if not len(ib) == len(ob):
        raise ValueError('Exact check failed at original source line 56')
    extend(ib, basis(hh))
    extend(ob, basis(hh))
    if not len(ib) == len(ob) == 8:
        raise ValueError('Exact check failed at original source line 56')
    extend(ib, [1 << i for i in range(9)])
    extend(ob, [1 << i for i in range(9)])
    if not len(ib) == len(ob) == 9:
        raise ValueError('Exact check failed at original source line 57')
    image = {0: 0}
    for av, bv in zip(ib, ob):
        image.update({x ^ av: y ^ bv for x, y in tuple(image.items())})
    if not len(image) == len(set(image.values())) == 512:
        raise ValueError('Exact check failed at original source line 60')
    for aa, bb in ps:
        target = S[newoutputs[op, aa, bb]] if (op, aa, bb) in newoutputs else S[bb]
        if not frozenset((image[x] for x in S[aa])) == target:
            raise ValueError((op, aa, bb))
    Gs[op] = [image[1 << i] for i in range(9)]
for w in c['warps']:
    w['G_columns'] = Gs[w['op']]
for d, p in pp.items():
    for e in p:
        if e[0] == 'warp' and (e[2], e[3], e[4]) in newoutputs:
            e[4] = newoutputs[e[2], e[3], e[4]]
pp = {d: _resynthesize(F, c, p) for d, p in pp.items()}
profiles = {}
formal = {}
for d, p in pp.items():
    rows, rec = X.literal_replay(V, c, p, d == 'backward')
    if not all((rows['L', r] == V.expected(('L', r), [], d == 'backward', False) for r in range(632))):
        raise ValueError('Exact check failed at original source line 71')
    profile = {int(k): v for k, v in rec['paid_profile'].items()}
    profiles[d] = profile
    reb = deepcopy(c)
    reb['R'] = 408
    reb['local_profile'] = profile
    V.replay(p, reb, [], d == 'backward', False)
    formal[d] = dict(rows=632, terms=sum((len(rows['L', r]) for r in range(632))), nonempty_words=sum((bool(w) for r in range(632) for v, w in rows['L', r])))
if not profiles['forward'] == profiles['backward']:
    raise ValueError('Exact check failed at original source line 72')
HH = Counter((len(c['frames'][b]) - len(c['frames'][a]) for a, b in zip(c['start'][224:], c['final'][224:])))
paid = profiles['forward']
mass = lambda a: sum((k * n for k, n in a.items()))
data = (json.dumps(dict(canonical=c, programs=pp), sort_keys=True, separators=(',', ':')) + '\n').encode()
(H / 'QUOTIENT153-ROUND3-ACTUAL-WORD.json.gz').write_bytes(gzip.compress(data, mtime=0))
out = dict(status='PASS_Q153_SHARED_MAPS_FORMAL_ENDPOINTS_PHASE_PENDING', paid=paid, helpers=dict(HH), local_deficit=mass(paid) - mass(HH), new_warp_outputs=paid_retimings, formal=formal, payload_sha256=hashlib.sha256(data).hexdigest())
(H / 'QUOTIENT153-ROUND3-ACTUAL-PROFILE.json').write_text(json.dumps(out, indent=2))
print(json.dumps(out, indent=2), flush=True)
fc = {}
KK = {}

def frame(i):
    if i not in fc:
        fc[i] = ce.canonical_frame(9, c['frames'][i])
    return fc[i]
for op, cols in Gs.items():
    G = ce.transpose(tuple(cols), 9)
    gi = ce.inv(G, 9)
    tr = ce.transpose(gi, 9)
    Q = tuple((1 << i ^ sum((ce.parity(a & b) << j for j, b in enumerate(tr))) for i, a in enumerate(tr)))
    KK[op] = ce.perm(9, G).then(ce.diag(9, Q))
classes = sorted({tuple(e[2:5]) for e in pp['forward'] if e[0] == 'warp'})
phase = []
st = time.monotonic()
for i, (op, a, b) in enumerate(classes):
    body = KK[abs(op)] if op > 0 else KK[abs(op)].adjoint()
    physical = frame(a).adjoint().then(body).then(frame(b))
    directions = {}
    for d in ('forward', 'backward'):
        actual = P.conjugate(ce, physical) if d == 'backward' else physical
        rec = X.N.lower_exact(P, ce, actual)
        if not rec['rank'] == 0:
            raise ValueError('Exact check failed at original source line 84')
        directions[d] = rec
    phase.append(dict(operator=op, input=a, output=b, recipes=directions))
    if i % 30 == 0:
        print('WARP_PHASE', i + 1, '/', len(classes), flush=True)
out['status'] = 'PASS_Q153_SHARED_MAPS_FORMAL_ENDPOINTS_ALL_WARP_PHASES'
out['warp_classes'] = len(classes)
out['warp_phase_seconds'] = time.monotonic() - st
(H / 'QUOTIENT153-ROUND3-ACTUAL-PROFILE.json').write_text(json.dumps(out, indent=2))
(H / 'QUOTIENT153-ROUND3-WARP-PHASES.json.gz').write_bytes(gzip.compress(json.dumps(phase, sort_keys=True).encode(), mtime=0))
print(out['status'], flush=True)
