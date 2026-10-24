#!/usr/bin/env python3
"""Independent PR5383/5387 conditional validation; no Git/network/candidate imports.

Chris R / Clear1nsight, substantial OpenAI Codex assistance; Apache-2.0.
Construction and all preserved reviewer engines retain exact frozen attribution.
"""
from pathlib import Path,PurePosixPath
import argparse,base64,copy,gzip,hashlib,json,os,shutil,subprocess,sys,tempfile,time
HERE=Path(__file__).resolve().parent;F=HERE/'frozen';C=F/'09-capsule-cold'
MAIN='1ec1119972c9aefe42525172d07b332fcff81cb4';HEAD='b1ab650d36f59e5be682a813145b7c67e219e341'
PACKET_SHA256='ab787e2df2650c7027d54f6fad9faae0c763bdbc5b41d299a792b0972dfe1b68'
ASSUMPTIONS=['native_all_columns','owned_erasure','compiler','precision_tape','analytic_recovery']
def need(v,why):
 if not v:raise ValueError(why)
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def safe(root,name):
 p=PurePosixPath(name);need(not p.is_absolute() and '..' not in p.parts and str(p)==name,'unsafe packet path')
 q=root
 for part in p.parts:q=q/part;need(not q.is_symlink(),'symbolic packet path')
 need(q.is_file(),'missing packet file '+name);return q
