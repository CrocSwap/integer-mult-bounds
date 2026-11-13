"""Independent transfer and explicit non-inheritance controls for the global map."""
from pathlib import Path
from types import ModuleType
from itertools import product
import hashlib,json
SOURCE=Path(__file__).with_name('check_global_candidate.py')
M=ModuleType('root_global_matching');M.__file__=str(SOURCE)
exec(compile(SOURCE.read_bytes(),str(SOURCE),'exec'),M.__dict__)
C2=((1,-1,1,1),(1,1,-1,1),(1,1,1,-1),(-1,1,1,1))
def S(x):return(x[0],-x[1],x[2],x[3])
def L(x):return(x[0],x[2],-x[3],x[1])
def Li(x):return(x[0],x[3],x[1],-x[2])
def Fc(x):return Li(M.F(S(x)))
def Fc_inv(x):return S(M.inv(L(x)))
def phase(x):return(-x[1],x[0],-x[3],x[2])
def K(x):return(x[0],-x[1],x[2],-x[3])
def cminus2(x):return K(M.mul(C2,K(x)))
def fourth(x):
 for _ in range(4):x=Fc(x)
 return x

def main():
 for i in range(4):
  x=tuple(int(j==i) for j in range(4))
  M.need(L(M.mul(C2,S(x)))==M.mul(M.H,x),'exact signed transfer')
  M.need(cminus2(M.mul(C2,x))==tuple(4*a for a in x),'ideal negative is inverse')
 for x in product(range(-3,4),repeat=4):
  y=Fc(x);z=Fc_inv(x)
  M.need(Fc_inv(y)==x and Fc(z)==x,'Gaussian exact inverse')
  for a,b in [(y,M.mul(C2,x)),(z,cminus2(x))]:
   M.need(sum((2*c-d)**2 for c,d in zip(a,b))<=4,'both ideal errors')
   M.need(M.radial_half(M.n2(a),M.n2(x)),'both radial allowances')
 controls={}
 x=(0,0,2,1);y=Fc(x)
 M.need(y==(2,-1,1,1) and (y[0]+y[2],y[1]+y[3])!=(x[0]+x[2],x[1]+x[3]),'sum noninheritance')
 controls['complex_sum']={'x':x,'output':y}
 x=(-2,-2,-2,-1);a=Fc(phase(x));b=phase(Fc(x))
 M.need(a==(2,-1,2,-2) and b==(1,-2,2,-2) and a!=b,'phase noninheritance')
 controls['global_i_phase']={'x':x,'F(ix)':a,'iF(x)':b}
 a=K(Fc(K(x)));b=Fc_inv(x)
 M.need(a==(-2,-2,-1,-2) and b==(-2,-1,-2,-2) and a!=b,'conjugation not inverse')
 controls['conjugated_positive_not_inverse']={'x':x,'conjugate':a,'inverse':b}
 x=(-2,-1,-2,2);a=fourth(x)
 M.need(a==(-3,1,-1,0) and a!=x,'fourth power noninheritance')
 controls['fourth_power']={'x':x,'output':a}
 print(json.dumps({'status':'PASS_ROOT_GAUSSIAN_TRANSFER_AND_NONINHERITANCE','input_cases':7**4,'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'controls':controls,'negative_provider':'S F_H_inverse L, not conjugated positive map'},indent=2))
if __name__=='__main__':main()
