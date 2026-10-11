from pathlib import Path
from collections import Counter,defaultdict
from fractions import Fraction as Q
import json,hashlib
O=Path(__file__).resolve().parent;R=O.parents[2];P=R/'experiments/architecture/collective-common-frame-bit/composed';w=json.load(open(P/'word.json'));F={int(k):v for k,v in json.load(open(P/'records/frames.json'))['frames'].items()}
def contained(a,b):return all(sum(Q(x)*Q(y) for x,y in zip(u,v))==0 for u in F[a]['B'] for v in F[b]['A'])
by=defaultdict(list)
for f,t,ss in w['B']:
 for s in ss:by[t].append((f,s,1))
groups=defaultdict(list)
for t,es in by.items():
 c=Counter()
 for i,(f,s,a) in enumerate(es):
  c[s]+=a
  if all(contained(f,g)for g,_,_ in es[i+1:]):groups[f,tuple(sorted(c.items()))].append((t,i+1))
nom=[]
for (f,cs),ts in groups.items():
 if len(ts)<2:continue
 for u,nu in ts:
  for d,nd in ts:
   if u>=d:continue
   # Independent symbolic proof: targets, D0 response, scatter response and every helper prefix treated as arbitrary variables.
   def add(a,b,k):
    for x,v in b.items():
     a[x]=a.get(x,0)+k*v
     if not a[x]:del a[x]
   U={'yu':1,'du':1,'su':1};D={'yd':1,'dd':1,'sd':1};old=dict(U);prefix={('h',s):a for s,a in cs};add(old,prefix,1)
   new=dict(U);add(new,D,-1);add(D,prefix,1);add(new,D,1);assert new==old
   # At zero, negative donor D0 is included by modifying receiver compensation; negative donor scatter comes from existing retained centre sources.
   sc=Counter(w['scatter'][u-120]);sc.subtract(w['scatter'][d-120]);sc={k:v for k,v in sc.items()if v}
   scatter_units=sum(abs(v)for v in sc.values());oldscatter=len(w['scatter'][u-120]);delta=2+scatter_units-oldscatter-nu
   nom.append(dict(receiver=u,donor=d,frame=f,rank=F[f]['dim'],prefix_terms=nu,donor_prefix_terms=nd,helper_coefficients=list(cs),scatter_new=sc,clean_add_unit_delta_excluding_rebuilt_compensation=delta,exact_signed_arbitrary_target_and_helper_symbolic_identity=True))
r={'status':'EXACT_SIGNED_PREFIX_CANDIDATES_ONLY','source_word_sha256':hashlib.sha256((P/'word.json').read_bytes()).hexdigest(),'count':len(nom),'candidates':nom,'scope':'Equality uses exact integer raw helper coefficients, not F2. Symbolic test allows arbitrary target, D0, retained scatter and helper dirt. Full producer compilation, receiver K reconstruction, acyclic selection, physical target-as-source chart and reflected paid invoice remain required.'}
(O/'TARGET-PREFIX-SIGNED.json').write_text(json.dumps(r,indent=2)+'\n');print('candidates',len(nom));print(Counter((n['rank'],n['prefix_terms'])for n in nom));print('bestclean',min((n['clean_add_unit_delta_excluding_rebuilt_compensation']for n in nom),default=None))
