#!/usr/bin/env python3
"""Independent funded compiler-point successor audit; no author code imports."""
from pathlib import Path
from hashlib import sha256,sha1
from fractions import Fraction as Q
import ast,json,argparse,resource
from exact_engine import evaluate,MODEL,need
from bind_and_check import checked_bytes,SOURCE_IDENTICAL,fraction_assignments
H=Path(__file__).resolve().parent;W=H.parent
CAP=W/'09-capsule-cold/capsule-5387-v1'
HEAD='b1ab650d36f59e5be682a813145b7c67e219e341';BASE='1ec1119972c9aefe42525172d07b332fcff81cb4'
MANIFEST_SHA='b0b7eaeef8895264f33e86d87c1bf63fba495d6ac2f50e1414ee3eae775a1594'
PACKAGE='research/eight-owned-relations'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def run():
    a=argparse.ArgumentParser();a.add_argument('--invoice-sha256',required=True);opt=a.parse_args()
    resource.setrlimit(resource.RLIMIT_AS,(500*1024*1024,500*1024*1024))
    out=H/'5387-receipt-v1.json';need(not out.exists(),'immutable 5387 arithmetic receipt exists')
    need(sha(CAP/'IMMUTABLE-MANIFEST.json')==MANIFEST_SHA,'5387 capsule mismatch')
    m=read(CAP/'IMMUTABLE-MANIFEST.json');need((m['candidate_head'],m['canonical_main'],m['package'])==(HEAD,BASE,PACKAGE),'5387 pins mismatch')
    for row in m['rows']:checked_bytes(row,(CAP/row['capsule_path']).read_bytes())
    for name,expected in SOURCE_IDENTICAL.items():need(sha(CAP/'snapshot'/name)==expected,'source certified formula changed '+name)
    for name,expected in [('EXACT-COMMIT.raw',HEAD),('CANONICAL-COMMIT.raw',BASE)]:
        b=(CAP/name).read_bytes();need(sha1(b'commit '+str(len(b)).encode()+b'\0'+b).hexdigest()==expected,'5387 raw commit mismatch')
    ip=W/'02-census/INVOICE-v2.json';need(sha(ip)==opt.invoice_sha256,'5387 independent invoice hash mismatch');inv=read(ip)
    need(inv['candidate']['head']==HEAD and inv['candidate']['module']==PACKAGE,'5387 invoice wrong candidate')
    need(inv['capsule_manifest_sha256']==MANIFEST_SHA and inv['census_status']=='LITERAL_RANK_AND_SCALAR_CENSUS_READY','5387 invoice source/status mismatch')
    for name,v in inv['input_hashes'].items():need(sha(CAP/'snapshot'/name)==v['sha256'],'5387 invoice input changed')
    need(inv['ordinary']['classification']=='constructively_upper_bounded' and inv['ordinary']['unknown_charges_are_zero'] is False,'unsupported ordinary charges')
    need(inv['ordinary']['local_units_upper']<10**7 and inv['ordinary']['raw_nonrecursive_units_upper']<10**9,'5387 ordinary cost fails')
    need(inv['histograms']==read(W/'02-census/INVOICE-v1.json')['histograms'],'profile successor changed P/T')
    pp=CAP/'snapshot'/PACKAGE/'price.py';typed=fraction_assignments(pp.read_bytes())
    need(typed['KAPPA']=='.003026674765' and typed['TESTED']=='.003026674766','5387 typed interface mismatch')
    config={'model':MODEL,'tuple':{'power':1024,'cutoff':20,'floor':21,'tail_offset':'1/5','theta':'63/64','logarithm_power':1000},'kappa':typed['KAPPA'],'tested':typed['TESTED'],'reserve':'1/1000000000000','root_bracket':['.00302667476807','.00302667476808'],'ordinary_BIT':read(CAP/'snapshot/research/query-thinned-controllers/RESULT.json')['ordinary_BIT']}
    r=evaluate(inv['histograms']['productive'],inv['histograms']['paid'],config)
    need((r['H'],r['j'])==(409549000000000000,58507),'5387 independent compiler threshold mismatch')
    alpha=tuple(map(Q,r['ratios']['alpha']));lower=Q(1,1024*(2**30-1));upper=1-alpha[1]
    need(lower<Q(config['reserve'])<upper,'5387 fixed-envelope reserve window closed')
    need(alpha[0]>1-Q(1,10**9),'5387 predecessor reserve mutation accepted')
    need(1/(1+1024*Q(1,10**13))+Q(4,2**32)>1,'5387 insufficient reserve accepted')
    old=read(H/'receipt-v2.json')
    need(old['endpoint_funded'] is True and old['targets']==r['targets'] and old['paid']==r['paid'],'5383 independent profile admission missing')
    r.update(schema='independent-exact-funding/1',status='PASS_EXACT_FUNDING_ARITHMETIC_BOUND_TO_5387_INDEPENDENT_CENSUS',candidate={'pr':5387,'head':HEAD,'canonical_base':BASE,'package':PACKAGE},config=config,invoice={'path':str(ip),'sha256':sha(ip),'producer_status':inv['census_status'],'complete_bill_status':inv['complete_bill_status'],'ordinary':inv['ordinary']},source={'capsule_manifest_path':str(CAP/'IMMUTABLE-MANIFEST.json'),'capsule_manifest_sha256':MANIFEST_SHA,'authenticated_blob_rows':len(m['rows']),'source_identical_reuse':SOURCE_IDENTICAL,'price_sha256':sha(pp),'typed_price_constants':typed},same_profile_predecessor={'path':str(H/'receipt-v2.json'),'sha256':sha(H/'receipt-v2.json'),'P_T_identical':True,'word_identical':False,'credit':'Ali Romman #5383 independently admitted P/T profile; Dugongue #5387 preparation ordering and funded compiler-point successor'},reserve_window={'fixed_rounding_envelope_strict_lower':str(lower),'certified_alpha_strict_upper':str(upper),'source_reserve':config['reserve'],'both_strict':True,'predecessor_1e_9_reserve_rejected':True,'insufficient_1e_13_reserve_rejected':True,'scope':'For the fixed1024-fold power and4/2^32 rounding envelope only'},gain_over_independent_5383=str(Q(r['kappa'])-Q(old['kappa'])),independent_invoice_bound=True,source_capsule_bound=True,finite_template_gate_bound=False,endpoint_funded=False,engine_sha256=sha(H/'exact_engine.py'),binding_runner_sha256=sha(Path(__file__)),scientific_scope='Actual reserved compiler point passes exact arithmetic and complete literal census. Requires independent changed-word physical/preparation and fresh new-N expanded template gates before conditional admission.',external_gate_requirements=['01 #5387 literal preparation/order physical gate','03 #5387 new-N/G/O/stock/template applicability','09 serial registered replay/publication'])
    raw=(json.dumps(r,indent=2,sort_keys=True)+'\n').encode();out.write_bytes(raw);out.chmod(0o444)
    (H/'5387-receipt-v1.sha256').write_text(sha(out)+'  5387-receipt-v1.json\n')
    print(json.dumps({'status':r['status'],'receipt_sha256':sha(out),'kappa':r['kappa'],'H':r['H'],'j':r['j'],'seconds':r['seconds'],'endpoint_funded':False}))
if __name__=='__main__':run()
