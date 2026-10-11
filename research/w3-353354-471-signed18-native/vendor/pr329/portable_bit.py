"""Fresh p = 10 local physical and complete five-stage global lowering (source527 integration, rebound).

Inherited source-bound PR234 lowering, integrated with source527 using
substantial OpenAI Codex assistance. Cover expansion is phase-major.
"""
from pathlib import Path
import hashlib,importlib.util,sys,time,json
sys.dont_write_bytecode=True
if not __debug__:raise SystemExit('assertions required')
HERE=Path(__file__).resolve().parent

def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

def phase_major_templates(lower):
 """Expand all cover classes for each yielded phase before advancing."""
 for stage in range(5):
  yield('helper',stage,lambda s=stage:lower.iter_stage(s))
  if stage in(1,2,4):
   i={1:0,2:1,4:2}[stage]
   yield('idle',i,lambda i=i:lower.iter_idle(i))
   yield('bridge',i,lambda i=i:lower.iter_bridges(i))
 yield('completion',0,lower.iter_completions)
 yield('terminal_exchange',0,lower.iter_exchanges)

# Transcript stages, in order (each binds to the exact output word of the previous one). A second descent and a
# second reorder round were searched on this word and found nothing (discovery/README.md), so they are not stages.
STAGES=('descent','target','kernel','restore','sink','descent2','reorder','reorder2')

def completion_census(run):
 """Five-stage completion rank per independent entrance: dim(sigma) + h - dim(endpoint) (endpoint FULL unless restored early)."""
 from collections import Counter
 C=run['C'];W=run['W'];v=W.v;regs=run['context']['regs'];init=run['initial_state'];ends=run.get('helper_endpoints',{});H=Counter()
 for j in range(len(regs)):
  s=2*v+j;a=C.dimf[init[s]]
  if s in ends:assert a and C.sub(init[s],ends[s])
  if a:H[a+W.h-C.dimf[ends.get(s,run["FULL"])]]+=1
 return H

