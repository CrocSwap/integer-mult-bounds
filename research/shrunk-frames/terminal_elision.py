#!/usr/bin/env python3
"""Compose shrunk deferred frames with exact terminal-accumulator elision.

The parent frame compiler and DAG are unchanged. Eligible destination-only
ordinary terminal roles are removed, and their updates are redirected to the
corresponding output at the original operation time. This finite generator
keeps a complete event receipt and derives the paid one-child histogram.
The construction adapts the terminal-elision work in PR #122 by
SovereignSteak; the shrunk-frame parent is PR #125 by Joel Pulikkan.
Prepared with OpenAI Codex assistance; Apache-2.0.
"""
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from itertools import combinations
from pathlib import Path
import random
import sys

P = (1 << 61) - 1


def need(condition, message):
    if not condition:
        raise ValueError(message)


def basis(vectors):
    pivots = {}
    for vector in vectors:
        for pivot in sorted(pivots, reverse=True):
            if vector >> pivot & 1:
                vector ^= pivots[pivot]
        if vector:
            pivot = vector.bit_length() - 1
            for old in pivots:
                if pivots[old] >> pivot & 1:
                    pivots[old] ^= vector
            pivots[pivot] = vector
    return tuple(pivots[p] for p in sorted(pivots, reverse=True))


def contains(frame, larger):
    larger = basis(larger)
    return len(basis(tuple(frame) + larger)) == len(larger)


def parent_word_from_capture(d):
    """Serialize the captured parent state in the terminal audit convention.

    Ordinary adjoints are stored as signed numerators over 42. Center vectors
    remain unscaled; their scatter rows carry the denominator 42.
    """
    h, v, roles = d['h'], d['v'], d['Rr']
    scale = 42
    word = dict(
        h=h, v=v, R=roles, q=d['q'], args=d['args'], roots=d['roots'],
        ops=d['ops'], frames={str(n): d['U'][n] for n in d['U']},
        sigma={str(s): d['placed'][s] for s in d['placed']},
        role_root={str(s): j for s, j in d['role_root'].items()},
        leaf_of={str(s): leaf for s, leaf in d['leaf_of'].items()},
        first_node=d['first_node'], target=d['target'], kind=list(d['kind']),
        adjoint_centre={str(s): d['cvec'][s] for s in range(roles)},
        adjoint_ordinary={str(s): {str(t): (scale * c) % P for t, c in d['dpart'][s].items()}
                          for s in range(roles)},
        reach={str(s): sorted(d['reach'][s]) for s in range(roles)},
        phase_one=d['phase1'], deferred=d['deferred'], chain_dims=d['chain_dims'],
        root_frames={str(s): d['root_frame'][s] for s in d['root_frame']},
        centre_of={str(j): i for j, i in d['centre_of'].items()},
        trip=[list(t) for t in d['trip']])
    return word


def canonical_word_bytes(word):
    def json_default(value):
        if hasattr(value, 'tolist'):
            return value.tolist()
        if isinstance(value, set):
            return sorted(value)
        raise TypeError('Unsupported captured value: ' + type(value).__name__)
    payload = json.dumps(word, separators=(',', ':'), default=json_default).encode()
    return gzip.compress(payload, mtime=0)


def normalize_word(word):
    """Accept either the compact list or keyed-map export convention."""
    for name in ('frames', 'sigma', 'role_root', 'leaf_of', 'adjoint_centre',
                 'adjoint_ordinary', 'reach', 'root_frames', 'centre_of'):
        value = word[name]
        if isinstance(value, list):
            word[name] = {str(i): row for i, row in enumerate(value)}
    return word


