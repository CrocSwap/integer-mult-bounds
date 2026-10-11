"""Verify source bytes and scoped tiny witnesses; no global supplier claim."""
from pathlib import Path
import hashlib,json,subprocess,sys
HERE=Path(__file__).resolve().parent
manifest=json.loads((HERE/'MANIFEST.json').read_text())
for name,expected in manifest.items():
    assert hashlib.sha256((HERE/name).read_bytes()).hexdigest()==expected,name
for script in ['sources/pr250/verify_query_retention.py','cache_toy.py']:
    run=subprocess.run([sys.executable,'-B',str(HERE/script)],capture_output=True,text=True)
    assert run.returncode==0,run.stdout+run.stderr
    print(run.stdout.strip())
print(json.dumps({'status':'PASS_SOURCE_PINNED_COLLABORATION_WITNESSES','files':len(manifest),
                  'scope':'Source integrity and tiny algebra witnesses; no global admission or improved score.'}))
