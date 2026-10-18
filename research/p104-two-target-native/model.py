"""Source-bound event assembly and exact binary frame coordinates (no compiler)."""
from pathlib import Path
import gzip, hashlib, importlib.util, json, sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
BASE=ROOT/'research/p104-native-channel'

def need(ok,why):
    if not ok: raise ValueError(why)

def read_json(path):
    def unique(pairs):
        out={}
        for key,value in pairs:
            need(key not in out,'duplicate JSON key '+key);out[key]=value
        return out
    return json.loads(path.read_text(encoding='utf8'),object_pairs_hook=unique)

def check_sources():
    for p in read_json(HERE/'SOURCES.json')['files']:
        if p['usage']=='input':
            need(hashlib.sha256((ROOT/p['path']).read_bytes()).hexdigest()==p['sha256'],'source bytes '+p['path'])
    for p in read_json(HERE/'EXTERNAL-SOURCES.json'):
        raw=(HERE/p['local']).read_bytes()
        need(hashlib.sha256(raw).hexdigest()==p['sha256'],'external bytes '+p['local'])
        need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==p['git_blob'],'external blob '+p['local'])

def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod)
    return mod

def span(rows):
    values={0}
    for x in rows:
        need(type(x) is int and 0<x<512,'binary label range')
        values|={v^x for v in tuple(values)}
    return frozenset(values)

def canon(rows):
    piv={}
    for x in rows:
        while x:
            bit=x.bit_length()-1
            if bit in piv:x^=piv[bit]
            else:piv[bit]=x;break
    for bit in sorted(piv):
        for high in piv:
            if high>bit and (piv[high]>>bit)&1:piv[high]^=piv[bit]
    return tuple(piv[k] for k in sorted(piv,reverse=True))

def assemble():
    original=read_json(BASE/'inputs/LOWRANK-WITNESS.json')
    correction=read_json(HERE/'inputs/PR2445-CIRCUIT.json')
    need(correction['source_witness_sha256']==hashlib.sha256((BASE/'inputs/LOWRANK-WITNESS.json').read_bytes()).hexdigest(),'word binding')
    initial={**original['initial_frames'],**correction['initial_frames']}
    final={**original['final_frames'],**correction['final_frames']}
    need(not(set(original['initial_frames'])&set(correction['initial_frames'])),'disjoint helper names')
    bycut={}
    for insertion in correction['insertions']:
        cut=insertion['completed_cut'];need(type(cut)is int and 0<=cut<=len(original['program']),'insertion cut')
        bycut.setdefault(cut,[]).extend(insertion['events'])
    events=[];added=[]
    for cut in range(len(original['program'])+1):
        for event in bycut.get(cut,[]):added.append(len(events));events.append(event)
        if cut<len(original['program']):events.append(original['program'][cut])
    need(len(initial)==358 and len(events)==4734 and len(added)==676,'exact source inventory')
    return initial,final,events,frozenset(added)

def native_source():
    return json.loads(gzip.decompress((BASE/'NATIVE-RECIPES.json.gz').read_bytes()))

def physical_map(iso,N):
    dual=tuple(iso['compressed_dual_gram'])
    need(tuple(N.inverse(tuple(iso['compressed_gram'])))==dual,'dual Gram inverse')
    mv=lambda rows,x:sum(((row&x).bit_count()&1)<<i for i,row in enumerate(rows))
    dot=lambda a,b:(a&mv(dual,b)).bit_count()&1
    orth=iso['orthonormal_basis_compressed']
    need(len(orth)==9 and all(dot(a,b)==int(i==j) for i,a in enumerate(orth) for j,b in enumerate(orth)),'physical isometry')
    convert=lambda x:sum(dot(x,v)<<j for j,v in enumerate(orth))
    need(len({convert(x) for x in range(512)})==512,'isometry bijective')
    return convert
