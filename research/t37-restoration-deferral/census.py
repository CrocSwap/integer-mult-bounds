# SPDX-License-Identifier: Apache-2.0
"""Coverage identity, restoration census and deferral profiles for T37.

Usage: census.py OUT.json

Reads only the hash-pinned committed replay archives (no extraction to disk).
Writes the census and every scenario profile that price.py certifies.
"""
import json
import sys
from collections import Counter

from common import (ROOT, SOURCES, canonical, canonical_restoration, concentrated, coverage_census,
                    emitted_restoration, global_profile, load_canonical, load_construction, load_programs,
                    rank_mass, require, restoration_census, sha256, window_deferral)

CENTRE_RANK = 8
HALVING_CAP = 48          # every idle window has capacity <= 48; 2*48^2 < 73^2


def counter_json(c):
    return {str(k): c[k] for k in sorted(c) if c[k]}


def role_summary(registers):
    out = {}
    for role in ('source', 'target', 'helper'):
        rs = [r for r in registers if r['role'] == role]
        pos = [r for r in rs if r['restoration'] > 0]
        out[role] = dict(registers=len(rs),
                         paid_endpoint_mass=sum(r['end'] - r['start'] for r in rs),
                         positive_restoration=len(pos),
                         restoration_mass=sum(r['restoration'] for r in pos),
                         restoration_profile=counter_json(Counter(r['restoration'] for r in pos)),
                         positive_restoration_touched_by_full_cleanup=sum(r['full_cleanup_gates'] > 0 for r in pos),
                         zero_restoration_low_ends=sum(r['restoration'] == 0 and r['low_end'] for r in rs),
                         full_cleanup_gates_on_positive_restoration=sum(r['full_cleanup_gates'] for r in pos))
    return out


def census(name):
    template, word = load_construction(name)
    local = restoration_census(word)
    rep = word['report']
    local_profile = Counter({int(k): n for k, n in rep['local_profile'].items()})
    require(local['paid'] == local_profile, f'{name}: replayed local profile differs from the word report')
    require(local['widths'] == Counter({int(k): n for k, n in rep['width_inventory'].items()}), 'width inventory')
    require(dict(local['centre_children']) == {CENTRE_RANK: 8}, 'eight rank-eight centre paths')
    data_steps = {r['end'] - r['start'] for r in local['registers'] if r['role'] != 'helper'}
    require(len(data_steps) == 1, 'every data register pays the same climb')
    data_step, = data_steps
    local_mass = rank_mass(local_profile)
    cov = coverage_census(template, local_mass, data_step)
    W, N, m = cov['live'], cov['calls'], cov['m']
    require(cov['coverage_values'] == {str(m): W}, f'{name}: coverage identity fails')
    require(cov['total_rank_mass'] == (m - 1) * W + local['centre_children'][CENTRE_RANK] * CENTRE_RANK * N,
            f'{name}: mass identity fails')
    require(cov['deficit'] == W - CENTRE_RANK * 8 * N, f'{name}: deficit identity fails')
    centres = cov['private_centre_families']
    require(centres[0] >= W, 'centre work families lie outside the live stock')
    H = global_profile(template, local_profile)
    assembly = json.loads((ROOT / SOURCES['constructions'][name]['assembly']).read_text())
    require(sha256((ROOT / SOURCES['constructions'][name]['assembly']).read_bytes())
            == SOURCES['constructions'][name]['assembly_sha256'], f'{name}: assembly digest')
    require(counter_json(H) == assembly['complex_profile'], f'{name}: global profile differs from the selected assembly')
    emitted = None
    binding = None
    if 'canonical_member' in SOURCES['constructions'][name]:
        (prov,) = template['local_providers'].values()
        native = [r for r in local['registers'] if r['role'] == 'helper']
        require([r['end'] - r['start'] for r in native] == prov['widths'], 'helper widths differ by index from the template')
        canon = canonical_restoration(load_canonical(name, template))
        v = local['v']
        require(canon[2 * v:] == [r['restoration'] for r in native],
                'helper restoration differs by index between the native and canonical words')
        require(sorted(canon[:v]) == sorted(r['restoration'] for r in local['registers'] if r['role'] == 'source'),
                'source restoration multiset differs between the native and canonical words')
        local['template_helper_restoration'] = canon[2 * v:]
        binding = dict(helper_widths_by_index='native word = hosted template provider (504 helpers)',
                       helper_restoration_by_index='native word = canonical provider word bound by the template',
                       source_restoration='equal as a multiset (sources are relabelled in the canonical word)')
    if 'program_member' in SOURCES['constructions'][name]:
        restored = Counter()
        for r in local['registers']:
            if r['restoration'] > 0:
                restored[r['restoration']] += 1
        no_centres = Counter(local_profile)
        no_centres.subtract(local['centre_children'])
        emitted = {}
        for orientation, e in emitted_restoration(load_programs(name, template)).items():
            require(e['final'] == restored, f'{name} {orientation}: emitted final climbs differ from the replay')
            require(+e['climbs'] == +no_centres and e['centres'] == 8, f'{name} {orientation}: emitted children')
            ph = e['phases']
            require(ph.index('final') < ph.index('full_frame_cleanup'), 'final climbs precede the full-frame cleanup')
            emitted[orientation] = dict(phases=ph, final_climbs=counter_json(e['final']))
    out = dict(construction=name, emitted_programs=emitted, index_binding=binding, local=dict(
        h=local['h'], v=local['v'], R=local['R'], profile=counter_json(local_profile), mass=local_mass,
        data_climb_per_incidence=data_step, centre_children=counter_json(local['centre_children']),
        phase_mass=counter_json(local['phase_mass']), roles=role_summary(local['registers'])),
        coverage=cov, global_profile=counter_json(H),
        identity=dict(statement='data_climb*k_f + 1 + hosted_f + idle_f = m for every live family f; '
                                'rank mass = (m-1)*W + 64*N; deficit = W - 64*N',
                      rank_mass=cov['total_rank_mass'], deficit=cov['deficit'], live=W, calls=N))
    return out, template, local, local_profile, H


