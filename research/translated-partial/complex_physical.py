#!/usr/bin/env python3
"""Direct tensor-stage physical edge/path audit after complex auxiliary source shift.

Runs each actual local compiled schedule at its global tensor dimensions.
An all-to-all gate dependency envelope is conservative, including retained
control values. Data frontiers are maximized to account for every cross-stage
permutation. The shared auxiliary bank keeps its actual per-role frontier.
"""
from pathlib import Path
from collections import Counter
from fractions import Fraction as Q
from math import comb
import argparse,json,sys,hashlib
# Copyright 2026 Zhihao Chen (jacklightChen), Apache-2.0.
# Phase source-frame extension and complete physical audit. Source-frame
# freedom is inspired by eumemic's Claude-assisted PR #13; the retained
# producer is from PR #7 and whole-residual recursion is icekylinx's PR #10.
# Research assistance is recorded in the repository contribution notice.
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[1]
sys.path.insert(0,str(REPO/'scripts'))
from paired_complex import PairedComplex
from complex_circuit import compile_roles

def stage(c,code,j,source_shift,previous_data=None,shared_aux=None):
 h=c.h;v=len(c.triples);R=c.roles;aux=R+h+1;n=2*v+aux;m=h**3
 a=h**(j-1);offset=(a-1)*h
 assert (j==3)==(shared_aux is not None)
 # A source/sink bookkeeping dimension is allowed to be formal at the
 # reframed terminal. Every actual changed edge rank equals its difference.
 aux_start=(h if j==3 else offset if j==2 and source_shift else 0)
 frame=[a]*v+[a-1]*v+[aux_start]*aux
 paths=[[0]*n for _ in range(2)]
 desc=[0]*n
 if previous_data is not None:
  for p in range(2):
   paths[p][:v]=[previous_data['path_envelopes'][p][0]]*v
   paths[p][v:2*v]=[previous_data['path_envelopes'][p][1]]*v
  desc[:v]=[previous_data['decrease_envelopes'][0]]*v
  desc[v:2*v]=[previous_data['decrease_envelopes'][1]]*v
 if shared_aux is not None:
  for p in range(2):paths[p][2*v:]=shared_aux['paths'][p].copy()
  desc[2*v:]=shared_aux['decreases'].copy()
 hist=Counter();classes={};decrease_edges=[];edges=0
 index={T:i for i,T in enumerate(c.triples)}
 centers=list(range(2*v+R,n))
 dims={node:1 if c.kind[node]=='in' else c.cover(node).bit_count()
       if c.kind[node]=='d0' else c.support[node].bit_count() for node in c.active}
 def gate(wires,dim,name):
  nonlocal edges
  wires=set(wires)
  if not wires:return
  ranks=[abs(frame[w]-dim) for w in wires]
  losses=[max(0,frame[w]-dim) for w in wires]
  hist.update(ranks);classes.setdefault(name,Counter()).update(ranks)
  depth=[max(paths[p][w]+r**(p+1) for w,r in zip(wires,ranks)) for p in range(2)]
  decrease=max(desc[w]+r for w,r in zip(wires,losses))
  for w,r,loss in zip(wires,ranks,losses):
   if loss:decrease_edges.append((name,w,loss))
   frame[w]=dim;desc[w]=decrease
   for p in range(2):paths[p][w]=depth[p]
  edges+=len(wires)
 def label(mode,node=None):
  if mode=='low':return offset
  if mode=='high':return offset+h
  if mode=='line':return offset+1
  if mode=='perp':return offset+h-1
  if mode=='node':return offset+dims[node]
  if mode=='complement':return offset+h-dims[node]
  raise ValueError(mode)
 def mix(mode,inv=False):
  for node,ins,outs in reversed(code['gates']) if inv else code['gates']:
   gate([2*v+s for s in ins+outs],label(mode,node),'L_'+mode)
 def copy(bank,mode):
  for T,slot in code['sources'].items():gate([bank+index[T],2*v+slot],label(mode),'V_'+mode)
 def inject(bank,mode):
  groups=[[] for _ in range(v)]
  for i,slot in code['outputs'].items():groups[index[c.pieces[i][0]]].append(2*v+slot)
  for t,slots in enumerate(groups):gate([bank+t]+slots,label(mode),'J_'+mode)
 def central(bank,mode,name):gate(list(range(bank,bank+v))+centers,label(mode),name)
 if j!=2:
  mix('low');inject(v,'low');mix('low',True);central(v,'low','R_early')
  copy(0,'line');central(0,'high','G_middle');central(v,'low','R_return')
  mix('node');inject(v,'perp');mix('high',True);central(0,'high','G_cleanup');copy(0,'high')
 else:
  copy(v,'low');central(v,'low','G_early');mix('low');inject(0,'line')
  mix('complement',True);central(0,'high','R_middle');central(v,'low','G_return')
  copy(v,'perp');central(0,'high','R_cleanup');mix('high');inject(0,'high');mix('high',True)
 for t in range(v):gate([t],a*h,'data_X_frontier');gate([v+t],a*h-1,'data_Y_frontier')
 # Stage-one auxiliary end is the shared-bank frontier, not an external sink.
 aux_end=(h if j==1 else m+offset if j==2 and source_shift else m)
 for w in range(2*v,n):gate([w],aux_end,'aux_frontier_or_sink')
 expected='G_return' if j==2 else 'R_return'
 assert len(decrease_edges)==h+1
 assert all(name==expected and w in centers and loss==h for name,w,loss in decrease_edges)
 assert max(desc)<=j*h
 data=dict(path_envelopes=[[max(p[:v]),max(p[v:2*v])] for p in paths],
           decrease_envelopes=[max(desc[:v]),max(desc[v:2*v])])
 auxout=dict(paths=[p[2*v:] for p in paths],decreases=desc[2*v:])
 report=dict(stage=j,reverse=j==2,source_shift=source_shift,offset=offset,
  aux_start_dimension=aux_start,aux_final_dimension=aux_end,
  physical_edges=edges,histogram=dict(sorted(hist.items())),
  classes={k:dict(sorted(v.items())) for k,v in classes.items()},
  sum_edge_ranks=sum(r*c for r,c in hist.items()),
  maximum_rank_path_envelope=max(paths[0]),
  maximum_squared_rank_path_envelope=max(paths[1]),
  maximum_path_decrease=max(desc),data_frontier=data,
  decreasing_edges=len(decrease_edges),all_decreases_on_central_return=True)
 return report,data,auxout

