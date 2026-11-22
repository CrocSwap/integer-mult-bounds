"""Freeze independently recomputed discovery values before strict replay."""
import argparse
import json
from pathlib import Path

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('--spec', type=Path, required=True)
ap.add_argument('--discovery', type=Path, required=True)
a = ap.parse_args()
spec = json.loads(a.spec.read_text())
for line in (a.discovery/'WITNESS-RECORD.jsonl').read_text().splitlines():
    key, value = json.loads(line)
    parts = key.split('.')
    if len(parts)>3 and parts[0]=='providers' and parts[2]=='artifacts':
        parts = parts[:3] + ['.'.join(parts[3:])]
    target = spec
    for part in parts[:-1]:
        target = target.setdefault(part, {})
    if parts[-1] in target:
        assert target[parts[-1]]==value, 'Conflicting independent recomputations: '+key
    target[parts[-1]] = value
assembly = json.loads((a.discovery/'ASSEMBLY.json').read_text())
for key in ('complex_lower','conservative_complex_lower','kappa','kappa_decimal','conservative_kappa_decimal'):
    spec['expected'][key] = assembly[key]
spec['expected']['assembly_controls_rejected'] = 69
spec['expected']['provider_counts'] = {'gauge44':333}
spec['expected']['mutations_rejected'] = 15
a.spec.write_text(json.dumps(spec, indent=2)+'\n')
print('Frozen exact witness for strict replay:', assembly['kappa_decimal'])
