"""Complete unchanged source replay plus the new common-idle/fresh caller.

The hook below observes the end of the original PR6702 Extension.run. It
returns that original value unchanged. Every original source check, control
and saved receipt still runs. The new caller, physical maps, full invoice,
precision/storage envelope and outer transfer are checked separately.
"""
from collections import Counter
from copy import deepcopy
from hashlib import sha256,sha1
from pathlib import Path
import importlib.util
import json
import sys
import tempfile
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
STATUS='PASS_CONDITIONAL_KAPPA_00330420_COMMON_IDLE_RETIREMENT'

def need(ok,message):
    if not ok:raise ValueError(message)
def read(path):return json.loads(Path(path).read_bytes())
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m;spec.loader.exec_module(m);return m
def encode(x):
    from fractions import Fraction
    if isinstance(x,Fraction):return str(x)
    if isinstance(x,dict):return {str(k):encode(v)for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [encode(v)for v in x]
    return x
def reject(action):
    try:action()
    except ValueError as e:return str(e)
    raise ValueError('Invalid control accepted')

def authenticate():
    pins=read(HERE/'SOURCE6702.json');actual=[]
    for pin in pins['files']:
        p=Path(pin['path']);need(not p.is_absolute()and'..'not in p.parts,'Local source path')
        raw=(HERE/p).read_bytes()
        need(sha256(raw).hexdigest()==pin['sha256']and
             sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==pin['git_blob'],
             'Exact PR6702 source bytes: '+str(p))
        actual.append(str(p))
    need(len(actual)==17 and set(actual)=={'source6702/'+p.name for p in(HERE/'source6702').iterdir()if p.is_file()},
         'Complete immutable top-level predecessor inventory')
    return pins

def candidate(native_word,local,native,L,source):
    # Load all new modules under private names; coefficient and independent-row
    # helpers retain their source names only after predecessor execution ends.
    load(HERE/'algebra.py','algebra');load(HERE/'rows.py','rows')
    C=load(HERE/'caller.py','new_root8_caller');R=load(HERE/'retirement.py','new_root8_retirement')
    D=load(HERE/'dual.py','new_root8_dual');S=load(HERE/'scalars.py','scalars')
    roots=load(HERE/'root_check.py','new_root8_root_check').verify(read(HERE/'ROOT.json'))
    base=C.construct();need(base==read(HERE/'CONTROLLER-UNRETIRED.json'),'Exact unretired constructor')
    C.replay(base);pair=D.verify(base,R.G,R.J)
    word,witness=R.construct(base)
    need(word==read(HERE/'CONTROLLER.json')and witness==read(HERE/'WITNESS.json'),'Exact changed caller and handoff')
    forward=C.replay(word);reverse=sys.modules['rows'].transpose(word);scalar=S.verify(word)
    controls=C.controls(word)
    for label,index in [('input_basis',0),('handoff',witness['handoff_after']),('return',len(word['events'])-1)]:
        bad=deepcopy(word);del bad['events'][index]
        controls['missing_'+label]=reject(lambda bad=bad:C.replay(bad))
    bad=deepcopy(word);bad['diagonal'][-1][0]=-1
    controls['unearned_fresh_central_target']=reject(lambda:sys.modules['rows'].transpose(bad))
    bad=deepcopy(word)
    fused=next(e for e in bad['events']if e[0]=='IDLE'and e[1:3]==[2,3])
    fused[-1]=fused[-1][:-1]+[fused[-1][0]]
    controls['repeated_fused_axis']=reject(lambda:C.replay(bad))
    def jobs(w):
        return [(e[0],e[1]if e[0]=='LOCAL'else e[3]if e[0]=='QUERY'else tuple(e[3]if e[0]=='IDLE'else e[2]))
                for e in w['events']if e[0]in('LOCAL','QUERY','IDLE','IDLE_ONE')]
    need(jobs(base)==jobs(word),'Fresh-input retirement preserves every paid job')
    slots={'ADD':(1,2),'SWAP':(1,2),'SCALE':(1,),'LAMBDA':(1,),'Q_POWER':(1,),
           'QUERY':(1,2),'LOCAL':(2,3),'IDLE':(1,2),'IDLE_ONE':(1,)}
    need(all(e[j]!=34 for e in word['events'][:witness['handoff_after']+1]for j in slots[e[0]]),
         'New independent field is absent before the handoff')
    physical=load(source/'physical.py','new_root8_physical').physical(word,native_word,L)
    need((physical['ports'],physical['full_calls'],physical['physical_contacts'],physical['ordinary_normalizations'])==
         (104,18,7488,110),'Fresh full physical contact inventory')
    price=load(HERE/'pricing.py','new_root8_price')
    bound=price.run(local,native,word,physical,L)
    previous=read(HERE/'source6702/RESULT.json')['candidate']['complete_cost']
    changes=load(HERE/'changes.py','new_root8_changes').verify(bound,previous)
    bad=deepcopy(local);bad['paid'][1]-=1
    controls['unpaid_native_job']=reject(lambda:price.assemble(bad,native,word,physical))
    bad=deepcopy(physical);bad['main_targets'][1]+=104
    controls['extra_productive_credit']=reject(lambda:price.assemble(local,native,word,bad))
    print('PASS changed 35-input caller, both coefficient engines, fresh dual pairs, all 7488 physical contacts, complete price and outer transfer',flush=True)
    return encode({'root':roots,'caller':forward,'reverse':reverse,'dual_pair':pair,'physical':physical,
                   'scalar_envelope':scalar,'complete_cost':bound,'changes':changes,'controls':controls,
                   'native_unchanged':{'public_inputs':local['public_inputs'],'owned_fields':local['owned_fields'],
                     'owned_lifetimes':local['owned_lifetimes'],'peak_owned_fields':local['peak_owned_fields'],
                     'all_columns':800,'native_program_events':len(native_word['program'])}})

def run():
    pins=authenticate();captured={}
    with tempfile.TemporaryDirectory(prefix='root8-replay-')as td:
        old_cache=sys.pycache_prefix;sys.pycache_prefix=str(Path(td)/'bytecode')
        try:
            source=load(HERE/'source6702/verify.py','root8_unchanged_6702_verifier')
            original=source.Extension.run
            def observed(self,native_word,old_caller,local,native,L):
                result=original(self,native_word,old_caller,local,native,L)
                need(not captured,'Single final predecessor observation')
                captured.update(candidate(native_word,local,native,L,self.source))
                return result
            source.Extension.run=observed
            retained=source.run(write=False)
            need(retained==read(HERE/'source6702/RESULT.json'),'Exact complete PR6702 receipt remains unchanged')
            need(captured,'The full source reached its declared native/caller boundary')
            return {'status':STATUS,'kappa':'16521/5000000','kappa_decimal':'0.00330420',
                    'source_head':pins['source_head'],'source_pr':6702,
                    'retained_source_result_sha256':sha256((HERE/'source6702/RESULT.json').read_bytes()).hexdigest(),
                    'candidate':captured,'assumptions':retained['assumptions'],'selected_frontier_changed':False,
                    'scope':'Conditional changed complete caller and full replay. Independent scientific admission, full quantified framework premises and a materialized multiplier remain outside this receipt.'}
        finally:sys.pycache_prefix=old_cache

if __name__=='__main__':
    need(sys.argv[1:]in([],['--write-result']),'Only explicit --write-result is supported')
    r=run()
    if sys.argv[1:]: (HERE/'RESULT.json').write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
    else:need(r==read(HERE/'RESULT.json'),'Exact new complete result')
    print(STATUS,flush=True)
