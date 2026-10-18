#!/usr/bin/env python3
"""Independent selected-event height ledger; no ledger producer imports.

Prepared for commdata2338 with substantial OpenAI Codex assistance. Apache-2.0.
Pinned PR2287 arithmetic is executed only as the subject of finite controls.
"""
import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import tarfile
from collections import Counter
from fractions import Fraction as Q

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
ARCHIVE = 'research/community-frontier1094-audit/selected-replay.tar.gz'
PREFIX = 'candidate/strict/global/'
MEMBERS = {
    'programs': 'base/providers/gauge44/LOCAL-PROGRAMS.json.gz',
    'template': 'hosted/GLOBAL-TEMPLATE.json.gz',
    'word': 'base/providers/gauge44/CANONICAL-WORD.json.gz',
    'recipes': 'base/providers/gauge44/CLIFFORD-RECIPES.json',
    'wrappers': 'base/providers/gauge44/RESIDUAL-ADAPTERS.json',
    'phases': 'base/work/complex-nine-native/DATA-PHASES.json',
    'invoice': 'audit/PREFIX-AND-INVOICE.json',
}
EXPECTED_PROFILE = {1: 349604, 2: 60192, 3: 62585, 4: 20448,
                    5: 11808, 7: 7, 8: 1152, 48: 4866}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    # JSON represents integer dictionary keys as strings. Normalize that boundary
    # before sorting, while retaining number types in values (1 differs from 1.0).
    return json.dumps(json.loads(json.dumps(value)), sort_keys=True, separators=(',', ':')).encode()


def authenticate():
    manifest = json.loads((PACKAGE / 'SOURCES.json').read_text())
    for pin in manifest['files']:
        if pin['usage'] == 'input':
            need(digest((ROOT / pin['path']).read_bytes()) == pin['sha256'],
                 'changed input: ' + pin['path'])
    for pin in manifest['pending_sources']:
        need(digest((PACKAGE / pin['path']).read_bytes()) == pin['sha256'],
             'changed pending source: ' + pin['path'])


def load():
    data, pins = {}, {}
    with tarfile.open(ROOT / ARCHIVE, 'r:gz') as archive:
        entries = archive.getmembers()
        for key, suffix in MEMBERS.items():
            matches = [m for m in entries if m.name == PREFIX + suffix]
            need(len(matches) == 1 and matches[0].isfile(), 'unique regular member')
            raw = archive.extractfile(matches[0]).read()
            pins[PREFIX + suffix] = digest(raw)
            data[key] = json.loads(gzip.decompress(raw) if suffix.endswith('.gz') else raw)
    artifacts = data['invoice']['providers']['gauge44']['artifacts']
    for name, sha in pins.items():
        if '/providers/gauge44/' in name:
            need(artifacts[name.rsplit('/', 1)[1]] == sha, 'invoice member binding')
    return data, pins


def binary_rank(rows):
    pivots = {}
    for x in rows:
        while x:
            b = x.bit_length() - 1
            if b not in pivots:
                pivots[b] = x
                break
            x ^= pivots[b]
    return len(pivots)


def monomial_inventory(data):
    """Check height-neutral shape, not the native operator equalities."""
    count = 0
    def walk(x):
        nonlocal count
        if isinstance(x, list):
            for value in x:
                walk(value)
        elif isinstance(x, dict):
            if 'matrix_rows' in x:
                need(set(x) == {'matrix_rows', 'offset', 'phase', 'linear_Z4', 'quadratic_rows'},
                     'monomial alphabet')
                rows = x['matrix_rows']
                need(len(rows) == 9 and all(type(r) is int and 0 <= r < 512 for r in rows)
                     and binary_rank(rows) == 9, 'invertible binary monomial')
                need(type(x['offset']) is int and 0 <= x['offset'] < 512, 'monomial offset')
                need(type(x['phase']) is int and 0 <= x['phase'] < 4, 'quarter phase')
                need(len(x['linear_Z4']) == len(x['quadratic_rows']) == 9, 'phase dimensions')
                need(all(type(a) is int and 0 <= a < 4 for a in x['linear_Z4'])
                     and all(type(a) is int and 0 <= a < 512 for a in x['quadratic_rows']),
                     'integer phase polynomial')
                count += 1
            else:
                for value in x.values():
                    walk(value)
    walk(data['recipes'])
    walk(data['wrappers'])
    return count


