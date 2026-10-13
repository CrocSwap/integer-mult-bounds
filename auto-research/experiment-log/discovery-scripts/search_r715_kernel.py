"""Fresh coordinate-response kernel nominations on PR463; exact local replay required."""
from pathlib import Path
from collections import Counter
import sys,json,gzip,math,subprocess
r=Path.cwd();out=r/'r715-kernel-search';out.mkdir(exist_ok=True)
sys.path[:0]=[str(r/'source454-review/e8-r740-replica32/code'),str(r/'source454-review/r740-hosted-rank149/code')]
import e8core as E
from hosted_kernel import kernel
w=E.load_word(str(r/'source463-review/data/R715_FP_final.json.gz'));L=E.Lat(w['lines']);masks=E.to_masks(w,L);dims=[L.dim(f) for f in masks]
a=E.replay(w,L=L,masks=masks,span_mode='z');assert not a['viol'],a['viol'][:5]
(out/'BASE-LOCAL.json').write_text(json.dumps(dict(profile=dict(a['H']),dims=dims,columns=a['n']),indent=2)+'\n');print('BASE PASS',a['n'],dict(a['H']),flush=True)
first={};response=Counter();v=w['v'];R=w['R']
for f,d,ss in w['D']:
 for h in ss:response[h]^=1<<(d-v)
for ph in ('A','B','C'):
 for f,d,ss in w[ph]:
  for h in [d]+ss:
   if h>=2*v and masks[f]:first.setdefault(h,f)
frames=[]
for fi,mask in enumerate(masks):
 axes={j for i in w['frames'][fi] for j,x in enumerate(w['lines'][i]) if x}
 if 0<dims[fi]<w['h'] and len(axes)==dims[fi]:frames.append(fi)
for penalty in [0.,-0.65,1.]:
 entries=[];piv=set();donors={};H=a['H'].copy();ENT=0;history=[]
 cost=lambda rank:rank*math.log(78/rank) if rank else 0
 while True:
  best=None
  for fi in frames:
   mask=masks[fi];er=dims[fi]
   avail=[h for h in first if h not in piv and h not in w['ret'] and (h not in donors or donors[h]==mask) and mask&masks[first[h]]==mask]
   avail.sort(key=lambda h:(h not in donors,dims[first[h]],h));basis={}
   for h in avail:
    x=response[h];subset=set()
    for bit,(row,rr) in sorted(basis.items(),reverse=True):
     if x>>bit&1:x^=row;subset^=rr
    if x:basis[x.bit_length()-1]=(x,subset^{h});continue
    if h in donors:continue
    delta=Counter();fd=dims[first[h]];delta[fd]-=1;delta[fd-er]+=1
    for d in subset:
     if d not in donors:
      fd=dims[first[d]];delta[fd]-=1;delta[er]+=1;delta[fd-er]+=1
    score=sum(cost(k)*n for k,n in delta.items())+penalty*er
    if score < -1e-10 and (best is None or score<best[0]):best=(score,fi,h,sorted(subset),delta)
  if best is None:break
  score,fi,h,ds,delta=best;entries.append([w['frames'][fi],h,ds]);piv.add(h);donors.update({d:masks[fi] for d in ds});H.update(delta);ENT+=dims[fi];history.append(dict(pivot=h,entrance=dims[fi],score=score))
  if len(entries)%20==0:print('penalty',penalty,'entries',len(entries),'rank',ENT,flush=True)
 tag=str(penalty).replace('-','neg').replace('.','p');word,ne,nr,nd=kernel(w,entries);audit=E.replay(word,span_mode='z');assert not audit['viol'];assert {k:n for k,n in H.items() if k and n}==dict(audit['H'])
 wp=out/f'KERNEL-{tag}.json';wp.write_text(json.dumps(word,separators=(',',':')))
 (out/f'SELECTION-{tag}.json').write_text(json.dumps(dict(entries=entries,entrance_rank=nr,donors=nd,history=history,local_profile=dict(audit['H'])),indent=2)+'\n')
 subprocess.run([sys.executable,'-B',str(r/'source463-review/code/rekid/mix_target_nochain.py'),str(wp),str(out/f'MIXED-{tag}.json')],check=True)
 print('KERNEL LOCAL PASS',tag,ne,nr,nd,flush=True)
