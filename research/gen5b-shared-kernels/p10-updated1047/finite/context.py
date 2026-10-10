"""Portable source and output routes for original finite checkers; upstream stays inert."""
from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import support
HERE=Path(__file__).resolve().parent
BASE=support.HERE
ADMISSION=support.HERE/'admission'
ADMISSION_OUTPUT=support.OUTPUT/'admission'
ARITHMETIC=support.OUTPUT/'arithmetic'
MATCHING=support.OUTPUT/'matching'
OUTPUT=support.out('finite','placeholder').parent
INPUTS=support.INPUTS
MANIFEST=support.HERE/'inputs.json'
WORD=MATCHING/'word_weighted890.json'
RATIONAL=support.HERE/'../p10/closure/chart_rational.py'
HEAD=support.HEAD
WORD_SHA=support.WORD_SHA
sha=support.sha
manifest=support.pins
raw_source=support.read_bytes
def load(p):return json.loads(Path(p).read_text())
def source(name):
    raw=raw_source(name)
    if name.endswith('.gz'):
        import gzip
        raw=gzip.decompress(raw)
    return json.loads(raw)if name.endswith(('.json','.json.gz'))else raw.decode()
def verify():
    support.require_assertions();support.verify_inputs();support.verify_dependencies();assert sha(WORD)==WORD_SHA
def mapping(word):
    alias={r:d for d,r in word['pairs']};roles=sorted(set(range(9120))-set(alias));ids={r:1920+i for i,r in enumerate(roles)}
    assert len(alias)==len(set(alias.values()))==890 and not(set(alias)&set(alias.values()))
    return roles,{r:ids[alias.get(r,r)]for r in range(9120)}
def inventory():
    old=source('bitword/selected/bit/word_p10.json.gz');word=load(WORD)
    oldroles,oldmap=mapping(old);roles,newmap=mapping(word);inverse={oldmap[r]:r for r in oldroles}
    frames={int(k):v for k,v in source('bitword/selected/bit/frames_p10.json.gz')['frames'].items()}
    sink=source('sink-selection.json')['sinks'];sunk={r['role']for r in sink};assert all(inverse[r['stream']]==r['role']for r in sink)
    roles=sorted(set(roles)-sunk);entrance={r:None for r in roles};ends={r:None for r in roles};origin={}
    for row in word['gauges']:
        if row['role']in entrance:entrance[row['role']]=frames[row['frame']];origin[row['role']]=dict(kind='gauge',frame=row['frame'])
    entries=source('kernel-selection.json')['families'];rebound=load(ADMISSION_OUTPUT/'rebound-kernel-entries.json')['entries'];assert len(entries)==len(rebound)==1047
    for i,(row,bound)in enumerate(zip(entries,rebound)):
        role=inverse[row['pivot']];assert entrance[role] is None
        assert bound['index']==i and bound['virtual_pivot']==role and bound['pivot']==newmap[role]
        assert bound['basis']==row['basis'] and bound['rank']==row['rank']
        assert bound['virtual_donors']==[inverse[d]for d in row['donors']] and bound['donors']==[newmap[inverse[d]]for d in row['donors']]
        entrance[role]=dict(dim=row['rank'],b=row['basis']);origin[role]=dict(kind='installed_kernel',index=i)
    for row in source('restore-selection.json')['entries']:
        role=inverse[row['helper']];assert entrance[role]['dim']==row['dims'][0] and ends[role]is None
        ends[role]=dict(dim=row['rank'],b=row['basis'])
    widths={r:(20 if ends[r]is None else ends[r]['dim'])-(0 if entrance[r]is None else entrance[r]['dim'])for r in roles}
    assert len(roles)==8223 and all(0<x<=20 for x in widths.values())
    return word,frames,roles,newmap,entrance,ends,widths,origin
