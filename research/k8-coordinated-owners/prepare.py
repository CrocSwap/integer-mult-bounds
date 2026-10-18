"""Materialize unchanged PR1018 verifiers with a new frozen owner nomination.

Prepared with OpenAI Codex assistance. Apache-2.0; upstream credit in NOTICE.md.
Only PLAN, OWNERS and the expected-value SPEC change. No guard is rewritten.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
UP = ROOT / 'research/gauge44-slots'


def read(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith('.gz') else raw)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2) + '\n')


def prepare(runtime, owners, frozen_spec=None):
    assert __debug__, 'Assertions are required'
    assert not runtime.exists() and not runtime.resolve().is_relative_to(ROOT)
    runtime.mkdir(parents=True)
    plan = read(UP / 'data/PLAN.json')
    roles = read(owners)
    widths = plan['provider_registry']['gauge44']['widths']
    spec = importlib.util.spec_from_file_location('reuse', UP / 'hosting/reuse_owners.py')
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    used, _ = checker.audit_roles(roles, plan, {tuple(c): widths for c in plan['order']}, 112, 480)
    idle = Counter()
    for key, (cap, _) in plan['windows'].items():
        rep, ch = map(int, key.split(','))
        for port in range(112):
            rem = cap - len(used[rep, ch, port])
            assert 0 <= rem <= 48
            if rem:
                idle[rem] += 1
    local = {int(r): n for r, n in plan['provider_registry']['gauge44']['actual_paid_profile'].items()}
    profile = Counter({r: 72*n for r, n in local.items()})
    profile.update(idle)
    assert 73*7168 - sum(r*n for r, n in profile.items()) == 2560
    plan.update(status='NOMINATED_COORDINATED_WHOLE_CALL_OWNERS_REQUIRES_STRICT_ADMISSION',
                profile=dict(sorted(profile.items())),
                assignment_sha256=hashlib.sha256(gzip.decompress(owners.read_bytes())).hexdigest(),
                source_owners_sha256=sha(UP / 'data/OWNERS.json.gz'),
                source_plan_sha256=sha(UP / 'data/PLAN.json'),
                solver_status='Frozen candidate; no optimizer is part of admission', gap=None)
    shutil.copytree(UP / 'code', runtime / 'code', ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copytree(UP / 'inputs', runtime / 'inputs')
    shutil.copy2(UP / 'verify_global.py', runtime / 'verify_global.py')
    (runtime / 'data').mkdir()
    shutil.copy2(UP / 'data/UPSTREAM-PINS.json', runtime / 'data/UPSTREAM-PINS.json')
    shutil.copy2(owners, runtime / 'data/OWNERS.json.gz')
    dump(runtime / 'data/PLAN.json', plan)
    witness = read(frozen_spec) if frozen_spec else read(UP / 'data/SPEC.json')
    recipe = Path(witness['pivot_swap']['recipe'])
    assert not recipe.is_absolute() and '..' not in recipe.parts
    (runtime / recipe).parent.mkdir(parents=True)
    shutil.copy2(UP / recipe, runtime / recipe)
    if not frozen_spec:
        witness.update(name='k8-coordinated-whole-call-owners', providers={},
                       expected={'gain_baseline_kappa': witness['expected']['gain_baseline_kappa']})
        witness['data'] = {'plan_sha256': sha(runtime / 'data/PLAN.json'),
                           'owners_sha256': sha(owners)}
    assert witness['data'] == {'plan_sha256': sha(runtime / 'data/PLAN.json'), 'owners_sha256': sha(owners)}
    dump(runtime / 'data/SPEC.json', witness)
    copied = [UP / 'verify_global.py', *(UP / 'code').glob('*.py')]
    identities = {f.relative_to(UP).as_posix(): sha(f) for f in copied}
    assert all(sha(runtime / name) == digest for name, digest in identities.items())
    result = dict(status='PASS_NOMINATION_COMBINATORICS_NOT_ASSEMBLY_ADMISSION',
                  helper_roles=len(roles), calls=72, helpers=480, live=7168, physical=7658,
                  deficit=2560, local_profile=local, idle_profile=dict(sorted(idle.items())),
                  global_profile=dict(sorted(profile.items())),
                  upstream_verifiers_copied_without_edits=identities,
                  owners_sha256=sha(owners), plan_sha256=sha(runtime / 'data/PLAN.json'))
    dump(runtime / 'PREPARATION.json', result)
    return result


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--owners', type=Path, default=P / 'OWNERS.json.gz')
    ap.add_argument('--spec', type=Path)
    args = ap.parse_args()
    print(json.dumps(prepare(args.runtime.resolve(), args.owners.resolve(), args.spec), indent=2))
