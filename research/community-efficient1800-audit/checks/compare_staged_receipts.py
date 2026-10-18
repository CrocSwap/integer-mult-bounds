"""Compare entire emitted scientific receipts, not just success markers."""
from pathlib import Path
import hashlib, json, platform, sys, time

start = time.monotonic()
P = Path('/tmp/pr-efficient1800')
pkg = P / 'sources/2841/research/t74-staged-cold-host-boundary'
raw = (P / 'check-2841.log').read_text()
decoder = json.JSONDecoder()
objects = []
position = 0
while position < len(raw):
    end = raw.find('\n', position)
    end = len(raw) if end < 0 else end
    if raw[position:position+1] in ('{', '['):
        try:
            value, consumed = decoder.raw_decode(raw[position:])
        except json.JSONDecodeError:
            pass
        else:
            objects.append(value)
            position += consumed
            if position < len(raw) and raw[position] == '\n':
                position += 1
            continue
    position = end + 1

expected = [json.loads((pkg / name).read_text()) for name in
            ('RESULT.json', 'exploration/NATURAL-BANK-RESULT.json')]
for value in expected:
    canonical = json.dumps(value, sort_keys=True)
    if sum(json.dumps(o, sort_keys=True) == canonical for o in objects) != 1:
        raise ValueError('Missing or differing full scientific receipt')
log = P / 'check-2841-supplement.log'
log.write_text('PASS: both complete primary and natural-bank receipts exactly equal committed JSON, including types and every field.\n')
receipt = dict(number=2841, head=json.loads((P/'2841.json').read_text())['headRefOid'],
    status='passed', seconds=time.monotonic()-start,
    commands=[dict(argv=[sys.executable, str(Path(__file__).resolve())], exit_code=0)],
    input_sha256={name:hashlib.sha256((P/name).read_bytes()).hexdigest() for name in
                  ('check-2841.log', 'compare_staged_receipts.py')},
    log_sha256=hashlib.sha256(log.read_bytes()).hexdigest(),
    environment=dict(python=sys.version, platform=platform.platform()),
    scope='Complete JSON comparison; no independent new circuit or inherited pricing admission.')
(P / 'check-2841-supplement.json').write_text(json.dumps(receipt, indent=2)+'\n')
print(log.read_text().strip())
