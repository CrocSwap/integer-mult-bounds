"""Fresh restoration, terminal sinks and reorder selections on an admitted p10b kernel.
Inherited exact transformations retain their own provenance; binding/discovery by OpenAI Codex.
"""
import sys,json,importlib.util,hashlib,collections,pathlib,gzip
if not __debug__:raise SystemExit("Assertions required")
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[1];PKG=ROOT/'vendor/predecessor';PROOF=pathlib.Path(sys.argv[1]);OUT=PROOF/'materialized';KSEL=ROOT/'stages/kernel-selection.json';OUT.mkdir();sys.path.insert(0,str(PKG));PIN=json.loads((ROOT/'SOURCE.json').read_text())
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
# Python 3.12 changed built-in float sum to compensated summation. The
# inherited discovery used Python 3.11's ordered left fold for its floating
# ranking ties. Pin that discovery-only numerical convention explicitly;
# every selected move and resulting word is still admitted exactly.
def discovery_sum(values,start=0):
 total=start
 for value in values:total+=value
 return total
DISCOVERY_PHI={int(k):float.fromhex(v)for k,v in json.loads((ROOT/'discovery/phi-hex.json').read_text()).items()}
assert set(DISCOVERY_PHI)==set(range(21))
mods={}
def mod(st):
 if st not in mods:mods[st]=load('portable527_p10b_'+st,(PKG if st=='parity' else ROOT/'engines')/(st+'_transform.py'))
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
 path=OUT/(st+'-selection.json');pin=ROOT/'stages'/(st+'-selection.json');assert json.loads(json.dumps(sel))==json.loads(pin.read_text()),'Regenerated selection differs: '+st;path.write_text(json.dumps(sel,indent=2)+'\n');assert hashlib.sha256(path.read_bytes()).digest()==hashlib.sha256(pin.read_bytes()).digest(),'Selection bytes differ: '+st;return path
def emit(st,run,sel,tag=None):
 path=save(st,sel);return mod(st).run(run,output_dir=OUT/st,selection_path=path,**({'tag':tag}if tag else{}))
def finalstate(run):
 final=dict(run['initial_state']);old=run['records']
 for k in range(0,len(old),6):
  if old[k]==0:final[old[k+1]]=old[k+3]
 return final
