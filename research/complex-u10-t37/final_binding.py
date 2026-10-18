"""Bind the fresh T37 receipts to one complete checked construction.

Finite receipt consistency is not authentication or an all-size theorem.
Adapted from PR890's explicit binding inventory; Apache-2.0.
"""
import argparse,gzip,hashlib,json,sys
from fractions import Fraction as Q
from pathlib import Path
from common import ROOT,P,T21,read,load

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def identity(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()

if not __debug__:
    raise RuntimeError('Assertions must remain enabled; do not use Python -O')

def content_sha(p):
    data=p.read_bytes()
    return hashlib.sha256(gzip.decompress(data) if p.suffix=='.gz' else data).hexdigest()

def check_adaptations(work):
    """Read-only regeneration from fixed source/edit code, never receipt edits."""
    expected=load(P/'prepare.py','t37_expected_adapters').expected_adaptations()
    records=read(work/'ADAPTATIONS.json')
    assert set(records)==set(expected),'Complete authorized adapter inventory'
    assert {p.name for p in (work/'adapted').glob('*.py')}=={n for n in expected if not n.startswith('runtime/')}
    assert {p.name for p in (work/'runtime/code').glob('*.py')}=={n.split('/',1)[1] for n in expected if n.startswith('runtime/')}
    for name,wanted in expected.items():
        generated=(work/'runtime/code'/name.split('/',1)[1]) if name.startswith('runtime/') else work/'adapted'/name
        data=wanted['text'].encode('utf-8')
        assert generated.read_bytes()==data,('Exact authorized adapter bytes',name)
        record=dict(source_sha256=sha(wanted['source']),generated_sha256=hashlib.sha256(data).hexdigest())
        if 'edits' in wanted:record['edits']=wanted['edits']
        assert records[name]==record,('Exact authorized adapter record',name)
    source=T21/'vendor/pr870/inputs';generated=work/'runtime/inputs'
    source_files={p.relative_to(source).as_posix():sha(p) for p in source.rglob('*') if p.is_file()}
    actual_files={p.relative_to(generated).as_posix():sha(p) for p in generated.rglob('*') if p.is_file()}
    assert actual_files==source_files,'Immutable runtime input copies'
    return {name:records[name]['generated_sha256'] for name in sorted(records)}

def check_construction(work):
    receipt=read(work/'CONSTRUCTION-CHECK.json')
    assert receipt['status']=='PASS_INDEPENDENT_FROZEN_T37_RECONSTRUCTION_NO_SEARCH'
    for key,value in dict(roles=167832,calls=333,edits=8,inherited_t16_edits=11,inherited_t21_edits=9,
                          source_plan_pin_verified=True,source_owner_pin_verified=True).items():
        assert receipt[key]==value,('Construction coverage',key)
    assert receipt['owner_content_sha256']==identity(read(P/'OWNERS.json.gz'))
    assert receipt['order_content_sha256']==identity(read(P/'ORDER.json'))
    paths=[ROOT/'research/gauge44-frames-x/data/PLAN.json',ROOT/'research/gauge44-frames-x/data/OWNERS.json.gz',
           T21/'vendor/pr870/t16/build_owners.py',T21/'data/T5-OWNERS.json.gz',T21/'data/EDITS.json',
           P/'EDITS.json',P/'OWNERS.json.gz',P/'ORDER.json']
    assert receipt['inputs']=={str(p.resolve()):sha(p) for p in paths},'Construction input bytes'

def check_independent_inputs(work,baseline):
    receipt=read(work/'INDEPENDENT-OWNERS.json');native=work/'native10/local';base=baseline/'global/global/base'
    assert receipt['status']=='PASS_INDEPENDENT_VARIABLE_T_LITERAL_WINDOWS_CHARTS_PREFIX_ROW'
    assert receipt['baseline_mode']=='provided_replay_base'
    paths=[native/'CANONICAL-WORD.json.gz',native/'INDEPENDENT-LOCAL-REPLAY.json',P/'OWNERS.json.gz',P/'EDITS.json',T21/'independent_check.py',
           base/'split-centres/GLOBAL-TEMPLATE.json.gz',base/'split-centres/CANONICAL-WORD.json.gz',base/'work/complex-nine-native/DATA-PHASES.json']
    assert receipt['input_sha256']=={str(p.resolve()):sha(p) for p in paths},'Independent owner input bytes'
    changes=[['2 * 512','2 * 1024',1],['prefix < 512','prefix < 1024',1],
             ['charged_prefix_bits=512','charged_prefix_bits=1024',1],['1 <= T <= 22','1 <= T <= 50',1]]
    source=T21/'independent_check.py';text=source.read_text()
    for before,after,count in changes:
        assert text.count(before)==count
        text=text.replace(before,after)
    adapter=work/'independent_check_1024.py'
    assert adapter.read_text()==text,'Independent checker exact source adaptation'
    assert receipt['checker_adaptation']==dict(source_sha256=sha(source),adapted_sha256=sha(adapter),changes=changes)

def check_payload_artifacts(work):
    """Bind actual controller, charts, idle axes and provider bytes to receipts."""
    g=work/'strict/global';hosted=g/'hosted';base=g/'base'
    summary=read(hosted/'HOSTED.json');owner=read(g/'audit/OWNERS-AND-PROFILE.json')
    controller=read(g/'audit/ASYNC-AUDIT.json');invoice=read(g/'audit/PREFIX-AND-INVOICE.json')
    template=read(hosted/'GLOBAL-TEMPLATE.json.gz');template_hash=content_sha(hosted/'GLOBAL-TEMPLATE.json.gz')
    assert template_hash==summary['template_sha256']==owner['template_sha256']==controller['complex_template_sha256']==invoice['template_sha256'],'Actual emitted template bytes'
    assert template['hosting']['owner_map_sha256']==sha(P/'OWNERS.json.gz')
    assert template['hosting']['pooled_slots']==read(P/'OWNERS.json.gz'),'Actual serialized frozen roles'
    assert template['async_schedule']['order']==read(P/'ORDER.json')
    assert summary['asynchronous_order_sha256']==identity(read(P/'ORDER.json'))
    expected_sources={'work/complex-nine-native/DATA-PHASES.json'}|{'providers/gauge44/'+name for name in
       ('CANONICAL-WORD.json.gz','LOCAL-PROGRAMS.json.gz','LOCAL-CHECKS.json','INDEPENDENT-LOCAL-REPLAY.json','RESIDUAL-ADAPTERS.json','CLIFFORD-RECIPES.json','CLIFFORD-REVIEW.json')}
    assert set(summary['source_artifacts'])==expected_sources,'Complete source-artifact inventory'
    assert owner['source_artifacts']==summary['source_artifacts']
    for relative,expected in summary['source_artifacts'].items():
        path=(base/relative).resolve()
        assert not Path(relative).is_absolute() and path.is_relative_to(base.resolve()),'Source-artifact path'
        assert sha(path)==expected,('Actual provider/phase bytes',relative)
    binding=read(g/'BINDING.json');plan=read(g/'PLAN.json')
    assert binding['status']=='PASS_FROZEN_048_ALLCOLD_DISPATCH_FRESH_PROVIDER_BINDING'
    assert binding['source_plan_sha256']==plan['runtime_source_plan_sha256']==sha(work/'lift/PLAN.json')
    assert binding['runtime_plan_sha256']==sha(g/'PLAN.json')
    assert template['async_schedule']['source_plan_sha256']==hashlib.sha256((g/'PLAN.json').read_bytes().replace(b'\r\n',b'\n')).hexdigest()
    assert set(binding['providers'])=={'gauge44'}
    provider_names={Path(p).name for p in expected_sources if p.startswith('providers/')}
    assert set(binding['providers']['gauge44']['artifact_sha256'])==provider_names
    for name,expected in binding['providers']['gauge44']['artifact_sha256'].items():
        assert sha(base/'providers/gauge44'/name)==expected,('Bound provider artifact',name)
    # The chart digest is a role stream, not a hash of the dictionary file.
    canonical=read(base/'providers/gauge44/CANONICAL-WORD.json.gz');phases=read(base/'work/complex-nine-native/DATA-PHASES.json')
    bases=[]
    for port in canonical['ports']:
        zero=next(i for i in range(9) if not(port>>i&1));correction=port^(1<<zero)
        axes=list(range(9));axes[0],axes[zero]=axes[zero],axes[0]
        bases.append([(1<<i)^(correction if correction>>i&1 else 0) for i in axes]+[1<<i for i in range(9,73)])
    sigmas={};cache={};stream=hashlib.sha256()
    for call in template['calls']:
        for helper,(family,route) in enumerate(call['owners'][224:]):
            port=family%112;child,offset=route[1:3];width=9 if route[0]==3 else route[3]
            key=(port,child,offset,width)
            if key not in cache:
                B=bases[port];pending=list(map(int,phases['recipes'][port]['idle_children'][child]['orthogonal_axes']))
                occupied=[B.index(v) for v in pending[offset:offset+width]]
                spectators=[j for j in range(73) if j not in occupied][:9-width]
                expected_route=[3,child,offset] if width==9 else [4,child,offset,width,spectators]
                order=occupied+spectators+[j for j in range(73) if j not in occupied and j not in spectators]
                sigma=[B[j] for j in order];sh=hashlib.sha256(json.dumps(sigma,separators=(',',':')).encode()).hexdigest()
                cache[key]=(sh,expected_route);sigmas[sh]=sigma
            sh,expected_route=cache[key];assert route==expected_route,'Actual sigma spectator route'
            stream.update(json.dumps([call['stage'],call['replica'],helper,family,sh],separators=(',',':')).encode()+b'\n')
    assert sigmas==read(hosted/'ACTUAL-SIGMAS.json.gz'),'Actual sigma dictionary content'
    assert len(sigmas)==9628
    assert stream.hexdigest()==summary['sigma_stream_sha256']==controller['actual_sigma_stream_sha256'],'Actual role sigma stream'
    idle=read(hosted/'IDLE-REMAINDER-FRAMES.json.gz');idle_receipt=read(g/'audit/IDLE-REMAINDER-FRAMES.json')
    assert content_sha(hosted/'IDLE-REMAINDER-FRAMES.json.gz')==idle_receipt['uncompressed_frames_sha256']
    expected_idle=[]
    for row in template['idle_children']:
        axes=list(map(int,phases['recipes'][row['port']]['idle_children'][row['child']]['orthogonal_axes']))[row['pending_offset']:]
        assert len(axes)==row['rank']
        expected_idle.append(dict(row,orthogonal_axes=axes))
    assert idle==expected_idle and idle_receipt['children']==len(idle)
    assert idle_receipt['template_sha256']==template_hash
    assert idle_receipt['source_data_phase_sha256']==sha(base/'work/complex-nine-native/DATA-PHASES.json')
    return dict(template=template_hash,sigma_stream=stream.hexdigest(),sigmas=len(sigmas),source_artifacts=summary['source_artifacts'])

def check_ancestry(work,baseline):
    coverage=load(T21/'vendor/pr858/baseline_coverage.py','t37_bound_ancestry_coverage')
    assert read(work/'ANCESTRY-COVERAGE.json')==coverage.check(baseline/'ancestor'),'Current ancestor coverage'
    binding=load(ROOT/'scripts/verify_frontier799_bindings.py','t37_bound_frontier799')
    expected=binding.check(baseline/'ancestor',baseline/'native',baseline/'global',baseline/'INDEPENDENT-LOCAL.json',baseline/'INDEPENDENT-PRICE.json')
    assert read(work/'BASELINE-BINDING.json')==expected,'Current complete ancestor binding'
    assert Q(expected['kappa'])==Q('0.001661634653669567')

def check(work,baseline):
    pins=load(P/'package.py','t37_package_pins').validate()
    adapters=check_adaptations(work)
    check_construction(work)
    check_independent_inputs(work,baseline)
    payload=check_payload_artifacts(work)
    check_ancestry(work,baseline)
    g=work/'strict/global';native=work/'native10/local'
    assembly=read(work/'strict/ASSEMBLY.json');invoice=read(g/'audit/PREFIX-AND-INVOICE.json')
    owner=read(g/'audit/OWNERS-AND-PROFILE.json');controller=read(g/'audit/ASYNC-AUDIT.json')
    independent=read(work/'INDEPENDENT-OWNERS.json');plan=read(work/'lift/PLAN.json')
    spec=read(work/'runtime/data/SPEC.json');price=read(work/'ALL-T-BOUND.json')
    assert assembly['status']=='PASS_GAUGE44_NATIVE_EXACT_GLOBAL_ASSEMBLY'
    assert Q(assembly['kappa'])==Q('0.001662039077758742')==Q(price['all_T_grid_upper'])==Q(price['relaxed_outer_lower']['kappa'])
    assert Q(assembly['complex_lower'])==Q(price['root']['lower'])==Q('0.00166480605047151514435')
    assert Q(assembly['kappa'])>Q('0.001661960547713947'),'Strict gain over the selected PR942 record'
    assert Q(assembly['bit_lower'])==Q('0.001733427039589844234749')
    assert assembly['complex_profile']==independent['profile']==owner['paid_profile']==controller['complex_profile']==plan['profile']==spec['expected']['global_profile']
    for key,n in dict(live=33152,physical=33666,rank_mass=2408256,deficit=11840).items():
        assert owner[key]==independent[key]==n,(key,n)
    assert independent['roles']==owner['hosted_residuals']==controller['complex_hosted_residuals']==167832
    assert independent['calls']==controller['complete_invocations']==invoice['complete_invocation_sweeps']==333
    assert independent['actual_73_axis_charts']==owner['actual_73column_sigmas']==controller['actual_orthogonal_73column_maps']==9628
    assert independent['idle']=={'1':6,'48':11086}
    assert independent['prefix_bits']==invoice['global_prefix_bits']==779<invoice['charged_prefix_bits']==1024
    assert independent['physical_row_coefficient']==invoice['finite']['physical_row_coefficient']==17495<20161
    assert len(independent['controls_rejected'])==6 and len(independent['omitted_edits_rejected'])==8
    parent=read(work/'PARENT-CHECK.json')
    assert parent['status']=='PASS_INDEPENDENT_T37_PARTIAL_BANK_ENVELOPE' and len(parent['controls_rejected'])==8
    assert parent['parent_content_sha256']==identity(read(work/'lift/GLOBAL-TEMPLATE.json.gz'))==invoice['parent_template_sha256']
    assert parent['source_content_sha256']==identity(read(baseline/'global/global/base/split-centres/GLOBAL-TEMPLATE.json.gz'))
    assert plan['assignment_sha256']==plan['replica_lift']['owners_file_sha256']==sha(P/'OWNERS.json.gz')
    assert plan['assignment_content_sha256']==identity(read(P/'OWNERS.json.gz'))
    assert spec['data']['owners_sha256']==sha(P/'OWNERS.json.gz') and spec['data']['plan_sha256']==sha(work/'lift/PLAN.json')
    assert assembly['template_sha256']==owner['template_sha256']==invoice['template_sha256']==controller['complex_template_sha256']
    assert invoice['owner_audit_sha256']==sha(g/'audit/OWNERS-AND-PROFILE.json')
    assert invoice['controller_audit_sha256']==sha(g/'audit/ASYNC-AUDIT.json')
    assert len(invoice['strict_checks'])==9 and all(invoice['strict_checks'].values())
    assert len(assembly['outer'])==47 and all(Q(v)>0 for v in assembly['outer'].values())
    ac=read(work/'strict/ADMISSION-CONTROLS.json');bc=read(work/'strict/BIT-CONTROLS.json')
    assert len(ac['rejected_controls'])==69 and not ac['discovery_accepted_controls']
    assert len(bc['rejected_controls'])==12 and bc['derived_deficit']==10272
    assert controller['mutation_controls_run'] and len(controller['mutations_rejected'])==15
    payload_controls=read(work/'PAYLOAD-CONTROLS.json')
    assert payload_controls['status']=='PASS_T37_PAYLOAD_BOUNDARIES_AND_STRICT_ADMISSION_MUTATIONS'
    assert len(payload_controls['rejected_controls'])==11
    assert payload_controls['geometry_path']==str((work/'INDEPENDENT-OWNERS.json').resolve())
    assert payload_controls['geometry_sha256']==sha(work/'INDEPENDENT-OWNERS.json')
    payload_inputs=[work/'INDEPENDENT-OWNERS.json',g/'audit/OWNERS-AND-PROFILE.json',g/'audit/PREFIX-AND-INVOICE.json',work/'runtime/code/assemble.py',work/'runtime/data/SPEC.json']
    assert payload_controls['inputs']=={str(p.resolve()):sha(p) for p in payload_inputs}
    steps=read(work/'native/STEPS.json')
    assert [s['step']for s in steps]==['barch','barch-controls','layer-end-controls','native','ledgers','local-replay','wrappers','phases']
    assert all(s['exit_code']==0 for s in steps)
    assert len(read(work/'native/barch-controls/controls.json'))==38
    assert len(read(work/'native/controls/COLD-END-CONTROLS.json')['rejected'])==95
    steps=read(work/'native10/STEPS.json')
    assert [s['step']for s in steps]==['u10','u10-controls','layer-end-controls','native','ledgers','local-replay','wrappers','phases']
    assert all(s['exit_code']==0 for s in steps)
    controls=read(work/'native10/u10-controls/controls.json')
    assert len(controls)==14 and all(x['ok'] for x in controls.values())
    assert len(read(work/'native10/controls/COLD-END-CONTROLS.json')['rejected'])==95
    u10_profile={'1':2548,'2':338,'3':450,'4':154,'5':76,'8':8}
    assert read(work/'native10/u10/FULL-WORD.json.gz')['report']['local_profile']==u10_profile
    local_checks=read(work/'native10/local/LOCAL-CHECKS.json')
    assert all(local_checks[o]['paid_profile']==u10_profile for o in ('forward','backward'))
    assert read(P/'CLAIM.json')['local_profile']==u10_profile
    for name in ('CANONICAL-WORD.json.gz','LOCAL-PROGRAMS.json.gz','LOCAL-CHECKS.json','INDEPENDENT-LOCAL-REPLAY.json','CLIFFORD-RECIPES.json','CLIFFORD-REVIEW.json','RESIDUAL-ADAPTERS.json','WRAPPER-CHECKS.json'):
        assert read(g/'base/providers/gauge44'/name)==read(native/name),name
    stages=read(work/'STAGES.json')
    expected=['ancestry-coverage','baseline799-binding','u8-native','u10-native','prepare','frozen-construction','independent-owners','build-parent','check-parent','independent-price','discovery','strict','payload-controls']
    names=[s['name']for s in stages]
    if names and names[-1]=='final-binding':names=names[:-1]
    assert names in(expected,['baseline799-cold']+expected)
    assert all(s['exit_code']==0 and sha(work/(s['name']+'.log'))==s['log_sha256']for s in stages)
    for mode,expected in [('discovery',['bind','emit','audit','invoice','assembly','freeze']),('strict',['bind','emit','audit','invoice','assembly','admission-controls','bit-controls'])]:
        stages=read(work/mode/'STAGES.json')
        assert [s['name']for s in stages]==expected and all(s['exit_code']==0 for s in stages)
        assert all(sha(work/mode/(s['name']+'.log'))==s['log_sha256'] for s in stages),'Substage log bytes'
    paths=['ANCESTRY-COVERAGE.json','BASELINE-BINDING.json','ADAPTATIONS.json','CONSTRUCTION-CHECK.json','INDEPENDENT-OWNERS.json','PARENT-CHECK.json','ALL-T-BOUND.json','PAYLOAD-CONTROLS.json','lift/PLAN.json','runtime/data/SPEC.json','native/STEPS.json','native10/STEPS.json','native10/u10-controls/controls.json','native10/controls/COLD-END-CONTROLS.json','strict/STAGES.json','strict/ASSEMBLY.json','strict/ADMISSION-CONTROLS.json','strict/BIT-CONTROLS.json','strict/global/audit/OWNERS-AND-PROFILE.json','strict/global/audit/PREFIX-AND-INVOICE.json','strict/global/audit/ASYNC-AUDIT.json']
    paths+=['lift/GLOBAL-TEMPLATE.json.gz','strict/global/PLAN.json','strict/global/BINDING.json',
            'strict/global/hosted/HOSTED.json','strict/global/hosted/GLOBAL-TEMPLATE.json.gz',
            'strict/global/hosted/ACTUAL-SIGMAS.json.gz','strict/global/hosted/IDLE-REMAINDER-FRAMES.json.gz',
            'strict/global/audit/IDLE-REMAINDER-FRAMES.json','discovery/STAGES.json','independent_check_1024.py']
    paths+=['strict/global/base/'+relative for relative in payload['source_artifacts']]
    assert load(P/'package.py','t37_package_pins_final').validate()==pins,'Source package changed during final binding'
    return dict(status='PASS_COMPLETE_U10_T37_RESULT_BINDINGS',pins=pins,kappa=assembly['kappa'],
                actual_payload=payload,authorized_adapters=adapters,artifacts={p:sha(work/p)for p in paths})

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--work',required=True,type=Path);ap.add_argument('--baseline',required=True,type=Path);a=ap.parse_args()
    result=check(a.work.resolve(),a.baseline.resolve())
    (a.work/'FINAL-BINDING.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['status'])
