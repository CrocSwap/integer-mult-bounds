#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent exact local audit of PR3133; no predecessor code is imported.

Arham Tahir, with substantial OpenAI Codex assistance. Source data and the
mechanism belong to dcharb78 and the credited predecessor chain (NOTICE).
"""
from collections import Counter
import copy
from fractions import Fraction as Q
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(str(message))


def load(name):
    raw = (HERE / 'inputs' / name).read_bytes()
    return json.loads(gzip.decompress(raw) if raw[:2] == b'\x1f\x8b' else raw)


def authenticate():
    sources = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    for row in sources['snapshot']:
        raw = (HERE / 'inputs' / row['local']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row['sha256'], ('source drift', row['local']))


@lru_cache(None)
def space(vectors):
    """Enumerate a binary span, independently of canonical-basis routines."""
    elements = {0}
    for vector in vectors:
        need(type(vector) is int and 0 <= vector < 512, 'binary vector range')
        elements |= {x ^ vector for x in tuple(elements)}
    return frozenset(elements)


def dim(subspace):
    size = len(subspace)
    need(size > 0 and size & (size - 1) == 0, 'subspace cardinality')
    return size.bit_length() - 1


FULL = space(tuple(1 << i for i in range(9)))


@lru_cache(None)
def warp_geometry(columns, from_vectors, to_vectors):
    """Check the binary symplectic frame action by finite point sets.

    For a subspace U the frame is L_U={(x,x+p): x in U, p in U^perp}.
    K_G(x,z)=(Gx, Gx+G^(-T)(x+z)); this is a binary-frame check, not
    a native Gaussian/Clifford phase or execution-cost certification.
    """
    need(len(columns) == 9, 'warp column count')
    images = []
    for x in range(512):
        image = 0
        for bit in range(9):
            if x & (1 << bit):
                image ^= columns[bit]
        need(0 <= image < 512, 'warp image range')
        images.append(image)
    need(len(set(images)) == 512, 'singular warp')
    inverse = {image: x for x, image in enumerate(images)}

    def inverse_transpose(z):
        return sum(((inverse[1 << bit] & z).bit_count() % 2) << bit for bit in range(9))

    def lifted(vector):
        x, z = vector & 511, vector >> 9
        gx = images[x]
        return gx | ((gx ^ inverse_transpose(x ^ z)) << 9)

    def frame(U):
        orthogonal = [p for p in range(512) if all((p & x).bit_count() % 2 == 0 for x in U)]
        return {x | ((x ^ p) << 9) for x in U for p in orthogonal}

    def pairing(a, b):
        return (((a & 511) & (b >> 9)).bit_count() + ((a >> 9) & (b & 511)).bit_count()) % 2

    U, V = space(from_vectors), space(to_vectors)
    need(dim(U) == len(from_vectors) == len(to_vectors) == dim(V), 'warp frame bases')
    need({images[x] for x in U} == set(V), 'warp does not map source frame')
    generators = [1 << bit for bit in range(18)]
    need(all(pairing(lifted(a), lifted(b)) == pairing(a, b)
             for i, a in enumerate(generators) for b in generators[i:]), 'non-symplectic warp')
    for old, new in ((space(()), space(())), (FULL, FULL), (U, V)):
        need({lifted(x) for x in frame(old)} == frame(new), 'lifted frame action')
    return tuple(images), inverse


def targets(word):
    v = word['report']['v']
    return range(v, 2 * v)


def regs(gate):
    return gate[1:3] if gate[0] == 'add' else gate[1:2]


def stream(word, ordinary=False):
    """Generate chronology, binding each B warp to its original ordinal ID."""
    yield from word['A'][word['prelude_events'] if ordinary else 0:]
    if not ordinary:
        yield from word['cut']
    at = {}
    for operator, record in enumerate(word['warps'], 1):
        need(0 <= record[0] <= len(word['B']), 'warp position')
        at.setdefault(record[0], []).append((operator, record))
    for position in range(len(word['B']) + 1):
        for operator, record in at.get(position, []):
            yield ['warp', record[1], operator, record[3], record[4]]
        if position < len(word['B']):
            yield word['B'][position]
    yield from word['restore']


def cleanup(word):
    """Inverse of non-target actions, using a zero buffer for each low end."""
    n = 2 * word['report']['v'] + word['report']['R']
    restored = set(map(int, word['helper_final']))
    remap = lambda r: r + n if r in restored else r
    out = []
    for gate in reversed(list(stream(word, ordinary=True))):
        if gate[0] != 'warp' and gate[1] in targets(word):
            continue
        if gate[0] == 'warp':
            out.append(['warp', remap(gate[1]), -gate[2], sorted(FULL - {0})])
        elif gate[0] == 'add':
            out.append(['add', remap(gate[1]), remap(gate[2]), -gate[3], gate[4], sorted(FULL - {0})])
        elif gate[0] == 'scale':
            out.append(['scale', remap(gate[1]), gate[3], gate[2], sorted(FULL - {0})])
        else:
            raise ValueError('unknown cleanup primitive')
    return out


def normalized_cleanup(gates):
    return [(g[:-1], space(tuple(g[-1]))) for g in gates]


def edit(parent, spec, names):
    """Splice source intervals once, recording an explicit old-to-new cut map."""
    word = copy.deepcopy(parent)
    hunks = {section: {} for section in ('A', 'B', 'restore')}
    for change in spec:
        if change['id'] not in names:
            continue
        for h in change.get('edits', [change]):
            section, start, stop = h['section'], h['start'], h['stop']
            need(parent[section][start:stop] == h['old'], ('wrong edit preimage', change['id']))
            need(start not in hunks[section] and start < stop, 'edit interval')
            hunks[section][start] = h
        for r, frames in change.get('helper_final', {}).items():
            need(parent['helper_final'][r] == frames['old'], 'terminal preimage')
            small, big = space(tuple(frames['new'])), space(tuple(frames['old']))
            need(small < big and 2 * len(small) == len(big), 'terminal hyperplane')
            word['helper_final'][r] = frames['new']
    maps = {}
    for section, changes in hunks.items():
        out, position, cuts = [], 0, {}
        while position <= len(parent[section]):
            cuts[position] = len(out)
            if position == len(parent[section]):
                break
            if position in changes:
                h = changes[position]
                need(not any(position < other < h['stop'] for other in changes), 'overlap')
                out.extend(copy.deepcopy(h['new']))
                position = h['stop']
            else:
                out.append(copy.deepcopy(parent[section][position]))
                position += 1
        word[section], maps[section] = out, cuts
    for record in word['warps']:
        need(record[0] in maps['B'], 'warp inside an edited interval')
        record[0] = maps['B'][record[0]]
    word['cleanup'] = cleanup(word)
    return word


def frame_bill(word):
    v, n = word['report']['v'], 2 * word['report']['v'] + word['report']['R']
    need((v, n, word['report']['h']) == (112, 704, 9), 'source geometry')
    live = set(range(n)) - set(word['removed'])
    for record in word['warps']:
        need(record[1] in live and record[1] not in targets(word), 'warp lender')
        warp_geometry(tuple(record[2]), tuple(record[3]), tuple(record[4]))
    start = [space((p,)) for p in word['ports']] + [space(())] * (n - v)
    end = [FULL] * n
    for i, port in enumerate(word['ports']):
        end[v + i] = frozenset(x for x in range(512) if (x & port).bit_count() % 2 == 0)
    for r, U in word['start_extra'].items():
        start[int(r)] = space(tuple(U))
    for r, U in word['helper_final'].items():
        end[int(r)] = space(tuple(U))
    current, bill, per_register = start.copy(), Counter(), {}

    def climb(r, destination):
        need(r in live, ('removed register', r))
        need(current[r] <= destination, ('nonmonotone frame', r, dim(current[r]), dim(destination)))
        difference = dim(destination) - dim(current[r])
        if difference:
            bill[difference] += 1
            per_register.setdefault(r, Counter())[difference] += 1
        current[r] = destination

    def perform(gate):
        if gate[0] == 'warp':
            r, old, new = gate[1], space(tuple(gate[3])), space(tuple(gate[4]))
            need(1 <= abs(gate[2]) <= len(word['warps']), 'warp operator ID')
            record = word['warps'][abs(gate[2]) - 1]
            need(r == record[1], 'warp operator lender mismatch')
            images, inverse = warp_geometry(tuple(record[2]), tuple(record[3]), tuple(record[4]))
            image = inverse if gate[2] < 0 else images
            need({image[x] for x in old} == set(new), 'prelude/chronological warp frame action')
            need(current[r] == old, ('warp entry frame', r, gate[2]))
            current[r] = new
        else:
            for r in regs(gate):
                climb(r, space(tuple(gate[-1])))

    for gate in word['A']:
        perform(gate)
    levels = {v + int(t): space(tuple(U)) for t, U in word['target_levels'].items()}
    need(all(current[r] == levels.get(r, space(())) for r in targets(word)), 'target cut frames')
    centre_bill = Counter()
    for r, U in zip(word['centers'], word['center_frames']):
        U = space(tuple(U))
        need(current[r] == U, 'centre entry')
        served = {levels.get(g[1], space(())) for g in word['cut'] if g[2] == r}
        for destination in sorted(served, key=len, reverse=True):
            need(destination <= U, 'centre nesting')
            if U != destination:
                centre_bill[dim(U) - dim(destination)] += 1
            U = destination
    # The stream's A and cut were handled separately above.
    for gate in list(stream(word))[len(word['A']) + len(word['cut']):]:
        perform(gate)
    for r in sorted(live):
        climb(r, end[r])
    bill.update(centre_bill)
    inventory = Counter(dim(end[r]) - dim(start[r]) for r in live if r >= 2 * v)
    need(normalized_cleanup(word['cleanup']) == normalized_cleanup(cleanup(word)), 'cleanup not inverse-reverse')
    return bill, inventory, per_register


def multiply(row, operators):
    """Left multiplication in a free group; no physical-warp identities assumed."""
    out = {}
    for (variable, tail), coefficient in row.items():
        reduced = []
        for operator in (*operators, *tail):
            if reduced and reduced[-1] == -operator:
                reduced.pop()
            else:
                reduced.append(operator)
        out[variable, tuple(reduced)] = coefficient
    return out


def add_into(destination, source, coefficient):
    for key, value in source.items():
        new = destination.get(key, 0) + coefficient * value
        if new:
            destination[key] = new
        else:
            destination.pop(key, None)


def endpoint(word, dual=False):
    """Compute every live input column simultaneously with rational row maps."""
    n, v = 704, 112
    live = set(range(n)) - set(word['removed'])
    restored = set(map(int, word['helper_final']))
    rows = {r: {(r, ()): Q(1)} for r in live}
    rows.update({r + n: {} for r in restored})
    # Separate free symbols for K and K^(-T), including prelude/corrections.
    dual_operator = lambda op: (1 if op > 0 else -1) * (abs(op) + 1000000)

    def gate(g):
        if g[0] == 'warp':
            op = dual_operator(g[2]) if dual else g[2]
            rows[g[1]] = multiply(rows[g[1]], (op,))
        elif g[0] == 'scale':
            scalar = Q(g[2], g[3])
            need(scalar != 0, 'zero scale')
            if dual:
                scalar = 1 / scalar
            rows[g[1]] = {key: scalar * value for key, value in rows[g[1]].items()}
        elif g[0] == 'add':
            t, s, scalar = g[1], g[2], Q(g[3], g[4])
            need(t != s, 'self add')
            if dual:
                t, s, scalar = s, t, -scalar
            add_into(rows[t], rows[s], scalar)
        else:
            raise ValueError('unknown semantic primitive')

    for correction in word['initial_corrections']:
        t, s = correction['target'], correction['source']
        scalar = Q(correction['coefficient'])
        operators = tuple(correction['operator_word'])
        if dual:
            t, s, scalar = s, t, -scalar
            operators = tuple(-dual_operator(op) for op in reversed(operators))
        add_into(rows[t], multiply(rows[s], operators), scalar)
    for g in (*word['precondition'], *word['compensation'], *stream(word)):
        gate(g)
    if not dual:
        for r in targets(word):
            need(rows[r] == {(r, ()): Q(1), (r - v, ()): Q(1)}, ('target before cleanup', r))
        for r in restored:
            need(rows[r] == {(r, ()): Q(1)}, ('dirty helper not restored before cleanup', r))
        need(all(not any(variable in restored and variable != r for variable, _ in row)
                 for r, row in rows.items()), 'restored dirty input leaks before cleanup')
    for g in word['cleanup']:
        gate(g)
    for r in live:
        expected = {(r, ()): Q(1)}
        if (dual and r < v) or (not dual and v <= r < 2 * v):
            expected[r + v if dual else r - v, ()] = Q(-1 if dual else 1)
        need(rows[r] == expected, ('endpoint', 'dual' if dual else 'forward', r))
    need(all(not rows[r + n] for r in restored), 'private buffer not zero at return')
    return {'independent_inputs': len(live), 'restored_helpers': len(restored), 'zero_buffers': len(restored)}


def signed_delta(a, b):
    return {str(k): a[k] - b[k] for k in sorted(a.keys() | b.keys()) if a[k] != b[k]}


def run():
    authenticate()
    spec = load('EDITS.json')
    reports = {}
    for variant in ('base', 'extra'):
        parent = load('PARENT-' + variant + '.json.gz')
        shipped = load('FINAL-' + variant + '.json.gz')
        changes = spec['edits'][variant]
        controls = {'R1_E42', 'R2_E7'}
        bills = {}
        register_bills = {}
        for name, added in (('restore_control', set()), ('586', {'B_586_438'}),
                            ('588', {'B_588_440'}), ('both', {'B_586_438', 'B_588_440'})):
            word = edit(parent, changes, controls | added)
            if name == 'both':
                need(set(word) == set(shipped), 'shipped section set differs')
                need(all(word[k] == shipped[k] for k in word if k not in ('cleanup', 'report')), 'shipped word differs from independent splices')
                need(normalized_cleanup(word['cleanup']) == normalized_cleanup(shipped['cleanup']), 'shipped cleanup differs')
            bill, inventory, per_register = frame_bill(word)
            bills[name] = bill
            register_bills[name] = per_register
            semantics = {orientation: endpoint(word, dual=orientation == 'dual') for orientation in ('forward', 'dual')}
            reports[variant + '/' + name] = {'profile': dict(sorted(bill.items())),
                'inventory': dict(sorted(inventory.items())), 'semantics': semantics,
                'binary_warps': len(word['warps']),
                'local_rank_mass': sum(r * count for r, count in bill.items()),
                'helper_width_mass': sum(r * count for r, count in inventory.items()),
                'delta_from_restore_control': signed_delta(bill, bills['restore_control']),
                'changed_register_bills': {str(r): signed_delta(per_register.get(r, Counter()), register_bills['restore_control'].get(r, Counter()))
                    for r in sorted(per_register.keys() | register_bills['restore_control'].keys())
                    if per_register.get(r, Counter()) != register_bills['restore_control'].get(r, Counter())}}
            if name == 'both':
                need({str(k): value for k, value in bill.items()} == spec['declared']['local_profile'] == shipped['report']['local_profile'], 'declared local profile')
                need({str(k): value for k, value in inventory.items()} == spec['declared']['width_inventory'] == shipped['report']['width_inventory'], 'declared inventory')
            print('CHECKED', variant, name, 'forward+dual', flush=True)
        need(signed_delta(bills['586'], bills['restore_control']) == {'2': 6, '3': -2, '4': -3, '5': 1}, '586 delta')
        need(signed_delta(bills['588'], bills['restore_control']) == {'2': 6, '3': -2, '4': -3, '5': 1}, '588 delta')
        need(all(bills['both'][r] - bills['restore_control'][r] ==
                 bills['586'][r] + bills['588'][r] - 2 * bills['restore_control'][r]
                 for r in bills['both'].keys() | bills['restore_control'].keys()), 'additive group deltas')
    result = {'status': 'PASS_INDEPENDENT_COUPLED_CARRIER_LOCAL_AUDIT', 'scenarios': reports,
              'scope': 'Exact local dirty-input maps and chronological local frame bills; no native, owner, cap or outer admission.'}
    encoded = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if '--write' in sys.argv:
        (HERE / 'RESULT.json').write_text(encoded, encoding='utf-8', newline='\n')
    else:
        need((HERE / 'RESULT.json').read_text(encoding='utf-8') == encoded, 'result receipt differs')
    print(result['status'])


if __name__ == '__main__':
    run()
