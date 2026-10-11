from pathlib import Path
import hashlib,json,subprocess,sys
if not __debug__:raise SystemExit('Assertions required')
P=Path(__file__).resolve().parent
manifest=json.loads((P/'SOURCE-MANIFEST.json').read_text())
for name,digest in manifest['files'].items():assert hashlib.sha256((P/name).read_bytes()).hexdigest()==digest,name
subprocess.run([sys.executable,'-B',str(P/'source_complex_chart.py')],check=True)
assert json.loads((P/'derived/SOURCE-COMPLEX-CHART.json').read_text())==json.loads((P/'EXPECTED-SOURCE-COMPLEX-CHART.json').read_text())
print('PASS_SOURCE_BOUND_TWO_HOST_REVIEW_WITNESS_ONLY')
