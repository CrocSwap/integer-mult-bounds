"""New finite source-behaviour controls. Inert ports; NO native qualification.

AST extracts complete actual changed functions and unchanged funding DATA
functions. It never imports an archived module or calls a real owner, process,
compiler, science command, filesystem publisher, or lock operation.
"""
import ast, copy, hashlib, json, os, stat, sys, types
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'implementation/active_complete_close_v1.py'
FUNDING=ROOT/'implementation/funding_current.py.txt'

def extract(tree, names):
    nodes=[x for x in ast.walk(tree) if isinstance(x,(ast.FunctionDef,ast.ClassDef)) and x.name in names]
    if {x.name for x in nodes} != set(names): raise RuntimeError('missing exact source function')
    return ast.Module(body=nodes,type_ignores=[])

ft=ast.parse(FUNDING.read_bytes());fg={'hashlib':hashlib,'json':json,'os':os,'stat':stat,'Path':Path}
constants=[x for x in ft.body if isinstance(x,ast.Assign)]
fnames=('need','plain','exact','uint','digest','label','pin','pairs','forbidden_number','decode','registry','require_append_only','select','validate_pre_entry_provenance')
exec(compile(ast.Module(body=constants+extract(ft,fnames+('FundingError',)).body,type_ignores=[]),str(FUNDING),'exec'),fg)
F=types.SimpleNamespace(**fg)
tree=ast.parse(SOURCE.read_bytes());ag={'hashlib':hashlib,'json':json,'Path':Path,'F':F,'os':os}
constants=[x for x in tree.body if isinstance(x,ast.Assign)]
exec(compile(ast.Module(body=constants+extract(tree,('ActiveError','need','canonical','exception_instance','complete_close_data')).body,type_ignores=[]),str(SOURCE),'exec'),ag)
canonical=ag['canonical'];sha=lambda b:hashlib.sha256(b).hexdigest()

def pin(path,raw=b'x',mode=0o444): return dict(path=str(path),bytes=len(raw),sha256=sha(raw),mode=mode)

