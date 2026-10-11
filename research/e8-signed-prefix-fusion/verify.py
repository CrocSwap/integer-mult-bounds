"""Full fresh signed25/alias/heterogeneous/fusion composition.
Usage: python -B verify.py NEW_OUTPUT. Python 3.12+; assertions required.
Prepared with OpenAI Codex assistance; Apache-2.0, inherited notices apply.
"""
from pathlib import Path
from hashlib import sha256
from fractions import Fraction as Q
import argparse,gzip,importlib.util,json,os,subprocess,sys
import adapt
if not __debug__ or sys.version_info<(3,12):raise SystemExit('Python 3.12+ with assertions enabled is required')
HERE=Path(__file__).resolve().parent
NAMES={'fusion':'e8-hetero-fusion-composition','ordinary':'e8-prefix-helper-composition','signed':'e8-bit-signed-validation',
 'composition':'e8-far-helper-composition','baseline':'e8-nine-stage-composition','bit':'e8-bit-helper-reuse',
 'bit-parent':'e8-bit-seven-stage','complex':'nine-stage-complex-e8','far':'e8-complex-far-retiming'}
read=lambda p:json.loads(Path(p).read_text())
digest=lambda p:sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):Path(p).write_text(json.dumps(x,sort_keys=True,indent=2)+'\n')
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def inventory(directory,manifest,count):
 directory=Path(directory).resolve();mf=directory/manifest;assert mf.is_file()and not mf.is_symlink()
 if manifest.endswith('.json'):entries=read(mf)['files']
 else:
  rows=[line.split(None,1)for line in mf.read_text().splitlines()];entries={name:want for want,name in rows};assert len(entries)==len(rows)
 normalized={Path(name).as_posix():want for name,want in entries.items()};assert len(normalized)==len(entries);entries=normalized
 assert manifest not in entries and len(entries)+1==count
 if directory==HERE:assert all(Path(name).name==name for name in entries)
 for name in entries:
  p=Path(name);assert not p.is_absolute()and '..'not in p.parts and '.'not in p.parts
 assert not any(p.is_symlink()for p in directory.rglob('*'))
 actual={p.relative_to(directory).as_posix():digest(p)for p in directory.rglob('*')if p.is_file()and p!=mf}
 assert actual==entries,'Missing, changed or unlisted package file: '+directory.name
 return digest(mf)
def check_sources(paths):
 source=read(HERE/'SOURCE.json');inventory(HERE,'MANIFEST.sha256',source['package_file_count'])
 for key,pin in source['dependencies'].items():assert inventory(paths[key],pin['manifest'],pin['file_count'])==pin['manifest_sha256'],key
 return source
def science(x):
 if isinstance(x,dict):return{k:science(v)for k,v in x.items()if k!='source_hashes'}
 if isinstance(x,list):return list(map(science,x))
 return x
