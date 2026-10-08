"""Durable independent CPU search over pinned current two-cycle construction.
Each accepted case regenerates and independently replays the literal word,
reconstructs paid frames, computes CPU CRT profiles and exact inequalities.
"""
from pathlib import Path
from hashlib import sha256
from concurrent.futures import ProcessPoolExecutor,as_completed
import argparse,ast,cProfile,gzip,importlib.util,json,os,pstats,subprocess,sys,time,types
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'scripts/experiments'))

def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def generate(h,groups,profile=False,mode="baseline",output_mode=None,coordinate=None,label="search",pricing=False,three_cycle_passes=0,node_order="pr74"):
 started=time.monotonic();out=ROOT/'results'/f'{h}-{groups}-{mode}-{output_mode}-{label}';out.mkdir(parents=True,exist_ok=True)
 compiler=load('search_compiler',ROOT/'scripts/experiments/compiler.py')
 source=(ROOT/'research/pair-assembly/pair_graph.py').read_text()
 donor=ROOT/'references/pr69/balanced_coarse_compiler.py'
 constants={n.targets[0].id:ast.literal_eval(n.value) for n in ast.parse(donor.read_text()).body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id in ('BEFORE','AFTER')}
 replacement=constants['AFTER'];needle='columns = [self.total([e(a,b) for a in groups[i]]) for b in groups[j]]'
 orientation=mode.removeprefix('envelope-') if mode.startswith('envelope-') else ('half' if h==23 else 'row')
 if orientation=='half':
  replacement=replacement.replace(needle,'columns = ([self.total([e(a,b) for a in groups[i]]) for b in groups[j]] if i+j < ng-1 else [self.total([e(a,b) for b in groups[j]]) for a in groups[i]])')
 elif orientation=='row':replacement=replacement.replace(needle,'columns = [self.total([e(a,b) for b in groups[j]]) for a in groups[i]]')
 assert source.count(constants['BEFORE'])==1
 graph=types.ModuleType('balanced_graph');graph.__file__=str(ROOT/'research/pair-assembly/pair_graph.py');exec(compile(source.replace(constants['BEFORE'],replacement),graph.__file__,'exec'),graph.__dict__)
 original=graph.circuit_class
 def subclass(dim):
  parent=original(dim)
  class Split(parent):
   def grouping(self,points):
    result=super().grouping(points);choices=[int(x) for x in groups];choice=choices[self._level] if self._level<len(choices) else 0
    if len(points)>3 and choice:
     first,mid,last=0,(len(result)-1)//2,len(result)-1
     requested={1:[first],2:[mid],3:[last],4:[first,mid],5:[first,last],6:[mid,last],7:[first,mid,last],8:[first,first+1],9:[last-1,last]}[choice]
     chosen=[]
     for k in requested:
      if k not in chosen and 0<=k<len(result) and len(result[k])==2 and len(result)+len(chosen)+1<len(points):chosen.append(k)
     for k in sorted(chosen,reverse=True):result[k:k+1]=[[x] for x in result[k]]
     assert sorted(x for group in result for x in group)==sorted(points)
    assert all(len(g) in (1,2) for g in result) and len(result)<len(points)
    return result
  return Split
 graph.circuit_class=subclass
 original_points=graph.alternating_points
 def anchored(dim,common):
  before=original_points(dim,common);chosen=min((a,a+1) for a in range(0,dim-1,2) if common not in (a,a+1))
  result=list(chosen)+[x for x in before if x not in chosen];assert sorted(result)==[x for x in range(dim) if x!=common];return result
 graph.alternating_points=anchored
 if mode.startswith('envelope-'):
  from nodeops import reorder,verify_dense
  original_graph=graph.graph;graph.graph=lambda dim:reorder(original_graph(dim),node_order)
 else:
  schedule=load('schedule',ROOT/'research/reordered-rank-pair/verify.py');compiler.build=schedule.reordered_build(compiler.build,'cover-core' if h==23 else 'reverse-node')
 compiler.graph=graph.graph
 checked=graph.graph(h);scalar=checked.verify();scalar['dense_global_support']=verify_dense(checked);(out/'scalar.json').write_text(json.dumps(scalar,indent=2)+'\n')
 compiler.OUTPUT_MODE=('route-late' if h==25 else 'baseline') if mode.startswith('envelope-') else mode;compiler.OUTPUT_MODE=output_mode if output_mode is not None else compiler.OUTPUT_MODE;compiler.ORACLE_COORDINATES=coordinate if pricing else list(range(h));compiler.THREE_CYCLE_PASSES=three_cycle_passes;compiler.PENDING_COST=True;compiler.oracles=[];compiler.ORACLE_EXE=str(ROOT/'bin/profile-oracle');compiler.ORACLE_INPUT=str(out/'oracle-input.bin')
 timer=time.monotonic();profiler=cProfile.Profile() if profile else None
 try:
  if profiler:profiler.enable()
  result,word=compiler.compile_(h,matching=True,reclaim=True,dirty=True)
 finally:
  if profiler:profiler.disable();profiler.dump_stats(str(out/'compile.prof'))
  for p in compiler.oracles:
   p.stdin.close();assert p.wait()==0
 compile_seconds=time.monotonic()-timer
 from nodeops import relabel
 if coordinate is not None:word=relabel(word,coordinate)
 raw=(json.dumps(word,separators=(',',':'))+'\n').encode();path=out/'word.json.gz';path.write_bytes(gzip.compress(raw,mtime=0))
 (out/'compiler-result.json').write_text(json.dumps(result,indent=2)+'\n')
 from binary_frame_replay import replay
 from binary_frame_profile_prepare import prepare
 timer=time.monotonic();replayed=replay(path);(out/'replay.json').write_text(json.dumps(replayed,indent=2)+'\n');replay_seconds=time.monotonic()-timer
 timer=time.monotonic();transitions=prepare(path,out/'transitions.bin');(out/'transitions.json').write_text(json.dumps(transitions,indent=2)+'\n')
 with (out/'profiles.log').open('w') as log:subprocess.run([str(ROOT/'bin/profiles'),str(out/'transitions.bin')],stdout=log,stderr=log,check=True)
 (out/'profiles.json').write_bytes((out/'transitions.bin.profiles.json').read_bytes());p=json.loads((out/'profiles.json').read_text());assert p['R']==replayed['roles']==result['roles'] and p['crt_disagreements']==0
 profile_seconds=time.monotonic()-timer
 summary={'h':h,'groups':groups,'mode':mode,'roles':result['roles'],'word_sha256':sha256(raw).hexdigest(),'stats':result['stats'],'full_physical_replay':'PASS both orientations','exact_CRT_profiles':'PASS','compile_seconds':compile_seconds,'replay_seconds':replay_seconds,'profile_seconds':profile_seconds}
 (out/'result.json').write_text(json.dumps(summary,indent=2)+'\n')
 ev=load('evaluate_case',ROOT/'evaluate.py');ev.baseline=json.loads((ROOT/'research/reordered-rank-pair/paired-candidate.json').read_text())
 profiles={d:ev.load(ROOT/'frozen'/f'h{d}') for d in (23,25)};profiles[h]=p;r=ev.fine(profiles)
 (out/'exact-result.json').write_text(json.dumps(ev.refine.arithmetic.js(r),indent=2,sort_keys=True)+'\n')
 summary.update(node_order=node_order,pricing=pricing,three_cycle_passes=three_cycle_passes,output_mode=output_mode,coordinate_permutation=coordinate,label=label,path=str(out.relative_to(ROOT)),kappa=str(r['kappa']),bit_saving=str(r['bit_saving']),W=r['bit']['W'],seconds=time.monotonic()-started)
 if groups=='112' and mode=='baseline':
  old=json.loads((ROOT/'baseline'/f'h{h}/result.json').read_text());assert summary['word_sha256']==old['word_sha256'],'Portable canary word differs'
  assert p==json.loads((ROOT/'baseline'/f'h{h}/profiles.json').read_text()),'Portable canary profile differs'
  assert str(r['kappa'])=='808741875211/15625000000000000','Portable canary exact certificate differs'
  summary['baseline_equality']='PASS word/profile/exact saving'
 if profiler:
  with (out/'compile-profile.txt').open('w') as log:pstats.Stats(profiler,stream=log).sort_stats('cumulative').print_stats(30)
 (out/'summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n');return summary