def inventory(root,manifest):
 seen=set()
 for r in manifest['files']:
  name=r['path'];need(name not in seen,'duplicate packet path');seen.add(name);b=safe(root,name).read_bytes()
  need(len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256'],'packet byte guard '+name)
 actual={p.relative_to(root).as_posix() for p in (root/'frozen').rglob('*') if p.is_file()}
 need(actual=={n for n in seen if n.startswith('frozen/')},'frozen inventory missing/extra bytes')
 return len(seen)
def run(argv,cwd,timeout=110):
 env=dict(os.environ);env.pop('PYTHONOPTIMIZE',None);env['PYTHONPYCACHEPREFIX']=str(cwd/'private-bytecode')
 args=[sys.executable]+(['-O'] if sys.flags.optimize else [])+['-B']+list(map(str,argv))
 q=subprocess.run(args,cwd=cwd,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=timeout)
 need(q.returncode==0,'independent subprocess failure '+str(args)+': '+q.stderr[-4000:]);return q.stdout

def merkle():
 results=[]
 # Call the exact included provenance verifier. It authenticates raw objects,
 # commit->tree->path->blob bytes and actual direct canonical source parent.
 for n in ['capsule-v1','capsule-5387-v1']:
  with tempfile.TemporaryDirectory(prefix='price-source-') as td:
   result=json.loads(run([C/'verify_merkle_provenance.py','--capsule',C/n,'--receipt',C/(n+'-MERKLE-PROVENANCE.json')],Path(td),15));results.append(result)
 # The same parser verifies the supplementary canonical precision proof paths.
 with tempfile.TemporaryDirectory(prefix='price-supplement-') as td:
  t=Path(td);proof=read(HERE/'SUPPLEMENT-MERKLE.json');m=b'canonical supplementary precision source paths';(t/'IMMUTABLE-MANIFEST.json').write_bytes(m)
  proof['capsule_manifest_sha256']=hashlib.sha256(m).hexdigest()
  for r in proof['rows']:
   p=t/r['capsule_path'];p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(F/r['capsule_path'],p)
  (t/'proof.json').write_text(json.dumps(proof));results.append(json.loads(run([C/'verify_merkle_provenance.py','--capsule',t,'--receipt',t/'proof.json'],t,15)))
 return results

def resolve_historical(name):
 aliases=read(HERE/'PATH-ALIASES.json');prefix=aliases['workspace_prefix']+'/'
 if name.startswith(prefix):name=name[len(prefix):]
 need(name in aliases['paths'],'undeclared historical dependency '+name)
 return safe(HERE,aliases['paths'][name])

def joined_static():
 result={}
 for rev,receipt_name,closure_name,light_name in [('5383','receipt-v3.json','CLOSURE-v2.json','LIGHT-ARITHMETIC.json'),('5387','5387-receipt-v2.json','CLOSURE-5387-v1.json','LIGHT-ARITHMETIC-5387.json')]:
  r=read(F/'04-exact-funding'/receipt_name);c=read(F/'03-precision-stock'/closure_name)
  need(r['status']=='FUNDED_CONDITIONAL_INDEPENDENT_STATIC_ADMISSION' and r['endpoint_funded'],'static funded gate '+rev)
  need(c['status']=='PASS_SAME_PREMISE_CONSTRUCTIVE_FINITE_TEMPLATE_SPECIALIZATION','precision applicability '+rev)
  need(c['retained_assumptions']==ASSUMPTIONS and not c['new_candidate_specific_assumptions'],'five framework assumptions '+rev)
  for name,h in r.get('closure_dependencies_sha256',{}).items():need(sha(resolve_historical(name))==h,'closure dependency '+name)
  for name,h in c['dependencies_sha256'].items():need(sha(resolve_historical(name))==h,'template dependency '+name)
  for name,h in c['source_proof_sha256'].items():need(sha(C/'supplement-03-v1/snapshot'/name)==h,'canonical source proof '+name)
  need(r['N']==c['expanded_constants']['N'],'fresh expanded finite N '+rev)
  need(not c['expanded_constants']['old_raw_cap_used_as_expanded_cap'],'expanded constants not raw cap '+rev)
  need(c['stock']['simultaneous_rule']=='product','simultaneous stock product '+rev)
  result[rev]=dict(head=r['candidate']['head'],funded_kappa=r['kappa'],N=r['N'],framework_assumptions=5)
 return result

def cold():
 v=read(C/'VALIDATION.json');b=read(C/'BOUNDED-REGISTERED-RUN.json')
 need(v['status']=='PASS_FUNDED_CONDITIONAL_AND_ONE_REGISTERED_NORMAL_OPTIMIZED_PAIR' and v['candidate']['head']==HEAD,'strongest frozen cold head/status')
 need(all(value==b.get(key) for key,value in v['registered_replay'].items()),'complete cold resource receipt join')
 need(b['status']=='PASS_COMPLETE_REGISTERED_NORMAL_AND_OPTIMIZED' and b['exit']==0 and b['resource_stop'] is None and not b['scientific_or_git_bytes_changed'],'actual frozen registered cold pair')
 need(read(C/'PRE-RUN-HASHES.json')==read(C/'POST-RUN-HASHES.json'),'complete original cold pre/post equality')
 need(len(read(C/'PRE-RUN-HASHES.json'))==20535,'complete original cold inventory count')
 need(sha(C/'REGISTERED-COLD.stdout.log')==b['stdout_sha256'] and sha(C/'REGISTERED-COLD.stderr.log')==b['stderr_sha256'],'complete cold stdout/stderr')
 need((C/'REGISTERED-COLD.stderr.log').stat().st_size==0,'cold stderr empty')
 log=(C/'REGISTERED-COLD.stdout.log').read_text();need(log.count('PASS_CONDITIONAL_KAPPA_003026674765_COMPILER_MARGIN')==2 and 'PASS_REGISTERED_RESEARCH_PACKAGE' in log,'both actual author modes')
 need(v['controls']['two_modes_total']==44 and v['assumptions']==ASSUMPTIONS,'actual cold controls and scope')
 author=C/'capsule-5387-v1/snapshot/research/eight-owned-relations'
 for key,name in [('RESULT_json_sha256','RESULT.json'),('WORD_gz_sha256','WORD.json.gz')]:need(sha(author/name)==v['fresh_artifact_equality'][key],'cold exact scientific artifact '+name)
 need(hashlib.sha256(gzip.decompress((author/'WORD.json.gz').read_bytes())).hexdigest()==v['fresh_artifact_equality']['WORD_decompressed_sha256'],'cold decompressed word')
 for role,r in v['independent_gates'].items():need(sha(resolve_historical(r['path']))==r['sha256'],'cold independent gate '+role)
 return dict(status=b['status'],seconds=b['seconds'],peak_sampled_descendant_rss_kib=b['peak_sampled_descendant_rss_kib'],original_unchanged_files=20535,author_controls=44,freshly_rerun_by_this_package=False,comparison5383_own_author_cold=False)

def stable(d):return {k:v for k,v in d.items() if k!='seconds'}
def fresh_engines(tmp):
 t=tmp/'frozen';shutil.copytree(F,t)
 # Every executable writes only private copies; the actual package is immutable.
 result={}
 for rev,where in [('5383','01-physical'),('5387','01-physical/5387-fresh')]:
  p=t/where/'independent_physical_check.py';old=read(F/where/'PHYSICAL-RECEIPT.json');new=json.loads(run([p],tmp))
  need(stable(new)==stable(old),'complete independent physical result '+rev)
  result['physical'+rev]=dict(status=new['status'],seconds=new['seconds'],actual_word_mutations=len(new['negative_controls']))
 # Original census and precision assertions are preserved with optimize=0;
 # physical/exact checks use explicit need/raise and inherit wrapper optimization.
 for rev,n,capsule in [('5383','v1','capsule-v1'),('5387','v2','capsule-5387-v1')]:
  run([HERE/'exec_frozen.py',t/'02-census'/('census.py' if n=='v1' else 'census-v2.py'),t/'09-capsule-cold'/capsule],tmp)
  invoice=read(t/'02-census'/('INVOICE-'+n+'.json'));old=read(F/'02-census'/('INVOICE-'+n+'.json'))
  need(invoice==old,'full independent literal invoice '+rev)
  need(sha(t/'02-census'/('CHRONOLOGY-'+n+'.json'))==old['chronology_sha256'],'full chronology regeneration '+rev)
  result['census'+rev]=dict(paid=invoice['totals']['paid_jobs'],productive=invoice['totals']['productive_fields'],complete_invoice_and_chronology_equal=True)
  path=t/'03-precision-stock'/('check_precision.py' if n=='v1' else 'check_precision_5387.py')
  run([HERE/'exec_frozen.py',path],tmp)
  name='LIGHT-ARITHMETIC.json' if n=='v1' else 'LIGHT-ARITHMETIC-5387.json'
  need(stable(read(t/'03-precision-stock'/name))==stable(read(F/'03-precision-stock'/name)),'full literal precision/scalar audit '+rev)
  receipt=F/'04-exact-funding'/('receipt-v3.json' if n=='v1' else '5387-receipt-v2.json')
  exact=json.loads(run([HERE/'replay_exact.py',t/'04-exact-funding/exact_engine.py',t/'02-census'/('INVOICE-'+n+'.json'),receipt],tmp))
  need(exact['root']['derivative_upper'].startswith('-') and exact['root']['remaining_moment_upper'].startswith('-'),'actual full-domain fixed-profile ceiling proof')
  result['exact'+rev]=dict(status=exact['status'],seconds=exact['seconds'],kappa=exact['kappa'],root=exact['root'],outer_strict=exact['outer']['strict_count'],outer_functional=exact['outer']['functional_count'])
  # The equality guard consumes a newly reconstructed full invoice, not a source
  # RESULT. False productive credits must fail that actual guard.
  mutant=copy.deepcopy(old);mutant['histograms']['productive']['9']+=128
  try:need(invoice==mutant,'unearned128H9 targets rejected by fresh literal census')
  except ValueError:pass
  else:raise ValueError('unearned productive credit accepted')
 result['assertion_adapter']='Frozen assertion-based census/precision source compiled with explicit optimize=0 in both parent modes; physical/exact need/raise checks inherit parent optimization.'
 return result

def controls(manifest,tmp):
 row=next(r for r in manifest['files'] if r['path'].endswith('capsule-5387-v1/snapshot/research/eight-owned-relations/WORD.json.gz'))
 q=tmp/row['path'];q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes((HERE/row['path']).read_bytes()+b'changed')
 try:inventory(tmp,dict(files=[row]))
 except ValueError as e:need('packet byte guard' in str(e),'source mutation wrong failure')
 else:raise ValueError('source mutation accepted')
 return ['actual changed WORD byte rejected before evaluation','unearned 128 productive H9 targets rejected against freshly reconstructed literal invoice','both fresh physical engines execute seven actual word mutation controls','exact engine rechecks root signs, derivative/away ceiling, reserve and all outer semantic controls']

def main():
 p=argparse.ArgumentParser();p.add_argument('--integrity-only',action='store_true');a=p.parse_args();start=time.monotonic()
 need(sha(HERE/'PACKET.json')==PACKET_SHA256,'immutable packet manifest')
 manifest=read(HERE/'PACKET.json');count=inventory(HERE,manifest);sources=merkle();static=joined_static();frozen=cold()
 result=dict(status='PASS_PRICE_PLANE_INDEPENDENT_INTEGRITY',canonical_base=MAIN,candidate_head=HEAD,inventory_files=count,source_proofs=sources,static_funded=static,frozen_actual_author_cold=frozen,selected_record_changed=False)
 if not a.integrity_only:
  with tempfile.TemporaryDirectory(prefix='price-independent-') as td:
   result['fresh_independent_engines']=fresh_engines(Path(td));result['controls']=controls(manifest,Path(td)/'mutation')
  inventory(HERE,manifest);result['status']='PASS_INDEPENDENT_PRICE_PLANE_CONDITIONAL_VALIDATION'
 result['seconds']=round(time.monotonic()-start,3);print(json.dumps(result,indent=2,sort_keys=True))
if __name__=='__main__':main()
