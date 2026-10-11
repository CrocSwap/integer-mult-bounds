"""Three additional source aliases read through the existing target basis.
Prepared by eumemic with substantial OpenAI Codex assistance; Apache-2.0.
"""
from pathlib import Path
from collections import defaultdict
import importlib.util,json,sys
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;P=D.parent
sp=importlib.util.spec_from_file_location('retained493_target_setup',P/'targetagg/setup.py');previous=importlib.util.module_from_spec(sp);sp.loader.exec_module(previous)
m=previous.m;W=m.W;C=m.C;selection=json.loads((D/'selection.json').read_text());chosen=[];fresh={}
used={r[k]for r in m.selection+m.gauge_selection for k in('source','partner')};newused=set()
for raw in selection:
 r=dict(raw);role,n=r['role'],r['source'];entry=m.kpair[n]
 assert entry['carrier']==r['partner']and not({n,r['partner']}&(used|newused));newused.update((n,r['partner']))
 assert role not in W.gauge and role not in m.borrow and n not in m.by_source
 f=entry['mix_frame'];q=W.register(r['mix_basis']);assert C.sub(f,q)and C.sub(q,f)and C.dimf[f]==2
 assert W.role_ops[role][0]==r['first_operation']and C.sub(f,W.opframe[r['first_operation']])and C.nondeg(f)
 r['mix_frame']=f;chosen.append(r);fresh[role]=r
 z=dict(role=role,frame=f,dim=2,targets=sorted(m.adj[role]));W.gauge[role]=z;W.w['gauges'].append(z);W.readtime[role]=0;W.w['reads'][str(role)]=len(W.phase1)
 m.borrow[role]=n;m.by_source[n]=r;m.gauge_borrow[role]=n;m.gauge_selection.append(r);m.extra_byrole[role]=r
assert len(chosen)==3 and len(newused)==6
W.order=list(fresh)+W.order;m.at=defaultdict(list)
for role in W.order:m.at[W.readtime[role]].append(role)
m.regs=sorted(set(W.phys.values())-set(m.borrow)-m.removed);m.idx={r:2*W.v+j for j,r in enumerate(m.regs)}
assert len(m.borrow)==496 and len(m.regs)==16618 and len(m.extra_byrole)==25
W.exact_frames();m.fresh=fresh
