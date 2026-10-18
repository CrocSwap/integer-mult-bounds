from pathlib import Path
import itertools,json
import numpy as np
OUT=Path(__file__).resolve().parent

def require(x,m):
 if not x:raise ValueError(m)
def rank(vs):
 b={}
 for v in vs:
  v=int(v)
  while v:
   k=v.bit_length()-1
   if k in b:v^=b[k]
   else:b[k]=v;break
 return len(b)
ix=np.array(list(itertools.combinations(range(14),4)),dtype=np.int16)
lut=np.array([rank(t)==4 for t in itertools.product(range(16),repeat=4)],dtype=np.uint8).reshape((16,)*4)
results=[]
for m in [8]:
 basis={};chosen=[];known=set();out=None
 for order in itertools.permutations(range(8,16)):
  cols=list(range(1,8))+list(order);cs=np.array(cols[:14],dtype=np.int16)
  gens=[sum(((int(c)>>j)&1)<<i for i,c in enumerate(cs))for j in range(4)]
  H=[0]
  for g in gens:H += [v^g for v in H]
  H=tuple(sorted(H))
  if H in known:continue
  known.add(H);trial=len(chosen);chosen.append(H)
  bits=lut[cs[ix[:,0]],cs[ix[:,1]],cs[ix[:,2]],cs[ix[:,3]]]
  v=int.from_bytes(np.packbits(bits,bitorder='little').tobytes(),'little');trace=1<<trial
  while v:
   p=v.bit_length()-1
   if p in basis:
    vv,tt=basis[p];v^=vv;trace^=tt
   else:basis[p]=(v,trace);break
  if v==0 and trace.bit_count()%2:
   ids=[i for i in range(trial+1)if trace>>i&1];kernel=set()
   for i in ids:kernel.symmetric_difference_update(chosen[i])
   require(0 in kernel,'diagonal')
   out={'coordinate_count_permuted':m,'cliques_tested':trial+1,'leading_rank':len(basis),'relation_size':len(ids),'selected_cliques':[chosen[i]for i in ids],'kernel_support':sorted(kernel)}
   print({k:v for k,v in out.items()if k not in('selected_cliques','kernel_support')},'support',len(kernel),flush=True)
   (OUT/f'CLIQUE-HALF-{m}.json').write_text(json.dumps(out)+'\n');break
 if out is None:
  out={'coordinate_count_permuted':m,'cliques_tested':len(chosen),'leading_rank':len(basis),'odd_relation_found':False};print(out,flush=True)
 results.append({k:v for k,v in out.items()if k not in('selected_cliques','kernel_support')})
 if out.get('relation_size'):break
(OUT/'CLIQUE-HALF.json').write_text(json.dumps(results,indent=2)+'\n')
