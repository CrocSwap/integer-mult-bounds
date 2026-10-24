#!/usr/bin/env python3
"""Independent #5392 exact arithmetic bound to the complete literal invoice.

No candidate module is imported. All source interpretation uses JSON/AST;
all numerical decisions use a standalone directed rational engine.
"""
from pathlib import Path
from hashlib import sha256
from fractions import Fraction as Q
import ast,json,resource
from exact_engine import evaluate,MODEL,need
from invoice import CAP,PKG,HEAD,BASE,checked,read,sha,transpose_records,local_paid
H=Path(__file__).resolve().parent
INVOICE_SHA='5263880a5a88ec356879aba7452f13be817ee82469bd00166b28d35e82233016'
def source_inventory():
 p=H/'frozen-canonical/research/pr4359-p7-padding/dependencies/compiler-refill/endpoint.py'
 node=next(n for n in ast.parse(p.read_bytes()).body if isinstance(n,ast.FunctionDef) and n.name=='ledger');x={}
 for n in node.body:
  if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and isinstance(n.value,ast.Dict):x[n.targets[0].id]=[k.value for k in n.value.keys]
 strict=set(x['checks'])|{k+'_above_kappa' for k in x['margins']};functional=set(x['functional'])|{'actual_new_BIT_stock_sublinear'}
 return {'path':str(p),'sha256':sha(p),'direct_strict':x['checks'],'derived_strict':[k+'_above_kappa' for k in x['margins']],'generic_functional':x['functional'],'new_source_functional':['actual_new_BIT_stock_sublinear'],'strict_keys':sorted(strict),'functional_keys':sorted(functional)}
def parameters():
 p=CAP/PKG/'price.py';out={}
 for n in ast.parse(p.read_bytes()).body:
  if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name) and n.value.func.id=='Q' and len(n.value.args)==1 and isinstance(n.value.args[0],ast.Constant):out[n.targets[0].id]=n.value.args[0].value
 need(out['KAPPA']=='.00302725' and out['TESTED']=='.00302726','new source tested interface changed')
 return out

