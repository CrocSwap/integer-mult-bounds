"""Exact prefix-monomial boundary floors for the fixed CK/JP8 runs.
Apache-2.0; substantial OpenAI Codex assistance for @woklerx.
"""
import argparse,gzip,hashlib,importlib.util,json,sys
from collections import Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];sys.path.insert(0,str(HERE))
import finite,backward,joint
need=backward.need
BASE='2921874911956718fcaaaf9396fe8267b3cfa9f0'
PROVIDERS='research/community-k492-audit/pr626/replay/mixed-global/base/providers/'
INPUTS=['research/complex-dyadic-lowering/lower.py','research/complex-swap-runs-seed37/compiler.py',
 'research/ck-sign-normalization-seed22/compile.py','research/complex-swap-runs-seed37/independent_checker.py',
 'research/complex-swap-runs-seed37/EXPECTED.json','research/complex-swap-runs-seed37/PROOF.md']
INPUTS += [PROVIDERS+p+'/LOCAL-PROGRAMS.json.gz'for p in('ck','jp8')]

def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)

def loads(raw):
    def pairs(xs):
        out={}
        for k,v in xs:need(k not in out,'duplicate key');out[k]=v
        return out
    def bad(x):raise ValueError('nonfinite')
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=bad)

def read(p):
    raw=p.read_bytes();return loads(gzip.decompress(raw)if p.suffix=='.gz'else raw)

def same(a,b,msg):need(canonical(a)==canonical(b),msg)

def pins_check(pins):
    need(set(pins)=={'base_commit','files'}and pins['base_commit']==BASE,'base manifest')
    need(set(pins['files'])==set(INPUTS),'exact source inventory')
    for p in INPUTS:need(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==pins['files'][p],'source SHA256')

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def cost(blocks):
    zero=False;n=0
    for block in blocks:
        for op in block:
            if tuple(op[1])==joint.WORK:
                if op[0]=='clear':
                    if zero:continue
                    zero=True
                else:zero=False
            n+=1
    return 2*n

