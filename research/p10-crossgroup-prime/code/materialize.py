#!/usr/bin/env python3
"""Deterministically reconstruct frozen cross-group selections and actual words.
Prepared with substantial OpenAI Codex assistance; Apache-2.0.
"""
import sys,json,importlib.util,hashlib,collections,pathlib,shutil
if not __debug__:raise SystemExit('Assertions required')
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[1]
PKG=ROOT/'vendor/predecessor';OUT=pathlib.Path(sys.argv[1])/'materialized';OUT.mkdir();sys.path.insert(0,str(PKG))
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
mods={}
def mod(st):
 if st not in mods:mods[st]=load('portable527_cross_'+st,PKG/(st+'_transform.py'))
 return mods[st]
def hist(out):
 H=collections.Counter()
 for k in range(0,len(out),6):
  if out[k]==0 and out[k+4]:H[out[k+4]]+=1
  elif out[k]==2:H[out[k+5]]+=1
 return H
def delta(out,run):
 D=hist(out);D.subtract({int(r):c for r,c in run['physical']['paid_histogram'].items()});return {str(r):c for r,c in sorted(D.items())if c}
def bind(sel,run):
 sel.update(n=2*run['W'].v+len(run['context']['regs']),v=run['W'].v,input_raw_sha256=hashlib.sha256(run['records'].tobytes()).hexdigest(),input_scalar_sha256=run['physical']['scalar_projection_sha256']);return sel
def save(st,sel):
 assert sel==json.loads((ROOT/'stages'/(st+'-selection.json')).read_text()), 'Regenerated selection differs: '+st
 path=OUT/(st+'-selection.json');path.write_text(json.dumps(sel,indent=2)+'\n');return path
def emit(st,run,sel,tag=None):
 path=save(st,sel);return mod('kernel'if st=='kernel2'else st).run(run,output_dir=OUT/st,selection_path=path,**({'tag':tag}if tag else{}))
def finalstate(run):
 final=dict(run['initial_state']);old=run['records']
 for k in range(0,len(old),6):
  if old[k]==0:final[old[k+1]]=old[k+3]
 return final
def export(st,run):
 dest=OUT/st;dest.mkdir(exist_ok=True);W,C=run['W'],run['C'];rec=run['records'];n=2*W.v+len(run['context']['regs'])
 (dest/'regs.json').write_text(json.dumps(run['context']['regs']));(dest/'records.bin').write_bytes(rec.tobytes());(dest/'initial.json').write_text(json.dumps(run['initial_state']));(dest/'final.json').write_text(json.dumps(finalstate(run)));(dest/'frames.json').write_text(json.dumps({str(f):dict(A=C.A[f],B=C.B[f],dim=C.dimf[f])for f in C.A}));(dest/'physical.json').write_text(json.dumps(run['physical'],indent=2));(dest/'meta.json').write_text(json.dumps(dict(n=n,v=W.v,ZERO=run['ZERO'],FULL=run['FULL'],category_names=run['physical']['category_names'],source_head='PR320 1b37957 + cross-entrance exchanges + presink4 + late rank6',word_sha=hashlib.sha256(rec.tobytes()).hexdigest()),indent=2));print('EXPORT',st,hashlib.sha256(rec.tobytes()).hexdigest(),run['physical']['weighted_scalar_events'],flush=True)
ctx=load('portable527_prepare',PKG/'prepare.py').prepare();run=load('portable527_physical',PKG/'code/physical527.py').run(dict(ctx),ctx['SOURCE_TEXT']);run=mod('parity').run(run)
for st in ('descent','target'):run=mod(st).run(run)
export('target-baseline',run)
base_initial=dict(run['initial_state']);base_final=dict(finalstate(run));base_regs=list(run['context']['regs'])
# New globally coherent selection. Existing late rank2 entries stay in the late stage.
x=json.loads((ROOT/'discovery/COMBINED.json').read_text());sel=json.load(open(PKG/'kernel-selection.json'));old=run['records'];readcat=run['physical']['category_names'].index('dirty_read');lr={}
for k in range(0,len(old),6):
 if old[k]==1 and old[k+4]==run['ZERO'] and old[k+5]==readcat:lr[old[k+2]]=k//6
families=[f for i,f in enumerate(sel['families'])if i not in x['removed_indices']]
for f in x['new_families']:
 r={k:v for k,v in f.items()if k!='cut'};cut=max(lr[s]for s in[r['pivot']]+r['donors']);r['cut_read']=[old[6*cut+j]for j in(1,2,3)];r['kind']='cross-entrance-shared-donor-rank'+str(r['rank']);families.append(r)
sel.update(families=families,selected_families=len(families),status='P10_CROSS_ENTRANCE_EXCHANGE_KERNEL',provenance=sel['provenance']+'; cross-entrance exchanges discovered with OpenAI Codex assistance, recomputed globally and admitted on actual scalar word')
bind(sel,run);out,init,fin,entries,execution,cats,proof,n,v=mod('kernel').transform(run,sel,'kernel');sel.update(expected_local_delta=delta(out,run),entrance_rank_histogram=proof['entrance_rank_histogram'],total_entrance_rank=proof['total_entrance_rank'],donor_sharing_histogram=proof['donor_sharing_histogram']);run=emit('kernel',run,sel);export('kernel',run)
# Restore screen rederived on the changed word.
rt=mod('restore');W,C=run['W'],run['C'];old=run['records'];n=2*W.v+len(run['context']['regs']);initial=dict(run['initial_state']);cats=list(run['physical']['category_names']);cut,rows,state=rt.screen(old,initial,n,W.v,C,W,cats,run['ZERO'],run['FULL']);entries=[]
for a,b,i,c,fa,fb in rows:
 E=W.register([list(x)for x in C.B[fa]]+[list(x)for x in C.B[fb]])
 if C.dimf[E]==W.h or not C.nondeg(E):continue
 entries.append(dict(helper=a,donor=b,coefficient=c,incidence=[old[6*i+j]for j in(1,2,3)],rank=C.dimf[E],basis=[list(x)for x in C.B[E]],dims=[C.dimf[initial[a]],C.dimf[fa],C.dimf[fb],C.dimf[E]]))
