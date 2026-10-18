"""Bind fresh native artifacts and specified owners to the fixed #799 geometry.

Data preparation only; unchanged dependency checkers independently admit every
result. Adapted from PR777 prepare_plan.py, with OpenAI Codex assistance.
"""
import argparse
from collections import Counter, defaultdict
import copy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def need(value, message):
    if not value:
        raise ValueError(message)


def verify_manifest(package):
    actual = {p.relative_to(package).as_posix(): sha(p) for p in package.rglob('*')
              if p.is_file() and p != package / 'MANIFEST.json' and '__pycache__' not in p.parts}
    need(actual == read(package / 'MANIFEST.json'), 'Dependency source manifest')


def add_native_arguments(parser):
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument('--native', type=Path, help='One complete native replay, named gauge44')
    selection.add_argument('--native-provider', action='append', metavar='PID=DIR',
                           help='Named complete native replay; repeat for mixed providers')
    parser.add_argument('--dispatch', type=Path, help='JSON array of 72 [stage, replica, provider] rows')


def selected_native_directories(args):
    if args.native is not None:
        need(args.dispatch is None, 'Use named providers for explicit dispatch')
        return {'gauge44': args.native.resolve()}
    result = {}
    for item in args.native_provider:
        pid, separator, directory = item.partition('=')
        need(separator and re.fullmatch(r'[a-z][a-z0-9_]*', pid) and pid not in result,
             'Unique simple provider names required')
        result[pid] = Path(directory).resolve()
    need(args.dispatch is not None, 'Explicit dispatch required for named providers')
    return result


