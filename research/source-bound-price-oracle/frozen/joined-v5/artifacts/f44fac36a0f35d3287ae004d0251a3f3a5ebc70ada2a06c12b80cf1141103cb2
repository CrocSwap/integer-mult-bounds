#!/usr/bin/env python3
"""Bind independent arithmetic to peer census and source capsule; no author imports."""
from pathlib import Path
from hashlib import sha256,sha1
import ast,json,resource
from exact_engine import evaluate,MODEL,need
HERE=Path(__file__).resolve().parent
WAVE=HERE.parent
CAP=WAVE/'09-capsule-cold/capsule-v1'
MANIFEST_SHA='ae6a1b933c386feabc9bab3300163df41e94bd3ddeeff973955695d33d5b11c8'
HEAD='4bd6efa51a495a7c7b7754915cf0244e7e60969e'
INVOICE_SHA='7c6dfe167dd83cc48b32743e6bcfa76e3420ccd5be997c935b02a99e3636f44e'
CANONICAL='1ec1119972c9aefe42525172d07b332fcff81cb4'
PACKAGE='research/kappa-joint-relations-20261023'
# Previously independently reviewed selected-source dependencies, rechecked live.
SOURCE_IDENTICAL={
'research/pr4359-p7-padding/dependencies/compiler-refill/endpoint.py':'d097e55f06c3f244f2074ffd7c1a0a5f3c4b4b6a6accf9619d1dde5c0ae85e15',
'research/query-thinned-controllers/RESULT.json':'6ebfc8c0f09166f4834e9d7427410cb31aefff2cd4d4ce588c8e52c9c70e9a0f',
'research/joint-helper-lattice/CONTROLLER.json':'1f5d6aa267e4e66048818714b5d3b5eae17a58abe91d15deeaa34574f7391a5f'}
def digest(b):return sha256(b).hexdigest()
def read(p):return json.loads(p.read_bytes())
def checked_bytes(row,data):
    need(len(data)==row['bytes'],'source byte length mismatch')
    need(digest(data)==row['sha256'],'source SHA256 mismatch')
    need(sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['git_blob'],'source Git blob mismatch')
def authenticate_capsule():
    raw=(CAP/'IMMUTABLE-MANIFEST.json').read_bytes();need(digest(raw)==MANIFEST_SHA,'capsule manifest mismatch');m=json.loads(raw)
    need((m['candidate_head'],m['canonical_main'],m['package'])==(HEAD,CANONICAL,PACKAGE),'source pin mismatch')
    checked=[]
    for row in m['rows']:
        p=CAP/row['capsule_path'];need(p.is_relative_to(CAP),'capsule path escapes');checked_bytes(row,p.read_bytes());checked.append(row['capsule_path'])
    for name,expected in SOURCE_IDENTICAL.items():need(digest((CAP/'snapshot'/name).read_bytes())==expected,'inherited source changed: '+name)
    for name,kind,expected in [('EXACT-COMMIT.raw','commit',HEAD),('CANONICAL-COMMIT.raw','commit',CANONICAL)]:
        b=(CAP/name).read_bytes();need(sha1(kind.encode()+b' '+str(len(b)).encode()+b'\0'+b).hexdigest()==expected,'raw commit changed')
    need(all(r['candidate_ancestor_exit']==r['canonical_ancestor_exit']==0 for r in m['history']),'source ancestry producer failure')
    return m,checked

def fraction_assignments(price):
    out={}
    for n in ast.parse(price).body:
        if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name) and n.value.func.id=='Q' and len(n.value.args)==1 and isinstance(n.value.args[0],ast.Constant):out[n.targets[0].id]=n.value.args[0].value
    return out

def load_bound_invoice(expected_sha=None,raw=None):
    path=WAVE/'02-census/INVOICE-v1.json';raw=path.read_bytes() if raw is None else raw
    if expected_sha is not None:need(digest(raw)==expected_sha,'invoice immutable hash mismatch')
    inv=json.loads(raw);need(inv['schema']=='independent-literal-invoice/1','unsupported invoice schema')
    need(inv['candidate']['head']==HEAD and inv['candidate']['base']==CANONICAL,'invoice source/head mismatch')
    need(inv['census_status']=='LITERAL_RANK_AND_SCALAR_CENSUS_READY','independent census not ready')
    for name,v in inv['input_hashes'].items():need(digest((CAP/'snapshot'/name).read_bytes())==v['sha256'],'invoice/capsule bytes disagree')
    need(inv['ordinary']['classification']=='constructively_upper_bounded' and inv['ordinary']['unknown_charges_are_zero'] is False,'unsupported ordinary invoice')
    need(inv['ordinary']['local_units_upper']<10**7 and inv['ordinary']['raw_nonrecursive_units_upper']<10**9,'ordinary charge budget failed')
    return inv,digest(raw)

