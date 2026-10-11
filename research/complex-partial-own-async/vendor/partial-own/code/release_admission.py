"""Bind successful finite proof objects, rather than accepting process exits alone.
OpenAI Codex; stdlib-only release gate. Usage: OUTPUT_ROOT REPORT.json
"""
from pathlib import Path
import gzip,hashlib,json,sys
if not __debug__:raise RuntimeError('assertions must remain enabled')
O,R=map(Path,sys.argv[1:]);V=O/'retimed/gauge80-kernel42';S=V/'split-centres'
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def good(p,status):
 z=read(p);assert z['status']==status,(p,z.get('status'));return z
source=good(O/'complex/RECEIPT.json','PASS_FULL_COMPLEX_GAUGE_KERNEL_COMPOSITION')
der=good(V/'RECEIPT.json','PASS_FRESH_PARTIAL_OWN_KERNEL_RETIMED_COMPLEX_WORD')
for p,h in der['artifacts'].items():assert sha(V/p)==h,p
assert all(z['exit_code']==0 for z in der['steps'])
assert der['source_full_word_sha256']==sha(O/'complex/gauge80-kernel42/split-centres/FULL-WORD.json.gz')
assert der['retimed_full_word_sha256']==sha(S/'FULL-WORD.json.gz')=='73afd6e5579644b131e5b1adef9a48b622affb6c17f26bad0eac2fcf086637ac'
assert der['unretimed_full_word_sha256']==sha(V/'unretimed/split-centres/FULL-WORD.json.gz')=='ae74a5368c90d38a4164aaa6ab60bde14e0500241730a465a4d157542aba3079'
source_root=Path(__file__).resolve().parent.parent
for key,path in [('frame_map_sha256','data/RETIME-FRAMES.json.gz'),('selection_sha256','data/KERNEL-SELECTION.json'),('owner_map_sha256','data/COLORED-OWNERS.json.gz'),('constructor_sha256','code/construct_partial.py')]:
 assert der[key]==sha(source_root/path),key
for name in ['PROTOTYPE.json','PACKET-PROGRAMS.json.gz']:
 assert der['fresh_hamming_inputs'][name]==sha(O/'complex/gauge80-kernel42/work/complex-network/hamming'/name)
local=read(S/'LOCAL-CHECKS.json')
for ori,z in local.items():
 assert ori in ['forward','backward'] and z['all_columns']==800
 assert z['private_centers_cleared'] and z['private_coefficient_stream_cleared_after_each_macro']
assert set(local)=={'forward','backward'}
good(V/'LEMMA-A.json','PASS_RESIDUAL_WRAPPERS_ARE_EXACT')
good(S/'INDEPENDENT-REPLAY.json','PASS_INDEPENDENT_NEW_STRUCTURAL_IR_REPLAY')
a=good(O/'partial-algebra/ALGEBRA.json','PASS_INDEPENDENT_PARTIAL_OWN_BASES_KERNEL_RELATIONS_AND_ALL_DIRT')
assert a['all_kernel_relations_checked']==84 and a['scalar_columns_each_orientation']==800
assert a['entrance_rank']==190 and a['entering_helpers']==164
assert a['retiming']['full_prelude_including_frames_unchanged'] and a['retiming']['full_prelude_events']==671
for path,h in a['inputs'].items():assert sha(Path(path))==h,path
for name,status in [('RETIME-FRAME-REVIEW.json','PASS_INDEPENDENT_FIXED_SCALAR_RETIMING_AND_BOTH_ACTUAL_FRAME_LEDGERS'),('PARTIAL-FRAME-REVIEW.json','PASS_CHANGED_SCALAR_WORD_RAW_BINDING_AND_BOTH_REFLECTED_LEDGERS')]:
 z=good(O/name,status);assert len(z['negative_controls_rejected'])==12
 for path,h in z.get('inputs',z.get('bindings',{})).items():assert sha(Path(path))==h,path
 for ori in ['forward','backward']:assert z['emitted_ledgers'][ori]['profile']==local[ori]['paid_profile']

def no_failures(z):
 if isinstance(z,dict):
  for k,v in z.items():
   if k in ['failures','n_label_violations','scalar_violations']:assert v in [0,[]],(k,v)
   else:no_failures(v)
 elif isinstance(z,list):
  for v in z:no_failures(v)
for directory in ['guarded','retimed-guarded']:
 for typ,script in [('INSTANCES','lg_instances'),('E2E','lg_e2e')]:
  result=O/directory/(typ+'-gauge80-kernel42.json');z=read(result)
  if typ=='E2E':assert z['status']=='PASS'
  else:
   for section in ['I-tr','I-comp','I-centre','I-helper']:assert z[section]['failures']==[]
  no_failures(z)
  g=read(O/directory/('PREOP-GUARDS-'+script+'.json'))
  assert g['identity_assertions_passed'] and g['maximum_proved_numerator_bits']<63
  assert g['checked_result_sha256']==sha(result)
lemma=read(V/'lemmaG/LEMMA-G-CHECK.json');no_failures(lemma)
assert lemma['calls']['ok'] and lemma['calls']['n']==72
assert lemma['end_to_end']['status']=='PASS'
mut=good(V/'lemmaG/MUTANT-ADAPTER-RECEIPT.json','PASS_ALL_14_RETIMED_LEMMA_G_NECESSITY_CONTROLS')
controls=read(V/'lemmaG/MUTANTS.json');assert len(controls)==14 and all(z['rejected']for z in controls)
assert mut['mutants_sha256']==sha(V/'lemmaG/MUTANTS.json')
for folder in [V/'hosted',O/'hosted']:
 assert read(folder/'GLOBAL-TEMPLATE.json.gz')==read(O/'hosted/GLOBAL-TEMPLATE.json.gz')
 assert read(folder/'ACTUAL-SIGMAS.json.gz')==read(O/'hosted/ACTUAL-SIGMAS.json.gz')
host=good(O/'HOSTING-AUDIT.json','PASS_INDEPENDENT_POOLED_WHOLE_OWNER_CONTROLLER_AND_SPECTATORS')
assert len(host['mutations_rejected'])==18 and host['one_owner_per_complete_invocation']
assert host['complete_invocations']==72 and host['helper_busy_family_window_checks']==40320
ad=good(O/'admission/ADMISSION.json','PASS_COMPLETE_POOLED_COMPLEX_FINITE_ADMISSION')
co=good(O/'COMPOSITION-REVIEW.json','PASS_INDEPENDENT_FRESH_SUPPLIER_COMPOSITION_GATE')
assert co['strict_outer_constraints']==47 and len(co['outer_controls'])==4
assert ad['kappa']==co['kappa']==read(O/'EXACT-MATH.json')['kappa']
report=dict(status='PASS_ALL_RELEASE_PROOF_OBJECTS_AND_FRESH_BINDINGS',word_sha256=sha(S/'FULL-WORD.json.gz'),derivative_receipt_sha256=sha(V/'RECEIPT.json'),physical_template_sha256=host['complex_template_sha256'],guarded_result_statuses_checked=True,source_and_derivative_bytes_bound=True,all800_dirty_columns=True,both_reflected_ledgers=True,whole_owners=40320,necessity_controls=14,controller_controls=18,strict_outer_constraints=47,kappa=co['kappa'])
R.write_text(json.dumps(report,indent=2)+'\n');print(report['status'])
