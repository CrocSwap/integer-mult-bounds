"""Authenticated finite source capsule; no runtime payload callbacks."""
import gzip, hashlib, json, sys, types
from pathlib import Path
from fractions import Fraction
ROOT=Path(__file__).resolve().parent
def need(ok,message):
    if not ok: raise ValueError(message)
def authenticate():
    rows=json.loads((ROOT/'DEPENDENCIES.json').read_bytes())['files']
    need(len(rows)==6,'six frozen dependencies')
    for r in rows:
        p=ROOT/r['local_path'];need(p.resolve().is_relative_to(ROOT),'local dependency')
        v=p.read_bytes();need(len(v)==r['bytes'],'source length')
        need(hashlib.sha256(v).hexdigest()==r['sha256'],'source SHA-256')
        need(hashlib.sha1(b'blob '+str(len(v)).encode()+b'\0'+v).hexdigest()==r['git_blob'],'source Git blob')
    return len(rows)
def vendor(name,path):
    authenticate();p=ROOT/path;m=types.ModuleType(name);m.__file__=str(p);sys.modules[name]=m
    exec(compile(p.read_bytes(),str(p),'exec'),m.__dict__);return m
def word():
    authenticate();w=json.loads(gzip.decompress((ROOT/'data/word.json.gz').read_bytes()))
    need(w['public']==1461 and len(w['program'])==71144,'exact source word');return w
def census():
    rows=[(i,tuple(e),Fraction(e[3])) for i,e in enumerate(word()['program']) if e[0] in ('ADD','COPY')]
    need(len(rows)==61053 and len({q for _,_,q in rows})==4462,'current ADD/COPY coefficient census')
    need([raw for _,raw,_ in rows if raw[0]=='COPY']==[('COPY',1485,770,'1',115)],'sole source COPY coefficient; no COPY implementation claim')
    return rows
def bind_witnesses():
    from tables import compile_compact
    rows={i:(raw,q) for i,raw,q in census()};registry={};receipts=[]
    for i in (252,1103,2798):
        raw,q=rows[i];table,receipt=compile_compact(q)
        registry[('local',i,raw)]=table;receipts.append(dict(pc=i,raw=list(raw),**receipt))
    return registry,receipts
