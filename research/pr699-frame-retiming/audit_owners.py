"""Independent literal owners, native profiles and rational moment audit.

Adapted from PR685 complex-promo4-cold72/extras/check_owner_map.py. The separate
rational interval helper is copied unchanged from PR626's
research/complex-k492-owner-repair/extras/exact_intervals.py and pinned in
SOURCES.json. No optimizer, emitter, constructor,
assembler or production moment-engine imports. Prepared for tekuuu with
substantial OpenAI Codex assistance; Apache-2.0. Predecessor credits remain
in the explicitly supplied dependency's NOTICE.md.
"""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path


def need(value, message):
    if not value:
        raise ValueError(message)


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def role_identity(rows):
    return Counter((r['time'], r['helper'], r['stage'], r['replica'], r['width']) for r in rows)


def literal_audit(plan, rows, spec, widths, local_paid, baseline_plan):
    for field in ('order', 'windows', 'pairs', 'sides'):
        need(plan[field] == baseline_plan[field], 'unchanged inherited geometry')
    need(len(plan['provider_calls']) == 72 and len(plan['order']) == 72, '72 calls')
    calls = {c['time']: c for c in plan['provider_calls']}
    need(set(calls) == set(range(72)), 'complete chronology')
    need(sorted(map(tuple, plan['order'])) == [(s, r) for s in range(9) for r in range(8)], 'complete call identities')
    dispatch = {(s, r): pid for s, r, pid in spec['dispatch']}
    need(len(spec['dispatch']) == len(dispatch) == 72, 'complete spec dispatch')
    need({(c['stage'], c['replica']): c['provider'] for c in calls.values()} == dispatch, 'spec dispatch')
    need(set(widths) == set(local_paid) == set(plan['provider_registry']) == set(dispatch.values()), 'provider census')
    need(plan['call_order'] == spec['call_order'] if 'call_order' in plan else plan['order'] == spec['call_order'], 'spec call order')
    paid = Counter()
    for t, call in calls.items():
        need((call['stage'], call['replica']) == tuple(plan['order'][t]), 'ordered provider call')
        pid = call['provider']
        need(call['orientation'] == ('forward' if call['stage'] % 2 == 0 else 'backward'), 'call orientation')
        need(plan['provider_registry'][pid]['widths'] == widths[pid], 'registry native widths')
        paid.update(local_paid[pid])
    helpers, families, cells = defaultdict(set), defaultdict(set), defaultdict(set)
    stage_pairs = {0: 0, 1: 0, 2: 0, 3: 1, 4: 1, 5: 2, 6: 2, 7: 3, 8: 3}
    cross = 0
    for row in rows:
        t, helper = row['time'], row['helper']
        need(type(t) is int and t in calls and type(helper) is int and 0 <= helper < 504, 'role domain')
        call = calls[t]
        need((row['stage'], row['replica']) == (call['stage'], call['replica']), 'ordered helper call')
        width = widths[call['provider']][helper]
        need(row['width'] == width, 'actual native width')
        rep, child, port, off = (row[k] for k in ('owner_replica', 'child', 'port', 'offset'))
        need(all(type(x) is int for x in (rep, child, port, off)) and 0 <= rep < 8 and 0 <= port < 112, 'owner domain')
        key = f'{rep},{child}'
        need(key in plan['windows'], 'known pending child')
        cap, times = plan['windows'][key]
        need(t in times, 'owner outside physical window')
        need(0 <= off and off + width <= cap, 'pending child capacity')
        pair, side = plan['pairs'][str(child)], plan['sides'][str(child)]
        family = rep * 896 + (2 * pair + side) * 112 + port
        need(row['family'] == family and row['copy'] == rep * 112 + port, 'physical family identity')
        need((rep, pair) != (row['replica'], stage_pairs[row['stage']]), 'active data alias')
        need(helper not in helpers[t], 'duplicate helper role')
        need(family not in families[t], 'same-call whole-family alias')
        helpers[t].add(helper)
        families[t].add(family)
        occupied = set(range(off, off + width))
        group = rep, child, port
        need(not cells[group] & occupied, 'overlapping pending coordinates')
        cells[group].update(occupied)
        cross += rep != row['replica']
    need(len(rows) == 36288 and all(helpers[t] == set(range(504)) for t in range(72)), 'all helper roles')
    idle = Counter()
    for key, (cap, _) in plan['windows'].items():
        rep, child = map(int, key.split(','))
        for port in range(112):
            used = cells[rep, child, port]
            need(used == set(range(len(used))), 'compacted pending prefix')
            if len(used) < cap:
                idle[cap - len(used)] += 1
    paid.update(idle)
    need(dict(paid) == {int(r): n for r, n in plan['profile'].items()}, 'literal global profile')
    need(dict(paid) == {int(r): n for r, n in spec['expected']['global_profile'].items()}, 'spec global profile')
    need(sum(r * n for r, n in paid.items()) == 520704, 'rank mass')
    return paid, idle, cross


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ('dependency', 'plan', 'owners', 'spec', 'output'):
        ap.add_argument('--' + name, type=Path, required=True)
    ap.add_argument('--provider', action='append', required=True, metavar='PID=DIR')
    args = ap.parse_args()
    dep = args.dependency.resolve()
    pins = read(dep / 'MANIFEST.json')
    dependencies = ('data/SPEC.json', 'data/PLAN.json', 'data/OWNERS.json.gz')
    for relative in dependencies:
        need(sha(dep / relative) == pins[relative], 'dependency source pin: ' + relative)
    baseline_spec, baseline_plan, baseline_rows = [read(dep / 'data' / name)
                                                  for name in ('SPEC.json', 'PLAN.json', 'OWNERS.json.gz')]
    here = Path(__file__).resolve().parent
    interval_path = here / 'exact_intervals.py'
    need(sha(interval_path) == read(here / 'SOURCES.json')['exact_intervals_sha256'], 'independent interval source pin')
    module = importlib.util.spec_from_file_location('independent_owner_intervals', interval_path)
    intervals = importlib.util.module_from_spec(module)
    module.loader.exec_module(intervals)
    spec, plan, rows = read(args.spec), read(args.plan), read(args.owners)
    need(sha(args.plan) == spec['data']['plan_sha256'], 'candidate plan pin')
    need(sha(args.owners) == spec['data']['owners_sha256'], 'candidate owner pin')
    providers = {}
    for item in args.provider:
        pid, separator, directory = item.partition('=')
        need(separator and pid and pid not in providers, 'unique PID=DIR arguments')
        providers[pid] = Path(directory).resolve()
    need(set(providers) == set(spec['providers']), 'complete native provider arguments')
    widths, paid, native_sources, native_semantics = {}, {}, {}, {}
    for pid, directory in providers.items():
        canonical = read(directory / 'CANONICAL-WORD.json.gz')
        programs = read(directory / 'LOCAL-PROGRAMS.json.gz')
        need((canonical['v'], canonical['h'], canonical['R']) == (112, 9, 504), 'native geometry')
        need(set(programs) == {'forward', 'backward'}, 'both native orientations')
        widths[pid] = [len(canonical['frames'][canonical['final'][h]]) - len(canonical['frames'][canonical['start'][h]])
                       for h in range(224, 728)]
        need(all(type(w) is int and 0 < w <= 9 for w in widths[pid]), 'positive native residual widths')
        paid[pid] = Counter(e[-1] for e in programs['forward'] if e[0] in ('climb', 'center'))
        need(paid[pid] == Counter(e[-1] for e in programs['backward'] if e[0] in ('climb', 'center')), 'equal orientation profiles')
        need(widths[pid] == spec['providers'][pid]['complete_contract']['widths'], 'spec native widths')
        need(dict(paid[pid]) == {int(r): n for r, n in spec['providers'][pid]['expected_profile'].items()}, 'spec native paid profile')
        native_sources[pid] = {name: sha(directory / name) for name in ('CANONICAL-WORD.json.gz', 'LOCAL-PROGRAMS.json.gz')}
        native_semantics[pid] = {name: hashlib.sha256(gzip.decompress((directory / name).read_bytes())).hexdigest()
                                 for name in native_sources[pid]}
        need(all(value == spec['providers'][pid]['artifact_semantic_sha256'][name]
                 for name, value in native_semantics[pid].items()), 'actual native payload binding')
    global_paid, idle, cross = literal_audit(plan, rows, spec, widths, paid, baseline_plan)
    fixed_map = False
    if len(providers) == len(baseline_spec['providers']) == 1:
        pid = next(iter(providers))
        old = next(iter(baseline_spec['providers'].values()))
        fixed_map = all(value == old['artifact_semantic_sha256'][name]
                        for name, value in native_semantics[pid].items())
        if fixed_map:
            need(role_identity(rows) == role_identity(baseline_rows), 'fixed-map invocation identity multiset')

    rejected = []
    def reject(name, changed_plan, changed_rows, expected):
        try:
            literal_audit(changed_plan, changed_rows, spec, widths, paid, baseline_plan)
        except ValueError as error:
            need(str(error) == expected, 'unexpected mutation rejection: ' + name + ': ' + str(error))
            rejected.append(dict(name=name, reason=str(error)))
        else:
            raise ValueError('accepted mutation: ' + name)

    reject('omit one role', plan, rows[:-1], 'all helper roles')
    mutant = list(rows)
    mutant[0] = dict(rows[0], width=rows[0]['width'] + 1)
    reject('wrong native width', plan, mutant, 'actual native width')
    mutant = list(rows)
    mutant[0] = dict(rows[0], family=rows[0]['family'] + 1)
    reject('wrong physical family', plan, mutant, 'physical family identity')
    row = rows[0]
    bad_key = next(key for key, (cap, times) in plan['windows'].items() if row['time'] not in times and cap >= row['width'])
    rep, child = map(int, bad_key.split(','))
    family = rep * 896 + (2 * plan['pairs'][str(child)] + plan['sides'][str(child)]) * 112 + row['port']
    mutant = list(rows)
    mutant[0] = dict(row, owner_replica=rep, child=child, family=family, copy=rep * 112 + row['port'], offset=0)
    reject('legal-size owner outside window', plan, mutant, 'owner outside physical window')
    groups = defaultdict(list)
    for index, row in enumerate(rows):
        groups[row['owner_replica'], row['child'], row['port']].append(index)
    pair = next((i, j) for group in groups.values() for i in group for j in group if i < j
                and rows[i]['offset'] + rows[j]['width'] <= plan['windows'][f"{rows[i]['owner_replica']},{rows[i]['child']}"][0])
    i, j = pair
    mutant = list(rows)
    mutant[j] = dict(rows[j], offset=rows[i]['offset'])
    reject('overlapping pending coordinates', plan, mutant, 'overlapping pending coordinates')
    same_call = defaultdict(list)
    for index, row in enumerate(rows):
        same_call[row['time'], row['width']].append(index)
    pair = next((i, j) for group in same_call.values() for i in group for j in group if i < j
                and rows[i]['offset'] + 2 * rows[i]['width'] <= plan['windows'][f"{rows[i]['owner_replica']},{rows[i]['child']}"][0])
    i, j = pair
    mutant = list(rows)
    mutant[j] = dict(rows[i], helper=rows[j]['helper'], offset=rows[i]['offset'] + rows[i]['width'])
    reject('whole-family alias with disjoint coordinates', plan, mutant, 'same-call whole-family alias')
    changed_profile = dict(plan['profile'])
    changed_profile['1'] = changed_profile.get('1', 0) + 1
    reject('underived paid profile', dict(plan, profile=changed_profile), rows, 'literal global profile')

    costs = []
    for label, endpoint in (('dependency', baseline_spec['expected']['complex_lower']),
                            ('candidate', spec['expected']['complex_lower'])):
        lower = upper = Q(0)
        exponent = Q(endpoint)
        for rank, count in global_paid.items():
            a, b = intervals.log(Q(73, rank))
            lo, hi = intervals.exp(exponent * a, exponent * b)
            lower += Q(rank * count, 73 * 7168) * lo
            upper += Q(rank * count, 73 * 7168) * hi
        need(upper < 1, 'strict exact moment: ' + label)
        costs.append(dict(endpoint=label, complex_lower=str(exponent), lower=str(lower),
                          upper=str(upper), strict_margin_lower=str(1 - upper)))
    b, kappa = Q(spec['expected']['complex_lower']), Q(spec['expected']['kappa'])
    need(kappa <= b / (1 + b), 'outer conversion')
    need(kappa > Q(baseline_spec['expected']['kappa']), 'strict improvement over dependency')
    result = dict(status='PASS_INDEPENDENT_LITERAL_OWNERS_NATIVE_PROFILE_AND_EXACT_MOMENTS',
                  calls=72, roles=len(rows), cross_replica_roles=cross,
                  provider_counts=dict(Counter(c['provider'] for c in plan['provider_calls'])),
                  profile=dict(sorted(global_paid.items())), idle=dict(sorted(idle.items())),
                  fixed_map_identity_multiset_checked=fixed_map, costs=costs, kappa=str(kappa),
                  negative_controls=rejected,
                  source_sha256=dict(plan=sha(args.plan), owners=sha(args.owners), spec=sha(args.spec),
                                     dependency_manifest=sha(dep / 'MANIFEST.json')),
                  dependency_sources={relative: sha(dep / relative) for relative in dependencies},
                  independent_intervals_sha256=sha(interval_path),
                  native_sources=native_sources, native_semantic_sha256=native_semantics,
                  scope='Finite literal roles using unchanged inherited phase windows and widths/paid children rederived from explicit native artifacts. Independent rational moment check; complete scalar, phase, wrapper, controller, coefficient and finite/outer admission remain separate obligations.')
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(result['status'], result['kappa'], flush=True)


if __name__ == '__main__':
    main()
