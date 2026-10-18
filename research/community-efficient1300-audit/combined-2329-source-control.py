import pathlib,importlib.util,tempfile,shutil,json
P=pathlib.Path('/tmp/pr-efficient1300');root=P/'sources/2329';pkg=root/'research/clifford-reciprocal-basis-obstruction'
s=importlib.util.spec_from_file_location('binding2329',pkg/'verify.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
with tempfile.TemporaryDirectory(prefix='pr2329-source-control-') as td:
 r=pathlib.Path(td);p=r/'research/clifford-reciprocal-basis-obstruction';p.mkdir(parents=True)
 shutil.copyfile(pkg/'SOURCES.json',p/'SOURCES.json')
 for name in v.INPUTS|{v.KERNEL}:
  f=r/name;f.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/name,f)
 before=v.check_sources(r,p)
 f=r/v.KERNEL;f.write_bytes(f.read_bytes()+b'\n# deliberate source drift\n')
 after=v.check_sources(r,p)
 if before!=after:raise RuntimeError('Expected missing binding not reproduced')
 result={'number':2329,'head':json.load(open(P/'2329.json'))['headRefOid'],'finding':'Runtime oracle source drift is no longer rejected by check_sources; dense.py still imports that oracle. Previous kernel-corruption control was redirected to unrelated README.','source':v.KERNEL,'source_check_before':before,'source_check_after':after}
 (P/'combined-2329-source-control.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
