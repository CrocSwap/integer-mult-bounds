#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Bounded exact local, whole-owner and moment verification; full admission separate."""
import argparse
import collections
import copy
import gzip
import hashlib
import importlib.util
import json
import sys
import tempfile
import uuid
from fractions import Fraction as Q
from pathlib import Path
from common import HERE, check_inputs, read, require, sha, write


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def owners(fill, order, dispatch, widths, plan, windows):
    require(fill['columns'] == ['time', 'helper', 'owner_replica', 'child', 'port', 'offset'], 'fill format')
    require(len(fill['rows']) == 666 * 422, 'complete role count')
    providers = {(s, r): provider for s, r, provider in dispatch}
    for s, r, provider in fill['dispatch_overrides']:
        providers[s, r] = provider
    seen = set()
    families = collections.defaultdict(set)
    cells = collections.defaultdict(int)
    for time, helper, replica, child, port, offset in fill['rows']:
        require(all(type(x) is int for x in [time, helper, replica, child, port, offset]), 'integer owner labels')
        require(0 <= time < 666 and 0 <= helper < 422, 'call and helper range')
        require((time, helper) not in seen, 'duplicate helper role')
        seen.add((time, helper))
        width = widths[providers[tuple(order[time])]][helper]
        capacity, allowed = windows[f'{replica},{child}']
        require(time in allowed and 0 <= port < 112, 'strict call window')
        family = replica * 896 + (2 * plan['pairs'][str(child)] + plan['sides'][str(child)]) * 112 + port
        require(family not in families[time], 'distinct physical families')
        families[time].add(family)
        require(0 <= offset and offset + width <= capacity, 'whole-width capacity')
        mask = ((1 << width) - 1) << offset
        key = replica, child, port
        require(not cells[key] & mask, 'overlapping ownership')
        cells[key] |= mask
    require(len(seen) == 281052, 'complete helper bijection')
    idle = collections.Counter()
    for key, (capacity, _) in windows.items():
        replica, child = map(int, key.split(','))
        for port in range(112):
            bits = cells[replica, child, port]
            used = bits.bit_count()
            require(bits == (1 << used) - 1, 'contiguous owned prefix')
            if capacity > used:
                idle[capacity - used] += 1
    return idle


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--discovery', action='store_true', help='Do not require the publication/full-admission receipts')
    args = parser.parse_args()
    require(__debug__, 'Inherited mathematical assertions must be enabled')
    if args.out:
        require(not args.out.exists(), 'Output must be new')
    # -B alone does not prevent loading a stale scientific-module cache.
    sys.dont_write_bytecode = True
    sys.pycache_prefix = str(Path(tempfile.gettempdir()) / ('kappa-cache-' + uuid.uuid4().hex))
    check_inputs()
    for name, pin in read(HERE / 'BOUNDED-SOURCES.json').items():
        require(sha(HERE / name) == pin['sha256'], 'Bounded source ' + name)
        raw = (HERE / name).read_bytes()
        if pin['decompress_for_source']:
            raw = gzip.decompress(raw)
        require(hashlib.sha256(raw).hexdigest() == pin['source_sha256'], 'Retained source bytes ' + name)
    independent = load('independent_late8', HERE / 'independent_late8.py')
    window_code = load('pinned_windows', HERE / 'vendor/build_parent.py')
    engine = load('pinned_interval_engine', HERE / 'vendor/ceiling.py')
    profiles, widths, maps, reports = {}, {}, {}, {}
    original_providers = read(HERE / 'inputs/pr2588-PROVIDERS.json')
    words = {}
    for tag, provider in [('base', 'gauge44'), ('extra', 'extra')]:
        path = HERE / f'inputs/candidate/eight-alias-{tag}.json.gz'
        raw = gzip.decompress(path.read_bytes())
        require(hashlib.sha256(raw).hexdigest() == independent.CANDIDATE_CONTENT_SHA256[tag], 'Candidate content pin')
        oldraw = gzip.decompress((HERE / f'inputs/pr2588-{tag}.json.gz').read_bytes())
        require(hashlib.sha256(oldraw).hexdigest() == independent.SOURCE_CONTENT_SHA256[tag], 'Comparison word pin')
        word, old = json.loads(raw), json.loads(oldraw)
        report, start, end = independent.check_frames(word)
        before, old_start, old_end = independent.check_frames(old)
        require({k: report['profile'].get(k, 0) - before['profile'].get(k, 0)
                 for k in set(report['profile']) | set(before['profile'])
                 if report['profile'].get(k, 0) != before['profile'].get(k, 0)} == {1: -4, 7: -4, 8: 4}, 'Entire local paid delta')
        report['cleanup_events'] = independent.check_cleanup(word)
        report['algebra'] = independent.algebra(word)
        live = sorted(set(range(224, 704)) - set(word['removed']))
        oldlive = sorted(set(range(224, 704)) - set(old['removed']))
        widths[provider] = [independent.dm(end[r]) - independent.dm(start[r]) for r in live]
        oldwidths = [independent.dm(old_end[r]) - independent.dm(old_start[r]) for r in oldlive]
        require(oldwidths == original_providers[provider]['widths'], 'Source physical widths')
        pools = collections.defaultdict(list)
        for index, width in enumerate(widths[provider]):
            pools[width].append(index)
        require(collections.Counter(oldwidths) == collections.Counter(widths[provider]), 'Identical helper inventory')
        maps[provider] = {i: pools[width].pop(0) for i, width in enumerate(oldwidths)}
        require(sorted(maps[provider].values()) == list(range(422)), 'Helper-index bijection')
        require(all(independent.dm(old_start[oldlive[i]]) == independent.dm(start[live[j]]) and
                    independent.dm(old_end[oldlive[i]]) == independent.dm(end[live[j]])
                    for i, j in maps[provider].items()), 'Matched entrance and terminal dimensions')
        profiles[provider] = report['profile']
        reports[tag] = report
        words[tag] = word
    require(maps['gauge44'] == maps['extra'], 'Common helper permutation')
    require(profiles['gauge44'] == profiles['extra'], 'Common local profile')
    source_order = read(HERE / 'inputs/pr2673/ORDER.json')
    require(source_order == sorted([[s, r] for s in range(9) for r in range(74)],
                            key=lambda c: (8*c[0] + 2*c[1] + [-10, -1, -5, -8, 1, 0, 0, 0, 0][c[0]], c[0], c[1])), 'Exact credited PR2673 priority order')
    from packing import generate as generate_packing
    fill, order = generate_packing()
    plan = read(HERE / 'inputs/source-PLAN.json.gz')
    windows, _ = window_code.actual_windows(read(HERE / 'inputs/source-GLOBAL-TEMPLATE.json.gz'), order)
    dispatch = read(HERE / 'inputs/pr2673/DISPATCH.json')
    before_idle = owners(fill, order, dispatch, {p: d['widths'] for p, d in original_providers.items()}, plan, windows)
    for row in fill['rows']:
        row[1] = maps['gauge44'][row[1]]
    idle = owners(fill, order, dispatch, widths, plan, windows)
    require(idle == before_idle, 'Index permutation preserves every physical width')
    profile = collections.Counter(idle)
    for rank, count in profiles['gauge44'].items():
        profile[rank] += 666 * count
    profile = dict(sorted(profile.items()))
    require(sum(r*n for r, n in profile.items()) == 4816512, 'Complete rank mass')
    comparison = read(HERE / 'inputs/pr2673/OUTER-CLAIM.json')
    oldprofile = collections.Counter(before_idle)
    require(original_providers['gauge44']['actual_paid_profile'] == original_providers['extra']['actual_paid_profile'], 'Common predecessor local bill')
    for rank, count in original_providers['gauge44']['actual_paid_profile'].items():
        oldprofile[int(rank)] += 666 * count
    require(dict(oldprofile) == {int(r): n for r, n in read(HERE / 'inputs/pr2673/PROFILE.json').items()}, 'Recomputed full PR2673 profile')
    expected = collections.Counter(oldprofile)
    expected.update({1: -2664, 7: -2664, 8: 2664})
    require(profile == dict(expected), 'Complete composition with PR2673')

    def moment(point):
        low = high = Q(0)
        for rank, count in profile.items():
            lo, hi = engine.child_cost(rank, 73, point)
            low += count * lo
            high += count * hi
        return low / 66304, high / 66304

    ticks_low, ticks_high, scale = 17 * 10**20, 18 * 10**20, 10**24
    while ticks_high - ticks_low > 1:
        mid = (ticks_low + ticks_high) // 2
        lo, hi = moment(Q(mid, scale))
        if hi < 1:
            ticks_low = mid
        elif lo > 1:
            ticks_high = mid
        else:
            raise ValueError('Exact interval too wide')
    lower, upper = Q(ticks_low, scale), Q(ticks_high, scale)
    require(moment(lower)[1] < 1 < moment(upper)[0], 'Directed endpoint bracket')
    caplo, caphi = engine.ceiling(profiles['gauge44'], 73, 896, 9, 64)
    require(engine.model(profiles['gauge44'], 73, 896, 9, 64)['local_mass'] == 5251, 'Coverage-law mass')
    controls = []
    def reject(name, function):
        try:
            function()
        except (AssertionError, ValueError, KeyError, IndexError):
            controls.append(name)
        else:
            raise ValueError('Invalid mutant accepted: ' + name)
    bad = copy.deepcopy(words['base'])
    i = next(i for i, event in enumerate(bad['A']) if event[0] == 'add')
    bad['A'][i][3] *= -1
    reject('wrong prelude sign: exact target identity', lambda: independent.algebra(bad))
    bad = copy.deepcopy(words['base']); bad['cleanup'].pop()
    reject('missing cleanup instruction', lambda: independent.check_cleanup(bad))
    bad = copy.deepcopy(words['base']); bad['report']['local_profile']['8'] += 1
    reject('uncharged centre child', lambda: independent.check_frames(bad))
    for kind in ['missing role', 'outside call window', 'duplicate physical family']:
        badfill = copy.deepcopy(fill)
        if kind == 'missing role':
            badfill['rows'].pop()
        elif kind == 'outside call window':
            row = badfill['rows'][0]
            row[0] = next(t for t in range(666) if t not in windows[f'{row[2]},{row[3]}'][1])
        else:
            a, b = next((a, b) for a, b in zip(badfill['rows'], badfill['rows'][1:]) if a[0] == b[0])
            b[2:] = a[2:]
        reject(kind, lambda: owners(badfill, order, dispatch, widths, plan, windows))
    result = dict(status='PASS_BOUNDED_LOCAL_OWNER_MOMENT', local=reports, profile=profile,
                  idle=dict(sorted(idle.items())), roles=281052, complex_lower=str(lower), complex_upper=str(upper),
                  moment_lower_upper=str(moment(lower)[1]), moment_upper_lower=str(moment(upper)[0]),
                  packing_ceiling=dict(lower=str(caplo), upper=str(caphi), realized_fraction_lower=str(lower/caphi),
                                       scope='Fixed local profile and coverage law, rank-51 relaxation; no packing optimum or old outer map.'),
                  rejected=controls, scope='Exact symbolic local identity, whole-role geometry and rational moment. Full native/global/outer admission is separate.')
    if not args.discovery:
        claim = read(HERE / 'CLAIM.json')
        ledger = read(HERE / 'evidence/OUTER-LEDGER.json')
        full = read(HERE / 'evidence/FULL-RESULT.json')
        for name, digest in full['execution_inputs'].items():
            require(sha(HERE / name) == digest, 'Full reproduction source binding: ' + name)
        row = ledger['rows']['struct_boundary_radix_union']
        kappa = Q(claim['kappa'])
        require(Q(claim['complex_lower']) == lower and Q(claim['complex_upper']) == upper, 'Published complex bracket binding')
        require({int(r): n for r, n in claim['global_profile'].items()} == profile, 'Published global profile binding')
        require({int(r): n for r, n in claim['local_profile'].items()} == profiles['gauge44'], 'Published local profile binding')
        require(Q(comparison['kappa_rational']) < kappa < lower, 'Strict improved claim below endpoint')
        require(Q(full['comparison_kappa']) == Q(claim['comparison']['kappa']) == Q(comparison['kappa_rational']), 'Pinned comparison rational binding')
        require(kappa <= Q(full['kappa']) == Q(row['kappa']['rational']), 'Published/full/outer rational binding')
        require({int(r): n for r, n in full['profile'].items()} == {int(r): n for r, n in ledger['profile'].items()} == profile, 'Full and bounded profile binding')
        require(full['status'] == 'PASS_CHANGED_T74_FULL_CONDITIONAL_ADMISSION' and full['fresh_baseline'] and full['fresh_changed_natives'], 'Recorded fresh admission')
        require(all(s['exit_code'] == 0 for s in full['stages'] + full['reproduction_stages']), 'Completed full stages')
        require(len(row['strict_checks']) == 63 and all(Q(v['rational']) > 0 for v in row['strict_checks'].values()), '63 exact outer inequalities')
        require(full['physical'] == 66814 and full['private_zero_buffers'] == 78, 'Paid private buffers')
        result['published_kappa'] = str(kappa)
    if args.out:
        write(args.out, result)
    print(result['status'], 'roles=281052', 'lower=' + str(lower), 'upper=' + str(upper), 'controls=' + str(len(controls)))

if __name__ == '__main__':
    main()
