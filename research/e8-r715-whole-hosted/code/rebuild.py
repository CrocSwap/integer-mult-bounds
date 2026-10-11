"""Exact reconstruction from the source-pinned PR463 R715 word.
No optimizer is run: verify the selected kernel and disjoint target mixing.
Chafreaky with OpenAI Codex assistance; upstream credits in NOTICE.md. Apache-2.0.
"""
import copy,gzip,hashlib,json,sys
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parent/'e8-r740-replica32/code'))
sys.path.insert(0,str(ROOT.parent/'r740-hosted-rank149/code'))
from e8core import replay
from hosted_kernel import kernel
from stages import retime
ld=lambda p:json.loads(gzip.decompress(p.read_bytes())) if p.suffix=='.gz' else json.loads(p.read_text())
base=ld(ROOT/'upstream463/R715_FP_final.json.gz');selected=ld(ROOT/'data/kernel.json')
assert base['R']==715 and base['v']==120 and base['h']==8
before=replay(base,span_mode='z');assert not before['viol']
c,entries,rank,donors=kernel(base,selected)
assert (entries,rank)==(109,120) and c==ld(ROOT/'data/kernel-word.json.gz')
mid=replay(c,span_mode='z');assert not mid['viol']
mix=ld(ROOT/'data/mixing.json');expected=ld(ROOT/'data/word.json.gz')
frames=ld(Path(sys.argv[1])/'frames.json')['frames'];dim={int(i):z['dim'] for i,z in frames.items()}
v,h=c['v'],c['h'];F=list(map(frozenset,c['frames']));zero=F.index(frozenset());assert zero==0
assert len(mix)==56 and len({u for u,w,G in mix})==56 and len({w for u,w,G in mix})==56
assert not {u for u,w,G in mix}&{w for u,w,G in mix}
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
for u,donor,G in mix:
 assert v<=u<2*v and v<=donor<2*v and u!=donor and G in [f for i,f,ss in seq[donor]]
 assert prefix(u,G) and prefix(u,G)==prefix(donor,G)
 assert F[G]<=F[c['final'][u]]
 assert all(F[G]<=F[f] for i,f,ss in seq[u] if not F[f]<=F[G])
w=copy.deepcopy(c);w['D']+=[[zero,u,[donor]] for u,donor,G in mix]
for u,donor,G in mix:w['scatter'][u-v]=sorted(set(c['scatter'][u-v])^set(c['scatter'][donor-v]))
drop={i for u,donor,G in mix for i,f,ss in seq[u] if F[f]<=F[G]}
keep=[g for i,g in enumerate(c['B']) if i not in drop];w['B']=[]
for k in range(h+1):
 w['B']+=[g for g in keep if dim[g[0]]==k]
 w['B']+=[[G,u,[donor]] for u,donor,G in mix if dim[G]==k]
w['target_mix']=dict(rule='y_u += y_w at frame G (after w reaches G); frame-0 preconditioner y_u += y_w; scatter_u ^= scatter_w',receivers=mix)
assert w==ld(ROOT/'data/mixed-word.json.gz') and Counter(dim[G] for u,donor,G in mix)==Counter({6:56})
for ph in ('D','A','B','C'):w[ph]=[[f,d,[s]] for f,d,ss in w[ph] for s in ss]
single=ld(ROOT/'data/single-retiming.json');paired=ld(ROOT/'data/pair-retiming.json')
assert len(single)==60 and all(x[0]=='A' for x in single)
assert len(paired)==28 and all(x[0]=='B' for x in paired)
w=retime(w,single)
# Bind the transferred pair moves to PR467's actual operands and frames.
up=ld(ROOT/'upstream467/word.json');up_moves=ld(ROOT/'upstream467/retiming.json')['changes'];bound=[]
for batch in up_moves:
 if len(batch['changes'])!=2:continue
 for ph,i,old,new in batch['changes']:
  assert w[ph][i][1:]==up[ph][i][1:] and w['frames'][w[ph][i][0]]==up['frames'][old]
  bound.append([ph,i,up['frames'][old],up['frames'][new]])
assert paired==bound
w=retime(w,paired);assert w==expected
after=replay(w,span_mode='z');assert not after['viol'] and after['n']==955
rejected=[]
for name,mutate in [('retained row pivot',lambda s:s[0].__setitem__(1,base['ret'][0])),('duplicate pivot',lambda s:s.append(copy.deepcopy(s[0])))]:
 bad=copy.deepcopy(selected);mutate(bad)
 try:kernel(base,bad)
 except AssertionError:rejected.append(name)
 else:raise AssertionError('accepted '+name)
bad=copy.deepcopy(w);bad['A'][0][2].pop()
try:r=replay(bad,span_mode='z')
except AssertionError:pass
else:assert r['viol']
rejected.append('omitted response correction')
print(json.dumps(dict(status='PASS_EXACT_R715_KERNEL_AND_MIXING_REBUILD',kernel_entries=entries,entrance_rank=rank,donor_slots=donors,
 receivers=56,donors=56,disjoint_mixing=True,single_retimings=60,paired_retimings=14,local_columns=955,local_profile=dict(sorted(after['H'].items())),
 base_and_kernel_integer_source_spans=True,final_integer_source_spans=True,mutations_rejected=rejected,
 canonical_word_sha256=hashlib.sha256(json.dumps(w,sort_keys=True,separators=(',',':')).encode()).hexdigest()),sort_keys=True))