def selected_dispatch(args, providers):
    rows = read(args.dispatch) if args.dispatch else [[s, r, 'gauge44'] for s in range(9) for r in range(8)]
    need(type(rows) is list and len(rows) == 72, 'Exactly 72 dispatch rows required')
    result = {}
    for row in rows:
        need(type(row) is list and len(row) == 3, 'Dispatch row shape')
        stage, replica, pid = row
        need(type(stage) is int and type(replica) is int and type(pid) is str
             and 0 <= stage < 9 and 0 <= replica < 8 and pid in providers, 'Dispatch row domain')
        need((stage, replica) not in result, 'Duplicate dispatch invocation')
        result[stage, replica] = pid
    need(set(result) == {(s, r) for s in range(9) for r in range(8)}, 'Complete dispatch invocation census')
    need(set(result.values()) == set(providers), 'Every named provider must be used')
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ('dependency', 'out'):
        ap.add_argument('--' + name, type=Path, required=True)
    add_native_arguments(ap)
    ap.add_argument('--owners', type=Path, help='Explicit gzipped owner rows; defaults to the dependency map')
    args = ap.parse_args()
    dep, out = [getattr(args, name).resolve() for name in ('dependency', 'out')]
    natives = selected_native_directories(args)
    dispatch = selected_dispatch(args, natives)
    owners_path = (args.owners or dep / 'data/OWNERS.json.gz').resolve()
    need(owners_path.suffix == '.gz', 'Supply a gzipped JSON owner map')
    owners_blob = owners_path.read_bytes()
    owners_sha256 = hashlib.sha256(owners_blob).hexdigest()
    need(not out.exists(), 'New output directory required')
    need(not out.is_relative_to(dep) and not any(out.is_relative_to(n) for n in natives.values()),
         'Output must be separate')
    verify_manifest(dep)
    plan = read(dep / 'data/PLAN.json')
    original = copy.deepcopy(plan)
    need(set(original['provider_registry']) == {'gauge44'}, 'Pinned single-provider source geometry')
    module_spec = importlib.util.spec_from_file_location('identity', dep / 'code/generated_identity.py')
    identity = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(identity)
    widths_by_provider, paid_by_provider = {}, {}
    plan['provider_registry'] = {}
    for pid, native in sorted(natives.items()):
        result = read(native / 'RESULT.json')
        need(result['status'] == 'PASS_COMPLETE_NATIVE_REPLAY_UNCHANGED_CHECKERS', 'Complete native replay required')
        need(result['input_sha256']['dependency_manifest'] == sha(dep / 'MANIFEST.json'), 'Native dependency binding')
        for relative, expected in read(native / 'RECEIPT.json')['artifacts'].items():
            need(sha(native / relative) == expected, 'Native output changed: ' + relative)
        local = native / 'local'
        canonical = read(local / 'CANONICAL-WORD.json.gz')
        programs = read(local / 'LOCAL-PROGRAMS.json.gz')
        checks = read(local / 'LOCAL-CHECKS.json')
        need((canonical['v'], canonical['h'], canonical['R']) == (112, 9, 504), 'Unchanged native geometry')
        desc = copy.deepcopy(original['provider_registry']['gauge44'])
        widths = [len(canonical['frames'][canonical['final'][h]]) - len(canonical['frames'][canonical['start'][h]])
                  for h in range(224, 728)]
        need(canonical['ports'] == desc['ports'] and canonical['centers'] == desc['centers'],
             'Unchanged ports and centers')
        need(len(widths) == 504 and all(type(w) is int and 0 < w <= 9 for w in widths),
             'Valid fresh native residual widths')
        paid = Counter(event[-1] for event in programs['forward'] if event[0] in ('climb', 'center'))
        need(paid == Counter(event[-1] for event in programs['backward'] if event[0] in ('climb', 'center')),
             'Both orientation profiles agree')
        need(dict(paid) == {int(r): n for r, n in result['profile'].items()}, 'Independent native profile')
        desc['artifact_semantic_sha256'] = identity.artifact_identities(local)
        desc['artifact_sha256'] = {name: sha(local / name) for name in desc['artifact_sha256']}
        desc['actual_paid_profile'] = dict(sorted(paid.items()))
        desc['widths'] = widths
        desc['orientation_program_sha256'] = {orientation: checks[orientation]['sha256'] for orientation in checks}
        desc['directory'] = 'providers/' + pid
        plan['provider_registry'][pid] = desc
        widths_by_provider[pid], paid_by_provider[pid] = widths, paid
    for call in plan['provider_calls']:
        call['provider'] = dispatch[call['stage'], call['replica']]
        call['local_program_sha256'] = plan['provider_registry'][call['provider']]['orientation_program_sha256'][call['orientation']]
    need(len(plan['per_call_widths']) == 72, 'Complete per-call width inventory')
    need({(c['stage'], c['replica']) for c in plan['per_call_widths']} ==
         {(s, r) for s in range(9) for r in range(8)}, 'Complete per-call width identities')
    for call in plan['per_call_widths']:
        call['widths'] = widths_by_provider[dispatch[call['stage'], call['replica']]].copy()
    rows = json.loads(gzip.decompress(owners_blob))
    used = defaultdict(set)
    helpers = defaultdict(set)
    families = defaultdict(set)
    calls = {call['time']: call for call in plan['provider_calls']}
    need(set(calls) == set(range(72)), 'Complete invocation chronology')
    stage_pair = {0: 0, 1: 0, 2: 0, 3: 1, 4: 1, 5: 2, 6: 2, 7: 3, 8: 3}
    for row in rows:
        need(all(type(row[k]) is int for k in ('time', 'helper', 'stage', 'replica', 'width',
                                              'owner_replica', 'child', 'port', 'offset', 'family', 'copy')),
             'Integer owner role fields')
        time, helper = row['time'], row['helper']
        need(type(time) is int and time in calls and type(helper) is int and 0 <= helper < 504,
             'Owner role domain')
        call = calls[time]
        need((row['stage'], row['replica']) == (call['stage'], call['replica']) == tuple(plan['order'][time]),
             'Owner invocation identity')
        need(row['width'] == widths_by_provider[call['provider']][helper],
             'Owner width equals the fresh native footprint')
        replica, child, port, offset = [row[k] for k in ('owner_replica', 'child', 'port', 'offset')]
        need(all(type(v) is int for v in (replica, child, port, offset))
             and 0 <= replica < 8 and 0 <= port < 112, 'Physical owner domain')
        window_key = f'{replica},{child}'
        need(window_key in plan['windows'], 'Known physical owner window')
        capacity, times = plan['windows'][window_key]
        need(time in times and 0 <= offset and offset + row['width'] <= capacity,
             'Owner footprint fits its invocation window')
        pair, side = plan['pairs'][str(child)], plan['sides'][str(child)]
        family = replica * 896 + (2 * pair + side) * 112 + port
        need(row['family'] == family and row['copy'] == replica * 112 + port, 'Physical family identity')
        need((replica, pair) != (row['replica'], stage_pair[row['stage']]), 'Owner does not alias active data')
        need(helper not in helpers[time] and family not in families[time], 'Unique helper and family per invocation')
        helpers[time].add(helper)
        families[time].add(family)
        key = replica, child, port
        cells = set(range(row['offset'], row['offset'] + row['width']))
        need(not used[key] & cells, 'Nonoverlapping owned coordinates')
        used[key].update(cells)
    need(len(rows) == 36288 and all(helpers[t] == set(range(504)) for t in range(72)),
         'Every native helper has exactly one owner per invocation')
    idle = Counter()
    for key, (capacity, window) in plan['windows'].items():
        replica, child = map(int, key.split(','))
        for port in range(112):
            occupied = used[replica, child, port]
            need(occupied == set(range(len(occupied))) and len(occupied) <= capacity, 'Compacted owner prefix')
            if len(occupied) < capacity:
                idle[capacity - len(occupied)] += 1
    profile = Counter()
    for call in calls.values():
        profile.update(paid_by_provider[call['provider']])
    profile.update(idle)
    need(sum(rank * count for rank, count in profile.items()) == 520704, 'Global rank mass')
    plan['profile'] = dict(sorted(profile.items()))
    plan['assignment_sha256'] = owners_sha256
    need(all(plan[key] == original[key] for key in original
             if key not in ('profile', 'provider_calls', 'provider_registry', 'per_call_widths', 'assignment_sha256')),
         'Inherited plan structure changed')
    out.mkdir(parents=True)
    (out / 'data').mkdir()
    dump(out / 'data/PLAN.json', plan)
    (out / 'data/OWNERS.json.gz').write_bytes(owners_blob)
    old_spec = read(dep / 'data/SPEC.json')
    spec = {key: copy.deepcopy(value) for key, value in old_spec.items()
            if key not in ('data', 'providers', 'expected', 'name')}
    spec.update(name='joint-frame-candidate',
                data={'plan_sha256': sha(out / 'data/PLAN.json'),
                      'owners_sha256': sha(out / 'data/OWNERS.json.gz')},
                providers={pid: {} for pid in sorted(natives)},
                dispatch=[[s, r, dispatch[s, r]] for s in range(9) for r in range(8)],
                expected={'gain_baseline_kappa': old_spec['expected']['gain_baseline_kappa']})
    pivot_path = spec['pivot_swap']['recipe']
    (out / pivot_path).parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(dep / pivot_path, out / pivot_path)
    need(sha(out / pivot_path) == spec['pivot_swap']['sha256'], 'Retained pivot recipe binding')
    dump(out / 'data/SPEC.json', spec)
    dump(out / 'REBINDING.json', {'status': 'PREPARED_FOR_UNCHANGED_GLOBAL_ADMISSION',
         'dependency_manifest_sha256': sha(dep / 'MANIFEST.json'),
         'dependency_plan_sha256': sha(dep / 'data/PLAN.json'),
         'native_receipt_sha256': {pid: sha(n / 'RECEIPT.json') for pid, n in natives.items()},
         'plan_sha256': sha(out / 'data/PLAN.json'), 'owners_sha256': sha(out / 'data/OWNERS.json.gz'),
         'source_owners_sha256': sha(dep / 'data/OWNERS.json.gz'),
         'native_widths': widths_by_provider,
         'width_changes': {pid: [[h, old, new] for h, (old, new) in
                           enumerate(zip(original['provider_registry']['gauge44']['widths'], widths)) if old != new]
                           for pid, widths in widths_by_provider.items()},
         'local_profiles': {pid: dict(paid) for pid, paid in paid_by_provider.items()},
         'provider_counts': dict(Counter(dispatch.values())), 'idle_profile': dict(idle), 'global_profile': dict(profile),
         'changed_plan_fields': ['profile', 'provider_calls.provider', 'provider_calls.local_program_sha256', 'provider_registry',
                                'per_call_widths.widths', 'assignment_sha256'],
         'scope': 'Data rebinding only. Complete independent native replay already passed. Discovery, strict global admission, independent owners/moments and outer checks are required separately.'})
    print('PREPARED_CANDIDATE', json.dumps(dict(profile)))


if __name__ == '__main__':
    main()