def audit(shift):
 c=PairedComplex(28);code=compile_roles(c);h=c.h;m=h**3;v=len(c.triples)
 one,d1,a1=stage(c,code,1,shift)
 two,d2,_=stage(c,code,2,shift,d1)
 three,_,_=stage(c,code,3,shift,d2,a1)
 hist=Counter()
 for result in (one,two,three):
  for r,count in result['histogram'].items():hist[r]+=v*v*count
 hist.pop(0,None)
 W=2*v*v*(v+c.roles+h+1);L=3*v*v*h*(h+1);D=2*v**3-2*L;s=W*m-D
 assert sum(r*count for r,count in hist.items())==s
 # This second count uses only DAG degrees and label dimensions, not the
 # compiled physical gate schedule. It reproduces the retained local
 # histogram and appends each macro transition exactly once.
 local=Counter();degree=Counter()
 for node in sorted(c.active):
  for parent in c.args[node] or ():degree[parent]+=1
 for _,node,_ in c.pieces:degree[node]+=1
 ranks={node:1 if c.kind[node]=='in' else c.cover(node).bit_count()
        if c.kind[node]=='d0' else c.support[node].bit_count() for node in c.active}
 for node in sorted(c.active):
  r=ranks[node]
  if c.args[node]:
   local[r]+=degree[node]-1;local[h-r]+=1
   for parent in c.args[node]:
    assert r>=ranks[parent]
    local[r-ranks[parent]]+=1
  else:local[1]+=degree[node]
 for _,node,_ in c.pieces:
  r=ranks[node];assert r<h
  local[h-1-r]+=1;local[1]+=1
 local[h]+=3*(h+1)
 assert sum(r*n for r,n in local.items())==h*(c.roles+h+1)+2*h*(h+1)
 local[h-1]+=2*v  # Both physical data frontiers of one local invocation.
 expected=Counter({r:3*v*v*n for r,n in local.items()})
 B=v*v*(c.roles+h+1);N=v**3
 external=[(m-2*h,B),((h-1)**2,2*N),((h*h-1)*(h-1),2*N)]
 external+=([(m-h,B)] if shift else [(h*h-h,B),(m-h*h,B)])
 for r,n in external:expected[r]+=n
 expected.pop(0,None)
 assert hist==expected
 q=m+6*h+(h*h-h if shift else 0);M=max(hist)
 assert max(result['maximum_rank_path_envelope'] for result in (one,two,three))<=q
 squaremax=max(result['maximum_squared_rank_path_envelope'] for result in (one,two,three))
 convex=M*M+(q-M)**2
 assert squaremax<=convex
 assert squaremax<m*m
 return dict(source_shift=shift,stages=[one,two,three],
  global_histogram=dict(sorted(hist.items())),W=W,m=m,s=s,D=D,
  independent_histogram_matches=True,independent_histogram_method='DAG degrees and exact local label dimensions, with explicit macro classes',
  source_sha256={name:hashlib.sha256((REPO/'scripts'/name).read_bytes()).hexdigest() for name in ['paired_complex.py','complex_circuit.py']},
  global_maximum_rank_path_envelope=max(result['maximum_rank_path_envelope'] for result in (one,two,three)),
  global_maximum_squared_rank_path_envelope=squaremax,
  squared_path_moment=Q(squaremax,m*m),
  safe_rank_path_budget=q,safe_convex_squared_moment=Q(convex,m*m),
  data_frontier_maximization='At every stage boundary, use each bank maximum over all triples for every incoming data role. This bounds all actual coordinate permutations and may introduce unrealizable paths.',
  shared_bank_frontier='Stage3 retains the exact stage1 per-role auxiliary depth vector. All stage1 invocations have identical local programs and identical input depth zero; the bank permutation preserves local role indices.',
  unchanged_interfaces='Full coefficient maps, dirty scratch restoration, all local binary labels and role residuals were previously checked. New source/sink operators are checked in complex_controls.py.')

def js(x):
 if isinstance(x,Q):return str(x)
 if isinstance(x,dict):return {str(k):js(v) for k,v in x.items()}
 if isinstance(x,(tuple,list)):return [js(v) for v in x]
 return x
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--old-control',action='store_true');args=ap.parse_args()
 result=audit(not args.old_control)
 output=Path(__file__).with_name('complex-old-control.json' if args.old_control else 'complex-physical.json')
 output.write_text(json.dumps(js(result),indent=2)+'\n')
 print('PASS independent physical histogram and cross-stage path envelope')
 print('Source shift:',result['source_shift'],'Maximum rank path:',result['global_maximum_rank_path_envelope'])
 print('Squared path moment:',result['squared_path_moment'],float(result['squared_path_moment']))
