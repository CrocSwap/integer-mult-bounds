"""Finite checks for a legal, but currently uneconomic, Pauli encoder partial word."""
from pathlib import Path
from fractions import Fraction
from collections import Counter
import sys,json,hashlib
import numpy as np
PACKAGE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PACKAGE / 'code'))
import e8_cubed as e

def basis(values):
 b={}
 for value in values:e.insert_binary(b,value)
 for low in sorted(b):
  for high in b:
   if high>low and (b[high]>>low)&1:b[high]^=b[low]
 return tuple(b[p]for p in sorted(b))

def contains(big,small):
 return len(basis(big+small))==len(big)

roots,fourth,ports,profiles=e.construct_shell();ports=ports[(profiles&4)==0,:16]
labels,packed,_=e.binary_labels(roots,ports)
selected=[0,2,1,42,6,12,20,30]
B=roots[selected].T.astype(np.int64);work=[[Fraction(int(x))for x in row]+[Fraction(int(i==j))for j in range(8)]for i,row in enumerate(B)];pivots=[];ops=[];det=Fraction(1)
for col in range(8):
 pivot=next(row for row in range(col,8)if work[row][col])
 if pivot!=col:work[col],work[pivot]=work[pivot],work[col];ops.append(['swap',col,pivot]);det=-det
 value=work[col][col];det*=value;pivots.append(str(value));e.require(abs(value.numerator)&(abs(value.numerator)-1)==0 and value.denominator&(value.denominator-1)==0,'Dyadic unit pivot')
 work[col]=[x/value for x in work[col]];ops.append(['scale',col,str(1/value)])
 for row in range(8):
  if row==col or not work[row][col]:continue
  value=work[row][col];work[row]=[x-value*y for x,y in zip(work[row],work[col])];ops.append(['add',row,col,str(-value)])
Binv=[[row[8+j]for j in range(8)]for row in work]
e.require(abs(det)==256,'Selected root minor determinant')
e.require(all(sum(Fraction(int(B[i,k]))*Binv[k][j]for k in range(8))==int(i==j)for i in range(8)for j in range(8)),'Exact mixer inverse')
# Every gate in reverse reduction realizes B; then the other112 carrier inputs are added.
M=np.eye(120,dtype=np.int64)
for coordinate,carrier in enumerate(selected):M[carrier]=roots[:,coordinate]
for coordinate,carrier in enumerate(selected):e.require(np.array_equal(M[carrier],roots[:,coordinate]),'Selected mixer row is the root-coordinate total')
paulis=[];Q=[]
for a in range(8):
 for b in range(8):
  if (a,b)==(0,0)or(a&b).bit_count()%2:continue
  values=(roots.astype(np.int64)*roots[:,[j^a for j in range(8)]]*[(-1)**((j&b).bit_count()%2)for j in range(8)]).sum(axis=1)
  e.require(set(map(int,values))=={-8,0,8} and int((values!=0).sum())==24,'Pauli root support')
  paulis.append([a,b]);Q.append(values)
Q=np.stack(Q,axis=1)
e.require(np.all((Q!=0).sum(axis=1)==7),'Exactly seven Pauli destinations per fixed quadratic root')
frame_records=[]
for orientation in range(2):
 groupframes=[]
 for fixed in range(120):
  port_ids=np.array([2160+2*(linear*120+fixed)+orientation if orientation==0 else 2160+2*(fixed*120+linear)+1 for linear in range(120)])
  F=basis(packed[port_ids]);e.require(len(F)==9,'Fixed quadratic root input frame dimension9')
  for coordinate in range(8):e.require(basis(packed[port_ids[roots[:,coordinate]!=0]])==F,'Each selected total spans the same input frame')
  groupframes.append(F)
 for p in range(35):
  U=basis([x for fixed in np.flatnonzero(Q[:,p])for x in groupframes[int(fixed)]])
  e.require(len(U)==15,'Pauli output frame dimension15')
  e.require(all(contains(U,groupframes[int(fixed)])for fixed in np.flatnonzero(Q[:,p])),'Every fanout climb is nested9 to15')
  frame_records.append(dict(orientation=orientation,pauli=paulis[p],frame=list(U)))
