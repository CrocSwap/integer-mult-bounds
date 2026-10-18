# SPDX-License-Identifier: Apache-2.0
"""Whole-role residual relay and five-copy cap attainment for pinned PR #2942.
No provider word is changed. Full native/global/outer admission is separate.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter,defaultdict
import argparse,gzip,json,hashlib,os,sys,types
sys.dont_write_bytecode=True

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b)if b[:2]==b'\x1f\x8b'else b)
def load(p,name):
 m=types.ModuleType(name);m.__file__=str(p);exec(compile(p.read_bytes(),str(p),'exec'),m.__dict__);return m
def save(p,v):
 b=(json.dumps(v,sort_keys=True,separators=(',',':'))+'\n').encode()
 if p.suffix=='.gz':b=gzip.compress(b,mtime=0)
 assert not p.exists();fd=os.open(str(p)+'.lock',os.O_CREAT|os.O_EXCL|os.O_WRONLY)
 try:p.write_bytes(b)
 finally:os.close(fd);Path(str(p)+'.lock').unlink()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,default=Path(__file__).parent/'source2942');ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();src=a.source.resolve();out=a.out.resolve();assert not out.exists();out.mkdir(parents=True)
 manifest=read(src/'MANIFEST.json');assert sha(src/'MANIFEST.json')=='23bd270f440c4c7ad0d106990ae391e1af799a61ef3601d00e27f1824ae8ba69'
 actual={f.relative_to(src).as_posix():sha(f)for f in src.rglob('*')if f.is_file()and f!=src/'MANIFEST.json'}
 assert not any(f.is_symlink()for f in src.rglob('*')) and actual==manifest,'complete pinned PR2942 source inventory'
 pins={'head':'a027b0f6fdb0ab2b42ba10fc31b53960166bf2bf','files':[{'path':k,'sha256':v}for k,v in manifest.items()]}
 for v in pins['files']:assert sha(src/v['path'])==v['sha256'],v['path']
 engine=load(src/'allocation/vendor/independent_owners.py','owners2942');root=load(src/'tools/root.py','root2942')
 template=read(src/'allocation/vendor/TEMPLATE.json.gz');plan=read(src/'allocation/vendor/PLAN.json.gz');providers=read(src/'allocation/PROVIDERS.json')
 for provider in providers.values():provider['actual_paid_profile']={int(r):n for r,n in provider['actual_paid_profile'].items()}
 old=read(src/'allocation/FILL.json.gz');oldorder=read(src/'allocation/ORDER.json');olddispatch=read(src/'allocation/DISPATCH.json');oldd={(s,r):p for s,r,p in olddispatch};oldprofile={int(k):v for k,v in read(src/'allocation/PROFILE.json').items()}
 k=5;T=74*k;order=[[s,r+74*j]for s,r in oldorder for j in range(k)];dispatch=[[s,r+74*j,p]for s,r,p in olddispatch for j in range(k)];d={(s,r):p for s,r,p in dispatch}
 win=engine.windows(template,order,T)
 rows=[[k*t+j,h,o+74*j,c,p,z]for t,h,o,c,p,z in old['rows']for j in range(k)]
 byrole={(v[0],v[1]):idx for idx,v in enumerate(rows)}
 journal=[]
 def move(t,h,j,dest,label):
  idx=byrole[k*t+j,h];row=rows[idx];w=providers[d[tuple(order[row[0]])]]['widths'][h];cap,lo,hi=win[dest[:2]];assert lo<row[0]<=hi
  before=list(row);rows[idx]=[row[0],h,*dest,0];journal.append(dict(mechanism=label,source=before,destination=list(rows[idx]),width=w))
 for j in range(k):move(56,134,j,(37+74*j,4,0),'neutral_width9_residual_relay')
 donor=[(33,0),(99,0),(142,0),(203,0),(492,76)]
 # All moved donor roles come from copy 0; one goes into each copy's new hole.
 # Try the zero-copy target at a time without its physical family already used.
 def family(row):
  _,_,o,c,p,_=row;return o*896+(2*plan['pairs'][str(c)]+plan['sides'][str(c)])*112+p
 target0=(34,4,1);tf=family([0,0,*target0,0]);used=defaultdict(set)
 for row in rows:used[row[0]].add(family(row))
 first=next((t,h)for t,h in donor if tf not in used[k*t]);donor.remove(first);donor=[first]+donor
 for j,(t,h)in enumerate(donor):move(t,h,0,(34+74*j,4,1),'five_copy_whole_role_concentration')
 # Compact every actual bin, preserving all times/helper identities/family labels.
 bybin=defaultdict(list)
 for idx,row in enumerate(rows):bybin[tuple(row[2:5])].append(idx)
 for ids in bybin.values():
  z=0
  for idx in ids:
   row=rows[idx];row[5]=z;z+=providers[d[tuple(order[row[0]])]]['widths'][row[1]]
 for entry in journal:entry['destination']=list(rows[byrole[entry['destination'][0],entry['destination'][1]]])
 fill={'columns':old['columns'],'dispatch_overrides':[],'method':'PR2942 five lockstep copies, five exact width-9 neutral relays, five whole-role concentration moves','rows':rows}
 expected=Counter({r:k*n for r,n in oldprofile.items()});expected.update({5:5,48:1,14:-5,3:-1});expected=Counter({r:n for r,n in expected.items()if n})
 result,_,_=engine.check(T,order,fill,d,expected,plan,template,providers)
 ideal={int(r):Q(n)*T for r,n in read(src/'certificates/RELAX-CAP.json')['idle_per_replica'].items()}
 actual={int(r):n for r,n in result['idle'].items()};assert actual==ideal
 # Keep the engine's historical physical field separate; actual changed words need 86 buffers.
 result['historical_engine_physical']=result.pop('physical');result['physical']=result['live']+408+8+86+2
 controls={}
 def reject(name,f):
  try:f()
  except (ValueError,AssertionError)as e:controls[name]=str(e)
  else:raise AssertionError('accepted corruption '+name)
 reject('missing_role',lambda:engine.check(T,order,{**fill,'rows':rows[:-1]},d,expected,plan,template,providers))
 badrow=list(rows[1]);badrow[0]=rows[0][0];badrow[1]=rows[0][1]
 reject('duplicate_helper',lambda:engine.check(T,order,{**fill,'rows':[rows[0],badrow]+rows[2:]},d,expected,plan,template,providers))
 badrow=list(rows[0]);badrow[5]=49
 reject('capacity_overflow',lambda:engine.check(T,order,{**fill,'rows':[badrow]+rows[1:]},d,expected,plan,template,providers))
 lo,hi=root.kappa_from_profile(expected,T,digits=25);base_lo,base_hi=root.kappa_from_profile(oldprofile,74,digits=25)
 assert lo>base_hi
 exact=dict(status='PASS_EXACT_COMPLETE_PROFILE_ROOT',lower=str(lo),upper=str(hi),lower_decimal=str(lo.numerator/lo.denominator),gain_lower=str(lo-base_hi),gain_upper=str(hi-base_lo),baseline_root_lower=str(base_lo),baseline_root_upper=str(base_hi),scope='Exact rational moment nomination only; new T370 native/source/global/outer admission remains separate.')
 for n,v in [('ORDER.json',order),('DISPATCH.json',dispatch),('FILL.json.gz',fill),('PROFILE.json',{str(r):n for r,n in sorted(expected.items())}),('PROVIDERS.json',providers),('JOURNAL.json',journal),('MOMENT.json',exact)]:save(out/n,v)
 result.update(status='PASS_T370_LITERAL_SOURCE_WINDOWS_FAMILIES_MASKS_PROFILE',controls=controls,source_head=pins['head'],moves=len(journal),scope='Finite whole-owner allocation only. Provider registry is unchanged, authenticated PR2942 input; no fresh native/global/outer claim.')
 save(out/'OWNERS.json',result)
 save(out/'ABLATIONS.json',dict(T=T,baseline_profile={str(r):k*n for r,n in sorted(oldprofile.items())},neutral_relay_profile={str(r):k*n for r,n in sorted(oldprofile.items())},both_profile={str(r):n for r,n in sorted(expected.items())},residual_only_paid_delta={},concentration_paid_delta={3:-1,5:5,14:-5,48:1},direct_concentration_without_relay='No cap-48 five-width-9 donor fits the original hole window (-1,59); a bounded exact census found zero. This is a scoped gadget check, not general infeasibility.'))
 for v in pins['files']:assert sha(src/v['path'])==v['sha256'],'source drift'
 save(out/'MANIFEST.json',{'files':{p.name:sha(p)for p in sorted(out.iterdir())if p.is_file()},'constructor_sha256':sha(Path(__file__))})
 print(json.dumps(dict(status=result['status'],T=T,roles=result['roles'],moves=len(journal),profile=dict(expected),root_lower=str(lo),root_upper=str(hi),gain_lower=str(lo-base_hi))),flush=True)
if __name__=='__main__':main()
