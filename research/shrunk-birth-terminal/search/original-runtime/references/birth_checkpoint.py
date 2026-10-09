"""Explicit adapter from PR125 virtual compiler to PR124 birth-read interface.

Source graph/matching/frames and their credits remain in the producer files.
Only representation changes here; all represented identities are rechecked.
"""
import hashlib
import json
import pickle


def basis(rows):
    piv = {}
    for x in rows:
        for p in sorted(piv, reverse=True):
            if x >> p & 1:
                x ^= piv[p]
        if x:
            p = x.bit_length()-1
            for q in piv:
                if piv[q] >> p & 1:
                    piv[q] ^= x
            piv[p] = x
    return tuple(piv[p] for p in sorted(piv, reverse=True))


def export_checkpoint(d, here):
    n, v, R = (d[k] for k in ('n', 'v', 'Rr'))
    args = [tuple(a) if a[0] else () for a in d['args']]
    ops = []
    for o in d['ops']:
        if o[0] == 'src':
            ops.append((0, o[1], o[2], -1))
        else:
            ops.append((1 if o[0] == 'add' else 2, *o[1:]))
    support = [0]*n
    for i in range(v):
        support[i+1] = 1 << i
    for x in d['order']:
        if args[x]:
            a, b = args[x]
            assert not support[a] & support[b]
            support[x] = support[a] | support[b]
    values = [0]*R
    for op, s, t, x in ops:
        if op == 0:
            assert values[s] == 0
            values[s] = 1 << (t-1)
        elif op == 1:
            assert not values[s] & values[t]
            values[s] |= values[t]
            assert values[s] == support[x]
        else:
            assert values[t] == 0
            values[t] = values[s]
            assert values[t] == support[x]
    assert all(values[s] == support[d['roots'][j]] for s, j in d['role_root'].items())
    g = dict(h=d['h'], v=v, args=args, core=list(d['core']), cover=list(d['cover']),
             rank=list(d['ranks']), kind=list(d['types']), active=d['order'],
             roots=list(d['roots']), targets=[-1 if t is None else t for t in d['target']],
             support=support, holds=d['holds'], first=d['first_node'], ops=ops,
             terminal=d['role_root'], last=[d['last'].get(s, -1) for s in range(R)],
             phase=d['Anc'], touched=d['touched'], center_roles=d['centre_roles'],
             U=[basis(d['U'].get(x, ())) for x in range(n)], tm=d['tmask'],
             reach=[sum(1 << t for t in ts) for ts in d['reach']], reach_all=d['reach_all'],
             placed={s:basis(F) for s,F in d['placed'].items()}, bytarget=dict(d['byT2']),
             histogram=dict(d['z']), chain_dims=[ds[:-1] for ds in d['chain_dims']],
             base_profile=d['out'])
    raw = pickle.dumps(g, protocol=4)
    (here/'FRAMES.pkl').write_bytes(raw)
    receipt = dict(status='PASS new-composition intermediate adapter and exact full input supports',
                   roles=R, operations=len(ops), deferred=len(g['placed']),
                   shrunk_frames=d['shrunk'], checkpoint_sha256=hashlib.sha256(raw).hexdigest())
    (here/'ADAPTER.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(receipt), flush=True)
