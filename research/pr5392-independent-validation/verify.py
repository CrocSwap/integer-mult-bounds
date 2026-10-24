#!/usr/bin/env python3
"""Independent exact-head PR5392 package; standard-library, Git/network free.

Chris R / Clear1nsight, substantial OpenAI Codex assistance; Apache-2.0.
Ali Romman and all original construction/physical/analytic notices retained.
"""
from pathlib import Path,PurePosixPath
import argparse,base64,gzip,hashlib,json,os,shutil,subprocess,sys,tempfile,time
HERE=Path(__file__).resolve().parent;F=HERE/'frozen';ROOT=F/'workspace';D=ROOT/'outputs/price-plane-5392-admission-20261024';C=D/'09-cold';CAP=C/'capsule-5392-v1';OLD=ROOT/'outputs/price-plane-swarm-20261024'
HEAD='329b2ff35d2994b11abbb59f770d12da75c494ac';MAIN='1ec1119972c9aefe42525172d07b332fcff81cb4';PARENT='5eb314069417db1f4305430b6b14f20e9251e509'
ASSUMPTIONS=['native_all_columns','owned_erasure','compiler','precision_tape','analytic_recovery']
PACKET_SHA256='4e1262a64705be34397f6300a448172cca10354b24e65b9f2280e1d0822cf9a6'
def need(v,why):
 if not v:raise ValueError(why)
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def oid(kind,b):return hashlib.sha1(kind.encode()+b' '+str(len(b)).encode()+b'\0'+b).hexdigest()
def safe(root,name):
 p=PurePosixPath(name);need(not p.is_absolute() and str(p)==name and '..' not in p.parts,'unsafe packet path')
 q=root
 for part in p.parts:q=q/part;need(not q.is_symlink(),'symbolic packet path')
 need(q.is_file(),'missing packet file '+name);return q
