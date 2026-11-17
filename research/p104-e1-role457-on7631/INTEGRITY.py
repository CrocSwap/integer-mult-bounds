#!/usr/bin/env python3
"""Check archive bytes and canonical word pins; this does not replay science."""
import gzip, hashlib, json
from pathlib import Path
P = Path(__file__).resolve().parent
manifest = json.loads((P / 'MANIFEST.json').read_text())
files = {str(p.relative_to(P)) for p in P.rglob('*') if p.is_file()} - {'MANIFEST.json'}
if files != set(manifest['files']):
    raise SystemExit('file inventory mismatch')
for name, expected in manifest['files'].items():
    if hashlib.sha256((P / name).read_bytes()).hexdigest() != expected:
        raise SystemExit('byte mismatch: ' + name)
for side, expected in manifest['canonical_words'].items():
    obj = json.loads(gzip.decompress((P / 'words' / (side + '.json.gz')).read_bytes()))
    raw = json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise SystemExit('canonical word mismatch: ' + side)
receipt = json.loads((P / 'EXACT-RECEIPT.json').read_text())
price = json.loads((P / 'PRICE.json').read_text())
for side in ('source', 'candidate'):
    for kind, name in (('gzip', 'words/' + side + '.json.gz'), ('cert', 'certificates/' + side + '.json')):
        if hashlib.sha256((P / name).read_bytes()).hexdigest() != receipt[side + '_' + kind + '_sha256']:
            raise SystemExit('receipt binding mismatch: ' + name)
    invoice = json.loads((P / 'invoices' / (side + '.json')).read_text())
    if invoice['paid'] != price[side]['invoice']['P'] or invoice['targets'] != price[side]['invoice']['T']:
        raise SystemExit('invoice projection mismatch: ' + side)
cont = P / 'continuation'
custody = json.loads((cont / 'CUSTODY-PROJECTION.json').read_text())
projection = json.loads((cont / 'RESULT-PROJECTION.json').read_text())
audit = json.loads((cont / 'INDEPENDENT-AUDIT.json').read_text())
snapshot_bytes = (cont / 'PROTECTED-SNAPSHOT.json').read_bytes()
if hashlib.sha256(snapshot_bytes).hexdigest() != custody['protected_snapshot_sha256']:
    raise SystemExit('protected snapshot binding mismatch')
snapshot = json.loads(snapshot_bytes)
if projection['original_sha256'] != snapshot['RESULT.json'] or projection['original_sha256'] != custody['result_sha256']:
    raise SystemExit('continuation result binding mismatch')
if hashlib.sha256((cont / 'INDEPENDENT-AUDIT.json').read_bytes()).hexdigest() != custody['independent_audit_sha256']:
    raise SystemExit('independent audit binding mismatch')
if audit['observer_sha256'] != custody['original_sha256']:
    raise SystemExit('observer binding mismatch')
for name in ('MATCHED-ORDINARY.json', 'ASSEMBLY.log'):
    if hashlib.sha256((cont / name).read_bytes()).hexdigest() != snapshot[name]:
        raise SystemExit('continuation file mismatch: ' + name)
for name, digest in projection['catalogue_log_sha256'].items():
    if hashlib.sha256((cont / name).read_bytes()).hexdigest() != digest:
        raise SystemExit('catalogue log mismatch: ' + name)
assembly = 'ODD-8X9-APPLICATION-CHECKS.json'
if hashlib.sha256((cont / assembly).read_bytes()).hexdigest() != projection['assembly_sha256']:
    raise SystemExit('assembly mismatch')
print('PASS: archive bytes, word pins, receipt bindings, invoices and continuation projection bindings; no scientific replay')
