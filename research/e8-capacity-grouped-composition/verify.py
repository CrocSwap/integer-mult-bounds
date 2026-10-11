"""Fresh grouped215 capacity plus fifteen enlargements and signed nine-stage composition.
Usage: python -B verify.py NEW_OUTPUT. Python3.12+, C++17 and assertions required.
Prepared with OpenAI Codex assistance; Apache-2.0, inherited notices apply.
"""
from pathlib import Path
from hashlib import sha256
import argparse,json,os,subprocess,sys
if not __debug__ or sys.version_info<(3,12):raise SystemExit('Python 3.12+ with assertions enabled is required')
sys.dont_write_bytecode=True
import compose,capacity_source,replicas64,enlargement_source,enlarged_runtime
HERE=Path(__file__).resolve().parent
NAMES={'parent':'e8-donor-prefix-composition','enlarged':'e8-enlarged-sequential-composition','shared':'e8-shared-donor-normalization-composition','response':'e8-response-normalization-composition','windows':'e8-two-window-frame-extension','six':'e8-six-edit-frame-extension','frame':'e8-signed-prefix-frame-extension','signed25':'e8-signed-prefix-fusion','fusion':'e8-hetero-fusion-composition','ordinary':'e8-prefix-helper-composition','signed':'e8-bit-signed-validation','composition':'e8-far-helper-composition','baseline':'e8-nine-stage-composition','bit':'e8-bit-helper-reuse','bit-parent':'e8-bit-seven-stage','complex':'nine-stage-complex-e8','far':'e8-complex-far-retiming'}
read=lambda p:json.loads(Path(p).read_bytes())
digest=lambda p:sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):Path(p).write_text(json.dumps(x,sort_keys=True,indent=2)+'\n')
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
 for name,pin in read(HERE/'ADAPTATION.json').items():
  original=paths['parent']/name;assert digest(original)==pin['original_sha256'];text=original.read_text()
  for change in pin['literal_replacements']:
   assert text.count(change['old'])==change['count'];text=text.replace(change['old'],change['new'])
  assert sha256(text.encode()).hexdigest()==pin['derived_sha256']and text.encode()==(HERE/name).read_bytes()
 return source
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('output',type=Path)
 for name,directory in NAMES.items():parser.add_argument('--'+name,type=Path,default=HERE.parent/directory)
 a=parser.parse_args();out=a.output.resolve();paths={name:getattr(a,name.replace('-','_')).resolve()for name in NAMES}
 assert not out.exists()
 for p in [HERE,*paths.values()]:assert not out.is_relative_to(p)
 for p in [out,HERE,*paths.values(),Path(sys.executable).resolve()]:assert not any(c.isspace()for c in str(p))
 source=check_sources(paths);out.mkdir(parents=True);env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHON=sys.executable)
 for key in list(env):
  if key in ['PYTHONOPTIMIZE','PR315','B3_OUT']or key.startswith(('COMPLEX_','CX_')):env.pop(key,None)
 env['PATH']=str(Path(sys.executable).parent)+os.pathsep+env.get('PATH','')
 def run(name,args):
  print('CHECK',name,flush=True)
  with(out/(name+'.log')).open('w')as log:subprocess.run([sys.executable,'-B',*map(str,args)],env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
 args=[paths['parent']/'verify.py',out/'parent','--parent',paths['enlarged']]
 for name,p in paths.items():
  if name not in ['parent','enlarged']:args+=['--'+name,p]
 run('full-fresh-frozen-prefix208-parent',args)
 parent=read(out/'parent/RECEIPT.json')
 assert parent['status']=='PASS_FRESH_PROPAGATED_PREFIX208_AND_SIGNED_NINE_STAGE_COMPOSITION'
 assert parent['package_manifest_sha256']==source['dependencies']['parent']['manifest_sha256']
 assert(out/'parent/VALIDATION.json').read_bytes()==(paths['parent']/'EXPECTED.json').read_bytes()
 native410=out/'parent/parent/native/pr410';native409=out/'parent/parent/native/pr409/research/e8-sequential-gauges'
 native=out/'parent/normalization/source416'
 assert inventory(native410,'MANIFEST.json',193)==source['upstream410']['manifest_sha256']
 run('fresh-enlarged-capacity215-normalization',[HERE/'replay.py',native,native409,out/'parent',out/'parent/parent/parent/parent/parent/complex',out/'normalization',paths['parent']])
 changed=read(out/'normalization/RECEIPT.json')
 assert changed['status']=='PASS_FRESH_ENLARGED215_RECOMPUTED_RESPONSE_LOCAL_PHASE_T64_BANKS_AND_FINITE_INTERFACE'
 for stage in changed['stages']:assert digest(out/'normalization'/(stage['name']+'.log'))==stage['log_sha256']
 for name,want in changed['output_sha256'].items():assert digest(out/'normalization'/name)==want
 run('actual-scalar-domain-and-controls',[HERE/'gx_domain.py',out/'normalization/source423',paths['shared'],out/'parent/parent/normalization/reconstruction/candidate.json',out/'normalization/reconstruction/candidate.json',out/'normalization',out/'normalization/domain'])
 native401=out/'parent/parent/parent/parent/pr401'
 assert inventory(native401,'MANIFEST.json',136)=='5ff08a6c7b051d227fcd516542b56718ae65bca93615acfe09cb8785d8e3f43c'
 validation=compose.run(out/'normalization/source423',out/'normalization',out/'parent/parent/parent/signed9',out/'parent/parent/parent/bit9',out/'parent/parent/parent/geometry9',native401,paths['baseline'],paths['fusion'],out/'composition')
 assert validation==read(HERE/'EXPECTED.json');write(out/'VALIDATION.json',validation)
 check_sources(paths);assert inventory(native410,'MANIFEST.json',193)==source['upstream410']['manifest_sha256']
 assert inventory(native401,'MANIFEST.json',136)=='5ff08a6c7b051d227fcd516542b56718ae65bca93615acfe09cb8785d8e3f43c'
 capacity_source.check(HERE,out/'normalization/reconstruction/capacity/native')
 enlargement_source.check(HERE,out/'normalization/reconstruction/enlargement/native')
 derived423=enlarged_runtime.check(native,out/'normalization/source423',out/'normalization/reconstruction/enlargement/native')
 replica=replicas64.check(native409.parent,out/'normalization/source409-T64',out/'normalization/reconstruction/capacity/native/CONFIG422.json')
 restorer=compose.load('frozen_enlarged_native_restore',paths['enlarged']/'native_restore.py');restorer.check(paths['enlarged'],out/'parent/parent/native')
 sys.path.insert(0,str(paths['parent']));import prefix_source,runtime_adapt,propagation_source
 prefix_source.check(paths['parent'],out/'parent/source411',native410)
 derived=runtime_adapt.check(out/'parent/source411',native,out/'parent/normalization/reconstruction/propagation/native');propagation_source.check(paths['parent'],out/'parent/normalization/reconstruction/propagation/native')
 receipt=dict(status=validation['status'],kappa=validation['kappa'],complex_b=validation['complex_b'],bit_c=validation['bit_c'],candidate_sha256=validation['candidate_sha256'],package_manifest_sha256=digest(HERE/'MANIFEST.sha256'),validation_sha256=digest(out/'VALIDATION.json'),fresh_frozen_parent_receipt_sha256=digest(out/'parent/RECEIPT.json'),fresh_normalization_receipt_sha256=digest(out/'normalization/RECEIPT.json'),fresh_signed_bit_receipt_sha256=digest(out/'parent/parent/parent/signed9/RECEIPT.json'),fresh_geometry_receipt_sha256=digest(out/'parent/parent/parent/geometry9/RECEIPT.json'),restored_upstream410_manifest_sha256=digest(native410/'MANIFEST.json'),derived416_inventory_sha256=derived['derived_inventory_sha256'],derived423_inventory_sha256=derived423['derived_inventory_sha256'],replica64_configuration=replica,all_frozen_sources_unchanged=True,fresh_stages=['full-frozen-prefix208-parent-including-native-signed9-and-geometry','unchanged421-constructor-with422-and421-seven-pivot-relations','six-required-additional-A-frame-propagations-and-seven-constructor-controls','unchanged423-constructor-with-updated422-thirteen-and424-gauge838-enlargements','own-gauge891-rank-five-witness-with-unchanged-constructor','all33-final-A-B-frame-reversions-against-fresh215','recomputed-nongauged-response-and-stale-response-controls','literal-coefficient-words-and-omitted-third-halving-control','both-local-operators-and46-native-frame-controls','whole215-independent-helper-tokens','native-exact-phase-boundaries','exact-native422-configuration-over-copied409-runtime','two-sided-T64-bank-emission','independent-bank-decoder','finite-interface-reserves','exact-scalar-domain-diagnostic','two-moment-engines-and-eight-signed-bit-continuations'],scope=validation['scope'])
 write(out/'RECEIPT.json',receipt);print(receipt['status'],receipt['kappa'],flush=True)
if __name__=='__main__':main()
