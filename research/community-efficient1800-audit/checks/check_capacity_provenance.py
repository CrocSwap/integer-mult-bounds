"""Compare exported capacity-proof inputs to their exact original Git objects."""
from pathlib import Path
import hashlib, json, subprocess

P = Path('/tmp/pr-efficient1800')
R = Path('/tmp/integer-mult-efficient1100-20261015')
for number, name, manifest in [
    (2831, 'selected-numerical-arena-backing', 'INPUTS.json'),
    (2845, 'selected-caller-capacity-prefix', 'SNAPSHOTS.json'),
]:
    package = P / 'sources' / str(number) / 'research' / name
    data = json.loads((package / manifest).read_text())
    entries = list(data['files'])
    if 'runtime_original_binding' in data:
        entries.append(data['runtime_original_binding'])
    for entry in entries:
        head = entry.get('source_commit', entry.get('head', entry.get('commit')))
        source = entry.get('source_path', entry.get('original_path'))
        spec = head + ':' + source
        raw = subprocess.check_output(['git', 'show', spec], cwd=R)
        blob = subprocess.check_output(['git', 'rev-parse', spec], cwd=R, text=True).strip()
        if raw != (package / entry['path']).read_bytes():
            raise ValueError('Export differs from original Git: ' + spec)
        if hashlib.sha256(raw).hexdigest() != entry['sha256'] or blob != entry['git_blob']:
            raise ValueError('Manifest differs from original Git: ' + spec)
    receipt = dict(number=number, status='PASS', original_git_bindings=len(entries),
                   manifest_sha256=hashlib.sha256((package / manifest).read_bytes()).hexdigest(),
                   scope='Exact original Git bytes and blob identities; proof review and execution recorded separately.')
    (P / f'provenance-{number}.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt))