def scalar_parameters(op):
    need(op[0] in ('add', 'scale'), 'charged scalar kind')
    need(len(op) == (5 if op[0] == 'add' else 4), 'scalar shape')
    need(type(op[-2]) is int and type(op[-1]) is int and op[-1] != 0, 'rational scalar syntax')
    c = Q(op[-2], op[-1])
    den = c.denominator
    need(den & (den - 1) == 0, 'nondyadic selected scalar')
    return c, abs(c.numerator).bit_length(), den.bit_length() - 1


def local_ledger(events, directed, endpoints, wrappers, frames):
    counts, children, coefficients = Counter(), Counter(), Counter()
    mass = height = source_charge = max_shift = 0
    prefixes = hashlib.sha256()
    for index, event in enumerate(events):
        need(isinstance(event, list) and event, 'event syntax')
        tag = event[0]
        counts[tag] += 1
        if tag in ('climb', 'center'):
            need(len(event) == (6 if tag == 'climb' else 5), 'child syntax')
            old, new, rank = event[-3:]
            need((old, new) in directed and directed[old, new]['rank'] == rank, 'native child rank binding')
            need(type(rank) is int and 0 < rank <= 48, 'proper selected child')
            children[rank] += 1
            mass += rank
        elif tag == 'scalar':
            need(len(event) == 3 and type(event[2]) is int and 0 <= event[2] < len(frames), 'scalar frame syntax')
            op = event[1]
            need(op[0] in ('add', 'scale', 'copy', 'clear'), 'closed scalar alphabet')
            counts['scalar/' + op[0]] += 1
            for role in op[1:3] if op[0] in ('add', 'copy') else op[1:2]:
                need(isinstance(role, list) and len(role) == 2 and role[0] in ('L', 'C')
                     and type(role[1]) is int and 0 <= role[1] < (704 if role[0] == 'L' else 8), 'scalar role syntax')
            if op[0] in ('add', 'scale'):
                c, b, k = scalar_parameters(op)
                height += max(b, k)
                source_charge += 2*b + k + 4
                max_shift = max(max_shift, k)
                coefficients[c] += 1
            else:
                need(len(op) == (3 if op[0] == 'copy' else 2), 'copy/clear syntax')
        elif tag == 'adapter':
            need(len(event) == 4 and event[1] in ('old_to_new', 'new_to_old'), 'endpoint adapter syntax')
            role, frame = event[2:]
            need(type(role) is int and 0 <= role < 704 and 0 <= frame < len(frames), 'endpoint adapter role/frame')
            if frame not in (0, 1):
                key = ('source', role) if role < 112 else ('target', role-112)
                need(key in endpoints and endpoints[key]['frame'] == frame and endpoints[key]['rank'] == 0,
                     'height-neutral endpoint adapter')
        elif tag == 'residual_adapter':
            need(len(event) in (4, 5) and event[1] in ('pre', 'post'), 'wrapper syntax')
            entrance = event[3]
            terminal = event[4] if len(event) == 5 else 1
            key = f'{entrance}:{terminal}' if len(event) == 5 else str(entrance)
            need(key in wrappers and wrappers[key]['frame'] == entrance
                 and wrappers[key]['rank'] == len(frames[terminal])-len(frames[entrance]), 'height-neutral wrapper binding')
        else:
            need(tag == 'phase' and len(event) == 2, 'closed native event alphabet')
        prefixes.update(canonical([index, mass, height, source_charge]) + b'\n')
    return {
        'events': len(events), 'counts': dict(counts), 'children': dict(sorted(children.items())),
        'child_count': sum(children.values()), 'endpoint_rank_mass': mass,
        'scalar_height': height, 'predecessor_scalar_charge': source_charge,
        'maximum_shift': max_shift, 'distinct_coefficients': len(coefficients),
        'coefficient_stream_sha256': digest(canonical([[str(c), n] for c, n in sorted(coefficients.items())])),
        'prefix_ledger_sha256': prefixes.hexdigest(),
    }, coefficients


