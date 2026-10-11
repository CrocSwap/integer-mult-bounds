"""Rebuild the frozen disjoint target-prefix selection using exact set checks.
Discovery and construction lineage: DreamingOfClouds PR450 with Claude.
Frozen exact reconstruction: chafreaky with OpenAI Codex. Apache-2.0.
"""
import copy,gzip,hashlib,json,sys
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];PARENT=ROOT.parent/'r740-hosted-rank149'
ld=lambda p:json.loads(gzip.decompress(p.read_bytes())) if p.suffix=='.gz' else json.loads(p.read_text())
c=ld(PARENT/'data/word.json.gz');expected=ld(ROOT/'data/word.json.gz');selected=ld(ROOT/'data/selection.json')
frames=ld(Path(sys.argv[1])/'frames.json')['frames'];dim={int(i):z['dim'] for i,z in frames.items()}
v,h=c['v'],c['h'];F=list(map(frozenset,c['frames']));zero=F.index(frozenset());assert zero==0
assert len(selected)==46 and len({u for u,w,G in selected})==46 and len({w for u,w,G in selected})==46
assert not {u for u,w,G in selected}&{w for u,w,G in selected},'the released selection has disjoint receivers and donors'
assert not c.get('source_basis_gates',0)
assert all(v<=d<2*v and all(s>=2*v for s in ss) for f,d,ss in c['B'])
assert not any(v<=s<2*v for ph in ('D','A','C') for f,d,ss in c[ph] for s in ss)
seq=defaultdict(list)
for i,(f,d,ss) in enumerate(c['B']):seq[d].append((i,f,ss))
def prefix(t,G):
 parity=set()
 for i,f,ss in seq[t]:
  if F[f]<=F[G]:
   for s in ss:parity.symmetric_difference_update([s])
 return parity
for u,w,G in selected:
 assert v<=u<2*v and v<=w<2*v and u!=w and G in [f for i,f,ss in seq[w]]
 assert prefix(u,G) and prefix(u,G)==prefix(w,G)
 assert F[G]<=F[c['final'][u]]
 assert all(F[G]<=F[f] for i,f,ss in seq[u] if not F[f]<=F[G])
w=copy.deepcopy(c);w['D']+= [[zero,u,[donor]] for u,donor,G in selected]
for u,donor,G in selected:w['scatter'][u-v]=sorted(set(c['scatter'][u-v])^set(c['scatter'][donor-v]))
drop={i for u,donor,G in selected for i,f,ss in seq[u] if F[f]<=F[G]}
keep=[g for i,g in enumerate(c['B']) if i not in drop]
w['B']=[]
for k in range(h+1):
 w['B'] += [g for g in keep if dim[g[0]]==k]
 w['B'] += [[G,u,[donor]] for u,donor,G in selected if dim[G]==k]
w['target_mix']=dict(rule='y_u += y_w at frame G (after w reaches G); frame-0 preconditioner y_u += y_w; scatter_u ^= scatter_w',receivers=selected)
assert w==expected,'frozen word differs from the exact selected construction'
assert all(w[k]==c[k] for k in c if k not in ('D','B','scatter'))
assert Counter(dim[G] for u,donor,G in selected)==Counter({6:42,5:4})
print(json.dumps(dict(status='PASS_EXACT_DISJOINT_TARGET_MIX_REBUILD',receivers=46,donors=46,disjoint=True,mixing_frame_dimensions={6:42,5:4},
 canonical_word_sha256=hashlib.sha256(json.dumps(w,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
 changed_phases=['D','scatter','B'],geometry_and_residuals_unchanged=True),sort_keys=True))
