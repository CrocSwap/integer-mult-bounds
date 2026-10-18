import json,gzip
def _dec(v): return frozenset(('c',x[1]) if isinstance(x,list) else x for x in v)
def _enc(v): return sorted((['c',x[1]] if isinstance(x,tuple) else x) for x in v) if False else [(['c',x[1]] if isinstance(x,tuple) else x) for x in sorted(v,key=repr)]
def _tup(m): return tuple(m)
def dump_pairs(t,path):
    M,sg,pv=t
    o={'M':[list(m) for m in M],'sg':[_enc(v) for v in sg],'pv':[[a,b,_enc(v)] for (a,b),v in sorted(pv.items())]}
    with gzip.GzipFile(path,'wb',mtime=0) as f: f.write(json.dumps(o,separators=(',',':')).encode())
def load_pairs(path):
    o=json.load(gzip.open(path))
    M=[tuple(m) for m in o['M']]
    return M,[_dec(v) for v in o['sg']],{(a,b):_dec(v) for a,b,v in o['pv']}