def inventory(root,manifest):
 seen=set()
 for row in manifest['files']:
  n=row['path'];need(n not in seen,'duplicate packet path');seen.add(n);b=safe(root,n).read_bytes()
  need(len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256'],'immutable byte guard '+n)
 actual={p.relative_to(root).as_posix() for p in (root/'frozen').rglob('*') if p.is_file()}
 need(actual=={n for n in seen if n.startswith('frozen/')},'complete frozen inventory')
 return len(seen)
def historical(name):
 a=read(HERE/'PATH-ALIASES.json');prefix=a['workspace_prefix']+'/'
 if name.startswith(prefix):name=name[len(prefix):]
 need(name in a['paths'],'undeclared historical path '+name);return safe(HERE,a['paths'][name])
def launch(argv,cwd,commands,timeout=150):
 env=dict(os.environ)
 for key in ['PYTHONOPTIMIZE','PYTHONPATH','PYTHONINSPECT']:env.pop(key,None)
 env['PYTHONPYCACHEPREFIX']=str(cwd/('private-bytecode-'+str(len(commands))))
 args=[sys.executable]+(['-O'] if sys.flags.optimize else [])+['-B']+list(map(str,argv));start=time.monotonic()
 q=subprocess.run(args,cwd=cwd,env=env,capture_output=True,text=True,timeout=timeout)
 commands.append(dict(argv=args,cwd=str(cwd),exit=q.returncode,seconds=round(time.monotonic()-start,6),environment=dict(PYTHONOPTIMIZE='removed',PYTHONPATH='removed',PYTHONPYCACHEPREFIX=env['PYTHONPYCACHEPREFIX']),stdout=q.stdout,stderr=q.stderr))
 need(q.returncode==0,'independent subprocess failed '+str(args)+': '+q.stderr[-5000:]);return q.stdout

def raw_objects(proof,key='commit_and_tree_objects'):
 out={}
 for obj,r in proof[key].items():
  b=base64.b64decode(r['base64'],validate=True);need(len(b)==r['bytes'] and oid(r['kind'],b)==obj,'raw object hash '+obj);out[obj]=(r['kind'],b)
 return out
def tree_entries(b):
 rows={};i=0
 while i<len(b):
  j=b.index(b' ',i);k=b.index(b'\0',j);n=b[j+1:k].decode();need(n not in rows and k+21<=len(b),'raw tree shape');rows[n]=(b[i:j].decode(),b[k+1:k+21].hex());i=k+21
 need(i==len(b),'raw tree boundary');return rows
def raw_path(objects,row,local):
 kind,b=objects[row['source_commit']];need(kind=='commit','source commit kind');tree=b.splitlines()[0].split()[1].decode();parts=row['path'].split('/')
 need(len(parts)==len(row['tree_chain']) and all(p not in ('','.','..') for p in parts),'source path shape')
 for i,part in enumerate(parts):
  need(tree==row['tree_chain'][i],'raw tree chain');kind,b=objects[tree];need(kind=='tree','tree kind');mode,obj=tree_entries(b)[part]
  if i+1<len(parts):need(mode=='40000','source directory mode');tree=obj
  else:need(mode in ('100644','100755') and obj==row['git_blob'],'source terminal object/mode')
 b=local.read_bytes();need(oid('blob',b)==obj and hashlib.sha256(b).hexdigest()==row['sha256'],'raw source path bytes '+row['path'])

def source_integrity():
 commands=[]
 with tempfile.TemporaryDirectory(prefix='pr5392-source-') as td:
  tmp=Path(td)
  primary=json.loads(launch([C/'verify_merkle_provenance.py','--capsule',CAP,'--receipt',C/'capsule-5392-v1-MERKLE-PROVENANCE.json'],tmp,commands,20))
  origins=json.loads(launch([C/'verify_origin_supplement.py','--capsule',CAP,'--receipt',C/'ORIGIN-SUPPLEMENT-v1.json'],tmp,commands,20))
 proof=read(C/'capsule-5392-v1-MERKLE-PROVENANCE.json');objects=raw_objects(proof)
 kind,b=objects[HEAD];need(kind=='commit' and [s.split()[1].decode() for s in b.splitlines() if s.startswith(b'parent ')]==[PARENT],'actual parent5eb distinct from canonical')
 need(primary['rows']==54 and origins['rows']==7,'complete publication and original-origin source paths')
 # All23 initial root files are exact aliases of authenticated HEAD blobs.
 m=read(D/'source-capsule/ROOT-MANIFEST.json');need(m['head']==HEAD and len(m['rows'])==23,'original root source contract')
 rows={r['path']:r for r in proof['rows'] if r['source_commit']==HEAD and r['capsule_path'].startswith('snapshot/')}
 for r in m['rows']:
  r2=rows[r['path']];need(r['git_blob']==r2['git_blob'] and r['sha256']==r2['sha256'],'root/closed source identity')
  raw_path(objects,r2,D/'source-capsule'/r['path'])
 # Authenticate exact original #5383 WORD independently of the new commit's
 # claim of source equivalence. Other old proof rows are not asserted present.
 oldproof=read(OLD/'09-capsule-cold/capsule-v1-MERKLE-PROVENANCE.json');oo=raw_objects(oldproof)
 selected=[r for r in oldproof['rows'] if r['path']=='research/kappa-joint-relations-20261023/WORD.json.gz' and r['capsule_path'].startswith('snapshot/')]
 need(len(selected)==1,'one exact original backward word');raw_path(oo,selected[0],OLD/'09-capsule-cold/capsule-v1'/selected[0]['capsule_path'])
 precision=read(HERE/'PRECISION-SOURCE-PROOF.json');po=raw_objects(precision)
 for row in precision['rows']:raw_path(po,row,OLD/row['capsule_path'])
 return dict(primary=primary,original_vendor_origins=origins,initial_root_aliases=23,original_backward_word_paths=1,canonical_precision_proof_paths=len(precision['rows']),actual_parent=PARENT,canonical_ancestor=MAIN,metadata_commands=commands)

def static_join():
 p=read(D/'01-physical/PHYSICAL-RECEIPT.json');erratum=read(D/'01-physical/SCOPE-ERRATUM-RECEIPT.json');closure=read(D/'03-closure/CLOSURE-v1.json');r=read(D/'04-funding/FUNDING-v2.json')
 need(erratum['status']=='APPEND_ONLY_FORMAL_ROW_SCOPE_CORRECTION' and erratum['candidate_head']==HEAD,'mandatory formal-row scope erratum')
 for name,h in erratum['bound_original_files'].items():need(sha(D/'01-physical'/name)==h,'scope erratum original binding '+name)
 need(sha(D/'01-physical/SCOPE-ERRATUM.md')==erratum['erratum_markdown_sha256'],'scope erratum prose')
 need(erratum['formal_nonzero_row_count']==8 and not erratum['actual_specialization_nonzero_claim_established'] and not erratum['surjectivity_claim_established'] and not erratum['reverse_zero_premise_required'] and erratum['arbitrary_bridge_substitution_cancellation_unchanged'],'formal versus physical row scope')
 need(p['head']==HEAD and p['status']=='PASS_FRESH_INDEPENDENT_PHYSICAL_OWNED_TRANSPOSE','full independent physical gate')
 for key,name in [('engine_sha256','exact_engine.py'),('invoice_runner_sha256','invoice.py'),('funding_runner_sha256','funding.py')]:need(sha(D/'04-funding'/name)==r[key],'exact independent executable binding '+name)
 need(p['same_five_assumptions']==ASSUMPTIONS and closure['retained_assumptions']==ASSUMPTIONS and not closure['new_candidate_specific_assumptions'] and r['assumptions']==ASSUMPTIONS,'same five source premises')
 need(p['coverage']['all_entry_columns']==641 and p['coverage']['arbitrary_owned']==17 and p['coverage']['arbitrary_full_operator_bridge_cancellation']==8,'universal complete owned endpoint')
 need(p['native5369_review']['independent_endpoint_relies_on_four_width_theorem'] is False,'universal endpoint not finite-cutoff extrapolation')
 for name,h in p['receipts'].items():need(sha(D/'01-physical'/name)==h,'physical complete receipt '+name)
 need(sha(OLD/'01-physical/PHYSICAL-RECEIPT.json')==p['predecessor5383_physical_receipt_sha256'],'unchanged backward physical premise')
 need(closure['status']=='PASS_SAME_PREMISE_CONSTRUCTIVE_FINITE_TEMPLATE_SPECIALIZATION','fresh closure')
 for name,h in closure['dependencies_sha256'].items():need(sha(historical(name))==h,'fresh closure dependency '+name)
 for name,h in closure['source_proof_sha256'].items():need(sha(OLD/'09-capsule-cold/supplement-03-v1/snapshot'/name)==h,'canonical closure proof')
 for name,h in r['closure_dependencies_sha256'].items():need(sha(historical(name))==h,'funded gate dependency '+name)
 for name,row in r['source']['canonical_dependencies'].items():
  path=historical(row['path']);need(sha(path)==row['sha256'] and oid('blob',path.read_bytes())==row['git_blob'],'independent canonical fixture '+name)
 need(r['candidate']['head']==HEAD and r['endpoint_funded'] and r['complete_bill_ready'] and r['status']=='FUNDED_CONDITIONAL_INDEPENDENT_STATIC_ADMISSION','complete independent funded point')
 need(closure['expanded_constants']['N']==r['N'] and closure['expanded_constants']['old_equal_N_implies_old_constants'] is False,'new expanded constants despite same N')
 need(closure['ordinary']['raw_local_owned_banks']==306 and not closure['ordinary']['raw_upper_used_as_expanded_cap'],'new306 bank prescription')
 need(closure['stocks']['simultaneous_rule']=='PRODUCT, never maximum','full simultaneous stock product')
 return dict(status=r['status'],kappa=r['kappa'],N=r['N'],literal_paid=r['paid_count'],literal_productive=r['productive_count'],framework_assumptions=ASSUMPTIONS,phase_classes=p['coverage']['paid_transpose_classes'],native_classes=p['coverage']['native_transpose_classes'],old_equal_N_constants_reused=False)

def frozen_cold():
 b=read(C/'BOUNDED-REGISTERED-RUN.json');v=read(C/'VALIDATION.json')
 need(b['status']=='PASS_COMPLETE_REGISTERED_NORMAL_AND_OPTIMIZED' and b['candidate_head']==HEAD and b['exit']==0 and b['resource_stop'] is None and not b['scientific_or_git_bytes_changed'],'actual complete registered author pair')
 pre=read(C/'PRE-RUN-HASHES.json');need(pre==read(C/'POST-RUN-HASHES.json') and len(pre)==b['hash_inventory_files'],'complete actual cold source immutability')
 need(sha(C/'REGISTERED-COLD.stdout.log')==b['stdout_sha256'] and sha(C/'REGISTERED-COLD.stderr.log')==b['stderr_sha256'],'complete cold stdout/stderr')
 need((C/'REGISTERED-COLD.stderr.log').stat().st_size==0,'empty cold stderr')
 expected=read(CAP/'snapshot/research/native-transpose-owned/RESULT.json')['status'];log=(C/'REGISTERED-COLD.stdout.log').read_text();need(log.count(expected)==2 and 'PASS_REGISTERED_RESEARCH_PACKAGE' in log,'both actual author modes')
 grant=read(C/'ROOT-HEAVY-GRANT.json');need(grant['authorized'] and grant['candidate_head']==HEAD and sha(C/'ROOT-HEAVY-GRANT.json')==b['root_grant_sha256'],'explicit root cold grant')
 for row in grant['substantive_gate_receipts']+grant.get('provenance_receipts',[]):need(sha(historical(row['path']))==row['sha256'],'actual cold granted source/gate '+row['path'])
 # v is the final source owner's complete classification/evidence record, also
 # frozen by PACKET; the bounded execution and full raw log are independently
 # checked above rather than accepting a quoted PASS classification alone.
 need(v['candidate']['head']==HEAD and v['status']=='PASS_STATIC_FUNDED_ADMISSION_AND_ONE_ACTUAL_REGISTERED_NORMAL_OPTIMIZED_PAIR','final validation exact candidate')
 correction=read(C/'BOUNDED-REGISTERED-RUN-CORRECTION.json');closed=C/'capsule-5392-v2/IMMUTABLE-MANIFEST.json';actual=sha(closed)
 need(correction['status']=='PASS_ACTUAL_EXECUTION_PRESERVED_WITH_CORRECTED_CAPSULE_LABEL' and correction['raw_receipt_sha256']==sha(C/'BOUNDED-REGISTERED-RUN.json'),'explicit raw execution metadata correction')
 need(correction['field']=='capsule_manifest_sha256' and b['capsule_manifest_sha256']==correction['incorrect_recorded_value'] and b['capsule_manifest_sha256']!=actual,'preserve actual mislabeled raw receipt field')
 need(correction['correct_effective_value']==actual==grant['capsule_manifest_sha256']==pre['IMMUTABLE-MANIFEST.json']==correction['capsule_manifest_pre_sha256']==correction['capsule_manifest_post_sha256']==correction['capsule_manifest_current_sha256'],'actual manifest grant/pre/post/sidecar binding')
 need(correction['root_grant_sha256']==sha(C/'ROOT-HEAVY-GRANT.json') and correction['exact_executed_guard_sha256']==sha(C/'run_guarded_registered.py'),'executed raw guard/grant identity')
 need(correction['before_hash_inventory_sha256']==sha(C/'PRE-RUN-HASHES.json') and correction['after_hash_inventory_sha256']==sha(C/'POST-RUN-HASHES.json') and correction['raw_stdout_sha256']==sha(C/'REGISTERED-COLD.stdout.log'),'complete correction evidence')
 need(not correction['source_changed'] and not correction['execution_repeated'] and correction['grant_validation_before_loop'],'metadata-only correction preserves execution')
 need(read(closed)['rows']==read(CAP/'IMMUTABLE-MANIFEST.json')['rows'],'closed and scientific capsule row equality')
 for row in read(closed)['rows']:need(pre[row['capsule_path']]==row['sha256']==sha(CAP/row['capsule_path']),'executed/current closed source payload '+row['path'])
 need(grant['guard_sha256']==sha(C/'run_guarded_registered.py'),'actual grant executed guard binding')
 effective=v['actual_registered_replay_effective_metadata']
 for key,value in effective.items():
  if key not in ('capsule_manifest_sha256','mandatory_metadata_correction'):need(value==b[key],'effective cold/raw field mismatch '+key)
 need(effective['capsule_manifest_sha256']==actual,'effective corrected cold manifest label')
 need(sha(C/'BOUNDED-REGISTERED-RUN-CORRECTION.json')==v['mandatory_corrections']['raw_execution_metadata']['sha256'],'final classification consumes explicit correction')
 need(sha(D/'01-physical/SCOPE-ERRATUM-RECEIPT.json')==v['mandatory_corrections']['physical_diagnostic_scope']['sha256'],'final classification consumes formal-row erratum')
 need(not v['formal_ghost_row_scope']['actual_physical_nonzero_established'] and not v['formal_ghost_row_scope']['physical_surjectivity_established'],'final formal-row scope')
 for name,record in v['fresh_artifact_equality']['artifacts'].items():
  path=CAP/'snapshot/research/native-transpose-owned'/name;raw=path.read_bytes();need(len(raw)==record['bytes'] and hashlib.sha256(raw).hexdigest()==record['sha256'],'four actual cold artifact bytes '+name)
  if 'decompressed_sha256' in record:
   payload=gzip.decompress(raw);need(len(payload)==record['decompressed_bytes'] and hashlib.sha256(payload).hexdigest()==record['decompressed_sha256'],'actual cold canonical payload '+name)
 return dict(status=b['status'],seconds=b['seconds'],peak_sampled_descendant_rss_kib=b['peak_sampled_descendant_rss_kib'],original_files_unchanged=len(pre),freshly_rerun_by_this_package=False,full_validation_receipt_sha256=sha(C/'VALIDATION.json'),raw_receipt_sha256=sha(C/'BOUNDED-REGISTERED-RUN.json'),raw_manifest_label_preserved=b['capsule_manifest_sha256'],actual_closed_manifest_sha256=actual,explicit_metadata_correction_sha256=sha(C/'BOUNDED-REGISTERED-RUN-CORRECTION.json'),four_artifact_equalities_authenticated=True)

def stable(d):return {k:v for k,v in d.items() if k!='seconds'}
def run_fresh(tmp):
 shutil.copytree(F/'workspace',tmp/'workspace');w=tmp/'workspace';d=w/'outputs/price-plane-5392-admission-20261024';commands=[];results={}
 # The entire candidate and predecessor source adapters are read-only; only
 # independent reviewer output receipts/chronology in private folders can change.
 for folder in [d/'source-capsule',d/'04-funding/frozen-canonical',w/'outputs/price-plane-swarm-20261024']:
  for p in folder.rglob('*'):
   if p.is_file():p.chmod(0o444)
 (d/'04-funding/frozen-owned-source-WORD.json.gz').chmod(0o444)
 for p in d.rglob('*.py'):p.chmod(0o444)
 for name,script in [('word','check_word.py'),('phase','check_phases.py'),('extra','check_extra_controls.py')]:
  receipt={'word':'WORD-RECEIPT.json','phase':'PHASE-RECEIPT.json','extra':'CONTROL-RECEIPT.json'}[name]
  launch([HERE/'exec_frozen.py',d/'01-physical'/script],tmp,commands)
  fresh=read(d/'01-physical'/receipt);need(stable(fresh)==stable(read(D/'01-physical'/receipt)),'complete independent '+name+' receipt')
  results[name]=fresh
 launch([HERE/'exec_frozen.py',d/'03-closure/check_closure.py'],tmp,commands)
 fresh=read(d/'03-closure/LIGHT-ARITHMETIC-v1.json');need(stable(fresh)==stable(read(D/'03-closure/LIGHT-ARITHMETIC-v1.json')),'complete changed-word scalar/owned grammar receipt');results['light_closure']=fresh
 results['literal_invoice']=json.loads(launch([HERE/'replay_invoice.py',d/'04-funding'],tmp,commands))
 results['exact_funding']=json.loads(launch([HERE/'replay_exact.py',d/'04-funding'],tmp,commands))
 root=results['exact_funding']['result']['root'];need(root['derivative_upper'].startswith('-') and root['remaining_moment_upper'].startswith('-'),'actual fixed-profile ceiling proof')
 results['commands']=commands;return results

def source_control(manifest,tmp):
 row=next(r for r in manifest['files'] if r['path'].endswith('source-capsule/research/native-transpose-owned/WORD.json.gz'))
 p=tmp/row['path'];p.parent.mkdir(parents=True);p.write_bytes((HERE/row['path']).read_bytes()+b'changed')
 try:inventory(tmp,dict(files=[row]))
 except ValueError as e:need('immutable byte guard' in str(e),'source control wrong failure')
 else:raise ValueError('changed actual source WORD accepted')
 return 'Actual changed WORD bytes rejected by the packet guard before evaluation.'
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--integrity-only',action='store_true');a=ap.parse_args();start=time.monotonic()
 need(sha(HERE/'PACKET.json')==PACKET_SHA256,'immutable packet manifest');packet=read(HERE/'PACKET.json');count=inventory(HERE,packet)
 result=dict(proof_scope={'eight_reverse_cuts':'Formal nonempty free-group rows only; no actual physical-specialization nonzero or surjectivity claim.','endpoint':'All bridge-dependent terms cancel for arbitrary substitutions; no reverse-zero premise used.','historical_receipt_fields':'Exact historical field names remain unchanged; mandatory scope erratum governs interpretation.'},status='PASS_PR5392_INDEPENDENT_INTEGRITY',head=HEAD,canonical_base=MAIN,actual_parent=PARENT,immutable_files=count,source_integrity=source_integrity(),static_gates=static_join(),frozen_actual_author_cold=frozen_cold(),selected_record_changed=False)
 if not a.integrity_only:
  with tempfile.TemporaryDirectory(prefix='pr5392-independent-') as td:
   tmp=Path(td);result['independent_fresh']=run_fresh(tmp);result['source_control']=source_control(packet,tmp/'mutant')
  inventory(HERE,packet);result['status']='PASS_PR5392_INDEPENDENT_CONDITIONAL_VALIDATION'
 result['seconds']=round(time.monotonic()-start,3);print(json.dumps(result,indent=2,sort_keys=True))
if __name__=='__main__':main()
