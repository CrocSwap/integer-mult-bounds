"""Exact auxiliary-line response-kernel constructor (stdlib only).
python nonroot_constructor.py SOURCE SELECTION OUTPUT_DIRECTORY
Imports retained schur_constructor.py for independent finite replay.
"""
from pathlib import Path
from fractions import Fraction as Q
import json,copy,hashlib,argparse
from schur_constructor import rank,check
canon=lambda z:json.dumps(z,sort_keys=True,separators=(',',':')).encode()
def annihilator(rows):
 a=[list(map(Q,r))for r in rows];r=0;piv=[]
 for c in range(8):
  j=next((j for j in range(r,len(a))if a[j][c]),None)
  if j is None:continue
  a[r],a[j]=a[j],a[r];q=a[r][c];a[r]=[x/q for x in a[r]]
  for j in range(len(a)):
   if j!=r and a[j][c]:q=a[j][c];a[j]=[x-q*y for x,y in zip(a[j],a[r])]
  piv.append(c);r+=1
 out=[]
 for c in range(8):
  if c in piv:continue
  b=[Q(0)]*8;b[c]=Q(1)
  for j,k in enumerate(piv):b[k]=-a[j][c]
  out.append(b)
 return out

def construct(z,selection,controls=True):
 assert z['v']==120 and z['R']==715
 original=copy.deepcopy(z);basis=selection['auxiliary_lines'];assert len(basis)==len({tuple(b)for b in basis});oldlines=len(z['lines']);oldframes=len(z['frames']);w=copy.deepcopy(z)
 for ix,ff in enumerate(z['frames']):
  ann=annihilator([z['lines'][i]for i in ff]);w['frames'][ix]=ff+[oldlines+j for j,b in enumerate(basis)if all(sum(x*y for x,y in zip(a,b))==0 for a in ann)]
 w['lines']+=basis;w['frames']+=[[oldlines+j]for j in range(len(basis))]
 oldp={h for h in range(240,955)if w['start'][h]};head=0
 for f,d,ss in w['A']:
  if not all(s in oldp for s in ss):break
  head+=1
 newp={c['pivot']for c in selection['entries']};assert len(newp)==len(selection['entries'])and not(oldp&newp)
 oldd={e[1]for e in w['A'][:head]};assert not(newp&oldd)
 dims=[rank([w['lines'][i]for i in f])for f in w['frames']];base=check(w,dims);before=check(original,[rank([original['lines'][i]for i in f])for f in original['frames']]);assert base==before
 pre=copy.deepcopy(w['A'][:head]);entries=[]
 for c in selection['entries']:
  p=c['pivot'];f=oldframes+c['line_index'];assert dims[f]==1;w['start'][p]=f
  for d in c['donors']:
   assert d not in oldp|newp and d!=p;pre.append([f,d,[p]])
  entries.append(dict(pivot=p,frame=f,basis=basis[c['line_index']],donors=c['donors']))
 pre.sort(key=lambda e:(e[1],dims[e[0]],e[0],e[2]));w['A']=pre+w['A'][head:];w['C']=[[1,d,ss]for f,d,ss in reversed(w['A'])];w['D']=[[f,d,[s for s in ss if s not in newp]]for f,d,ss in w['D']];w['D']=[e for e in w['D']if e[2]]
 got=check(w,dims);delta={r:got['profile'].get(r,0)-base['profile'].get(r,0)for r in set(got['profile'])|set(base['profile'])};delta={r:n for r,n in delta.items()if n};assert sum(r*n for r,n in delta.items())==-len(entries)
 ctl={}
 if controls:
  for p in sorted(newp):
   bad=copy.deepcopy(w);bad['A']=[e for i,e in enumerate(w['A'])if not(i<len(pre)and e[2]==[p])];bad['C']=[[1,d,ss]for f,d,ss in reversed(bad['A'])]
   try:check(bad,dims)
   except AssertionError as e:ctl[str(p)]=str(e)
   else:raise AssertionError('vacuous omission control')
 return w,dict(status='PASS_SOURCE_BOUND_AUXILIARY_LINE_KERNEL',ports=120,line_count=len(w['lines']),helper_count=715,new_entries=entries,old_prefix_rows=head,new_prefix_rows=len(pre),base=base,candidate=got,delta=delta,controls=ctl,scope='Exact rational auxiliary-line closure, unchanged original frame geometry, all955 arbitrary-dirty binary columns and integer operand support. Physical paired hosting and final global invoice checked separately.')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('source',type=Path);ap.add_argument('selection',type=Path);ap.add_argument('out',type=Path);a=ap.parse_args();raw=a.source.read_bytes();s=json.loads(a.selection.read_bytes());assert hashlib.sha256(raw).hexdigest()==s['source_sha256'];assert not a.out.exists();w,r=construct(json.loads(raw),s);b=canon(w);sha=hashlib.sha256(b).hexdigest();assert sha==s['candidate_sha256'];r.update(source_sha256=s['source_sha256'],candidate_sha256=sha);a.out.mkdir(parents=True);(a.out/'word.json').write_bytes(b);(a.out/'NONROOT-AUDIT.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k]for k in ['status','source_sha256','candidate_sha256','delta']}))
if __name__=='__main__':main()
