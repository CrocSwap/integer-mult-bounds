"""Strict portable contract for the fresh PR325 480-retiming candidate."""
from pathlib import Path
import base64,gzip,hashlib,json,os,shutil
HERE=Path(__file__).resolve().parent
INPUTS=Path(os.environ.get('P325_INPUTS',str(HERE/'local-inputs'))).resolve()
OUTPUT=Path(os.environ.get('P325_OUTPUT',str(HERE/'output'))).resolve()
SOURCE,FRAME,BANK,PREPARED,GLOBAL,AUDIT,INERT=[OUTPUT/x for x in ['source','frame','bank','prepared','global','audit','inert']]
HEAD='0eca9340a3df6141b8e71a41638c3937b3522888'
WORD='601da0e6a67715011a4bbc44f6977f13625c5833d4d40443c10b0d5a9da1896d'
FRAMES='fec07e983f81459c45747dfaa4eecabc3429e84d4685f385771904dee4c4fbc0'
def require_assertions():
 if not __debug__:raise RuntimeError('Assertions must be enabled; run without -O.')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
 p=Path(p);b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def portable(x):
 if isinstance(x,dict):return {portable(k):portable(v)for k,v in x.items()}
 if isinstance(x,list):return [portable(v)for v in x]
 if isinstance(x,str):
  for root,label in [(OUTPUT,'$OUTPUT'),(INPUTS,'$INPUTS'),(HERE,'$PACKAGE')]:x=x.replace(str(root),label)
 return x
def dump(p,x):
 p=Path(p);b=(json.dumps(portable(x),sort_keys=True,separators=(',',':'))+'\n').encode();p.write_bytes(gzip.compress(b,mtime=0)if p.suffix=='.gz'else b)
def source_manifest():
 x=read(HERE/'inputs.json');assert x['head']==HEAD and x['word_gzip_sha256']==WORD
 assert len(x['files'])==27 and len({z['local']for z in x['files']})==27
 for z in x['files']:
  assert not Path(z['local']).is_absolute()and '..'not in Path(z['local']).parts and not z['local'].endswith('.py')
  assert z['url']==f"https://raw.githubusercontent.com/{z['repository']}/{HEAD}/research/five-stage-p10b-banks/{z['path']}"
 return x
def check_input(raw,z):
 require_assertions();assert len(raw)==z['bytes']and hashlib.sha256(raw).hexdigest()==z['sha256'],z['local']
 assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==z['git_blob'],z['local']
def verify_inputs():
 require_assertions();m=source_manifest()
 for z in m['files']:check_input((INPUTS/z['local']).read_bytes(),z)
 upstream=read(INPUTS/'MANIFEST.json')['files'];assert sha(INPUTS/'MANIFEST.json')==m['upstream_manifest_sha256']
 for z in m['files']:
  if z['path']!='MANIFEST.json':assert upstream[z['path']]==z['sha256']
 return m
def setup_data():
 m=verify_inputs()
 for p in [SOURCE,FRAME,BANK,PREPARED,GLOBAL,AUDIT,INERT,SOURCE/'inputs']:p.mkdir(parents=True,exist_ok=True)
 for z in m['files']:
  raw=(INPUTS/z['local']).read_bytes()
  for parent in [INERT,SOURCE/'inputs']:(parent/z['local']).write_bytes(raw)
  if z['local'].endswith('.gz'):
   (INERT/(z['local']+'.b64')).write_bytes(base64.b64encode(raw))
   (INERT/z['local'][:-3]).write_bytes(gzip.decompress(raw))
 shutil.copyfile(HERE/'source/SOURCES.json',SOURCE/'SOURCES.json')
 (AUDIT/'inert').mkdir(exist_ok=True)
 for z in m['files']:
  if z['acquisition_provenance'].startswith('Inert PR325 theorem'):shutil.copyfile(INPUTS/z['local'],AUDIT/'inert'/z['local'])
 shutil.copyfile(HERE/'FRAME-CONTRACT.md',AUDIT/'FRAME-CONTRACT.md')
 if(HERE/'audit/AUDIT.md').exists():shutil.copyfile(HERE/'audit/AUDIT.md',AUDIT/'AUDIT.md')
 if(HERE/'bank/assessment-sources.json').exists():shutil.copyfile(HERE/'bank/assessment-sources.json',OUTPUT/'SOURCES.json')
 if(HERE/'bank/baseline-census.json').exists():dump(OUTPUT/'LEDGER.json',{'pr325':read(HERE/'bank/baseline-census.json')})
