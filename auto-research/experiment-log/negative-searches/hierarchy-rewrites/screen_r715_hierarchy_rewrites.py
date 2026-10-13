"""Compile every legal two-symbol hierarchy alternative; no supplier admission claim."""
from pathlib import Path
from types import SimpleNamespace
from collections import Counter
import os,sys,json,hashlib,copy,time,heapq
r=Path.cwd();out=r/'r715-hierarchy-rewrite-screen';assert not out.exists();out.mkdir();os.environ['E8COORD']='ham'
sys.path[:0]=[str(r/'source463-review/code/rekid'),str(r/'source454-review/e8-r740-replica32/parent436/code/reuse')]
import c2x as C2,compile as C,fullword,reuse as RU,retime as RT,frames as Fm
source=json.loads((r/'r715-hierarchy-rewrite-inventory/HIERARCHY.json').read_text());inventory=json.loads((r/'r715-hierarchy-rewrite-inventory/RESULT.json').read_text());cases=[None]+inventory['candidates'];ledger=[]
def reordered_hierarchy(z):
 # Preserve sources; order other nodes by frame dimension and original ID subject to dependency readiness.
 N=len(z['content']);children=[list(k) if k else [] for k in z['kids']];users=[[] for _ in range(N)];pending=[len(k) for k in children]
 for u,ks in enumerate(children):
  for k in ks:users[k].append(u)
 done=list(range(120));ready=[]
 for u in done:
  for d in users[u]:
   pending[d]-=1
   if pending[d]==0:heapq.heappush(ready,(z['dim'][d],d))
 while ready:
  _,u=heapq.heappop(ready);done.append(u)
  for d in users[u]:
   pending[d]-=1
   if pending[d]==0:heapq.heappush(ready,(z['dim'][d],d))
 assert len(done)==N and len(set(done))==N,'cyclic or unsupported source-free symbol'
 ix={u:i for i,u in enumerate(done)}
 return SimpleNamespace(content=[z['content'][u] for u in done],frame=[z['frame'][u] for u in done],dim=[z['dim'][u] for u in done],kids=[tuple(ix[k] for k in children[u]) if children[u] else None for u in done],need=[set(ix[u] for u in ss) for ss in z['need']])
def histogram(word):
 dims=[Fm.closure(sum(1<<s for s in fr))[1] if fr else 0 for fr in word['frames']];cur=word['start'][:];H=Counter()
 def visit(reg,f):
  if cur[reg]!=f:
   old=cur[reg];a=sum(1<<x for x in word['frames'][old]);b=sum(1<<x for x in word['frames'][f]);assert a&~b==0
   d=dims[f]-dims[old];assert d>0;H[d]+=1;cur[reg]=f
 for ph in ['D','A']:
  for f,d,ss in word[ph]:
   for reg in [d]+ss:visit(reg,f)
 for reg in word['ret']:H[dims[cur[reg]]]+=1
 for ph in ['B','C']:
  for f,d,ss in word[ph]:
   for reg in [d]+ss:visit(reg,f)
 for reg,f in enumerate(word['final']):visit(reg,f)
 return dict(sorted(H.items()))
for i,case in enumerate(cases):
 tag='baseline' if case is None else 'candidate-'+str(i-1);d=out/tag;d.mkdir();start=time.monotonic();z=copy.deepcopy(source)
 if case is not None:
  assert z['kids'][case['rule']]==case['old'];z['kids'][case['rule']]=case['replacement']
 try:
  h=reordered_hierarchy(z);W=C2.compile2(h);bad=C.f2_check(W);assert not any(bad),'compiler F2 failure'
  raw=fullword.build(W);word,reuse=RU.reuse(raw);word,moves=RT.retime(word,sweeps=6,M=78);H=histogram(word)
  fullword.save(word,str(d/'WORD.json.gz'));result=dict(status='PASS_COMPILER_F2_REUSE_RETIMING_PROFILE_ONLY',id=tag,rule=case,helpers=word['R'],raw_helpers=W.nh,compiler_stats=W.stats,profile=H,moves=moves,word_sha256=hashlib.sha256(json.dumps(word,sort_keys=True,separators=(',',':')).encode()).hexdigest(),seconds=round(time.monotonic()-start,3),scope='Compiler F2 and monotone frame/profile screen only. Needs independent955-or-changed-stock dirty columns, native checks, new kernel/target-factor search, physical hosting and exact final composition. Fewer helpers alone is not a bound.')
 except Exception as e:result=dict(status='FAILED_CONSTRUCTION_SCREEN',id=tag,rule=case,error=repr(e),seconds=round(time.monotonic()-start,3))
 (d/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');ledger.append(result);(out/'LEDGER.json').write_text(json.dumps(ledger,indent=2)+'\n');print(tag,result['status'],result.get('helpers'),result.get('error',''),flush=True)
(out/'COMPLETE.json').write_text(json.dumps(dict(status='FINISHED',cases=len(ledger),failed=sum(x['status']=='FAILED_CONSTRUCTION_SCREEN' for x in ledger),min_helpers=min(x['helpers'] for x in ledger if 'helpers' in x)),indent=2)+'\n')