def fixture():
    C,D=ag['CONTROL'],ag['DOMAIN']
    request=dict(schema='fresh-round-request-v1',round_id=F.ROUND_ID,label='target',command_sha256='1'*64,body_reservation_ns=10,policy_sha256='2'*64,phase_release_sha256=None)
    registration=pin(C/'target-registration.json')
    start=dict(schema='fresh-round-start-v1',round_id=F.ROUND_ID,label='target',command_sha256=request['command_sha256'],body_reservation_ns=10,policy_sha256='2'*64,pre_entry_provenance=dict(schema='fresh-original-preentry-provenance-v1',entry_id='target',command_sha256=request['command_sha256'],body_reservation_ns=10,registration_pin=registration,original_start_pin=pin(C/'original-target-start.json'),pending_manifest_pin=pin(C/'original-target-pending.json')))
    sp=pin(D/'target/START.json',canonical(start),0o600)
    registry=dict(schema='fresh-round-registry-v2',round_id=F.ROUND_ID,authorization_sha256=F.AUTHORIZATION_SHA256,opening_pin=pin(C/'opening.json'),predecessor_sha256=None,phase='INITIAL',phase_release_sha256=None,policies=[dict(pin(C/'policy.json'),sha256='2'*64)],events=[dict(kind='REGISTER',label='target',pin=sp)])
    rr=canonical(registry);rh=canonical(dict(schema='fresh-active-head-v1',sequence=1,registry_pin=pin(C/'REGISTRY-000001.json',rr),previous_head_sha256='0'*64))
    hp=pin(ag['HEAD'],rh,0o600);base=pin(C/'REGISTRY-000000.json')
    own=dict(request,label='closer',command_sha256='3'*64,body_reservation_ns=2000)
    ownstart={'begin':100};ownprov={'original_start_pin':pin(C/'closer-start.json',canonical(ownstart))}
    docs={'source_manifest_pin':b'original admitted source bytes','profile_pin':b'original admitted profile bytes','policy':{'administrative_debit_ns':2}}
    b=dict(schema='complete-close-evidence-binding-v1',source_manifest_pin=pin(C/'source.json',docs['source_manifest_pin']),profile_pin=pin(C/'profile.json',docs['profile_pin']),expected_head_pin=hp,closer_start_clock_path=['begin'])
    contract=dict(schema='complete-close-result-contract-v1',kind='FULL_POSITIVE',command_sha256=request['command_sha256'],source_manifest_pin=b['source_manifest_pin'],profile_pin=b['profile_pin'])
    docs['result_contract_pin']=canonical(contract);b['result_contract_pin']=pin(C/'contract.json',docs['result_contract_pin'])
    admission=dict(schema='complete-close-original-admission-v1',request=request,start_pin=sp,baseline_registry_pin=base,source_manifest_pin=b['source_manifest_pin'],profile_pin=b['profile_pin'],result_contract_pin=b['result_contract_pin'],registration_pin=registration)
    docs['admission_pin']=canonical(admission);b['admission_pin']=pin(C/'admission.json',docs['admission_pin'])
    receipt=dict(schema='fresh-round-receipt-v1',round_id=F.ROUND_ID,label='target',start_sha256=sp['sha256'],outcome='PASS',body_elapsed_ns=5,administrative_debit_ns=2,body_begin_ns=10,body_end_ns=15,body_fully_observed=True,cleanup_known=True,custody_complete=True,nested_entries_complete=True,uncertainty=[],peak_sampled_rss_bytes=1,tail_state='COMPLETE',independent_outcome_review_sha256='0'*64)
    evidence={k:v for k,v in receipt.items() if k not in ('schema','administrative_debit_ns','independent_outcome_review_sha256')}
    evidence.update(schema='complete-close-accepted-evidence-v1',command_sha256=request['command_sha256'],interval_scope='COMPLETE_OUTER_COMMAND',rss_scope='AGGREGATE_SAMPLED_ROOT',result_kind='FULL_POSITIVE',raw_inputs=[pin('/fixture/original-raw.bin',b'complete raw fixture')])
    for name in ('admission','source_manifest','profile','result_contract'): evidence[name+'_sha256']=b[name+'_pin']['sha256']
    docs['evidence_manifest_pin']=canonical(evidence);b['evidence_manifest_pin']=pin(C/'evidence.json',docs['evidence_manifest_pin'])
    clock=dict(schema='complete-close-clock-lineage-v1',clock_domain_sha256='4'*64,target_start_sha256=sp['sha256'],closer_start_sha256=ownprov['original_start_pin']['sha256'],target_end_ns=15,closer_begin_ns=100)
    docs['clock_pin']=canonical(clock);b['clock_pin']=pin(C/'clock.json',docs['clock_pin'])
    closure=dict(request=request,start=start,start_pin=sp,baseline_registry_pin=base,receipt_pin={},review_pin={},evidence_binding=b)
    x=dict(closure=closure,receipt=receipt,docs=docs,own=own,ownprov=ownprov,ownstart=ownstart,current=F.decode(rh),rh=rh,rr=rr)
    refresh(x);return x

def refresh(x):
    b=x['closure']['evidence_binding'];proj=dict(x['receipt']);proj.pop('independent_outcome_review_sha256')
    review=dict(schema='complete-close-independent-review-v1',decision='ACCEPT_COMPLETE_OUTCOME',receipt_projection_sha256=sha(canonical(proj)),evidence_binding_sha256=sha(canonical(b)))
    x['review_raw']=canonical(review);x['receipt']['independent_outcome_review_sha256']=sha(x['review_raw']);x['raw']=canonical(x['receipt'])
    x['closure']['receipt_pin']=pin(ag['CONTROL']/'accepted-receipt.json',x['raw']);x['closure']['review_pin']=pin(ag['R']/'review/complete-close.json',x['review_raw'])

def validate(x):return ag['complete_close_data'](F,x['closure'],x['raw'],x['review_raw'],x['docs'],x['own'],x['ownprov'],x['ownstart'],x['current'],x['rh'],x['rr'])

results=[]
def check(name,fn):
    fn();results.append(name)
def require(ok):
    if ok is not True:raise RuntimeError('independent fixture expectation failed')
def denied(x):
    try:validate(x)
    except (ValueError,RuntimeError,KeyError,TypeError):return
    raise RuntimeError('mutation was not rejected')

