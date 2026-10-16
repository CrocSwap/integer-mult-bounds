#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Restore retired source pairs before handoff; generate twelve joint aliases.

Derived from PR2462 (Jeremy Kothe), PR2436 lifted-target work (Tekalign),
and PR2322 generator utilities (Vlado Vojdanovski), all with AI assistance.
This derivative: OpenAI Codex at the user's direction. See README for scope.
"""
import sys,json,gzip,copy,importlib.util
from pathlib import Path
from fractions import Fraction as Q
from collections import defaultdict,Counter
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'vendor'))
import generate_words as G
import gf_chart as C
from target_transport import step

def mod(name,path):
 spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def paid_lifted(w):
 src=Path(G.__file__).read_text();src=src[src.index('def paid_profile('):src.index('\ndef build(')]
 src=src.replace("for event in word['A']:\n        gate(event)","""for event in word['A']:
        if event[0]=='warp':
            _,r,op,U,V=event
            cols=word['warps'][abs(op)-1][2]
            if op<0:
                back={mapped(cols,x):x for x in range(512)};cols=[back[1<<i] for i in range(9)]
            require(cur[r]==basis(U),'prelude source frame')
            require(basis(mapped(cols,x) for x in U)==basis(V),'prelude transport')
            cur[r]=basis(V)
        else:gate(event)""")
 ns=dict(G.__dict__);exec(src,ns);return ns['paid_profile'](w)

def make(source, output, tag='base', *, seed, assignments):
 S2=Path(source);BASE=Path(output);BASE.mkdir(parents=True,exist_ok=True)
 AU2=mod('audit_local',S2/'new/borrow/audit_local.py');WP=mod('word_patch',S2/'new/borrow/word_patch.py')
 w=copy.deepcopy(seed);nw=copy.deepcopy(w)
 assignments=list(assignments)
 # Pair partners can be restored immediately after the existing first-axis restorations.
 before=defaultdict(list);deletes=set();replace={};newrecords=[]
 cur={r:([w['ports'][r]] if r<112 else w['start_extra'].get(str(r),[])) for r in range(704)}
 for g in w['A']:
  if g[0]=='warp':cur[g[1]]=g[-1]
  else:
   for r in G.incident(g):cur[r]=g[-1]
 wp=defaultdict(list)
 for op,x in enumerate(w['warps'],1):wp[x[0]].append((op,x))
 snapshots={}
 for i,g in enumerate(w['B']):
  for op,x in wp[i]:cur[x[1]]=x[4]
  snapshots[i]=copy.deepcopy(cur)
  for r in G.incident(g):cur[r]=g[-1]
 for h,r,partner in assignments:
  assert not any(h in G.incident(g) for g in w['A'] if g[0]!='warp')
  first=next(i for i,g in enumerate(w['B']) if g[1]==h)
  olduses=[i for i,g in enumerate(w['B']) if r in G.incident(g)]
  if r in [33,55,74,85]:
   at=1+max(i for i,g in enumerate(w['B']) if set(G.incident(g))&{r,partner})
   U=G.basis(snapshots[at][r]);assert U==G.basis(snapshots[at][partner])
   before[at].append(['add',r,partner,1,2,list(U)])
  elif r in [49,101,83,98]:
   at=1+max(i for i,g in enumerate(w['B']) if set(G.incident(g))&{r,partner})
   U=G.basis(snapshots[at][r]);assert U==G.basis(snapshots[at][partner])
   before[at].append(['add',r,partner,-1,1,list(U)])
  elif r in [80,88]:
   restoration=max(i for i,g in enumerate(w['B']) if set(G.incident(g))&{80,88})
   U=G.basis(snapshots[restoration+1][r])
   if r==80:before[restoration+1]+=[['add',88,80,1,2,list(U)],['add',80,88,-1,1,list(U)]]
  elif r==31:
   at=next(x[0] for x in w['warps'] if x[1]==12);U=G.basis(snapshots[at][r]);before[at].append(['add',31,12,1,2,list(U)]);assert max(olduses)<at
  elif r==68:
   at=next(x[0] for x in w['warps'] if x[1]==4);U=G.basis(snapshots[at][r]);before[at]+=[['scale',68,1,2,list(U)],['add',68,4,-1,1,list(U)]]
   assert max(olduses)<at
  else:
   restoration=next(i for i,g in enumerate(w['B']) if g[:3]==['add',partner,r] and Q(g[3],g[4])==Q(1,2))
   assert max(olduses)==restoration,(r,olduses[-8:],restoration)
   U=G.basis(w['B'][restoration][-1]);before[restoration+1].append(['add',r,partner,-1,1,list(U)])
  echo=[i for i,g in enumerate(w['B'][:first]) if h in G.incident(g)]
  assert all(w['B'][i][0]=='add' and w['B'][i][2]==h and 112<=w['B'][i][1]<224 for i in echo)
  deletes.update(echo)
  F=G.basis(w['B'][first][-1]);line=w['start_extra'][str(h)];a=[w['ports'][r]];b=list(line)
  for x in U:
   if len(G.basis(a+[x]))>len(a):a.append(x)
  for x in F:
   if len(b)<len(a) and len(G.basis(b+[x]))>len(b):b.append(x)
  assert len(a)==len(b)==4
  cols=C.gf_change(a,b,9);E=[C.gf_linear(cols,x) for x in U] if hasattr(C,'gf_linear') else [G.mapped(cols,x) for x in U]
  op=len(w['warps'])+len(newrecords)+1;newrecords.append([first,r,cols,list(U),E]);replace[h]=r
  nw['removed'].append(h);del nw['start_extra'][str(h)];nw['helper_final'].pop(str(h),None)
 # Keep preexisting operator IDs stable; extra warps are appended to the table.
 newB=[];position={}
 for i in range(len(w['B'])+1):
  newB.extend(before[i]);position[i]=len(newB)
  if i<len(w['B']) and i not in deletes:
   g=copy.deepcopy(w['B'][i])
   for k in range(1,3 if g[0]=='add' else 2):g[k]=replace.get(g[k],g[k])
   newB.append(g)
 nw['B']=newB
 for x in nw['warps']:x[0]=position[x[0]]
 for x in newrecords:x[0]=position[x[0]]
 nw['warps']+=newrecords;nw['removed']=sorted(nw['removed'])
 # Exact residual nomination before cleanup.
 live=sorted(set(range(704))-set(nw['removed']));rows={r:{(r,()):Q(1)} for r in live}
 def apply(g):AU2.walg_apply(g[:3] if g[0]=='warp' else g,rows,False,10**6)
 for t in nw['initial_corrections']:apply(['corr',t['target'],t['source'],tuple(t['operator_word']),Q(t['coefficient'])])
 for sec in ['precondition','compensation','A','cut']:
  for g in nw[sec]:apply(g)
 by=defaultdict(list)
 for op,x in enumerate(nw['warps'],1):by[x[0]].append((op,x))
 for i in range(len(nw['B'])+1):
  for op,x in by[i]:apply(['warp',x[1],op])
  if i<len(nw['B']):apply(nw['B'][i])
 for g in nw['restore']:apply(g)
 groups=defaultdict(dict)
 for t in range(112,224):
  residual=dict(rows[t]);AU2.walg_add(residual,{(t,()):Q(1),(t-112,()):Q(1)},-1)
  for (r,op),q in residual.items():
   assert len(op)==1 and op[0]>len(w['warps']),(t,r,op,q)
   groups[r,op[0]][t]=-q
 prelude=[];targetlines={}
 for (r,op),coeff in groups.items():
  for g in nw['precondition']+nw['compensation']:coeff=step(coeff,g,set(range(112,224)))
  record=nw['warps'][op-1];line=[G.mapped(record[2],w['ports'][r])]
  for t in coeff:
   assert t not in targetlines or targetlines[t]==line,(t,r,op,line,targetlines.get(t),dict(groups))
   targetlines[t]=line
  prelude.append(['warp',r,op,[w['ports'][r]],line])
  for t,q in sorted(coeff.items()):prelude.append(['add',t,r,q.numerator,q.denominator,line])
  prelude.append(['warp',r,-op,line,[w['ports'][r]]])
 lifts=[]
 for t,line in sorted(targetlines.items()):
  key=str(t-112);old=nw['target_levels'].get(key,[]);assert not old or G.basis(old)==G.basis(line)
  if not old:lifts.append(['scale',t,1,1,line]);nw['target_levels'][key]=line
 nw['A']=lifts+prelude+nw['A'];nw['prelude_events']+=len(lifts)+len(prelude)
 tmp=copy.deepcopy(nw);tmp['A']=tmp['A'][nw['prelude_events']:];nw['cleanup']=WP.derive_cleanup(tmp,WP.restored_of(w))
 pp,iv=paid_lifted(nw);nw['report']['local_profile']=pp;nw['report']['width_inventory']=iv
 out=BASE/f'eight-alias-{tag}.json.gz';out.write_bytes(gzip.compress(json.dumps(nw,separators=(',',':')).encode()))
 print('BUILT',tag,'newops',len(newrecords),'targets',targetlines,'file',out,flush=True)
 AU2.run(out,BASE/f'eight-alias-{tag}-audit.json')
 return nw