def audit(data):
    t, programs = data['template'], data['programs']
    need((t['m'], t['live'], t['physical']) == (73, 14336, 14826), 'selected dimensions')
    need(t['cover'] == 'all matrices d in O(73,2), in lexicographic row order', 'selected cover domain')
    need(set(programs) == {'forward', 'backward'}, 'two selected directions')
    need(t['local_providers']['gauge44']['local_programs'] == programs, 'embedded program binding')
    directed = {(r['old'], r['new']): r for r in data['recipes']['children']}
    endpoints = {(r['role'], r['port']): r for r in data['recipes']['endpoint_adapters']}
    local, coefficients = {}, Counter()
    program_hashes = {direction: digest(canonical(events)) for direction, events in programs.items()}
    for direction in sorted(programs):
        item, cs = local_ledger(programs[direction], directed, endpoints,
                                data['wrappers']['recipes'], data['word']['frames'])
        local[direction] = item
        coefficients.update(cs)
        need(item['events'] == 24767, 'selected local event count')
    calls = {(c['stage'], c['replica']): c for c in t['calls']}
    need(len(calls) == len(t['calls']) == 144, 'unique selected calls')
    idle = {(z['replica'], z['child'], z['port']): z for z in t['idle_children']}
    need(len(idle) == len(t['idle_children']) == 7526, 'unique idle children')
    seen_calls, seen_idle, idle_slots = set(), set(), set()
    paid, event_counts, direction_counts = Counter(), Counter(), Counter()
    height = source_charge = bridge_adds = local_events = 0
    chronological = []
    for position, event in enumerate(t['execution_schedule']):
        kind = event['kind']
        event_counts[kind] += 1
        if kind == 'local_cover_sweep':
            key = event['stage'], event['replica']
            need(key in calls and key not in seen_calls, 'one dispatch per local call')
            call = calls[key]
            need(call['time'] == event['time'] and call['provider_id'] == event['provider_id'] == 'gauge44',
                 'chronological native dispatch')
            direction = call['orientation']
            need(direction in programs and call['local_program_sha256'] == program_hashes[direction],
                 'exact called local word')
            seen_calls.add(key)
            direction_counts[direction] += 1
            item = local[direction]
            paid.update(item['children'])
            height += item['scalar_height']
            source_charge += item['predecessor_scalar_charge']
            local_events += item['events']
        elif kind == 'idle_cover_sweep':
            need(len(event['child_indices']) == 2, 'two idle source/target fields')
            for child in event['child_indices']:
                for port in range(112):
                    key = event['replica'], child, port
                    need(key not in idle_slots, 'one idle deadline')
                    idle_slots.add(key)
                    if key in idle:
                        z = idle[key]
                        original = data['phases']['recipes'][port]['idle_children'][child]
                        need(type(z['rank']) is int and 0 < z['rank'] <= 48
                             and z['rank'] + z['pending_offset'] == len(original['orthogonal_axes']), 'idle endpoint rank binding')
                        paid[z['rank']] += 1
                        seen_idle.add(key)
        elif kind == 'bridge':
            need(type(event['coefficient']) is int and event['coefficient'] in (-1, 1), 'selected bridge coefficient')
            bridge_adds += 224
            height += 224
            source_charge += 224*8
        elif kind == 'bank_padding_cover_sweep':
            need(not t['bank_padding']['children'], 'no uncounted padding children')
        else:
            need(kind in ('terminal_Y_translations', 'terminal', 'translate_every_live_family'), 'closed caller alphabet')
        chronological.append([position, kind, sum(r*n for r, n in paid.items()), height, source_charge])
    need(seen_calls == set(calls) and seen_idle == set(idle), 'complete child dispatch')
    need(len(idle_slots) == 35840 and len(t['execution_schedule']) == 482, 'complete caller domains')
    need(dict(paid) == EXPECTED_PROFILE, 'reconstructed selected paid histogram')
    mass = sum(r*n for r, n in paid.items())
    need(mass == 1041408, 'unnormalized endpoint rank mass')
    return {
        'local': local, 'caller_events': len(t['execution_schedule']),
        'event_counts': dict(event_counts), 'call_orientations': dict(direction_counts),
        'local_events_per_cover': local_events, 'bridge_scalar_adds_per_cover': bridge_adds,
        'idle_deadlines_per_cover': len(idle_slots), 'positive_idle_children_per_cover': len(idle),
        'child_histogram_per_cover': dict(sorted(paid.items())), 'children_per_cover': sum(paid.values()),
        'unnormalized_rank_mass_per_cover': mass, 'scalar_height_per_cover': height,
        'predecessor_scalar_charge_per_cover': source_charge,
        'caller_prefix_ledger_sha256': digest(canonical(chronological)),
        'height_neutral_monomial_records': monomial_inventory(data),
    }, coefficients


