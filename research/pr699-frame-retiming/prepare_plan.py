"""Bind unchanged PR699 owners to the freshly verified frame-retimed provider.

Packaging only: admission independently checks the native contracts and every
owner role. Prepared by Tekalign with substantial OpenAI Codex assistance.
Apache-2.0; predecessor registry format and semantic identity code are PR699's.
"""
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--dependency', type=Path, required=True)
    ap.add_argument('--local', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    package = Path(__file__).resolve().parent
    pins = read(package / 'SOURCES.json')
    dep, local = args.dependency, args.local
    assert sha(dep / 'MANIFEST.json') == pins['pr699_manifest_sha256']
    assert sha(dep / 'data/PLAN.json') == pins['pr699_plan_sha256']
    assert sha(dep / 'data/OWNERS.json.gz') == pins['pr699_owners_sha256']
    plan = read(dep / 'data/PLAN.json')
    word = read(local / 'CANONICAL-WORD.json.gz')
    programs = read(local / 'LOCAL-PROGRAMS.json.gz')
    checks = read(local / 'LOCAL-CHECKS.json')
    desc = plan['provider_registry']['gauge44']
    widths = [len(word['frames'][word['final'][h]]) - len(word['frames'][word['start'][h]])
              for h in range(224, 728)]
    assert widths == desc['widths'] and word['ports'] == desc['ports']
    assert word['centers'] == desc['centers']
    paid = Counter(e[-1] for e in programs['forward'] if e[0] in ('climb', 'center'))
    assert paid == Counter(e[-1] for e in programs['backward'] if e[0] in ('climb', 'center'))
    assert paid == {1: 2556, 2: 334, 3: 430, 4: 194, 5: 56, 8: 8}
    spec = importlib.util.spec_from_file_location('identity', dep / 'code/generated_identity.py')
    identity = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(identity)
    desc['artifact_semantic_sha256'] = identity.artifact_identities(local)
    desc['artifact_sha256'] = {name: sha(local / name) for name in desc['artifact_sha256']}
    desc['actual_paid_profile'] = dict(sorted(paid.items()))
    desc['orientation_program_sha256'] = {o: checks[o]['sha256'] for o in checks}
    desc['directory'] = 'providers/gauge44'
    for call in plan['provider_calls']:
        assert call['provider'] == 'gauge44'
        call['local_program_sha256'] = checks[call['orientation']]['sha256']
    roles = read(dep / 'data/OWNERS.json.gz')
    used = defaultdict(int)
    for role in roles:
        used[role['owner_replica'], role['child'], role['port']] += role['width']
    idle = Counter()
    for key, (capacity, window) in plan['windows'].items():
        replica, child = map(int, key.split(','))
        for port in range(112):
            left = capacity - used[replica, child, port]
            assert left >= 0
            if left:
                idle[left] += 1
    assert idle == {1: 1, 3: 1, 44: 1, 48: 2396}
    profile = Counter({rank: 72 * count for rank, count in paid.items()})
    profile.update(idle)
    assert sum(rank * count for rank, count in profile.items()) == 520704
    plan['profile'] = dict(sorted(profile.items()))
    plan['status'] = 'PR699_UNCHANGED_OWNERS_WITH_EIGHT_FRAME_RETIMINGS'
    plan['source_plan_sha256'] = pins['pr699_plan_sha256']
    args.out.write_text(json.dumps(plan, indent=2) + '\n')
    print('PASS_UNCHANGED_OWNERS_FRESH_NATIVE_PLAN', dict(profile))


if __name__ == '__main__':
    main()
