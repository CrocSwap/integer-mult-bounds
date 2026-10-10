"""Focused replay of the inspected PR117 addition DAG and unchanged matcher."""
from pathlib import Path
import hashlib, importlib.util, json, subprocess, sys
P=Path(__file__).resolve().parent
PUB=P/'pr117-public';TREE=PUB/'tree';OUT=P/'round8-optimize-reuse117-producer-output'
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
read=lambda path:json.loads(path.read_text())
audit=read(PUB/'DOWNLOAD_AUDIT.json');inherited=read(PUB/'INHERITED_SOURCE_AUDIT.json')
commit='cbb05ce504d571546d9b7794c186a613c659c3bf'
assert audit['commit']==inherited['commit']==commit
records={r['path']:r for r in audit['files']+inherited['files']}
names=['scripts/deferred_product/replayed.py','certificates/deferred-product-complex-dag.json.gz',
 'certificates/deferred-product-complex-input.json','scripts/endpoint_gauge/match_complex_general.cpp',
 'scripts/partial_swap/binary_io.hpp']
for name in names:assert sha(TREE/name)==records[name]['sha256'],name
# replayed.py was inspected in full: stdlib only and prefix-limited writes.
# The two compiler sources are byte-identical to the previously audited matcher.
OUT.mkdir(exist_ok=True)
subprocess.run(['c++','-O3','-std=c++17',str(TREE/names[3]),'-o',str(OUT/'matcher')],check=True)
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('reuse117_producer',TREE/names[0])
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
prefix=OUT/'complex';raw=mod.build(TREE/names[1],prefix)
run=subprocess.run([str(OUT/'matcher'),str(prefix)+'.bin',str(prefix)+'.labels'],
                   capture_output=True,text=True,check=True)
(OUT/'matching.log').write_text(run.stderr)
matched=json.loads(run.stdout);expected=read(TREE/names[2])
assert all(expected[k]==value for k,value in matched.items())
assert expected['dag_sha256']==sha(TREE/names[1])
assert raw['R']==matched['baseline_R'] and matched['R']==matched['c']+matched['q']-matched['matched']
assert raw['scalar_validation']==expected['scalar_validation']
out=dict(status='PASS exact addition DAG supports, rational scatter, nondegenerate nested frames and complete legal carrier matching. Physical signed-core compatibility remains separate.',
 commit=commit,matched=matched,scalar_validation=raw['scalar_validation'],dag_sha256=sha(TREE/names[1]),
 producer_sha256=sha(TREE/names[0]),source_sha256={str((TREE/name).relative_to(P)):sha(TREE/name) for name in names},
 generated_sha256={ext:sha(Path(str(prefix)+ext)) for ext in ('.bin','.labels')})
Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ('source_sha256','matched')},indent=2))
