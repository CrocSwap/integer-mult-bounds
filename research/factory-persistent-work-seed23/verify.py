"""Source-bound complete cache/gauge census and independent checks.
Prepared for @woklerx with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
import search
import independent as oracle
BASE='2921874911956718fcaaaf9396fe8267b3cfa9f0'
INPUTS=(search.SRC,'research/complex-dyadic-lowering/lower.py',
        'research/complex-factory-scale-frontier27/EXPECTED.json')
need=oracle.require


def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)


def load(raw):
    def pairs(items):
        d={}
        for k,v in items:
            need(k not in d,'duplicate key');d[k]=v
        return d
    def bad(x):raise ValueError('nonfinite JSON')
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=bad)


def source_check(pins):
    need(set(pins)=={'base_commit','files'} and pins['base_commit']==BASE,'source manifest metadata')
    need(set(pins['files'])==set(INPUTS),'source inventory')
    for p in INPUTS:need(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==pins['files'][p],'source hash')


def old_lowerer():
    spec=importlib.util.spec_from_file_location('pinned_pr696',ROOT/INPUTS[1])
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    return m.lower


def lowered_reference(macros,lower):
    ops=[];names={'add':'plus','subtract':'minus','halve':'half','negate':'neg'}
    for op in macros:
        if op[0]=='add':
            _,d,s,c=op;old=['add',['L',d],['L',s],c.numerator,c.denominator]
        else:
            _,d,c=op;old=['scale',['L',d],c.numerator,c.denominator]
        for primitive in lower(old):
            ops.append([names.get(primitive[0],primitive[0])]+[
                8 if tuple(r)==('W',0) else r[1]for r in primitive[1:]])
    return ops


def run():
    pins=load((HERE/'SOURCES.json').read_bytes());source_check(pins)
    raw=load((ROOT/INPUTS[0]).read_bytes())['replacement']
    need(len(raw)==32 and sum(o[0]=='add'for o in raw)==26,'frozen topology')
    need(all(o[-1]==[390,74,44,30]for o in raw),'common frame')
    oracle.check_orientations(search.variants(raw))
    result=search.search(raw);literal=[];checked=0;lower=old_lowerer()
    for name,word in search.variants(raw).items():
        row=result[name]
        need(row['count']==39424,'complete magnitude domain')
        need(row['histograms']==oracle.census(word),'independent version-label histogram')
        adds,totals,uses,slots=search.normalize(word)
        for mode in ('per_add','clean','defer','cache'):
            for winner in row['best'][mode]['winners']:
                for sign_slot in range(8):
                    placement=winner.copy();placement[5]=sign_slot
                    macros=search.materialize(adds,totals,placement)
                    stream,reuses=search.compile_word(macros,mode)
                    need(len(stream)==row['best'][mode]['cost'],'sign quotient cost')
                    summary=oracle.check(stream,word)
                    reference=lowered_reference(macros,lower)
                    need(reference==search.compile_word(macros,'per_add')[0],'pinned PR696 emitter mismatch')
                    before=oracle.check(reference,word)
                    literal.append({'orientation':name,'mode':mode,'slots':placement,
                       'cost':len(stream),'prefix':summary,'reference_prefix':before,
                       'stream_sha256':hashlib.sha256(canonical(stream).encode()).hexdigest()})
                    checked+=1
    predecessor=load((ROOT/INPUTS[2]).read_bytes())
    # The credited forward 73 floor and full magnitude histogram are reproduced.
    need(predecessor['minimum_primitives']==73 and predecessor['magnitude_placements']==39424,'PR949 domain')
    need(canonical(load(canonical(result['forward']['histograms']['per_add'])))==canonical(predecessor['histogram_magnitude']),
         'PR949 magnitude histogram')
    controls=[]
    def reject(name,fn):
        try:fn()
        except (ValueError,KeyError):controls.append(name);return
        raise ValueError('negative control accepted: '+name)
    chosen=result['forward']['best']['cache']['stream']
    reject('dirty entry: omit first COPY',lambda:oracle.check(chosen[1:],raw))
    reject('omit final work CLEAR',lambda:oracle.check(chosen[:-1],raw))
    reject('work aliases source',lambda:search.compile_word([['add',0,8,search.F(2)]],'cache'))
    reject('work aliases target',lambda:search.compile_word([['add',8,0,search.F(2)]],'cache'))
    fixture=[['add',1,0,search.F(2)],['add',0,2,search.F(1)],['add',3,0,search.F(2)]]
    fixture_raw=[['add',1,0,2,1,[]],['add',0,2,1,1,[]],['add',3,0,2,1,[]]]
    good,_=search.compile_word(fixture,'cache');oracle.check(good,fixture_raw)
    # Delete the second coefficient reload after source0 was modified.
    indices=[i for i,op in enumerate(good)if op[0]=='copy']
    stale=good[:indices[1]]+good[indices[1]+2:]
    reject('stale cached source after ADD write',lambda:oracle.check(stale,fixture_raw))
    scale_fixture=[['add',1,0,search.F(2)],['scale',0,search.F(-2)],['add',2,0,search.F(1,2)]]
    scale_raw=[['add',1,0,2,1,[]],['scale',0,-2,1,[]],['add',2,0,1,2,[]]]
    scaled,_=search.compile_word(scale_fixture,'cache');oracle.check(scaled,scale_raw)
    bad=[op.copy()for op in scaled];bad[-2][0]='plus' if bad[-2][0]=='minus' else 'minus'
    reject('wrong cache sign after source SCALE',lambda:oracle.check(bad,scale_raw))
    missing=load(canonical(pins));del missing['files'][INPUTS[0]]
    reject('missing source pin',lambda:source_check(missing))
    reject('duplicate JSON',lambda:load('{"n":1,"n":2}'))
    reject('nonfinite JSON',lambda:load('{"n":NaN}'))
    reject('Boolean cost metadata',lambda:need(canonical({'n':1})==canonical({'n':True}),'typed receipt'))
    reject('omitted magnitude tuple',lambda:need(sum(list(result['forward']['histograms']['cache'].values())[1:])==39424,'coverage'))
    return {'format':'factory-persistent-work/1','base_commit':BASE,'seed':23,
        'status':'PASS_FACTORY_PERSISTENT_WORK','source_pins':pins,'orientations':result,
        'literal_winner_replays':checked,'literal_checks':literal,'controls_rejected':controls,
        'scope':'fixed26 ADD topology; six single SCALE placements; just-in-time single-current-source dyadic work cache; no speculative prep, arbitrary circuits, full supplier or new kappa'}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write-certificate',action='store_true');a=p.parse_args()
    result=run();path=HERE/'CERTIFICATE.json'
    if a.write_certificate:path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8')
    else:need(canonical(load(canonical(result)))==canonical(load(path.read_bytes())),'certificate mismatch')
    print('PASS_FACTORY_PERSISTENT_WORK placements=39424x4 minima='+','.join(str(v['best']['cache']['cost'])for v in result['orientations'].values())+
        ' controls='+str(len(result['controls_rejected']))+' no_new_kappa')
if __name__=='__main__':main()
