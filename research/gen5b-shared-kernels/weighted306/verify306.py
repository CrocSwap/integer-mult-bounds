"""Focused PR306 aggregate: inherited306 raw-crossing admission is explicit."""
from pathlib import Path
import argparse,contextlib,hashlib,io,json,os,time

REVIEW_DATA={}

def run(check=False):
 import context306 as c
 import price_reorder as price,check_transport,review_finite,check_chart_transport
 import check_bridge as oldbridge,check_scalar_bounds as oldnorm,check_candidate_charts
 import witness
 started=time.monotonic();c.OUTPUT.mkdir(parents=True,exist_ok=True)
 c.verify_package();sourcecount=c.verify_new();oldcount=c.oldsource.verify();depcount=c.verify_dependencies()
 baseline,candidate,summary=price.run()
 oldbridge.configure('156');b=oldbridge.run();n=oldnorm.run()
 bridge=check_transport.run(b,n)
 (c.OUTPUT/'prior156-bridge.json').write_text(json.dumps(b,indent=2)+'\n')
 (c.OUTPUT/'bridge-full.json').write_text(json.dumps(bridge,indent=2)+'\n')
 assert bridge['local_histogram_delta']==candidate['selected_kernel_delta']
 assert bridge['selected_pivots']==156 and bridge['selected_distinct_donors']==197
 assert bridge['setup_adds']==2545
 prior=json.loads((c.BASE/'certificates/case156.json').read_text())
 for key in ['literal_stock','calls','rank_mass','residual_census','packing_patterns']:
  assert json.loads(json.dumps(price.old.ae.serial(candidate[key])))==prior[key],key
 assert prior['role_bank_binding']['assignments_per_stage']==925440
 chart=check_candidate_charts.run(witness.write_case('156'),b,candidate['literal_stock'])
 chartpath=c.OUTPUT/'prior156-charts.json';chartpath.write_text(json.dumps(price.old.ae.serial(chart),separators=(',',':'))+'\n')
 assert hashlib.sha256(chartpath.read_bytes()).hexdigest()==prior['changed_chart_receipt_sha256']
 config=dict(old_source=str(c.oldsource.SOURCE),new_source=str(c.INPUTS),new_input_manifest=str(c.HERE/'inputs.json'),
  pricing_dir=str(c.OUTPUT),prior_case=str(c.BASE/'certificates/case156.json'),prior_charts=str(chartpath),
  witness=str(witness.write_case('156')),output_dir=str(c.OUTPUT))
 (c.OUTPUT/'review-config.json').write_text(json.dumps(config,indent=2)+'\n')
 charts=check_chart_transport.run(config)
 with contextlib.redirect_stdout(io.StringIO()):finite=review_finite.run(config)
 assert finite['candidate156']['displayed_finite_coefficient']==90417469526202901
 bound=dict(status='PASS_PR306_PLUS156_UNDER_EXPLICIT_INHERITED_RAW_CROSSING_CONTRACT',source_head=c.HEAD,
  kappa=candidate['assembly']['kappa_decimal'],baseline_kappa=baseline['assembly']['kappa_decimal'],
  stock=candidate['literal_stock'],calls=candidate['calls'],rank_mass=candidate['rank_mass'],
  candidate_sha256=bridge['candidate_sha256'],original156_sha256=prior['candidate_sha256'],
  kernel_delta=candidate['selected_kernel_delta'],reorder_delta=baseline['local_reorder_delta'],
  first_quotient_charts=281,role_chart_uses=706,bank_assignments_per_stage=925440,bank_stages=5,
  inherited_bank_assignment_digest=prior['role_bank_binding']['assignment_sha256'],
  norm=bridge['unsigned_norm_transport'],displayed_finite_coefficient=finite['candidate156']['displayed_finite_coefficient'],
  assembly_constraints=47,inherited_reorder_contract=bridge['inherited_reorder_contract'],
  scope='Changed156 composition is checked. Pinned PR306 raw crossing/full-word admission remains inherited; all239 raw crossings are not independently replayed. Compiler, prime/recovery, complex and all-size interfaces remain conditional. Displayed finite coefficient is not the unknown full primitive constant. No optimality claim.')
 def stable(x):
  if isinstance(x,dict):return {k:stable(v)for k,v in x.items()if k not in ('seconds',)}
  if isinstance(x,list):return [stable(v)for v in x]
  return x
 def save(name,value):
  value=json.loads(json.dumps(price.old.ae.serial(value)));(c.OUTPUT/(name+'.json')).write_text(json.dumps(value,indent=2)+'\n')
  expected=c.HERE/'certificates'/(name+'.json')
  if check:assert stable(value)==json.loads(expected.read_text()),('Frozen receipt differs',name)
  return value
 save('baseline',baseline)
 compactbridge={k:v for k,v in bridge.items()if k not in ('selected_paths','seconds')}
 save('transport',compactbridge);save('finite',finite);save('charts',charts);save('combined156',bound)
 result=dict(status='PASS_FOCUSED_PORTABLE_PR306_AGGREGATE',new_source_files=sourcecount,inherited_source_files=oldcount,
  unchanged_dependency_files=depcount,receipts=5,kappa=bound['kappa'],seconds=time.monotonic()-started,
  inherited306_raw_crossing_admission=True,all239_crossings_independently_replayed=False)
 REVIEW_DATA.update(baseline=baseline,candidate=candidate,summary=summary,bridge=bridge,prior_bridge=b,config=config)
 (c.OUTPUT/'aggregate.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
 if not __debug__:raise RuntimeError('Assertions required')
 p=argparse.ArgumentParser();p.add_argument('--inputs',type=Path);p.add_argument('--prior-inputs',type=Path);p.add_argument('--output',type=Path);p.add_argument('--check',action='store_true');a=p.parse_args()
 if a.inputs:os.environ['PR306_INPUTS']=str(a.inputs.resolve())
 if a.prior_inputs:os.environ['PR305_INPUTS']=str(a.prior_inputs.resolve())
 if a.output:
  os.environ['PR306_OUTPUTS']=str(a.output.resolve());os.environ['PR305_OUTPUTS']=str(a.output.resolve()/'prior156')
 print(json.dumps(run(a.check),indent=2))
