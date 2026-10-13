"""Map the prior kernel by response and clean-state signatures, recheck every retained relation."""
from pathlib import Path
from collections import Counter,defaultdict
import json,gzip,sys,hashlib
r=Path.cwd();out=r/'r714-kernel-transfer';assert not out.exists();out.mkdir();sys.path[:0]=[str(r/'source454-review/e8-r740-replica32/code'),str(r/'source454-review/r740-hosted-rank149/code')]
import e8core as E
from hosted_kernel import kernel
old=E.load_word(str(r/'r715-delivery-kernel-search/PRECURSOR.json.gz'));new=E.load_word(str(r/'r714-precursor-check/PRECURSOR.json.gz'));sel=json.loads((r/'r715-warm-pooled-search/best-36/SELECTION.json').read_text())['entries']
def signatures(w):
 v=w['v'];n=2*v+w['R'];resp=Counter();state=[1<<i if i<v else 0 for i in range(n)];first={};trace=defaultdict(list)
 for f,d,ss in w['D']:
  for h in ss:
   if h>=2*v:resp[h]^=1<<(d-v)
 for f,d,ss in w['A']:
  for h in [d]+ss:
   if h>=2*v and w['frames'][f]:first.setdefault(h,sum(1<<i for i in w['frames'][f]))
  for h in ss:state[d]^=state[h]
  trace[d].append(state[d])
 for f,d,ss in w['B']:
  for h in ss:
   if h>=2*v and w['frames'][f]:first.setdefault(h,sum(1<<i for i in w['frames'][f]))
 return {h:(resp[h],state[h],tuple(trace[h])) for h in range(2*v,n)},first,resp
a,af,ar=signatures(old);b,bf,br=signatures(new);index=defaultdict(list)
for h,key in b.items():index[key].append(h)
mapping={h:index[key][0] for h,key in a.items() if len(index[key])==1};chosen=[];skipped=[];pivs=set();donorat={}
for ee,h,ds in sel:
 E_mask=sum(1<<i for i in ee);regs=[h]+ds
 if not all(x in mapping for x in regs):skipped.append(dict(pivot=h,reason='unmatched signature'));continue
 pp=mapping[h];dd=[mapping[d] for d in ds];v=br[pp]
 for d in dd:v^=br[d]
 if v or len(set([pp]+dd))!=len([pp]+dd) or any(E_mask&~bf[x] for x in [pp]+dd) or pp in pivs or pp in donorat or any(d in pivs or(d in donorat and donorat[d]!=E_mask) for d in dd):skipped.append(dict(pivot=h,reason='relation/frame/role mismatch'));continue
 chosen.append([ee,pp,dd]);pivs.add(pp);donorat.update({d:E_mask for d in dd})
w,ne,nr,nd=kernel(new,chosen);audit=E.replay(w,span_mode='z');assert not audit['viol'];(out/'WORD.json').write_text(json.dumps(w,sort_keys=True,separators=(',',':')));(out/'SELECTION.json').write_text(json.dumps(dict(entries=chosen,entrance_rank=nr,donors=nd),indent=2)+'\n');result=dict(status='PASS_PARTIAL_KERNEL_TRANSFER_EXACT_LOCAL_ONLY',matched_helpers=len(mapping),old_helpers=old['R'],new_helpers=new['R'],entries=ne,entrance_rank=nr,donors=nd,skipped=skipped,columns=audit['n'],profile=dict(audit['H']),mapping=mapping);(out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print({k:v for k,v in result.items() if k not in ('mapping','skipped')},flush=True)
