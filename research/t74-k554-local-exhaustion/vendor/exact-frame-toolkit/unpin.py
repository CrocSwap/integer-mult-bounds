"""unpin:remove from a SPEC every leaf key that the discovery WITNESS-RECORD re-derives (same path rule as freeze_spec.py), so
freeze_spec only checks the record's internal consistency.  usage: python -B unpin.py SPEC.json DISCOVERY_DIR"""
import json, sys
from pathlib import Path
spec_p, disc = Path(sys.argv[1]), Path(sys.argv[2]); spec = json.loads(spec_p.read_text()); removed = 0; keys = set()
for line in (disc / 'WITNESS-RECORD.jsonl').read_text().splitlines():
    key, value = json.loads(line); parts = key.split('.')
    if len(parts) > 3 and parts[0] == 'providers' and parts[2] == 'artifacts': parts = parts[:3] + ['.'.join(parts[3:])]
    t = spec
    for part in parts[:-1]:
        t = t.get(part) if isinstance(t, dict) else None
        if t is None: break
    if isinstance(t, dict) and parts[-1] in t: del t[parts[-1]]; removed += 1
    keys.add(key)
spec_p.write_text(json.dumps(spec, indent=1) + '\n'); print('record keys', len(keys), '| removed from spec', removed)
