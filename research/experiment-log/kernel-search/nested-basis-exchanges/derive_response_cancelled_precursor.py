"""Move the verified response-packet deletion before kernel selection to expose new first frames."""
from pathlib import Path
from collections import defaultdict
import sys,json,gzip,hashlib,importlib.util
r=Path.cwd();out=r/'response-cancelled-precursor';assert not out.exists();out.mkdir();sys.path[:0]=[str(r/'source454-review/e8-r740-replica32/code'),str(r/'source483-review/code')]
import e8core as E
from schur_constructor import rewrite,check
from algebra_constructor import responses
w=E.load_word(str(r/'r715-delivery-kernel-search/PRECURSOR.json.gz'));factors=json.loads((r/'source483-review/code/SELECTION473.json').read_text())['selected'];w,_=rewrite(w,factors);old=json.loads(json.dumps(w));groups=defaultdict(list)
for i,key in responses(w).items():groups[key].append(i)
removed=[]
for key,ids in sorted(groups.items()):removed+=ids if key[1]==0 else ids[:len(ids)//2*2]
w['A']=[g for i,g in enumerate(w['A']) if i not in set(removed)];w['C']=[[1,d,ss] for f,d,ss in reversed(w['A'])]
L=E.Lat(w['lines']);masks=E.to_masks(w,L);a=E.replay(w,L=L,masks=masks,span_mode='z');assert not a['viol'];check(w,[L.dim(m) for m in masks])
def first(c):
 z={}
 for ph in 'ABC':
  for f,d,ss in c[ph]:
   for h in [d]+ss:
    if h>=240 and c['frames'][f]:z.setdefault(h,f)
 return z
before,after=first(old),first(w);changed=[dict(helper=h,old_frame=before[h],new_frame=after[h],old_dim=L.dim(masks[before[h]]),new_dim=L.dim(masks[after[h]])) for h in before if before[h]!=after[h]];blob=json.dumps(w,sort_keys=True,separators=(',',':')).encode();(out/'PRECURSOR.json.gz').write_bytes(gzip.compress(blob,mtime=0));(out/'RESULT.json').write_text(json.dumps(dict(status='PASS_RESPONSE_CANCELLED_PRECURSOR_EXACT_LOCAL',removed_injections=removed,columns=a['n'],profile=dict(a['H']),changed_first_frames=changed,word_sha256=hashlib.sha256(blob).hexdigest()),indent=2)+'\n');print(changed,flush=True)
