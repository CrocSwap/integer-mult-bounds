"""Fresh ordinary/signed ancestor, heterogeneous endpoints, fusion and exact assembly.
Usage: python -B verify.py FRESH_OUTPUT_DIRECTORY. Python 3.12+; assertions required.
Prepared with OpenAI Codex assistance; Apache-2.0, inherited notices apply.
"""
from pathlib import Path
from hashlib import sha256
import argparse,copy,gzip,importlib.util,json,os,subprocess,sys
import assembly,source_adapter
assert __debug__ and sys.version_info>=(3,12)
HERE=Path(__file__).resolve().parent
NAMES={'ordinary':'e8-prefix-helper-composition','signed':'e8-bit-signed-validation',
       'composition':'e8-far-helper-composition','baseline':'e8-nine-stage-composition',
       'bit':'e8-bit-helper-reuse','bit-parent':'e8-bit-seven-stage',
       'complex':'nine-stage-complex-e8','far':'e8-complex-far-retiming'}
read=lambda p:json.loads(Path(p).read_text())
digest=lambda p:sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):Path(p).write_text(json.dumps(x,sort_keys=True,indent=2)+'\n')
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def inventory(directory,manifest,count):
 directory=Path(directory).resolve();mf=directory/manifest
 assert mf.is_file()and not mf.is_symlink()
 if manifest.endswith('.json'):entries=read(mf)['files']
 else:
  rows=[line.split(None,1)for line in mf.read_text().splitlines()]
  entries={name:want for want,name in rows};assert len(entries)==len(rows)
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
def science(value):
 """Remove only named source-hash provenance; retain every operator/owner field."""
 if isinstance(value,dict):return{k:science(v)for k,v in value.items()if k!='source_hashes'}
 if isinstance(value,list):return list(map(science,value))
 return value
