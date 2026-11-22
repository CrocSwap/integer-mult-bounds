"""Derive per-step frame changes of lane A's five stage-2 extractions (parent = previous step word), base from the realized
step words; check that the same records reproduce the extra provider's final L27 word."""
import gzip, json, copy, collections, sys
from fractions import Fraction as Q
from pathlib import Path
S = Path('S')
A = S / 'r14/agents/A-extract/out'
sys.path.insert(0, str(S / 'wt-r13pub2/research/paired-extension-normal45/vendor'))
import preload_move as pm
def read(p):
    b = Path(p).read_bytes(); return json.loads(gzip.decompress(b) if b[:2] == b'\x1f\x8b' else b)
HS = [226, 228, 230, 363, 395]
TR = [read(next(A.glob(f'L27-base-TRANSFORM-step{k}-h{h}.json'))) for k, h in enumerate(HS, 1)]
for k, h in enumerate(HS, 1):
    assert read(next(A.glob(f'L27-extra-TRANSFORM-step{k}-h{h}.json'))) == TR[k - 1]
R42 = json.load(open(A / 'R42.json')); R7 = json.load(open(A / 'R42R7.json'))
for t, r in zip(TR, R42 + R7):
    assert t['before'] == r['transform']['before'] and t['after'] == r['transform']['after'] and t['helper'] == r['transform']['helper'], 'realized transform == shipped'
def insert(word, t):
    h = t['helper']; x = copy.deepcopy(word); n = x['prelude_events']
    x['A'] = x['A'][:n] + copy.deepcopy(t['before']) + x['A'][n:]
    x['restore'] += copy.deepcopy(t['after'])
    x['helper_final'][str(h)] = list(pm.basis(t['after'][0][-1]))
    C = collections.defaultdict(dict)
    for g in x['compensation']:
        C[g[2]][g[1]] = C[g[2]].get(g[1], Q(0)) + Q(g[3], g[4])
    for g in reversed(t['before']):
        if g[0] == 'scale':
            C[g[1]] = {u: a * Q(g[2], g[3]) for u, a in C[g[1]].items()}
        else:
            u, s = g[1:3]
            for target, a in C[u].items():
                C[s][target] = C[s].get(target, Q(0)) + Q(g[3], g[4]) * a
    x['compensation'] = [['add', u, r, a.numerator, a.denominator, []] for r, col in sorted(C.items()) for u, a in sorted(col.items()) if a]
    return x
def finish(x):
    profile, inventory = pm.frame_report(x)
    x['report']['local_profile'], x['report']['width_inventory'] = profile, inventory
    z = copy.deepcopy(x); z['A'] = z['A'][z['prelude_events']:]
    x['cleanup'] = pm.derive_cleanup(z, set(map(int, x['helper_final'])))
    return x
out = []
words = [read(A / 'L22-base.json.gz')] + [read(A / f'R42-step{k}.json.gz') for k in (1, 2, 3)] + [read(A / f'R42R7-step{k}.json.gz') for k in (1, 2)]
assert words[-1] == read(A / 'L27-base.json.gz'), 'realized base step words end at L27-base'
for k, t in enumerate(TR, 1):
    par, ch = words[k - 1], words[k]
    x = insert(par, t)
    diff = sorted(key for key in x if x[key] != ch[key])
    fc = []
    for sec in ('A', 'B', 'restore'):
        assert len(x[sec]) == len(ch[sec]), (k, sec)
        for i, (g, c) in enumerate(zip(x[sec], ch[sec])):
            assert g[:-1] == c[:-1], (k, sec, i, g, c)
            if g[-1] != c[-1]:
                fc.append(dict(section=sec, index=i, gate=g[:-1], old_frame=g[-1], new_frame=c[-1]))
    hf = {h_: (x['helper_final'].get(h_), U) for h_, U in ch['helper_final'].items() if x['helper_final'].get(h_) != U}
    other = sorted(key for key in x if key not in ('A', 'B', 'restore', 'report', 'cleanup', 'helper_final') and x[key] != ch[key])
    print('step', k, t['helper'], 'normal', t['normal'], 'inputs', len(t['before']), 'outputs', len(t['after']), 'frame changes', len(fc),
          collections.Counter(e['section'] for e in fc), 'new-gate fc', sum(1 for e in fc if (e['section'] == 'restore' and e['index'] >= len(par['restore'])) or (e['section'] == 'A' and par['prelude_events'] <= e['index'] < par['prelude_events'] + len(t['before']))),
          'helper_final diffs', hf, 'other', other)
    y = copy.deepcopy(x)
    for e in fc: y[e['section']][e['index']][-1] = list(e['new_frame'])
    y = finish(y)
    assert y == ch, ('reproduce step', k, [key for key in ch if y[key] != ch[key]])
    out.append(dict(helper=t['helper'], normal=t['normal'], step=k, before=t['before'], after=t['after'], frame_changes=fc))
# extra: same records must reproduce L27-extra exactly from L22-extra
w = read(A / 'L22-extra.json.gz')
for k, t in enumerate(out, 1):
    x = insert(w, t)
    for e in t['frame_changes']:
        g = x[e['section']][e['index']]
        assert g[:-1] == e['gate'] and g[-1] == e['old_frame'], ('extra preimage', k, e)
        g[-1] = list(e['new_frame'])
    w = finish(x)
print('extra final == L27-extra:', w == read(A / 'L27-extra.json.gz'))
json.dump(out, open(S / 'r14pub-build/derive/stage2-transforms.json', 'w'), indent=1)
