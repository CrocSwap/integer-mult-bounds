"""Freeze the source DAG in dependency order, with no runtime issuance."""
import ast
import hashlib
import json
import re
from pathlib import Path

from build_source_assembly import NEW, OLD, ORIGINAL, encode, pin, put, relocate

def freeze():
    source=NEW/'implementation/source'
    common=pin(source/'run_guarded_v3.py')
    supervisor=source/'fresh_supervisor.py'
    text=supervisor.read_text()
    text=text.replace('/implementation/source/fresh_runner.py', '/implementation/source/run_guarded_v3.py')
    text=re.sub(r"(?m)^RUNNER_SHA = '[0-9a-f]{64}'$",'RUNNER_SHA = '+repr(common['sha256']),text)
    put(supervisor,text.encode())
    # Every selected owner leaf is frozen before a manifest can name it.
    for path in (NEW/'implementation').rglob('*.py'):
        if '/stages/' not in str(path):
            ast.parse(path.read_bytes(), filename=str(path))
            path.chmod(0o444)
    entry=pin(source/'candidate_entry.py')
    receiver=pin(source/'full_result_receiver.py')
    relay=pin(source/'bounded_relay.py')
    stages={}
    for mode,leaf in [('normal','joined-full-candidate-v1'),('optimized','joined-full-candidate-refusal-v1')]:
        base=NEW/'implementation/bindings/stages'/leaf
        jobs=json.loads((base/'JOBS.json').read_bytes())
        jobs[mode].pop('bootstrap',None)
        jobs[mode]['entry']='integration/candidate_entry.py'
        put(base/'JOBS.json',encode(jobs))
        put(base/'integration/candidate_entry.py',(source/'candidate_entry.py').read_bytes())
        declared=json.loads((base/'STAGE.json').read_bytes())
        declared['files']['JOBS.json']={'sha256':pin(base/'JOBS.json')['sha256'],'mode':0o444}
        declared['files']['integration/candidate_entry.py']={'sha256':entry['sha256'],'mode':0o444}
        declared.update(runner_sha256=common['sha256'],full_receiver_sha256=receiver['sha256'],
            relay_sha256=relay['sha256'],native_entry_source_sha256=pin(NEW/'implementation/native/science_view_entry.c')['sha256'],
            scope='Source-only connected waiting-entry successor; original scientific payload bytes preserved. Runtime and full caller admission unissued.')
        put(base/'STAGE.json',encode(declared))
        stages[mode]=pin(base/'STAGE.json')
    queue=NEW/'implementation/bindings/control/IndependentPrefixDATAComposedV1-QUEUE.json'
    q=json.loads(queue.read_bytes())
    for case in q['cases']:case['stage_sha256']=stages[case['job']]['sha256']
    put(queue,encode(q))
    commands=NEW/'implementation/bindings/profiles/commands.json'
    profile=json.loads(commands.read_bytes())
    for mode,leaf,suffix in [('normal','joined-full-candidate-v1','N'),('optimized','joined-full-candidate-refusal-v1','O')]:
        label='IndependentPrefixDATAComposedV1'+suffix
        wait=NEW/'runtime/completed-source/IndependentPrefixDATAComposedV1'/label/'supervision/WAIT.json'
        profile['root_runner_argv'][mode]=['/usr/bin/python3.12','-S','-s','-P','-B',common['path'],leaf,mode,label,
            '--waiting-config',str(wait),'--waiting-sha256','@ACTUAL_'+mode.upper()+'_WAITING_SHA256@']
    profile['required'].append('Candidate qualification occurs in the source-authenticated parent after actual stopped entry arrival. One immutable common runner pin and one-use release; primary wall/CPU endpoints unchanged.')
    profile['required']=list(dict.fromkeys(profile['required']))
    put(commands,encode(profile))
    effects=NEW/'implementation/bindings/profiles/effects.json'
    e=json.loads(effects.read_bytes())
    e['roles']['WaitingEntry']=['Known-close ARRIVED then SIGSTOP before inner birth; authenticate intent/release after one held-pidfd SIGCONT; own inherited capture aliases and pipe-only native launch.']
    e['required'].append('The loader permits exactly one authenticated _COMMON source-pair binding. RUNNER_PATH and RUNNER_SHA remain immutable frozen source selections. Runtime grants and native qualification are separate inputs.')
    e['required']=list(dict.fromkeys(e['required']))
    put(effects,encode(e))
    # Packet has only existing leaf pins; it does not contain itself/manifest.
    packet=NEW/'implementation/bindings/SELECTED-SOURCE-PACKET-v1.json'
    old_packet=json.loads((OLD/'implementation/bindings/SELECTED-SOURCE-PACKET-v1.json').read_bytes())
    files={}
    for path in old_packet['files']:
        new_path=Path(path.replace(str(OLD),str(NEW)))
        if new_path.name=='fresh_runner.py':new_path=source/'run_guarded_v3.py'
        row=pin(new_path);files[str(new_path)]={k:v for k,v in row.items() if k!='path'}
    for path in (source/'candidate_entry.py',source/'run_guarded_v3.py'):
        row=pin(path);files[str(path)]={k:v for k,v in row.items() if k!='path'}
    put(packet,encode({'schema':old_packet['schema'],'files':files}))
    manifest=dict(ORIGINAL)
    manifest['source_pins']={}
    for key,row in ORIGINAL['source_pins'].items():
        path=Path(row['path'])
        if path.is_relative_to(OLD):path=NEW/path.relative_to(OLD)
        if key=='runner':path=source/'run_guarded_v3.py'
        manifest['source_pins'][key]=pin(path)
    manifest['source_pins'].update(common_runner=common,waiting_entry=entry)
    manifest['profiles']={key:pin(NEW/'implementation/bindings/profiles'/(key+'.json')) for key in ORIGINAL['profiles']}
    # Historical control evidence is retained at its original exact identity.
    manifest['control_pins']=ORIGINAL['control_pins']
    manifest['argv_shapes']=relocate(ORIGINAL['argv_shapes'])
    manifest['source_only']=True;manifest['execution_permission']=False
    target=NEW/'implementation/bindings/SOURCE-MANIFEST-v2.json'
    put(target,encode(manifest))
    report={'schema':'connected-static-source-assembly-v1','manifest':pin(target),
        'source_role_count':len(manifest['source_pins']),'profiles':len(manifest['profiles']),
        'historical_control_pins':len(manifest['control_pins']),'stages':stages,
        'runtime_contracts_issued':False,'runtime_START_or_grant_created':False,
        'runtime_input_dependency':'The genuine original parent supplies reviewed original issued inputs, native/TCB/compiler/query subjects, grants and financial provenance to derive_fixed_role_data. No fabricated ROLE-CONTRACTS or currentness input is created.',
        'source_only':True,'execution_permission':False}
    put(NEW/'control/ASSEMBLY-v1.json',encode(report))
    print(json.dumps(report,indent=2))

if __name__=='__main__':
    freeze()
