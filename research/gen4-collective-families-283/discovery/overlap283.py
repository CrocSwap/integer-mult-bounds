"""Helpers touched by PR #283's transformations (original gen4 numbering) and overlaps with our families / the 424 pairs."""
import json, sys, collections
R, SEL424, OUT = sys.argv[1], sys.argv[2], sys.argv[3]; sels=sys.argv[4:]
k=json.load(open(R+'/inputs/kernel-original.json')); rm=json.load(open(R+'/inputs/kernel-remapped.json'))
dropped={(d['old_pivot'] if 'old_pivot' in d else d['pivot'], d['cut']) for d in rm['dropped_rows']}
kept=[c for c in k['candidates'] if (c['pivot'],c['cut']) not in dropped]
print('kernel-original candidates', len(k['candidates']), 'kept after sink remap', len(kept), 'kinds', collections.Counter(c['kind'] for c in kept))
print('  family sizes (|roles|)', sorted(collections.Counter(len(c['roles']) for c in kept).items()), 'entrance dims', sorted(collections.Counter(c['dim'] for c in kept).items()), 'total entrance rank', sum(c['dim'] for c in kept), 'cuts', collections.Counter(c['cut'] for c in kept))
H_kpiv={c['pivot'] for c in kept}; H_kroles={r for c in kept for r in c['roles']}
H_sink={s['physical_role'] for s in json.load(open(R+'/inputs/sinks.json'))['candidates']}
H_tr={e['stream'] for e in json.load(open(R+'/inputs/entrances60.json'))['entries']}
ret=json.load(open(R+'/inputs/retiming.json'))['entries']; H_ret={x for e in ret for x in e['scalar'][:2] if x>=3520}
print('helpers: kernel pivots', len(H_kpiv), 'kernel roles', len(H_kroles), 'sinks', len(H_sink), 'transported (all 60 candidates)', len(H_tr), 'retimed-gate helper operands', len(H_ret))
H283=H_kroles|H_sink|H_tr
json.dump(dict(kernel_roles=sorted(H_kroles),kernel_pivots=sorted(H_kpiv),sinks=sorted(H_sink),transported60=sorted(H_tr),retimed_operands=sorted(H_ret),all=sorted(H283|H_ret)), open(OUT,'w'))
p424=json.load(open(SEL424))['pairs']; P424={p['a'] for p in p424}|{p['b'] for p in p424}; piv424={p['a'] for p in p424}
print('424 pairs: helpers', len(P424), 'overlap with #283 kernel roles', len(P424&H_kroles), 'pivot-pivot', len(piv424&H_kpiv), 'with sinks', len(P424&H_sink), 'with transported', len(P424&H_tr), 'with retimed operands', len(P424&H_ret), 'pairs fully disjoint from #283 helpers', sum(1 for p in p424 if not ({p['a'],p['b']}&(H283|H_ret))))
for s in sels:
    sel=json.load(open(s)); ents=[(e['a'],[e['b']],e['kind'] if 'kind' in e else 'pair') for e in sel['pairs']]+[(e['pivot'],e['donors'],e['kind']) for e in sel['families']]
    M={x for p,ds,_ in ents for x in [p]+ds}; PV={p for p,_,_ in ents}
    dis=[(p,ds,kd) for p,ds,kd in ents if not (({p}|set(ds))&(H283|H_ret))]
    print(s.split('/')[-1], 'entries', len(ents), 'helpers', len(M), '| overlap with #283: kernel roles', len(M&H_kroles), 'pivot-pivot', len(PV&H_kpiv), 'sinks', len(M&H_sink), 'transported', len(M&H_tr), 'retimed operands', len(M&H_ret), '| entries disjoint from all #283 helpers', len(dis), collections.Counter(kd for _,_,kd in dis), '| overlap with 424 pairs helpers', len(M&P424))
