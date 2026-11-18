#!/usr/bin/env python3
"""Check the source-bound selector, complete extent and parked parent state."""
from hashlib import sha1, sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from controller import Machine, need, require_view, seek_table


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def authenticate():
    for row in json.loads((HERE / 'VENDORED.json').read_text())['files']:
        raw = (HERE / row['path']).read_bytes()
        need(sha256(raw).hexdigest() == row['sha256'], 'source SHA256')
        need(sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == row['git_blob'], 'source Git blob')
    for row in json.loads((HERE / 'SOURCES.json').read_text())['files']:
        if row['usage'] == 'input':
            need(sha256((HERE.parents[1] / row['path']).read_bytes()).hexdigest() == row['sha256'], 'retained proof input')


authenticate()
sys.path.insert(0, str(HERE / 'source'))
import banks
import word


def span(basis):
    result = {0}
    for vector in basis:
        need(vector not in result, 'independent source basis')
        result |= {x ^ vector for x in result}
    return result


def source_boundary():
    _, native = word.words()
    sites = banks.plan(native)
    at = 88263
    event = native['program'][at]
    need(event == ['MOVE', 1510, 477, 1090, True], 'exact owned MOVE')
    need(sites[35] == [1510, 88260, 477, 91760, 1090], 'exact parent owner')
    active = [i for i, site in enumerate(sites) if site[1] < at < site[3]]
    need(len(sites) == 234 and len(active) == 34 and 35 in active, 'current owner plan')
    large = span(native['frames'][477])
    small = span(native['frames'][1090])
    need(len(large) == 256 and len(small) == 16 and small < large, 'rank-four nested boundary')
    return native, sites, {'clock': at, 'event': event, 'parent_owner_ordinal': 35,
                           'active_parent_ordinals': active, 'parent_bank_count': len(sites),
                           'child_rank': 4, 'native_rank': 9,
                           'word_sha256': sha256(word.encoded(native)).hexdigest(),
                           'lifetime_plan_sha256': sha256(word.encoded(sites)).hexdigest()}


def check_shapes():
    cases = []
    for rows, factor, width in [(1, 1, 1), (2, 1, 3), (1, 2, 1)]:
        parent = banks.make_guide(rows, 9 * factor, width)
        child_rows = rows * 2 ** (5 * factor)
        child = banks.make_guide(child_rows, 4 * factor, width)
        require_view(parent, child)
        address_count = rows * 2 ** (9 * factor)
        child_size = 2 ** (4 * factor)
        for address in range(address_count):
            outer, native = divmod(address, 2 ** (9 * factor))
            spectator, inner = divmod(native, child_size)
            child_outer = outer * 2 ** (5 * factor) + spectator
            need(child_outer * child_size + inner == address, 'ordered complete child record map')
        cases.append({'rows': rows, 'factor': factor, 'width': width,
                      'child_rows': child_rows, 'child_axes': 4 * factor,
                      'addresses': address_count, 'extent': len(parent) - 2})
    same_length_wrong_format = (banks.make_guide(3, 0, 1), banks.make_guide(1, 0, 6))
    need(len(same_length_wrong_format[0]) == len(same_length_wrong_format[1]), 'equal-extent control')
    for wrong_pair in [same_length_wrong_format,
                       (banks.make_guide(1, 9, 1), banks.make_guide(16, 4, 1))]:
        try:
            require_view(*wrong_pair)
        except ValueError as exc:
            need(str(exc) == 'complete shape and order equality', 'shape rejection cause')
        else:
            raise ValueError('invalid child view accepted')
    return cases


def check_lifetimes(native, sites):
    count = len(sites)
    guide = banks.make_guide(1, 0, 1)
    machine = Machine(guide, 2 * count, count, banks)
    parent = machine.data[:count * len(guide)]
    lookup = {s[1]: (i, 'INIT') for i, s in enumerate(sites)}
    lookup.update({s[3]: (i, 'CLEAR') for i, s in enumerate(sites)})
    total, trace = 0, []
    for clock in sorted(lookup):
        ordinal, operation = lookup[clock]
        need(native['program'][clock][0] == operation, 'chronological source service')
        slot = count + ordinal
        cost = machine.reset(slot, operation)
        total += cost
        trace.append([clock, ordinal, operation, cost])
        body = machine.data[slot * len(guide) + 1:(slot + 1) * len(guide) - 1]
        need(body == ([c for _, c in guide[1:-1]] if operation == 'INIT' else [banks.BLANK] * (len(guide) - 2)), 'exact selected reset body')
    need(machine.data[:len(parent)] == parent, 'all suspended parents unchanged')
    need(machine.guide == tuple(guide) * (2 * count), 'immutable complete guide')
    extent = len(guide) - 2
    need(total == 1316484 * extent + 2631096, 'complete source reset overhead')
    return {'services': len(trace), 'extent': extent, 'charged': total,
            'trace_sha256': sha256(encoded(trace)).hexdigest(), 'counts': dict(machine.counts)}


