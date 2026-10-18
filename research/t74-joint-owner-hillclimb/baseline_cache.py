"""Complete source-bound cache coverage for an already executed upstream run.

JSON payloads retain every field. Gzip JSON is bound after decompression, so
container headers and JSON formatting do not affect a cached proof payload.
All other files, including source and transcripts, retain exact byte bindings.
"""
import gzip
import hashlib
import json
from pathlib import Path

if not __debug__:
    raise RuntimeError('Assertions must be enabled for cache evidence validation')

HEAD='614c74a63b0f6d4a24c7740d7ddb90d37861b3c7'
MANIFEST='557d8d6cfe0768c427e564beed37fbdfe3f65d10367f4c3a3dc36359c89cc62b'
SCHEMA='t74-complete-baseline-cache/2'
ROOTS=('parent','strict','native-new-base','native-new-extra')
TOP=('STAGES.json','LEMMAG-LABELS.json','GEOMETRY-CONTROLS.json')
CHAINS={'base':'native-new-base','extra':'native-new-extra',
        'retained-base':'parent/native-base','retained-extra':'parent/native-extra'}
STEPS=['native','ledgers','local-replay','wrappers','phases']


def read(path):
    b=path.read_bytes()
    return json.loads(gzip.decompress(b) if path.name.endswith('.json.gz') else b)


def binding(path):
    b=path.read_bytes()
    if path.name.endswith('.json.gz'):
        b=json.dumps(json.loads(gzip.decompress(b)),sort_keys=True,
                     separators=(',',':'),ensure_ascii=True).encode()
        kind='canonical-json-gzip'
    elif path.suffix=='.json':
        b=json.dumps(json.loads(b),sort_keys=True,separators=(',',':'),
                     ensure_ascii=True).encode()
        kind='canonical-json'
    else:
        kind='exact-bytes'
    return {'kind':kind,'sha256':hashlib.sha256(b).hexdigest()}


def covered_files(baseline):
    out={}
    for root in ROOTS:
        assert (baseline/root).is_dir(),('Missing baseline coverage root',root)
    for p in baseline.rglob('*'):
        if not p.is_file():continue
        rel=p.relative_to(baseline)
        # The sealing receipt cannot contain its own hash. Delta runtimes are
        # new workspaces and never supply baseline inputs. Bytecode is not an
        # input to the -B replay. Every other file, including logs, is bound.
        if rel.as_posix()=='PORTABLE-RESULT.json':continue
        if '__pycache__' in rel.parts:continue
        if len(rel.parts)>2 and rel.parts[:2]==('parent','layout') and rel.parts[2].startswith('delta-'):continue
        out[rel.as_posix()]=p
    for rel in TOP:
        p=baseline/rel;assert p.is_file(),('Missing baseline receipt',rel)
        out[rel]=p
    return out


def seal_completed_baseline(baseline,package,receipt):
    """Called only after the full cold runner has completed every required stage."""
    assert receipt['status']=='PASS_PORTABLE_T74_EXACT_FILL_COMPLETE_FINITE_ADMISSION'
    assert receipt['manifest_sha256']==hashlib.sha256((package/'MANIFEST.json').read_bytes()).hexdigest()==MANIFEST
    chains={}
    for key,relative in CHAINS.items():
        directory=baseline/relative;steps=read(directory/'STEPS.json')
        assert [x['step']for x in steps]==STEPS and all(x['exit_code']==0 for x in steps)
        kind=key.split('-')[-1]
        if key.startswith('retained-'):
            word=package/'vendor/pr1297'/('gauge44-word.json.gz'if kind=='base'else'extra-word.json.gz')
        else:
            word=package/('new/borrow/words/BORROW-WORD-43'+kind+'.json.gz')
        assert read(directory/'local/FULL-WORD.json.gz')==read(word)
        chains[key]={'directory':relative,'steps':steps,
                     'steps_binding':binding(directory/'STEPS.json'),
                     'word_binding':binding(word)}
    result=dict(receipt)
    result['cache_schema']=SCHEMA
    result['head']=HEAD
    result['cache_coverage']={'roots':['.'],'required_roots':list(ROOTS),'required_top':list(TOP),
        'ignored':['PORTABLE-RESULT.json self receipt','__pycache__ directories',
                   'parent/layout/delta-* derivative workspaces'],
        'json_policy':'Every JSON field retained; only object order, whitespace and gzip headers normalized'}
    result['bindings']={rel:binding(p) for rel,p in covered_files(baseline).items()}
    result['native_chains']=chains
    return result


def validate_baseline(baseline,package,receipt):
    assert receipt['cache_schema']==SCHEMA,'A complete cold-run cache receipt is required'
    assert receipt['head']==HEAD and receipt['manifest_sha256']==MANIFEST
    files=covered_files(baseline)
    assert set(files)==set(receipt['bindings']),'Missing or unexpected baseline proof artifact'
    for relative,p in files.items():
        assert binding(p)==receipt['bindings'][relative],('Baseline proof artifact changed',relative)
    assert set(receipt['native_chains'])==set(CHAINS)
    for key,relative in CHAINS.items():
        chain=receipt['native_chains'][key];directory=baseline/relative
        assert chain['directory']==relative
        steps=read(directory/'STEPS.json')
        assert steps==chain['steps'] and binding(directory/'STEPS.json')==chain['steps_binding']
        assert [x['step']for x in steps]==STEPS and all(x['exit_code']==0 for x in steps)
        kind=key.split('-')[-1]
        word=(package/'vendor/pr1297'/('gauge44-word.json.gz'if kind=='base'else'extra-word.json.gz')
              if key.startswith('retained-') else
              package/('new/borrow/words/BORROW-WORD-43'+kind+'.json.gz'))
        assert binding(word)==chain['word_binding']
        assert read(directory/'local/FULL-WORD.json.gz')==read(word)
    return {'status':'PASS_ALL_BASELINE_CACHE_BINDINGS',
            'artifact_count':len(files),'native_chains':len(CHAINS)}
