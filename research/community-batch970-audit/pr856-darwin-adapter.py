"""Independent macOS replay of PR856. Does not attest its Linux binary pin."""
import importlib.util,pathlib,subprocess,json,hashlib,os,resource,shutil
r=pathlib.Path('/tmp/integer-mult-queue-20261013');p=r/'research/r420-scatter-lifecycle';out=pathlib.Path('/tmp/batch970-pr856-darwin');out.mkdir(exist_ok=False)
s=importlib.util.spec_from_file_location('lifecycle',p/'check.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
lean=pathlib.Path('/Users/colkitt/.elan/toolchains/leanprover--lean4---v4.21.0/bin/lean');root=lean.parent.parent
version=subprocess.check_output([str(lean),'--version'],text=True).strip();assert 'version 4.21.0,' in version and 'commit 6741444a63ee' in version
manifest=v.bind(r);core=json.loads((r/manifest['core_manifest']).read_text());assert v.sha(r/manifest['core_manifest'])==v.CORE_MANIFEST_SHA
records=[]
for mod in core['ordered_modules']:
 src=root/mod['source']['file'];obj=root/mod['object']['file'];assert v.sha(src)==mod['source']['sha256'],mod['module'];assert obj.is_file()
 records.append({'module':mod['module'],'source':{'path':str(src.relative_to(root)),'sha256':v.sha(src)},'object':{'path':str(obj.relative_to(root)),'sha256':v.sha(obj)}})
assert len(records)==317
# Darwin RLIMIT_AS cannot implement the authored Linux virtual-memory cap.
# Retain CPU and wall-clock limits; use a separately recorded uncapped-memory replay.
def limits():
 os.setsid();resource.setrlimit(resource.RLIMIT_CPU,(60,62))
v.limits=limits
receipts=v.compile_modules(lean,out/'build',manifest);v.bind(r)
# The precise authored missing-proof mutation, refreshing its source hash.
changed=out/'mutated';changed.mkdir()
for f in list(p.glob('*.lean'))+[p/'MANIFEST.json']:shutil.copyfile(f,changed/f.name)
f=changed/'R420ScatterLifecycle.lean';before=':=\n  BitCopyScatter.runWindows_eq_clear_direct temp windows windows_nonempty windows_well_formed s';txt=f.read_text();assert txt.count(before)==1;f.write_text(txt.replace(before,':= by sorry'))
mut=json.loads((changed/'MANIFEST.json').read_text());mut['modules'][-1]['sha256']=v.sha(f);(changed/'MANIFEST.json').write_text(json.dumps(mut,indent=2)+'\n');v.PACKAGE=changed;v.bind(r)
try:v.compile_modules(lean,out/'mutant-build',mut)
except ValueError as e:
 assert str(e)=='nonstandard axioms: CurrentMain.R420ScatterLifecycle.exact_lifecycle',str(e)
 assert 'sorryAx' in (out/'mutant-build/R420ScatterLifecycle.log').read_text();negative=str(e)
else:raise AssertionError('Missing-proof mutant accepted')
for mod,rec in zip(core['ordered_modules'],records):assert v.sha(root/mod['source']['file'])==rec['source']['sha256'] and v.sha(root/mod['object']['file'])==rec['object']['sha256']
result={'status':'PASS_DARWIN_SEPARATE_REPLAY','linux_pinned_checker_pass':False,'memory_cap':'No RLIMIT_AS on Darwin; CPU and wall limits retained','lean_version':version,'binary_sha256':v.sha(lean),'core_modules':records,'receipts':receipts,'negative_control':negative}
(out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS macOS: four fresh modules, 28 axiom probes, actual compiled sorryAx mutant rejected; no Linux checker claim')
