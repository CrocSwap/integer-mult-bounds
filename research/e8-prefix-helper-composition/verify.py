"""Fresh signed-bit baseline plus source-bound PR390 prefix/helper composition.
Usage: python -B verify.py FRESH_OUTPUT_DIRECTORY. Assertions and Python 3.12+ required.
Prepared with OpenAI Codex assistance; Apache-2.0, inherited notices apply.
"""
from pathlib import Path
from hashlib import sha256
import argparse,importlib.util,json,os,subprocess,sys
import complex_supplier
assert __debug__ and sys.version_info >= (3,12)
HERE=Path(__file__).resolve().parent
NAMES={'signed':'e8-bit-signed-validation','composition':'e8-far-helper-composition',
       'baseline':'e8-nine-stage-composition','bit':'e8-bit-helper-reuse',
       'bit-parent':'e8-bit-seven-stage','complex':'nine-stage-complex-e8',
       'far':'e8-complex-far-retiming'}
read=lambda p:json.loads(Path(p).read_text())
digest=lambda p:sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):Path(p).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def inventory(directory,manifest,count):
 directory=Path(directory).resolve();mf=directory/manifest
 assert mf.is_file() and not mf.is_symlink()
 if manifest.endswith('.json'):entries=read(mf)['files']
 else:
  rows=[line.split(None,1)for line in mf.read_text().splitlines()]
  entries={name:want for want,name in rows};assert len(entries)==len(rows)
 normalized={Path(name).as_posix():want for name,want in entries.items()}
 assert len(normalized)==len(entries);entries=normalized
 assert manifest not in entries and len(entries)+1==count
 if directory==HERE:assert all(Path(name).name==name for name in entries)
 for name in entries:
  p=Path(name);assert not p.is_absolute() and '..'not in p.parts and '.'not in p.parts
 assert not any(p.is_symlink()for p in directory.rglob('*'))
 actual={p.relative_to(directory).as_posix():digest(p)for p in directory.rglob('*')if p.is_file()and p!=mf}
 assert actual==entries,'Missing, changed, or unlisted package file: '+directory.name
 return digest(mf)

def check_sources(paths):
 assert inventory(HERE,'MANIFEST.sha256',14)
 source=read(HERE/'SOURCE.json')
 for name,pin in source['dependencies'].items():
  assert inventory(paths[name],pin['manifest'],pin['file_count'])==pin['manifest_sha256'],name
 assert digest(HERE/'prefix_source.py')==source['prefix']['source_carrier_sha256']
 assert digest(HERE/'prefix_selection.json')==source['prefix']['selection_carrier_sha256']
 return source

def validate(out,signed_out,paths):
 source=read(HERE/'SOURCE.json');prior=read(signed_out/'RECEIPT.json')
 assert prior['status']=='PASS_FULL_FRESH_COMPOSITION_AND_SIGNED_BIT_SUPPLEMENT'
 assert prior['compensated_counted_coefficient']==56223565818967
 finite=read(signed_out/'validation/FINITE.json')
 priced=read(signed_out/'composition/baseline/replay/unsplit-bit/kappa-input.json')
 supplier=complex_supplier.run(paths['complex'],out/'complex')
 write(out/'complex-supplier.json',supplier)
 assembly=load('prefix_assembly',paths['baseline']/'assembly.py').run(paths['bit-parent'],priced,finite,supplier)
 write(out/'assembly.json',assembly)
 assert supplier['b']==source['complex_b'] and assembly['kappa']==source['kappa']
 assert assembly['binding']=='complex'
 assert all(c['charged_coefficient']==56223565818967 for c in assembly['finite_cutoffs'])
 result=dict(status='PASS_FRESH_PR390_PREFIX_HELPER_COMPLEX_AND_SIGNED_SEVEN_STAGE_BIT',
   candidate_sha256=digest(out/'complex/candidate.json'),complex_b=supplier['b'],kappa=assembly['kappa'],
   signed_bit_coefficient=finite['coefficient'],complex_paid_calls=sum(supplier['histogram'].values()),
   complex_live=supplier['W'],complex_row=supplier['finite_invoice']['physical_row_coefficient'],
   output_sha256={name:digest(out/name)for name in ['complex-supplier.json','assembly.json','complex/SOURCE-DIFFS.json','complex/EXTENSION.json','complex/PREFIX-SOURCE.json']},
   scope='Finite main-only target-to-target extension with exact raw-map/retained-total and frozen-response checks. The ordinary equal-endpoint nine-stage template and the corrected signed seven-stage bit supplier are freshly replayed. Inherited compressed-window, chart/compiler, arbitrary correlated dirt, precision/recovery, restored-row and analytic interfaces, including the stage-specific dominating C_full cutoff, remain conditional. No heterogeneous endpoints or nine-stage bit supplier is used.')
 transport=read(out/'complex/PREFIX-SOURCE.json')
 assert transport['status']=='PASS_EXACT_PR390_CRLF_SOURCE_RECONSTRUCTION'
 for name,key in [('prefix_source.py','source'),('prefix_selection.json','selection')]:
     native=out/'complex/prefix-native'/name
     assert digest(native)==source['prefix'][key+'_sha256']==transport['files'][name]['original_sha256']
     assert transport['files'][name]['carrier_sha256']==source['prefix'][key+'_carrier_sha256']
 result['prefix_source_transport']=transport
 assert result['candidate_sha256']==source['candidate_sha256']
 return result

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path)
 for name,directory in NAMES.items():p.add_argument('--'+name,type=Path,default=HERE.parent/directory)
 a=p.parse_args();out=a.output.resolve();paths={name:getattr(a,name.replace('-','_')).resolve()for name in NAMES}
 assert not out.exists()
 for q in [HERE,*paths.values()]:assert not out.is_relative_to(q)
 for q in [out,HERE,*paths.values(),Path(sys.executable).resolve()]:assert not any(c.isspace()for c in str(q))
 check_sources(paths);out.mkdir(parents=True)
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHON=sys.executable)
 for key in ['PYTHONOPTIMIZE','PR315','CX_PINS','CX_SOURCE_PINS','CX_RECORD','CX_RECEIPT','B3_OUT']:env.pop(key,None)
 env['PATH']=str(Path(sys.executable).parent)+os.pathsep+env.get('PATH','')
 def run(stage,args):
  print('CHECK',stage,flush=True)
  with (out/(stage+'.log')).open('w')as log:subprocess.run([sys.executable,'-B',*map(str,args)],env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
 args=[paths['signed']/'verify.py',out/'signed']
 for name,path in paths.items():
  if name!='signed':args+=['--'+name,path]
 run('full-fresh-signed-bit-baseline',args)
 run('source-bound-prefix-complex',[HERE/'replay.py',paths['complex'],paths['far'],paths['composition'],out/'complex'])
 result=validate(out,out/'signed',paths)
 expected=read(HERE/'EXPECTED.json');assert result==expected
 write(out/'VALIDATION.json',result);check_sources(paths)
 receipt=dict(status=result['status'],kappa=result['kappa'],complex_b=result['complex_b'],
   candidate_sha256=result['candidate_sha256'],package_manifest_sha256=digest(HERE/'MANIFEST.sha256'),
   signed_receipt_sha256=digest(out/'signed/RECEIPT.json'),complex_verification_sha256=digest(out/'complex/VERIFICATION.json'),
   validation_sha256=digest(out/'VALIDATION.json'),all_frozen_sources_unchanged=True,scope=result['scope'])
 write(out/'RECEIPT.json',receipt);print(receipt['status'],receipt['kappa'],flush=True)
if __name__=='__main__':main()