sel=bind(dict(status='GEN5_EARLY_RESTORATION_PR280_SCREEN',cut=cut,selected=len(entries),entries=entries,expected_local_delta={}),run);out,*_=rt.transform(run,sel);sel['expected_local_delta']=delta(out,run);run=emit('restore',run,sel);print('RESTORE',len(entries),sel['expected_local_delta'],flush=True)
# Rebind four inherited constructed-frame retimings by exact scalar content and basis.
ps=mod('presink');sel=json.load(open(PKG/'presink-selection.json'));old=run['records'];C=run['C']
for r in sel['entries']:
 hits=[k//6 for k in range(0,len(old),6)if old[k]==1 and[old[k+j]for j in(1,2,3,5)]==r['scalar']and C.dimf[old[k+4]]==r['old_dimension']and ps.sha_basis(C.B[old[k+4]])==r['old_basis_sha256']];assert len(hits)==1,(r['scalar'],hits);r['record']=hits[0]
bind(sel,run);sel['source_record_count']=len(old)//6;out,*_=ps.transform(run,sel);sel['expected_local_histogram_delta']=delta(out,run);sel['expected_rank_mass']=run['physical']['paid_rank_mass'];sel['expected_removed_calls']=sum(int(c)for c in run['physical']['paid_histogram'].values())-sum(hist(out).values());sel['expected_scalar_additions']=run['physical']['weighted_scalar_events'];run=emit('presink',run,sel);print('PRESINK',sel['expected_local_histogram_delta'],flush=True)
# Terminal sinks freshly screened and frozen.
sm=mod('sink');W=run['W'];old=run['records'];n=2*W.v+len(run['context']['regs']);entry,rows=sm.screen(old,dict(run['initial_state']),dict(finalstate(run)),n,W.v,list(run['physical']['category_names']),run['ZERO'],run['FULL']);used=set();keep=[]
for r in rows:
 if used&set(r['targets']):continue
 used.update(r['targets']);keep.append(r)
assert len(keep)==len(rows)
sel=bind(dict(status='GEN5_TERMINAL_SINKS_PR283_SCREEN',entry=entry,selected=len(keep),sinks=[dict(role=run['context']['regs'][r['stream']-2*W.v],stream=r['stream'],targets=r['targets'],pivot=r['pivot'],root_frame_basis=[list(x)for x in run['C'].B[r['root_frame']]],forward_writes=len(r['writes']),cleanups=len(r['cleanups']))for r in keep],expected_local_delta={}),run);out,*_=sm.transform(run,sel);sel['expected_local_delta']=delta(out,run);run=emit('sink',run,sel);rolemap={i:i for i in range(2*run['W'].v)};newregs=run['context']['regs'];lookup={r:i+2*run['W'].v for i,r in enumerate(newregs)};rolemap.update({i+2*run['W'].v:lookup[r] for i,r in enumerate(base_regs)if r in lookup});(OUT/'baseline-compacted-initial.json').write_text(json.dumps({rolemap[i]:f for i,f in base_initial.items()if i in rolemap}));(OUT/'baseline-compacted-final.json').write_text(json.dumps({rolemap[i]:f for i,f in base_final.items()if i in rolemap}));(OUT/'role-map.json').write_text(json.dumps(rolemap));print('SINK',len(keep),sel['expected_local_delta'],flush=True)
# Run the inherited discovery algorithm in this producer environment; no pipeline rerun.
rm=mod('reorder');TAG='reorder'
src=(PKG/'discovery/build_reorder_selection.py').read_text();env=dict(globals());env['ROOT']=OUT;exec('import math,bisect\nfrom collections import Counter,defaultdict\n'+src[src.index("W,C=run['W']"):],env);sel=env['sel'];run=emit('reorder',run,sel,tag='reorder');export('pre-kernel2',run)
# Rebind the three known rank2 quads to final exact sink-compacted indices.
sel=json.loads((ROOT/'stages/kernel2-selection.json').read_text());old=run['records'];readcat=run['physical']['category_names'].index('dirty_read')
for f in sel['families']:
 members=[f['pivot']]+f['donors'];cut=max(k//6 for k in range(0,len(old),6)if old[k]==1 and old[k+2]in members and old[k+4]==run['ZERO']and old[k+5]==readcat);f['cut_read']=[old[6*cut+j]for j in(1,2,3)]
bind(sel,run);out,init,fin,entries,execution,cats,proof,n,v=mod('kernel').transform(run,sel,'kernel2');sel.update(expected_local_delta=delta(out,run),entrance_rank_histogram=proof['entrance_rank_histogram'],total_entrance_rank=proof['total_entrance_rank'],donor_sharing_histogram=proof['donor_sharing_histogram']);run=emit('kernel2',run,sel,tag='kernel2');export('final',run);print('COMPLETE',flush=True)

assert json.loads((OUT/'target-baseline/meta.json').read_text())['word_sha']==json.loads((pathlib.Path(sys.argv[1])/'predecessor/kernel.json').read_text())['input_raw_sha256'], 'Fresh target prefix disagrees with strict frozen predecessor'