def run():
    resource.setrlimit(resource.RLIMIT_AS,(500*1024*1024,500*1024*1024))
    need(not (HERE/'receipt-v1.json').exists(),'immutable receipt already exists; use new version')
    manifest,checked=authenticate_capsule();inv,invhash=load_bound_invoice(INVOICE_SHA)
    pricep=CAP/'snapshot'/PACKAGE/'price.py';price=pricep.read_bytes();f=fraction_assignments(price)
    need(f['KAPPA']=='.00302666' and f['TESTED']=='.00302667','typed source interface changed')
    bit=read(CAP/'snapshot/research/query-thinned-controllers/RESULT.json')['ordinary_BIT']
    config={'model':MODEL,'tuple':{'power':1024,'cutoff':20,'floor':21,'tail_offset':'1/5','theta':'63/64','logarithm_power':1000},'kappa':f['KAPPA'],'tested':f['TESTED'],'reserve':'1/1000000000','root_bracket':['.00302667476807','.00302667476808'],'ordinary_BIT':bit}
    T=inv['histograms']['productive'];P=inv['histograms']['paid'];r=evaluate(T,P,config)
    need((r['paid_count'],r['productive_count'],r['rank_mass_surplus'])==(64148,10800,752),'independent census disagreement')
    controls={}
    mutant=read(WAVE/'02-census/INVOICE-v1.json');mutant['histograms']['productive']['9']+=128
    try:load_bound_invoice(invhash,json.dumps(mutant).encode())
    except ValueError as e:controls['unearned_productive_credit_hash_binding']=str(e)
    else:raise ValueError('unearned productive credit accepted')
    row=manifest['rows'][0];data=(CAP/row['capsule_path']).read_bytes()
    try:checked_bytes(row,data+b'\n')
    except ValueError as e:controls['source_mutation']=str(e)
    else:raise ValueError('source mutation accepted')
    try:evaluate(T,P,dict(config,model='unproved-model'))
    except ValueError as e:controls['unsupported_model']=str(e)
    else:raise ValueError('unsupported model accepted')
    try:evaluate(T,P,dict(config,tuple=dict(config['tuple'],cutoff=22)))
    except ValueError as e:controls['unsupported_parameter_domain']=str(e)
    else:raise ValueError('unsupported tuple accepted')
    r.update(schema='independent-exact-funding/1',status='PASS_EXACT_FUNDING_ARITHMETIC_BOUND_TO_INDEPENDENT_CENSUS',candidate={'pr':5383,'head':HEAD,'canonical_base':CANONICAL,'package':PACKAGE},invoice={'path':str(WAVE/'02-census/INVOICE-v1.json'),'sha256':invhash,'producer_status':inv['census_status'],'complete_bill_status':inv['complete_bill_status'],'ordinary':inv['ordinary']},source={'capsule_manifest_path':str(CAP/'IMMUTABLE-MANIFEST.json'),'capsule_manifest_sha256':MANIFEST_SHA,'authenticated_blob_rows':len(checked),'source_identical_reuse':SOURCE_IDENTICAL,'price_sha256':digest(price),'typed_price_constants':f,'ancestry_status':'independent capsule producer reports authenticated raw Git ancestry; consumer rechecked blob/commit bytes'},config=config,independent_invoice_bound=True,source_capsule_bound=True,finite_template_gate_bound=False,endpoint_funded=False,binding_controls=controls,engine_sha256=digest((HERE/'exact_engine.py').read_bytes()),binding_runner_sha256=digest(Path(__file__).read_bytes()),scientific_scope='Exact compiler/outer arithmetic funded at final rational κ, conditional on role01 physical and role03 fresh precision/stock/template gate. This receipt alone does not promote complete scientific admission or selected status.')
    raw=(json.dumps(r,indent=2,sort_keys=True)+'\n').encode();(HERE/'receipt-v1.json').write_bytes(raw);(HERE/'receipt-v1.sha256').write_text(digest(raw)+'  receipt-v1.json\n')
    print(json.dumps({'receipt_sha256':digest(raw),'invoice_sha256':invhash,'status':r['status'],'kappa':r['kappa'],'seconds':r['seconds']}))
if __name__=='__main__':run()
