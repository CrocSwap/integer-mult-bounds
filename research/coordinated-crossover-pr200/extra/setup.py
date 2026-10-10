"""Source493 role setup; actual word executed by targetagg/replay.py.
Prepared with substantial OpenAI Codex assistance; Apache-2.0.
The22 extra source mixes retime existing K mixes and unmixes.
"""
from pathlib import Path
from collections import defaultdict
import importlib.util,json,sys
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;P=D.parent/'newg'
sp=importlib.util.spec_from_file_location('source471base',P/'replay.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
extra=json.loads((D/'selection.json').read_text());oldborrow=m.borrow.copy();used={s for r in m.selection+m.gauge_selection for s in[r['source'],r['partner']]};assert len(oldborrow)==471
for r in extra:
 role,n=r['role'],r['source'];e=m.kpair[n];assert e['carrier']==r['partner']and e['mix_frame']==r['mix_frame'];assert not({n,r['partner']}&used);used.update([n,r['partner']])
 assert role not in m.borrow and role not in m.W.gauge and role not in m.W.donor and role not in m.removed and role not in m.W.source.values()
 assert set(m.adj[role])==set(r['targets'])and set(m.adj[role].values())=={1}
 assert role not in {s for i in m.W.phase1 for s in m.W.ops[i][:2]};f=m.W.register(r['split_gauge_basis'])if'split_gauge_basis'in r else e['mix_frame'];assert m.C.dimf[f]in(2,4) and m.C.nondeg(f)and m.C.sub(f,m.W.opframe[m.W.role_ops[role][0]])
 assert all(all(m.W.module.dot(m.C.cov[t],b)==0 for b in m.C.B[f])for t in r['targets'])
 z=dict(role=role,frame=f,dim=m.C.dimf[f],targets=r['targets']);m.W.gauge[role]=z;m.W.w['gauges'].append(z);m.W.readtime[role]=0;m.W.w['reads'][str(role)]=len(m.W.phase1)
 m.borrow[role]=n;m.by_source[n]=r;m.gauge_borrow[role]=n;m.gauge_selection.append(r)
m.W.order=[r['role']for r in extra]+m.W.order
# The third ordered rank4 source entrance follows all retained new-source gauges.
m.W.readtime[14073]=168;m.W.w['reads']['14073']=len(m.W.phase1)+168
m.W.order.remove(14073);at_index=max(m.W.order.index(r['role'])for r in m.new_gauge_selection)+1;m.W.order.insert(at_index,14073)
m.at=defaultdict(list)
for role in m.W.order:m.at[m.W.readtime[role]].append(role)
m.regs=sorted(set(m.W.phys.values())-set(m.borrow)-m.removed);m.idx={r:2*m.W.v+j for j,r in enumerate(m.regs)};assert len(m.borrow)==493 and len(m.regs)==16621
assert all(0<=m.W.readtime[s]<=m.W.first[s]for s in m.W.gauge);m.W.exact_frames()
m.extra_roles={r['role']for r in extra};m.extra_selection=extra
