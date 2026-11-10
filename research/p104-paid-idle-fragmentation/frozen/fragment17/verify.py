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
STATUS='PASS_CONDITIONAL_KAPPA_00330580_REBALANCED_PAID_FRAGMENT'

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
    for label,index in [('fragmented_B_idle',word['events'].index(['IDLE_ONE',2,[5,6,7,8]])),('body_input_basis',3),('body_handoff',witness[0]['handoff_after']+3),('D_handoff',witness[1]['handoff_after']),('final_return',len(word['events'])-1)]:
        bad=deepcopy(word);bad['events'][index]=['SCALE',0,'1']
        controls[label]=rejected(lambda bad=bad:C.replay(bad))
    for role,label in[(6,'body_prefix_unearned_head'),(32,'body_suffix_wrong_body'),(33,'D_suffix_unearned_head')]:
        bad=deepcopy(word)
        if role==32:bad['diagonal'][role][10]=0
        else:bad['diagonal'][role][0]=-1
        controls[label]=rejected(lambda bad=bad:sys.modules['rows'].transpose(bad))
    physical=load(physical_source/'physical.py','fragment_physical').physical(word,native_word,L)
    need((physical['ports'],physical['full_calls'],physical['physical_contacts'],physical['ordinary_normalizations'])==(104,17,7072,104),'Complete source physical-contact and phase census')
    price=load(HERE/'pricing.py','fragment_complete_price');bound=price.run(local,native,word,physical,L)
    old=prior['complete_cost'];T=Counter({int(k):v for k,v in bound['targets'].items()});P=Counter({int(k):v for k,v in bound['paid'].items()})
    t=Counter({int(k):v for k,v in old['targets'].items()});p=Counter({int(k):v for k,v in old['paid'].items()})
    dt=Counter(T);dt.subtract(t);dp=Counter(P);dp.subtract(p)
    need(sum(T.values())==13107,'Every independent productive field is counted')
    need(sum(P.values())==63294,'Every paid fragmented and native request is counted')
    E=L.load(L.ROOT/'research/higher-moment-strictification/verify.py','fragment_predecessor_rejection')
    ot,op=E.moment(t,1-price.KAPPA),E.moment(p,1-price.KAPPA)
    need(ot[1]<op[0],'Previous complete caller cannot fund the new claim')
    bad=deepcopy(local);bad['paid'][1]-=1
    controls['unpaid_native_job']=rejected(lambda:price.assemble(bad,native,word,physical))
    bad=deepcopy(physical);bad['main_targets'][32]+=104
    controls['extra_productive_credit']=rejected(lambda:price.assemble(local,native,word,bad))
    return encode({'root':root,'unretired':forward_base,'body_retirement':body_forward,'caller':forward,'reverse':reverse,'retirement_witnesses':witness,'physical':physical,'scalar_envelope':scalar,'complete_cost':bound,'controls':controls,'target_delta':{r:n for r,n in dt.items()if n},'paid_delta':{r:n for r,n in dp.items()if n},'signed_gain':'104*((H9-H8)-(H41-H40)) at the new child allocation > 0 for H(r)=r^t, 0<t<1','native_unchanged':{'public_inputs':local['public_inputs'],'owned_fields':local['owned_fields'],'owned_lifetimes':local['owned_lifetimes'],'peak_owned_fields':local['peak_owned_fields'],'all_columns_previously_replayed':800,'events':len(native_word['program'])}})

def run():
    # Reuse the once fully replayed, byte-pinned native theorem. Only caller,
    # physical fresh-stage maps, invoice, finite compiler and outer ledger change.
    from types import SimpleNamespace
    import gzip
    pins=authenticate();frozen=read(HERE.parent/'fragment/FROZEN.json')
    for record in frozen['files']:
        need(sha256((HERE.parent/'fragment'/record['path']).read_bytes()).hexdigest()==record['sha256'],'Unchanged admitted predecessor '+record['path'])
    deps=read(HERE/'DEPENDENCIES.json')
    for record in deps:
        need(sha256((HERE.parent/record['path']).read_bytes()).hexdigest()==record['sha256'],'Exact replay dependency '+record['path'])
    old=read(HERE.parent/'fragment/RESULT.json')
    need(old['status']=='PASS_CONDITIONAL_KAPPA_00330500_PAID_FRAGMENT_RETIREMENT','Once fully replayed native/caller evidence')
    runtime=HERE.parent/'runtime/root'
    L=SimpleNamespace(ROOT=runtime,need=need,read=read,load=load)
    native_path=HERE.parent/'sources/pr6702/unpacked/research/gaussian-root-retirement/native/research/p104-scaled-transport-fusion/WORD.json.gz'
    native_word=json.loads(gzip.decompress(native_path.read_bytes()))
    native_old=old['candidate']['native_unchanged']
    need((native_word['public'],native_word['owned_fields'],len(native_word['program']))==(771,29,18577),'Identical complete native word boundary')
    helpers={1:14,2:8,3:4,4:108,5:16,6:3,7:9,8:40,9:361}
    paid={1:2231,2:454,3:490,4:109,5:152,6:8,7:9,8:1}
    local={'helpers':helpers,'paid':paid,'public_inputs':771,'owned_fields':29,'owned_lifetimes':47,'peak_owned_fields':14,'real_scalar_allowance':137990}
    native={'helpers':helpers,'helper_normalizers':1126,'main_adapters':208}
    physical_source=HERE.parent/'sources/pr6702/unpacked/research/gaussian-root-retirement'
    captured=candidate(native_word,local,native,L,physical_source,old['candidate'])
    independent=load(HERE/'independent.py','fragment17_independent').run()
    return{'status':STATUS,'kappa_decimal':'0.00330580','previous_claim':'0.00330500','absolute_gain':'0.00000080','gain_over_PR6716':'0.00000160','source':pins,'native_evidence_sha256':sha256((HERE.parent/'fragment/RESULT.json').read_bytes()).hexdigest(),'candidate':captured,'independent':independent,'assumptions':old['assumptions'],'selected_frontier_changed':False,'scope':'Changed complete caller with independently checked all-input identities, physical maps, invoice, finite compiler and outer transfer; unchanged native evidence reused from a full source replay. Same five conditional framework assumptions; no materialized uniform word.'}

if __name__=='__main__':
    need(sys.argv[1:]in([],['--write-result']),'Explicit output mode')
    r=run()
    if sys.argv[1:]:(HERE/'RESULT.json').write_text(json.dumps(r,sort_keys=True,indent=2)+'\n')
    else:need(r==read(HERE/'RESULT.json'),'Frozen full receipt')
    print(STATUS,flush=True)