SOURCE_ARTIFACTS=['retiming-selection.json','source-events.json.gz','scalar-events.json.gz','physical-source-map.json']
def freeze_source():
 result=read(SOURCE/'RESULT.json');assert set(result['artifacts'])==set(SOURCE_ARTIFACTS)
 value={'status':'REGENERATED_CURRENT_SOURCE_PACKET','head':HEAD,'word_gzip_sha256':WORD,'input_manifest_sha256':sha(HERE/'inputs.json'),'source_provenance_sha256':sha(HERE/'source/SOURCES.json'),'producers':{p.name:sha(p)for p in sorted((HERE/'source').glob('*.py'))},'files':[{'path':n,'sha256':sha(SOURCE/n)}for n in ['RESULT.json','SOURCES.json',*SOURCE_ARTIFACTS]]}
 dump(SOURCE/'MANIFEST.json',value);verify_source()
def verify_source():
 verify_inputs();m=read(SOURCE/'MANIFEST.json');r=read(SOURCE/'RESULT.json')
 assert m['head']==HEAD and m['word_gzip_sha256']==WORD and m['input_manifest_sha256']==sha(HERE/'inputs.json')
 assert m['source_provenance_sha256']==sha(HERE/'source/SOURCES.json')==sha(SOURCE/'SOURCES.json')==r['sources_sha256']
 assert set(m['producers'])=={p.name for p in(HERE/'source').glob('*.py')}
 for n,h in m['producers'].items():assert sha(HERE/'source'/n)==h,n
 assert set(z['path']for z in m['files'])=={'RESULT.json','SOURCES.json',*SOURCE_ARTIFACTS}
 for z in m['files']:assert sha(SOURCE/z['path'])==z['sha256'],z['path']
 assert r['status']=='PASS_ALL480_PR325_PARTNER_MIX_RETIMINGS_RAW_LOCAL_PROOF'
 assert r['checker_sha256']==sha(HERE/'source/check_retimings.py')and r['head']==HEAD and r['word_gzip_sha256']==WORD and r['frames_gzip_sha256']==FRAMES
 assert r['admitted']==480 and r['rejected']==0 and r['formal_columns']==10020
 assert r['scalar_projection_unchanged']and r['full_F2_forward_and_inverse_all_columns_pass']and not r['prior_role_or_frame_selections_imported']and not r['upstream_programs_executed']
 assert set(r['artifacts'])==set(SOURCE_ARTIFACTS)
 for n,h in r['artifacts'].items():assert sha(SOURCE/n)==h,n
 return m
def verify_frame():
 verify_source();r=read(FRAME/'RESULT.json');v=read(FRAME/'VALIDATION.json')
 assert r['status']=='PASS_FRESH_PR325_480_RETIMINGS_FULL_LOCAL_FRAME_WORD'and v['status']=='PASS_INDEPENDENT_PR325_FULL_LOCAL_RECORD_AND_FRAME_AUDIT'
 assert (v['frames'],v['records'],v['exact_MOVE_containment_pairs'])==(12885,398660,40125)
 assert v['all_frame_ranks_and_annihilators_exact']and v['all_frame_G_nondegeneracy_certified']and v['source_and_target_and_helper_final_states_exact']
 assert r['head']==HEAD and r['candidate_sha256']==WORD and r['source_manifest_sha256']==sha(SOURCE/'MANIFEST.json')and r['source_result_sha256']==sha(SOURCE/'RESULT.json')
 assert r['checker_sha256']==sha(HERE/'frame/build_local.py')and v['checker_sha256']==sha(HERE/'frame/validate_local.py')and v['builder_receipt_sha256']==sha(FRAME/'RESULT.json')
 assert r['source_retimings']==480 and r['columns']==10020 and not r['source_selections_imported_from_old_word']
 assert set(r['artifacts'])=={'local-events.json.gz','local-records.json.gz','local-frames.json.gz','local-endpoints.json','local-paths.json.gz','role-map.json','source-frame-map.json'}
 for n,h in r['artifacts'].items():assert sha(FRAME/n)==h,n
 return r
