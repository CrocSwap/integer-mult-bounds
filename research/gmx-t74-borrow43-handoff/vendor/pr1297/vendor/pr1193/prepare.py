"""Reuse PR942's explicit source adapters and build the five-bank parent.

The frozen order, owner map, and PR1148 supplier metadata are replaced.
The PR942 finite invoice still charges its 1024-bit prefix reserve.
"""
import copy,os,shutil
from common import P,ROOT,read,dump,load,sha,identity

def prepare(work,baseline,providers):
    t37=ROOT/'research/complex-t37-owners'
    t21=ROOT/'research/complex-t21-owners'
    os.environ.update(T37_WORK=str(work),T37_BASELINE=str(baseline))
    old=load(t37/'prepare.py','retained_t37_preparation')
    runtime=work/'runtime';adapted=work/'adapted';adapted.mkdir()
    load(t21/'source_adapters.py','retained_t21_adapters').materialize(runtime)
    (runtime/'ADAPTERS.json').rename(runtime/'T21-INTERMEDIATE-ADAPTERS.json')
    receipts={}
    for name,record in old.expected_adaptations().items():
        target=runtime/'code'/name.split('/',1)[1]if name.startswith('runtime/')else adapted/name
        text=record['text'];extra=[]
        if name=='runtime/assemble.py':
            for before,after in [
              ('the gauge44-barch U8 local word and all 72 cold helper ends','the mixed joint-entrance three- and four-demotion k8 local words'),
              ('explicit all333 whole-owner dispatch with a T21 plus T16 eight-role trade','explicit 333-call wave dispatch with frozen integer pattern flows'),
              ('This is a new T37 composition of the PR870 U8 and PR589 suppliers.','This is a new T37 composition of the mixed joint-entrance three- and four-demotion k8 and PR589 suppliers.')]:
                assert text.count(before)==1,(before,text.count(before));text=text.replace(before,after);extra.append([before,after,1])
        if name=='runtime/freeze_spec.py':
            for before,after in [("spec['expected']['assembly_controls_rejected'] = 69","spec['expected']['assembly_controls_rejected'] = 114"),
              ("spec['expected']['provider_counts'] = {'gauge44':333}","spec['expected']['provider_counts'] = dict(__import__('collections').Counter(pid for s,r,pid in spec['dispatch']))"),
              ("spec['expected']['mutations_rejected'] = 15","spec['expected']['mutations_rejected'] = 23")]:
                assert text.count(before)==1
                text=text.replace(before,after);extra.append([before,after,1])
        target.write_text(text,encoding='utf-8',newline='\n')
        receipts[name]=dict(source_sha256=sha(record['source']),generated_sha256=sha(target),edits=record.get('edits',[]),description_edits=extra)
    dump(work/'ADAPTATIONS.json',receipts)
    source=read(baseline/'global/base/split-centres/GLOBAL-TEMPLATE.json.gz')
    builder=load(adapted/'build_parent.py','retained_t37_parent_lift');parent=builder.lift(source)
    plan=read(P/'vendor/pr1148/PLAN.json.gz');order=read(P/'data/ORDER.json');owners=read(P/'data/OWNERS.json.gz')
    windows_mod=load(t21/'vendor/pr870/t16/build_parent.py','retained_physical_windows')
    windows,schedule=windows_mod.actual_windows(parent,order)
    mix=read(P/'data/MIX.json')
    assert [[s,r]for pid,s,r in mix]==order
    identities=load(ROOT/'research/complex-t21-owners/vendor/pr870/code/generated_identity.py','mixed_artifact_identities')
    plan['provider_registry']={};plan['provider_calls']=[];plan['per_call_widths']=[]
    for pid,directory in sorted(providers.items()):
        word=read(directory/'CANONICAL-WORD.json.gz');checks=read(directory/'LOCAL-CHECKS.json')
        widths=[len(word['frames'][word['final'][h]])-len(word['frames'][word['start'][h]])for h in range(224,704)]
        plan['provider_registry'][pid]=dict(directory='providers/'+pid,artifact_sha256={n:sha(directory/n)for n in identities.FILES},
          ports=word['ports'],centers=word['centers'],widths=widths,actual_paid_profile=word['local_profile'],
          orientation_program_sha256={o:checks[o]['sha256']for o in ('forward','backward')},artifact_semantic_sha256=identities.artifact_identities(directory))
    for time,(pid,stage,replica)in enumerate(mix):
        desc=plan['provider_registry'][pid];orientation='forward'if stage%2==0 else'backward'
        plan['provider_calls'].append(dict(time=time,stage=stage,replica=replica,provider=pid,orientation=orientation,local_program_sha256=desc['orientation_program_sha256'][orientation]))
        plan['per_call_widths'].append(dict(stage=stage,replica=replica,widths=desc['widths']))
    claim=read(P/'CLAIM.json')
    plan.update(T=37,live=33152,deficit=11840,order=order,windows=windows,profile=claim['complex_profile'],
      status='FROZEN_T37_MIXED_DEMOTIONS_WHOLE_OWNER_NOMINATION',mode='gauge44-three-demotions-t37-wave',
      solver_status='Frozen integer pattern flow, reconstructed by regular bipartite matching; no optimizer runs',
      assignment_sha256=sha(P/'data/OWNERS.json.gz'),assignment_content_sha256=identity(owners),
      replica_lift=dict(groups=[8,8,8,8,5],source_replicas=8,replicas=37,parent_template_content_sha256=identity(parent),
        owners_file_sha256=sha(P/'data/OWNERS.json.gz'),schedule_content_sha256=identity(schedule),window_semantics='Strict physical source-event intervals, including bridges'))
    assert len(owners)==159840 and sum(int(r)*n for r,n in plan['profile'].items())==73*33152-11840
    for z in owners:
        assert order[z['time']]==[z['stage'],z['replica']]
        assert z['time']in windows[f"{z['owner_replica']},{z['child']}"][1]
    frozen=read(P/'data/PLAN.json.gz')
    for pid,desc in plan['provider_registry'].items():
        # Regenerated compression and timing are rebound by the unchanged
        # native binder. All proof-relevant semantic identities must agree.
        assert desc['artifact_semantic_sha256']==frozen['provider_registry'][pid]['artifact_semantic_sha256']
        desc['artifact_sha256']=frozen['provider_registry'][pid]['artifact_sha256']
    assert plan==frozen,'Derived geometry/dispatch/provider plan differs from frozen nomination'
    lift=work/'lift';lift.mkdir();dump(lift/'GLOBAL-TEMPLATE.json.gz',parent);dump(lift/'PLAN.json',plan)
    parentdir=work/'parent';shutil.copytree(baseline/'parent558',parentdir)
    shutil.copyfile(lift/'GLOBAL-TEMPLATE.json.gz',parentdir/'complex-global/base/split-centres/GLOBAL-TEMPLATE.json.gz')
    (runtime/'data').mkdir(exist_ok=True)
    spec=read(P/'data/SPEC.json')
    assert spec['call_order']==order and spec['dispatch']==[[s,r,pid]for pid,s,r in mix]
    assert spec['data']=={'owners_sha256':sha(P/'data/OWNERS.json.gz'),'plan_sha256':sha(lift/'PLAN.json')}
    pivot=ROOT/'research/gauge44-slots/construction/leaver/PIVOT-SWAP-k8.json'
    assert sha(pivot)==spec['pivot_swap']['sha256']
    spec['pivot_swap']['recipe']=str(pivot.resolve())
    dump(runtime/'data/SPEC.json',spec)
    return plan
