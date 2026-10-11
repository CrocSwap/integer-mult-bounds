"""Fresh exact E8 paid profile and both rational moment engines. OpenAI Codex assistance."""
import sys
if not __debug__:raise SystemExit('Assertions required')
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(0)
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import argparse,json,gzip,hashlib,importlib.util
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def serial(x):
 if isinstance(x,Q):return str(x)
 if isinstance(x,dict):return{k:serial(v)for k,v in x.items()}
 if isinstance(x,(tuple,list)):return list(map(serial,x))
 return x

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--guard',required=True,type=Path);ap.add_argument('--output',required=True,type=Path);a=ap.parse_args();assert not a.output.exists();pins=read(ROOT/'SOURCE.json');raw=gzip.decompress((ROOT/pins['certificate_gzip_path']).read_bytes());assert hashlib.sha256(raw).hexdigest()==pins['candidate_sha256'];c=json.loads(raw);guard=read(a.guard);H=Counter()
 for block in c['blocks'].values():H.update({int(r):5*n for r,n in block.items()})
 h,v,R=c['h'],c['v'],c['R'];m,W=5*h,4*v+R
 for r in [2*h-2,h-1,2*h+2,4]:H[r]+=2*v
 assert(m,W,h,v,R)==(45,1263,9,120,783)
 assert H==Counter({int(r):n for r,n in guard['ledger']['histogram'].items()})
 assert(sum(H.values()),sum(r*n for r,n in H.items()),m*W-sum(r*n for r,n in H.items()),max(H))==(20830,56715,120,20)
 P=ROOT/'upstream/pr352/code/pricing';cost=load('e8_price_moment',P/'moment.py');other=load('e8_price_other',P/'base_two_moment.py');result={};grid=Q(1,10**18)
 for fallback in [True,False]:
  label='with_fallback'if fallback else'without_fallback';root=cost.certify(dict(H),m,W,fallback);b=Q(int(Q(root['lower'])*10**18),10**18);cm=cost.moment(dict(H),m,W,b,fallback);nm=cost.moment(dict(H),m,W,b+grid,fallback);assert cm[1]<1<nm[0]
  lower,upper=other.moment(m,W,list(H.items()),b);nlower,nupper=other.moment(m,W,list(H.items()),b+grid)
  if fallback:
   total=32*m*m*sum(H.values());bl,bu=other.moment(m,W,[(1,total)],b);nbl,nbu=other.moment(m,W,[(1,total)],b+grid);lower+=Q(1,10**16)*bl;upper+=Q(1,10**16)*bu;nlower+=Q(1,10**16)*nbl;nupper+=Q(1,10**16)*nbu
  assert upper<1<nlower;result[label]=dict(b=b,moment_interval=cm,next_grid_excluded=nm,independent_moment_interval=(lower,upper),independent_next_grid=(nlower,nupper))
 assert result['with_fallback']['b']==Q(pins['complex_coarse'])
 out=dict(status='PASS_E8_FULL_PAID_PROFILE_TWO_EXACT_MOMENTS',candidate_sha256=pins['candidate_sha256'],guard_sha256=sha(a.guard),engine_pins={f:sha(P/f)for f in ['moment.py','base_two_moment.py']},profile=dict(m=m,W=W,histogram=dict(H),calls=sum(H.values()),rank_mass=sum(r*n for r,n in H.items()),deficit=120,maxchild=20),roots=result,kappa_claim=False)
 a.output.write_text(json.dumps(serial(out),sort_keys=True,indent=2)+'\n');print('PASS exact E8 moment roots',result['with_fallback']['b'],result['without_fallback']['b'],flush=True)
if __name__=='__main__':main()
