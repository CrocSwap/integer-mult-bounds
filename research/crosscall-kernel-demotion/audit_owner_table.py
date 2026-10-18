"""Independent bounded check of an owner-table replacement; no source-package execution.
Checks changed literal map using published, hash-pinned windows and phase axes.
Inherited windows/local semantics are explicit assumptions; this is not whole-proof verification.
"""
import argparse,json,gzip,hashlib,collections,copy,time
from pathlib import Path

def read(p):
 b=Path(p).read_bytes();return json.loads(gzip.decompress(b) if str(p).endswith('.gz') else b)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(x,msg):
 if not x:raise RuntimeError(msg)
def idle_basis(q):
 z=next(j for j in range(9) if not(q>>j)&1);u=q^(1<<z);order=list(range(9));order[0],order[z]=order[z],order[0]
 return [(1<<j)^(u if (u>>j)&1 else 0) for j in order]+[1<<j for j in range(9,73)]

def verify(rows,P,S,canon,ph,override=None,widths_by_call=None,profiles_by_call=None,parent=None):
 T=P["T"]; nc=9*T; live=896*T; deficit=320*T
 widths_by_call=widths_by_call or {}; profiles_by_call=profiles_by_call or {}
 order=[tuple(x) for x in P['order']];at={k:i for i,k in enumerate(order)};need(len(order)==nc and len(at)==nc,'call order');need(order==[tuple(x) for x in S['call_order']],'published order');widths=S['providers']['gauge44']['complete_contract']['widths'];need(len(widths)==480,'provider width count')
 need(len(rows)==nc*480,'role count');seen=set();families=collections.defaultdict(set);groups=collections.defaultdict(list);sigmas={};chart_cache={};chart_hashes={};stream=hashlib.sha256();cross=0
 if parent is not None:
  context=rebuild_windows(parent,order,T,ph);need(context['windows']==P['windows'],'actual source-event windows');need(context['pairs']==P['pairs'] and context['sides']==P['sides'],'actual child family identity')
  for z in rows:
   need(z['owner_replica']!=z['replica'] or int(P['pairs'][str(z['child'])])!=context['stage_pair'][z['stage']],'caller active family collision')
 bases=[idle_basis(q) for q in canon['ports']];need(len(bases)==112 and ph['ports']==112 and [r['q'] for r in ph['recipes']]==canon['ports'],'phase port geometry')
 for B in bases:
  need(len(set(B))==73 and all(((x&y).bit_count()%2)==int(i==j) for i,x in enumerate(B) for j,y in enumerate(B)),'orthogonal basis')
 for p,B in enumerate(bases):
  reserved=collections.defaultdict(set)
  for child,recipe in enumerate(ph['recipes'][p]['idle_children']):
   axes=set(recipe['orthogonal_axes']);need(len(axes)==recipe['rank'] and axes<=set(B),'complete pending physical basis')
   if not recipe['rank']:continue
   need(str(child) in P['pairs'] and P['windows'][f'0,{child}'][0]==recipe['rank'],'complete pending cap')
   key=(P['pairs'][str(child)],P['sides'][str(child)])
   need(not(reserved[key]&axes),'distinct-child pending axes overlap');reserved[key].update(axes)
 for idx,z in enumerate(rows):
  need(all(type(z.get(k)) is int for k in ('stage','replica','helper','time','owner_replica','child','port','copy','family','offset','width')),'integer role schema')
  st,r,h=z['stage'],z['replica'],z['helper'];time_=z['time'];o,c,p=z['owner_replica'],z['child'],z['port'];w,off=z['width'],z['offset'];role=(st,r,h)
  need((st,r) in at and time_==at[st,r],'call time');need(0<=h<480 and w==widths_by_call.get((st,r),widths)[h],'helper width');need(role not in seen,'duplicate role');seen.add(role)
  need(0<=o<T and 0<=p<112,'owner port');key=f'{o},{c}';need(key in P['windows'],'pending child');cap,allowed=P['windows'][key];need(time_ in allowed,'out of window');need(0<=off and off+w<=cap,'coordinate bound');need(z['copy']==112*o+p,'copy identity');need(z['family']==896*o+(2*P['pairs'][str(c)]+P['sides'][str(c)])*112+p,'family identity');need(z['family'] not in families[time_],'per-call family alias');families[time_].add(z['family']);groups[o,c,p].append(z);cross+=o!=r
  ck=(p,c,off,w)
  if ck not in chart_cache:
   B=bases[p];pending=list(map(int,ph['recipes'][p]['idle_children'][c]['orthogonal_axes']));need(len(pending)==cap and len(set(pending))==cap,'pending axis rank');need(all(x in B for x in pending),'pending basis containment');occ=[B.index(x) for x in pending[off:off+w]];sp=[j for j in range(73) if j not in occ][:9-w];perm=occ+sp+[j for j in range(73) if j not in occ+sp];need(sorted(perm)==list(range(73)),'full chart permutation');sigma=[B[j] for j in perm];need(sigma[:w]==pending[off:off+w] and len(set(occ+sp))==9,'actual residual chart');chart_cache[ck]=sigma
  sigma=chart_cache[ck]
  if override and idx in override:need(override[idx]==sigma,'wrong chart')
  if ck not in chart_hashes:chart_hashes[ck]=hashlib.sha256(json.dumps(sigma,separators=(',',':')).encode()).hexdigest()
  sh=chart_hashes[ck];sigmas[sh]=sigma;stream.update(json.dumps([st,r,h,z['family'],sh],separators=(',',':')).encode()+b'\n')
 need(seen=={(s,r,h) for s in range(9) for r in range(T) for h in range(480)},'complete roles')
 used={}
 for k,zs in groups.items():
  pointer=0
  for z in sorted(zs,key=lambda z:(z['time'],z['helper'])):
   need(z['offset']==pointer,'overlapping or non-chronological axes');pointer+=z['width']
  used[k]=pointer
 idle=collections.Counter();remainders=[]
 for key,(cap,allowed) in P['windows'].items():
  o,c=map(int,key.split(','))
  for p in range(112):
   used_=used.get((o,c,p),0);rem=cap-used_;need(rem>=0,'negative remainder')
   if rem:
    idle[rem]+=1;remainders.append({'owner_replica':o,'child':c,'port':p,'family':896*o+(2*P['pairs'][str(c)]+P['sides'][str(c)])*112+p,'pending_offset':used_,'rank':rem})
 paid=collections.Counter()
 for call in order:
  paid.update({int(k):v for k,v in profiles_by_call.get(call,S['providers']['gauge44']['expected_profile']).items()})
 paid.update(idle);mass=sum(k*v for k,v in paid.items());need(mass==S['expected']['rank_mass']==73*live-deficit,'rank mass');need(73*live-mass==deficit,'rank deficit')
 return {'roles':len(rows),'calls':nc,'helper_per_call':480,'profile':dict(sorted(paid.items())),'idle_profile':dict(sorted(idle.items())),'idle_remainders':sum(idle.values()),'rank_mass':mass,'deficit':deficit,'cross_replica':cross,'actual_73column_sigmas':len(sigmas),'sigma_stream_sha256':stream.hexdigest(),'sigmas':sigmas,'remainders':remainders}


