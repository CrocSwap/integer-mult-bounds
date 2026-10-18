from pathlib import Path
import itertools, json, random
import numpy as np
OUT=Path(__file__).resolve().parent

def require(x,m):
 if not x: raise ValueError(m)

def gf2rank(vs):
 b={}
 for v in vs:
  v=int(v)
  while v:
   k=v.bit_length()-1
   if k in b:v^=b[k]
   else:b[k]=v;break
 return len(b)

ix=np.array(list(itertools.combinations(range(14),4)),dtype=np.int16)
lut=np.array([gf2rank((a,b,c,d))==4 for a,b,c,d in itertools.product(range(16),repeat=4)],dtype=np.uint8).reshape((16,)*4)
rng=random.Random(148)
basis={}; chosen=[]; lead=[]
for trial in range(3000):
 cols=list(range(1,16));rng.shuffle(cols)
 cs=np.array(cols[:14],dtype=np.int16)
 bits=lut[cs[ix[:,0]],cs[ix[:,1]],cs[ix[:,2]],cs[ix[:,3]]]
 vec=int.from_bytes(np.packbits(bits,bitorder='little').tobytes(),'little')
 gens=[sum(((int(c)>>j)&1)<<i for i,c in enumerate(cs)) for j in range(4)]
 H=[0]
 for g in gens:H += [v^g for v in H]
 require(all(h==0 or h.bit_count() in (7,8)for h in H),'illegal clique')
 chosen.append(H);lead.append(vec)
 trace=1<<trial;v=vec
 while v:
  p=v.bit_length()-1
  if p in basis:
   vv,tt=basis[p];v^=vv;trace^=tt
  else:
   basis[p]=(v,trace);break
 if v==0 and trace.bit_count()%2:
  ids=[i for i in range(trial+1)if trace>>i&1]
  kernel=set()
  for i in ids:kernel.symmetric_difference_update(chosen[i])
  require(0 in kernel,'diagonal')
  require(all(x==0 or x.bit_count()in(7,8)for x in kernel),'support')
  result={'sampled_cliques':trial+1,'leading_span_rank':len(basis),'odd_relation_size':len(ids),'selected_cliques':[chosen[i]for i in ids],'kernel_support':sorted(kernel)}
  (OUT/'CLIQUE-LEADING.json').write_text(json.dumps(result)+'\n')
  print({k:v for k,v in result.items()if k not in ('selected_cliques','kernel_support')},'kernel_support',len(kernel),flush=True)
  break
 if trial%100==0:print('trial',trial,'rank',len(basis),flush=True)
else:
 (OUT/'CLIQUE-LEADING.json').write_text(json.dumps({'sampled_cliques':3000,'leading_span_rank':len(basis),'odd_relation':False})+'\n')
