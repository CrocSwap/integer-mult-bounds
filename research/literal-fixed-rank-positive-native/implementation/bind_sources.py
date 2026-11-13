"""Authenticate exact retained pins and emitted graph metadata."""
from pathlib import Path
from hashlib import sha1, sha256
import atexit
import json
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
_cache = tempfile.TemporaryDirectory(prefix='positive-bind-')
atexit.register(_cache.cleanup)
sys.dont_write_bytecode = True
sys.pycache_prefix = str(Path(_cache.name)/'required-absent')


def verify(repo=None):
    manifest=json.loads((HERE/'SOURCES.json').read_text())
    for pin in manifest['files']:
        raw=(HERE/pin['local']).read_bytes()
        if len(raw)!=pin['bytes'] or sha256(raw).hexdigest()!=pin['sha256']:
            raise ValueError('retained source drift: '+pin['local'])
    parent=json.loads((HERE/'reference/rank2/SOURCES.json').read_text())
    for pin in parent['files']:
        raw=(HERE/'reference/rank2'/pin['local']).read_bytes()
        if sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()!=pin['blob']:
            raise ValueError('original Git blob drift: '+pin['local'])
    if sha256((HERE/'reference/rank2/FREEZE.json').read_bytes()).hexdigest()!=manifest['parent_rank2_freeze_sha256']:
        raise ValueError('parent freeze drift')
    pin=manifest['prior_proof'];raw=(HERE/pin['local']).read_bytes()
    if sha256(raw).hexdigest()!=pin['sha256']:
        raise ValueError('prior proof drift')
    if repo is not None:
        original=subprocess.check_output(['git','show',pin['commit']+':'+pin['path']],cwd=repo)
        if original!=raw:
            raise ValueError('canonical prior proof mismatch')
    import adapter as A
    result=json.loads((HERE/'RESULT.json').read_text())
    for record in result['tables']:
        code,_,_=A.C.compile_join(record['rank'])
        if len(code)!=record['locations'] or sha256(repr(code).encode()).hexdigest()!=record['sha256']:
            raise ValueError('fixed table drift')
    graph,_=A.compile_home(3)
    serial=[graph.start,[[state,[[r.target,r.tests,r.writes,r.moves] for r in rows]]
                         for state,rows in graph.rules.items()]]
    raw=json.dumps(serial,separators=(',',':')).encode()
    return {'status':'PASS','retained_pins':len(manifest['files']),
            'original_git_blobs':len(parent['files']),
            'canonical_prior_proof_checked':repo is not None,
            'rank_three_HOME_states':len(graph.rules),
            'rank_three_HOME_json_bytes':len(raw),
            'rank_three_HOME_sha256':sha256(raw).hexdigest(),
            'core_tables':result['tables']}


if __name__=='__main__':
    repo=sys.argv[sys.argv.index('--source-repo')+1] if '--source-repo' in sys.argv else None
    result=verify(repo)
    if '--write' in sys.argv:
        (HERE/'SOURCE-BINDING.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,sort_keys=True))
