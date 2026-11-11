from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import packet325 as contract
contract.require_assertions()
contract.verify_inputs()
contract.verify_frame_binding()
"""Independent exact checks of fresh route/boundary and positive COPY geometry.
No emitter imports, upstream execution, or numerical rank screens.
"""
from pathlib import Path
from fractions import Fraction as Q
import json,gzip,hashlib,os
import numpy as np
if not __debug__:raise RuntimeError('Assertions required')
HERE=contract.GLOBAL
P=contract.GLOBAL
L=contract.FRAME
def read(p):
 p=Path(p);b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 routes=read(P/'fresh-data-routes.json');labels=routes['ports'];I=np.eye(20,dtype=np.int64);q=np.array([int(j<3)for j in range(20)],dtype=np.int64)
 PP=np.outer(q,3*q-1);KK=6*I-PP
 assert np.array_equal(PP@PP,6*PP)and np.array_equal(KK@KK,6*KK)and not np.any(PP@KK)
 def rho(s):
  R=6*np.eye(100,dtype=np.int64)
  if s:
   w=slice(s*20,(s+1)*20);R[:20,:20]=PP;R[w,w]=PP;R[:20,w]=KK;R[w,:20]=KK
  assert np.array_equal(R@R,36*np.eye(100,dtype=np.int64));return R
 def stage(s,k):
  A=np.zeros((100,100),dtype=np.int64);A[:20,:20]={'P':PP,'K':KK,'H':6*I,'0':0*I}[k]
  for j in range(1,s+1):A[j*20:(j+1)*20,j*20:(j+1)*20]=KK
  return A
 def data(s,k):
  v=rho(s)@stage(s,k)@rho(s);assert not np.any(v%36);return v//36
 z=np.zeros((100,100),dtype=np.int64);ii=6*np.eye(100,dtype=np.int64);p=data(0,'P')
 pairs=[(p,data(1,'H')),(z,data(1,'K')),(data(2,'P'),data(3,'P')),(data(2,'0'),data(3,'0')),(data(2,'H'),ii),(data(2,'K'),ii-p),(data(4,'H'),ii),(data(4,'K'),ii-p)]
 ranks=[]
 for a,b in pairs:
  diff=b-a;assert np.array_equal(diff@diff,6*diff);ranks.append(int(np.trace(diff)//6))
 assert ranks==[38,38,19,19,42,42,4,4]
 # For every fresh label, explicit40dimensional route is S*rho_star*S^-1.
 canonical=np.block([[PP,KK],[KK,PP]])
 for port in labels:
  pi=np.zeros((20,20),dtype=np.int64)
  for j,i in enumerate(port['pi_columns']):pi[i,j]=1
  chi=np.array([int(j in port['label'])for j in range(20)]);pchi=np.outer(chi,3*chi-1)
  assert np.array_equal(pi@q,chi)and np.array_equal(pi@PP@pi.T,pchi)
  r=np.block([[pchi,pi@KK],[KK@pi.T,PP]]);s=np.block([[pi,0*I],[0*I,I]])
  assert np.array_equal(r,s@canonical@s.T)and np.array_equal(r@r,36*np.eye(40,dtype=np.int64))
 # Actual20 center frames have codimension2; derive their positive projector exactly.
 frames=read(L/'local-frames.json.gz');records=read(L/'local-records.json.gz');overrides=read(P/'copied-work-projector-overrides.json')
 centers={r[3]for r in records if r[0]==2};assert len(centers)==20 and len(overrides)==100
 def mul(a,b):return [[sum(x*y for x,y in zip(row,col))for col in zip(*b)]for row in a]
 id20=[[Q(i==j)for j in range(20)]for i in range(20)]
 for f in centers:
  A=[list(map(Q,row))for row in frames[str(f)]['annihilator']];assert len(A)==2
  U=[[A[k][j]-sum(A[k])/11 for k in range(2)]for j in range(20)];M=mul(A,U);det=M[0][0]*M[1][1]-M[0][1]*M[1][0];assert det
  inv=[[M[1][1]/det,-M[0][1]/det],[-M[1][0]/det,M[0][0]/det]];N=mul(mul(U,inv),A)
  Pp=[[id20[i][j]-N[i][j]for j in range(20)]for i in range(20)]
  assert mul(Pp,Pp)==Pp and sum(Pp[i][i]for i in range(20))==18
  minus=[[-x for x in row]for row in Pp];assert mul(minus,minus)!=minus
 for x in overrides:
  assert x['rank']==18 and(x['difference_orientation']==(-1 if not x['complement']else 1))
  assert x['old_frame']in centers and frames[str(x['new_frame'])]['rank']==0
 result={'status':'PASS_FRESH_PR325_EXACT_DATA_BOUNDARY_AND_COPY_GEOMETRY','routes':960,'all_rho_involutions':True,'boundary_ranks':ranks,'universal_port_conjugacy_checked':True,
 'actual_center_projectors':20,'positive_copy_overrides':100,'negative_center_projector_rejected':True,'global_result_sha256':sha(P/'RESULT.json'),'checker_sha256':sha(__file__),
 'scope':'Exact finite rational coordinate geometry. Common-frame pointwise-array lifting, generic primitive, prime and all-size interfaces remain separately scoped.'}
 (HERE/'GEOMETRY-CONTROLS.json').write_text(json.dumps(contract.portable(result),indent=2)+'\n');print(json.dumps(contract.portable(result),indent=2))
if __name__=='__main__':main()
