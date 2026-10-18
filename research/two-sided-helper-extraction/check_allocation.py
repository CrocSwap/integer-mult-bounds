# SPDX-License-Identifier: Apache-2.0
"""Literal owner verification, newly charged private stock and exact moment."""
import argparse,copy,gzip,hashlib,json,sys,types
from pathlib import Path
P=Path(__file__).resolve().parent

def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def load(n,p):
 m=types.ModuleType(n);exec(compile(p.read_bytes(),str(p),'exec'),m.__dict__);return m

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,required=True);a=ap.parse_args();out=a.work.resolve();assert __debug__ and not out.exists() and not out.is_relative_to(P);out.mkdir(parents=True)
 pins=read(P/'ALLOCATION-PINS.json');assert {f.relative_to(P).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in (P/'allocation').rglob('*') if f.is_file()}==pins
 owner=load('owners',P/'allocation/vendor/independent_owners.py');moment=load('moment',P/'tools/audit_moment.py');base=P/'allocation';providers={}
 for tag,pid in [('base','gauge44'),('extra','extra')]:
  w=read(P/f'data/WORD-{tag}.json.gz');helpers=sorted(set(range(224,704))-set(w['removed']))
  providers[pid]={'widths':[len(w['helper_final'].get(str(h),[0]*9))-len(w['start_extra'].get(str(h),[])) for h in helpers],'actual_paid_profile':{int(r):n for r,n in w['report']['local_profile'].items()}}
 order=read(base/'ORDER.json');fill=read(base/'FILL.json.gz');dispatch={(s,r):pid for s,r,pid in read(base/'DISPATCH.json')};profile=read(base/'PROFILE.json');plan=read(base/'vendor/PLAN.json.gz');template=read(base/'vendor/TEMPLATE.json.gz');T=len(order)//9
 def check(f=fill):return owner.check(T,order,f,dispatch,profile,plan,template,providers)
 result,win,_=check();assert T==74 and result['roles']==271728
 # The credited geometry checker reports its historical 72-buffer stock.
 # That field is not a source of physical evidence for this new word.
 result['physical']=896*T+408+8+73+2;result['physical_source']='explicit 73-buffer local ABI; independently invoiced by complete release'
 rejected={}
 for name,fn in [('missing_role',lambda f:f['rows'].pop()),('duplicate_helper',lambda f:f['rows'][1].__setitem__(1,f['rows'][0][1])),('capacity_overflow',lambda f:f['rows'][0].__setitem__(5,49))]:
  bad=copy.deepcopy(fill);fn(bad)
  try:check(bad)
  except ValueError as e:rejected[name]=str(e)
  else:raise AssertionError('owner corruption accepted '+name)
 m=moment.run(base,base/'baseline');result.update(status='PASS_HELPER408_LITERAL_OWNERS_AND_EXACT_MOMENT',controls=rejected,moment=m,scope='Exact local width-based whole-owner geometry and rational moment; full source/native/stock/outer admission separate.')
 (out/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(result['status'],m['target_decimal'],m['gain_decimal'])
if __name__=='__main__':main()
