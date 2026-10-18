"""Source-bound line normalization of PR2681's zero-retention QQ16 word.

The retained Arham Tahir checker supplies source reconstruction, routed algebra
and the already-published logical inverse. New physical frames, word lowering,
native checks and comparison: ywz65 with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
F16 = tuple((1 << i, 1) for i in range(9, 25))
RETAINED = {'verify.py', 'WORD.json', 'RESULT.json', 'SOURCES.json', 'README.md',
            'PROOF.md', 'references/PR2540-PROOF.md', 'references/PR2540-README.md'}


def need(ok, why):
    if not ok:
        raise ValueError(why)


def read_json(path):
    def unique(pairs):
        out = {}
        for key, value in pairs:
            need(key not in out, 'duplicate JSON key')
            out[key] = value
        return out
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def load_source():
    retained = read_json(HERE / 'PREDECESSORS.json')['files']
    need({r['local'] for r in retained} == {'vendor/pr2681/' + n for n in RETAINED}
         and len(retained) == len(RETAINED), 'complete retained source set')
    raw = {}
    pins = {}
    for record in retained:
        data = (HERE / record['local']).read_bytes()
        need(digest(data) == record['sha256'], 'retained source SHA256')
        need(hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
             == record['git_blob'], 'retained source Git blob')
        raw[record['local']] = data
        pins[record['local']] = digest(data)
    source_pins = read_json(HERE / 'SOURCES.json')['files']
    expected = {x['path'] for x in json.loads(raw['vendor/pr2681/SOURCES.json'])['files']
                if x['usage'] == 'input'}
    actual = [x['path'] for x in source_pins if x['usage'] == 'input']
    need(set(actual) == expected and len(actual) == len(expected), 'complete main input set')
    for record in source_pins:
        if record['usage'] != 'input':
            continue
        data = (ROOT / record['path']).read_bytes()
        need(digest(data) == record['sha256'], 'main source SHA256')
        need(hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
             == record['git_blob'], 'main source Git blob')
        pins[record['path']] = digest(data)
    path = HERE / 'vendor/pr2681/verify.py'
    P = types.ModuleType('authenticated_pr2681')
    P.__file__ = str(path)
    exec(compile(raw['vendor/pr2681/verify.py'], str(path), 'exec'), P.__dict__)
    P.ROOT = ROOT
    R, routes, labels = P.load(P.authenticate())
    return P, R, routes, labels, pins


def bridge(P, g, q):
    """Affine translation aligning g(F17) to F16*C_q, including phase."""
    target = P.phase(F16 + ((q, 1),))
    moved = P.phase(P.move(P.F17, g, 0))
    need(target[1] == moved[1], 'quadratic bridge discrepancy')
    difference = [(x - y) % 4 for x, y in zip(target[0], moved[0])]
    need(all(x in (0, 2) for x in difference), 'odd bridge discrepancy')
    return sum((x // 2) << j for j, x in enumerate(difference))


def lower(P, R):
    original = P.word(R)
    need(canonical(original) == canonical(read_json(HERE / 'vendor/pr2681/WORD.json')),
         'complete source word regeneration')
    result = []
    future = False
    for event in original:
        e = list(event)
        if e[0] == 'stage':
            continue
        if e[:2] == ['begin', 'future_logger_inverse']:
            future = True
        if e[0] == 'clear' and e[2] == 'wide' and future:
            e[2] = 'query2'
        if e[0] == 'map' and e[2] == 2:
            if e[4]:
                result.extend([['line', e[1], e[3], 1], e])
            else:
                result.extend([e, ['line', e[1], e[3], -1]])
        else:
            result.append(e)
        if e[:2] == ['end', 'future_logger_inverse']:
            future = False
    need(not future, 'closed transformed future sweep')
    return result


def replay(P, w, routes, labels, x2, y2, expected, middle=None):
    owned = {s + str(p) for s in ('Z', 'W') for p in range(112)}
    rows = {name: {(name, P.AXES): Q(1)} for name in owned}; frames = {name: () for name in owned}
    for side, bank in (('X', x2), ('Y', y2)):
        for p in range(112):
            name = side + str(p); rows[name] = bank[p]
            frames[name] = P.F17 + (((labels[p], -1),) if side == 'Y' else ())
    borrowed = {n: dict(r) for n, r in rows.items() if n[0] in ('X', 'Y')}
    borrowed_frames = {n: frames[n] for n in borrowed}
    active = set(); counts = Counter()
    for index, e in enumerate(w):
        op = e[0]; counts[op] += 1
        if op == 'begin':
            P.need(not active, 'overlapping private sweeps')
            active = {'F' + str(k) for k in range(8)}
            if e[2] == 16: active |= {'G' + str(k) for k in range(8)}
            P.need(e[2] == len(active), 'private scratch count')
            for name in active: rows[name], frames[name] = {(name, P.AXES): Q(1)}, ()
        elif op == 'end':
            P.need(len(active) == e[2], 'private boundary')
            P.need(all(not rows[n] and P.phase(frames[n]) == P.phase(()) for n in active), 'scratch leak')
            for name in active: del rows[name], frames[name]
            active = set()
        elif op == 'clear':
            _, name, f = e; P.need(name in owned | active, 'clear borrowed input'); rows[name] = {}
            frames[name] = {'wide': P.F17, 'current': P.F17, 'identity': (), 'query2': F16}.get(f)
            if f.startswith('hole'): frames[name] = P.F17 + ((labels[int(f[4:])], -1),)
            P.need(frames[name] is not None, 'unknown clear frame')
        elif op == 'add':
            _, dst, src, q = e
            P.need(dst in owned | active and dst != src, 'ADD ownership/alias')
            P.need(dst in rows and src in rows, 'nonlive ADD role')
            P.need(P.phase(frames[dst]) == P.phase(frames[src]), 'ADD frame mismatch ' + str(index))
            q = Q(q); P.need(abs(q) in (1, Q(1, 4)), 'unpriced coefficient')
            rows[dst] = P.add(rows[dst], rows[src], q)
            counts['unit_ADD' if abs(q) == 1 else 'quarter_ADD'] += 1
        elif op == 'line':
            _, name, p, sign = e
            P.need(not active and name in owned and sign in (-1, 1), 'line boundary')
            frames[name] += ((labels[p], sign),)
        elif op == 'stage':
            _, name, sign = e
            P.need(not active and name in owned and sign in (-1, 1), 'stage boundary')
            frames[name] += tuple((v, sign) for v in P.BLOCK)
        elif op == 'map':
            _, name, stage, p, inverse = e[:5]
            P.need(not active and name in owned and stage in (1, 2), 'map inside private sweep')
            g = routes[stage][p]; b = P.alignment(g, P.F17) if stage == 1 else bridge(P, g, labels[p])
            if inverse: b = P.act(g, b)
            if len(e) > 5 and e[5] == 'omit_shift': b = 0
            if len(e) > 5 and e[5] == 'wide_shift': b = P.alignment(g, P.F25)
            if len(e) > 5 and e[5] == 'wrong_inverse_shift': b = bridge(P, g, labels[p])
            frames[name] = P.move(frames[name], g, b); rows[name] = P.routed(g, rows[name])
        elif op == 'checkpoint':
            P.need(not active, 'incomplete sweep at checkpoint')
            if middle is not None:
                P.need([rows['Z' + str(p)] for p in range(112)] == middle[0]
                     and [rows['W' + str(p)] for p in range(112)] == middle[1], 'inverse B1 checkpoint')
        else: raise ValueError('unknown event')
    P.need(not active, 'unterminated private sweep')
    for side, bank in zip(('Z', 'W'), expected):
        for p in range(112):
            name = side + str(p)
            P.need(rows[name] == bank[p], 'wrong output ' + name)
            P.need(P.phase(frames[name]) == P.phase(P.F17), 'wrong final frame')
    P.need(all(rows[n] == r and frames[n] == borrowed_frames[n] for n, r in borrowed.items()), 'borrowed restoration')
    return counts



def phase_checks(P, routes, labels):
    characters = [0] + list(P.AXES) + [P.AXES[i] ^ P.AXES[j]
                  for i in range(73) for j in range(i + 1, 73)]
    def character(frame, value):
        return sum(c * ((v & value).bit_count() % 2) for v, c in frame) % 4
    records = []
    comparisons = 0
    for stage in (1, 2):
        for port, g in enumerate(routes[stage]):
            target = P.F17 if stage == 1 else F16 + ((labels[port], 1),)
            shift = P.alignment(g, P.F17) if stage == 1 else bridge(P, g, labels[port])
            inverse_shift = P.act(g, shift)
            entry = P.move(P.F17, g, shift)
            exit_frame = P.move(target, g, inverse_shift)
            need(P.phase(entry) == P.phase(target), 'entry frame identity')
            need(P.phase(exit_frame) == P.phase(P.F17), 'inverse frame identity')
            for value in characters:
                need(character(entry, value) == character(target, value), 'independent entry character')
                need(character(exit_frame, value) == character(P.F17, value), 'independent exit character')
                comparisons += 2
            records.append([stage, port, shift, inverse_shift])
    return {'records': records, 'degree_two_basis_characters': len(characters),
            'literal_character_equalities': comparisons}


def kernel_checks(P, labels, word, wrong_negative_offset=False):
    recipes = []
    columns = 0
    for port, q in enumerate(labels):
        pivot = (q & -q).bit_length() - 1
        basis = (q,) + tuple(1 << i for i in range(9) if i != pivot)
        inverse = {P.act(basis, x): x for x in range(512)}
        need(len(inverse) == 512, 'line basis bijective')
        for sign in (1, -1):
            offset = q if sign == -1 else 0
            if wrong_negative_offset and sign == -1:
                offset = 0
            for x in range(512):
                middle = inverse[x]
                actual = {P.act(basis, middle) ^ offset: (1, 1),
                          P.act(basis, middle ^ 1) ^ offset: (1, -1)}
                expected = {x: (1, sign), x ^ q: (1, -sign)}
                need(actual == expected, 'signed line native kernel/global phase')
                columns += 1
            occurrences = [i for i, e in enumerate(word)
                           if e[0] == 'line' and e[2:] == [port, sign]]
            need(len(occurrences) == (2 if sign == 1 else 1), 'all line occurrences')
            recipes.append({'port': port, 'q': q, 'sign': sign, 'rank': 1,
                            'left_columns': list(basis), 'left_offset': offset,
                            'right_columns': [inverse[1 << j] for j in range(9)],
                            'events': occurrences})
    need(sum(len(r['events']) for r in recipes) == 336, 'complete native child coverage')
    return {'signed_rank_one_recipes': recipes, 'basis_columns': columns,
            'positive_children': 336, 'monomial_wrappers': 672,
            'spectator_action': 'identity outside first nine address coordinates'}


def compute():
    P, R, routes, labels, pins = load_source()
    word = lower(P, R)
    original = [[{(s + str(p), P.AXES): Q(1)} for p in range(112)] for s in ('x', 'y')]
    x2, y2, x1, y1 = P.forward(R, routes, *original)
    counts = replay(P, word, routes, labels, x2, y2, original, (x1, y1))
    current = [[{(s + str(p), P.AXES): Q(1)} for p in range(112)] for s in ('X', 'Y')]
    inverse = P.inverse_formula(R, routes, *current)
    replay(P, word, routes, labels, *current, inverse)
    need(P.forward(R, routes, *inverse)[:2] == tuple(current), 'other full inverse order')
    frames = phase_checks(P, routes, labels)
    native = kernel_checks(P, labels, word)
    controls = {}
    def reject(name, change):
        altered = deepcopy(word)
        change(altered)
        try:
            replay(P, altered, routes, labels, *current, inverse)
        except (ValueError, KeyError) as error:
            controls[name] = str(error)
        else:
            raise ValueError('ineffective semantic control: ' + name)
    first_negative = next(i for i, e in enumerate(word) if e[0] == 'line' and e[3] == -1)
    first_future_exit = next(i for i, e in enumerate(word) if e[0] == 'map' and e[2] == 2 and e[4])
    reject('missing common-frame normalization', lambda w: w.pop(first_negative))
    reject('wrong common-frame normalization sign', lambda w: w[first_negative].__setitem__(3, 1))
    reject('wrong normal', lambda w: w[first_negative].__setitem__(2, (w[first_negative][2] + 1) % 112))
    reject('missing restoration line', lambda w: w.pop(first_future_exit - 1))
    reject('old wide-frame shift', lambda w: next(e for e in w if e[0] == 'map' and e[2] == 2).append('wide_shift'))
    nonfixed = next(p for s, p, b, inv in frames['records'] if s == 2 and b != inv)
    reject('wrong inverse translation', lambda w: next(e for e in w if e[:4] == ['map', 'W' + str(nonfixed), 2, nonfixed] and e[4]).append('wrong_inverse_shift'))
    reject('borrowed clear', lambda w: w[0].__setitem__(1, 'X0'))
    reject('missing output dirt clear', lambda w: w.pop(0))
    reject('private scratch leakage', lambda w: w.remove(['clear', 'F0', 'identity']))
    reject('wrong logical inverse sign', lambda w: next(e for e in w if e[:3] == ['add', 'F0', 'G0']).__setitem__(3, '1'))
    try:
        kernel_checks(P, labels, word, True)
    except ValueError as error:
        controls['negative child missing XOR wrapper'] = str(error)
    else:
        raise ValueError('ineffective native negative control')
    invoice = {'rank_one_children': counts['line'], 'rank_eight_children': counts['stage'],
               'native_rank_mass': counts['line'], 'native_monomial_wrappers': 2 * counts['line'],
               'full_cover_maps': counts['map'], 'unit_ADDs': counts['unit_ADD'],
               'quarter_ADDs': counts['quarter_ADD'], 'CLEARs': counts['clear'],
               'real_scalar_primitive_allowance': 8 * counts['unit_ADD'] + 12 * counts['quarter_ADD'] + 2 * counts['clear'],
               'owned_full_cover_outputs': 224, 'early_record_banks': 0,
               'peak_local_owned_scratch': 16, 'untouched_borrowed_current_fields': 224}
    need((invoice['rank_one_children'], invoice['rank_eight_children'], invoice['full_cover_maps'],
          invoice['real_scalar_primitive_allowance']) == (336, 0, 464, 25840), 'full paid local invoice')
    operators = [[[[s, list(g), str(c)] for (s, g), c in sorted(row.items())] for row in bank] for bank in inverse]
    source_result = read_json(HERE / 'vendor/pr2681/RESULT.json')
    need(digest(canonical(operators)) == source_result['output_operator_sha256'], 'same full output operator')
    need(8 ** 15 > 7 ** 16, 'exact child moment range witness')
    result = {'status': 'PASS_QQ16_LINE_NORMALIZED_DECODER', 'events': len(word),
              'trace': dict(counts), 'invoice': invoice, 'frame_maps': frames,
              'native': native, 'controls': controls, 'source_sha256': pins,
              'two_sided_224_array_inverse': True, 'output_operator_sha256': digest(canonical(operators)),
              'operator_terms': sum(len(row) for bank in inverse for row in bank),
              'comparison': {'source_2681_children_removed': {'8': 448}, 'source_2681_children_added': {'1': 224},
                             'versus_2540_child_delta': {'1': 112, '8': -16},
                             'strict_child_moment_improvement_domain': '0 <= a <= 1/16',
                             'integer_witness': {'8^15': 8 ** 15, '7^16': 7 ** 16},
                             'versus_2540_wrappers_added': 192, 'versus_2540_maps_added': 256,
                             'versus_2540_scalar_allowance_added': 8368},
              'limits': 'Ideal finite local word; actual map/wrapper hosting, movement, rounded precision, inherited F0/B1 and consumer/supplier admission remain open. No kappa or optimality claim.'}
    return result, word


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    if args.write:
        need(not (HERE / 'RESULT.json').exists() and not (HERE / 'WORD.json').exists(), 'output already exists')
    result, word = compute()
    for name, value in [('RESULT.json', result), ('WORD.json', word)]:
        path = HERE / name
        if args.write:
            with path.open('x', encoding='utf-8', newline='\n') as stream:
                stream.write(json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n')
        else:
            need(canonical(read_json(path)) == canonical(value), 'typed complete receipt mismatch ' + name)
    print(result['status'], 'events=3823 children=336H1 maps=464 controls=' + str(len(result['controls'])))


if __name__ == '__main__':
    main()
