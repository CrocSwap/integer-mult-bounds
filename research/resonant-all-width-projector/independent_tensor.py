"""Independent literal tensor checks for the all-width resonance theorem."""
import json,hashlib,sys
from pathlib import Path
from fractions import Fraction

def need(c,m):
 if not c:raise ValueError(m)
def add(a,b):return a[0]+b[0],a[1]+b[1]
def mul(a,b):return a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]
U=((1,0),(0,1),(-1,0),(0,-1));Z=(0,0)
def matrix(records,f,projective=False):
 d=8**f;out={}
 for r in records:
  s=1 if r['coefficient']=='1/16' else -1
  for j in range(d):
   v=j;k=0;p=0;place=1
   for _ in range(f):
    digit=v%8;v//=8;k+=r['permutation'][digit]*place;place*=8
    p+=r['phase_i'][digit]-(r['phase_i'][0] if projective else 0)
   w=U[p%4];w=s*w[0],s*w[1];key=k,j;old=out.get(key,Z);new=add(old,w)
   if new==Z:out.pop(key,None)
   else:out[key]=new
 return out

def check(path,poly):
 records=json.loads(path.read_text(encoding='utf8'));need(len(records)==256,'frozen support')
 need(not matrix(records,1),'literal odd width one must vanish')
 M=matrix(records,2);need(bool(M),'literal width two nonzero')
 (row,col),pivot=next(iter(M.items()))
 for i in range(64):
  a=M.get((i,col),Z)
  for j in range(64):need(mul(M.get((i,j),Z),pivot)==mul(a,M.get((row,j),Z)),'exact rank-one minors')
 need(not matrix(records,3),'literal odd width three must vanish')
 need(matrix(records,2,True)!=M,'dropped global phase must change actual tensor matrix')
 norm2=Fraction(sum(a*a+b*b for a,b in M.values()),256)
 # rank(A2)=1 gives its unique positive Gram eigenvalue = ||A2||_F^2.
 lam=norm2/16;q=poly[1:];qvalue=sum(Fraction(c)*lam**i for i,c in enumerate(q));need(qvalue==0,'annihilator at direct positive eigenvalue')
 rvalue=-sum(Fraction(c)*lam**(i-1) for i,c in enumerate(q) if i)/q[0]
 need(lam*rvalue==1,'image inverse polynomial')
 need((rvalue/16)*norm2==1,'correct pseudoinverse scaling')
 need((16*rvalue)*norm2!=1,'inverse scaling mutation must reject')
 return {'status':'PASS_INDEPENDENT_RESONANT_TENSOR_CHECKS','direct_width_one_rank':0,'direct_width_two_rank':1,'direct_width_three_rank':0,'width_two_nonzero_entries':len(M),'width_two_gram_positive_eigenvalue':str(norm2),'scaled_gram_eigenvalue':str(lam),'global_phase_mutation_rejected':True,'wrong_pseudoinverse_scale_rejected':True}
if __name__=='__main__':
 root=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parent
 import importlib.util
 spec=importlib.util.spec_from_file_location('rank_certificate',root/'verify.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
 print(json.dumps(check(root/'TARGET.json',v.POLY),sort_keys=True))