def run():
 resource.setrlimit(resource.RLIMIT_AS,(500*1024*1024,500*1024*1024))
 outp=H/'FUNDING-v1.json';need(not outp.exists(),'immutable funding receipt exists')
 need(sha(H/'INVOICE-v1.json')==INVOICE_SHA,'independent invoice changed');inv=read(H/'INVOICE-v1.json')
 root=read(CAP/'ROOT-MANIFEST.json');need(root['head']==HEAD and sha(CAP/'ROOT-MANIFEST.json')==inv['authentication']['root_manifest_sha256'],'root source manifest changed')
 for row in root['rows']:checked(row,(CAP/row['path']).read_bytes())
 for name,row in inv['authentication']['canonical'].items():need(sha(Path(row['path']))==row['sha256'],'canonical source changed')
 typed=parameters();inventory=source_inventory();bit=read(H/'frozen-canonical/research/query-thinned-controllers/RESULT.json')['ordinary_BIT']
 config={'model':MODEL,'tuple':{'power':1024,'cutoff':20,'floor':21,'tail_offset':'1/5','theta':'63/64','logarithm_power':1000},'kappa':typed['KAPPA'],'tested':typed['TESTED'],'reserve':'1/1000000000','root_bracket':['.00302728824993','.00302728824994'],'ordinary_BIT':bit}
 r=evaluate(inv['histograms']['productive'],inv['histograms']['paid'],config)
 need((r['paid_count'],r['productive_count'],r['rank_mass_surplus'])==(64116,10784,752),'literal complete counts disagree')
 need((r['H'],r['j'])==(31385200000000,44836),'finite compiler mismatch')
 need(set(inventory['strict_keys'])==set(r['outer']['strict_checks']) and set(inventory['functional_keys'])==set(r['outer']['functional_checks']),'uncovered current-source predicate inventory')
 controls={};word=read(CAP/PKG/'WORD.json.gz');base=read(H/'frozen-canonical/research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz');c=base['canonical']
 mutant=json.loads((H/'INVOICE-v1.json').read_bytes());mutant['histograms']['productive']['9']+=16
 try:need(sha256(json.dumps(mutant).encode()).hexdigest()==INVOICE_SHA,'unearned productive-credit invoice hash mismatch')
 except ValueError as e:controls['unearned_16_rank9_helper_credit']=str(e)
 else:raise ValueError('unearned credit accepted')
 row=next(x for x in root['rows'] if x['path']==PKG+'/WORD.json.gz')
 try:checked(row,(CAP/row['path']).read_bytes()+b'\0')
 except ValueError as e:controls['source_word_mutation']=str(e)
 else:raise ValueError('source mutation accepted')
 bad=list(word['forward_body']);hit=next(i for i,e in enumerate(bad) if e[0]=='scalar' and e[1][0]=='clear');del bad[hit]
 try:need(bad==transpose_records(word['backward'],c),'transposed COPY/CLEAR chronology mismatch')
 except ValueError as e:controls['missing_transposed_clear']=str(e)
 else:raise ValueError('missing clear accepted')
 bad=[['transpose_paid_source',next(e[1] for e in word['forward_body'] if e[0]=='transpose_paid_source'),100]]
 try:local_paid(bad,c,word['backward'])
 except ValueError as e:controls['wrong_transposed_paid_rank']=str(e)
 else:raise ValueError('wrong paid rank accepted')
 for key,patch in [('unsupported_model',{'model':'unproved_transpose_model'}),('unsupported_cutoff',{'tuple':dict(config['tuple'],cutoff=22)})]:
  try:evaluate(inv['histograms']['productive'],inv['histograms']['paid'],dict(config,**patch))
  except ValueError as e:controls[key]=str(e)
  else:raise ValueError('unsupported source domain accepted')
 # Compare with frozen independently admitted predecessors without using them
 # to produce the new invoice, and prove the claimed extra changed-profile gain.
 oldpath=H.parents[2]/'outputs/price-plane-swarm-20261024/02-census/INVOICE-v1.json';need(sha(oldpath)=='7c6dfe167dd83cc48b32743e6bcfa76e3420ccd5be997c935b02a99e3636f44e','predecessor independent invoice changed');old=read(oldpath)
 delta={name:{str(k):int(inv['histograms'][name].get(str(k),0))-int(old['histograms'][name].get(str(k),0)) for k in set(map(int,inv['histograms'][name]))|set(map(int,old['histograms'][name]))} for name in ['paid','productive']}
 delta={name:{k:v for k,v in z.items() if v} for name,z in delta.items()}
 need(delta=={'paid':{'1':-16,'8':-16},'productive':{'9':-16}},'changed profile delta mismatch')
 r.update(schema='independent-exact-transpose-funding/1',status='PASS_EXACT_ARITHMETIC_BOUND_TO_LITERAL_TRANSPOSE_INVOICE',candidate=inv['candidate'],invoice={'path':str(H/'INVOICE-v1.json'),'sha256':INVOICE_SHA,'ordinary':inv['ordinary']},source={'root_manifest_sha256':inv['authentication']['root_manifest_sha256'],'candidate_rows_rechecked':len(root['rows']),'price_sha256':sha(CAP/PKG/'price.py'),'typed_constants':typed,'canonical_dependencies':inv['authentication']['canonical']},source_predicate_inventory=inventory,config=config,source_binding_controls=controls,delta_from_independently_admitted_5383=delta,gain_over_5383=str(Q(r['kappa'])-Q('.00302666')),gain_over_5387=str(Q(r['kappa'])-Q('.003026674765')),engine_sha256=sha(H/'exact_engine.py'),invoice_runner_sha256=sha(H/'invoice.py'),funding_runner_sha256=sha(Path(__file__)),independent_invoice_bound=True,source_capsule_bound=True,finite_template_gate_bound=False,endpoint_funded=False,scientific_scope='Independent literal complete invoice and exact profile/compiler/BIT/outer arithmetic. Physical transposition/all641 columns/native phases and fresh expanded precision/stock/tape source applicability remain separate01/03 gates; no author replay or unconditional theorem.',external_gate_requirements=['01 physical transposition/all641/native phases','03 fresh expanded constants/stock/tape applicability','root decision and09 serial registered replay/publication'])
 raw=(json.dumps(r,indent=2,sort_keys=True)+'\n').encode();outp.write_bytes(raw);outp.chmod(0o444);(H/'FUNDING-v1.sha256').write_text(sha(outp)+'  FUNDING-v1.json\n')
 print(json.dumps({'status':r['status'],'sha256':sha(outp),'kappa':r['kappa'],'root':r['root']['bracket'],'seconds':r['seconds'],'endpoint_funded':False}))
if __name__=='__main__':run()
