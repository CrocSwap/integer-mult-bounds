"""Minimal old-complex complete signed call portfolio portable default."""
from pathlib import Path
import json,gzip,hashlib,shutil,subprocess,sys,os
assert __debug__,'Assertions required'
P=Path(__file__).resolve().parent;D=P/'derived';D.mkdir(exist_ok=True);rd=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();canon=lambda p:hashlib.sha256(gzip.decompress(p.read_bytes())).hexdigest();inv=rd(P/'INVENTORY.json');binding=rd(P/'PARENT-BINDING.json');parent=P/'parent-pool60';calls=[];env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'}
assert (P/'SOURCE-MANIFEST.json').is_file(),'Source manifest required'
for name,h in rd(P/'SOURCE-MANIFEST.json')['files'].items():
 if name not in rd(P/'INCREMENTAL-TRANSPORT.json'):assert sha(P/name)==h,name
assert binding['commit']=='6c00693e6e8e6191f313e9be590aa807c8a81364'and binding['tree']=='707d8ce6254bb08ac88cdb57b8b8571c68789a1d'
for n,z in inv['preserved_parent_files'].items():assert sha(parent/n)==z['sha256'],n
for n,z in inv['incremental_sources'].items():assert sha(P/n)==z['sha256'],n
def run(name,args):
 print('RUN',name,flush=True);calls.append(name)
 with (D/(name+'.log')).open('w')as out:subprocess.run([sys.executable,'-B',*map(str,args)],env=env,stdout=out,stderr=subprocess.STDOUT,check=True)
 print('PASS',name,flush=True)
run('new-incremental-sigma-materialization',[P/'materialize_incremental.py'])
for n,z in inv['original_frozen69_sources'].items():
 q=P/z['packet_path']
 if not q.exists():q=parent/z['packet_path']
 assert sha(q)==z.get('projected_sha256',z['sha256']),n
run('parent-materialize-once',[parent/'materialize.py'])
run('parent-entire-default-once',[parent/'verify-portable.py'])
W=D/'replay'
if W.exists():shutil.rmtree(W)
shutil.copytree(parent/'derived/replay',W);shutil.copytree(P/'sources',W,dirs_exist_ok=True)
run('mechanical-source-adapters',[P/'apply_adapters.py',W,D/'PATH-ADAPTERS.json'])
A=W/'experiments/architecture/bit-provider-portfolio-v4';G=A/'global';B=W/'experiments/architecture/whole-owner-pooling-v4/bit60';I=W/'experiments/architecture/signed-provider-independent-v4';C=W/'experiments/architecture/bit-provider-portfolio-closure-v4'
run('fresh-lazy-complete-provider',[A/'construct.py'])
run('independent-base980-dirt120adjoints',[I/'check_local.py',B/'local',B/'local',I/'fresh-base',B/'local'])
run('independent-lazy980-dirt120adjoints',[I/'check_local.py',A/'drop970-948-lazy',B/'local',I/'fresh-lazy',B/'local'])
run('actual-eight-call-controller',[A/'emit_portfolio.py']);assert canon(G/'GLOBAL-TEMPLATE.json.gz')=='27d699eba7bfd715720b1e0a92406ef7c47f4a1cd1ee09c18109db6838e18379'
run('all65120-fresh78sigma',[G/'hosted_sigma.py'])
run('1320-targetcharts10560owners2520controls',[G/'target_address.py'])
for name in ['portfolio_global','portfolio_sigma','portfolio_prefix','portfolio_addresses']:
 run('independent-'+name,[I/(name+'.py')])
run('actual-paid-registry-stagecut-invoice',[G/'invoice.py'])
run('old-complex-dual-eight47-repricing',[C/'reprice_old_complex.py'])
run('independent-old-complex-eight47-invoice',[I/'portfolio_old_complex_arithmetic.py'])
r=rd(C/'REPRICED-OLD-COMPLEX.json');assert r['kappa']=='1259574957280999831405951/1000000000000000000000000000'and len(r['bootstrap'])==8 and len(r['strict_constraints'])==47
f=rd(G/'local/GLOBAL-BOUND.json')['finite'];assert(f['prefix_bits'],f['three_level_bits'],f['raw_unit_additions'],f['signed_unit_additions'],f['provider_registry_selector_calls'])==(159,532,1359872,1471984,898544)
assert calls.count('parent-materialize-once')==calls.count('parent-entire-default-once')==1
out={'status':'PASS_PORTABLE_MINIMAL_OLD_COMPLEX_CONDITIONAL_SIGNED_COMPLETE_CALL_PORTFOLIO','kappa':r['kappa'],'parent_commit':binding['commit'],'parent_tree':binding['tree'],'preserved_parent_transport_files':1134,'frozen_original_source_attestations':69,'projected_source_bindings':69,'canonical_template_sha256':canon(G/'GLOBAL-TEMPLATE.json.gz'),'whole_helper_roles':65120,'calls':88,'alternate_calls':8,'target_owner_gates':10560,'finite':f,'run_sequence':calls,'independent_checks':'fresh980+dirt+inverse+120adjoints forbothproviders; heterogeneouscontroller/sigma/prefix/address/full8+47oldcomplexinvoice','source_projection_ledger_sha256':sha(P/'SOURCE-PROJECTION.json'),'parent_gzip_runtime_repair_sha256':sha(parent/'PORTABLE-GZIP-REPAIR.json'),'scope':'No paid458 mathematical dependence; its two frozen69records and historical fullgate remain archival evidence only. Inherited whole dirty-slot/cover, weighted source/current-target compiler, C_full/chart/commonprime/precision/tape/recovery/analytic premises conditional. Publication readiness additionally needs independent parentpublication/relocation gate.'}
(D/'PORTFOLIO-RESULT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