# Inert method environment; actual source function bodies including advance.
def environment(x,fail_at=None,report_failure=None):
    e=dict(ag);events=[];files={};r=dict(role='CLOSER',phase='HELD',first=None,secondary=[],secondary_saturated=False,complete_errors=[None]*34,complete_error_count=1,complete_used=False,head_pin=x['closure']['evidence_binding']['expected_head_pin'],protocol_anchor_ns=0)
    for name in ('admission_pin','source_manifest_pin','profile_pin','result_contract_pin','evidence_manifest_pin','clock_pin'):files[x['closure']['evidence_binding'][name]['path']]=x['docs'][name]
    files[str(ag['HEAD'])]=x['rh'];files[x['current']['registry_pin']['path']]=x['rr']
    files[x['closure']['receipt_pin']['path']]=x['raw'];files[x['closure']['review_pin']['path']]=x['review_raw'];files[x['ownprov']['original_start_pin']['path']]=canonical(x['ownstart'])
    def verify(r):require(r['phase'] not in ('FAILED_UNCERTAIN_NO_RETRY','RELEASED','CLOSE_UNKNOWN'))
    def read_manual(r):r.update(manual_request=x['own'],manual_provenance=x['ownprov'])
    def read(r,p):
        raw=files[p['path']];require(len(raw)==p['bytes'] and sha(raw)==p['sha256']);return raw
    def fail(r,error):
        if report_failure is not None:raise report_failure
        if r['first'] is None:r['first']=error
        r['phase']='FAILED_UNCERTAIN_NO_RETRY';return r['first']
    def publish(r,path,raw,mode,replace_head=False):
        tag='head' if replace_head else 'receipt' if path.name=='receipt.json' else 'history' if path.parent==ag['HEADS'] else 'registry'
        events.append(tag)
        if fail_at==tag:raise primary
        p=pin(path,raw,mode);files[str(path)]=raw
        if tag=='head':r['head_pin']=p
        return p
    def head(r,p):
        if 'head' in events:
            if fail_at=='readback':raise primary
            h=files[str(ag['HEAD'])];obj=F.decode(h);return obj,h,files[obj['registry_pin']['path']]
        return x['current'],x['rh'],x['rr']
    def close_actual(r):
        events.append('release')
        if fail_at=='release':raise primary
    primary=RuntimeError('raw primary operation failure')
    e.update(role='CLOSER',complete_closure=x['closure'],closure=None,complete_validator=ag['complete_close_data'],complete_validator_image=None,active_globals={'complete_close_data':ag['complete_close_data']},unchanged_function=lambda *a:None,verify=verify,read_manual=read_manual,read=read,funding_io=lambda *a: {'policies':{x['own']['policy_sha256']:x['docs']['policy']}},current_registry_pin=lambda r: x['current']['registry_pin'],active_view=lambda r:None,head=head,publish=publish,stage_empty=lambda:None,fail=fail,rec=lambda self:r,close_actual=close_actual,time=types.SimpleNamespace(monotonic_ns=lambda:1000))
    e.update(cg={'FIRST':[None]},first_state=None);e['first_state']=e['cg']['FIRST']
    e['F']=types.SimpleNamespace(**vars(F),metadata_decode=F.decode)
    e['os']=types.SimpleNamespace(getuid=lambda:0)
    code=extract(tree,('complete_failure','publish_complete','advance','publish_reviewed_close','release'))
    exec(compile(code,str(SOURCE),'exec'),e)
    return e,r,events,primary

def method_success():
    e,r,events,_=environment(fixture());out=e['publish_reviewed_close'](object());require(events==['receipt','registry','history','head']);require(out['all_costs_settled'] is False and out['native_capability'] is False and out['execution_permission'] is False);require(r['complete_own_request']['label']=='closer');require(r['request']['label']=='target')
    try:e['publish_reviewed_close'](object())
    except RuntimeError:pass
    else:raise RuntimeError('replay accepted')
    require(events==['receipt','registry','history','head'])
check('actual changed close and advance exact publication sequence, no grants, one use',method_success)
check('whole validator complete positive',lambda:require(validate(fixture())[0]['outcome']=='PASS'))
for key,value in [('outcome','STOP'),('body_elapsed_ns',True),('body_begin_ns',False),('peak_sampled_rss_bytes',None),('cleanup_known',False),('custody_complete',False),('nested_entries_complete',False),('uncertainty',['unknown']),('tail_state','UNKNOWN'),('administrative_debit_ns',True),('label','other'),('start_sha256','f'*64)]:
    def case(key=key,value=value):x=fixture();x['receipt'][key]=value;refresh(x);denied(x)
    check('receipt mutation '+key,case)