def recurrence(ledger):
    need(type(ledger['unnormalized_rank_mass_per_cover']) is int and
         ledger['unnormalized_rank_mass_per_cover'] ==
         sum(int(r)*n for r, n in ledger['child_histogram_per_cover'].items()),
         'height mass must equal the unnormalized emitted children')
    gamma = (1 << 1296) * math.prod((1 << (2*i))-1 for i in range(1, 37))
    s = gamma * ledger['unnormalized_rank_mass_per_cover']
    E, C0 = 1 << 100000, 1 << 210000
    B = s + E
    slack = 32*73
    h = gamma * ledger['scalar_height_per_cover'] + slack
    old_h = gamma * ledger['predecessor_scalar_charge_per_cover'] + slack
    need(0 < h <= old_h < E, 'actual scalar and remainder reserve')
    need(8 <= 2*B and 2*B*(73-48) >= s+E, 'all-width induction coefficients')
    need(2*B+18 < C0, 'whole-layer height guard')
    checked = 0
    for e in list(range(1, 1001)) + [10**k+j for k in (6, 12, 60) for j in (0, 1, 72)]:
        f, delta = divmod(e, 73)
        if f:
            need(2*B*48*f+s*f+h <= 2*B*e, 'internal height consequence')
            need(delta+1 <= slack, 'remainder prefix slack')
        else:
            need(e+1 <= 8*e <= 2*B*e, 'direct leaf prefixes')
        checked += 1
    return {'cover_bits': gamma.bit_length(), 'cover_sha256_hex_integer': digest(hex(gamma).encode()),
            'unnormalized_mass_bits': s.bit_length(), 'scalar_and_remainder_charge_bits': h.bit_length(),
            'predecessor_scalar_charge_bits': old_h.bit_length(), 'remainder_slack': slack,
            'E_exponent': 100000, 'C0_exponent': 210000, 'finite_width_checks': checked,
            'inequalities': ['Gamma*H+2336 <= Gamma*H_old+2336 < E', '8 <= 2B',
                             '2B*(73-48) >= s+E', '2B+18 < C0'],
            'conditional_conclusion': 'A(e)<=2Be; all layer coefficient prefixes < C0*d'}


def import_arithmetic():
    base = PACKAGE / 'sources' / 'pr2287'
    for name, path in (('streams', base / 'vendor' / 'streams.py'),
                       ('height_subject_arithmetic', base / 'arithmetic.py')):
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return module


def actual_coefficient_controls(coefficients):
    module = import_arithmetic()
    cases = divisions = additions = 0
    witnesses = {}
    for c in sorted(coefficients):
        b, k = abs(c.numerator).bit_length(), c.denominator.bit_length()-1
        increment = max(b, k)
        p, delta = 4, increment+2
        F, width = p+delta, p+2*delta+3
        for numerator in (-16, -15, -1, 0, 1, 15, 16):
            x = Q(numerator, 1 << p)
            encoded = int(x * (1 << F))
            word = bytearray((encoded >> j) & 1 for j in range(width))
            grid = module.Grid(width, F)
            out = grid.scale(word, c)
            value = sum(bit << j for j, bit in enumerate(out)) - (out[-1] << width)
            need(Q(value, 1 << F) == c*x, 'source coefficient exact oracle')
            for temp in grid.workspace:
                v = sum(bit << j for j, bit in enumerate(temp)) - (temp[-1] << width)
                q = Q(v, 1 << F)
                need(abs(q) <= (1 << increment), 'source coefficient prefix magnitude')
                need(((1 << (p+increment)) * q).denominator == 1, 'source coefficient prefix denominator')
            divisions += grid.exact_divisions
            grid.close()
            need(not grid.workspace, 'coefficient work closes')
            cases += 1
            for target in (-1, 0, 1):
                grid = module.Grid(width, F)
                a = bytearray(((target << F) >> j) & 1 for j in range(width))
                out = grid.add(a, grid.scale(word, c))
                value = sum(bit << j for j, bit in enumerate(out)) - (out[-1] << width)
                need(Q(value, 1 << F) == target+c*x, 'source ADD coefficient oracle')
                for temp in grid.workspace:
                    v = sum(bit << j for j, bit in enumerate(temp)) - (temp[-1] << width)
                    q = Q(v, 1 << F)
                    need(abs(q) <= (1 << increment) and
                         ((1 << (p+increment))*q).denominator == 1, 'source ADD prefix reserve')
                grid.close()
                additions += 1
        if k > 0 and 'missing_denominator_charge' not in witnesses:
            exact = c * Q(1, 1 << p)
            need(((1 << p)*exact).denominator > 1, 'denominator omission witness')
            witnesses['missing_denominator_charge'] = {'coefficient': str(c), 'input': '1/16', 'output': str(exact)}
        if abs(c.numerator) > abs(c) and abs(c.numerator) > 1 and 'endpoint_only_horner' not in witnesses:
            witnesses['endpoint_only_horner'] = {'coefficient': str(c), 'input': '1', 'prefix': abs(c.numerator)}
    need(len(witnesses) == 2, 'source scalar shortcut witnesses')
    return {'distinct_source_coefficients': len(coefficients), 'scale_cases': cases, 'add_cases': additions,
            'exact_divisions': divisions, 'shortcut_witnesses': witnesses}


