"""Full pinned-source replay of one paid fragment and two retirements.

Original caller/source authors retain the credits in the pinned predecessor.
The additional mechanism and audit were developed with OpenAI Codex for zxv.
No unconditional framework discharge or selected-frontier mutation is claimed.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import importlib.util,json,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'sources/pr6716'
STATUS='PASS_CONDITIONAL_KAPPA_00330500_PAID_FRAGMENT_RETIREMENT'

def need(ok,msg):
    if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_bytes())
def load(p,name):
    spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def encode(v):
    if isinstance(v,Q):return str(v)
    if isinstance(v,dict):return{str(k):encode(x)for k,x in v.items()}
    if isinstance(v,(list,tuple)):return[encode(x)for x in v]
    return v
def rejected(f):
    try:f()
    except (ValueError,AssertionError)as e:return str(e)
    raise ValueError('Invalid control accepted')
def authenticate():
    pins=read(SOURCE/'LOCAL-PINS.json')
    need(len(pins)==45,'Complete pinned PR6716 inventory')
    for pin in pins:
        p=Path(pin['path']);need(not p.is_absolute()and'..'not in p.parts,'Source relative path')
        b=(SOURCE/p).read_bytes();need(len(b)==pin['bytes']and sha256(b).hexdigest()==pin['sha256'],'Exact source '+str(p))
    return{'head':'a467457692bc9e11113d9b2e2e34ea8ffb553b58','files':len(pins),'manifest_sha256':sha256((SOURCE/'LOCAL-PINS.json').read_bytes()).hexdigest()}

def candidate(native_word,local,native,L,physical_source,prior):
    load(HERE/'algebra.py','algebra');load(HERE/'rows.py','rows');load(HERE/'scalars.py','scalars')
    C=load(HERE/'caller.py','fragment_caller_verified');R=load(HERE/'retirement.py','fragment_retirement_verified')
    root=load(HERE/'root_check.py','fragment_root_verified').verify(read(HERE/'ROOT.json'))
    base=C.construct();need(base==read(HERE/'CALLER-UNRETIRED.json'),'Exact paid fragmented caller')
    forward_base=C.replay(base)
    body,word,witness=R.construct(base)
    need(body==read(HERE/'CALLER-BODY-RETIRED.json')and word==read(HERE/'CONTROLLER.json')and witness==read(HERE/'RETIREMENT-WITNESSES.json'),'Literal retirement construction and census')
    body_forward=C.replay(body);forward=C.replay(word);reverse=sys.modules['rows'].transpose(word)
    scalar=sys.modules['scalars'].verify(word)
    slots=R.SLOTS
    for w,proof in[(body,witness[0]),(word,witness[1])]:
        need(all(e[j]!=proof['fresh']for e in w['events'][:proof['handoff_after']+1]for j in slots[e[0]]),'Additional arbitrary input is untouched until handoff')
    def jobs(w):
        return [(e[0],e[1]if e[0]=='LOCAL'else e[3]if e[0]=='QUERY'else tuple(e[3]if e[0]=='IDLE'else e[2]))for e in w['events']if e[0]in('LOCAL','QUERY','IDLE','IDLE_ONE')]
    need(jobs(base)==jobs(body)==jobs(word),'Retirements preserve every paid fragmented request')
    controls=C.controls(word)
    for label,index in [('fragmented_B_idle',word['events'].index(['IDLE_ONE',2,[5,6]])),('body_input_basis',3),('body_handoff',witness[0]['handoff_after']+3),('D_handoff',witness[1]['handoff_after']),('final_return',len(word['events'])-1)]:
        bad=deepcopy(word);bad['events'][index]=['SCALE',0,'1']
        controls[label]=rejected(lambda bad=bad:C.replay(bad))
    for role,label in[(6,'body_prefix_unearned_head'),(34,'body_suffix_wrong_body'),(35,'D_suffix_unearned_head')]:
        bad=deepcopy(word)
        if role==34:bad['diagonal'][role][8]=0
        else:bad['diagonal'][role][0]=-1
        controls[label]=rejected(lambda bad=bad:sys.modules['rows'].transpose(bad))
    physical=load(physical_source/'physical.py','fragment_physical').physical(word,native_word,L)
    need((physical['ports'],physical['full_calls'],physical['physical_contacts'],physical['ordinary_normalizations'])==(104,18,7488,110),'Complete source physical-contact and phase census')
    price=load(HERE/'pricing.py','fragment_complete_price');bound=price.run(local,native,word,physical,L)
    old=prior['complete_cost'];T=Counter({int(k):v for k,v in bound['targets'].items()});P=Counter({int(k):v for k,v in bound['paid'].items()})
    t=Counter({int(k):v for k,v in old['targets'].items()});p=Counter({int(k):v for k,v in old['paid'].items()})
    dt=Counter(T);dt.subtract(t);dp=Counter(P);dp.subtract(p)
    need({r:n for r,n in dt.items()if n}=={16:104,25:104,41:-104},'Every new productive target is priced')
    need({r:n for r,n in dp.items()if n}=={16:104,24:104,40:-104},'Fragment acquisition is fully paid')
    E=L.load(L.ROOT/'research/higher-moment-strictification/verify.py','fragment_predecessor_rejection')
    ot,op=E.moment(t,1-price.KAPPA),E.moment(p,1-price.KAPPA)
    need(ot[1]<op[0],'Previous complete caller cannot fund the new claim')
    bad=deepcopy(local);bad['paid'][1]-=1
    controls['unpaid_native_job']=rejected(lambda:price.assemble(bad,native,word,physical))
    bad=deepcopy(physical);bad['main_targets'][16]+=104
    controls['extra_productive_credit']=rejected(lambda:price.assemble(local,native,word,bad))
    return encode({'root':root,'unretired':forward_base,'body_retirement':body_forward,'caller':forward,'reverse':reverse,'retirement_witnesses':witness,'physical':physical,'scalar_envelope':scalar,'complete_cost':bound,'controls':controls,'target_delta':{16:104,25:104,41:-104},'paid_delta':{16:104,24:104,40:-104},'signed_gain':'104*((H25-H24)-(H41-H40)) > 0 for H(r)=r^t, 0<t<1','native_unchanged':{'public_inputs':local['public_inputs'],'owned_fields':local['owned_fields'],'owned_lifetimes':local['owned_lifetimes'],'peak_owned_fields':local['peak_owned_fields'],'all_columns':800,'events':len(native_word['program'])}})

def run():
    pins=authenticate();B=load(SOURCE/'verify.py','fragment_pinned_predecessor');original=B.candidate;captured={}
    def observed(native_word,local,native,L,source):
        old=original(native_word,local,native,L,source)
        need(old==read(SOURCE/'RESULT.json')['candidate'],'Exact pinned predecessor candidate receipt')
        need(not captured,'One complete source replay')
        captured.update(candidate(native_word,local,native,L,source,old))
        return old
    B.candidate=observed;retained=B.run();need(retained==read(SOURCE/'RESULT.json'),'Unchanged complete predecessor replay')
    need(captured,'New candidate reached full source boundary')
    return{'status':STATUS,'kappa_decimal':'0.00330500','previous_claim':'0.00330420','absolute_gain':'0.00000080','source':pins,'candidate':captured,'assumptions':retained['assumptions'],'selected_frontier_changed':False,'scope':'Complete changed conditional construction under unchanged five framework assumptions. No unconditional theorem, scientific admission, selected-frontier change, or materialized uniform word.'}

if __name__=='__main__':
    need(sys.argv[1:]in([],['--write-result']),'Explicit output mode')
    r=run()
    if sys.argv[1:]:(HERE/'RESULT.json').write_text(json.dumps(r,sort_keys=True,indent=2)+'\n')
    else:need(r==read(HERE/'RESULT.json'),'Frozen full receipt')
    print(STATUS,flush=True)
