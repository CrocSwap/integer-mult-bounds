import argparse,collections,json,copy
from pathlib import Path
import independent_core as A
ap=argparse.ArgumentParser();ap.add_argument('--parent',type=Path,required=True);ap.add_argument('--data',type=Path,required=True);ap.add_argument('--provider',action='append',required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();dirs={p:Path(d) for p,d in (x.split('=',1) for x in a.provider)};plan=A.read(a.data/'PLAN.json');dispatch={(s,r):p for s,r,p in A.read(a.data/'DISPATCH.json')};roles=A.read(a.data/'OWNERS.json.gz');parent=A.read(a.parent);phases=A.read(a.parent.parent.parent/'work/complex-nine-native/DATA-PHASES.json');canonical=A.read(a.parent.parent/'CANONICAL-WORD.json.gz');inventories={};words={};replays={};profiles={};prefix=[]
A.R=len(next(iter(plan['provider_registry'].values()))['widths']);A.require(all(len(d_['widths'])==A.R for d_ in plan['provider_registry'].values()),'common helper count R');A.require(len(dispatch)==len(plan['order']) and set(dispatch.values())==set(dirs),'complete provider dispatch')
A.require({(c['stage'],c['replica']):c['provider'] for c in plan['provider_calls']}==dispatch,'plan dispatch binding')
for pid,d in dirs.items():
 w,r=A.read(d/'CANONICAL-WORD.json.gz'),A.read(d/'INDEPENDENT-LOCAL-REPLAY.json');A.require(r['status']=='PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY','native status');A.require(r['canonical_word_sha256']==A.filehash(d/'CANONICAL-WORD.json.gz'),'word binding');A.require(set(r['local'])=={'forward','backward'},'both orientations');A.require(w['ports']==canonical['ports'],'common ports');A.require([A.basis(w['frames'][f]) for f in w['center_frames']]==[A.basis(canonical['frames'][f]) for f in canonical['center_frames']],'common ordered center frames');A.EXPECTED_WIDTHS=collections.Counter(plan['provider_registry'][pid]['widths']);ws,paid=A.local_inventory(w,r,A.read(d/'LOCAL-PROGRAMS.json.gz'));A.require(ws==plan['provider_registry'][pid]['widths'],'ordered provider widths');inventories[pid]=ws;profiles[pid]=paid;words[pid]=w;replays[pid]=r;prefix.extend(x['prefix_bits_upper'] for x in r['local'].values())
 for _nm,_mut in (('changed lifted target frame',lambda b_:b_['target_levels'].__setitem__('23',0)),):
  _bad=copy.deepcopy(w);_mut(_bad)
  try:A.local_inventory(_bad,r,None)
  except ValueError as _e:A.require(str(_e)=='target line30','target mutation rejection')
  else:raise ValueError('accepted changed lifted target')
 _pg=A.read(d/'LOCAL-PROGRAMS.json.gz');_bp=copy.deepcopy(_pg);_bp['forward'].remove(next(e for e in _bp['forward'] if e[0]=='center'))
 try:A.local_inventory(w,r,_bp)
 except ValueError as _e:A.require(str(_e)=='literal centre COPY segments','COPY mutation rejection')
 else:raise ValueError('accepted missing split COPY child')
pid=next(iter(dirs));A.EXPECTED_WIDTHS=collections.Counter(inventories[pid]);A.T=plan['T'];A.EXPECTED_IDLE={int(k):v for k,v in A.read(a.data/'CONSTRUCTION.json')['idle'].items()};ctx=A.make_context(parent,phases,canonical['ports'],words[pid],replays[pid],roles);A.require(set(ctx['order'])==set(dispatch),'complete dispatch calls');ctx['call_widths']={c:inventories[p] for c,p in dispatch.items()};ctx['aggregate_paid']=collections.Counter()
A.require(A.ZERO_BUFFERS==max(len(w.get('zero_buffers',[]))for w in words.values()),'shared private buffer bank')
for p in dispatch.values():ctx['aggregate_paid'].update(profiles[p])
ctx.update(max_local_prefix=max(prefix),local_profiles=profiles,width_inventories={p:dict(collections.Counter(ws)) for p,ws in inventories.items()});pending=A.check_pending_axes(ctx);receipt=A.check_roles(ctx,roles);A.require(receipt['profile']=={int(k):v for k,v in plan['profile'].items()},'aggregate profile binding');receipt['controls_rejected']=A.controls(ctx,roles)
# A wrong provider at one changed call must fail the literal width predicate.
call=next(c for c,p in dispatch.items() if p=='extra');bad=dict(ctx,call_widths=dict(ctx['call_widths']));bad['call_widths'][call]=inventories['gauge44'] if inventories['gauge44']!=inventories['extra'] else (lambda w:(lambda i,j:w[:i]+[w[j]]+w[i+1:j]+[w[i]]+w[j+1:])(0,next(k for k in range(len(w)) if w[k]!=w[0])))(list(inventories['extra']))   # borrowed words have identical width lists: control = swapped widths of two helpers at that call
try:A.check_roles(bad,roles)
except ValueError as e:A.require(str(e)=='whole-helper residual width','wrong provider control predicate');receipt['controls_rejected'].append(dict(name='wrong_provider_at_changed_call',reason=str(e)))
else:raise ValueError('accepted incorrect provider')
receipt.update(disjoint_pending_child_axis_checks=pending,provider_counts=dict(collections.Counter(dispatch.values())),input_sha256={str(p):A.filehash(p) for p in [a.data/'PLAN.json',a.data/'DISPATCH.json',a.data/'OWNERS.json.gz',a.parent]+[d/'CANONICAL-WORD.json.gz' for d in dirs.values()]});a.out.write_text(json.dumps(receipt,indent=2)+'\n');print('PASS_INDEPENDENT_MIXED_OWNER',len(receipt['controls_rejected']),flush=True)
