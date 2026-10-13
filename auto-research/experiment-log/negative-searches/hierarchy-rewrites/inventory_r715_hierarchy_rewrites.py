"""Read the pinned hierarchy as inert data and enumerate legal two-term rule rewrites.
No pickle-supplied callable is executed. This is a structural inventory, not a bound.
"""
from pathlib import Path
from collections import defaultdict,Counter
import pickle,io,json,hashlib
r=Path.cwd();out=r/'r715-hierarchy-rewrite-inventory';assert not out.exists();out.mkdir();src=r/'source463-review/data/R715_FP_hier.h'
class Data:pass
class Restricted(pickle.Unpickler):
 def find_class(self,module,name):
  if (module,name)==('ham1','SH'):return Data
  raise ValueError(('unexpected pickle global',module,name))
h=Restricted(io.BytesIO(src.read_bytes())).load();V=120;N=len(h.content);assert len(h.frame)==len(h.dim)==len(h.kids)==N and len(h.need)==V
need=set();todo=[u for ss in h.need for u in ss]
while todo:
 u=todo.pop()
 if u in need:continue
 need.add(u)
 if h.kids[u]:todo.extend(h.kids[u])
for u in need:
 if u>=V:
  assert len(h.kids[u])==2;a,b=h.kids[u];assert h.content[u]==h.content[a]^h.content[b]
  assert h.frame[a]&~h.frame[u]==0 and h.frame[b]&~h.frame[u]==0
from functools import lru_cache
@lru_cache(None)
def descendants(u):return frozenset([u]).union(*(descendants(k) for k in h.kids[u])) if h.kids[u] else frozenset([u])
# Force a full acyclic traversal before nominations.
for u in need:descendants(u)
bycontent=defaultdict(list)
for w in need:
 if w>=V:bycontent[h.content[w]].append(w)
options=[];pairs=0
for x in range(N):
 for y in range(x+1,N):
  pairs+=1
  for w in bycontent.get(h.content[x]^h.content[y],[]):
   if (x,y)==tuple(sorted(h.kids[w])) or w in (x,y):continue
   if (h.frame[x]|h.frame[y])&~h.frame[w]:continue
   if w in descendants(x) or w in descendants(y):continue
   seen=set();todo=[u for ss in h.need for u in ss]
   while todo:
    u=todo.pop()
    if u in seen:continue
    seen.add(u)
    kids=(x,y) if u==w else h.kids[u]
    if kids:todo.extend(kids)
   options.append(dict(rule=w,old=list(h.kids[w]),replacement=[x,y],needed_symbols_before=len(need),needed_symbols_after=len(seen),removed_needed=sorted(need-seen),added_needed=sorted(seen-need),same_frame_forward_dependency=any(h.dim[k]==h.dim[w] and k>w for k in [x,y])))
options.sort(key=lambda z:(z['needed_symbols_after'],z['rule'],z['replacement']))
raw=dict(content=h.content,frame=h.frame,dim=h.dim,kids=h.kids,need=[sorted(s) for s in h.need]);(out/'HIERARCHY.json').write_text(json.dumps(raw,separators=(',',':'))+'\n')
res=dict(status='PASS_ACYCLIC_XOR_FRAME_RULE_INVENTORY',source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),symbols=N,needed_symbols=len(need),pairs_enumerated=pairs,legal_alternatives=len(options),fewer_needed_candidates=sum(x['needed_symbols_after']<len(need) for x in options),candidates=options,scope='Exact hierarchy XOR identities, frame containment and acyclicity only. Number of needed symbols is a discovery proxy, not helper stock or paid recurrence. Requires fresh compiler ordering, raw word/reuse/retiming and all native/global checks.')
(out/'RESULT.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps({k:v for k,v in res.items() if k!='candidates'}),flush=True)
