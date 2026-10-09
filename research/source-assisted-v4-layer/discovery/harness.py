#!/usr/bin/env python3
"""General v4 harness: modules/local/f8 -> graph -> our carrier matching + PR162 extension -> closure -> gauges -> descent -> numeric screen.
Numerical screen only; candidates need the independent exact audits before admission."""
from pathlib import Path
import sys,json,gzip,math,time,hashlib,argparse
H=Path(__file__).resolve().parent;TOP=H.parent;SRC=TOP/'source';sys.path.insert(0,str(SRC/'scripts'));sys.path.insert(0,str(H))
from paired_cube.graph import Graph
from paired_cube.modules import triple_module_from,pair_module_from,all_but_one_from,merge_outputs
from paired_cube.closure import compile_closure
from paired_cube.gauges import select
from paired_cube_physical import physical
from physical_opt import Physical
from matching import carrier_matching
from extend import extended_arcs
import joint,bundles,deep
from pairs_mw import pairs_maxweight
def root(prof):
 hist={int(r):c for r,c in prof['child_histogram'].items()};m=prof['m'];W=prof['W_per_vertex'];lo=0.;hi=.01
 for _ in range(70):
  a=(lo+hi)/2
  if math.fsum(c*r*math.exp(a*math.log(m/r)) for r,c in hist.items())<m*W:lo=a
  else:hi=a
 return lo
def save(out,name,data):
 with gzip.GzipFile(filename='',fileobj=(out/(name+'.json.gz')).open('wb'),mode='wb',mtime=0) as f:f.write((json.dumps(data,separators=(',',':'))+'\n').encode())
def build(f8='f8:00111100',local=None,tmod=None,pmod=None,qmod=None,ordering='reverse',frozen_arcs=False):
 src=SRC/'references/paired-cube/sources'
 local=json.loads(Path(local).read_text()) if local else json.loads((src/'local_L1.json').read_text())
 b=Graph(11,local=local)
 import os
 g=b.finish(triple_module_from(tmod or src/'tmod_TE_TD_TB3_1_1_4_full_6.0617964e-4.json',11),pair_module_from(pmod or src/'pmod_J0_full_6.0666810e-4.json',10),all_but_one_from(qmod or src/'qmod_climb3u_best.json',9),center_kind=os.environ.get('CENTER_KIND','star'))
 g=merge_outputs(g,b,f8);g['matching_frames']='coordinate'
 if frozen_arcs:
  arcs=json.loads((SRC/'references/paired-cube/selected-module/matching-arcs.json').read_text());match=dict(frozen=len(arcs))
 else:
  arcs,match=carrier_matching(g,ordering);arcs=extended_arcs(g,arcs)
 base,w=compile_closure(g,arcs);row,word=select(g,base,w)
 return g,base,w,row,word,arcs,match
def descend(g,w,row,word,light=False,deep_depth=0,frames=None,mw=0,pair_first=False):
 o=Physical(g,w,word,row)
 if frames:
  for i,F in frames:o.frames[i]=tuple(F)
 def cycle(seed):
  if light:o.descend(6);return
  for k in range(3):
   a=o.descend(6);b=bundles.descend(o,3);c=joint.descend(o,3,'forward',seed+k)
   d=deep.descend(o,deep_depth,2,seed+k) if deep_depth else []
   if not any(x['changed'] for x in a) and not any(x['moved_components'] for x in b) and not any(x['moved'] for x in c) and not any(x['moved'] for x in d):break
 if pair_first:
  pairs,stats=pairs_maxweight(o)
  for d,b,_ in pairs:o.end[d]=o.gauge[b]
 cycle(0)
 if not pair_first:pairs,stats=(pairs_maxweight(o) if mw else o.pairs())
 for d,b,_ in pairs:o.end[d]=o.gauge[b]
 cycle(10)
 for it in range(mw-1 if mw else 0):
  # re-pair on the descended frames (donor end frames may now allow better donors), then descend again
  for d,b,_ in pairs:o.end[d]=o.full
  newpairs,newstats=pairs_maxweight(o)
  if newstats['total_weight']<=stats['total_weight']+1e-9:
   for d,b,_ in pairs:o.end[d]=o.gauge[b]
   break
  pairs,stats=newpairs,newstats
  for d,b,_ in pairs:o.end[d]=o.gauge[b]
  cycle(20+it)
 def written_in_rest(d):return any(i not in o.phase and o.ops[i][0]==d for i in o.role_ops[d])
 good=[k for k,(d,b,t) in enumerate(pairs) if t is not None and written_in_rest(d)]
 if good:pairs.append(pairs.pop(good[-1]))
 frames=o.changed();prof=physical(g,w,word,row,frames,pairs)
 return prof,frames,pairs,stats
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--f8',default='f8:00111100');ap.add_argument('--local');ap.add_argument('--tmod');ap.add_argument('--pmod');ap.add_argument('--qmod');ap.add_argument('--ordering',default='reverse');ap.add_argument('--frozen-arcs',action='store_true');ap.add_argument('--light',action='store_true');ap.add_argument('--deep',type=int,default=0);ap.add_argument('--mw',type=int,default=0);ap.add_argument('--pair-first',action='store_true');ap.add_argument('--seed-frames');ap.add_argument('--tag',required=True);a=ap.parse_args()
 t=time.monotonic();g,base,w,row,word,arcs,match=build(a.f8,a.local,a.tmod,a.pmod,a.qmod,a.ordering,a.frozen_arcs)
 print(json.dumps(dict(tag=a.tag,stage='compiled',c=row['c'],q=row['q'],R=row['R'],matched=row['matched'],arcs=len(arcs),selected=row['selected_roles'],numeric_before=row['numerical_complex_root'],seconds=time.monotonic()-t)),flush=True)
 seed=json.loads(gzip.decompress(Path(a.seed_frames).read_bytes())) if a.seed_frames else None
 prof,frames,pairs,stats=descend(g,w,row,word,a.light,a.deep,seed,a.mw,a.pair_first)
 r=root(prof);out=H/('h-'+a.tag);out.mkdir(exist_ok=True)
 for name,data in [('graph',g),('baseline',base),('frames',w),('word',word),('profile-before',row),('physical-frames',frames),('physical-pairs',pairs),('profile',prof)]:save(out,name,data)
 res=dict(tag=a.tag,deep=a.deep,mw=a.mw,pair_stats=stats,f8=a.f8,local=a.local,tmod=a.tmod,pmod=a.pmod,qmod=a.qmod,ordering=a.ordering,frozen_arcs=a.frozen_arcs,light=a.light,root=r,W=prof['W_per_vertex'],physical_R=prof['physical_R'],pairs=prof['pairs'],changed=len(frames),seconds=time.monotonic()-t,pins={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.glob('*.json.gz')})
 (out/'result.json').write_text(json.dumps(res,sort_keys=True,indent=2)+'\n');print(json.dumps({k:res[k] for k in ('tag','root','W','physical_R','pairs','changed','seconds')}),flush=True)
