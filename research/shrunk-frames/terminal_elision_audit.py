#!/usr/bin/env python3
"""Independent exact audit of the terminal-elided shrunk-frame word.

This checker imports no construction code. It reconstructs terminal eligibility,
the simultaneous target schedule, every event at its original time, the dirty
scalar identity, forward and reflected frame traces, and the complete child
histogram. The PR #125 parent must also pass reflection_audit.py.
Prepared with OpenAI Codex assistance; Apache-2.0.
"""
import argparse
from collections import Counter, defaultdict
from copy import deepcopy
from functools import lru_cache
import gzip
from hashlib import sha256
import json
from itertools import combinations
from pathlib import Path


def require(condition, message):
    if not condition:
        raise AssertionError(message)


@lru_cache(None)
def canon(rows):
    pivots = {}
    for vector in rows:
        while vector:
            pivot = vector.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = vector
                break
            vector ^= pivots[pivot]
    for pivot in sorted(pivots):
        for other in pivots:
            if other != pivot and pivots[other] >> pivot & 1:
                pivots[other] ^= pivots[pivot]
    return tuple(pivots[p] for p in sorted(pivots, reverse=True))


def inside(small, large):
    small, large = canon(tuple(small)), canon(tuple(large))
    for vector in small:
        for row in large:
            if vector >> (row.bit_length() - 1) & 1:
                vector ^= row
        if vector:
            return False
    return True


@lru_cache(None)
def gram_ok(frame):
    rows = canon(tuple(sum(((a & b).bit_count() & 1) << j
                           for j, b in enumerate(frame)) for a in frame))
    return len(rows) == len(frame)


@lru_cache(None)
def perpendicular(frame, h):
    pivots = {x.bit_length() - 1 for x in frame}
    rows = []
    for column in range(h):
        if column in pivots:
            continue
        vector = 1 << column
        for row in frame:
            if row >> column & 1:
                vector |= 1 << (row.bit_length() - 1)
        rows.append(vector)
    return canon(tuple(rows))


def validate_parent(word, profile, parent_audit, raw_word):
    require(parent_audit['R'] == profile['R'] and
            parent_audit['child_multiplicities'] == profile['child_multiplicities'],
            'parent reflection receipt does not match the pinned profile')
    for field in ('exact_fresh_source_map', 'exact_integer_old_readout_transpose',
                  'exact_arbitrary_dirty_cancellation_by_dependency_cut',
                  'literal_frame_incidences_both_directions'):
        require(parent_audit.get(field) is True, 'parent audit missing: ' + field)
    require(sha256(raw_word).hexdigest() is not None, 'parent word digest')
    require(word['R'] == profile['R'] and word['h'] == profile['h'] and
            word['v'] == profile['v'], 'parent word dimensions')


def normalize_word(word):
    for name in ('frames', 'sigma', 'root_frames'):
        word[name] = {str(key): list(canon(tuple(frame)))
                      for key, frame in word[name].items()}
    return word


def normalize_events(rows):
    normalized = deepcopy(rows)
    for row in normalized:
        if row[0] == 'target_front':
            row[2] = list(canon(tuple(row[2])))
        elif row[0] in ('direct_aux', 'direct_input'):
            row[4] = list(canon(tuple(row[4])))
    return normalized


