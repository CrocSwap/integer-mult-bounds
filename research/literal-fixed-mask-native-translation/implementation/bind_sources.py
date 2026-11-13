"""Source/graph authentication for the fixed-offset literal templates."""
from pathlib import Path
from hashlib import sha1,sha256
import atexit
import json
import sys
import tempfile

HERE=Path(__file__).resolve().parent
_cache=tempfile.TemporaryDirectory(prefix='affine-bind-')
atexit.register(_cache.cleanup)
sys.dont_write_bytecode=True
sys.pycache_prefix=str(Path(_cache.name)/'required-absent')


def verify():
    m=json.loads((HERE/'SOURCES.json').read_text());own_blobs=0
    for pin in m['files']:
        raw=(HERE/pin['local']).read_bytes()
        if len(raw)!=pin['bytes'] or sha256(raw).hexdigest()!=pin['sha256']:
            raise ValueError('retained pin drift: '+pin['local'])
        if 'blob' in pin:
            if sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()!=pin['blob']:
                raise ValueError('original Git blob drift: '+pin['local'])
            own_blobs+=1
    parent=json.loads((HERE/'reference/rank2/SOURCES.json').read_text())
    for pin in parent['files']:
        raw=(HERE/'reference/rank2'/pin['local']).read_bytes()
        if sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()!=pin['blob']:
            raise ValueError('parent original Git blob drift: '+pin['local'])
    if sha256((HERE/'reference/rank2/FREEZE.json').read_bytes()).hexdigest()!=m['parent_rank2_freeze_sha256']:
        raise ValueError('parent freeze drift')
    import adapter as A
    result=json.loads((HERE/'RESULT.json').read_text())
    for record in result['tables']:
        code,_,_=A.C.compile_translation(record['offset'])
        if len(code)!=record['locations'] or sha256(repr(code).encode()).hexdigest()!=record['sha256']:
            raise ValueError('fixed emitted template drift')
    graphs=[]
    for offset in (0,264,510,511):
        graph,_=A.compile_home(offset)
        serial=[graph.start,[[name,[[r.target,r.tests,r.writes,r.moves] for r in rows]]
                            for name,rows in graph.rules.items()]]
        raw=json.dumps(serial,separators=(',',':')).encode()
        graphs.append({'offset':offset,'states':len(graph.rules),'json_bytes':len(raw),
                       'sha256':sha256(raw).hexdigest()})
    return {'status':'PASS','retained_pins':len(m['files']),
            'original_git_blobs':own_blobs+len(parent['files']),
            'core_templates':result['tables'],'HOME_graphs':graphs}


if __name__=='__main__':
    result=verify()
    if '--write' in sys.argv:(HERE/'SOURCE-BINDING.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,sort_keys=True))
