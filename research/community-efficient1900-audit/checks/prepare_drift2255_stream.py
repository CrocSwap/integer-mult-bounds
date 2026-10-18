from pathlib import Path
import json,hashlib,subprocess
P=Path('/tmp/pr-efficient1900');D=Path('/tmp/pr-efficient1200/sources/2255');rel='research/live-pin-drift-audit-seed5985/verify.py';src=P/'sources/2255'/rel;s=src.read_text()
start=s.index('def build_ledger():');end=s.index('\n\ndef add_provenance',start)
new='''def build_ledger():
    # Count each manifest before reading the next. Keeping all 2.5 million
    # intermediate dictionaries at once needlessly exceeds 1 GiB. Sorting
    # manifests, then their entries, preserves the original global ordering.
    pins_seen = 0
    decode_failures = 0
    manifests_seen = 0
    shapes = ('L', 'R-input', 'R-provenance', 'P')
    counts = {shape: {'match': 0, 'drift': 0, 'unresolved': 0, 'ignored': 0} for shape in shapes}
    live_drift, live_unresolved = [], []
    for path in walk_json():
        manifests_seen += 1
        try:
            node = json.loads(path.read_bytes().decode('utf-8'))
        except (UnicodeDecodeError, ValueError):
            decode_failures += 1
            continue
        found = []
        collect(node, found, 'P')
        del node
        manifest = path.relative_to(ROOT).as_posix()
        for key, digest, shape in sorted(found, key=lambda row: (row[0], row[2])):
            pins_seen += 1
            status, current = classify(key, digest)
            counts[shape][status] += 1
            if shape in ('L', 'R-input') and status in ('drift', 'unresolved'):
                row = {'manifest': manifest, 'key': key, 'recorded': digest, 'shape': shape}
                if status == 'drift':
                    row['current'] = current
                    live_drift.append(row)
                else:
                    live_unresolved.append(row)
    return {'pins_seen': pins_seen, 'manifests_seen': manifests_seen, 'counts': counts,
            'live_drift': live_drift, 'live_unresolved': live_unresolved,
            'json_decode_failures': decode_failures}
'''
s=s[:start]+new+s[end:];dest=P/'resolutions/2255'/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(s);(D/rel).write_text(s)
r=json.loads((P/'check-2255.json').read_text());r['scope']='Attempted full original revised audit; stopped by sampled descendant RSS guard before emitting a result. No audit pass or mathematical failure inferred.';(P/'check-2255-original-resource-stop.json').write_text(json.dumps(r,indent=2)+'\n');(P/'check-2255.json').unlink()
print('Prepared streaming implementation; original checked attempt retained')