def run():
    pins=read(HERE/'SOURCES.json');pins_check(pins)
    lower=module('paid_lower',INPUTS[0]).lower;old=module('old_swap',INPUTS[1]);sign=module('old_sign',INPUTS[2]);check=module('old_independent',INPUTS[3])
    # PR919 permits a deferred sign. Adapt only the inherited prefix-set
    # membership test, keeping its independent dense endpoint replay intact.
    source=(ROOT/INPUTS[3]).read_text();anchor='require(tuple(row) in seen, "replacement prefix row absent from original trace")'
    need(source.count(anchor)==1,'signed prefix checker anchor')
    source=source.replace(anchor,'require(tuple(row) in seen or tuple(-v for v in row) in seen, "replacement prefix row absent up to sign")')
    signed_check={'__name__':'signed_prefix_checker'};exec(compile(source,INPUTS[3], 'exec',optimize=0),signed_check)
    prior=read(ROOT/INPUTS[4]);floors={}
    for name,perm in [('2',[2,1]),('2+3',[2,1,4,5,3])]:
        for clean in(False,True):
            primary=finite.solve(perm,clean);other=backward.solve(perm,clean)
            need(primary['minimum']==other['minimum'],'independent exact distance')
            backward.replay(perm,primary['witness'],clean)
            floors[name+('/clean'if clean else'/dirty')]={'forward':primary,'backward':other}
    programs={};boundaries=[]
    for provider in('ck','jp8'):
        for orientation,events in read(ROOT/(PROVIDERS+provider+'/LOCAL-PROGRAMS.json.gz')).items():
            key=provider+'/'+orientation;runs=old.scalar_runs(events)
            same([{'start':a,'end':b,'frame':f}for a,b,f in runs],check.scalar_runs(events),'independent complete run partition')
            direct=[[p for e in events[a:b]for p in lower(e[1])]for a,b,f in runs]
            previous=old.compile_program(events,lower)
            new=[joint.compile_block(events,a,b,lower)for a,b,f in runs]
            receipts={'clear_only':cost(direct),'sign_only':cost([sign.optimize_run(b)for b in direct]),
              'swap_only':cost([b['primitives']for b in previous]),
              'swap_then_sign':cost([sign.optimize_run(b['primitives'])for b in previous]),
              'joint':cost([b['primitives']for b in new])}
            need(receipts['swap_only']==prior['programs'][key]['receipts']['deferred_known_zero']['real_primitives'],'strongest retained comparator')
            need(receipts['joint']==receipts['swap_then_sign']==receipts['swap_only'],'pilot tie')
            histogram=Counter();boundary_bill=0;checked=0
            for block,candidate in zip(previous,new):
                if not block['swap_starts']:continue
                # Independently recover locations from dense-recognized swaps.
                loc={};seen=[];i=block['start']
                while i<block['end']:
                    recognized=check.recognize(events,i)if i+4<=block['end']else None
                    if recognized:
                        a,b,f=recognized;loc.setdefault(a,a);loc.setdefault(b,b);loc[a],loc[b]=loc[b],loc[a];seen.append(i);i+=4
                    else:i+=1
                same(seen,block['swap_starts'],'complete swap detection')
                same([[list(r),list(s)]for r,s in sorted(loc.items())],block['permutation'],'independent permutation')
                restore,cycles=old.materialize(loc);check.check_replacement({'permutation':tuple(loc.items())},restore)
                sizes=sorted(len(c)for c in cycles);name='+'.join(map(str,sizes));need(name in('2','2+3'),'frozen boundary type')
                minimum=floors[name+'/dirty']['forward']['minimum'];need(len(restore)==minimum,'attained boundary floor')
                signed_check['check_block'](events,block['start'],block['end'],candidate['primitives'])
                histogram[name]+=1;boundary_bill+=minimum;checked+=1
                boundaries.append({'program':key,'start':block['start'],'end':block['end'],'frame':block['frame'],
                    'cycles':[[list(r)for r in c]for c in cycles],'minimum':minimum})
            same(dict(histogram),{'2':28,'2+3':14},'complete boundary census')
            need(boundary_bill==224 and checked==42,'complete boundary bill')
            programs[key]={'runs':len(runs),'boundary_types':dict(histogram),'boundary_primitives_per_component':boundary_bill,
               'independent_changed_run_checks':checked,'complete_real_primitive_costs':receipts,
               'joint_rotations':sum(len(b['rotations'])for b in new),'signed_two_cycles_used':sum(b['optimized_two_cycles']for b in new),
               'old_paid_profile_unchanged':prior['programs'][key]['paid_profile_unchanged']}
    controls=[]
    def reject(name,fn):
        try:fn()
        except ValueError:controls.append(name);return
        raise ValueError('control accepted '+name)
    word=floors['2/dirty']['forward']['witness'];perm=[2,1]
    reject('missing cleanup',lambda:backward.replay(perm,word[:-1]))
    reject('missing saved input',lambda:backward.replay(perm,word[1:]))
    reject('arithmetic mixing leaves monomial class',lambda:backward.replay(perm,[['add',0,1]]+word))
    reject('nonunit scale leaves monomial class',lambda:backward.replay(perm,[['halve',0]]+word))
    reject('one-shorter minimum claim',lambda:need(floors['2+3/dirty']['backward']['minimum']<=7,'distance lower bound'))
    reject('unpaid two-cycle restore',lambda:backward.replay(perm,[]))
    reverse_word=floors['2+3/dirty']['forward']['witness']
    reject('reverse three-cycle direction',lambda:backward.replay([2,1,5,3,4],reverse_word))
    missing=loads(canonical(pins));del missing['files'][INPUTS[0]]
    reject('missing source pin',lambda:pins_check(missing))
    reject('duplicate JSON',lambda:loads('{"a":1,"a":2}'))
    reject('nonfinite JSON',lambda:loads('{"a":NaN}'))
    reject('Boolean minimum',lambda:same({'n':1},{'n':True},'typed number'))
    backward.replay(perm,[['negate',0],['negate',0]]+word)
    backward.replay(perm,[['clear',2],['halve',2],['double',2]]+word)
    return {'format':'complex-monomial-boundary-floor/1','status':'PASS_COMPLEX_MONOMIAL_FLOORS','base_commit':BASE,'seed':25,
      'source_pins':pins,'floors':floors,'programs':programs,'boundaries':boundaries,'controls_rejected':controls,
      'positive_controls':['paid paired signs','zero-work scales are no-ops'],
      'scope':'fixed moved coordinates plus one dirty/clean work; every prefix0 or signed incoming coordinate; boundary floor only, not unrestricted arithmetic or whole-run optimum'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write-certificate',action='store_true');a=p.parse_args();result=run()
    if a.write_certificate:(HERE/'CERTIFICATE.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf8')
    else:same(result,read(HERE/'CERTIFICATE.json'),'complete certificate mismatch')
    print('PASS_COMPLEX_MONOMIAL_FLOORS minima=4,8 programs=4 boundaries=168 controls='+str(len(result['controls_rejected']))+' no_new_kappa')
if __name__=='__main__':main()
