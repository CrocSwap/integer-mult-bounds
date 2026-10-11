"""Pure exact R740 response-kernel reconstruction, with an explicit RHS convention."""
from pathlib import Path
from hashlib import sha256
from collections import defaultdict,Counter
import json,copy,sys,gzip

def reconstruct(raw,selection):
 assert sha256(raw).hexdigest()==selection['source_sha256'];c=json.loads(raw);v=c['v'];n=2*v+c['R'];assert(v,c['R'])==(120,740)
 rows=[{i:1}for i in range(n)]
 def add(a,b,k=1):
  for i,x in b.items():
   q=a.get(i,0)+k*x
   if q:a[i]=q
   else:a.pop(i,None)
 for f,d,ss in c['A']:
  for s in ss:add(rows[d],rows[s])
 copies=[dict(rows[q])for q in c['ret']]
 for t,ss in enumerate(c['scatter']):
  for s in ss:add(rows[v+t],copies[s])
 for f,d,ss in c['B']:
  for s in ss:add(rows[d],rows[s],-1 if d<v else 1)
 K={h:tuple(rows[v+t].get(h,0)for t in range(v))for h in range(2*v,n)}
 frames=list(map(set,c['frames']));first={}
 for ph in('A','B','C'):
  for f,d,ss in c[ph]:
   for h in[d]+ss:
    if h>=2*v and f:first.setdefault(h,f)
 piv=set();donors={};by=defaultdict(list);signs=[];rank=0
 for z in selection['entries']:
  p,f=z['pivot'],z['frame'];ds=z['donor_coefficients'];assert frames[f]==set(z['entrance'])and frames[f]
  assert p not in piv and p not in donors and p not in c['ret']and c['start'][p]==0
  assert frames[f]<=frames[first[p]] and len(dict(ds))==len(ds)
  for d,a in ds:
   assert a in(-1,1)and d!=p and d not in piv and d not in c['ret']and c['start'][d]==0
   assert donors.setdefault(d,f)==f and frames[f]<=frames[first[d]]
   by[d,f].append(p);signs.append(dict(pivot=p,donor=d,entrance_coefficient=-a,coda_coefficient=a))
  assert all(K[p][i]==sum(a*K[d][i]for d,a in ds)for i in range(v))
  piv.add(p);rank+=z['rank']
 assert not piv&set(donors);assert len(piv)==selection['pivots']and len(donors)==selection['donor_count']and rank==selection['entrance_rank']
 w=copy.deepcopy(c)
 for z in selection['entries']:w['start'][z['pivot']]=z['frame']
 w['D']=[[f,d,[s for s in ss if s not in piv]]for f,d,ss in w['D']]
 w['A']=[[f,d,sorted(ps)]for(d,f),ps in sorted(by.items())]+w['A'];w['C']+=[[c['final'][0],d,sorted(ps)]for(d,f),ps in sorted(by.items())]
 data=json.dumps(w,sort_keys=True,separators=(',',':')).encode();assert sha256(data).hexdigest()==selection['output_sha256']
 return data,dict(status='PASS_SOURCE_BOUND_EXACT_INTEGER_R740_RELATION_RECONSTRUCTION',source_sha256=sha256(raw).hexdigest(),output_sha256=sha256(data).hexdigest(),pivots=len(piv),donors=len(donors),entrance_rank=rank,coefficient_convention='Selection donor_coefficients are the RHS of K_p=sum(a_d*K_d). The signed prelude uses -a_d, its matching appended coda uses +a_d. Every unchanged inherited C cleanup uses -1. Native F2 bytes remain all plus.',signed_arcs=signs,scope='Pure exact response algebra and physical F2 reconstruction; complete signed decoder, ledgers, banks, common geometry, finite invoice and exact pricing are separate fresh gates.')

def main():
 source,selection,out=map(Path,sys.argv[1:]);assert not out.exists();s=json.loads(selection.read_bytes());raw=source.read_bytes()
 if source.suffix=='.gz':raw=gzip.decompress(raw)
 data,r=reconstruct(raw,s);controls=[]
 for name in('wrong source','wrong relation sign','missing donor','duplicate pivot','wrong entrance'):
  rr=raw;t=copy.deepcopy(s)
  if name=='wrong source':rr+=b' '
  elif name=='wrong relation sign':t['entries'][0]['donor_coefficients'][0][1]*=-1
  elif name=='missing donor':t['entries'][0]['donor_coefficients'].pop()
  elif name=='duplicate pivot':t['entries'][1]['pivot']=t['entries'][0]['pivot']
  else:t['entries'][0]['entrance']=[]
  try:reconstruct(rr,t)
  except AssertionError:controls.append(name)
  else:raise AssertionError(name)
 out.mkdir(parents=True);(out/'word.json').write_bytes(data);r.update(selection_sha256=sha256(selection.read_bytes()).hexdigest(),controls=controls)
 (out/'RECEIPT.json').write_text(json.dumps(r,sort_keys=True,indent=2)+'\n');print(r['status'])
if __name__=='__main__':main()