def rebuild_windows(parent,order,T,ph=None):
 """Reconstruct last-touch to idle boundaries from literal original32-event source."""
 need(len(parent['calls'])==72,'original source call count')
 source=parent.get('async_schedule',{}).get('source_schedule',parent['execution_schedule']);need(len(source)==32,'source event count')
 blocks={};global_events=[];stage=None
 for index,event in enumerate(source):
  kind=event['kind']
  if kind in ('bank_padding_cover_sweep','translate_every_live_family'):
   global_events.append(index);continue
  if kind=='local_cover_sweep':stage=event['stage'];blocks[stage]=[]
  need(stage is not None,'event before invocation');blocks[stage].append((index,event))
 need(global_events==[30,31],'source global tail')
 events=[(idx,event,r,t) for t,(s,r) in enumerate(order) for idx,event in blocks[s]]
 projections=collections.defaultdict(list)
 for idx,event,r,t in events:projections[r].append(idx)
 need(set(projections)==set(range(T)) and all(z==list(range(30)) for z in projections.values()),'per-replica event order')
 ranks={c['child']:c['rank'] for c in parent['idle_children']}
 if ph is not None:
  ranks={j:z['rank'] for j,z in enumerate(ph['recipes'][0]['idle_children']) if z['rank']>0}
  for recipe in ph['recipes']:
   need({j:z['rank'] for j,z in enumerate(recipe['idle_children']) if z['rank']>0}==ranks,'phase rank geometry')
   need(all(len(z['orthogonal_axes'])==z['rank'] for z in recipe['idle_children']),'actual phase axis rank')
 stage_pair={x['stage']:x['pair'] for x in parent['recipe'] if x['kind']=='local'}
 last={};bounds={};callpos={};pairs={};sides={}
 for pos,(idx,event,r,t) in enumerate(events):
  kind=event['kind']
  if kind=='local_cover_sweep':last[r,stage_pair[event['stage']]]=pos;callpos[t]=pos
  elif kind=='bridge':last[r,event['src']]=last[r,event['dst']]=pos
  elif kind=='idle_cover_sweep':
   for side,child in enumerate(event['child_indices']):
    if child in ranks:
     bounds[r,child]=(last.get((r,event['pair']),-1),pos);pairs[str(child)]=event['pair'];sides[str(child)]=side
 need(set(callpos)==set(range(9*T)),'complete source invocation positions')
 windows={f'{r},{c}':[ranks[c],[t for t,p in sorted(callpos.items()) if lo<p<hi]] for (r,c),(lo,hi) in bounds.items()}
 return dict(windows=windows,pairs=pairs,sides=sides,stage_pair=stage_pair,events=len(events))