def controls(data, ledger):
    rejected = []
    def reject(label, mutate, expected):
        altered = copy.deepcopy(data)
        mutate(altered)
        altered['template']['local_providers']['gauge44']['local_programs'] = altered['programs']
        try:
            audit(altered)
        except ValueError as error:
            need(str(error) == expected, 'control failed at unexpected gate: ' + label + ': ' + str(error))
            rejected.append(label)
        else:
            raise ValueError('accepted malformed ledger: ' + label)
    reject('omitted_local_event', lambda x: x['programs']['forward'].pop(), 'selected local event count')
    reject('wrong_native_child_rank', lambda x: next(e for e in x['programs']['forward'] if e[0] == 'climb').__setitem__(-1, 48), 'native child rank binding')
    reject('omitted_positive_idle', lambda x: x['template']['idle_children'].pop(), 'unique idle children')
    reject('duplicate_call', lambda x: x['template']['calls'].__setitem__(0, copy.deepcopy(x['template']['calls'][1])), 'unique selected calls')
    reject('changed_call_direction', lambda x: x['template']['calls'][0].__setitem__('orientation', 'backward'), 'exact called local word')
    reject('unknown_caller_event', lambda x: x['template']['execution_schedule'][0].__setitem__('kind', 'unpriced_kernel'), 'closed caller alphabet')
    reject('unpriced_bank_child', lambda x: x['template']['bank_padding']['children'].append({'rank': 1}), 'no uncounted padding children')
    reject('non_quarter_phase', lambda x: x['recipes']['children'][0]['left'].__setitem__('phase', Q(1, 2)), 'quarter phase')
    try:
        scalar_parameters(['scale', ['L', 0], 1, 3])
    except ValueError:
        rejected.append('nondyadic_coefficient')
    else:
        raise ValueError('accepted nondyadic scalar')
    bad = copy.deepcopy(ledger)
    bad['unnormalized_rank_mass_per_cover'] = Q(bad['unnormalized_rank_mass_per_cover'], 14336)
    try:
        recurrence(bad)
    except ValueError as error:
        need(str(error) == 'height mass must equal the unnormalized emitted children', 'normalization control gate')
        rejected.append('live_family_normalization')
    else:
        raise ValueError('accepted time-normalized height mass')
    return rejected


def build_result():
    authenticate()
    data, pins = load()
    ledger, coefficients = audit(data)
    return {'status': 'PASS_SELECTED_COMPLEX_HEIGHT_LEDGER', 'member_sha256': pins,
            'ledger': ledger, 'recurrence': recurrence(ledger),
            'source_coefficient_controls': actual_coefficient_controls(coefficients),
            'rejected_controls': controls(data, ledger)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='explicitly regenerate this package receipt')
    args = parser.parse_args()
    result = build_result()
    path = PACKAGE / 'RESULT.json'
    if args.write:
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        need(canonical(json.loads(path.read_text())) == canonical(result), 'receipt mismatch')
    ledger = result['ledger']
    print(result['status'], 'local_events=' + str(ledger['local_events_per_cover']),
          'children=' + str(ledger['children_per_cover']), 'rank_mass=' + str(ledger['unnormalized_rank_mass_per_cover']),
          'scalar_height=' + str(ledger['scalar_height_per_cover']),
          'controls=' + str(len(result['rejected_controls'])), 'conditional_no_new_kappa')


if __name__ == '__main__':
    main()
