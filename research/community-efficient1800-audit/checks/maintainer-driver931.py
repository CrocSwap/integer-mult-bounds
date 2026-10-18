"""Replay original PR931 supplemental controls from exact historical inputs."""
import importlib.util,pathlib,subprocess,sys,tempfile
root=pathlib.Path(__file__).resolve().parent
pkg=pathlib.Path('research/complex-factory-butterfly')
spec=importlib.util.spec_from_file_location('replay',root/pkg/'pinned_replay.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
pins=m.manifest(root/pkg/'SOURCES.json');before=m.checkout_state(root)
try:
 with tempfile.TemporaryDirectory(prefix='maintainer931 historical ') as tmp:
  dst=pathlib.Path(tmp)/'source';dst.mkdir();m.export_sources(root,dst,pins);m.copy_package(root/pkg,dst/pkg)
  for flags,script in [([], 'test_independent.py'),(['-O'],'test_independent.py'),(['-O'],'test_package.py')]:
   subprocess.run([sys.executable,'-I','-B',*flags,str(dst/pkg/script)],cwd=dst,env=m.verifier_environment(),check=True)
finally:m.unchanged(root,before)
print('PASS_MAINTAINER931 original_supplemental_controls source_checkout=unchanged')