def scenarios(template, local, local_profile, H):
    N = len(template['calls'])
    restoration = dict(enumerate(local['template_helper_restoration']))
    positive = sorted(i for i, d in restoration.items() if d > 0)
    idle_ranks = Counter(c['rank'] for c in template['idle_children'])
    base_mass = rank_mass(H)
    out = {}

    def add(key, profile, realizable, **meta):
        require(73 * 73 > 2 * max(profile) ** 2, f"{key}: child above the halving cap")
        if realizable:
            require(max(profile) <= HALVING_CAP, f"{key}: child above every window capacity")
        out[key] = dict(profile=counter_json(profile), rank_mass=rank_mass(profile),
                        rank_mass_neutral=rank_mass(profile) == base_mass,
                        realizable_in_selected_windows=realizable, **meta)

    add('baseline', H, True, description='Selected T37 profile.')
    H1, removed, returned = window_deferral(template, local_profile, restoration, set(positive))
    require(rank_mass(H1) == base_mass, 'deferral must be mass neutral')
    add('defer_all_selected_hosting', H1, True,
        description='Every positive helper restoration climb (all calls) is deferred; its host '
                    'coordinates return to the same hosting window and are advanced by that '
                    "window's idle child, merged per window. Owner map unchanged.",
        deferred_helpers_per_call=len(positive), deferred_children=counter_json(removed),
        windows_receiving=sum(returned.values()), returned_window_ranks=counter_json(returned))
    H3 = concentrated(H, removed, idle_ranks, HALVING_CAP)
    add('defer_all_free_concentration', H3, False,
        description='Relaxation of the previous row: all idle coordinates, including the returned '
                    'ones, placed in capacity-48 children, ignoring helper indivisibility, windows '
                    'and chronology.')
    H4 = concentrated(H, Counter(), idle_ranks, HALVING_CAP)
    add('baseline_free_concentration', H4, False,
        description='The same relaxation with no deferral (control for the relaxation itself).')
    # One rank-one restoration climb per call moved into an existing rank-48 idle child.
    H5 = Counter(H)
    H5[1] -= N
    H5[48] -= N
    H5[49] += N
    require(idle_ranks[48] >= N, 'enough rank-48 children')
    add('exchange_merge_rank1_into_48', +H5, False,
        description='Relaxation: per call, one rank-one climb is removed and its coordinate joins an '
                    'existing rank-48 idle child (48 -> 49; halving 2*49^2 < 73^2). Every selected window '
                    'has capacity at most 48 and every rank-48 child fills a whole idle window, so no '
                    're-hosting realizes this; it over-estimates one deferred rank-one climb per call.')
    H6 = Counter(H)
    H6[1] -= N
    out['zero_cost_delete_rank1'] = dict(
        profile=counter_json(+H6), rank_mass=rank_mass(H6), rank_mass_neutral=False,
        realizable_in_selected_windows=False,
        description='PR974-style relaxation: one rank-one child per call deleted with zero parent '
                    'cost. It leaves N live coordinates unadvanced; priced only for comparison.')
    single = {}
    for i in positive:
        Hi, rem, _ = window_deferral(template, local_profile, restoration, {i})
        single[i] = Hi
    return out, single, positive, restoration


def main():
    target = sys.argv[1]
    t37, template, local, local_profile, H = census('T37')
    t21 = census('T21')[0]
    rows, single, positive, restoration = scenarios(template, local, local_profile, H)
    changed = {str(i): counter_json(Hi) for i, Hi in single.items() if Hi != H}
    result = dict(status='PASS_T37_RESTORATION_CENSUS', base_commit=SOURCES['base_commit'],
                  T37=t37, T21=dict(construction='T21', coverage=t21['coverage'], identity=t21['identity']),
                  helper_restoration={str(i): restoration[i] for i in sorted(restoration)},
                  positive_restoration_helpers=positive,
                  scenarios=rows,
                  single_helper_profiles=changed,
                  single_helper_unchanged=sorted(int(i) for i in single if single[i] == H))
    with open(target, 'w') as f:
        f.write(canonical(result))
    print(result['status'])
    for role, s in t37['local']['roles'].items():
        print(f"{role:7s} restoration mass {s['restoration_mass']:4d} in {s['positive_restoration']:3d} registers, "
              f"{s['positive_restoration_touched_by_full_cleanup']:3d} touched by full-frame cleanup")
    print('T37 coverage', t37['coverage']['coverage_values'], 'deficit', t37['coverage']['deficit'],
          '| T21 coverage', t21['coverage']['coverage_values'], 'deficit', t21['coverage']['deficit'])


if __name__ == '__main__':
    main()