def run(prepared_context=None,raw=None,output_dir=None,run_geometry=True,package_root=None):
 begun=time.monotonic();package=Path(package_root or HERE).resolve()
 if prepared_context is None:prepared_context=load('portable527_prepare',package/'prepare.py').prepare()
 if raw is None:raw=load('portable527_raw_ledger',package/'raw_ledger.py').run(prepared_context)
 physical_module=load('portable527_physical',package/'code/physical527.py')
 context=dict(prepared_context);source=context['SOURCE_TEXT']
 producer_output=Path(output_dir)/'producer-bit' if output_dir is not None else None
 producer=physical_module.run(context,source,output_dir=producer_output)
 physical_run=load('portable527_parity',package/'parity_transform.py').run(producer,output_dir=output_dir)
 raw=load('portable527_parity_raw',package/'raw_ledger.py').rebind_parity(raw,physical_run['parity_census'])
 for name in STAGES:
  if name=='descent':
   physical_run=load('portable527_descent',package/'descent_transform.py').run(physical_run,output_dir=output_dir)
   raw=load('portable527_descent_raw',package/'raw_ledger.py').rebind_descent(raw,physical_run['descent_census'])
  elif name=='target':
   targetmod=load('portable527_target',package/'target_transform.py');physical_run=targetmod.run(physical_run,output_dir=output_dir)
   raw=targetmod.rebind(raw,physical_run['target_census'])
  elif name=='kernel':
   physical_run=load('portable527_kernel',package/'kernel_transform.py').run(physical_run,output_dir=output_dir)
   raw=load('portable527_kernel_raw',package/'raw_ledger.py').rebind_kernel(raw,physical_run['kernel_census'])
  elif name=='restore':
   physical_run=load('portable527_restore',package/'restore_transform.py').run(physical_run,output_dir=output_dir)
   raw=load('portable527_restore_raw',package/'raw_ledger.py').rebind_restore(raw,physical_run['restore_census'],completion_census(physical_run))
  elif name=='sink':
   physical_run=load('portable527_sink',package/'sink_transform.py').run(physical_run,output_dir=output_dir)
   raw=load('portable527_sink_raw',package/'raw_ledger.py').rebind_sink(raw,physical_run['sink_census'],completion_census(physical_run))
  elif name=='descent2':
   physical_run=load('portable527_descent2',package/'descent2_transform.py').run(physical_run,output_dir=output_dir)
   raw=load('portable527_descent2_raw',package/'raw_ledger.py').rebind_descent2(raw,physical_run['descent2_census'],completion_census(physical_run))
  else:
   assert name in('reorder','reorder2')
   physical_run=load('portable527_reorder',package/'reorder_transform.py').run(physical_run,output_dir=output_dir,tag=name)
   raw=load('portable527_'+name+'_raw',package/'raw_ledger.py').rebind_reorder(raw,physical_run[name+'_census'],completion_census(physical_run),name)
 raw['transcript_stages']=list(STAGES)
 # The global lowering binds the final register count of the emitted word (after terminal sinks).
 from word_pins import expect
 assert expect('final_physical_R',len(physical_run['context']['regs']))==raw['physical_R']
 global_module=load('portable527_global',package/'code/global_lowering.py')
 context=physical_run['context']
 physical=physical_run['physical'];physical['source_head']=raw['source_head']
 assert physical['source_heads']==raw['source_aliases']and physical['independent_dirty_registers']==raw['physical_R']
 assert physical['paid_histogram']=={int(k):v for k,v in raw['one_stage_helper_histogram_including_copies'].items()}
 assert physical['initial_independent_entrances']=={int(k):v for k,v in raw['auxiliary_entrance_rank_histogram'].items()}
 lower=global_module.Lowerer(physical_run['records'],physical_run);global_result=global_module.verify(lower,raw)
 assert global_result['paid_histogram']=={int(k):v for k,v in raw['five_stage_profile']['histogram'].items()}
 global_result.update(source_head=raw['source_head'],scalar_projection_sha256=physical['scalar_projection_sha256'],local_tagged_sha256=physical['tagged_scalar_sha256'],weighted_stage_additions=global_result['opcode_counts'][global_module.ADD],bridge_additions=global_result['opcode_counts'][global_module.BRIDGE],total_weighted_additions=global_result['opcode_counts'][global_module.ADD]+global_result['opcode_counts'][global_module.BRIDGE],m=global_module.M,global_live=global_module.LIVE,external_work_family=global_module.WORK)
 phases=[(name,index)for name,index,method in phase_major_templates(lower)]
 assert phases==[('helper',0),('helper',1),('idle',0),('bridge',0),('helper',2),('idle',1),('bridge',1),('helper',3),('helper',4),('idle',2),('bridge',2),('completion',0),('terminal_exchange',0)]
 geometry=None
 if run_geometry:geometry=load('portable527_geometry',package/'code/geometry527.py').run(context,global_module)
 result=dict(context=context,helper_endpoints=physical_run.get('helper_endpoints',{}),**{name+'_census':physical_run[name+'_census']for name in STAGES},W=context['W'],C=context['C'],records=physical_run['records'],lower=lower,raw=raw,physical=physical,global_result=global_result,geometry=geometry,phase_major_schedule=phases,scalar_observer_result=physical_run['scalar_result'],kernel_entrances=physical_run.get('kernel_entrances',[]),seconds=time.monotonic()-begun)
 if output_dir is not None:
  out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
  for name in('physical','global_result','geometry','raw'):
   if result[name]is not None:(out/(name+'.json')).write_text(json.dumps(result[name],indent=2)+'\n')
 return result

def summary(result):
 return dict(status='PASS_PORTABLE_P10_FRESH_PHYSICAL_GLOBAL_AND_GEOMETRY',source_head=result['raw']['source_head'],local_record_count=len(result['records'])//6,scalar_projection_sha256=result['physical']['scalar_projection_sha256'],physical_tagged_sha256=result['physical']['tagged_scalar_sha256'],global_result=result['global_result'],geometry=result['geometry'],phase_major_schedule=result['phase_major_schedule'],seconds=result['seconds'])