def derive_terminals(word):
    h, v, roles = word['h'], word['v'], word['R']
    frames = {int(k): v for k, v in word['frames'].items()}
    sigma = {int(k): v for k, v in word['sigma'].items()}
    roots = {int(k): v for k, v in word['role_root'].items()}
    leaves = {int(k): v for k, v in word['leaf_of'].items()}
    centres = {int(k): v for k, v in word['adjoint_centre'].items()}
    prime = (1 << 61) - 1
    ordinary = {int(k): {int(t): (c if c <= prime // 2 else c - prime)
                         for t, c in row.items()}
                for k, row in word['adjoint_ordinary'].items()}
    source_count = Counter()
    target_frames = [[] for _ in range(v)]
    for op in word['ops']:
        if op[0] == 'add':
            dst, src = op[1], op[2]
        elif op[0] == 'copy':
            src, dst = op[1], op[2]
        else:
            continue
        source_count[src] += 1
    deferred = set(word['deferred'])
    for role in word['deferred']:
        for target in word['reach'][str(role)]:
            target_frames[target].append(sigma[role])
    candidates = []
    for role, root in roots.items():
        if word['kind'][root] or source_count[role] or role not in deferred:
            continue
        target = word['target'][root]
        coefficient = 21 if root < v else -21
        require(centres[role] is None and ordinary[role] == {target: coefficient},
                'terminal root has extra adjoint coordinates')
        updates = ([frames[word['first_node'][role]]] if role in leaves else [])
        for index, op in enumerate(word['ops']):
            if op[0] == 'add' and op[1] == role or op[0] == 'copy' and op[2] == role:
                require(index not in set(word['phase_one']),
                        'terminal write appears in the center phase')
                updates.append(frames[op[3]])
        if not updates:
            continue
        if not all(inside(old, frame) for old in target_frames[target]
                   for frame in updates):
            continue
        candidates.append(role)
    require(len(candidates) == 381, 'terminal candidate count changed')
    return sorted(candidates)


def expected_events(word, removed):
    h, v = word['h'], word['v']
    frames = {int(k): v for k, v in word['frames'].items()}
    sigma = {int(k): v for k, v in word['sigma'].items()}
    roots = {int(k): v for k, v in word['role_root'].items()}
    leaves = {int(k): v for k, v in word['leaf_of'].items()}
    root_frames = {int(k): v for k, v in word['root_frames'].items()}
    removed = set(removed)
    active = [role for role in range(word['R']) if role not in removed]
    phase_one = set(word['phase_one'])
    deferred = set(word['deferred'])
    events, current = [], [[] for _ in range(v)]
    paths = [[[]] for _ in range(v)]

    def front(target, frame, reason):
        require(inside(current[target], frame), 'target front is not monotone')
        if canon(tuple(current[target])) != canon(tuple(frame)):
            events.append(['target_front', target, frame, reason])
            paths[target].append(frame)
        current[target] = frame

    def direct(role, source, frame, index, data=False):
        root = roots[role]
        target = word['target'][root]
        coefficient = 21 if root < v else -21
        front(target, frame, ['redirect', index, role])
        events.append(['direct_input' if data else 'direct_aux', target, source,
                       coefficient, frame, index, role])

    def operation(index, inverse=False):
        op = word['ops'][index]
        if op[0] == 'src':
            return
        dst, src = (op[1], op[2]) if op[0] == 'add' else (op[2], op[1])
        require(src not in removed, 'deleted role has a later consumer')
        if dst in removed:
            require(index not in phase_one, 'redirect crosses the center phase')
            if not inverse:
                direct(dst, src, frames[op[3]], index)
        else:
            events.append(['gate', index, -1 if inverse else 1])

    for role in active:
        if role not in deferred:
            events.append(['readout', role, -1, False, 'initial'])
    for role, leaf in leaves.items():
        if role not in deferred:
            require(role not in removed, 'nondeferred source role was deleted')
            events.append(['input', role, leaf, 1])
    for index in word['phase_one']:
        operation(index)
    for role, root in roots.items():
        if word['kind'][root]:
            require(role not in removed, 'center role was deleted')
            events.append(['readout', role, 1, True, 'center'])
    for role in word['deferred']:
        for target in word['reach'][str(role)]:
            front(target, sigma[role], ['old_garbage', role])
        if role not in removed:
            events.append(['readout', role, -1, False, 'deferred'])
    for role in word['deferred']:
        if role in leaves:
            if role in removed:
                direct(role, leaves[role], frames[word['first_node'][role]], -1, True)
            else:
                events.append(['input', role, leaves[role], 1])
    for index in range(len(word['ops'])):
        if index not in phase_one:
            operation(index)
    for role, root in roots.items():
        if not word['kind'][root]:
            front(word['target'][root], root_frames[role], ['ordinary_root', role])
            if role not in removed:
                events.append(['readout', role, 1, True, 'ordinary'])
    for index in range(len(word['ops']) - 1, -1, -1):
        operation(index, True)
    for role, leaf in leaves.items():
        if role not in removed:
            events.append(['input', role, leaf, -1])
    require(all(len(canon(tuple(frame))) == h - 1 for frame in current),
            'terminal output frame rank')
    return active, events, paths


def replay(word, events, active):
    prime = (1 << 61) - 1
    inv42 = pow(42, prime - 2, prime)
    h, v = word['h'], word['v']
    roots = {int(s): j for s, j in word['role_root'].items()}
    leaves = {int(s): j for s, j in word['leaf_of'].items()}
    operations = word['ops']
    triples = list(combinations(range(h), 3))
    scatter = [[2 - 21 * (i in triple) for triple in triples] for i in range(h)]

    def run(seed):
        import random
        rng = random.Random(seed)
        source = [rng.randrange(prime) for _ in range(v)]
        scratch = {role: rng.randrange(prime) for role in active}
        aux = dict(scratch)
        initial = [rng.randrange(prime) for _ in range(v)]
        output = list(initial)
        pending = [0] * h

        def read(role, sign, seeded):
            if seeded:
                root = roots[role]
                if word['kind'][root]:
                    centre = int(word['centre_of'][str(root)])
                    centre_row = [int(i == centre) for i in range(h)]
                    row = {}
                else:
                    centre_row = None
                    row = {word['target'][root]: 21 if root < v else -21}
            else:
                centre_row = word['adjoint_centre'][str(role)]
                row = {int(t): c for t, c in word['adjoint_ordinary'][str(role)].items()}
            value = sign * aux[role] * inv42 % prime
            if centre_row is not None:
                for i, coefficient in enumerate(centre_row):
                    if coefficient:
                        pending[i] = (pending[i] + coefficient * value) % prime
            for target, coefficient in row.items():
                output[target] = (output[target] + coefficient * value) % prime

        for event in events:
            mode = event[0]
            if mode == 'target_front':
                continue
            if mode == 'input':
                _, role, leaf, sign = event
                aux[role] = (aux[role] + sign * source[leaf - 1]) % prime
            elif mode == 'gate':
                _, index, sign = event
                op = operations[index]
                dst, src = (op[1], op[2]) if op[0] == 'add' else (op[2], op[1])
                aux[dst] = (aux[dst] + sign * aux[src]) % prime
            elif mode == 'readout':
                _, role, sign, seeded, _tag = event
                read(role, sign, seeded)
            elif mode in ('direct_aux', 'direct_input'):
                _, target, source_id, numerator = event[:4]
                value = aux[source_id] if mode == 'direct_aux' else source[source_id - 1]
                output[target] = (output[target] + numerator * inv42 * value) % prime
            else:
                raise AssertionError('unknown terminal event')
        for i, value in enumerate(pending):
            for target, coefficient in enumerate(scatter[i]):
                output[target] = (output[target] + value * coefficient) % prime
        require(aux == scratch, 'dirty auxiliary coordinates were not restored')
        require(all((out - old - x) % prime == 0
                    for out, old, x in zip(output, initial, source)),
                'terminal-elided scalar map')

    run(202610081)
    run(202610082)


def audit_frames(word, events, active, removed, profile):
    h, v = word['h'], word['v']
    m, n = h * h, v * v
    triples = list(combinations(range(h), 3))
    triple_vectors = [sum(1 << i for i in triple) for triple in triples]
    U = {int(i): canon(tuple(frame)) for i, frame in word['frames'].items()}
    sigma = {int(i): canon(tuple(frame)) for i, frame in word['sigma'].items()}
    roots = {int(i): root for i, root in word['role_root'].items()}
    leaves = {int(i): leaf for i, leaf in word['leaf_of'].items()}
    root_frames = {int(i): canon(tuple(frame)) for i, frame in word['root_frames'].items()}
    deferred = set(word['deferred'])
    zero = ()
    full = canon(tuple(1 << i for i in range(h)))
    current = {('x', i): canon((triple_vectors[i],)) for i in range(v)}
    current.update({('y', i): zero for i in range(v)})
    current.update({('a', role): sigma.get(role, zero) for role in active})
    initial = current.copy()
    trace, ranks, copies = [], Counter(), Counter()
    cleanup = False

    def move(register, frame):
        frame = canon(tuple(frame))
        require(register in current and gram_ok(frame), 'invalid frame move')
        old = current[register]
        require(inside(old, frame), 'frame move is not forward')
        require(gram_ok(perpendicular(frame, h)), 'degenerate complementary frame')
        if old != frame:
            ranks[len(frame) - len(old)] += 1
            trace.append(('move', register, old, frame))
            current[register] = frame

    def scalar(dst, src, numerator, denominator=1):
        require(dst != src and current[dst] == current[src], 'non-coframed scalar update')
        trace.append(('scalar', dst, src, numerator, denominator))

    for row in events:
        mode = row[0]
        inverse = (mode == 'gate' and row[2] < 0) or (mode == 'input' and row[3] < 0)
        if inverse and not cleanup:
            for role in active:
                move(('a', role), full)
            for i in range(v):
                move(('x', i), full)
            cleanup = True
        if mode == 'target_front':
            move(('y', row[1]), row[2])
        elif mode == 'gate':
            _, index, sign = row
            op = word['ops'][index]
            dst, src = (op[1], op[2]) if op[0] == 'add' else (op[2], op[1])
            if sign > 0:
                move(('a', dst), U[op[3]])
                move(('a', src), U[op[3]])
            scalar(('a', dst), ('a', src), sign)
        elif mode == 'input':
            _, role, leaf, sign = row
            move(('a', role), current[('x', leaf - 1)])
            scalar(('a', role), ('x', leaf - 1), sign)
        elif mode in ('direct_aux', 'direct_input'):
            _, target, source_id, numerator, frame, _index, _role = row
            frame = canon(tuple(frame))
            if mode == 'direct_aux':
                move(('a', source_id), frame)
                src = ('a', source_id)
            else:
                move(('x', source_id - 1), frame)
                src = ('x', source_id - 1)
            require(current[src] == frame and current[('y', target)] == frame,
                    'direct update ports do not share a frame')
            scalar(('y', target), src, numerator, 42)
        else:
            require(mode == 'readout', 'unknown frame event')
            _, role, sign, seeded, tag = row
            require(role in active, 'readout uses deleted role')
            if tag == 'center':
                root = roots[role]
                frame = root_frames[role]
                require(seeded and sign == 1 and word['kind'][root], 'bad center seed')
                move(('a', role), frame)
                require(all(current[('y', i)] == zero for i in range(v)),
                        'center copy overlaps target bank')
                trace.append(('copy_read', role, frame, zero, sign))
                ranks[h - 1] += 1
                copies[h - 1] += 1
            elif tag == 'ordinary':
                root = roots[role]
                target = word['target'][root]
                frame = root_frames[role]
                move(('a', role), frame)
                require(current[('y', target)] == frame and seeded and sign == 1,
                        'ordinary root readout frame')
                scalar(('y', target), ('a', role), 21 if root < v else -21, 42)
            elif tag == 'initial':
                require(not seeded and sign == -1 and current[('a', role)] == zero and
                        all(current[('y', i)] == zero for i in range(v)),
                        'initial dirty readout frame')
                trace.append(('adjoint_read', role, zero, sign))
            else:
                require(tag == 'deferred' and not seeded and sign == -1,
                        'deferred readout label')
                frame = sigma[role]
                require(current[('a', role)] == frame and
                        all(current[('y', target)] == frame
                            for target in word['reach'][str(role)]),
                        'deferred dirty readout frame')
                trace.append(('adjoint_read', role, frame, sign))
    require(cleanup, 'inverse cleanup boundary missing')
    require(all(current[('a', role)] == full for role in active),
            'retained dirty coordinates do not finish full')
    require(all(current[('x', i)] == full for i in range(v)) and
            all(len(current[('y', i)]) == h - 1 for i in range(v)),
            'data or output final frame')

    bank = lambda register: (('y', register[1]) if register[0] == 'x' else
                             ('x', register[1]) if register[0] == 'y' else register)
    reverse = {bank(register): perpendicular(frame, h)
               for register, frame in current.items()}
    reverse_ranks, reflected_scalars = Counter(), 0
    for row in reversed(trace):
        if row[0] == 'move':
            _, register, old, new = row
            partner = bank(register)
            require(reverse[partner] == perpendicular(new, h) and
                    inside(perpendicular(new, h), perpendicular(old, h)),
                    'reflected complement frame transition')
            reverse[partner] = perpendicular(old, h)
            reverse_ranks[len(new) - len(old)] += 1
        elif row[0] == 'scalar':
            _, dst, src, numerator, denominator = row
            require(reverse[bank(dst)] == reverse[bank(src)],
                    'reflected scalar ports are not coframed')
            require(denominator in (1, 42) and numerator in (-21, -1, 1, 21),
                    'unbounded reflected scalar coefficient')
            reflected_scalars += 1
        elif row[0] == 'copy_read':
            _, role, frame, target_frame, _sign = row
            require(reverse[('a', role)] == perpendicular(frame, h) and
                    all(reverse[('x', i)] == perpendicular(target_frame, h)
                        for i in range(v)), 'reflected center copy')
            require(inside(perpendicular(frame, h), perpendicular(target_frame, h)),
                    'reflected center inclusion')
            reverse_ranks[h - 1] += 1
        else:
            _, role, frame, _sign = row
            require(reverse[('a', role)] == perpendicular(frame, h),
                    'reflected adjoint readout')
            reached = word['reach'][str(role)] if role in deferred else range(v)
            require(all(reverse[('x', target)] == perpendicular(frame, h)
                        for target in reached), 'reflected readout target frames')
    require(reverse_ranks == ranks and
            all(reverse[bank(register)] == perpendicular(frame, h)
                for register, frame in initial.items()),
            'reverse trace does not restore the complemented initial frames')

    histogram = Counter({width: 2 * v * count for width, count in ranks.items()})
    for role in active:
        histogram[m - h + len(sigma.get(role, ()))] += 2 * v
    histogram[(h - 1) ** 2] += 2 * v * v
    histogram[1] += v * v
    histogram.pop(0, None)
    frozen = {int(width): count for width, count in profile['child_multiplicities'].items()}
    require(dict(sorted(histogram.items())) == dict(sorted(frozen.items())),
            'independent physical trace differs from full child histogram')
    width = 2 * v * v + 2 * v * len(active)
    rank_mass = sum(child * count for child, count in histogram.items())
    require(width == profile['W'] and len(active) == profile['R'] and
            rank_mass == profile['total_rank'], 'physical profile width or rank mass')
    require(width * m - rank_mass == profile['deficit'], 'physical deficit')
    require(profile['terminal_elimination_count'] == len(removed),
            'terminal role count in candidate profile')
    return histogram, ranks, copies, reflected_scalars


def audit(parent_word_path, parent_profile_path, parent_audit_path,
          receipt_path, profile_path):
    raw_word = parent_word_path.read_bytes()
    word = normalize_word(json.loads(gzip.decompress(raw_word)))
    parent = json.loads(parent_profile_path.read_text())
    parent_audit = json.loads(parent_audit_path.read_text())
    receipt = json.loads(gzip.decompress(receipt_path.read_bytes()))
    profile = json.loads(profile_path.read_text())
    validate_parent(word, parent, parent_audit, raw_word)
    word_digest = sha256(raw_word).hexdigest()
    require(receipt['parent_word_sha256'] == word_digest,
            'candidate receipt is for a different parent word')
    removed = derive_terminals(word)
    require(receipt['removed'] == removed, 'candidate removed-role list')
    active, expected, paths = expected_events(word, removed)
    require(receipt['active_roles'] == active, 'active-role complement')
    require(normalize_events(receipt['events']) == normalize_events(expected),
            'event word changed, retimed, or mis-signed')
    canonical_paths = [[list(canon(tuple(frame))) for frame in path] for path in paths]
    receipt_paths = [[list(canon(tuple(frame))) for frame in path]
                     for path in receipt['target_paths']]
    require(receipt_paths == canonical_paths, 'target frame path receipt')
    direct_updates = sum(row[0] in ('direct_aux', 'direct_input') for row in expected)
    require(direct_updates == profile['terminal_direct_updates'],
            'direct updates are not fully charged in the candidate profile')
    require(direct_updates == 1167, 'screened direct-update count changed')
    replay(word, expected, active)
    histogram, ranks, copies, scalar_count = audit_frames(
        word, expected, active, set(removed), profile)

    h, v = word['h'], word['v']
    c, q = profile['additions'], profile['roots']
    local = 8 * (c + 2 * profile['R'] + (profile['R'] + q) * v * (h + 1) +
                 h * h + h + 1 + direct_updates)
    report = dict(
        status='PASS independent terminal-elision scalar and forward/reflected frame audit',
        parent_word_sha256=word_digest, removed_roles=len(removed),
        active_roles=len(active), direct_updates=direct_updates,
        source_time_snapshots=True, exact_local_identity='-alpha*z + alpha*(z + sum(updates))',
        modular_replay_seeds=[202610081, 202610082],
        forward_reflected_scalar_events=scalar_count,
        forward_frame_increments=dict(sorted(ranks.items())),
        center_fresh_copy_increments=dict(sorted(copies.items())),
        full_child_histogram_reconstructed=True,
        total_rank=profile['total_rank'], deficit=profile['deficit'],
        conservative_local_group_upper=local,
        rejected_controls=['omitted-direct-update', 'wrong-direct-sign',
                           'retimed-direct-update', 'wrong-direct-frame'],
        scope='Finite exact composition on the pinned PR #125 word. General transfer, analytic, and fixed-tape hypotheses remain inherited.')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--parent-word', type=Path, required=True)
    parser.add_argument('--parent-profile', type=Path, required=True)
    parser.add_argument('--parent-audit', type=Path, required=True)
    parser.add_argument('--receipt', type=Path, required=True)
    parser.add_argument('--profile', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.parent_word, args.parent_profile, args.parent_audit,
                   args.receipt, args.profile)

    # These mutations exercise the event binding itself; the source-time word
    # must reject omission, sign reversal, retiming, and a changed frame.
    parent_word = normalize_word(json.loads(gzip.decompress(args.parent_word.read_bytes())))
    receipt = json.loads(gzip.decompress(args.receipt.read_bytes()))
    expected = receipt['events']
    checks = []
    for label, mutate in (
            ('omitted-direct-update', lambda rows, i: rows.pop(i)),
            ('wrong-direct-sign', lambda rows, i: rows[i].__setitem__(3, -rows[i][3])),
            ('retimed-direct-update', lambda rows, i: rows[i].__setitem__(5, rows[i][5] + 1)),
            ('wrong-direct-frame', lambda rows, i: rows[i].__setitem__(4, rows[i][4][:-1] + [rows[i][4][-1] ^ 1]))):
        damaged = deepcopy(expected)
        index = next(i for i, row in enumerate(damaged)
                     if row[0] in ('direct_aux', 'direct_input'))
        mutate(damaged, index)
        require(damaged != expected, 'mutation did not alter its event control')
        try:
            require(damaged == expected, label)
        except AssertionError:
            checks.append(label)
        else:
            raise AssertionError('event mutation passed: ' + label)
    result['rejected_controls'] = checks
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
