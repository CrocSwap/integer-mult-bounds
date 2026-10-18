"""Semantic regenerated-artifact check for a T74 package (PR1319 family).

Regenerated owners (reconstruct.py) and parent (lift_parent.py) are compared to the pinned package files by
semantic hash = sha256 of canonical JSON (sort_keys, compact) of the decompressed payload, NOT by container bytes.
PLAN.json is the only file allowed to differ, and only in fields that are container (gzip-byte) hashes; each such field
must equal sha256 of the corresponding regenerated container, and every content-hash field in PLAN must equal the
semantic payload hash of the regenerated file. Container-byte agreement is reported separately (portability witness).
usage: t74_semantic_regen.py PKG OWNERS_DIR PARENT_DIR OUT.json"""
import gzip, hashlib, json, sys
from pathlib import Path
P, O, Q, out = map(Path, sys.argv[1:5])
def payload(p): b = p.read_bytes(); return gzip.decompress(b) if p.suffix == '.gz' else b
def obj(p): return json.loads(payload(p))
def sem(p): return hashlib.sha256(json.dumps(obj(p), sort_keys=True, separators=(',', ':')).encode()).hexdigest()
def raw(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def paysha(p): return hashlib.sha256(payload(p)).hexdigest()
def diff(x, y, pre=''):
    if isinstance(x, dict) and isinstance(y, dict):
        return [d for k in sorted(set(x) | set(y)) for d in (diff(x.get(k), y.get(k), pre + k + '.') if x.get(k) != y.get(k) else [])]
    return [pre.rstrip('.')]
rows, ok = {}, True
for d, names in ((O, ['OWNERS.json.gz', 'ORDER.json', 'DISPATCH.json', 'PROFILE.json']),
                 (Q, ['GLOBAL-TEMPLATE.json.gz', 'CONSTRUCTION.json', 'PLAN.json'])):
    for n in names:
        r = dict(container_equal=raw(d / n) == raw(P / n), semantic_equal=sem(d / n) == sem(P / n),
                 semantic_sha256=sem(P / n), regenerated_semantic_sha256=sem(d / n))
        if n == 'PLAN.json': r['paths_differing'] = diff(obj(d / n), obj(P / n))
        rows[str(d.name) + '/' + n] = r
pinned, regen = obj(P / 'PLAN.json'), obj(Q / 'PLAN.json')
CONTAINER = {'assignment_sha256': 'OWNERS.json.gz', 'replica_lift.owners_file_sha256': 'OWNERS.json.gz'}
CONTENT = {'assignment_content_sha256': (O / 'OWNERS.json.gz', paysha)}
def get(x, path):
    for k in path.split('.'): x = x[k]
    return x
checks = {}
for path, n in CONTAINER.items():
    checks['pinned ' + path + ' == sha(pinned container)'] = get(pinned, path) == raw(P / n)
    checks['regenerated ' + path + ' == sha(regenerated container)'] = get(regen, path) == raw(O / n)
for path, (f, h) in CONTENT.items():
    checks['pinned ' + path + ' == payload sha of regenerated'] = get(pinned, path) == h(f) == get(regen, path)
checks['template content pin'] = get(pinned, 'replica_lift.parent_template_content_sha256') == get(regen, 'replica_lift.parent_template_content_sha256')
pd = rows[Q.name + '/PLAN.json']['paths_differing']
checks['PLAN differs only in container-hash fields'] = set(pd) <= set(CONTAINER)
def strip(x):
    x = json.loads(json.dumps(x)); x.pop('assignment_sha256', None); x['replica_lift'].pop('owners_file_sha256', None); return x
checks['PLAN semantic hash (container fields removed) equal'] = strip(pinned) == strip(regen)
checks['all non-PLAN semantic hashes equal'] = all(r['semantic_equal'] for k, r in rows.items() if not k.endswith('PLAN.json'))
checks['SPEC geometry equal'] = obj(Q / 'SPEC.json')['geometry'] == obj(P / 'SPEC.json')['geometry']
# negative control: alter one role, semantic hash must change
roles = obj(P / 'OWNERS.json.gz'); roles[0] = dict(roles[0], time=roles[0]['time'] + 1)
checks['control: altered role changes semantic hash'] = hashlib.sha256(json.dumps(roles, sort_keys=True, separators=(',', ':')).encode()).hexdigest() != sem(P / 'OWNERS.json.gz')
ok = all(checks.values())
res = dict(status='PASS_T74_SEMANTIC_REGENERATED_ARTIFACTS' if ok else 'FAIL', python=sys.version.split()[0], package=str(P),
           container_bytes_all_equal=all(r['container_equal'] for r in rows.values()), checks=checks, files=rows)
Path(out).write_text(json.dumps(res, indent=1) + '\n'); print(res['status'], 'containers_equal=%s' % res['container_bytes_all_equal'])
for k, v in checks.items():
    if not v: print('FAILED:', k)
sys.exit(0 if ok else 1)
