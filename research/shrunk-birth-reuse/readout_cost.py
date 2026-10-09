"""Original exact signed integer dirty-readout responses and literal unit bill.
All coefficients are represented over42 by unsigned bitplanes; no modular test.
"""
import sys,os
if sys.flags.optimize or os.environ.get('PYTHONOPTIMIZE'):raise RuntimeError('Assertions required')
from pathlib import Path
from functools import reduce
from operator import or_
from itertools import combinations
import pickle,json,time,resource,hashlib
ROOT=Path(__file__).resolve().parent;start=time.monotonic();(sys.platform=='darwin' or resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2)));resource.setrlimit(resource.RLIMIT_CPU,(30,30))
g=pickle.loads((ROOT/'FRAMES.pkl').read_bytes());R=len(g['first']);v=g['v'];N=v*v;allbits=(1<<v)-1;tr=list(combinations(range(24),3));point=[sum(1<<j for j,t in enumerate(tr)if i in t)for i in range(24)]
def scaled(mask,n):return tuple(mask if n>>i&1 else 0 for i in range(n.bit_length()))
def plus(a,b):
 out=[];carry=0
 for i in range(max(len(a),len(b))):
  x=a[i]if i<len(a)else 0;y=b[i]if i<len(b)else 0;out.append(x^y^carry);carry=(x&y)|(x&carry)|(y&carry)
 if carry:out.append(carry)
 while out and not out[-1]:out.pop()
 return tuple(out)
def absdiff(a,b):
 out=[];borrow=0
 for i in range(max(len(a),len(b))+1):
  x=a[i]if i<len(a)else 0;y=b[i]if i<len(b)else 0;out.append(x^y^borrow);borrow=((~x&(y|borrow))|(y&borrow))&allbits
 neg=borrow;carry=neg;absolute=[]
 for x in out:
  y=x^neg;absolute.append(y^carry);carry=y&carry
 assert not carry
 while absolute and not absolute[-1]:absolute.pop()
 return tuple(absolute),neg
P=[()]*R;M=[()]*R
for s,j in g['terminal'].items():
 if j>=len(g['roots'])-24:
  i=j-(len(g['roots'])-24);P[s]=scaled(allbits^point[i],2);M[s]=scaled(point[i],19)
 elif j<v:P[s]=scaled(1<<g['targets'][j],21)
 else:M[s]=scaled(1<<g['targets'][j],21)
seeds=(P[:],M[:]);source_ops=0;workspace_ops=0
for op,s,t,x in reversed(g['ops']):
 if op==0:source_ops+=1;continue
 workspace_ops+=1
 a,b=(t,s)if op==1 else(s,t);P[a]=plus(P[a],P[b]);M[a]=plus(M[a],M[b])
# Check the carry/subtract primitives exactly on adversarial small masks.
for a in range(80):
 for b in range(80):
  z,neg=absdiff(scaled(1,a),scaled(1,b));assert sum((1<<i)for i,w in enumerate(z)if w&1)==abs(a-b);assert bool(neg&1)==(a<b)
count=weight=maximum=0;max_role=-1;digest=hashlib.sha256();dense_reached=0
for s,(a,b)in enumerate(zip(P,M)):
 z,neg=absdiff(a,b);nonzero=reduce(or_,z,0);count+=nonzero.bit_count();weight+=sum(w.bit_count()*(1<<i)for i,w in enumerate(z))
 candidates=nonzero;maxhere=0
 for i in range(len(z)-1,-1,-1):
  if candidates&z[i]:maxhere|=1<<i;candidates &= z[i]
 if maxhere>maximum:maximum=maxhere;max_role=s
 # Pin full exact responses, including zero coefficients and signs.
 digest.update(s.to_bytes(4,'little'));digest.update(len(z).to_bytes(4,'little'));digest.update(neg.to_bytes((v+7)//8,'little'))
 for w in z:digest.update(w.to_bytes((v+7)//8,'little'))
 if s in g['placed']:
  # Deferred origin has no center contribution; every actual target is in the conservative reach set.
  assert not(nonzero&~g['reach'][s]);dense_reached+=nonzero.bit_count()
terminal_weight=0;terminal_count=0
for a,b in zip(*seeds):
 z,_=absdiff(a,b);terminal_weight+=sum(w.bit_count()*(1<<i)for i,w in enumerate(z));terminal_count+=reduce(or_,z,0).bit_count()
# A read divides a computed complete copy by42 and uses signed unit adds.
# Eight scans per origin/terminal covers copy, division, parking and discard.
read_bill=weight+terminal_weight+8*(R+len(g['terminal']))
# True chronological forward/inverse injections and workspace gates; finite slot bookkeeping.
local=read_bill+2*(source_ops+workspace_ops)+16*R+16*24
# A factor16 additionally covers phase/sign wrappers and implementation scans.
G=16*(2*v*local+8*N)
record=dict(status='PASS exact integer old-readout response and explicit conservative scalar bill; no <=1 coefficient assumption',denominator=42,readout_nonzero_terms=count,readout_numerator_L1=weight,max_abs_numerator=maximum,max_abs_coefficient=f'{maximum}/42',max_role=max_role,deferred_readout_terms=dense_reached,terminal_terms=terminal_count,terminal_numerator_L1=terminal_weight,source_injection_count=source_ops,workspace_gate_count=workspace_ops,readout_copy_scan_bill=read_bill,local_scalar_upper=local,global_scalar_group_upper=G,expansion='At each readout, form one complete computed copy divided by42, then |numerator| signed unit additions to targets. Reverse all workspace/source gates chronologically. Factor16 and explicit endpoint groups bound scalar bookkeeping/wrappers.',odd_grid='Denominator42=2*21; retain common odd21 grid with per-local-word G and completed-child preservation.',exact_response_sha256=digest.hexdigest(),seconds=time.monotonic()-start,rss_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
blob=pickle.dumps(dict(positive=P,negative=M,terminal_positive=seeds[0],terminal_negative=seeds[1]),protocol=4);(ROOT/'READOUTS.pkl').write_bytes(blob);record['checkpoint_sha256']=hashlib.sha256(blob).hexdigest();(ROOT/'READOUT_COST.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