# Dense integer diagnostic of the compressed universal affine identities.
rng=np.random.default_rng(170816);worst=0
for orientation in range(2):
 X=rng.integers(-8,9,size=(120,120),dtype=np.int64);C0=rng.integers(-8,9,size=(120,120),dtype=np.int64)
 C=M@(C0+X);D0=rng.integers(-8,9,size=(120,35,8),dtype=np.int64);Z0=rng.integers(-8,9,size=(8,35),dtype=np.int64)
 D=D0.copy();Z=Z0.copy()
 for fixed,p in np.argwhere(Q!=0):
  D[fixed,p]+=2*Q[fixed,p]*C[selected,fixed]
  Z[:,p]+=D[fixed,p]
 dirt=Z0.copy();MC0=M@C0
 for fixed,p in np.argwhere(Q!=0):dirt[:,p]+=D0[fixed,p]+2*Q[fixed,p]*MC0[selected,fixed]
 e.require(np.array_equal(Z-dirt,2*roots.T@X@Q),'Encoder output after old-dirt cancellation')
 # Reverse every addition atFULL. This identity is coefficient-wise, not an approximate check.
 for fixed,p in reversed(np.argwhere(Q!=0).tolist()):Z[:,p]-=D[fixed,p]
 for fixed,p in reversed(np.argwhere(Q!=0).tolist()):D[fixed,p]-=2*Q[fixed,p]*C[selected,fixed]
 e.require(np.array_equal(Z,Z0)and np.array_equal(D,D0),'Fanout and center dirt restored')
 # Explicit inverse: subtract untouched-column contributions, then apply the verified8x8 inverse.
 Cback=C.copy();other=[j for j in range(120)if j not in selected]
 top=C[selected]-roots[other].T@C[other]
 for i,carrier in enumerate(selected):
  for column in range(120):
   value=sum(Binv[i][j]*int(top[j,column])for j in range(8));e.require(value.denominator==1,'Inverse returns integral original carrier values');Cback[carrier,column]=value.numerator
 Cback-=X;e.require(np.array_equal(Cback,C0),'All input-carrier dirt restored')
helper_profiles={"input_[1,8,8]":28800,"fanout_[9,6,2]":13440,"Pauli_center_[15,2]":560,"full_center_[17]":256}
receipt=dict(status='PASS_ENCODER_PARTIAL_WORD_ONLY',helpers=43056,helper_profiles=helper_profiles,
 source_profile=[16],source_count=30960,target_during_this_partial_word=0,
 paid_center_copies={15:560,17:256},center_copy_rank_bill=12752,
 mixer=dict(selected_root_rows=selected,determinant=str(det),reduction_pivots=pivots,reduce_B_to_identity=ops,inverse=[[str(x)for x in row]for row in Binv]),
 frame_records=frame_records,
 compressed_affine_identity='C=M(C0+X); D[b,P,i]=D0[b,P,i]+2*qP(b)*C[selected_i,b]; Z[i,P]=Z0[i,P]+sum_b D[b,P,i]. Subtract the same expression with X=0 at target frame0 before gathering. The remaining fresh coefficient is2*R^T X Q. Reverse the additions and the verified dyadic mixer atFULL17 to restore all old C,D,Z.',
 frame_schedule='Input copies at their one-dimensional port lines; carriers climb to fixed-root9 frames and execute the invertible120-carrier mixer there. Fanouts enter at the9 frame, climb to the containing Pauli15 frame, feed the center, then finish atFULL17. Centers enter at15, send a private15-to0 scatter copy, and finish at17. Full-width centers gather once sources reach17, and send private17-to0 copies. All arbitrary initial helper responses are subtracted from targets at0 before any helper moves; all non-target scalar gates are undone at17.',
 limitations='This constructs only the exact K encoder/scatter/restoration partial word. It does not implement I-K, does not complete target endpoints, and does not establish a new kappa. The simpler816 full-width-center encoder requires only816 helpers and is financially stronger unless this narrow encoder work can be shared with compensation.')
print(json.dumps(receipt,indent=2,sort_keys=True))
