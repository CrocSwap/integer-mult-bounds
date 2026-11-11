"""Causal-history two-buffer split; proposed constructor, not an admission.

Ali Romman's owned-buffer identity and CubeJerry's contact-free retiming are
predecessors. Implementation for dillona with OpenAI Codex assistance.
Apache-2.0. The complete exact native and caller checks remain mandatory.
"""
from collections import defaultdict, Counter
from copy import deepcopy
from fractions import Fraction as Q
from support import L
from split import basis, inverse


def construct(word, hit, neutral_paths):
    n, owned = word['public'], word['owned_fields']
    f, pivot, cut = hit['frame'], hit['pivot'], hit['cut']
    u, v = word['initial'][pivot], word['final'][pivot]
    c, d = ({int(k): Q(q) for k, q in hit[s].items()} for s in ('c', 'd'))
    main = set(word['live']) | {r+112 for r in word['live']} | set(word['hosted']['X2']) | set(word['hosted']['Y2'])
    group = {r for r in range(n) if r not in main and (word['initial'][r], word['final'][r]) == (u, v)}
    L.need(pivot in group and set(c) | set(d) <= group, 'One helper boundary group')
    spaces = list(map(L.span, word['frames']))
    L.need(spaces[u] < spaces[f] < spaces[v], 'Strict productive boundaries')
    L.need(hit['ranks'] == [len(word['frames'][f])-len(word['frames'][u]), len(word['frames'][v])-len(word['frames'][f])], 'Exact target ranks')
    gathers, injections = defaultdict(list), defaultdict(list)
    for obs in hit['gathers']:
        L.need(obs['frame'] == f and obs['cut'] <= cut, 'Gather chronology')
        gathers[obs['cut']].append(obs)
    for obs in hit['injections']:
        L.need(obs['frame'] == f and obs['cut'] >= cut, 'Injection chronology')
        injections[obs['cut']].append(obs)
    selected = {}
    for obs in hit['gathers'] + hit['injections']:
        if 'path' in obs:
            p = neutral_paths[obs['path']]
            L.need(p['role'] == obs['role'] and p['frame'] == f and p['lo'] <= obs['cut'] <= p['hi'], 'Observation belongs to its neutral path')
            selected[(p['role'], p['lo'], p['hi'])] = (p, False)
        if 'paid_path' in obs:
            p = hit['path']
            L.need(obs['paid_path'] == hit['paid_path'] and p['role'] == obs['role'] and p['frame'] == f and p['lo'] <= obs['cut'] <= p['hi'], 'Observation belongs to its paid path')
    if 'path' in hit:
        p = hit['path']
        selected[(p['role'], p['lo'], p['hi'])] = (p, True)
    # A pivot may use a neutral path even when its value is not gathered.
    for p in neutral_paths:
        if p['role'] == pivot and p['frame'] == f and p['lo'] <= cut <= p['hi']:
            selected.setdefault((p['role'], p['lo'], p['hi']), (p, False))
            break
    enter, leave, remove, delta = defaultdict(list), defaultdict(list), set(), Counter()
    events = word['program']
    for p, paid in selected.values():
        r, lo, hi = p['role'], p['lo'], p['hi']
        actual = [i for i in range(lo, hi) if events[i][1] == r or (events[i][0] in ('ADD', 'COPY') and events[i][2] == r)]
        L.need(actual == p['moves'] and actual, 'Complete contact-free interval')
        path = [events[i] for i in actual]
        L.need(all(e[0] == 'MOVE' and e[1] == r and e[4] == (r >= n) for e in path), 'Only owned-typed MOVEs')
        L.need(all(a[3] == b[2] for a, b in zip(path, path[1:])), 'Continuous original path')
        L.need(not remove.intersection(actual), 'Nonoverlapping changed intervals')
        remove.update(actual)
        if paid:
            a, b = path[0][2], path[-1][3]
            L.need((a, b) == (p['old'], p['new']) and (spaces[a] <= spaces[f] <= spaces[b] or spaces[b] <= spaces[f] <= spaces[a]), 'Paid nested midpoint')
            before = [['MOVE', r, a, f, r >= n]] if a != f else []
            after = [['MOVE', r, f, b, r >= n]] if f != b else []
        else:
            frames = [path[0][2]] + [e[3] for e in path]
            L.need(frames == p['frames'] and f in frames, 'Exact retained neutral path')
            at = frames.index(f)
            before, after = path[:at], path[at:]
        enter[lo].extend(before)
        leave[hi].extend(after)
        delta.update(abs(len(word['frames'][e[3]])-len(word['frames'][e[2]])) for e in before+after)
        delta.subtract(abs(len(word['frames'][e[3]])-len(word['frames'][e[2]])) for e in path)
    L.need({r: q for r, q in delta.items() if q} == {int(r): q for r, q in hit['paid_delta'].items()}, 'Complete paid histogram change')
    boundary = basis(c, d, pivot, u)
    out = deepcopy(word)
    out['public'] = n+1
    out['owned_fields'] = owned+2
    out['initial'].append(f)
    out['final'].append(v)
    out['final'][pivot] = f
    A, B = n+1+owned, n+2+owned
    program = inverse(boundary)
    current = word['initial'] + [None]*owned
    first, last = min(gathers), max(injections)

    def mapped(event, after):
        e = event.copy()
        for pos in (1, 2) if e[0] in ('ADD', 'COPY') else (1,):
            r = e[pos]
            e[pos] = n if after and r == pivot else r+int(r >= n)
        return e

    def original(event, after):
        op, r = event[:2]
        if op == 'MOVE':
            L.need(current[r] == event[2], 'Retimed path entry')
            current[r] = event[3]
        elif op == 'INIT':
            L.need(current[r] is None, 'Fresh original owned field')
            current[r] = event[2]
        elif op == 'CLEAR':
            L.need(current[r] == event[2], 'Original owned clear')
            current[r] = None
        else:
            L.need(current[r] == event[-1], 'Original scalar frame')
            if op in ('ADD', 'COPY'):
                L.need(current[event[2]] == event[-1], 'Original scalar source frame')
        program.append(mapped(event, after))

    for i in range(len(events)+1):
        for e in enter[i]:
            original(e, i > cut)
        if i == first:
            program.append(['INIT', A, f])
        for obs in gathers[i]:
            L.need(current[obs['role']] == f, 'Literal scheduled gather frame')
            r = obs['role'] + int(obs['role'] >= n)
            program.append(['ADD', A, r, str(Q(obs['coefficient'])), f])
        if i == cut:
            L.need(current[pivot] == f, 'Literal pivot residency')
            program.extend([
                ['INIT', B, f], ['ADD', B, n, '1', f], ['ADD', B, A, '-1', f],
                ['ADD', n, pivot, '1', f], ['ADD', n, A, '-1', f], ['ADD', n, B, '-1', f],
                ['ADD', pivot, A, '1', f], ['ADD', pivot, n, '-1', f], ['CLEAR', A, f]])
        for obs in injections[i]:
            L.need(current[obs['role']] == f, 'Literal scheduled injection frame')
            r = n if obs['role'] == pivot else obs['role'] + int(obs['role'] >= n)
            program.append(['ADD', r, B, str(Q(obs['coefficient'])), f])
        if i == last:
            program.append(['CLEAR', B, f])
        for e in leave[i]:
            original(e, i >= cut)
        if i < len(events) and i not in remove:
            original(events[i], i >= cut)
    L.need(current == word['final'] + [None]*owned, 'All original final frames')
    program += [mapped([*e[:-1], v], True) for e in boundary]
    out['program'] = program
    return out