def child_env():return dict(os.environ,P325_INPUTS=str(INPUTS),P325_OUTPUT=str(OUTPUT))
def input_for(path):
 return INPUTS/next(z['local']for z in source_manifest()['files']if z['path']==path)
def freeze_frame():
 r=verify_frame();a=read(AUDIT/'FULL-FRAME-AUDIT.json')
 assert a['status']=='PASS_PR325_FULL_LOCAL_ARRAY_FRAME_CONTRACT'and a['checker_sha256']==sha(HERE/'audit/check_full_frames.py')
 assert a['full_frame_result_sha256']==sha(FRAME/'RESULT.json')and a['full_frame_validation_sha256']==sha(FRAME/'VALIDATION.json')and a['source_result_sha256']==sha(SOURCE/'RESULT.json')
 assert a['proof_sha256']==sha(HERE/'FRAME-CONTRACT.md')
 assert a['arbitrary_dirty_operator_retained_by_common_array_frame_identity']and a['address_geometry_distinguished_from_F2_payload_values']
 binding={'status':'PASS_SEPARATE_INDEPENDENT_LOCAL_ARRAY_FRAME_AUDIT_BOUND','audit_files':{n:sha(AUDIT/n)for n in ['FULL-FRAME-AUDIT.json','FRAME-CONTRACT.md']},'local_result_sha256':sha(FRAME/'RESULT.json'),'local_validation_sha256':sha(FRAME/'VALIDATION.json'),'checker_sha256':sha(HERE/'audit/check_full_frames.py'),'pinned_theorems':a['pinned_theorems'],'conclusion':'All finite premises of the pinned common-array-frame and complete COPY identities are verified. Generic primitive, prime, global compiler, bank/price and all-size interfaces remain separate.'}
 dump(FRAME/'ARBITRARY-DIRTY-AUDIT-BINDING.json',binding)
 names=['RESULT.json','VALIDATION.json','ARBITRARY-DIRTY-AUDIT-BINDING.json',*sorted(r['artifacts'])]
 dump(FRAME/'MANIFEST.json',{'status':'REGENERATED_CURRENT_FULL_LOCAL_FRAME_PACKET','head':HEAD,'source_manifest_sha256':sha(SOURCE/'MANIFEST.json'),'producers':{p.name:sha(p)for p in sorted((HERE/'frame').glob('*.py'))},'files':[{'path':n,'sha256':sha(FRAME/n)}for n in names]})
 verify_frame_binding()
