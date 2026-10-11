"""Deterministic retiming witness: apply a frozen list of gate frame changes to a bitE8/1 word and re-list B by frame dimension.
usage: retime_apply.py IN_WORD WITNESS.json OUT_WORD [--unchecked]   (--unchecked: negative controls only, skips the output hash)
       retime_apply.py --make BASE_WORD RETIMED_WORD WITNESS.json
Every ordered scalar ADD (destination and sources) is identical; only frames change, all inside the pinned frame family."""
import gzip, json, hashlib, sys
def load(p): return json.load(gzip.open(p, 'rt') if p.endswith('.gz') else open(p))
def dump(w, p):
    raw = json.dumps(w, sort_keys=True, separators=(',', ':')).encode()
    (gzip.open(p, 'wb') if p.endswith('.gz') else open(p, 'wb')).write(raw)
def content(w): return hashlib.sha256(json.dumps(w, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
def dimof(w):
    from fractions import Fraction as Fr
    def rank(idx):
        rows = []
        for i in idx:
            x = [Fr(a) for a in w['lines'][i]]
            for r in rows:
                p = next(k for k in range(len(r)) if r[k])
                if x[p]: f = x[p] / r[p]; x = [a - f * b for a, b in zip(x, r)]
            if any(x): rows.append(x)
        return len(rows)
    return [rank(f) for f in w['frames']]
def apply(w, sel, unchecked=False):
    assert content(w) == sel['input_sha256'], 'input word differs from the witness input'
    out = json.loads(json.dumps(w)); seen = set()
    for ph, i, old, new in sel['gates']:
        assert ph in ('A', 'B') and (ph, i) not in seen; seen.add((ph, i))
        g = out[ph][i]; assert g[0] == old, (ph, i, g[0], old)
        assert 0 <= new < len(out['frames']); g[0] = new
    assert len(seen) == sel['count']
    dim = dimof(out); out['B'] = sorted(out['B'], key=lambda g: dim[g[0]])   # stable re-listing by frame dimension
    for ph in 'DABC':
        assert len(out[ph]) == len(w[ph])
        if ph != 'B': assert all(g[1:] == h[1:] for g, h in zip(out[ph], w[ph]))
    assert sorted(map(json.dumps, (g[1:] for g in out['B']))) == sorted(map(json.dumps, (g[1:] for g in w['B'])))
    assert unchecked or content(out) == sel['output_sha256'], 'output differs from the witness'
    return out
if __name__ == '__main__':
    if sys.argv[1] == '--make':
        base, ret = load(sys.argv[2]), load(sys.argv[3])
        gates = []
        for ph in 'AB':
            # match B gates by (dest, sources) multiset order: the retimed B is re-listed, so map by scalar content in original order
            if ph == 'A':
                for i, (g, h) in enumerate(zip(base['A'], ret['A'])):
                    assert g[1:] == h[1:]
                    if g[0] != h[0]: gates.append(['A', i, g[0], h[0]])
            else:
                from collections import defaultdict, deque
                pool = defaultdict(deque)
                for h in ret['B']: pool[json.dumps(h[1:])].append(h[0])
                for i, g in enumerate(base['B']):
                    nf = pool[json.dumps(g[1:])].popleft()
                    if nf != g[0]: gates.append(['B', i, g[0], nf])
        sel = dict(input_sha256=content(base), output_sha256=content(ret), count=len(gates), gates=gates,
                   rule='frame changes only, inside the pinned family; B re-listed by frame dimension after the changes')
        json.dump(sel, open(sys.argv[4], 'w'), indent=0)
        print('changes', len(gates), 'A', sum(1 for g in gates if g[0] == 'A'), 'B', sum(1 for g in gates if g[0] == 'B'))
        out = apply(base, sel); assert content(out) == sel['output_sha256']; print('witness replays: OK')
    else:
        out = apply(load(sys.argv[1]), load(sys.argv[2]), unchecked='--unchecked' in sys.argv[4:]); dump(out, sys.argv[3]); print('ok', content(out))
