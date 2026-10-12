"""Physical frame-label checks and finite-address controls for target additions.
Address field F3, bit values F2: these are deliberately different fields.
The general shared-label proof is in PROOF.md; finite cases are controls.
Chafreaky with OpenAI Codex assistance; Apache-2.0.
"""
import gzip,hashlib,json,struct,sys
from collections import Counter
from itertools import product
from pathlib import Path
import sympy as S
ROOT=Path(__file__).resolve().parents[1]
recdir=Path(sys.argv[1]);word=json.loads(gzip.decompress((ROOT/'data/word.json.gz').read_bytes()))
fs=json.loads((recdir/'frames.json').read_text())['frames'];state=json.loads((recdir/'249-states.json').read_text())
records=list(struct.iter_unpack('<6i',(recdir/'249-records.bin').read_bytes()))
selected=json.loads((ROOT/'data/mixing.json').read_text());v=word['v'];n=2*v+word['R'];current=[state['initial'][str(i)] for i in range(n)]+[-1]
want=Counter((ph,f,d,s) for phase,ph in [('D',1),('A',2),('B',4),('C',5)] for f,d,ss in word[phase] for s in ss if v<=s<2*v);seen=Counter();projectors={}
for op,a,b,c,f,z in records:
 if op==0:assert current[a]==b;current[a]=c
 elif op==1:
  assert current[a]==current[b]==f
  if v<=b<2*v:
   assert v<=a<2*v and c==1;seen[z,f,a,b]+=1
   if f not in projectors:
    B=S.Matrix(fs[str(f)]['B']) if fs[str(f)]['B'] else S.zeros(0,8)
    P=B.T*(B*B.T).inv()*B if B.rows else S.zeros(8);I=S.eye(8)
    D=(I-P).row_join(P).col_join(P.row_join(I-P))
    assert P.T==P and P*P==P and P.trace()==fs[str(f)]['dim'] and D*D==S.eye(16)
    projectors[f]=D
 elif op==2:assert b==n;current[n]=f
 else:assert op==3 and b==n;current[n]=-1
assert seen==want and sum(seen.values())>=112
assert current[:n]==[state['final'][str(i)] for i in range(n)]

q=3;m=2;addresses=list(product(range(q),repeat=2*m));index={x:i for i,x in enumerate(addresses)};N=len(addresses)
def permutation(P):
 result=[]
 for z in addresses:
  x,y=z[:m],z[m:];delta=[sum(P[i][j]*(y[j]-x[j]) for j in range(m))%q for i in range(m)]
  image=tuple((x[i]+delta[i])%q for i in range(m))+tuple((y[i]-delta[i])%q for i in range(m))
  result.append(index[image])
 assert sorted(result)==list(range(N)) and all(result[result[i]]==i for i in range(N))
 return result
perms={'zero':permutation([[0,0],[0,0]]),'coordinate':permutation([[1,0],[0,0]]),
       'diagonal':permutation([[2,2],[2,2]]),'full':permutation([[1,0],[0,1]])}
def label(bits,pa,pb):
 answer=0
 while bits:
  low=bits&-bits;i=low.bit_length()-1;bits-=low
  j=pa[i] if i<N else N+pb[i-N];answer^=1<<j
 return answer
def add(bits):
 mask=(1<<N)-1;left=bits&mask;right=bits>>N
 return (left^right)|(right<<N)
checks=0
for name,p in perms.items():
 for i in range(2*N):
  e=1<<i;assert label(add(e),p,p)==add(label(e,p,p));checks+=1
bad=[]
for i in range(2*N):
 e=1<<i
 if label(add(e),perms['zero'],perms['diagonal'])!=add(label(e,perms['zero'],perms['diagonal'])):bad.append(i)
assert bad,'unequal physical labels must not pass the common-frame test'
result=dict(status='PASS_TARGET_COMMON_LABEL_LIFT_CONTROLS',target_additions=sum(seen.values()),inherited_preconditioners=56,inherited_mix_additions=56,
 actual_mixing_labels=len(projectors),actual_address_matrix_dimension=16,role_dependent_label_parameters=False,
 finite_control=dict(address_field=3,bit_value_field=2,address_dimension=4,addresses_per_family=N,scalar_columns=2*N,
   frames=list(perms),exact_shared_label_commutations=checks,unequal_label_columns_rejected=len(bad),first_bad_column=bad[0]),
 scope='Exact current-frame binding on every new target operand; exact address involutions for its frame. The finite F3/F2 controls illustrate the general pullback-linearity proof and reject mismatched labels. All-size compilation remains inherited.')
(recdir.parent/'LABELS.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
