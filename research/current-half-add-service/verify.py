#!/usr/bin/env python3
"""Bind one literal rounded ADD and bound its error through the native suffix."""
from fractions import Fraction as Q
from copy import deepcopy
from hashlib import sha1, sha256
from pathlib import Path
from types import SimpleNamespace
import gzip
import json
import sys

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
CLOCK = 100504
RAW = ('ADD', 210, 457, '-1/2', 218)
TOKEN = ('local', CLOCK, RAW)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def authenticate():
    for row in json.loads((ROOT / 'SOURCES.json').read_text())['files']:
        if row['usage'] == 'input':
            need(sha256((REPO / row['path']).read_bytes()).hexdigest() == row['sha256'], 'retained input hash')
    for row in json.loads((ROOT / 'VENDORED.json').read_text())['files']:
        raw = (ROOT / row['path']).read_bytes()
        need(sha256(raw).hexdigest() == row['sha256'], 'candidate source hash')
        need(sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == row['git_blob'], 'candidate source blob')
    raw = gzip.decompress((ROOT / 'source/WORD.json.gz').read_bytes())
    grid = json.loads((ROOT / 'source/GRID.json').read_text())
    need(sha256(raw).hexdigest() == grid['decompressed_sha256'], 'grid receipt word binding')
    word = json.loads(raw)
    need(tuple(word['program'][CLOCK]) == RAW, 'exact half-ADD token')
    need(word['program'][CLOCK - 1] == ['MOVE', 457, 966, 218, False], 'preceding MOVE')
    charts = word['initial'] + [None] * word['owned_fields']
    for event in word['program'][:CLOCK]:
        op, r = event[:2]
        if op == 'INIT':
            need(charts[r] is None, 'fresh owned lifetime')
            charts[r] = event[2]
        elif op == 'CLEAR':
            need(charts[r] == event[2], 'owned return chart')
            charts[r] = None
        elif op == 'MOVE':
            need(charts[r] == event[2], 'MOVE source chart')
            charts[r] = event[3]
        elif op == 'SCALE':
            need(charts[r] == event[3], 'scalar chart')
        elif op in ('ADD', 'COPY'):
            need(charts[r] == charts[event[2]] == event[4], 'matched scalar charts')
        else:
            raise ValueError('unknown source opcode')
    need(charts[210] == charts[457] == 218, 'actual local common chart')
    return word


def suffix_bound(word):
    n = word['public'] + word['owned_fields']
    weights = [Q(0)] * n
    weights[210] = Q(1)
    peak, peak_at, clear_bounds = Q(1), [CLOCK + 1, 210], []
    for pc in range(CLOCK + 1, len(word['program'])):
        event = word['program'][pc]
        op, r = event[:2]
        if op in ('INIT', 'CLEAR'):
            if op == 'CLEAR':
                clear_bounds.append([pc, r, str(weights[r])])
            weights[r] = Q(0)
        elif op == 'SCALE':
            weights[r] *= abs(Q(event[2]))
        elif op in ('ADD', 'COPY'):
            if op == 'COPY':
                need(weights[r] == 0, 'COPY zero target in error model')
            weights[r] += abs(Q(event[3])) * weights[event[2]]
        elif op != 'MOVE':
            raise ValueError('unknown suffix opcode')
        if weights[r] > peak:
            peak, peak_at = weights[r], [pc + 1, r]
    public = weights[:word['public']]
    worst = max(range(len(public)), key=public.__getitem__)
    backward = [Q(0)] * n
    backward[worst] = Q(1)
    for event in reversed(word['program'][CLOCK + 1:]):
        op, r = event[:2]
        if op in ('INIT', 'CLEAR'):
            backward[r] = Q(0)
        elif op == 'SCALE':
            backward[r] *= abs(Q(event[2]))
        elif op in ('ADD', 'COPY'):
            backward[event[2]] += abs(Q(event[3])) * backward[r]
            if op == 'COPY':
                backward[r] = Q(0)
    need(backward[210] == public[worst], 'independent backward error transport')
    strict_power = 0
    while Q(2) ** strict_power <= peak:
        strict_power += 1
    return {
        'suffix_events': len(word['program']) - CLOCK - 1,
        'maximum_field_gain': str(peak), 'maximum_field_gain_witness': peak_at,
        'strict_peak_power_of_two': strict_power,
        'maximum_public_gain': str(public[worst]), 'maximum_public_role': worst,
        'public_sum_squared_gains': str(sum(x * x for x in public)),
        'nonzero_public_upper_bounds': sum(bool(x) for x in public),
        'suffix_clear_count': len(clear_bounds),
        'nonzero_clear_upper_bounds': sum(Q(row[2]) != 0 for row in clear_bounds),
        'clear_bounds_sha256': digest(clear_bounds),
        'public_gains_sha256': digest([str(x) for x in public]),
        'backward_witness_gain': str(backward[210]),
    }


