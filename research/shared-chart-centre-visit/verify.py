#!/usr/bin/env python3
"""Price one shared exit-chart visit for the centre-chain observation.

The #4839 strip-all terminal moves every X support and pivot down to the empty
chart. Those supports already share chart 1, and every affected Y chart is a
width-8 subspace of that same chart. This word parks each selected centre on
chart 1 and lifts each Y by one nested rank. The endpoint matches the strip
policy. The incremental moment stays strictly negative even if the centre's
width-9 round trip is free. No new kappa.

Chris R / Clear1nsight's evaluator contract in
research/center-chain-terminal-feasibility/verify.py is reimplemented here
with attribution; that package is not modified. Apache-2.0.
Prepared by unpaidmoon with substantial Cursor Grok assistance.
"""
from collections import Counter, defaultdict
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import itertools
import json
import sys
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SRC = ROOT / 'research/center-helper-normal-form'
N = 640


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(path, name):
    out = types.ModuleType(name)
    out.__file__ = str(path)
    sys.modules[name] = out
    exec(compile(path.read_bytes(), str(path), 'exec'), out.__dict__)
    return out


def authenticate():
    pins = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    need(pins['base_commit'] == json.loads((HERE / 'TASK.json').read_text(encoding='utf-8'))['base_commit'],
         'TASK and SOURCES base commits differ')
    for row in pins['files']:
        if row['usage'] != 'input':
            continue
        raw = (ROOT / row['path']).read_bytes()
        need(sha256(raw).hexdigest() == row['sha256'], 'changed live input ' + row['path'])
    return pins


def plus(dst, src, coefficient=Q(1)):
    for key, value in tuple(src.items()):
        value = dst.get(key, Q(0)) + coefficient * value
        if value:
            dst[key] = value
        else:
            dst.pop(key, None)


def identity():
    return [{i: Q(1)} for i in range(N)]


def mm(a, b):
    out = []
    for row in a:
        new = {}
        for j, value in row.items():
            plus(new, b[j], value)
        out.append(new)
    return out


def transpose(a):
    out = [{} for _ in a]
    for i, row in enumerate(a):
        for j, value in row.items():
            out[j][i] = value
    return out


def rank(rows):
    pivots = {}
    for x in rows:
        while x:
            k = x.bit_length() - 1
            if k not in pivots:
                pivots[k] = x
                break
            x ^= pivots[k]
    return len(pivots)


def span(basis):
    need(rank(basis) == len(basis), 'independent chart basis')
    out = {0}
    for v in basis:
        out |= {x ^ v for x in tuple(out)}
    return out


def evaluate(events, starts, final, frames):
    """Retained nested-chart evaluator: transport changes only the chart label."""
    rows = [{(i, ()): Q(1)} for i in range(N)]
    charts = list(starts)
    spaces = list(map(span, frames))
    paid = Counter()
    for e in events:
        op, dst = e[:2]
        if op == 'add':
            _, _, src, q, f = e
            need(dst != src and charts[dst] == charts[src] == f, 'actual scalar common chart')
            plus(rows[dst], rows[src], q)
        elif op == 'scale':
            _, _, q, f = e
            need(charts[dst] == f and q != 0, 'invertible scale chart')
            rows[dst] = {k: q * v for k, v in rows[dst].items()}
        elif op == 'transport':
            _, _, a, b, width = e
            need(charts[dst] == a and (spaces[a] < spaces[b] or spaces[b] < spaces[a]),
                 'nested physical chart move')
            need(width == abs(len(frames[a]) - len(frames[b])), 'derive recursive width')
            paid[width] += 1
            charts[dst] = b
        elif op == 'warp':
            _, _, letter, a, b = e
            need(charts[dst] == a, 'actual warp chart')
            new = {}
            for (i, word), value in rows[dst].items():
                word = word[1:] if word and word[0] == -letter else (letter,) + word
                plus(new, {(i, word): value})
            rows[dst] = new
            charts[dst] = b
        else:
            raise ValueError('unknown actual operation')
    need(charts == final, 'every endpoint chart restored')
    need(all(not word for row in rows for i, word in row), 'all source warp words cancel')
    return [{i: v for (i, word), v in row.items()} for row in rows], paid


def target(abi, observations, selected):
    out = identity()
    for i in range(112):
        out[112 + i][i] = Q(1)
    for i, row in enumerate(abi['B_rows']):
        plus(out[i], {j: Q(v) for j, v in row if j - 632 not in selected})
    for j, row in enumerate(observations):
        if j not in selected:
            plus(out[632 + j], row)
    return out


