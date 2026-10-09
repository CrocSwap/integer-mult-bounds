"""Exact setup for492 source heads,87 equal groups and8 integer rank groups.
Prepared with substantial OpenAI Codex assistance; Apache-2.0.
"""
from pathlib import Path
from collections import defaultdict
import importlib.util,json,sys
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;P=D.parent
sp=importlib.util.spec_from_file_location('ordered492_setup',P/'extra/setup.py');source=importlib.util.module_from_spec(sp);sp.loader.exec_module(source)
m=source.m;extra=source.extra;W=m.W;C=m.C;groups=json.loads((D/'selection.json').read_text())['groups'];agg=[];role_groups=defaultdict(list);owner={}
for k,g in enumerate(groups):
 F=W.register(g['frame_basis']);ts=g['targets'];assert C.nondeg(F)and g['pivot']in ts
 for t in ts:assert t not in owner;owner[t]=k
 for s in g['roles']:
  assert set(ts)<=set(m.adj[s])and len({m.adj[s][t]for t in ts})==1 and C.sub(W.gauge[s]['frame'],F);role_groups[s].append(k)
 agg.append(dict(targets=ts,pivot=g['pivot'],roles=g['roles'],frame=F))
assert len(agg)==87 and len(owner)==324
byrole={r['role']:r for r in extra};rf={}
for k,g in enumerate(agg):
 for role in g['roles']:
  r=byrole.get(role);f=W.gauge[role]['frame']
  if r and'split_gauge_basis'in r and r['early_role']not in g['roles']:f=r['mix_frame']
  assert C.sub(f,g['frame']);rf[role,k]=f
for role,ks in role_groups.items():ks.sort(key=lambda k:C.dimf[rf[role,k]])
m.agg=agg;m.role_groups=role_groups;m.target_group=owner;m.read_frames=rf;m.extra_byrole=byrole
rankselection=json.loads((P/'rank/selection.json').read_text());rankgroups=[];rankowner={}
for k,g in enumerate(rankselection['groups']):
 F=W.register(g['frame_basis']);dep={int(t):{int(p):c for p,c in cs.items()}for t,cs in g['dependent'].items()};assert not(set(dep)&{p for cs in dep.values()for p in cs})
 for t in g['targets']:assert t not in owner and t not in rankowner;rankowner[t]=k;assert all(W.module.dot(C.cov[t],b)==0 for b in C.B[F])
 for s in g['prefix_roles']:
  assert C.sub(W.gauge[s]['frame'],F)
  for t,cs in dep.items():assert m.adj[s].get(t,0)==sum(c*m.adj[s].get(p,0)for p,c in cs.items())
 rankgroups.append(dict(targets=g['targets'],dependent=dep,roles=set(g['prefix_roles']),frame=F))
assert len(rankgroups)==8 and len(rankowner)==64 and sum(len(g['dependent'])for g in rankgroups)==29
m.rankgroups=rankgroups;m.rankowner=rankowner
