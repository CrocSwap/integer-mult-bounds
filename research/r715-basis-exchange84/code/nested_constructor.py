"""Finite nested-donor flag constructor; full all-size interfaces remain conditional."""
from pathlib import Path
import argparse,json,hashlib,copy
from schur_constructor import check,rank
canonical=lambda w:json.dumps(w,sort_keys=True,separators=(',',':')).encode()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('source',type=Path);ap.add_argument('selection',type=Path);ap.add_argument('out',type=Path);a=ap.parse_args();assert not a.out.exists();raw=a.source.read_bytes();s=json.loads(a.selection.read_bytes());assert hashlib.sha256(raw).hexdigest()==s['source_sha256'];w=json.loads(raw);dims=[rank([w['lines'][i]for i in f])for f in w['frames']];before=check(w,dims);up={u['pivot']:u for u in s['upgrades']};head=s['source_kernel_rows'];pivs={r for r in range(2*w['v'],2*w['v']+w['R'])if w['start'][r]};assert all(all(r in pivs for r in ss)for f,t,ss in w['A'][:head]);assert not all(r in pivs for r in w['A'][head][2]);z=copy.deepcopy(w)
 for p,u in up.items():
  old,new=u['old_frame'],u['new_frame'];assert w['start'][p]==old;assert set(w['frames'][old])<set(w['frames'][new]);z['start'][p]=new
 pre=[]
 for f,t,ss in w['A'][:head]:
  by={}
  for p in ss:by.setdefault(up[p]['new_frame']if p in up else f,[]).append(p)
  for ff,ps in sorted(by.items()):pre.append([ff,t,ps])
 pre.sort(key=lambda g:(g[1],dims[g[0]],g[0],g[2]));last={};donors=set()
 for f,t,ss in pre:
  assert t not in pivs;donors.add(t)
  if t in last:assert set(w['frames'][last[t]])<=set(w['frames'][f])
  last[t]=f
 z['A']=pre+w['A'][head:];assert len(pre)==s['candidate_kernel_rows'];assert all(w[k]==z[k]for k in w if k not in ['A','start']);after=check(z,dims);assert after['profile']=={int(k):v for k,v in s['profile'].items()};controls={}
 for i,(f,t,ss)in enumerate(pre):
  changed=[p for p in ss if p in up]
  if not changed:continue
  bad=copy.deepcopy(z);bad['A'].pop(i)
  try:check(bad,dims)
  except AssertionError:controls[str(i)+' missing correction']='REJECTED'
  else:raise AssertionError('vacuous omission control')
  bad=copy.deepcopy(z);bad['A'][i][0]=up[changed[0]]['old_frame']
  try:check(bad,dims)
  except AssertionError:controls[str(i)+' obsolete frame']='REJECTED'
  else:raise AssertionError('vacuous frame control')
 raw=canonical(z);assert hashlib.sha256(raw).hexdigest()==s['candidate_sha256'];a.out.mkdir(parents=True);(a.out/'word.json').write_bytes(raw);r=dict(status='PASS_NESTED_DONOR_FLAG_CONSTRUCTION',source_sha256=s['source_sha256'],candidate_sha256=s['candidate_sha256'],upgrades=s['upgrades'],source_kernel_rows=head,candidate_kernel_rows=len(pre),distinct_donor_roles=len(donors),monotone_donor_chains=True,before=before,after=after,controls=controls,scope='Exact955GF2dirtycolumns,rational ranks,clean integer operand spans,finite monotone correction schedule; native signed columns/global invoice/all-size interfaces separate.');(a.out/'NESTED-AUDIT.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
if __name__=='__main__':main()
