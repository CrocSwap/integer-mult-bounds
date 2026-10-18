#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Source-bound R2 native slice; no native producer code is imported."""
import argparse
import copy
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path
import types

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SOURCE = 'research/rank7-shared-restore-fanin/evidence/'
KERNEL = 'research/frontier1094-recipes-exact-seed76/clifford.py'
W = [256, 128, 64, 34, 17, 11, 4]
E = [256, 128, 64, 34, 16, 10, 4, 1]
FULL = [256, 128, 64, 32, 16, 8, 4, 2, 1]
PHASES = ['zero_frame_precondition', 'entry_adapters', 'A', 'centers', 'B',
          'cleanup_tail', 'final', 'exit_adapters', 'full_frame_cleanup', 'done']
FILES = ('CANONICAL-WORD.json.gz', 'LOCAL-PROGRAMS.json.gz',
         'CLIFFORD-RECIPES.json', 'RESIDUAL-ADAPTERS.json')


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def unique(pairs):
    out = dict(pairs)
    need(len(out) == len(pairs), 'duplicate JSON key')
    return out


def parse(raw):
    need(len(raw) <= 16 * 1024 * 1024, 'artifact capacity')
    return json.loads(raw, object_pairs_hook=unique)


def read(path):
    raw = path.read_bytes()
    return parse(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def pin_inputs():
    blobs = {}
    for row in read(PACKAGE / 'SOURCES.json')['files']:
        if row['usage'] == 'input':
            raw = (ROOT / row['path']).read_bytes()
            need(sha(raw) == row['sha256'], 'source pin: ' + row['path'])
            blobs[row['path']] = raw
    required = {KERNEL, SOURCE + 'NATIVE-RECEIPT.json', SOURCE + 'SOURCE-MANIFEST.json',
                SOURCE + 'WORD-base.json.gz', SOURCE + 'WORD-extra.json.gz'}
    need(required <= set(blobs), 'required source inventory')
    return blobs


def artifacts(blobs, tag, data):
    receipt = parse(blobs[SOURCE + 'NATIVE-RECEIPT.json'])['providers'][tag]
    need(sha(blobs[SOURCE + f'WORD-{tag}.json.gz']) == receipt['word_sha256'], 'provider word binding')
    out = {}
    for name in FILES:
        path = data / tag / (name if name.endswith('.gz') else name + '.gz')
        raw = path.read_bytes()
        original = raw if name.endswith('.gz') else gzip.decompress(raw)
        need(sha(original) == receipt['complete_native_files']['local/' + name],
             'native artifact binding: ' + tag + '/' + name)
        out[name] = parse(gzip.decompress(original) if name.endswith('.gz') else original)
    return out


def span(rows):
    out = {0}
    for x in rows:
        need(type(x) is int and 0 < x < 512 and x not in out, 'independent binary frame')
        out |= {y ^ x for y in out}
    return frozenset(out)


def regs(g):
    need(g[0] in ('add', 'scale'), 'restore gate kind')
    need(len(g) == (6 if g[0] == 'add' else 5), 'restore gate schema')
    return g[1:3] if g[0] == 'add' else g[1:2]


def frame_boundaries(word, canonical):
    """Read source frame labels, independently of the emitted prefix."""
    need((word['report']['h'], word['report']['v'], word['report']['R']) == (9, 112, 480), 'source domain')
    need((canonical['h'], canonical['v'], canonical['R']) == (9, 112, 408)
         and canonical['ports'] == word['ports'], 'canonical domain and source ports')
    kept = [r for r in range(704) if r not in word['removed']]
    need(len(kept) == 632 and kept[224:] == canonical['helper_origin'], 'compact map')
    frames = canonical['frames']
    spaces = [span(f) for f in frames]
    need(len(set(spaces)) == len(spaces), 'unique canonical frames')
    ids = {s: i for i, s in enumerate(spaces)}
    starts = {r: [word['ports'][r]] if r < 112 else [] for r in kept}
    starts.update({int(r): f for r, f in word['start_extra'].items()})
    need([ids[span(starts[r])] for r in kept] == canonical['start'], 'source entrances')
    finals = {r: FULL for r in kept}
    for r in range(112, 224):
        p = word['ports'][r - 112]
        need(spaces[canonical['final'][r]] == frozenset(x for x in range(512) if (x & p).bit_count() % 2 == 0),
             'target terminal frame')
        finals[r] = frames[canonical['final'][r]]
    finals.update({int(r): f for r, f in word['helper_final'].items()})
    need([ids[span(finals[r])] for r in kept] == canonical['final'], 'source terminals')
    state = {r: ids[span(starts[r])] for r in kept}

    def move(r, target):
        f = ids[span(target)]
        need(spaces[state[r]] <= spaces[f], 'source monotone frame')
        state[r] = f

    for g in word['A']:
        if g[0] == 'warp':
            need(state[g[1]] == ids[span(g[3])], 'A warp boundary')
            state[g[1]] = ids[span(g[4])]
        else:
            for r in regs(g):
                move(r, g[-1])
    warps = {}
    for pos, r, _columns, old, new in word['warps']:
        warps.setdefault(pos, []).append((r, old, new))
    for i in range(len(word['B']) + 1):
        for r, old, new in warps.get(i, []):
            need(state[r] == ids[span(old)], 'B warp boundary')
            state[r] = ids[span(new)]
        if i < len(word['B']):
            for r in regs(word['B'][i]):
                move(r, word['B'][i][-1])
    return kept, ids, [state[r] for r in kept]


def scalar(g, mapping, backward):
    operands = [['L', mapping[r]] for r in regs(g)]
    a, b = g[-3:-1]
    need(type(a) is int and type(b) is int and a and b, 'nonzero rational scalar')
    if backward and g[0] == 'add':
        operands.reverse()
        a = -a
    elif backward:
        a, b = b, a
    return [g[0], *operands, a, b]


def expected_tail(word, canonical, kept, ids, boundary, backward):
    state = boundary.copy()
    mapping = {r: i for i, r in enumerate(kept)}
    frames = canonical['frames']
    spaces = [span(f) for f in frames]
    out, touched = [], []
    for i, g in enumerate(word['restore']):
        f = ids[span(g[-1])]
        for old_r in regs(g):
            r = mapping[old_r]
            old = state[r]
            need(spaces[old] <= spaces[f], 'tail monotone frame')
            if old != f:
                event = ['climb', 'cleanup_tail', r, old, f, len(frames[f]) - len(frames[old])]
                out.append(event)
                if old_r in (40, 54) and i >= 162:
                    touched.append([i, event])
                state[r] = f
        out.append(['scalar', scalar(g, mapping, backward), f])
    final = []
    for r, f in enumerate(canonical['final']):
        old = state[r]
        need(spaces[old] <= spaces[f], 'final monotone frame')
        if old != f:
            final.append(['climb', 'final', r, old, f, len(frames[f]) - len(frames[old])])
    return out, final, touched


def bind_events(word, canonical, programs):
    kept, ids, boundary = frame_boundaries(word, canonical)
    frames = canonical['frames']
    wrapped = [r for r in range(224, len(kept)) if canonical['start'][r] != 0 or canonical['final'][r] != 1]
    keys = [str(canonical['start'][r]) if canonical['final'][r] == 1 else
            f"{canonical['start'][r]}:{canonical['final'][r]}" for r in wrapped]
    need(set(programs) == {'forward', 'backward'}, 'both emitted orientations')
    report = {}
    for orientation, stream in programs.items():
        need(len(stream) <= 50000, 'event capacity')
        phases, sections = [], {}
        cursor = canonical['start'].copy()
        spaces = [span(f) for f in frames]
        for event in stream:
            need(type(event) is list and event, 'event schema')
            if event[0] == 'phase':
                phases.append(event[1])
                need(phases == PHASES[:len(phases)], 'phase order')
                sections[event[1]] = []
                if event[1] == 'cleanup_tail':
                    need(cursor == boundary, 'emitted/source tail entrance')
            else:
                need(phases, 'event before phase')
                sections[phases[-1]].append(event)
                if phases[-1] in PHASES[:5]:
                    if event[0] == 'climb':
                        _, phase, r, old, new, rank = event
                        need(phase == phases[-1] and cursor[r] == old and spaces[old] < spaces[new]
                             and rank == len(frames[new]) - len(frames[old]), 'prefix climb chronology')
                        cursor[r] = new
                    elif event[0] == 'warp':
                        _, role, _op, old, new = event
                        need(role[0] == 'L' and cursor[role[1]] == old, 'prefix warp chronology')
                        cursor[role[1]] = new
        need(phases == PHASES, 'complete phases')
        tail, final, touched = expected_tail(word, canonical, kept, ids, boundary, orientation == 'backward')
        need(sections['cleanup_tail'] == tail, 'exact source tail event sequence')
        need(sections['final'] == final, 'exact final event sequence')
        expected_wrappers = []
        for side in ('pre', 'post'):
            for r in wrapped:
                a, b = canonical['start'][r], canonical['final'][r]
                expected_wrappers.append(['entry_adapters' if side == 'pre' else 'full_frame_cleanup',
                    ['residual_adapter', side, r, a] + ([b] if b != 1 else [])])
        actual = [[phase, e] for phase in PHASES for e in sections[phase] if e[0] == 'residual_adapter']
        need(actual == expected_wrappers, 'residual wrapper owner/side/phase binding')
        post = [e for phase, e in expected_wrappers if phase == 'full_frame_cleanup']
        need(sections['full_frame_cleanup'][-len(post):] == post, 'post wrappers after complete cleanup')
        entry_all = []
        for r, a in enumerate(canonical['start']):
            b = canonical['final'][r]
            entry_all.append(['residual_adapter', 'pre', r, a] + ([b] if b != 1 else [])
                             if r in wrapped else ['adapter', 'old_to_new', r, a])
        need(sections['entry_adapters'] == entry_all, 'complete entry adapter phase')
        for r in (18, 22, 40, 54):
            need(r not in wrapped and canonical['final'][r] == 1, 'R2 ordinary source boundary')
            entry = [e for e in sections['entry_adapters'] if e[0] == 'adapter' and e[2] == r]
            exit_ = [e for e in sections['exit_adapters'] if e[0] == 'adapter' and e[2] == r]
            need(entry == [['adapter', 'old_to_new', r, canonical['start'][r]]] and
                 exit_ == [['adapter', 'new_to_old', r, 1]], 'ordinary source adapter binding')
        need([(i, e[2], frames[e[3]], frames[e[4]], e[5]) for i, e in touched] ==
             [(163, 40, W, E, 1), (203, 40, E, FULL, 1), (203, 54, W, FULL, 2)],
             'exact changed native climbs')
        report[orientation] = {'events': len(stream), 'tail_events': len(tail),
            'final_events': len(final), 'changed_climbs': touched, 'wrapper_occurrences': len(actual)}
    return report, sorted(set(keys)), ids


def restore_control(word):
    gates = word['restore']
    need(len(gates) == 204, 'R2 restore length')
    literals = {162: ['add', 40, 54, -2, 1, W], 163: ['add', 18, 40, 1, 1, E],
                175: ['add', 22, 40, 1, 1, E], 176: ['add', 22, 45, -1, 1, E],
                203: ['add', 40, 54, 2, 1, FULL]}
    need(all(gates[i] == g for i, g in literals.items()), 'R2 literal boundaries')
    need([i for i, g in enumerate(gates) if i >= 162 and set(regs(g)) & {40, 54}] ==
         [162, 163, 175, 203], 'exclusive fan-in source contacts')
    old = copy.deepcopy(gates[:162] + gates[163:203])
    old.insert(163, ['add', 18, 54, -2, 1, E])
    old.insert(177, ['add', 22, 54, -2, 1, E])
    kept = [r for r in range(704) if r not in word['removed']]

    def matrix(gs, backward):
        rows = {r: {r: Fraction(1)} for r in kept}
        for g in gs:
            if g[0] == 'scale':
                q = Fraction(g[2], g[3])
                q = 1 / q if backward else q
                rows[g[1]] = {j: q * x for j, x in rows[g[1]].items()}
            else:
                dst, src = g[1:3]
                q = Fraction(g[3], g[4])
                if backward:
                    dst, src, q = src, dst, -q
                for j, x in list(rows[src].items()):
                    value = rows[dst].get(j, 0) + q * x
                    if value:
                        rows[dst][j] = value
                    else:
                        rows[dst].pop(j, None)
        return rows
    for backward in (False, True):
        need(matrix(gates, backward) == matrix(old, backward), 'R1/R2 arbitrary-input equality')
    return {'columns_per_orientation': len(kept), 'restore_gates': len(gates)}


def dual(circuit):
    result = copy.deepcopy(circuit)
    for i, g in enumerate(result):
        if g[0] == 'C':
            result[i] = (g[0], g[1], -g[2])
        elif g[0] == 'D':
            result[i] = (g[0], g[1], [(-a) % 4 for a in g[2]])
        elif g[0] == 'PH':
            result[i] = (g[0], -g[1] % 4)
        else:
            need(g[0] in ('P', 'X'), 'dual native gate')
    return result


def decode(kernel, rec):
    need(type(rec['rank']) is int and 0 <= rec['rank'] <= 9, 'native rank domain')
    need(kernel.well_formed(rec['left']), 'left monomial schema')
    if rec['rank'] == 0:
        need(rec['right'] is None, 'rank-zero right factor')
        return kernel.monomial(rec['left'])
    need(kernel.well_formed(rec['right']), 'right monomial schema')
    return kernel.monomial(rec['right']) + kernel.fourier(rec['rank']) + kernel.monomial(rec['left'])


def check_recipe(kernel, rec, old, new, cache):
    need(rec['rank'] == len(new) - len(old), 'recipe rank difference')
    key = json.dumps([rec, old, new], sort_keys=True)
    actual = decode(kernel, rec)
    if key not in cache:
        expected = kernel.adjoint(kernel.canonical_frame(old)) + kernel.canonical_frame(new)
        need(kernel.same_operator(actual, expected), 'native phase-exact operator')
        need(kernel.same_operator(dual(actual), dual(expected)), 'dual phase-exact operator')
        cache.add(key)
    return actual


def semantics(kernel, canonical, recipes, adapters, keys, ids, cache):
    frames = canonical['frames']
    children = {(r['old'], r['new']): r for r in recipes['children']}
    need(len(children) == len(recipes['children']), 'unique child recipe keys')
    circuits = []
    for old, new in ((W, E), (E, FULL), (W, FULL)):
        key = (ids[span(old)], ids[span(new)])
        need(key in children, 'changed child recipe coverage')
        circuits.append(check_recipe(kernel, children[key], old, new, cache))
    need(kernel.same_operator(circuits[0] + circuits[1], circuits[2]), 'split/fused native equality')
    need(kernel.same_operator(dual(circuits[0] + circuits[1]), dual(circuits[2])), 'dual split/fused equality')
    need(set(adapters['recipes']) == set(keys), 'exact used residual recipe inventory')
    for key in keys:
        rec = adapters['recipes'][key]
        a, b = rec['frame'], rec.get('terminal', 1)
        need(key == (str(a) if b == 1 else f'{a}:{b}'), 'residual recipe key')
        need(rec['vectors'] == frames[a] and rec['entrance_rank'] == len(frames[a]), 'residual entrance metadata')
        if b != 1:
            need(rec['terminal_vectors'] == frames[b] and rec['terminal_rank'] == len(frames[b]),
                 'residual terminal metadata')
        check_recipe(kernel, rec, frames[a], frames[b], cache)
        wrapped_key = 'wrapped:' + json.dumps([rec, frames[a], frames[b]], sort_keys=True)
        if wrapped_key not in cache:
            sequence = (kernel.adjoint(kernel.monomial(rec['right'])) +
                        kernel.adjoint(kernel.canonical_frame(frames[a])) + kernel.canonical_frame(frames[b]) +
                        kernel.adjoint(kernel.monomial(rec['left'])))
            need(kernel.same_operator(sequence, kernel.fourier(rec['rank'])), 'inverse residual wrapper order')
            need(kernel.same_operator(dual(sequence), kernel.fourier(rec['rank'], -1)), 'dual residual wrapper order')
            cache.add(wrapped_key)
    for r in (18, 22, 40, 54):
        matches = [x for x in recipes['endpoint_adapters'] if x['role'] == 'source' and x['port'] == r]
        need(len(matches) == 1, 'source endpoint recipe coverage')
        rec = matches[0]
        need(rec['rank'] == 0 and rec['frame'] == canonical['start'][r], 'source endpoint rank/frame')
        reference = [('C', canonical['ports'][r], -1)] + kernel.canonical_frame(frames[rec['frame']])
        actual = decode(kernel, rec)
        need(kernel.same_operator(actual, reference), 'source endpoint phase')
        need(kernel.same_operator(dual(actual), dual(reference)), 'dual source endpoint phase')
    return {'changed_child_recipes': 3, 'residual_recipes': len(keys), 'source_endpoint_recipes': 4,
            'native_columns_each': 512, 'orientations': 2, 'phase_included': True}


def audit(kernel, word, data, cache):
    canonical, programs, recipes, adapters = (data[n] for n in FILES)
    events, keys, ids = bind_events(word, canonical, programs)
    return {'events': events, 'scalar_control': restore_control(word),
            'native': semantics(kernel, canonical, recipes, adapters, keys, ids, cache)}


def failure_controls(kernel, word, data):
    """Mutate semantic payloads after authentication, so hash checks cannot mask bugs."""
    rejected = []

    def reject(name, mutate, predicate, reason):
        w, d = copy.deepcopy(word), copy.deepcopy(data)
        mutate(w, d)
        need(w != word or d != data, 'nonvacuous mutant: ' + name)
        try:
            predicate(w, d)
        except ValueError as exc:
            need(str(exc) == reason, 'wrong rejection for ' + name + ': ' + str(exc))
            rejected.append(name)
        else:
            raise ValueError('semantic mutant accepted: ' + name)

    event_check = lambda w, d: bind_events(w, d[FILES[0]], d[FILES[1]])
    def event(d, orientation, predicate):
        return next(e for e in d[FILES[1]][orientation] if predicate(e))

    reject('forward fan-in sign', lambda w, d: event(d, 'forward', lambda e: e[:1] == ['scalar'] and
           e[1] == ['add', ['L', 40], ['L', 54], -2, 1])[1].__setitem__(3, 2),
           event_check, 'exact source tail event sequence')
    reject('dual fan-in sign', lambda w, d: event(d, 'backward', lambda e: e[:1] == ['scalar'] and
           e[1] == ['add', ['L', 54], ['L', 40], 2, 1])[1].__setitem__(3, -2),
           event_check, 'exact source tail event sequence')
    reject('rank-two child undercharge', lambda w, d: event(d, 'forward', lambda e:
           e[:3] == ['climb', 'cleanup_tail', 54] and e[-1] == 2).__setitem__(5, 1),
           event_check, 'exact source tail event sequence')
    reject('tail phase substitution', lambda w, d: event(d, 'forward', lambda e:
           e == ['phase', 'cleanup_tail']).__setitem__(1, 'final'), event_check, 'phase order')
    reject('wrapper side', lambda w, d: event(d, 'forward', lambda e:
           e[:2] == ['residual_adapter', 'post']).__setitem__(1, 'pre'),
           event_check, 'residual wrapper owner/side/phase binding')
    reject('dual wrapper owner', lambda w, d: event(d, 'backward', lambda e:
           e[:2] == ['residual_adapter', 'pre']).__setitem__(2, 40),
           event_check, 'residual wrapper owner/side/phase binding')
    def early_post(w, d):
        stream = d[FILES[1]]['forward']
        i = next(i for i, e in enumerate(stream) if e[:2] == ['residual_adapter', 'post'])
        j = next(i for i, e in enumerate(stream) if e == ['phase', 'full_frame_cleanup'])
        block = stream[i:-1]
        del stream[i:-1]
        stream[j + 1:j + 1] = block
    reject('post wrappers before cleanup', early_post, event_check, 'post wrappers after complete cleanup')
    reject('source exit frame', lambda w, d: event(d, 'forward', lambda e:
           e[:3] == ['adapter', 'new_to_old', 40]).__setitem__(3, 0),
           event_check, 'ordinary source adapter binding')
    reject('missing dirty restoration', lambda w, d: w['restore'].pop(),
           lambda w, d: restore_control(w), 'R2 restore length')
    reject('extra fan-in observer', lambda w, d: w['restore'][180].__setitem__(2, 54),
           lambda w, d: restore_control(w), 'exclusive fan-in source contacts')
    reject('prefix wrong source frame', lambda w, d: event(d, 'forward', lambda e:
           e[0] == 'climb' and e[3] != 0).__setitem__(3, 0), event_check, 'prefix climb chronology')

    wid = data[FILES[0]]['frames'].index(W)
    def child(d):
        return next(x for x in d[FILES[2]]['children'] if (x['old'], x['new']) == (wid, 1))
    def phase(rec):
        rec['left']['phase'] = (rec['left']['phase'] + 1) % 4
    child_check = lambda w, d: check_recipe(kernel, child(d), W, FULL, set())
    reject('native global phase', lambda w, d: phase(child(d)), child_check, 'native phase-exact operator')
    reject('native translation', lambda w, d: child(d)['left'].__setitem__('offset', child(d)['left']['offset'] ^ 1),
           child_check, 'native phase-exact operator')
    reject('native child rank', lambda w, d: child(d).__setitem__('rank', 1), child_check, 'recipe rank difference')
    key = sorted(data[FILES[3]]['recipes'])[0]
    def residual_check(w, d):
        rec = d[FILES[3]]['recipes'][key]
        frames = d[FILES[0]]['frames']
        check_recipe(kernel, rec, frames[rec['frame']], frames[rec.get('terminal', 1)], set())
    reject('residual global phase', lambda w, d: phase(d[FILES[3]]['recipes'][key]),
           residual_check, 'native phase-exact operator')
    reject('residual translation', lambda w, d: d[FILES[3]]['recipes'][key]['right'].__setitem__('offset',
           d[FILES[3]]['recipes'][key]['right']['offset'] ^ 1), residual_check, 'native phase-exact operator')
    return rejected


def compute(data_path):
    blobs = pin_inputs()
    kernel = types.ModuleType('r2_independent_clifford')
    exec(compile(blobs[KERNEL], KERNEL, 'exec'), kernel.__dict__)
    need(kernel.same_operator([('C', 1, 1), ('C', 1, 1)], [('X', 1)]), 'hand C squared calibration')
    need(kernel.same_operator([('C', 3, 1), ('C', 3, -1)], []), 'hand inverse calibration')
    need(not kernel.same_operator([('PH', 1)], []), 'global phase sensitivity calibration')
    cache, providers = set(), {}
    for tag in ('base', 'extra'):
        word = parse(gzip.decompress(blobs[SOURCE + f'WORD-{tag}.json.gz']))
        data = artifacts(blobs, tag, data_path)
        providers[tag] = audit(kernel, word, data, cache)
        providers[tag]['rejected_controls'] = failure_controls(kernel, word, data)
    need(pin_inputs() == blobs, 'source changed during check')
    return {'status': 'PASS_PR3044_R2_NATIVE_SLICE', 'providers': providers,
            'kernel_sha256': sha(blobs[KERNEL]),
            'scope': 'R2 tail/final binding, three native children, four source endpoints, all used residual '
                     'recipes and placement. Other native phases, physical owners, full cleanup semantics '
                     'and supplier/outer theorem remain outside this audit.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', action='store_true')
    parser.add_argument('--data', type=Path, default=PACKAGE / 'data')
    args = parser.parse_args()
    result = compute(args.data)
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        need(result == read(PACKAGE / 'RESULT.json'), 'saved result differs')
        print(result['status'])


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, TypeError, IndexError, OSError) as exc:
        raise SystemExit('FAIL: ' + str(exc)) from None