for key,value in [('interval_scope','PREFIX_ONLY'),('rss_scope','MAX_SINGLE_CHILD'),('result_kind','EXPECTED_REFUSAL'),('command_sha256','f'*64),('source_manifest_sha256','f'*64),('profile_sha256','f'*64),('admission_sha256','f'*64),('raw_inputs',[])]:
    def case(key=key,value=value):x=fixture();d=F.decode(x['docs']['evidence_manifest_pin']);d[key]=value;x['docs']['evidence_manifest_pin']=canonical(d);x['closure']['evidence_binding']['evidence_manifest_pin']=pin(ag['CONTROL']/'evidence.json',x['docs']['evidence_manifest_pin']);refresh(x);denied(x)
    check('accepted evidence mutation '+key,case)
for tag in ('receipt','registry','history','head','readback'):
    def case(tag=tag):
        e,r,events,a=environment(fixture(),tag)
        try:e['publish_reviewed_close'](object())
        except BaseException as caught:require(caught is a)
        else:raise RuntimeError('fault unobserved')
        saved=list(events)
        try:e['publish_reviewed_close'](object())
        except BaseException:pass
        require(events==saved and r['first'] is a)
    check('actual advance publication boundary failure '+tag,case)

def resource_failure(outcome='STOP'):
    x=fixture();x['receipt'].update(outcome=outcome,body_end_ns=40,body_elapsed_ns=30,peak_sampled_rss_bytes=F.RSS_LIMIT+1)
    d=F.decode(x['docs']['evidence_manifest_pin']);d.update({k:x['receipt'][k] for k in ('outcome','body_end_ns','body_elapsed_ns','peak_sampled_rss_bytes')});x['docs']['evidence_manifest_pin']=canonical(d);x['closure']['evidence_binding']['evidence_manifest_pin']=pin(ag['CONTROL']/'evidence.json',x['docs']['evidence_manifest_pin']);d=F.decode(x['docs']['clock_pin']);d['target_end_ns']=40;x['docs']['clock_pin']=canonical(d);x['closure']['evidence_binding']['clock_pin']=pin(ag['CONTROL']/'clock.json',x['docs']['clock_pin']);refresh(x);require(validate(x)[0]['body_elapsed_ns']==30)
check('known resource-invalid STOP retains untrimmed actual values',resource_failure)
check('original resource-invalid PASS retains untrimmed actual values',lambda:resource_failure('PASS'))

def custody():
    c=RuntimeError('recorder C');e,r,events,b=environment(fixture(),'release',c);a=RuntimeError('original A');r['first']=a;r['complete_errors'][0]=a;r['complete_used']=True
    try:e['release'](object())
    except BaseException as caught:require(caught is a)
    require(any(v is b for v in r['complete_errors']) and any(v is c for v in r['complete_errors']))
check('A remains primary through release B and recorder C',custody)
for name,mutate in [('own reservation cannot borrow target',lambda x:x['own'].update(body_reservation_ns=5)),('wrong role',None),('stale reviewed HEAD',lambda x:x['closure']['evidence_binding']['expected_head_pin'].update(sha256='f'*64))]:
    def case(name=name,mutate=mutate):
        x=fixture()
        if mutate:mutate(x)
        e,r,events,_=environment(x)
        if name=='own reservation cannot borrow target':e['time']=types.SimpleNamespace(monotonic_ns=lambda:7)
        if name=='wrong role':e['role']='CONTROLLER'
        try:e['publish_reviewed_close'](object())
        except BaseException:pass
        else:raise RuntimeError('invalid admission accepted')
        require(events==[])
    check(name,case)
def request_start_mismatch():
    x=fixture();x['closure']['request']['command_sha256']='5'*64
    try:validate(x)
    except RuntimeError as error:require('request agrees with actual registered START' in str(error));return
    raise RuntimeError('mismatched valid-looking alternate request accepted')
check('request command cannot substitute for actual registered START',request_start_mismatch)