def semantic_hash(x):return sha256((json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()).hexdigest()
def validate(out,paths):
 source=read(HERE/'SOURCE.json');parent=out/'parent';signed=parent/'ordinary/signed';ordinary=out/'complex'
 assert read(parent/'RECEIPT.json')['status']=='PASS_FRESH_HETEROGENEOUS_FUSION_AND_SIGNED_SEVEN_STAGE_COMPOSITION'
 ov=read(ordinary/'VERIFICATION.json');assert ov['status']==adapt.NEW_STATUS and len(ov['stages'])==10
 assert ov['candidate_sha256']==source['ordinary_candidate_sha256']==digest(ordinary/'candidate.json')
 controls=read(ordinary/'EXTENSION.json');assert controls['target_reading_main_adds']==50
 assert set(controls['controls_rejected'])=={'missing_initial_subtraction','missing_recovery','changed_helper_word','target_to_source','target_to_helper','wrong_signed_setup','wrong_signed_recovery'}
 discovery=read(ordinary/'prefix-native/upstream-discovery/RESULT.json');assert len(discovery['negative_controls'])==4 and discovery['ablation']
 proof=read(out/'fusion/RECEIPT.json');raw=read(out/'fusion/admission/COMPLEX-SUPPLIER.json')
 assert proof['status']=='PASS_FINITE_CONDITIONAL_PR394_PADDING_FUSION_ON_R781_HETEROGENEOUS_COMPLEX'
 assert proof['candidate_sha256']==digest(out/'fusion/candidate/candidate.json')==source['candidate_sha256']
 assert proof['complex_b']==raw['b']==source['complex_b']
 assert proof['exact_live_columns']==1021 and proof['complete_existing_phase_edges']==3142 and len(proof['mutation_controls'])==10
 template_bytes=gzip.decompress((out/'fusion/admission/GLOBAL-TEMPLATE.json.gz').read_bytes())
 assert sha256(template_bytes).hexdigest()==raw['template_sha256'];template=science(json.loads(template_bytes));write(out/'SCIENCE-TEMPLATE.json',template)
 supplier=science(raw);supplier['template_sha256']=semantic_hash(template)
 supplier['template_hash_kind']='SHA256 canonical JSON plus LF after deleting only source_hashes provenance fields; full fresh raw source binding retained in pipeline outputs.'
 write(out/'complex-supplier.json',supplier)
 priced=read(signed/'composition/baseline/replay/unsplit-bit/kappa-input.json');finite=read(signed/'validation/FINITE.json')
 assert finite['coefficient']==56223565818967 and finite['payload_prefix_bits']==71
 original=load('original_signed25_assembly',paths['baseline']/'assembly.py').run(paths['bit-parent'],priced,finite,supplier)
 assert original['kappa']==source['original_slack_kappa']==proof['kappa']
 assert original['eta']==str(Q(1,10**24))and original['beta']==str(Q(1,10**9));write(out/'assembly-original-slacks.json',original)
 improved=load('smaller_signed25_assembly',paths['fusion']/'assembly.py').run(paths['baseline'],paths['bit-parent'],priced,finite,supplier)
 assert improved['kappa']==source['kappa']and Q(improved['kappa'])>Q(original['kappa'])and improved['binding']=='complex'
 assert improved['eta']==improved['beta']==str(Q(1,10**30))and improved['outer_cutoffs']['common_cutoff']==14*10**30;write(out/'assembly.json',improved)
 fields=['complex_b','exact_live_columns','complete_existing_phase_edges','fresh_tensor_rank3_children','fusions','unfused_padding','rank_mass','live','physical','profile','finite_invoice','local_scalar_macros','local_real_component_primitives','mutation_controls']
 validation={k:proof[k]for k in fields}
 validation.update(status='PASS_FRESH_SIGNED25_HETEROGENEOUS_FUSION_AND_SIGNED_SEVEN_STAGE_COMPOSITION',candidate_sha256=source['candidate_sha256'],ordinary_candidate_sha256=source['ordinary_candidate_sha256'],
  kappa=improved['kappa'],original_slack_kappa=original['kappa'],signed_bit_coefficient=finite['coefficient'],signed_bit_prefix_bits=71,
  bit_c=priced['bit_coarse'],ordinary_extension=controls,upstream_discovery=discovery,
  source395_carriers=read(ordinary/'PREFIX-SOURCE.json'),adaptation_sha256=digest(out/'runtime/ADAPTATION.json'),
  selection_sha256=semantic_hash(read(out/'fusion/candidate/selection.json')),science_template_sha256=semantic_hash(template),fusion_phases_sha256=digest(out/'fusion/admission/FUSION-PHASES.json'),
  output_sha256={name:digest(out/name)for name in ['complex-supplier.json','assembly.json','assembly-original-slacks.json']},outer_common_log2_cutoff=14*10**30,
  scope='Finite source-template evidence, not a separately materialized global IR or an unconditional theorem. Exact rational local maps, signed-prefix controls, tensor phases with both exterior occupancies, explicit endpoint flags, owners, banks, primitive invoices, two moment engines, eight signed-bit continuations and 47 outer inequalities are checked. Mixed local/exterior compiler, whole correlated-bank chronological substitution, all-size chart/precision/recovery/restored-row/analytic interfaces and stage-specific dominating C_full obligations remain conditional.')
 return validation
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('output',type=Path)
 for name,directory in NAMES.items():parser.add_argument('--'+name,type=Path,default=HERE.parent/directory)
 a=parser.parse_args();out=a.output.resolve();paths={name:getattr(a,name.replace('-','_')).resolve()for name in NAMES}
 assert not out.exists()
 for p in [HERE,*paths.values()]:assert not out.is_relative_to(p)
 for p in [out,HERE,*paths.values(),Path(sys.executable).resolve()]:assert not any(c.isspace()for c in str(p))
 check_sources(paths);out.mkdir(parents=True);env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHON=sys.executable)
 for key in ['PYTHONOPTIMIZE','PR315','CX_PINS','CX_SOURCE_PINS','CX_RECORD','CX_RECEIPT','B3_OUT']:env.pop(key,None)
 env['PATH']=str(Path(sys.executable).parent)+os.pathsep+env.get('PATH','')
 def run(name,args):
  print('CHECK',name,flush=True)
  with(out/(name+'.log')).open('w')as log:subprocess.run([sys.executable,'-B',*map(str,args)],env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
 args=[paths['fusion']/'verify.py',out/'parent']
 for name,p in paths.items():
  if name!='fusion':args+=['--'+name,p]
 run('full-fresh-frozen-fusion-parent',args)
 adapt.prepare(paths['ordinary'],paths['fusion'],out/'runtime')
 run('signed25-source-and-ordinary-admission',[out/'runtime/replay.py',paths['complex'],paths['far'],paths['composition'],paths['ordinary'],out/'parent/sources/pr390',out/'complex'])
 signed=out/'parent/ordinary/signed'
 run('signed25-heterogeneous-admission',[out/'runtime/hetero_replay.py',out/'parent/sources/pr390',out/'complex',signed,paths['baseline'],paths['bit-parent'],out/'hetero'])
 run('signed25-fusion-admission',[out/'runtime/fusion_replay.py',out/'parent/sources/pr390',out/'parent/sources/pr394',out/'complex',out/'hetero',signed,paths['baseline'],paths['bit-parent'],out/'fusion'])
 validation=validate(out,paths);assert validation==read(HERE/'EXPECTED.json');write(out/'VALIDATION.json',validation);check_sources(paths)
 for name in ['pr390','pr394']:
  src=out/'parent/sources'/name;wanted=read(src/'INPUTS.json')['files'];assert{p.relative_to(src).as_posix():digest(p)for p in src.rglob('*')if p.is_file()and p.name!='INPUTS.json'}==wanted
 receipt=dict(status=validation['status'],kappa=validation['kappa'],original_slack_kappa=validation['original_slack_kappa'],complex_b=validation['complex_b'],candidate_sha256=validation['candidate_sha256'],
  package_manifest_sha256=digest(HERE/'MANIFEST.sha256'),validation_sha256=digest(out/'VALIDATION.json'),fresh_frozen_parent_receipt_sha256=digest(out/'parent/RECEIPT.json'),all_frozen_sources_unchanged=True,
  fresh_stages=['frozen-fusion-parent','pinned-signed25-reconstruction','ordinary-ten-stage-admission','heterogeneous-endpoints','full-flags-fusion','original-and-smaller-slack-assembly'],scope=validation['scope'])
 write(out/'RECEIPT.json',receipt);print(receipt['status'],receipt['kappa'],flush=True)
if __name__=='__main__':main()