def semantic_hash(value):return sha256((json.dumps(value,sort_keys=True,separators=(',',':'))+'\n').encode()).hexdigest()
def validate(out,paths):
 source=read(HERE/'SOURCE.json');ordinary=out/'ordinary';signed=ordinary/'signed'
 prior=read(ordinary/'RECEIPT.json');assert prior['status']=='PASS_FRESH_PR390_PREFIX_HELPER_COMPLEX_AND_SIGNED_SEVEN_STAGE_BIT'
 raw=read(out/'fusion/admission/COMPLEX-SUPPLIER.json');proof=read(out/'fusion/RECEIPT.json')
 assert proof['status']=='PASS_FINITE_CONDITIONAL_PR394_PADDING_FUSION_ON_R781_HETEROGENEOUS_COMPLEX'
 assert proof['candidate_sha256']==digest(out/'fusion/candidate/candidate.json')==source['candidate_sha256']
 assert proof['complex_b']==raw['b']==source['complex_b']
 assert proof['exact_live_columns']==1021 and proof['fusions']==864 and proof['unfused_padding']==27171
 assert proof['fresh_tensor_rank3_children']==3 and len(proof['mutation_controls'])==10
 template=json.loads(gzip.decompress((out/'fusion/admission/GLOBAL-TEMPLATE.json.gz').read_bytes()))
 assert sha256(gzip.decompress((out/'fusion/admission/GLOBAL-TEMPLATE.json.gz').read_bytes())).hexdigest()==raw['template_sha256']
 stable=science(template);write(out/'SCIENCE-TEMPLATE.json',stable)
 supplier=science(raw);supplier['template_sha256']=semantic_hash(stable)
 supplier['template_hash_kind']='SHA256 canonical JSON plus LF after deleting only source_hashes provenance fields; full fresh raw source binding retained in pipeline outputs.'
 write(out/'complex-supplier.json',supplier)
 priced=read(signed/'composition/baseline/replay/unsplit-bit/kappa-input.json');finite=read(signed/'validation/FINITE.json')
 assert finite['coefficient']==56223565818967 and finite['payload_prefix_bits']==71
 result=assembly.run(paths['baseline'],paths['bit-parent'],priced,finite,supplier);write(out/'assembly.json',result)
 assert result['kappa']==source['kappa']and result['binding']=='complex'
 assert result['eta']==source['eta']and result['beta']==source['beta']
 assert result['outer_cutoffs']['common_cutoff']==source['outer_common_log2_cutoff']
 selection=read(out/'fusion/candidate/selection.json')
 validation=dict(status='PASS_FRESH_HETEROGENEOUS_FUSION_AND_SIGNED_SEVEN_STAGE_COMPOSITION',candidate_sha256=source['candidate_sha256'],
  complex_b=raw['b'],bit_c=priced['bit_coarse'],kappa=result['kappa'],signed_bit_coefficient=finite['coefficient'],
  exact_live_columns=proof['exact_live_columns'],complete_existing_phase_edges=proof['complete_existing_phase_edges'],
  fusions=proof['fusions'],unfused_padding=proof['unfused_padding'],rank_mass=proof['rank_mass'],
  live=proof['live'],physical=proof['physical'],profile=proof['profile'],finite_invoice=proof['finite_invoice'],
  local_scalar_macros=proof['local_scalar_macros'],local_real_component_primitives=proof['local_real_component_primitives'],
  mutation_controls=proof['mutation_controls'],selection_sha256=semantic_hash(selection),
  science_template_sha256=semantic_hash(stable),fusion_phases_sha256=digest(out/'fusion/admission/FUSION-PHASES.json'),
  source_inputs_sha256={name:digest(out/'sources'/name/'INPUTS.json')for name in ['pr390','pr394']},
  output_sha256={name:digest(out/name)for name in ['complex-supplier.json','assembly.json']},
  outer_common_log2_cutoff=result['outer_cutoffs']['common_cutoff'],
  scope='Source-template finite evidence: complete local rational lowering, exact tensor phases including both exterior occupancies, endpoint flags, owners, banks, finite invoices, both moment engines, eight counted bit continuations and 47 outer inequalities. Mixed local/exterior compiler and whole correlated-bank chronological substitution remain conditional, as do all-size chart, precision, recovery, restored-row, analytic and stage-specific dominating C_full interfaces. This is not a separately materialized astronomical global IR or a new unconditional theorem.')
 return validation
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('output',type=Path)
 for name,directory in NAMES.items():parser.add_argument('--'+name,type=Path,default=HERE.parent/directory)
 a=parser.parse_args();out=a.output.resolve();paths={name:getattr(a,name.replace('-','_')).resolve()for name in NAMES}
 assert not out.exists()
 for p in [HERE,*paths.values()]:assert not out.is_relative_to(p)
 for p in [out,HERE,*paths.values(),Path(sys.executable).resolve()]:assert not any(c.isspace()for c in str(p))
 check_sources(paths);out.mkdir(parents=True)
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHON=sys.executable)
 for key in ['PYTHONOPTIMIZE','PR315','CX_PINS','CX_SOURCE_PINS','CX_RECORD','CX_RECEIPT','B3_OUT']:env.pop(key,None)
 env['PATH']=str(Path(sys.executable).parent)+os.pathsep+env.get('PATH','')
 def run(name,args):
  print('CHECK',name,flush=True)
  with (out/(name+'.log')).open('w')as log:subprocess.run([sys.executable,'-B',*map(str,args)],env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
 args=[paths['ordinary']/'verify.py',out/'ordinary']
 for name,p in paths.items():
  if name!='ordinary':args+=['--'+name,p]
 run('full-fresh-ordinary-and-signed',args)
 pr390,pr394=source_adapter.prepare(paths['complex'],paths['bit-parent'],paths['ordinary'],out/'ordinary/complex',paths['far'],paths['composition'],out/'sources')
 run('heterogeneous-endpoint-admission',[HERE/'hetero_replay.py',pr390,out/'ordinary/complex',out/'ordinary/signed',paths['baseline'],paths['bit-parent'],out/'hetero'])
 run('fusion-admission',[HERE/'fusion_replay.py',pr390,pr394,out/'ordinary/complex',out/'hetero',out/'ordinary/signed',paths['baseline'],paths['bit-parent'],out/'fusion'])
 validation=validate(out,paths);assert validation==read(HERE/'EXPECTED.json');write(out/'VALIDATION.json',validation)
 # Every generated native source and parent file must remain unchanged.
 h=load('final_hetero_sources',HERE/'hetero_replay.py');h.manifest(pr390)
 assert source_adapter.inventory(pr394)==read(pr394/'INPUTS.json')['files']
 check_sources(paths)
 receipt=dict(status=validation['status'],kappa=validation['kappa'],complex_b=validation['complex_b'],
  candidate_sha256=validation['candidate_sha256'],package_manifest_sha256=digest(HERE/'MANIFEST.sha256'),
  validation_sha256=digest(out/'VALIDATION.json'),all_frozen_sources_unchanged=True,
  source_input_sha256=validation['source_inputs_sha256'],fresh_stages=['ordinary-and-signed','heterogeneous-endpoints','fusion','smaller-positive-slack-assembly'],scope=validation['scope'])
 write(out/'RECEIPT.json',receipt);print(receipt['status'],receipt['kappa'],flush=True)
if __name__=='__main__':main()
