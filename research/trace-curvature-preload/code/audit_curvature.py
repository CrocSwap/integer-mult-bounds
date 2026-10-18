"""Exact finite curvature-cone certificate; independent of moment engines."""
import json,sys
from pathlib import Path

def certificate(old,new):
 old={int(r):n for r,n in old.items()};new={int(r):n for r,n in new.items()}
 assert all(isinstance(n,int) and n>=0 for n in list(old.values())+list(new.values()))
 assert all(r>=1 for r in [*old,*new])
 R=max([1,*old,*new]);d={r:new.get(r,0)-old.get(r,0) for r in range(1,R+1)}
 assert sum(d.values())==sum(r*n for r,n in d.items())==0
 C={j:sum((j-r)*d[r]for r in range(1,j))for j in range(1,R+1)}
 assert C[1]==C[R]==0 and all(x>=0 for x in C.values())
 assert all(d[r]==C.get(r-1,0)-2*C[r]+C.get(r+1,0)for r in d)
 assert any(C.values())
 return {'delta':{str(r):n for r,n in d.items()if n},'curvature':{str(r):n for r,n in C.items()if n},'count':sum(new.values()),'rank_mass':sum(r*n for r,n in new.items())}

def main():
 baseline,local,invoice,out=map(Path,sys.argv[1:5]);old=json.loads(baseline.read_text())['nine']['profile']
 loc=json.loads(local.read_text());new=json.loads(invoice.read_text())['bit_profile']
 # Native legality receipt carries the actual regenerated frame-chain profile.
 for key in ['paid_histogram','profile','paid_profile','histogram','rank_histogram']:
  if key in loc:loc=loc[key];break
 if isinstance(loc,list):loc=dict(loc)
 if not all(str(k).isdigit()for k in loc):raise AssertionError(('unknown native histogram schema',list(loc)))
 localold={1:1200,2:1440,4:180,6:120,8:9}
 a=certificate(localold,loc);b=certificate(old,new)
 assert a['curvature']=={'2':60} and b['curvature']=={'2':17280}
 assert b['delta']=={r:288*n for r,n in a['delta'].items()}
 controls=[]
 for name,x,y in [('reverse',new,old),('missing_rank3',old,{**new,'3':int(new['3'])-1})]:
  try:certificate(x,y)
  except AssertionError:controls.append(name)
  else:raise AssertionError(('control accepted',name))
 out.write_text(json.dumps({'status':'PASS_CURVATURE_CONE','local':a,'global':b,'negative_controls':controls},indent=2)+'\n')
if __name__=='__main__':main()