def inverse(a):
    unit = identity()
    k = [dict(row) for row in a]
    for i in range(N):
        plus(k[i], unit[i], Q(-1))
    k2 = mm(k, k)
    need(not any(mm(k2, k)), 'cube-zero endpoint')
    inv = identity()
    for i in range(N):
        plus(inv[i], k[i], Q(-1))
        plus(inv[i], k2[i])
    need(mm(inv, a) == mm(a, inv) == unit, 'two-sided inverse')
    return inv


def raw_dual(events):
    """Predecessor tail convention: swap each ADD and leave transports in order."""
    out = []
    for e in events:
        if e[0] == 'add':
            out.append(('add', e[2], e[1], -e[3], e[4]))
        elif e[0] == 'scale':
            out.append(('scale', e[1], 1 / e[2], e[3]))
        else:
            need(e[0] == 'transport', 'no extra warp hidden in the tail')
            out.append(e)
    return out


def rejected(fn):
    try:
        fn()
    except ValueError:
        return True
    return False


def y_terms(abi, centre):
    terms = []
    for i, row in enumerate(abi['B_rows']):
        for k, v in row:
            if k == centre:
                terms.append((i, centre, Q(v)))
    return terms


def shared_tail(selected, observations, abi, final, frames):
    """Park every selected centre on chart 1, correct there, then restore.

    Each affected Y chart is a width-8 subspace of chart 1, so the Y register
    makes one width-1 hop up, subtracts, and hops back. The centre's own
    empty-chart round trip is one width-9 hop each way.
    """
    events = []
    y_by_field = defaultdict(list)
    obs_fields = []
    for j in selected:
        centre = 632 + j
        need(final[centre] == 0, 'centre exits at the empty chart')
        events.append(('transport', centre, 0, 1, len(frames[1]) - len(frames[0])))
        for i, value in sorted(observations[j].items()):
            need(final[i] == 1, 'observation support exits at chart 1')
            events.append(('add', centre, i, -value, 1))
            obs_fields.append(i)
        for field, owner, value in y_terms(abi, centre):
            y_by_field[field].append((owner, value))
    y_fields = sorted(y_by_field)
    need(set(y_fields).isdisjoint(obs_fields), 'Y fields are distinct from the observation supports')
    for field in y_fields:
        hop = len(frames[1]) - len(frames[final[field]])
        events.append(('transport', field, final[field], 1, hop))
        for owner, value in y_by_field[field]:
            events.append(('add', field, owner, -value, 1))
        events.append(('transport', field, 1, final[field], hop))
    for j in selected:
        events.append(('transport', 632 + j, 1, 0, len(frames[1]) - len(frames[0])))
    return events, y_fields, obs_fields


def strip_tail(selected, observations, abi, final, frames):
    """The predecessor policy: strip every touched field, correct, restore."""
    y_by_field = defaultdict(list)
    obs_fields = []
    for j in selected:
        centre = 632 + j
        for i, value in observations[j].items():
            obs_fields.append(i)
        for field, owner, value in y_terms(abi, centre):
            y_by_field[field].append((owner, value))
    touched = sorted(set(obs_fields) | set(y_by_field))
    events = [('transport', i, final[i], 0, len(frames[final[i]])) for i in touched]
    for j in selected:
        centre = 632 + j
        events.extend(('add', centre, i, -value, 0) for i, value in sorted(observations[j].items()))
        for field, owner, value in y_terms(abi, centre):
            events.append(('add', field, owner, -value, 0))
    events.extend(('transport', i, 0, final[i], len(frames[final[i]])) for i in touched)
    return events


def moment_upper(selected_count, y_count):
    """Delta = s*8^t - 2 n_Y - 2 s*9^t for t = 1-C in [0,1].

    On that interval 1 <= 8^t <= 9^t. The 9^t terms therefore dominate the
    reward, and the largest value is the t = 0 number -s - 2 n_Y.
    """
    need(selected_count > 0 and y_count > 2 * selected_count, 'Y supports exceed the reward count')
    upper = -selected_count - 2 * y_count
    # Dropping the two width-9 charges leaves s*8^t - 2 n_Y <= 8 s - 2 n_Y.
    free_round_trip = 8 * selected_count - 2 * y_count
    need(upper < 0 and free_round_trip < 0, 'both relaxations stay negative')
    return upper, free_round_trip