def check_actual_boundary(sites):
    count = len(sites)
    guide = banks.make_guide(1, 9, 1)
    require_view(guide, banks.make_guide(32, 4, 1))
    machine = Machine(guide, 2 * count, count, banks)
    old = machine.data.copy()
    receipts = []
    for slot in (count, 2 * count - 1):
        for operation in ('INIT', 'CLEAR'):
            receipts.append({'slot': slot, 'operation': operation,
                             'charged': machine.reset(slot, operation)})
    for slot in range(2 * count):
        start = slot * len(guide)
        need(machine.data[start] == old[start] and machine.data[start + len(guide) - 1] == old[start + len(guide) - 1], 'all exterior guards unchanged')
        if slot not in (count, 2 * count - 1):
            need(machine.data[start:start + len(guide)] == old[start:start + len(guide)], 'all unselected cells unchanged')
    need(machine.guide == tuple(guide) * (2 * count), 'guide preserved at actual extent')
    # This borrower tests the frame condition. It is not a Gaussian child.
    loan = {key: (state, '1' if write == '0' else write, move)
            for key, (state, write, move) in banks.graph('INIT').items()}
    before = machine.data.copy()
    machine.execute(machine.forward, 35)
    machine.execute(loan, 'start')
    machine.execute(machine.backward, 35)
    lo, hi = 35 * len(guide), 36 * len(guide)
    need(machine.data[:lo] == before[:lo] and machine.data[hi:] == before[hi:] and machine.data[lo:hi] != before[lo:hi], 'borrowed view isolation')
    need(machine.guide_head == machine.data_head == 0, 'borrower head return')
    return {'extent': len(guide) - 2, 'banks': 2 * count,
            'payload_cells': len(machine.data), 'immutable_guide_cells': len(machine.guide),
            'reset_receipts': receipts, 'borrowed_slot': 35,
            'borrower_scope': 'write-only frame-condition witness, not a Gaussian child'}


def check_controls():
    guide = banks.make_guide(1, 0, 1)
    machine = Machine(guide, 2, 1, banks)
    parked = machine.data[:len(guide)]
    machine.reset(0, 'CLEAR')
    need(machine.data[:len(guide)] != parked, 'aliased child owner changes the parked parent')
    private = [banks.LEFT] + ['1'] * (len(guide) - 2) + [banks.RIGHT]
    banks.run_reset('CLEAR', guide[:-2] + guide[-1:], private)
    need(private[-2] == '1', 'short guide leaves old backing')
    machine = Machine(guide, 2, 1, banks)
    machine.execute(machine.forward, 1)
    machine.execute(banks.graph('CLEAR'), 'start')
    need(machine.guide_head != 0 and machine.data_head != 0, 'omitted selector return leaves displaced heads')
    return ['same extent with a different format rejected', 'missing child spectators rejected',
            'aliased child slot changes parent', 'short guide leaves old backing',
            'omitted selector return leaves both heads displaced']


def main():
    native, sites, boundary = source_boundary()
    count = 2 * len(sites)
    result = {'boundary': boundary, 'shapes': check_shapes(),
              'source_lifetimes': check_lifetimes(native, sites),
              'actual_boundary': check_actual_boundary(sites), 'controls': check_controls(),
              'fixed_control_rows': 2 * len(seek_table(count, 1, banks.ALLOWED)) + len(banks.graph('INIT')) + len(banks.graph('CLEAR')),
              'single_service_cost': '8k(L+2)+9L+14',
              'complete_child_reset_cost': {'L': 1316484, 'constant': 2631096}}
    path = HERE / 'RESULT.json'
    if sys.argv[1:] == ['--write']:
        need(not path.exists(), 'do not replace a checked receipt')
        path.write_text(json.dumps(result, indent=2) + '\n')
    else:
        need(not sys.argv[1:], 'unexpected arguments')
        need(result == json.loads(path.read_text()), 'complete source-bound receipt')
    print('PASS_CURRENT_NATIVE_BANK_SELECTOR ' + json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
