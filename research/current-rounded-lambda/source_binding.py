"""Immutable exact source capsule and local class bindings."""
import hashlib,json,sys,types,gzip
from pathlib import Path
ROOT=Path(__file__).resolve().parent
_loaded=False
def need(ok,msg):
    if not ok:raise ValueError(msg)
def authenticate():
    global _loaded
    rows=json.loads((ROOT/'DEPENDENCIES.json').read_bytes())['files']
    if not _loaded:
        for r in rows:
            p=ROOT/r['local_path'];need(p.resolve().is_relative_to(ROOT),'local capsule')
            v=p.read_bytes();need(len(v)==r['bytes'] and hashlib.sha256(v).hexdigest()==r['sha256'],'immutable source bytes')
            need(hashlib.sha1(b'blob '+str(len(v)).encode()+b'\0'+v).hexdigest()==r['git_blob'],'immutable source blob')
        _loaded=True
    return len(rows)
def vendor(name,path):
    authenticate();p=ROOT/path;m=types.ModuleType(name);m.__file__=str(p);sys.modules[name]=m
    exec(compile(p.read_bytes(),str(p),'exec'),m.__dict__);return m
def inputs():
    authenticate();return json.loads((ROOT/'data/caller.json').read_bytes()),json.loads(gzip.decompress((ROOT/'data/word.json.gz').read_bytes()))
def lambda_sites():
    c,w=inputs();need(len(c['events'])==3095 and len(w['ports'])==104,'exact source classes');out=[]
    for pc,e in enumerate(c['events']):
        if e[0] in ('A','B') and e[1]=='LAMBDA':
            need(type(e[3])is int and e[3] in (-1,1),'source lambda sign')
            for port in c['types'][e[0]]['ports']:
                q=w['ports'][port];need(0<q<512,'central nine-axis source direction')
                out.append(dict(site=pc,type=e[0],role=e[2],port=port,q=q,sign=e[3],raw=e))
    return out