def paid_dict(counter):
    return {str(k): counter[k] for k in sorted(counter)}


def run():
    pins = authenticate()
    normal = load(SRC / 'verify.py', 'centre_normalizer')
    engine = load(SRC / 'inputs/retained_verify.py', 'frozen_centre_emitter')
    engine.HERE = SRC
    payload = engine.load()
    frames = payload['canonical']['frames']
    need(frames[0] == [] and len(frames[1]) == 9, 'chart 0 is empty and chart 1 has width 9')
    need(span(frames[0]) < span(frames[1]), 'empty chart is strictly nested in chart 1')
    abi = json.loads((SRC / 'inputs/ABI.json').read_text(encoding='utf-8'))
    rows = [{i: Q(v) for i, v in row} for row in abi['R_rows']]
    cold = {i for i in range(224, 632)
            if payload['canonical']['start'][i] == 0 and payload['canonical']['final'][i] == 1}
    header, det, _ = normal.make_header(rows, cold)
    footer = normal.inverse_header(header, 1)
    need(len(header) == len(footer) == 379 and det == 64, 'whole joint normalization stays charged')
    starts, _centers, source = engine.emit(payload)
    _, _, dual_source = engine.emit(payload, dual=True)
    final = payload['canonical']['final'] + [0] * 8
    observations = [{i: v for i, v in rows[j].items() if i < 224} | {normal.J[j]: Q(1)}
                    for j in range(8)]
    for j, piv in enumerate(normal.J):
        need(final[piv] == 1 and all(final[i] == 1 for i in observations[j]),
             'every observation support exits at chart 1')
        for field, _owner, _value in y_terms(abi, 632 + j):
            need(len(frames[final[field]]) == 8, 'each affected Y chart has width 8')
            need(span(frames[final[field]]) < span(frames[1]), 'each Y chart is strictly inside chart 1')
            need(len(frames[1]) - len(frames[final[field]]) == 1, 'Y hop into chart 1 has width 1')
    word = header + source + footer
    dual_prefix = normal.dual_header(header) + dual_source + normal.dual_header(footer)
    original, old_paid = evaluate(word, starts, final, frames)
    need(original == target(abi, observations, set()), 'full normalized source ABI')
    need(old_paid == Counter(engine.PAID), 'source recursive profile')
    groups = [(j,) for j in range(8)] + list(itertools.combinations(range(8), 2)) + [tuple(range(8))]
    need(len(groups) == 37, 'eight singletons, twenty-eight pairs and the octet')
    screens = []
    for group in groups:
        selected = set(group)
        shared, y_fields, obs_fields = shared_tail(selected, observations, abi, final, frames)
        stripped = strip_tail(selected, observations, abi, final, frames)
        wanted = target(abi, observations, selected)
        shared_rows, shared_paid = evaluate(word + shared, starts, final, frames)
        strip_rows, strip_paid = evaluate(word + stripped, starts, final, frames)
        need(shared_rows == wanted == strip_rows, 'shared visit and strip policy share the endpoint')
        dual_rows, dual_paid = evaluate(dual_prefix + raw_dual(shared), starts, final, frames)
        need(dual_rows == transpose(inverse(wanted)) and dual_paid == shared_paid,
             'raw inverse transpose of the shared visit')
        delta = shared_paid - old_paid
        strip_delta = strip_paid - old_paid
        need(delta == Counter({1: 2 * len(y_fields), 9: 2 * len(selected)}),
             'shared visit pays two width-9 centre moves and two width-1 Y hops')
        upper, free_round_trip = moment_upper(len(selected), len(y_fields))
        screens.append({
            'selected': list(group),
            'observation_supports': len(set(obs_fields)),
            'distinct_Y': len(y_fields),
            'shared_added_requests': paid_dict(delta),
            'strip_added_requests': paid_dict(strip_delta),
            'moment_expression': 's*8^t - 2*n_Y - 2*s*9^t',
            'uniform_upper_bound': upper,
            'upper_bound_if_width9_free': free_round_trip,
            'scalar_adds': sum(1 for e in shared if e[0] == 'add'),
        })
    chosen = screens[0]
    need(chosen['selected'] == [0], 'first screen is centre 0')
    need(chosen['distinct_Y'] == 56 and chosen['shared_added_requests'] == {'1': 112, '9': 2},
         'centre 0 replaces the strip bill by one width-9 round trip and 112 width-1 hops')
    need(chosen['strip_added_requests'] == {'8': 112, '9': 114}, 'strip policy bill for centre 0')
    need(chosen['uniform_upper_bound'] == -113 and chosen['upper_bound_if_width9_free'] == -104,
         'centre-0 moment upper bound')
    pair_bounds = {row['uniform_upper_bound'] for row in screens if len(row['selected']) == 2}
    octet = screens[-1]
    need(octet['selected'] == list(range(8)) and octet['distinct_Y'] == 112
         and octet['shared_added_requests'] == {'1': 224, '9': 16}
         and octet['uniform_upper_bound'] == -232
         and octet['upper_bound_if_width9_free'] == -160, 'octet shared visit')
    # The predecessor's pair census had 88 distinct Y fields. Keep that fact
    # visible; every pair in this schedule uses that same count.
    need({row['distinct_Y'] for row in screens if len(row['selected']) == 2} == {88},
         'every pair meets 88 distinct Y fields')
    need(pair_bounds == {-178}, 'every pair upper bound is -178')
    need({row['upper_bound_if_width9_free'] for row in screens if len(row['selected']) == 2} == {-160},
         'every pair still loses if the width-9 round trips are free')

    tail, y_fields, _obs = shared_tail({0}, observations, abi, final, frames)
    wanted = target(abi, observations, {0})
    dropped = False
    missing = []
    for event in tail:
        if not dropped and event[0] == 'add' and event[1] == 632 and event[2] < 224:
            dropped = True
            continue
        missing.append(event)
    need(dropped and evaluate(word + missing, starts, final, frames)[0] != wanted,
         'omitted X observation rejected')
    missing_y = [e for e in tail if not (e[0] == 'add' and e[1] == y_fields[0])]
    need(evaluate(word + missing_y, starts, final, frames)[0] != wanted,
         'omitted centre-to-Y correction rejected')
    need(rejected(lambda: evaluate(word + [('add', 632, 0, Q(-1), 0)], starts, final, frames)),
         'ADD at the empty chart while X remains on chart 1 rejected')
    need(rejected(lambda: evaluate(word + [('transport', 632, 0, 1, 8)], starts, final, frames)),
         'undercharged chart-1 width rejected')
    y_chart = final[y_fields[0]]
    # The centre is still on the empty chart here, so a hop that claims to
    # start on chart 1 is rejected. The legal width-1 Y hop is inside the word.
    need(rejected(lambda: evaluate(
        word + [('transport', 632, 1, y_chart, 1)], starts, final, frames)),
         'centre cannot leave chart 1 before it arrives there')
    short = []
    replaced = False
    for event in tail:
        if not replaced and event[0] == 'transport' and event[1] == y_fields[0] and event[2] != 0:
            short.append((event[0], event[1], event[2], event[3], event[4] + 1))
            replaced = True
        else:
            short.append(event)
    need(replaced and rejected(lambda: evaluate(word + short, starts, final, frames)),
         'overcharged Y hop rejected')
    controls = [
        'missing data observation',
        'missing centre-to-Y correction',
        'empty-chart ADD against a chart-1 support',
        'undercharged centre transport',
        'centre hop before arrival',
        'overcharged Y hop',
    ]
    return {
        'status': 'PASS_SHARED_CHART_CENTRE_VISIT_STILL_LOSES',
        'new_kappa': None,
        'base_commit': pins['base_commit'],
        'model': 'retained nested-chart ADD/transport evaluator; no fresh Clifford replay',
        'source_paid': paid_dict(old_paid),
        'joint_normalization_gates': 758,
        'groups_checked': len(screens),
        'centre0': chosen,
        'pair_distinct_Y': 88,
        'pair_uniform_upper_bound': -178,
        'octet': octet,
        'screens': screens,
        'controls': controls,
        'compiler_route': 'unchanged; no outer admission',
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    value = json.loads(json.dumps(run()))
    if args.out:
        need(not args.out.exists(), 'fresh output file required')
        args.out.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    else:
        expected = json.loads((HERE / 'RESULT.json').read_text(encoding='utf-8'))
        canonical = lambda item: json.dumps(item, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
        need(canonical(value) == canonical(expected), 'exact scientific receipt')
    print('PASS_SHARED_CHART_CENTRE_VISIT_STILL_LOSES no_new_kappa')


if __name__ == '__main__':
    main()
