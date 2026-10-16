#!/usr/bin/env python3
"""Source-bound exact one-frame verification; no native or outer admission inferred.
Marius-Paul Dumitrean with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import copy
import gzip
import hashlib
import importlib
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent/'concentrated-prelife-composition'
OLD = ['add',393,515,1,1,[259,132,66,36,16,9]]
NEW = ['add',393,515,1,1,[259,148,66,36,9]]

def need(ok, message):
    if not ok:
        raise ValueError(message)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)

def authenticate():
    pins = read(HERE/'SOURCE-HEADS.json')
    need(sha(PARENT/'ARTIFACTS.json')==pins['published2733_artifacts_sha256'],
         'Exact published PR2733 artifact manifest')
    for name,digest in read(PARENT/'ARTIFACTS.json').items():
        need(sha(PARENT/name)==digest, 'Published source: '+name)
    for row in read(PARENT/'SOURCES.json')['files']:
        if row['usage']=='input':
            need(sha(HERE.parents[1]/row['path'])==row['sha256'], 'External source: '+row['path'])
    manifest=read(HERE/'expected/MANIFEST.json')
    actual={p.relative_to(HERE/'expected').as_posix() for p in (HERE/'expected').rglob('*')
            if p.is_file() and p.name!='MANIFEST.json'}
    need(actual==set(manifest), 'Complete candidate input set')
    for name,digest in manifest.items():
        need(sha(HERE/'expected'/name)==digest,'Candidate input: '+name)
    sys.path.insert(0,str(PARENT))
    algebra=importlib.import_module('composition_algebra')
    need(Path(algebra.__file__).resolve()==(PARENT/'composition_algebra.py').resolve(),
         'Authenticated independent algebra module')
    return algebra

def check_provider(A, tag):
    before=read(PARENT/f'expected/words/{tag}.json.gz')
    after=read(HERE/f'expected/words/{tag}.json.gz')
    need(set(before)==set(after),'Complete word keys')
    changed=copy.deepcopy(before)
    need(changed['B'][1149]==OLD,'Exact original B1149')
    changed['B'][1149]=copy.deepcopy(NEW)
    changed['report']['local_profile']['1']-=2
    changed['report']['local_profile']['2']+=1
    need(changed==after,'Exactly one B frame and its paid report change')
    need(A.S(NEW[-1])<A.S(OLD[-1]),'Strict frame containment')
    old,starts,ends=A.check_frames(before)
    report,newstarts,newends=A.check_frames(after)
    need(starts==newstarts and ends==newends and old['inventory']==report['inventory'],
         'All entrances, ends and helper widths unchanged')
    delta={r:report['profile'].get(r,0)-old['profile'].get(r,0)
           for r in set(old['profile'])|set(report['profile'])}
    need({r:n for r,n in delta.items() if n}=={1:-2,2:1},'Exact H2-2H1 local invoice')
    cleanup=A.check_cleanup(after)
    operators=A.algebra(after)
    need(operators=={'forward':'PASS','dual':'PASS'},'Every dirty input in both orientations')
    controls=[]
    for label in ['zero_frame','coefficient_sign']:
        mutant=copy.deepcopy(after)
        if label=='zero_frame':mutant['B'][1149][-1]=[]
        else:mutant['B'][1149][3]*=-1
        try:
            (A.check_frames if label=='zero_frame' else A.algebra)(mutant)
        except (AssertionError,ValueError) as exc:
            controls.append({'name':label,'rejected':True,'reason':str(exc)[:240]})
        else:
            raise ValueError('Mutation accepted: '+label)
    return {'profile':report['profile'],'width_inventory':report['inventory'],
            'live_inputs':704-len(after['removed']),'helpers':480-len(after['removed']),
            'private_buffers':len(after['helper_final']),'cleanup_events':cleanup,
            'operators':operators,'mutations':controls,
            'word_sha256':sha(HERE/f'expected/words/{tag}.json.gz')}

def main():
    need(__debug__,'Assertions required; run without optimized Python')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path)
    args=parser.parse_args()
    if args.out is not None:need(not args.out.exists(),'Refuse output overwrite')
    started=time.process_time()
    A=authenticate()
    reports={tag:check_provider(A,tag) for tag in ['base','extra']}
    for tag in reports:
        need((reports[tag]['live_inputs'],reports[tag]['helpers'],reports[tag]['private_buffers'])
             ==(639,415,72),'Actual unchanged inventory')
    for name in ['FILL.json.gz','ORDER.json']:
        need(sha(HERE/'expected'/name)==sha(PARENT/'expected'/name),'Unchanged owner data '+name)
    oldproviders=read(PARENT/'expected/PROVIDERS.json')
    providers=read(HERE/'expected/PROVIDERS.json')
    for name in providers:
        expected=copy.deepcopy(oldproviders[name])
        expected['actual_paid_profile']={str(r):n for r,n in reports['base']['profile'].items()}
        need(providers[name]==expected,'Only provider paid profile changes')
    old={int(r):n for r,n in read(PARENT/'expected/PROFILE.json').items()}
    expected=old.copy();expected[1]-=1332;expected[2]+=666
    profile={int(r):n for r,n in read(HERE/'expected/PROFILE.json').items()}
    need(profile==expected,'Whole 666-call invoice including unchanged remaining children')
    need(sum(r*n for r,n in profile.items())==4816512,'Unchanged global rank mass')
    result={'status':'PASS_SOURCE_BOUND_ONE_FRAME_FULL_OPERATORS_INVOICE_AND_CONTROLS',
            'providers':reports,'global_profile':profile,'stock':66801,
            'native_normalization':'M(b)=sum H_r*(r/73)^(1-b)/66304',
            'native_difference':'666*73^(b-1)/66304*(2^(1-b)-2)<0 for 0<b<1',
            'moment_scope':'Exact profile and native strict concavity comparison; numerical endpoint, conservative surcharge, emitted native phases and full supplier/outer admission are separate.',
            'all_size_scope':'Inherited machine/common-label, physical hosting, precision, analytic, bit and outer assumptions unchanged; no unconditional theorem or global optimum.',
            'parent_artifacts_sha256':sha(PARENT/'ARTIFACTS.json'),
            'candidate_manifest_sha256':sha(HERE/'expected/MANIFEST.json'),
            'checker_sha256':sha(Path(__file__)),'algebra_sha256':sha(PARENT/'composition_algebra.py'),
            'cpu_seconds':time.process_time()-started}
    authenticate()
    if args.out is not None:
        with args.out.open('x') as stream:json.dump(result,stream,indent=2);stream.write('\n')
    print(result['status'])

if __name__=='__main__':main()