def terminal_dependency(word):
    touches = []
    for pc, event in enumerate(word['program'][CLOCK + 1:], CLOCK + 1):
        op, dest = event[:2]
        if op in ('ADD', 'COPY'):
            need(event[2] != 210, 'no later source read of the changed field')
        if dest == 210:
            need(op == 'ADD' and event[2] != 210, 'only source-independent translations remain')
            touches.append([pc, event])
    need(touches == [[100527, ['ADD', 210, 292, '-1/2', 218]]], 'exact terminal update')
    need(word['final'][210] == 218, 'returned public field chart')
    return {'later_target_updates': touches, 'later_source_reads': 0,
            'returned_public_role': 210, 'returned_chart': 218,
            'other_public_and_owned_differences': 0, 'exact_difference_multiplier': 1}


def run_primitive(physical, registry, target, source, width, work=None):
    p = physical
    target_tape = p.Tape(p.encode_symbols(p.symbols(target, width)), 17)
    source_tape = p.Tape(p.encode_symbols(p.symbols(source, width)), 29, True)
    if work is None:
        work = [p.Tape((1, 0, 1, 1, 0), 41), p.Tape((0, 1, 0), 63)]
        work[0].pos += 2
        work[1].pos += 3
    context = p.Tape((1, 0, 1), 83, True)
    ports = {210: target_tape, 457: source_tape, 1569: work[0], 1570: work[1], 1571: context}
    need(len({id(t) for t in ports.values()}) == 5, 'physically distinct primitive ports')
    before = {i: t.body() for i, t in ports.items()}
    old_dirty = sum(len(t.body()) for t in work)
    start_actions = sum(t.actions for t in ports.values())
    measured = p.RowCounter(registry[TOKEN])
    state = SimpleNamespace(payloads=ports, primitive_work=(1569, 1570),
                            primitive_context=(1571,), services={TOKEN: measured})
    error = None
    try:
        p.M.Controller.primitive(state, TOKEN, (210, 457))
    except ValueError as exc:
        error = str(exc)
    need(source_tape.body() == before[457] and context.body() == before[1571], 'source and context preservation')
    need(all(t.protected() for t in ports.values()), 'local markers and ancestors')
    expected = tuple(x - y // 2 for x, y in zip(target, source))
    fits = all(-(1 << (width - 1)) <= x < (1 << (width - 1)) for x in expected)
    need((error is None) == fits, 'exact final signed range iff')
    if error is None:
        actual = p.decode(target_tape.body(), width)
        need(actual == expected, 'direct integer floor oracle')
        need(all(t.pos == t.origin for t in ports.values()), 'successful head return')
        need(all(t.blank() for t in work), 'complete successful work retirement')
    else:
        actual = None
        need(error == 'rounded signed output overflow', 'range rejection has the expected cause')
        need(target_tape.body() == before[210], 'complete-field failure atomicity')
    components = len(target)
    extent = components * (width + 1)
    actions = sum(t.actions for t in ports.values()) - start_actions
    charged = actions + measured.steps + 64
    bound = 512 * (extent + 1) + 64 * components + 7 * old_dirty + 16
    need(charged <= bound, 'physical actions and control rows fit complete bound')
    return {'fits': fits, 'output': None if actual is None else list(actual), 'charged': charged, 'bound': bound,
            'table_steps': measured.steps, 'old_dirty': old_dirty}, work


def physical_checks():
    sys.path.insert(0, str(REPO / 'research/current-rounded-scalar-tables'))
    from tables import compile_rounded
    import physical
    table, construction = compile_rounded('ADD', Q(-1, 2))
    need(set(row[0] for row in table) <= {'branch', 'write', 'move', 'goto', 'halt', 'reject'}, 'literal instruction alphabet')
    registry = {TOKEN: table}
    need(('local', CLOCK - 1, RAW) not in registry, 'wrong local clock rejected')
    need(('local', CLOCK, ('ADD', 210, 457, '1/2', 218)) not in registry, 'wrong local coefficient rejected')
    success, rejected, count, max_charge, min_slack = 0, 0, 0, 0, None
    for width in range(1, 6):
        bound = 1 << (width - 1)
        for x in range(-bound, bound):
            for y in range(-bound, bound):
                receipt, _ = run_primitive(physical, registry, (x, 0), (y, 0), width)
                count += 1
                success += receipt['fits']
                rejected += not receipt['fits']
                max_charge = max(max_charge, receipt['charged'])
                slack = receipt['bound'] - receipt['charged']
                min_slack = slack if min_slack is None else min(slack, min_slack)
    odd, work = run_primitive(physical, registry, (0, 0), (1, -1), 4)
    need(odd['output'] == [0, 1], 'both odd signs at the actual half-ADD')
    late, work = run_primitive(physical, registry, (0, 0, 7, 0), (1, 0, -2, 0), 4, work)
    need(not late['fits'], 'late overflow rejects the whole field')
    reuse, work = run_primitive(physical, registry, (0, 0), (1, -1), 2, work)
    need(reuse['output'] == [0, 1] and reuse['old_dirty'] > 0, 'failure work can be retired before reuse')
    native_field, work = run_primitive(physical, registry, (0,) * 1024, (1, -1) * 512, 4, work)
    need(native_field['output'] == [0, 1] * 512, '512-complex-value field staging')
    wrong_table, _ = compile_rounded('ADD', Q(1, 2))
    try:
        run_primitive(physical, {TOKEN: wrong_table}, (0, 0), (1, 0), 4)
    except ValueError as exc:
        need(str(exc) == 'direct integer floor oracle', 'wrong-sign control fails on semantics')
    else:
        raise ValueError('wrong-sign table accepted')
    return {'construction': construction, 'table_sha256': digest(table),
            'exhaustive_pairs': count, 'successful_pairs': success, 'range_rejections': rejected,
            'maximum_observed_charge': max_charge, 'minimum_bound_slack': min_slack,
            'odd_boundary': odd, 'late_overflow': late, 'reuse_after_failure': reuse,
            'native_512_field': {k: v for k, v in native_field.items() if k != 'output'},
            'controls': ['wrong clock', 'wrong coefficient token', 'wrong-sign table', 'late whole-field overflow']}


def calculate():
    word = authenticate()
    terminal = terminal_dependency(word)
    dependency_controls = []
    for label, replacement in [
        ('legal reversed ADD exports the error', ['ADD', 292, 210, '-1/2', 218]),
        ('legal SCALE changes the error gain', ['SCALE', 210, '2', 218]),
    ]:
        changed = deepcopy(word)
        changed['program'][100527] = replacement
        try:
            terminal_dependency(changed)
        except ValueError:
            dependency_controls.append(label)
        else:
            raise ValueError('terminal dependency control accepted')
    return {'word_sha256': digest(word), 'clock': CLOCK, 'raw': list(RAW),
            'physical': physical_checks(), 'suffix_error': suffix_bound(word),
            'terminal_dependency': terminal, 'dependency_controls': dependency_controls}


def main():
    result = calculate()
    need(result == json.loads((ROOT / 'RESULT.json').read_text()), 'complete receipt')
    print('PASS_CURRENT_HALF_ADD_SERVICE ' + json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
