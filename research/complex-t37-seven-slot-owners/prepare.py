"""Reuse PR942's explicit source adapters and build the five-bank parent.

Only the frozen order, owner map, and PR1022 supplier metadata are replaced.
The PR942 finite invoice still charges its 1024-bit prefix reserve.
"""
import copy,os,shutil
from common import P,ROOT,read,dump,load,sha,identity

def prepare(work,baseline):
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
              ('the gauge44-barch U8 local word and all 72 cold helper ends','the PR1022 seven-slot k8 local word'),
              ('explicit all333 whole-owner dispatch with a T21 plus T16 eight-role trade','explicit 333-call wave dispatch with frozen integer pattern flows'),
              ('This is a new T37 composition of the PR870 U8 and PR589 suppliers.','This is a new T37 composition of the PR1022 seven-slot k8 and PR589 suppliers.')]:
                assert text.count(before)==1,(before,text.count(before));text=text.replace(before,after);extra.append([before,after,1])
        target.write_text(text,encoding='utf-8',newline='\n')
        receipts[name]=dict(source_sha256=sha(record['source']),generated_sha256=sha(target),edits=record.get('edits',[]),description_edits=extra)
    dump(work/'ADAPTATIONS.json',receipts)
    source=read(baseline/'global/base/split-centres/GLOBAL-TEMPLATE.json.gz')
    builder=load(adapted/'build_parent.py','retained_t37_parent_lift');parent=builder.lift(source)
    slots=P/'vendor/pr1022/research/gauge44-slots'
    plan=read(slots/'data/PLAN.json');order=read(P/'data/ORDER.json');owners=read(P/'data/OWNERS.json.gz')
    windows_mod=load(t21/'vendor/pr870/t16/build_parent.py','retained_physical_windows')
    windows,schedule=windows_mod.actual_windows(parent,order)
    for field in ('provider_calls','per_call_widths'):
        lookup={(c['stage'],c['replica']):c for c in plan[field]};plan[field]=[]
        for time,(stage,replica)in enumerate(order):
            call=copy.deepcopy(lookup[stage,replica%8]);call['replica']=replica
            if 'time'in call:call['time']=time
            plan[field].append(call)
    claim=read(P/'CLAIM.json')
    plan.update(T=37,live=33152,deficit=11840,order=order,windows=windows,profile=claim['complex_profile'],
      status='FROZEN_T37_SEVEN_SLOT_WHOLE_OWNER_NOMINATION',mode='gauge44-seven-slot-k8-t37-wave',
      solver_status='Frozen integer pattern flow, reconstructed by regular bipartite matching; no optimizer runs',
      assignment_sha256=sha(P/'data/OWNERS.json.gz'),assignment_content_sha256=identity(owners),
      replica_lift=dict(groups=[8,8,8,8,5],source_replicas=8,replicas=37,parent_template_content_sha256=identity(parent),
        owners_file_sha256=sha(P/'data/OWNERS.json.gz'),schedule_content_sha256=identity(schedule),window_semantics='Strict physical source-event intervals, including bridges'))
    assert len(owners)==159840 and sum(int(r)*n for r,n in plan['profile'].items())==73*33152-11840
    for z in owners:
        assert order[z['time']]==[z['stage'],z['replica']]
        assert z['time']in windows[f"{z['owner_replica']},{z['child']}"][1]
    lift=work/'lift';lift.mkdir();dump(lift/'GLOBAL-TEMPLATE.json.gz',parent);dump(lift/'PLAN.json',plan)
    parentdir=work/'parent';shutil.copytree(baseline/'parent558',parentdir)
    shutil.copyfile(lift/'GLOBAL-TEMPLATE.json.gz',parentdir/'complex-global/base/split-centres/GLOBAL-TEMPLATE.json.gz')
    (runtime/'data').mkdir(exist_ok=True)
    spec=read(P/'data/SPEC.json')
    assert spec['data']=={'owners_sha256':sha(P/'data/OWNERS.json.gz'),'plan_sha256':sha(lift/'PLAN.json')},'Frozen owner/plan bindings differ'
    spec['pivot_swap']['recipe']=str((P/spec['pivot_swap']['recipe']).resolve())
    dump(runtime/'data/SPEC.json',spec)
    return plan
