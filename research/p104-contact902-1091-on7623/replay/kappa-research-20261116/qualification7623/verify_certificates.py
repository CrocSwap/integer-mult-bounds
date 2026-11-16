"""Standalone verifier for certs_*.json (does NOT import clearform or the builder).
Re-replays the word over Q; at each CLEAR checks: field/event match, erased row matches the recorded row,
every certificate key is a live register other than the cleared one, and sum c_k row_k == erased row exactly.
Negative controls: one corrupted coefficient and one wrong field must be rejected.
usage: verify_certs.py WORD.json.gz CERTS.json
"""
import copy, gzip, hashlib, json, sys
from fractions import Fraction as Q

def run(W, certs):
    n, N = W['public'], W['public'] + W['owned_fields']
    rows = [{r: Q(1)} if r < n else {} for r in range(N)]
    live = set(range(n)); j = 0; bad = []
    for i, e in enumerate(W['program']):
        op, r = e[0], e[1]
        if op == 'INIT':
            live.add(r); rows[r] = {}
        elif op == 'CLEAR':
            c = certs[j]; j += 1
            erased = {k: v for k, v in rows[r].items()}
            rec = {} if c['erased'] is None else {int(k): Q(v) for k, v in c['erased'].items()}
            cert = {int(k): Q(v) for k, v in (c['certificate'] or {}).items()}
            ok = c['event'] == i and c['field'] == r and rec == erased and c['certificate'] is not None
            ok = ok and all(k in live and k != r for k in cert)
            s = {}
            for k, cf in cert.items():
                for t, v in rows[k].items():
                    s[t] = s.get(t, 0) + cf * v
            ok = ok and {t: v for t, v in s.items() if v} == erased
            if not ok: bad.append(c['clear_index'])
            rows[r] = {}; live.discard(r)
        elif op == 'SCALE':
            q = Q(e[2]); rows[r] = {k: v * q for k, v in rows[r].items()}
        elif op in ('ADD', 'COPY'):
            q = Q(e[3]); R = rows[r]
            for k, v in rows[e[2]].items():
                nv = R.get(k, 0) + q * v
                if nv: R[k] = nv
                else: R.pop(k, None)
    return j, bad

wp, cp = sys.argv[1:3]
raw = open(wp, 'rb').read(); W = json.loads(gzip.decompress(raw)); D = json.load(open(cp))
assert D['summary']['sha256'] == hashlib.sha256(raw).hexdigest(), 'certificate file is for a different word'
cnt, bad = run(W, D['clears'])
print(f'word sha256={D["summary"]["sha256"][:16]} CLEARs checked={cnt} failures={bad}')
X = copy.deepcopy(D['clears'])
k = next(i for i, c in enumerate(X) if c['certificate'])
f0 = next(iter(X[k]['certificate'])); X[k]['certificate'][f0] = str(Q(X[k]['certificate'][f0]) + 1)
_, b1 = run(W, X)
Y = copy.deepcopy(D['clears']); kk = next(i for i, c in enumerate(Y) if c['certificate'] and len(c['certificate']) > 0)
k2 = next(iter(Y[kk]['certificate'])); v = Y[kk]['certificate'].pop(k2); Y[kk]['certificate'][str(Y[kk]['field'])] = v
_, b2 = run(W, Y)
print(f'control corrupted coefficient (CLEAR #{k}) rejected: {k in b1}; control cleared-field-as-term (CLEAR #{kk}) rejected: {kk in b2}')
ok = cnt == len(D['clears']) == 180 and not bad and k in b1 and kk in b2
print('PASS_CLEAR_CERTIFICATES' if ok else 'FAIL_CLEAR_CERTIFICATES')
sys.exit(0 if ok else 1)
