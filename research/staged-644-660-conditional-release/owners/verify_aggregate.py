"""Solver-independent integer primal check of the new aggregate owner flow.

Standard library only. Source geometry is read from the attributed frozen source
template through its retained window routine; literal copied owners are checked
separately. This certifies one finite primal, not LP optimality.
"""
from pathlib import Path
from collections import Counter,defaultdict
import sys,json,gzip,hashlib,os
if not __debug__:
 raise SystemExit('unoptimized Python required by retained owner engines')
HERE=Path(__file__).resolve().parent
if not os.environ.get('OWNER_SOURCE_REPO'):
 raise SystemExit('OWNER_SOURCE_REPO must identify the declared source checkout or export')
ROOT=Path(os.environ['OWNER_SOURCE_REPO']).resolve()
P=ROOT/'research/coupled-carrier-cap740'
# Authenticate every imported predecessor before executing any of its code.
_pins=json.loads((HERE/'SOURCE-PINS.json').read_text())
for _rel,_digest in _pins['repo_files'].items():
 _path=ROOT/_rel
 if not _path.is_file() or _path.is_symlink() or hashlib.sha256(_path.read_bytes()).hexdigest()!=_digest:
  raise ValueError('stale retained source '+_rel)
import types
common=types.ModuleType('staged_owner_retained_common');common.__file__=str(P/'common.py')
exec(compile((P/'common.py').read_bytes(),common.__file__,'exec'),common.__dict__)
W=(4,5,6,7,8,9);INV=Counter(dict(zip(W,(26,2,18,52,97,213))))
LOCAL={1:2439,2:726,3:224,4:102,5:20,8:8}

def need(v,reason):
 if not v:raise ValueError(reason)

def check(cert):
 pins_path=HERE/'SOURCE-PINS.json'
 if pins_path.exists():
  pins=common.read(pins_path)
  for rel,digest in pins['repo_files'].items():need(common.sha(P.parents[1]/rel)==digest,'pinned retained source '+rel)
 c=common.context();order=[call for call in c.order if call[1]<37]
 need(cert['order']==order,'literal T37 source chronology')
 need(cert['S']==20,'twenty copied source chronologies')
 need(cert['widths']==list(W),'ordered width alphabet')
 need(Counter({int(k):v for k,v in cert['inventory'].items()})==INV,'complete new inventory')
 win=c.owner.windows(c.template,order,37);groups=defaultdict(list)
 for (owner,child),(cap,lo,hi) in win.items():
  for port in range(112):groups[cap,lo,hi].append((owner,child,port))
 G=sorted(groups);need(cert['groups']==[[*g,len(groups[g])] for g in G],'literal window classes and physical bin counts')
 S=cert['S'];xb=Counter();xw=Counter();idle=Counter();seen=set()
 for gi,q,n in cert['x']:
  need(type(gi)is int and 0<=gi<len(G) and len(q)==6 and all(type(k)is int and k>=0 for k in q) and type(n)is int and n>0,'integral pattern record')
  need((gi,tuple(q)) not in seen,'duplicate pattern record');seen.add((gi,tuple(q)))
  used=sum(w*k for w,k in zip(W,q));need(used<=G[gi][0] and sum(q)<=S,'whole capacity-feasible pattern')
  xb[gi]+=n
  for w,k in zip(W,q):xw[gi,w]+=n*k
  if used<G[gi][0]:idle[G[gi][0]-used]+=n
 need(all(xb[g]==S*len(groups[G[g]]) for g in range(len(G))),'complete physical bin inventory')
 zw=Counter();call=Counter();gt=Counter();seen=set()
 for gi,t,w,n in cert['z']:
  need(all(type(k)is int for k in (gi,t,w,n)) and 0<=gi<len(G) and 0<=t<333 and w in W and n>0,'integral role-flow record')
  need((gi,t,w) not in seen,'duplicate role-flow record');seen.add((gi,t,w))
  need(G[gi][1]<t<=G[gi][2],'open lower and closed upper source window')
  zw[gi,w]+=n;call[t,w]+=n;gt[gi,t]+=n
 need(zw==+xw,'pattern width supply equals literal role flow')
 need(all(call[t,w]==S*INV[w] for t in range(333) for w in W),'complete per-call width demand')
 need(all(n<=S*len(groups[G[gi]]) for (gi,t),n in gt.items()),'per-copy physical group capacity')
 profile=Counter({r:n*333*S for r,n in LOCAL.items()});profile.update(idle)
 need(sum(r*n for r,n in profile.items())==65088*37*S,'complete paid rank mass')
 need(cert['profile']=={str(r):n for r,n in sorted(profile.items())},'attained complete histogram')
 return dict(status='PASS_EXACT_FINITE_INTEGER_AGGREGATE_PRIMAL',S=S,replicas=37*S,calls=333*S,roles=333*S*408,groups=len(G),idle=dict(sorted(idle.items())),profile=dict(sorted(profile.items())),rank_mass=sum(r*n for r,n in profile.items()),scope='Exact finite primal and source windows; no LP dual or universal optimality, no native or outer theorem.')

def main():
 cert=common.read(HERE/'AGGREGATE-INTEGER-FLOW.json.gz');result=check(cert);controls=[]
 def reject(name,changed,reason):
  try:check(changed)
  except ValueError as error:need(str(error)==reason,'unexpected defect rejection');controls.append(dict(name=name,reason=reason))
  else:raise ValueError('accepted defect '+name)
 reject('deleted_integral_role_flow',{**cert,'z':cert['z'][1:]},'pattern width supply equals literal role flow')
 reject('duplicated_pattern_record',{**cert,'x':cert['x']+[cert['x'][0]]},'duplicate pattern record')
 bad=[row[:] for row in cert['z']];j=next(j for j,(g,t,w,n) in enumerate(bad) if cert['groups'][g][1]>=0);g,t,w,n=bad[j];bad[j][1]=cert['groups'][g][1]
 reject('role_on_excluded_lower_endpoint',{**cert,'z':bad},'open lower and closed upper source window')
 reject('deleted_whole_owner_bin_pattern',{**cert,'x':cert['x'][1:]},'complete physical bin inventory')
 result['controls']=controls;result['certificate_sha256']=common.sha(HERE/'AGGREGATE-INTEGER-FLOW.json.gz')
 print(json.dumps(result,indent=2))

if __name__=='__main__':main()