def inventory(word):
    h, v, roles = word['h'], word['v'], word['R']
    frames = {int(k): v for k, v in word['frames'].items()}
    sigma = {int(k): v for k, v in word['sigma'].items()}
    roots = {int(k): v for k, v in word['role_root'].items()}
    leaves = {int(k): v for k, v in word['leaf_of'].items()}
    centre = {int(k): v for k, v in word['adjoint_centre'].items()}
    ordinary = {int(k): {int(t): (c if c <= P // 2 else c - P) for t, c in row.items()}
                for k, row in word['adjoint_ordinary'].items()}
    destinations, sources = Counter(), Counter()
    gate_frames = [[] for _ in range(roles)]
    for op in word['ops']:
        if op[0] == 'add':
            dst, src = op[1], op[2]
        elif op[0] == 'copy':
            src, dst = op[1], op[2]
        else:
            continue
        destinations[dst] += 1
        sources[src] += 1
        gate_frames[dst].append(frames[op[3]])

    target_frames = [[] for _ in range(v)]
    for s in word['deferred']:
        for t in word['reach'][str(s)]:
            target_frames[t].append(sigma[s])
    candidates, blocked = [], Counter()
    for s in range(roles):
        if s not in roots or word['kind'][roots[s]] or sources[s]:
            continue
        if s not in sigma:
            blocked['not_deferred'] += 1
            continue
        j = roots[s]
        t = word['target'][j]
        expected = {t: 21 if j < v else -21}
        if centre[s] is not None or ordinary[s] != expected:
            blocked['nonterminal_adjoint'] += 1
            continue
        updates = ([frames[word['first_node'][s]]] if s in leaves else []) + gate_frames[s]
        if not updates:
            blocked['no_updates'] += 1
            continue
        if any(not contains(old, update) for old in target_frames[t] for update in updates):
            blocked['target_past_update_frame'] += 1
            continue
        candidates.append(s)

    # Check the whole target schedule before deleting any role. Every target
    # starts with its old deferred-readout frames, then grows at source times.
    current = [[] for _ in range(v)]
    by_target = defaultdict(list)
    for s in candidates:
        j = roots[s]
        t = word['target'][j]
        if s in leaves:
            by_target[t].append((-1, s, frames[word['first_node'][s]]))
    phase_one = set(word['phase_one'])
    for i, op in enumerate(word['ops']):
        if op[0] == 'add':
            dst = op[1]
        elif op[0] == 'copy':
            dst = op[2]
        else:
            continue
        if dst in candidates:
            need(i not in phase_one, 'terminal update crosses the center phase')
            by_target[word['target'][roots[dst]]].append((i, dst, frames[op[3]]))
    for s in word['deferred']:
        for t in word['reach'][str(s)]:
            need(contains(current[t], sigma[s]), 'parent target-frame reversal')
            current[t] = sigma[s]
    accepted, rejected, targets = set(), set(), {}
    for t, rows in by_target.items():
        rows.sort(key=lambda row: (row[0], row[1]))
        chain = [current[t]] + [row[2] for row in rows]
        nested = all(contains(a, b) for a, b in zip(chain, chain[1:]))
        role_ids = {row[1] for row in rows}
        (accepted if nested else rejected).update(role_ids)
        targets[t] = dict(roles=sorted(role_ids), nested=nested,
                          frame_dimensions=[len(basis(f)) for f in chain],
                          event_indices=[row[0] for row in rows])
    need(set(candidates) == accepted | rejected, 'incomplete target schedule')
    return dict(candidates=sorted(candidates), accepted=sorted(accepted),
                rejected=sorted(rejected), terminal_blocked=dict(blocked),
                target_count=len(by_target), targets=targets)


def build(word, parent_profile, parent_word_sha256=None):
    """Build the terminal-elided profile and a complete chronological receipt."""
    need(not sys.flags.optimize, 'Assertions required')
    selection = inventory(word)
    removed = set(selection['accepted'])
    need(removed and not selection['rejected'], 'simultaneous target chain is not nested')
    # The candidate set is frozen against the pinned #125 parent. A changed
    # parent must be re-screened instead of silently changing the submission.
    need(len(removed) == 381 and selection['target_count'] == 381,
         'terminal inventory differs from the screened PR #125 candidate')

    h, v, roles = word['h'], word['v'], word['R']
    m = h * h
    frames = {int(k): v for k, v in word['frames'].items()}
    sigma = {int(k): v for k, v in word['sigma'].items()}
    roots = {int(k): v for k, v in word['role_root'].items()}
    leaves = {int(k): v for k, v in word['leaf_of'].items()}
    root_frames = {int(k): v for k, v in word['root_frames'].items()}
    phase_one = set(word['phase_one'])
    deferred = set(word['deferred'])
    active = [s for s in range(roles) if s not in removed]

    events, current = [], [[] for _ in range(v)]
    target_paths = [[[]] for _ in range(v)]

    def front(target, frame, why):
        need(contains(current[target], frame), 'target frame reversal')
        if basis(current[target]) != basis(frame):
            events.append(['target_front', target, frame, why])
            target_paths[target].append(frame)
        current[target] = frame

    def redirect(role, source, frame, index, data=False):
        root = roots[role]
        target = word['target'][root]
        coefficient = 21 if root < v else -21
        front(target, frame, ['redirect', index, role])
        events.append(['direct_input' if data else 'direct_aux', target,
                       source, coefficient, frame, index, role])

    def gate(index, inverse=False):
        op = word['ops'][index]
        if op[0] == 'src':
            return
        dst, src = ((op[1], op[2]) if op[0] == 'add'
                    else (op[2], op[1]))
        need(src not in removed, 'terminal role is used as a control')
        if dst in removed:
            need(index not in phase_one, 'terminal redirect crosses the center phase')
            if not inverse:
                redirect(dst, src, frames[op[3]], index)
        else:
            events.append(['gate', index, -1 if inverse else 1])

    for role in active:
        if role not in deferred:
            events.append(['readout', role, -1, False, 'initial'])
    for role, leaf in leaves.items():
        if role not in deferred:
            need(role not in removed, 'nondeferred leaf role was deleted')
            events.append(['input', role, leaf, 1])
    for index in word['phase_one']:
        gate(index)
    for role, root in roots.items():
        if word['kind'][root]:
            need(role not in removed, 'center role was deleted')
            events.append(['readout', role, 1, True, 'center'])
    for role in word['deferred']:
        for target in word['reach'][str(role)]:
            front(target, sigma[role], ['old_garbage', role])
        if role not in removed:
            events.append(['readout', role, -1, False, 'deferred'])
    for role in word['deferred']:
        if role in leaves:
            if role in removed:
                redirect(role, leaves[role], frames[word['first_node'][role]], -1, True)
            else:
                events.append(['input', role, leaves[role], 1])
    for index in range(len(word['ops'])):
        if index not in phase_one:
            gate(index)
    for role, root in roots.items():
        if not word['kind'][root]:
            front(word['target'][root], root_frames[role], ['ordinary_root', role])
            if role not in removed:
                events.append(['readout', role, 1, True, 'ordinary'])
    for index in reversed(range(len(word['ops']))):
        gate(index, True)
    for role, leaf in leaves.items():
        if role not in removed:
            events.append(['input', role, leaf, -1])
    need(all(len(basis(frame)) == h - 1 for frame in current),
         'terminal target frames')

    # Reprice the removed auxiliary chains and replace the old target fronts.
    old_target, new_target, deleted = Counter(), Counter(), Counter()
    levels = [{0, h - 1} for _ in range(v)]
    for role in word['deferred']:
        for target in word['reach'][str(role)]:
            levels[target].add(len(basis(sigma[role])))
    for dimensions in levels:
        for low, high in zip(sorted(dimensions), sorted(dimensions)[1:]):
            old_target[high - low] += 2 * v
    for path in target_paths:
        dims = [len(basis(frame)) for frame in path]
        for low, high in zip(dims, dims[1:]):
            if high > low:
                new_target[high - low] += 2 * v
    for role in removed:
        dimensions = word['chain_dims'][role]
        for low, high in zip(dimensions[:-1], dimensions[1:-1]):
            if high > low:
                deleted[high - low] += 2 * v
        deleted[h - dimensions[-2]] += 2 * v
        deleted[m - h + dimensions[0]] += 2 * v
    deleted.pop(0, None)
    need(sum(width * count for width, count in deleted.items()) ==
         2 * v * len(removed) * m, 'deleted role rank mass')
    histogram = Counter({int(t): c for t, c in parent_profile['child_multiplicities'].items()})
    histogram.subtract(deleted)
    histogram.subtract(old_target)
    histogram.update(new_target)
    need(all(count >= 0 for count in histogram.values()), 'negative child multiplicity')
    histogram = Counter({width: count for width, count in histogram.items() if count})
    new_roles = roles - len(removed)
    new_width = 2 * v * v + 2 * v * new_roles
    rank_mass = sum(width * count for width, count in histogram.items())
    need(new_width * m - rank_mass == parent_profile['deficit'],
         'complete deficit changed')
    direct_updates = sum(event[0] in ('direct_aux', 'direct_input') for event in events)
    profile = dict(parent_profile)
    profile.update(
        pre_elimination_R=roles, R=new_roles, W=new_width, total_rank=rank_mass,
        terminal_elimination_count=len(removed), terminal_direct_updates=direct_updates,
        child_multiplicities=dict(sorted(histogram.items())), maxchild=max(histogram),
        deferred_roles=parent_profile['deferred_roles'] - len(removed),
        role_count_scope='Terminal-elided physical word; additions + roots - links is pre-elimination.')
    dimensions = Counter({int(k): value for k, value in parent_profile['deferred_dims'].items()})
    for role in removed:
        dimensions[len(basis(sigma[role]))] -= 1
    profile['deferred_dims'] = {k: value for k, value in sorted(dimensions.items()) if value}

    receipt = dict(
        parent_word_sha256=parent_word_sha256,
        removed=sorted(removed), active_roles=active, events=events,
        target_paths=target_paths,
        deleted_child_multiplicities=dict(sorted(deleted.items())),
        old_target_histogram=dict(sorted(old_target.items())),
        new_target_histogram=dict(sorted(new_target.items())),
        target_delta={width: new_target[width] - old_target[width]
                      for width in sorted(old_target.keys() | new_target.keys())
                      if new_target[width] != old_target[width]})
    replay(word, receipt, removed)
    return profile, receipt, selection


def replay(word, receipt, removed):
    events = receipt['events']
    h, v, roles = word['h'], word['v'], word['R']
    roots = {int(s): j for s, j in word['role_root'].items()}
    leaves = {int(s): j for s, j in word['leaf_of'].items()}
    operations = word['ops']
    active = receipt['active_roles']
    inv42 = pow(42, P - 2, P)
    triples = list(combinations(range(h), 3))
    scatter = [[2 - 21 * (i in triple) for triple in triples] for i in range(h)]

    def run(seed):
        rng = random.Random(seed)
        x = [rng.randrange(P) for _ in range(v)]
        scratch = {s: rng.randrange(P) for s in active}
        aux = dict(scratch)
        y0 = [rng.randrange(P) for _ in range(v)]
        y = list(y0)
        pending_centres = [0] * h

        def read(role, sign, seeded):
            if seeded:
                root = roots[role]
                if word['kind'][root]:
                    centre = int(word['centre_of'][str(root)])
                    centre_row = [int(i == centre) for i in range(h)]
                    ordinary_row = {}
                else:
                    centre_row = None
                    target = word['target'][root]
                    ordinary_row = {target: 21 if root < v else -21}
            else:
                centre_row = word['adjoint_centre'][str(role)]
                ordinary_row = {int(t): c for t, c in word['adjoint_ordinary'][str(role)].items()}
            value = sign * aux[role] * inv42 % P
            if centre_row is not None:
                for i, coefficient in enumerate(centre_row):
                    if coefficient:
                        pending_centres[i] = (pending_centres[i] + coefficient * value) % P
            for target, coefficient in ordinary_row.items():
                y[target] = (y[target] + coefficient * value) % P

        for event in events:
            mode = event[0]
            if mode == 'target_front':
                continue
            if mode == 'input':
                _, role, leaf, sign = event
                aux[role] = (aux[role] + sign * x[leaf - 1]) % P
            elif mode == 'gate':
                _, index, sign = event
                op = operations[index]
                dst, src = (op[1], op[2]) if op[0] == 'add' else (op[2], op[1])
                aux[dst] = (aux[dst] + sign * aux[src]) % P
            elif mode == 'readout':
                _, role, sign, seeded, _tag = event
                read(role, sign, seeded)
            elif mode in ('direct_aux', 'direct_input'):
                _, target, source, numerator = event[:4]
                value = aux[source] if mode == 'direct_aux' else x[source - 1]
                y[target] = (y[target] + numerator * inv42 * value) % P
            else:
                raise ValueError('unknown event: ' + mode)
        for i, value in enumerate(pending_centres):
            for target, coefficient in enumerate(scatter[i]):
                y[target] = (y[target] + value * coefficient) % P
        need(aux == scratch, 'retained dirty scratch was not restored')
        need(all((out - base - source) % P == 0
                 for out, base, source in zip(y, y0, x)), 'normalized scalar map')

    seeds = (202610081, 202610082)
    for seed in seeds:
        run(seed)
    receipt['modular_replay'] = dict(seeds=list(seeds), prime=P, passed=True)


def write_outputs(directory, profile, receipt, selection):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / 'complex-profile.json').write_text(json.dumps(profile, indent=1) + '\n')
    payload = json.dumps(receipt, separators=(',', ':')).encode()
    (directory / 'terminal-elision.json.gz').write_bytes(gzip.compress(payload, mtime=0))
    (directory / 'terminal-selection.json').write_text(json.dumps(selection, indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--word', type=Path, required=True)
    parser.add_argument('--profile', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    raw = args.word.read_bytes()
    word = normalize_word(json.loads(gzip.decompress(raw)))
    profile, receipt, selection = build(
        word, json.loads(args.profile.read_text()), hashlib.sha256(raw).hexdigest())
    write_outputs(args.out, profile, receipt, selection)
    print(json.dumps(dict(removed=len(receipt['removed']), R=profile['R'], W=profile['W'],
                          direct_updates=profile['terminal_direct_updates'],
                          total_rank=profile['total_rank'], replay='PASS'), indent=2))


if __name__ == '__main__':
    main()