def first_state_custody():
    e,r,events,d=environment(fixture(),'release',RuntimeError('recorder C'))
    a=RuntimeError('established original A');b=RuntimeError('initial verify B');e['first_state'][0]=a
    def bad_verify(record):raise b
    e['verify']=bad_verify
    try:e['publish_reviewed_close'](object())
    except BaseException as caught:require(caught is a)
    require(r['complete_used'] is False and any(v is b for v in r['complete_errors']))
    try:e['release'](object())
    except BaseException as caught:require(caught is a)
    require(any(v is d for v in r['complete_errors']) and r['phase']=='CLOSE_UNKNOWN')
    before=list(events)
    try:e['release'](object())
    except BaseException:pass
    require(events==before)
check('original FIRST A survives initial verify B, release D, recorder C and one release',first_state_custody)

def legacy():
    x=fixture();x['receipt'].update(outcome='STOP',cleanup_known=False,tail_state='UNKNOWN',uncertainty=['unresolved original'])
    refresh(x);e,r,events,_=environment(x);e['complete_closure']=None;e['closure']={k:v for k,v in x['closure'].items() if k!='evidence_binding'}
    result=e['publish_reviewed_close'](object());require(events==['receipt','registry','history','head'])
    require(set(result)=={'receipt_pin','head_pin','all_costs_settled','execution_permission'})
check('actual legacy STOP UNKNOWN branch result and publication retained',legacy)

def capacity():
    x=fixture();x['current']['sequence']=2*F.MAX_ENTRIES;denied(x)
check('prospective exhausted registry generation before publication',capacity)

def large_metadata():
    x=fixture();x['raw']=b' '* (F.META_CAP+1);denied(x)
check('oversized formal receipt metadata rejected',large_metadata)

def selected_result(kind, outcome):
    x=fixture();b=x['closure']['evidence_binding'];contract=F.decode(x['docs']['result_contract_pin']);contract['kind']=kind
    x['docs']['result_contract_pin']=canonical(contract);b['result_contract_pin']=pin(ag['CONTROL']/'contract.json',x['docs']['result_contract_pin'])
    admission=F.decode(x['docs']['admission_pin']);admission['result_contract_pin']=b['result_contract_pin'];x['docs']['admission_pin']=canonical(admission);b['admission_pin']=pin(ag['CONTROL']/'admission.json',x['docs']['admission_pin'])
    x['receipt']['outcome']=outcome;d=F.decode(x['docs']['evidence_manifest_pin']);d.update(outcome=outcome,result_kind=kind,result_contract_sha256=b['result_contract_pin']['sha256'],admission_sha256=b['admission_pin']['sha256'])
    x['docs']['evidence_manifest_pin']=canonical(d);b['evidence_manifest_pin']=pin(ag['CONTROL']/'evidence.json',x['docs']['evidence_manifest_pin']);refresh(x)
    require(validate(x)[0]['outcome']==outcome)
check('selected original expected-refusal oracle positive',lambda:selected_result('EXPECTED_REFUSAL','PASS'))
check('selected original known-STOP disposition positive',lambda:selected_result('KNOWN_STOP','STOP'))

def static_compatibility():
    # These are static properties, not executed bind/native authentication.
    old=ast.parse((ROOT/'reference/active_original.py.txt').read_bytes())
    def method(t):return next(x for x in ast.walk(t) if isinstance(x,ast.FunctionDef) and x.name=='publish_reviewed_close')
    before=method(old).body;after=method(tree).body
    require(ast.dump(ast.Module(body=before,type_ignores=[]))==ast.dump(ast.Module(body=[after[0]]+after[2:],type_ignores=[])))
    def methods(t):return [x.name for c in ast.walk(t) if isinstance(c,ast.ClassDef) and c.name=='Context' for x in c.body if isinstance(x,ast.FunctionDef)]
    require(methods(old)==methods(tree))
check('static exact legacy close body and Context method set retained',static_compatibility)

print(json.dumps({'schema':'complete-close-finite-control-result-v1','mode':'assertion-on' if __debug__ else 'optimized','source_sha256':sha(SOURCE.read_bytes()),'funding_sha256':sha(FUNDING.read_bytes()),'passed':len(results),'cases':results,'scope':'AST-extracted whole changed functions and actual advance with INERT ports; no native ownership, bootstrap authentication, genuine evidence or fit qualification'},indent=2))