def export(st,run):
 dest=OUT/st;dest.mkdir(exist_ok=True);W,C=run['W'],run['C'];rec=run['records'];regs=run['context']['regs'];v=W.v;n=2*v+len(regs);init=dict(run['initial_state']);final=finalstate(run);used={r['frame_id']for r in run['physical']['used_frames']}|set(init.values())|set(final.values());frames={str(f):dict(A=C.A[f],B=C.B[f],dim=C.dimf[f])for f in sorted(used)}
 meta=dict(n=n,v=v,R=len(regs),ZERO=run['ZERO'],FULL=run['FULL'],category_names=run['physical']['category_names'],regs=regs,raw_sha256=hashlib.sha256(rec.tobytes()).hexdigest(),scalar_projection_sha256=run['physical']['scalar_projection_sha256'],source_head='Fresh all-rank donor-flow PR325 derivative plus pinned descent/target/kernel/restore/sink/reorder/descent2')
 for name,value in [('regs',regs),('initial',init),('final',final),('frames',frames),('physical',run['physical']),('meta',meta)]:(dest/(name+'.json')).write_text(json.dumps(value,indent=2)+'\n')
 (dest/'records.bin').write_bytes(rec.tobytes());print('EXPORT',st,meta['raw_sha256'],run['physical']['weighted_scalar_events'],sum(run['physical']['paid_histogram'].values()),len(rec)//6,flush=True)
ctx=load('portable527_prepare',PKG/'prepare.py').prepare();run=load('portable527_physical',PKG/'code/physical527.py').run(dict(ctx),ctx['SOURCE_TEXT']);run=mod('parity').run(run)
export('parity-baseline',run)
assert run['records'].tobytes()==gzip.decompress((PROOF/'predecessor/records.bin.gz').read_bytes()),'Original parity word disagrees with fresh strict predecessor'
assert json.loads((OUT/'parity-baseline/physical.json').read_text())['used_frames']==json.loads((PROOF/'predecessor/physical.json').read_text())['used_frames']
for st in ('descent','target'):
 path=OUT/(st+'-selection.json');path.write_bytes((ROOT/'stages'/(st+'-selection.json')).read_bytes());run=mod(st).run(run,output_dir=OUT/st,selection_path=path)
export('target',run)
assert hashlib.sha256(run['records'].tobytes()).hexdigest()==PIN['target_prefix_sha256']
base_initial=dict(run['initial_state']);base_final=finalstate(run);base_regs=list(run['context']['regs']);run=mod('kernel').run(run,output_dir=OUT/'kernel',selection_path=KSEL);save('kernel',json.load(open(KSEL)))
rt=mod('restore');W,C=run['W'],run['C'];old=run['records'];n=2*W.v+len(run['context']['regs']);initial=dict(run['initial_state']);cats=list(run['physical']['category_names']);cut,rows,state=rt.screen(old,initial,n,W.v,C,W,cats,run['ZERO'],run['FULL']);entries=[]
for a,b,i,c,fa,fb in rows:
 E=W.register([list(x)for x in C.B[fa]]+[list(x)for x in C.B[fb]])
 if C.dimf[E]==W.h or not C.nondeg(E):continue
 entries.append(dict(helper=a,donor=b,coefficient=c,incidence=[old[6*i+j]for j in(1,2,3)],rank=C.dimf[E],basis=[list(x)for x in C.B[E]],dims=[C.dimf[initial[a]],C.dimf[fa],C.dimf[fb],C.dimf[E]]))
sel=bind(dict(status='P10B_FRESH_EARLY_RESTORATION_SCREEN',cut=cut,selected=len(entries),entries=entries,expected_local_delta={}),run);out,*_=rt.transform(run,sel);sel['expected_local_delta']=delta(out,run);run=emit('restore',run,sel);export('post-restore',run)
sm=mod('sink');W=run['W'];old=run['records'];n=2*W.v+len(run['context']['regs']);entry,rows=sm.screen(old,dict(run['initial_state']),finalstate(run),n,W.v,list(run['physical']['category_names']),run['ZERO'],run['FULL']);used=set();keep=[]
for r in rows:
 if used&set(r['targets']):continue
 used.update(r['targets']);keep.append(r)
assert len(keep)==len(rows)
sel=bind(dict(status='P10B_FRESH_TERMINAL_SINKS_SCREEN',entry=entry,selected=len(keep),sinks=[dict(role=run['context']['regs'][r['stream']-2*W.v],stream=r['stream'],targets=r['targets'],pivot=r['pivot'],root_frame_basis=[list(x)for x in run['C'].B[r['root_frame']]],forward_writes=len(r['writes']),cleanups=len(r['cleanups']))for r in keep],expected_local_delta={}),run);out,*_=sm.transform(run,sel);sel['expected_local_delta']=delta(out,run);run=emit('sink',run,sel);rolemap={i:i for i in range(2*run['W'].v)};lookup={r:i+2*run['W'].v for i,r in enumerate(run['context']['regs'])};rolemap.update({i+2*run['W'].v:lookup[r]for i,r in enumerate(base_regs)if r in lookup});(OUT/'baseline-compacted-initial.json').write_text(json.dumps({rolemap[i]:f for i,f in base_initial.items()if i in rolemap}));(OUT/'baseline-compacted-final.json').write_text(json.dumps({rolemap[i]:f for i,f in base_final.items()if i in rolemap}));(OUT/'role-map.json').write_text(json.dumps(rolemap));export('post-sink',run)
rm=mod('reorder');TAG='reorder';src=(ROOT/'discovery/build_reorder_selection.py').read_text();phi_definition='phi=lambda r:r*math.log(100/r)if r else 0.0';assert src.count(phi_definition)==1;src=src.replace(phi_definition,'phi=lambda r:DISCOVERY_PHI[r]');env=dict(globals());env['ROOT']=OUT;env['sum']=discovery_sum;exec('import math,bisect\nfrom collections import Counter,defaultdict\n'+src[src.index("W,C=run['W']"):],env);sel=env['sel'];run=emit('reorder',run,sel,tag='reorder');export('before-descent2',run)
path=OUT/'descent2-selection.json';path.write_bytes((ROOT/'stages/descent2-selection.json').read_bytes());run=mod('descent2').run(run,output_dir=OUT/'descent2',selection_path=path);export('final',run);print('COMPLETE',flush=True)

assert hashlib.sha256(run['records'].tobytes()).hexdigest()==PIN['final_word_sha256']
