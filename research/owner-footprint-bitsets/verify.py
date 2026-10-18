#!/usr/bin/env python3
"""Full-check equivalence, repinned negative controls and portable replay."""
import argparse
from collections import defaultdict
import copy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
sp = importlib.util.spec_from_file_location('adapter', HERE / 'adapter.py')
A = importlib.util.module_from_spec(sp)
sp.loader.exec_module(A)
NATIVE = Path('research/community-k492-audit/pr622/replay/mixed-global/base/providers')


def load(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def save(path, data):
    raw = (json.dumps(data, indent=2) + '\n').encode()
    path.write_bytes(gzip.compress(raw, mtime=0) if path.suffix == '.gz' else raw)


def command(root, engine, out, optimized=False, direct=False):
    cmd = [sys.executable, '-I', '-B'] + (['-O'] if optimized else [])
    if direct:
        cmd += [str(root / A.CHECKER)]
    else:
        cmd += [str(HERE / 'adapter.py'), '--root', str(root), '--engine', engine]
    return cmd + ['--work', str(root), '--out', str(out), '--provider',
                  'ck=' + str(root / NATIVE / 'ck'), '--provider',
                  'jp8=' + str(root / NATIVE / 'jp8')]


def invoke(root, engine, out, optimized=False, direct=False):
    r = subprocess.run(command(root, engine, out, optimized, direct),
                       capture_output=True, text=True, timeout=30)
    diagnostic = r.stderr.strip().splitlines()[-1] if r.stderr.strip() else ''
    return r.returncode, r.stdout, diagnostic


def copy_inputs(root):
    for name in A.origins()['files']:
        dst = root / name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(A.ROOT / name, dst)


def repin(root):
    pkg = root / A.PACKAGE
    spec = load(pkg / 'data/SPEC.json')
    for key, file in [('plan_sha256', 'PLAN.json'), ('owners_sha256', 'OWNERS.json.gz')]:
        spec['data'][key] = hashlib.sha256((pkg / 'data' / file).read_bytes()).hexdigest()
    save(pkg / 'data/SPEC.json', spec)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, help='New validation receipt file')
    args = ap.parse_args()
    if args.out:
        A.require(not args.out.exists(), 'output must not already exist')
    A.check_pins()
    expected = (HERE / 'evidence/EXPECTED.json').read_bytes()
    rows = []
    with tempfile.TemporaryDirectory(prefix='owner masks check ') as tmp:
        root = Path(tmp) / 'relocated checkout'
        copy_inputs(root)
        # Original direct CLI and both adapters must agree, including -O runs.
        for optimized in (False, True):
            for engine, direct in [('sets', True), ('sets', False), ('masks', False)]:
                out = Path(tmp) / ('positive-%s-%s-%s.json' % (engine, optimized, direct))
                got = invoke(root, engine, out, optimized, direct)
                A.require(got == (0, 'PASS independent map and exact moments\n', ''), str(got))
                A.require(out.read_bytes() == expected, 'complete receipt differs')
                rows.append(dict(case='baseline', engine=engine, direct=direct,
                                 optimized=optimized, receipt_sha256=hashlib.sha256(expected).hexdigest()))

        pkg = root / A.PACKAGE
        original = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()}
        roles0 = load(pkg / 'data/OWNERS.json.gz')
        plan0 = load(pkg / 'data/PLAN.json')
        groups = defaultdict(list)
        for i, r in enumerate(roles0):
            groups[r['owner_replica'], r['child'], r['port']].append(i)
        pairs = [ids[:2] for ids in groups.values() if len(ids) > 1]
        overlap_i, overlap_j = pairs[91 % len(pairs)]
        spare = []
        for key, ids in groups.items():
            cap = plan0['windows'][str(key[0]) + ',' + str(key[1])][0]
            i = max(ids, key=lambda k: roles0[k]['offset'])
            if roles0[i]['offset'] + roles0[i]['width'] < cap:
                spare.append(i)
        gap_i = spare[91 % len(spare)]
        cases = [
            ('overlap', 'disjoint footprints'), ('gap', 'compacted prefix'),
            ('negative_offset', 'window and footprint'), ('past_capacity', 'window and footprint'),
            ('width', 'actual width'), ('duplicate_helper', 'unique helper and physical family'),
            ('family', 'physical family'), ('copy', 'copy'), ('stage', 'ordered complete call'),
            ('missing_role', 'all helper calls'), ('profile', 'independent paid profile'),
            ('candidate_moment', 'strict exact moment candidate'),
            ('predecessor_moment', 'strict exact moment PR623'),
            ('native_orientation', 'both actual orientations'),
            ('geometry', 'unchanged inherited physical geometry'),
            ('plan_pin', 'plan pin'), ('owner_pin', 'owner pin'),
            ('checker_source', 'source/input pin mismatch'),
            ('interval_source', 'source/input pin mismatch'),
            ('shuffled_roles', None),
        ]
        for case, failure in cases:
            for name, data in original.items():
                (root / name).write_bytes(data)
            roles = copy.deepcopy(roles0)
            plan = copy.deepcopy(plan0)
            spec = load(pkg / 'data/SPEC.json')
            if case == 'overlap':
                roles[overlap_j]['offset'] = roles[overlap_i]['offset']
            elif case == 'gap':
                roles[gap_i]['offset'] += 1
            elif case == 'negative_offset':
                roles[91]['offset'] = -1
            elif case == 'past_capacity':
                r = roles[91]
                cap = plan['windows'][str(r['owner_replica']) + ',' + str(r['child'])][0]
                r['offset'] = cap - r['width'] + 1
            elif case == 'width':
                roles[91]['width'] += 1
            elif case == 'duplicate_helper':
                roles[92] = copy.deepcopy(roles[91])
            elif case in ('family', 'copy', 'stage'):
                roles[91][case] += 1000000 if case == 'family' else 1
            elif case == 'missing_role':
                roles.pop(91)
            elif case == 'profile':
                plan['profile']['1'] -= 1
            elif case == 'candidate_moment':
                spec['expected']['complex_lower'] = '1/100'
            elif case == 'predecessor_moment':
                old = load(pkg / 'comparison/PR623-SPEC.json')
                old['expected']['complex_lower'] = '1/100'
                save(pkg / 'comparison/PR623-SPEC.json', old)
            elif case == 'native_orientation':
                path = root / NATIVE / 'ck/LOCAL-PROGRAMS.json.gz'
                programs = load(path)
                event = next(e for e in programs['backward'] if e[0] in ('climb', 'center'))
                event[-1] += 1
                save(path, programs)
                hashes = load(pkg / 'comparison/PR622-NATIVE-HASHES.json')
                hashes['ck/LOCAL-PROGRAMS.json.gz'] = hashlib.sha256(path.read_bytes()).hexdigest()
                save(pkg / 'comparison/PR622-NATIVE-HASHES.json', hashes)
            elif case == 'geometry':
                plan['windows']['0,0'][0] += 1
            elif case == 'shuffled_roles':
                random.Random(91).shuffle(roles)
            save(pkg / 'data/OWNERS.json.gz', roles)
            save(pkg / 'data/PLAN.json', plan)
            save(pkg / 'data/SPEC.json', spec)
            repin(root)
            if case in ('plan_pin', 'owner_pin'):
                pin = 'plan_sha256' if case == 'plan_pin' else 'owners_sha256'
                spec = load(pkg / 'data/SPEC.json')
                spec['data'][pin] = '0' * 64
                save(pkg / 'data/SPEC.json', spec)
            if case in ('checker_source', 'interval_source'):
                path = root / (A.CHECKER if case == 'checker_source' else A.INTERVALS)
                path.write_bytes(path.read_bytes() + b'\n# source drift control\n')
            results = []
            for engine in ('sets', 'masks'):
                out = Path(tmp) / (case + '-' + engine + '.json')
                result = invoke(root, engine, out)
                if failure is None:
                    A.require(result[0] == 0 and out.read_bytes() == expected, case + ': positive control')
                else:
                    matches = (result[2].startswith('ValueError: ' + failure) if case.endswith('_source')
                               else result[2] == 'ValueError: ' + failure)
                    A.require(result[0] != 0 and matches and not out.exists(),
                              case + ': expected ' + failure + ', got ' + str(result))
                results.append(result)
            A.require(results[0] == results[1], case + ': acceptance or diagnostic changed')
            rows.append(dict(case=case, expected='reject' if failure else 'accept',
                             diagnostic=results[0][2], engines_agree=True))
    A.check_pins()
    receipt = dict(status='PASS_OWNER_FOOTPRINT_MASKS', baseline_runs=6,
                   negative_controls=19, positive_controls=1, controls=rows,
                   seed=91, overlap_rows=[overlap_i, overlap_j], gap_row=gap_i,
                   scope='Pinned independent owner checker only; archived native artifacts, no cold supplier rebuild.')
    if args.out:
        with args.out.open('x') as f:
            json.dump(receipt, f, indent=2)
            f.write('\n')
    print('PASS_OWNER_FOOTPRINT_MASKS baseline_runs=6 negative_controls=19 positive_controls=1')


if __name__ == '__main__':
    main()
