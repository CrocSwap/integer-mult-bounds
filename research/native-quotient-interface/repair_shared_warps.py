"""Portable exact typed quotient checker. Apache-2.0; substantial AI assistance."""
from pathlib import Path
from collections import Counter, defaultdict
from copy import deepcopy
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
base, old, *_ = J.construct()
ce = F.load(R / 'research/t74-native-fast/vendor/native/new/code/borrow/vendor/clifford/clifford_exact.py', 'qfixed_ce')
P = F.load(R / 'research/kappa-function-composition/complex/prune_native.py', 'qfixed_decode')
X = F.load(R / 'research/kappa-rebuild/complex/native_extensions.py', 'qfixed_lower')
V = F.load(R / 'research/kappa-causal-continuation/buffer-borrowing/verify_buffers.py', 'qfixed_rows')
q = json.loads(gzip.decompress((H / 'QUOTIENT-WORD.json.gz').read_bytes()))
rawprograms = json.loads(gzip.decompress((H / 'QUOTIENT-PROGRAMS.json.gz').read_bytes()))
c = deepcopy(base)
for k in ('frames', 'start', 'final'):
    c[k] = q[k]
spaces = [F.span(b) for b in c['frames']]
pairs = defaultdict(set)
for e in rawprograms['forward']:
    if e[0] == 'warp':
        op, a, b = e[2:5]
        if op < 0:
            a, b = (b, a)
        if len(spaces[a]) not in (1, 512):
            pairs[abs(op)].add((a, b))

def basis(s):
    out = []
    cur = {0}
    for x in sorted(s):
        if x not in cur:
            out.append(x)
            cur |= {v ^ x for v in tuple(cur)}
    return out

def independent_append(B, x):
    if ce.rank(B + [x]) > len(B):
        B.append(x)
Gs = {}
checks = []
for op, ps in sorted(pairs.items()):
    ps = sorted(ps, key=lambda ab: len(spaces[ab[0]]))
    small = [ab for ab in ps if len(spaces[ab[0]]) < 256]
    if not len(small) in (1, 2):
        raise ValueError('Exact check failed at original source line 39')
    if len(small) == 2:
        (a, b), (A, B) = small
        if not len(spaces[a]) == len(spaces[b]) == 2:
            raise ValueError('Exact check failed at original source line 41')
        av = next(iter(spaces[a] - {0}))
        bv = next(iter(spaces[b] - {0}))
        ain = av in spaces[A]
        if not ain == (bv in spaces[B]):
            raise ValueError('Exact check failed at original source line 42')
        if ain:
            ib = [av]
            ob = [bv]
        else:
            ib = []
            ob = []
        for x in basis(spaces[A]):
            independent_append(ib, x)
        for x in basis(spaces[B]):
            independent_append(ob, x)
        if not ain:
            ib.append(av)
            ob.append(bv)
    else:
        a, b = small[0]
        ib = basis(spaces[a])
        ob = basis(spaces[b])
    if not len(ib) == len(ob):
        raise ValueError('Exact check failed at original source line 50')
    for i in range(8):
        independent_append(ib, 1 << i)
        independent_append(ob, 1 << i)
    if not len(ib) == len(ob) == 8:
        raise ValueError('Exact check failed at original source line 52')
    ib.append(256)
    ob.append(256)
    image = {0: 0}
    for a, b in zip(ib, ob):
        image.update({x ^ a: y ^ b for x, y in tuple(image.items())})
    if not len(image) == len(set(image.values())) == 512:
        raise ValueError('Exact check failed at original source line 55')
    for a, b in ps:
        if not frozenset((image[x] for x in spaces[a])) == spaces[b]:
            raise ValueError('Exact check failed at original source line 56')
    Gs[op] = [image[1 << i] for i in range(9)]
    checks.append(dict(operator=op, declared_pairs=len(ps), all_512_columns_bijective=True, all_shared_frame_pairs=True))
if not set(Gs) == set(range(1, 73)):
    raise ValueError('Exact check failed at original source line 59')
for w in c['warps']:
    w['G_columns'] = Gs[w['op']]
