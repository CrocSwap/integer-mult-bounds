"""Replay source-closed finite cross-copy witnesses without modifying evidence."""
from pathlib import Path
from hashlib import sha256
import json
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent

def read(path):
    return json.loads(path.read_text())

def digest(path):
    return sha256(path.read_bytes()).hexdigest()

manifest = read(HERE / 'SOURCE-MANIFEST.json')['files']
for name, expected in manifest.items():
    assert digest(HERE / name) == expected, name
derived = HERE / 'derived'
if derived.exists():
    shutil.rmtree(derived)
shutil.copytree(HERE / 'evidence', derived / 'replay')
replay = derived / 'replay'
operator = replay / 'experiments/architecture/cross-copy-operator'
inventory = replay / 'experiments/architecture/cross-copy-inventory'
checks = []
for script, output in ((operator / 'check.py', operator / 'RESULT.json'),
                       (operator / 'encoded.py', operator / 'ENCODED.json'),
                       (operator / 'flags.py', operator / 'FLAGS.json'),
                       (inventory / 'bind_split.py', inventory / 'BOUND-SPLITS.json'),
                       (operator / 'actual_gate.py', operator / 'ACTUAL-FIRST-LAST.json'),
                       (inventory / 'spectator_address_gate.py', inventory / 'SPECTATOR-ADDRESS-GATE.json')):
    before = read(output)
    run = subprocess.run([sys.executable, '-B', str(script)], cwd=script.parent,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    assert run.returncode == 0, (script.name, run.stdout)
    after = read(output)
    reviewed_scope_extension = False
    if script.name == 'spectator_address_gate.py' and after.get('scope') != before.get('scope'):
        # The frozen receipt adds a reviewed domain caveat to the producer's prose.
        assert before['scope'].startswith(after['scope'] + ' Assumes logical and each physical stream')
        after['scope'] = before['scope']
        reviewed_scope_extension = True
    assert after == before, (script.name, 'reconstructed fields differ from frozen evidence')
    checks.append({'script': script.name, 'status': after['status'], 'all_computed_fields_match': True,
                   'frozen_scope_extension_reviewed': reviewed_scope_extension})
for name, expected in manifest.items():
    assert digest(HERE / name) == expected, name
result = {'status': 'PASS_SOURCE_CLOSED_SCOPED_CROSS_COPY_REPLAY', 'checks': checks,
          'all_bound_bytes_unchanged': True, 'source_files_verified': len(manifest),
          'source_manifest_sha256': digest(HERE / 'SOURCE-MANIFEST.json'),
          'scope': 'Specified finite full-stream, fixed encoding and selector gates; constructive terminal encoding. No full supplier, compiler admission, broad impossibility or improved score.'}
(derived / 'RESULT.json').write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
print(json.dumps(result, sort_keys=True))