def verify_frame_binding():
 r=verify_frame();m=read(FRAME/'MANIFEST.json');b=read(FRAME/'ARBITRARY-DIRTY-AUDIT-BINDING.json');a=read(AUDIT/'FULL-FRAME-AUDIT.json')
 assert m['head']==HEAD and m['source_manifest_sha256']==sha(SOURCE/'MANIFEST.json')
 assert set(m['producers'])=={p.name for p in(HERE/'frame').glob('*.py')}
 for n,h in m['producers'].items():assert sha(HERE/'frame'/n)==h,n
 assert set(z['path']for z in m['files'])=={'RESULT.json','VALIDATION.json','ARBITRARY-DIRTY-AUDIT-BINDING.json',*r['artifacts']}
 for z in m['files']:assert sha(FRAME/z['path'])==z['sha256'],z['path']
 assert b['local_result_sha256']==sha(FRAME/'RESULT.json')and b['local_validation_sha256']==sha(FRAME/'VALIDATION.json')
 assert b['checker_sha256']==sha(HERE/'audit/check_full_frames.py')==a['checker_sha256']
 assert set(b['audit_files'])=={'FULL-FRAME-AUDIT.json','FRAME-CONTRACT.md'}
 for n,h in b['audit_files'].items():assert sha(AUDIT/n)==h,n
 assert a['proof_sha256']==sha(HERE/'FRAME-CONTRACT.md')==sha(AUDIT/'FRAME-CONTRACT.md')
 assert a['full_frame_result_sha256']==sha(FRAME/'RESULT.json')and a['full_frame_validation_sha256']==sha(FRAME/'VALIDATION.json')and a['source_result_sha256']==sha(SOURCE/'RESULT.json')
 assert a['status']=='PASS_PR325_FULL_LOCAL_ARRAY_FRAME_CONTRACT'and a['arbitrary_dirty_operator_retained_by_common_array_frame_identity']and a['address_geometry_distinguished_from_F2_payload_values']
 assert set(a['pinned_theorems'])=={'UPSTREAM-PR234-PROOF.md','bitword/README.md','proof/INTEGRATED_PROOF.md','proof/PARITY-CONTRACT.md','proof/copied-centers-lemma.tex','proof/primary/03-motifs.tex'}
 assert b['pinned_theorems']==a['pinned_theorems']
 for n,h in a['pinned_theorems'].items():assert sha(input_for(n))==h,n
 return b
BANK_RECEIPTS={'BASE-LEDGER.json':'check_base_ledger.py','BANK-RESULT.json':'check_admitted_banks.py','PRICE-RESULT.json':'price_admitted_profile.py','CONTROLS.json':'check_controls.py','FRAME-BINDING.json':'check_full_frame_binding.py'}
def freeze_bank():
 value={'status':'REGENERATED_CURRENT_PR325_BANK_CERTIFICATE','head':HEAD,'source_manifest_sha256':sha(SOURCE/'MANIFEST.json'),'full_frame_result_sha256':sha(FRAME/'RESULT.json'),'producers':{p.name:sha(p)for p in sorted((HERE/'bank').glob('*.py'))},'witnesses':{n:sha(HERE/'bank'/n)for n in ['BANK-SOURCES.json','assessment-sources.json','baseline-census.json']},'files':{n:sha(BANK/n)for n in [*BANK_RECEIPTS,'endpoint-charts.json.gz','literal-bank-assignments.bin.gz']}}
 dump(BANK/'MANIFEST.json',value);verify_bank()
def verify_bank():
 verify_frame();m=read(BANK/'MANIFEST.json')
 assert m['head']==HEAD and m['source_manifest_sha256']==sha(SOURCE/'MANIFEST.json')and m['full_frame_result_sha256']==sha(FRAME/'RESULT.json')
 assert set(m['producers'])=={p.name for p in(HERE/'bank').glob('*.py')}
 for n,h in m['producers'].items():assert sha(HERE/'bank'/n)==h,n
 assert set(m['witnesses'])=={'BANK-SOURCES.json','assessment-sources.json','baseline-census.json'}
 for n,h in m['witnesses'].items():assert sha(HERE/'bank'/n)==h,n
 assert set(m['files'])=={*BANK_RECEIPTS,'endpoint-charts.json.gz','literal-bank-assignments.bin.gz'}
 for n,h in m['files'].items():assert sha(BANK/n)==h,n
 for n,code in BANK_RECEIPTS.items():assert read(BANK/n)['checker_sha256']==sha(HERE/'bank'/code),n
 b=read(BANK/'BANK-RESULT.json');p=read(BANK/'PRICE-RESULT.json');f=read(BANK/'FRAME-BINDING.json')
 assert b['source_admission_sha256']==sha(SOURCE/'RESULT.json')and b['base_ledger_sha256']==sha(BANK/'BASE-LEDGER.json')and p['bank_result_sha256']==sha(BANK/'BANK-RESULT.json')
 assert f['full_frame_result_sha256']==sha(FRAME/'RESULT.json')and f['bank_result_sha256']==sha(BANK/'BANK-RESULT.json')
 return m
