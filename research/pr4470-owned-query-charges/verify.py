#!/usr/bin/env python3
"""Independent selected4470 query/idle charging check. Apache-2.0; Codex assistance."""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import argparse
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CONTROLLER = 'research/joint-helper-lattice/CONTROLLER.json'
PHASES = 'research/kappa-0023-productive-jobs/dependencies/kappa-next-regime/direct-decoder/sources/DATA-PHASES.json'
ONE = (F(1), F(0))
A = (F(1, 2), F(1, 2))
B = (F(1, 2), F(-1, 2))


def need(ok, why):
    if not ok:
        raise ValueError(why)


def add(a, b):
    return a[0]+b[0], a[1]+b[1]


def mul(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def scaled_sum(a, x, b, y):
    out = {}
    for scale, row in ((a, x), (b, y)):
        for key, value in row.items():
            out[key] = add(out.get(key, (0, 0)), mul(scale, value))
    return {k: v for k, v in out.items() if v != (0, 0)}


def gaussian(rows, width):
    for axis in range(width):
        rows = [scaled_sum(A, row, B, rows[i ^ (1 << axis)]) for i, row in enumerate(rows)]
    return rows


def independent_inverse(rows, width):
    out = []
    for i in range(len(rows)):
        row = {}
        for mask in range(1 << width):
            coefficient = ONE
            for axis in range(width):
                coefficient = mul(coefficient, A if mask >> axis & 1 else B)
            row = scaled_sum(ONE, row, coefficient, rows[i ^ mask])
        out.append(row)
    return out


def symbols(name, size):
    return [{(name, i): ONE} for i in range(size)]


def trace(width, mutation=None):
    size = 1 << (width+1)
    x, y, z, helper = [symbols(name, size) for name in ('X', 'Y', 'Z', 'H')]
    if mutation != 'omit_clear':
        z = [{} for _ in z]
    z = [scaled_sum(ONE, a, ONE, b) for a, b in zip(z, x)]
    if mutation != 'omit_query':
        z = gaussian(z, width-1 if mutation == 'omit_last_column' else width)
    if mutation != 'omit_translation':
        z = [z[i ^ ((1 << width)-1)] for i in range(size)]
    if mutation == 'drop_spectator':
        z = z[:size//2]*2
    if mutation == 'overwrite_destination':
        y = z
    else:
        y = [scaled_sum(ONE, a, ONE, b) for a, b in zip(y, z)]
    if mutation == 'clear_borrowed':
        helper = [{} for _ in helper]
    if mutation == 'partial_erase':
        z = [{} for _ in z[:size//2]]+z[size//2:]
    elif mutation != 'omit_erase':
        z = [{} for _ in z]
    return x, y, z, helper


def semantic_controls():
    rejected = []
    for width in (1, 2, 3):
        size = 1 << (width+1)
        x, y, h = [symbols(name, size) for name in ('X', 'Y', 'H')]
        expected = (x, [scaled_sum(ONE, a, ONE, b) for a, b in zip(y, independent_inverse(x, width))],
                    [{} for _ in x], h)
        need(trace(width) == expected, 'Exact independent-column query endpoint')
        for mutation in ('omit_clear', 'omit_query', 'omit_translation', 'omit_erase',
                         'clear_borrowed', 'overwrite_destination', 'omit_last_column',
                         'drop_spectator', 'partial_erase'):
            need(trace(width, mutation) != expected, 'Reject '+mutation)
            rejected.append(f'f={width}:{mutation}')
    return rejected


def phase_signature(terms):
    def value(x):
        return sum(power*((axis & x).bit_count() % 2) for axis, power in terms) % 4
    linear = [value(1 << i) for i in range(9)]
    quadratic = [(value((1 << i) | (1 << j))-linear[i]-linear[j]) % 4
                 for i in range(9) for j in range(i+1, 9)]
    return linear, quadratic


def ports_checked(phases):
    need(phases['ports'] == 112 and len(phases['recipes']) == 112, 'All actual source ports')
    for recipe in phases['recipes']:
        q = recipe['q']
        basis = recipe['idle_children'][0]['orthogonal_axes'][:8]
        need(0 < q < 512 and q.bit_count() % 2 == 1, 'Actual norm-one central direction')
        need(len(basis) == 8 and all(0 < b < 512 for b in basis), 'Old-eight complement')
        need(all((a & b).bit_count() % 2 == int(i == j)
                 for i, a in enumerate([q]+basis) for j, b in enumerate([q]+basis)),
             'Actual old-nine orthonormal chart')
        old, old_cross = phase_signature([(1 << i, 1) for i in range(9)]+[(q, -1)])
        new, new_cross = phase_signature([(b, 1) for b in basis])
        delta = [(a-b) % 4 for a, b in zip(old, new)]
        need(old_cross == new_cross and all(d % 2 == 0 for d in delta), 'D0 complement differs only by a translation')
        shift = sum((d//2) << i for i, d in enumerate(delta))
        need(shift == recipe['idle_children'][0]['translation_after'], 'Actual source absolute-phase translation')
    return len(phases['recipes'])


def site_map(controller):
    need(controller['kind'] == 'complex' and controller['pairs'] == 16 and controller['prefix_pairs'] == 7,
         'Selected p16/a7 caller')
    events = controller['physical_events']
    expected_queries = [['QUERY_SHEAR', 2*j+2, j, False] for j in range(15)]
    expected_idles = ([['IDLE', j, [0]+list(range(1, 2*j, 2))] for j in range(1, 8)] +
                      [['IDLE', j, list(range(2*j+3, 32, 2))+[32]] for j in range(7, 15)])
    need([e for e in events if e[0] == 'QUERY_SHEAR'] == expected_queries, 'All thin sources/destinations in chronology')
    need([e for e in events if e[0] == 'IDLE'] == expected_idles, 'All whole IDLE stage sets in chronology')
    need(len(events) == 154, 'Unchanged complete event sequence')
    sites, jobs = [], {}
    for event_index, event in enumerate(events):
        if event[0] == 'QUERY_SHEAR':
            _, stage, pair, backward = event
            row = {'event_index': event_index, 'kind': 'QUERY_SHEAR', 'stage': stage, 'pair': pair,
                   'source_role': 2*pair, 'destination_role': 2*pair+1, 'rank_coefficient': 1,
                   'paid_occurrences': 112, 'owned_stream': 'private Z, reused after ERASE',
                   'operations': ['OWNED_CLEAR', 'COPY_X_TO_Z', 'RIGHT_MONOMIAL', 'PAID_CHILD',
                                  'LEFT_MONOMIAL', 'TENSOR_TRANSLATION', 'ADD_Z_TO_Y', 'OWNED_ERASE']}
            need(not backward, 'Every actual thin call is forward')
            keys = [(event_index, p, 'Z') for p in range(112)]
        elif event[0] == 'IDLE':
            _, pair, stages = event
            row = {'event_index': event_index, 'kind': 'IDLE', 'pair': pair, 'stages': stages,
                   'rank_coefficient': 8*len(stages), 'paid_occurrences': 224,
                   'operations': ['RIGHT_MONOMIAL', 'PAID_CHILD', 'LEFT_MONOMIAL'],
                   'owned_stream': None}
            keys = [(event_index, p, role) for p in range(112) for role in (2*pair, 2*pair+1)]
        else:
            continue
        for key in keys:
            need(key not in jobs, 'Unique recursive child charge')
            jobs[key] = row['rank_coefficient']
        sites.append(row)
    idle = Counter({r: n for r, n in Counter(jobs.values()).items() if r != 1})
    need(Counter(jobs.values())[1] == 1680, 'Query calibration only')
    need(idle == Counter({**{r: 448 for r in range(16, 65, 8)}, 72: 224}), 'Whole IDLE jobs retain every stage')
    need(all(row['operations'].count('PAID_CHILD') == 1 for row in sites), 'Exactly one child per expanded site')
    nonrecursive = 7*1680+2*3360
    allowance = 16*1680+32*112*len(events)
    need(nonrecursive <= allowance, 'Explicit logical records fit existing finite allowance')
    return {'sites': sites, 'query_jobs': 1680, 'idle_jobs': 3360,
            'scoped_nonrecursive_logical_records': nonrecursive,
            'source_nonrecursive_logical_record_allowance_subset': allowance,
            'width_rule': 'Each rank coefficient r denotes one complete rank-r*f child at every f >= 1.'}


def authenticate():
    manifest = json.loads((HERE/'SOURCES.json').read_text())
    for row in manifest['files']:
        if row['usage'] == 'input':
            path = ROOT/row['path']
            need(not path.is_symlink() and sha256(path.read_bytes()).hexdigest() == row['sha256'],
                 'Source byte pin: '+row['path'])


def run():
    authenticate()
    controller = json.loads((ROOT/CONTROLLER).read_text())
    phases = json.loads((ROOT/PHASES).read_text())
    sites = site_map(controller)
    controls = semantic_controls()
    for mutation in ('drop_query', 'reorient_query', 'omit_idle_stage', 'thin_idle_stage'):
        bad = deepcopy(controller)
        if mutation == 'drop_query':
            bad['physical_events'].remove(next(e for e in bad['physical_events'] if e[0] == 'QUERY_SHEAR'))
        elif mutation == 'reorient_query':
            next(e for e in bad['physical_events'] if e[0] == 'QUERY_SHEAR')[3] = True
        elif mutation == 'omit_idle_stage':
            next(e for e in bad['physical_events'] if e[0] == 'IDLE')[2].pop()
        else:
            next(e for e in bad['physical_events'] if e[0] == 'IDLE')[2][-1] = 2
        try:
            site_map(bad)
        except ValueError:
            controls.append(mutation)
        else:
            raise ValueError('Unrejected source-site control: '+mutation)
    return {'status': 'PASS_SCOPED_OWNED_QUERY_CHARGES', 'ports_checked': ports_checked(phases),
            **sites, 'rejected_controls': controls,
            'claim': 'Conditional scoped all-width charging lemma; no new kappa or physical tape admission.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = run()
    path = HERE/'RESULT.json'
    if args.write:
        path.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else:
        need(result == json.loads(path.read_text()), 'Committed complete site receipt')
    print(result['status'], 'sites='+str(len(result['sites'])),
          'controls='+str(len(result['rejected_controls'])))