programs = {d: F.synthesize(c, p) for d, p in rawprograms.items()}
profiles = {}
literal = {}
formal = {}
for d, p in programs.items():
    rows, rec = X.literal_replay(V, c, p, d == 'backward')
    if not all((rows['L', r] == V.expected(('L', r), [], d == 'backward', False) for r in range(632))):
        raise ValueError('Exact check failed at original source line 63')
    profiles[d] = {int(k): n for k, n in rec['paid_profile'].items()}
    rebound = deepcopy(c)
    rebound['local_profile'] = profiles[d]
    V.replay(p, rebound, [], d == 'backward', False)
    literal[d] = rec
    rows_items = [(r, rows['L', r]) for r in range(632)]
    nonempty = sum((bool(word) for r, row in rows_items for variable, word in row))
    if not nonempty == 0:
        raise ValueError('Exact check failed at original source line 66')
    formal[d] = dict(persistent_rows=632, exact_formal_terms=sum((len(row) for r, row in rows_items)), nonempty_warp_words=nonempty, owned_C_terms=len(rows['C', 0]), coefficient_ring='Q', operator_ring='free group algebra on shared native symbols; no matrix substitution', endpoint='identity on 408 helpers and original signed identity shear on 224 main logical fields')
if not profiles['forward'] == profiles['backward'] == {1: 2177, 2: 424, 3: 389, 4: 147, 5: 50, 8: 8}:
    raise ValueError('Exact check failed at original source line 68')
bad = deepcopy(programs['forward'])
next((e for e in bad if e[0] == 'warp'))[2] = 999
_badrows, _ = X.literal_replay(V, c, bad, False)
if not any((_badrows['L', r] != V.expected(('L', r), [], False, False) for r in range(632))):
    raise ValueError('Exact check failed at original source line 71')
formal['shared_symbol_negative_control'] = dict(changed_one_occurrence_to_fresh_symbol=True, rejected_by_nonzero_exact_endpoint_difference=True)
framecache = {}
K = {}

def frame(a):
    if a not in framecache:
        framecache[a] = ce.canonical_frame(9, c['frames'][a])
    return framecache[a]
for op, cols in Gs.items():
    G = ce.transpose(tuple(cols), 9)
    gi = ce.inv(G, 9)
    tr = ce.transpose(gi, 9)
    Q = tuple((1 << i ^ sum((ce.parity(a & b) << j for j, b in enumerate(tr))) for i, a in enumerate(tr)))
    K[op] = ce.perm(9, G).then(ce.diag(9, Q))
classes = sorted({tuple(e[2:5]) for e in programs['forward'] if e[0] == 'warp'})
phase = []
st = time.monotonic()
for i, (op, a, b) in enumerate(classes):
    body = K[abs(op)] if op > 0 else K[abs(op)].adjoint()
    actual = frame(a).adjoint().then(body).then(frame(b))
    ds = {}
    for d in ('forward', 'backward'):
        physical = P.conjugate(ce, actual) if d == 'backward' else actual
        rec = X.N.lower_exact(P, ce, physical)
        if not (rec['rank'] == 0 and rec['right'] is None):
            raise ValueError('Exact check failed at original source line 84')
        ds[d] = rec
    phase.append(dict(operator=op, input=a, output=b, recipes=ds))
    if i % 30 == 0:
        print('PHASE', i + 1, '/', len(classes), flush=True)
payload = {'canonical': c, 'programs': programs}
data = (json.dumps(payload, sort_keys=True, separators=(',', ':')) + '\n').encode()
(H / 'REPAIRED-WARP-WORD.json.gz').write_bytes(gzip.compress(data, mtime=0))
out = dict(status='PASS_SHARED_MAP_QUOTIENT_WARPS_ONLY_CANONICAL_MAIN_STILL_OPEN', paid=profiles, shared_maps=checks, actual_warp_classes=len(classes), both_orientation_absolute_phase=True, canonical_payload_sha256=sha256(data).hexdigest(), phase_seconds=time.monotonic() - st, formal_cancellation=formal, scope='Changed supplier main charts retained; not a canonical supplier or kappa certificate')
(H / 'REPAIRED-WARP-RECEIPT.json').write_text(json.dumps(out, indent=2))
(H / 'REPAIRED-WARP-PHASES.json.gz').write_bytes(gzip.compress(json.dumps(phase, sort_keys=True).encode(), mtime=0))
print(json.dumps({k: v for k, v in out.items() if k != 'shared_maps'}, indent=2))
