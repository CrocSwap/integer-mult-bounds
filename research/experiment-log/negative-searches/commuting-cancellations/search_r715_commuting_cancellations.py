"""Nominate duplicate transvection removal only through commuting gates at the same frame.
Exact frame, integer-support and955-column replay is mandatory; no compiler claim.
"""
from pathlib import Path
from collections import Counter
import json,sys,copy,hashlib
r=Path.cwd();out=r/'r715-commuting-cancellations';assert not out.exists();out.mkdir();src=r/'pr472-delivery-publication/research/r715-factor-replica84/data/word.json';w=json.loads(src.read_text())
sys.path.insert(0,str(r/'source454-review/e8-r740-replica32/code'));import e8core as E
L=E.Lat(w['lines']);masks=E.to_masks(w,L);before=E.replay(w,L=L,masks=masks,span_mode='z');assert not before['viol']
changes=[];tested=0
for ph in ['D','A','B','C']:
 gates=[[f,d,[s]] for f,d,ss in w[ph] for s in ss];active=[]
 for k,(f,d,ss) in enumerate(gates):
  s=ss[0];found=None
  for j in reversed(range(len(active))):
   ff,dd,tt,old=active[j];t=tt[0];tested+=1
   if (ff,dd,t)==(f,d,s):found=j;break
   if dd==s or d==t:break
  if found is not None:
   old=active.pop(found);changes.append(dict(phase=ph,removed_original_indices=[old[3],k],gate=[f,d,[s]]))
  else:active.append((f,d,ss,k))
 w[ph]=[[f,d,ss] for f,d,ss,k in active]
a=E.replay(w,L=L,masks=masks,span_mode='z');assert not a['viol'],a['viol'][:5]
raw=json.dumps(w,sort_keys=True,separators=(',',':')).encode();(out/'WORD.json').write_bytes(raw)
result=dict(status='PASS_EXACT_LOCAL_CANCELLATION_NOMINEE_GLOBAL_PENDING' if changes else 'PASS_NO_DUPLICATE_COMMUTING_CANCELLATIONS',source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),word_sha256=hashlib.sha256(raw).hexdigest(),changes=changes,commutation_comparisons=tested,before_profile=dict(before['H']),after_profile=dict(a['H']),columns=a['n'],scope='Phase-local identical-frame duplicate transvections separated only by scalar commuting gates. Exact finite local replay only. Native signed/formal validation and global compiler/physical admission pending for any changed word.')
(out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
