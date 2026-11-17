#!/usr/bin/env python3
"""Blind finite audit of the frozen contact composition. Python standard library."""
import argparse
from collections import Counter
from difflib import SequenceMatcher
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import json
from math import gcd, lcm
from pathlib import Path
import runpy
import sys


MODEL = 'OpenAI Codex Sol, high reasoning (coordinator designation)'
HEADS = {'7643': '694667c8c129508d78b53a6a51690d4c284d0549',
         '7644': '32cfa1d20d3e4587dc601e69ccac1cd24a239e5c',
         '7113': '07a76c5e2738882c0cb322278e56f6cae3c9885d'}
FROZEN = '58a045048c853c7f89c53b8b5542e127ba2d12d122a6551d107119bd63e4b067'
UNIT = 1 << 48
ODD = 1125
GRID = UNIT * ODD


class Rejected(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise Rejected(str(message))


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def load(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if data.startswith(b'\x1f\x8b') else data)


def span(vectors):
    out = {0}
    for v in vectors:
        require(0 < v < 512 and v not in out, ('independent frame', vectors))
        out |= {v ^ u for u in out}
    return out


def scaled(row, q, i):
    if q == 1:
        return row
    out = {}
    for j, a in row.items():
        value, rem = divmod(a * q.numerator, q.denominator)
        require(not rem, ('exact grid overflow', i, j, str(q)))
        if value:
            out[j] = value
    return out


def frozen(row):
    return tuple(sorted(row.items()))


def summarize(row, explicit=False):
    if row is None:
        return None
    answer = {'terms': len(row), 'sha256': digest(row)}
    if explicit:
        answer['coefficients'] = [[k, str(Q(v, GRID))] for k, v in row]
    return answer


def change_blocks(left, right):
    a = list(map(tuple, left))
    b = list(map(tuple, right))
    lo = 0
    while lo < min(len(a), len(b)) and a[lo] == b[lo]:
        lo += 1
    tail = 0
    while tail < min(len(a), len(b)) - lo and a[-1-tail] == b[-1-tail]:
        tail += 1
    hi_a, hi_b = len(a)-tail, len(b)-tail
    match = SequenceMatcher(None, a[lo:hi_a], b[lo:hi_b], autojunk=True)
    blocks = [(op, i+lo, j+lo, k+lo, m+lo) for op, i, j, k, m in match.get_opcodes()]
    if lo:
        blocks.insert(0, ('equal', 0, lo, 0, lo))
    if tail:
        blocks.append(('equal', hi_a, len(a), hi_b, len(b)))
    return blocks


def replay(word, selected=(), mutate=None):
    n, m = word['public'], word['owned_fields']
    basis = word['frames']
    spaces = [span(f) for f in basis]
    require(len(word['initial']) == len(word['final']) == n, 'public inventory')
    frames = word['initial'] + [None]*m
    rows = [{r: GRID} for r in range(n)] + [{} for _ in range(m)]
    live, first, versions, clears, births = {}, {}, {}, [], []
    reads, routes, opened = {}, [], {}
    private_moves, owner_ordinals = [], Counter()
    selected = set(selected)
    ops, paid, rise, returned, odd_ops, chart_tags = (Counter() for _ in range(6))
    odd_grid, height, max_mass, peak = 1, 0, GRID, 0

    def measure(row):
        nonlocal odd_grid, height, max_mass
        max_mass = max(max_mass, sum(abs(a) for a in row.values()))
        for a in row.values():
            odd_grid = lcm(odd_grid, ODD // gcd(ODD, a))
            height = max(height, 49 - (abs(a) & -abs(a)).bit_length())

    for i, original in enumerate(word['program']):
        e = mutate[1] if mutate and i == mutate[0] else original
        op, r = e[:2]
        require(type(r) is int and 0 <= r < n+m, ('destination', i, e))
        ops[op] += 1
        if frames[r] == 922 or e[-1] == 922:
            chart_tags[op] += 1
        private = r >= n
        if op == 'INIT':
            require(private and frames[r] is None and r not in live and not rows[r], ('INIT', i, e))
            live[r], frames[r] = i, e[2]
            owner_ordinals[r] += 1
            peak = max(peak, len(live))
            if e[2] == 922:
                opened[r] = i
            births.append([i, r, e[2]])
        elif op == 'CLEAR':
            require(private and r in live and frames[r] == e[2], ('CLEAR', i, e))
            clears.append([live.pop(r), i, r, e[2], summarize(frozen(rows[r]), explicit=True)])
            if i in selected:
                versions[i] = {'clear': frozen(rows[r])}
            frames[r], rows[r] = None, {}
            opened.pop(r, None)
        elif op == 'MOVE':
            _, r, a, b, owned = e
            require(frames[r] == a and owned is private and (not private or r in live), ('MOVE ownership/frame', i, e))
            up = spaces[a] < spaces[b]
            require(up or (private and spaces[b] < spaces[a]), ('MOVE nesting', i, e))
            rank = abs(len(basis[a])-len(basis[b]))
            paid[rank] += 1
            if private:
                (rise if up else returned)[rank] += 1
                private_moves.append([i, live[r], r, owner_ordinals[r], a, b, rank,
                                      summarize(frozen(rows[r]), explicit=True)])
            if a == 922:
                opened.pop(r, None)
            if b == 922:
                opened[r] = i
            routes.append((i, r, a, b, owned, rank, live.get(r)))
            if i in selected:
                versions[i] = {'route_operand': frozen(rows[r])}
            frames[r] = b
        else:
            require(op in {'ADD', 'COPY', 'SCALE'}, ('opcode', i, e))
            s = r if op == 'SCALE' else e[2]
            require(type(s) is int and 0 <= s < n+m, ('source', i, e))
            require(frames[r] is not None and frames[r] == frames[s] == e[-1], ('arithmetic frame', i, e))
            require((r == s) == (op == 'SCALE'), ('distinct operands', i, e))
            q = Q(e[-2])
            require(q and abs(q)+1 < 2**16, ('finite coefficient', i, e))
            if q.denominator & (q.denominator-1):
                odd_ops[op] += 1
            if op == 'COPY':
                require(private and r in live and not rows[r], ('COPY zero destination guard', i, e))
            if e[-1] == 922:
                for reg in {r, s}:
                    key = reg, opened.get(reg, -1)
                    if key not in first:
                        first[key] = [i, reg, key[1], e, summarize(frozen(rows[reg]), explicit=True)]
            if private or s >= n or i in selected or e[-1] == 922:
                row_s, row_r = frozen(rows[s]), frozen(rows[r])
                if i in selected or e[-1] == 922:
                    versions[i] = {'source': row_s, 'destination_before': row_r}
                if private or s >= n:
                    reads[i] = {'source': row_s, 'destination_before': row_r,
                                'source_owner': live.get(s), 'destination_owner': live.get(r),
                                'source_owner_ordinal': owner_ordinals[s] if s in live else None,
                                'destination_owner_ordinal': owner_ordinals[r] if r in live else None}
            product = scaled(rows[s], q, i)
            measure(product)
            if op == 'SCALE':
                rows[r] = product
            else:
                for j, a in product.items():
                    z = rows[r].get(j, 0)+a
                    if z:
                        rows[r][j] = z
                    else:
                        rows[r].pop(j, None)
                measure(rows[r])
            if i in versions:
                versions[i]['destination_after'] = frozen(rows[r])
    require(not live and frames == word['final'] + [None]*m, 'return ownership and final charts')
    require(all(a % ODD == 0 for row in rows[:n] for a in row.values()), 'dyadic public return')
    endpoint = [frozen(row) for row in rows[:n]]
    return {'endpoint': endpoint, 'routes': routes, 'versions': versions, 'private': reads,
            'private_moves': private_moves,
            'first922': sorted(first.values()), 'clears': clears, 'births': births,
            'accounting': {'opcodes': ops, 'rank_sites': paid, 'private_rises': rise,
                           'private_returns': returned, 'peak_private': peak, 'lifetimes': len(clears),
                           'odd_divisions': odd_ops, 'odd_grid_lcm': odd_grid, 'dyadic_height': height,
                           'maximum_scaled_mass': str(Q(max_mass, UNIT)), 'chart922_opcodes': chart_tags}}


def render_versions(record, explicit=False):
    return {key: (summarize(value, explicit) if isinstance(value, tuple) else value)
            for key, value in record.items()}


def compare(left, right, first, second, blocks):
    removed, inserted, private, retained_changed = [], [], [], []
    matched_private = 0
    for op, i, j, k, m in blocks:
        if op == 'equal':
            for a, b in zip(range(i, j), range(k, m)):
                src = first['private'].get(a)
                dst = second['private'].get(b)
                if src is not None or dst is not None:
                    # Owner birth indices can shift under deletion. Operand equality
                    # is on ordered coordinate rows with owner links reported separately.
                    keys = ('source', 'destination_before', 'source_owner_ordinal', 'destination_owner_ordinal')
                    if (src is None or dst is None or
                            any(src[key] != dst[key] for key in keys)):
                        retained_changed.append([a, b, left['program'][a]])
                        private.append({'left': a, 'right': b, 'event': left['program'][a],
                                        'before': render_versions(src or {}, True),
                                        'after': render_versions(dst or {}, True)})
                    else:
                        matched_private += 1
            continue
        for src, start, end, result, output in (
                (left, i, j, first, removed), (right, k, m, second, inserted)):
            for p in range(start, end):
                e = src['program'][p]
                operands = result['private'].get(p)
                output.append({'index': p, 'event': e, 'operands': render_versions(
                    dict(result['versions'].get(p, {}), **(operands or {})), True)})
    return {'removed': removed, 'inserted': inserted, 'changed_aligned_private_reads': private,
            'matched_ordered_private_reads': matched_private,
            'changed_aligned_private_read_count': len(retained_changed),
            'literal_blocks': [list(b) for b in blocks if b[0] != 'equal']}


def exact_physical(pairs, frames, compiler, interpreter):
    comp = compiler['canonical_frame']
    lower = compiler['lower_child']
    frame, adj, recipe, state = (interpreter[k] for k in ('frame', 'adjoint', 'recipe', 'state'))
    results, control = [], None
    for a, b in sorted(pairs):
        fa, fb = frames[a], frames[b]
        expected = adj(frame(fa, 9)) + frame(fb, 9)
        rec, _ = lower(comp(9, fa).adjoint().then(comp(9, fb)))
        actual = recipe(rec)
        require(rec['rank'] == abs(len(fa)-len(fb)), ('lowered rank', a, b))
        for direct, reference in ((actual, expected), (adj(actual), adj(expected))):
            require(interpreter['tableau'](direct) == interpreter['tableau'](reference), ('signed tableau', a, b))
            for v in range(512):
                require(state(direct, v) == state(reference, v), ('Gaussian phase/column', a, b, v))
        if control is None:
            wrong = actual + (('phase', 1),)
            require(interpreter['tableau'](wrong) == interpreter['tableau'](actual), 'phase-only mutation tableau')
            require(state(wrong) != state(expected), 'phase-only mutation rejected by absolute state')
            control = {'route': [a, b], 'column': 0, 'phase_multiplier': 'i'}
        results.append({'route': [a, b], 'rank': rec['rank'], 'forward_columns': 512,
                        'adjoint_columns': 512, 'recipe_sha256': digest(rec)})
    require(control is not None, 'at least one changed physical route')
    return results, control


def hist(counter):
    return {int(r): int(n) for r, n in counter.items() if n}


def delta(a, b):
    return {r: b.get(r, 0)-a.get(r, 0) for r in sorted(a.keys() | b.keys()) if b.get(r, 0) != a.get(r, 0)}


def charge(native, common, stages):
    result = Counter({r: stages*n for r, n in native.items()})
    result.update(common)
    return hist(result)


def caller_binding(caller, word):
    stages, ambient, role_count = (caller[k] for k in ('stages', 'ambient_rank', 'roles'))
    require(caller['schema'] == 'mixed-root-caller/1' and (stages, ambient, role_count) == (17, 145, 72),
            'pinned caller boundary')
    types = caller['types']
    hosted = word['hosted']
    require(hosted['Dports'] == types['A']['ports'], 'A ports match hosted X2/Y2')
    require(sorted(types['A']['ports']+types['B']['ports']) == list(range(len(word['live']))), 'caller port partition')
    require(len(hosted['X2']) == len(hosted['Y2']) == len(hosted['Dports']), 'second plane inventory')
    require(hosted['alpha2'] == types['A']['alpha2'] and hosted['beta2'] == types['A']['beta2'], 'A scalar binding')
    second = dict(zip(hosted['Dports'], zip(hosted['X2'], hosted['Y2'])))
    widths = {kind: len(desc['ports']) for kind, desc in types.items()}
    domains = {kind: set(range(desc['offset'], desc['offset']+desc['roles'])) for kind, desc in types.items()}
    require(not domains['A'] & domains['B'] and domains['A'] | domains['B'] == set(range(role_count)), 'caller role partition')
    main = set(word['live']) | {r+112 for r in word['live']} | set(hosted['X2']) | set(hosted['Y2'])
    helpers = sorted(set(range(word['public']))-main)
    helper_targets = Counter()
    for r in helpers:
        before, after = (word['frames'][word[key][r]] for key in ('initial', 'final'))
        require(span(before) <= span(after), ('helper productive nesting', r))
        if (gain := len(after)-len(before)):
            helper_targets[gain] += 1
    target_owners, caller_targets = [], Counter()
    for kind, desc in types.items():
        require(len(desc['diagonal']) == desc['roles'], ('diagonal owner inventory', kind))
        for r, diagonal in zip(sorted(domains[kind]), desc['diagonal']):
            require(len(diagonal) == stages+2 and diagonal[:2] == [-1, 0] and set(diagonal[2:]) <= {0, 1},
                    ('central parity and fresh axes', kind, r))
            # The negative central line uses one direction. Every active stage
            # contributes its own eight distinct spectator directions.
            support = [stage for stage, flag in enumerate(diagonal[2:], 1) if flag]
            rank = 1+8*len(support)
            for p in desc['ports']:
                target_owners.append([kind, p, r, rank, support])
                caller_targets[rank] += 1
    bindings, opcodes, direct_paid, direct_sites = [], Counter(), Counter(), []
    for i, event in enumerate(caller['events']):
        kind, op, *args = event
        if kind == 'J':
            stage, a, b = event[1:]
            require(stage == len(bindings)+1 and len(a) == len(set(a)) == 4 and set(a) <= domains['A'], ('A contact', i))
            require(len(b) == 4 and len(set(b[:2])) == 2 and set(b[:2]) <= domains['B'], ('B contact', i))
            require(b[2:] == [hosted['alpha'], hosted['beta']], ('B scalar binding', i))
            owner_map = []
            for p, x in enumerate(word['live']):
                pair = a[:2] if p in second else b[:2]
                owner_map.extend([(x, p, pair[0]), (x+112, p, pair[1])])
                if p in second:
                    x2, y2 = second[p]
                    owner_map.extend([(x2, p, a[2]), (y2, p, a[3])])
            require({r for r, _, _ in owner_map} == main and len(set(owner_map)) == len(main), ('contact owner coverage', i))
            require(len({(p, r) for _, p, r in owner_map}) == len(main), ('contact owner collisions', i))
            bindings.append({'stage': stage, 'caller_index': i, 'contact': event,
                             'main_owner_map': owner_map, 'fresh_helper_count': len(helpers)})
            continue
        require(kind in types and op in ('ADD', 'SCALE', 'SWAP', 'LAMBDA', 'QUERY', 'IDLE_ONE', 'IDLE_ODD'), ('caller opcode', i, event))
        opcodes[kind, op] += 1
        require(args[0] in domains[kind], ('caller destination owner', i, event))
        if op in ('ADD', 'SWAP', 'QUERY'):
            require(args[1] in domains[kind] and args[0] != args[1], ('caller source owner', i, event))
        rank = None
        if op == 'QUERY':
            rank = 1
        if op in ('IDLE_ONE', 'IDLE_ODD'):
            require(args[1] and len(args[1]) == len(set(args[1])) and
                    set(args[1]) <= set(range(1, stages+1)), ('idle fresh stage list', i, event))
            # The odd idle field keeps the central line as well as the fresh
            # axes. An even idle field touches only the fresh axes.
            rank = 8*len(args[1])+(op == 'IDLE_ODD')
        if rank is not None:
            direct_paid[rank] += widths[kind]
            direct_sites.append({'index': i, 'event': event, 'rank': rank, 'ports': types[kind]['ports']})
    require(len(bindings) == stages, 'complete caller chronology')
    return {'stages': stages, 'ambient': ambient, 'widths': widths, 'contacts': bindings,
            'caller_opcodes': {f'{k}/{op}': n for (k, op), n in opcodes.items()},
            'helper_targets_per_stage': hist(helper_targets), 'target_owners': target_owners,
            'root_target_ranks': hist(caller_targets), 'direct_paid_ranks': hist(direct_paid),
            'direct_paid_sites': direct_sites}


def directed(inv, interval):
    signed = delta(hist(inv['paid']), hist(inv['targets']))
    moment, show = interval['moment'], interval['show']
    cap = Q('.00376669')
    derivative = (0, 0)
    for r, c in signed.items():
        # -c r^(1-k) ln r is increasing if c>=0 and decreasing otherwise.
        term = interval['mul'](interval['power'](r, cap if c >= 0 else 0), interval['log'](r))
        derivative = interval['add'](derivative, interval['smul'](term, -c))
    require(derivative[1] < 0, 'strictly decreasing directed moment')
    require(moment(signed, 0)[0] > 0 > moment(signed, cap)[1], 'unique crossing within BIT band')
    lo, hi = Q(0), cap
    for _ in range(75):
        mid = (lo+hi)/2
        a, b = moment(signed, mid)
        require(a > 0 or b < 0, ('ambiguous directed bisection', str(mid)))
        if a > 0:
            lo = mid
        else:
            hi = mid
    scale = 10**22
    lower_integer, upper_integer = (lo*scale).__floor__(), (hi*scale).__ceil__()
    record = {'bracket': [str(lo), str(hi)],
              'outward_decimal_bracket': [f'0.{lower_integer:022d}', f'0.{upper_integer:022d}'],
              'moments': [show(moment(signed, lo)), show(moment(signed, hi))],
              'derivative_bound': show(derivative), 'rank_surplus': sum(r*c for r, c in signed.items())}
    return (lo, hi), record


def mutation_word(word, replayed):
    for i, rows in sorted(replayed['private'].items()):
        e = word['program'][i]
        if e[0] == 'COPY' and e[-1] == 922 and rows['source']:
            break
    else:
        for i, rows in sorted(replayed['private'].items()):
            e = word['program'][i]
            if e[0] == 'COPY' and rows['source']:
                break
        else:
            raise Rejected('no meaningful nonzero COPY source for operand control')
    expected = replayed['versions'].get(i, {}).get('destination_after')
    if expected is None:
        expected = frozen(scaled(dict(rows['source']), Q(e[-2]), i))
    wrong = list(e)
    wrong[-2] = str(-Q(e[-2]))
    try:
        tested = replay(word, (i,), mutate=(i, wrong))
        require(tested['versions'][i]['destination_after'] == expected, ('ordered COPY operand control', i))
    except Rejected as exc:
        return {'index': i, 'original': e, 'mutation': wrong, 'rejected_by': str(exc)}
    raise Rejected('sign-flipped COPY accepted')


def contact_operands(words, replays):
    first = {k: {row[1]: row for row in v['first922']} for k, v in replays.items()}
    for r in (779, 949, 587, 960, 7, 196):
        require(all(entries[r][-1] == first['7605'][r][-1] for entries in first.values()),
                ('unaltered first chart-922 coordinate row', r))
    require(first['combined'][185][-1] == first['7644'][185][-1], 'chart-922 contact entry row')

    def find(label, destination, source, coefficient):
        word, rec = words[label], replays[label]
        matches = [(i, word['program'][i], v) for i, v in rec['versions'].items()
                   if word['program'][i] == ['ADD', destination, source, coefficient, 922]]
        require(matches, ('first chart-922 arithmetic occurrence', label, destination, source, coefficient))
        return min(matches, key=lambda row: row[0])

    old = find('7605', 185, 7, '1')
    pre = find('combined', 185, 779, '-1/4')
    same = find('combined', 185, 7, '1')
    post = find('combined', 185, 7, '-5/4')
    ordered = sorted((pre, same, post), key=lambda row: row[0])
    require(ordered[0] == pre, 'chart-922 preadjustment precedes reads of register 7')
    require(old[2]['source'] == same[2]['source'] == post[2]['source'], 'three chart-922 reads of register 7')
    require(all(a[2]['destination_after'] == b[2]['destination_before'] for a, b in zip(ordered, ordered[1:])),
            'ordered chart-922 transfer into register 185')
    return {'original': [old[0], old[1], render_versions(old[2], True)],
            'combined': [[i, e, render_versions(v, True)] for i, e, v in ordered],
            'same_after_each_combined_add': [old[2]['destination_after'] == row[2]['destination_after'] for row in ordered],
            'same_after_complete_contact': old[2]['destination_after'] == ordered[-1][2]['destination_after'],
            'affected_source_rows_equal': [779, 949, 587, 960, 7, 196]}


def contact_mutation(word, before, entry):
    i, e, _ = entry
    wrong = list(e)
    wrong[-2] = str(Q(wrong[-2])*2)
    try:
        tested = replay(word, (i,), mutate=(i, wrong))
        require(tested['versions'][i]['destination_after'] == before['versions'][i]['destination_after'],
                ('changed chart-922 transfer changes exact coordinate row', i))
    except Rejected as exc:
        return {'index': i, 'original': e, 'mutation': wrong, 'rejected_by': str(exc)}
    raise Rejected('incorrect chart-922 transfer accepted')


def main(args, out):
    paths = {label: getattr(args, 'word'+label) for label in ('7605', '7642', '7643', '7644')}
    paths['combined'] = args.combined
    words = {label: load(path) for label, path in paths.items()}
    out['inputs'] = {label: {'path': str(path), 'file_sha256': sha256(path.read_bytes()).hexdigest(),
                             'canonical_sha256': digest(words[label])} for label, path in paths.items()}
    require(out['inputs']['combined']['canonical_sha256'] == FROZEN, 'frozen canonical combined digest')
    caller = load(args.caller)
    out['inputs']['caller'] = {'path': str(args.caller), 'file_sha256': sha256(args.caller.read_bytes()).hexdigest(),
                               'canonical_sha256': digest(caller)}
    if args.comparator_final:
        comp = load(args.comparator_final)
        require(comp['original_canonical_sha256'] == out['inputs']['7605']['canonical_sha256'] and
                comp['candidate_canonical_sha256'] == out['inputs']['7644']['canonical_sha256'] and
                comp['caller_sha256'] == out['inputs']['caller']['file_sha256'], 'comparator input identity')
        out['comparator_final_7644'] = {'path': str(args.comparator_final), 'canonical_sha256': digest(comp),
                                      'ordinary_bound': comp['ordinary_bound'], 'precision_c': comp['precision_c'],
                                      'tape': comp['tape'], 'status': comp['status']}
    baseline = words['7605']
    comparisons = [('7605', '7642'), ('7642', '7643'), ('7643', '7644'),
                   ('7644', 'combined'), ('7643', 'combined'), ('7605', 'combined')]
    orders, selected = {}, {k: set() for k in words}
    for label, word in words.items():
        require(all(word[k] == baseline[k] for k in ('initial', 'final', 'hosted', 'live', 'ports', 'public', 'owned_fields')), ('boundary data', label))
        require(word['frames'] == baseline['frames'], ('canonical frame tables', label))
    for a, b in comparisons:
        order = change_blocks(words[a]['program'], words[b]['program'])
        orders[a, b] = order
        for op, i, j, k, m in order:
            if op != 'equal':
                selected[a].update(range(i, j))
                selected[b].update(range(k, m))
    replays = {}
    out['words'] = {}
    for label, word in words.items():
        print('symbolic replay', label, flush=True)
        rec = replay(word, selected[label])
        replays[label] = rec
        out['words'][label] = {'accounting': rec['accounting'], 'first_chart_922_reads': rec['first922'],
                               'returns_and_lifetimes': rec['clears'], 'endpoint_sha256': digest(rec['endpoint']),
                               'private_ordered_read_count': len(rec['private']),
                               'private_move_operands': rec['private_moves']}
    pair_set = set()
    out['literal_comparisons'] = {}
    for a, b in comparisons:
        rec = compare(words[a], words[b], replays[a], replays[b], orders[a, b])
        duplicates = Counter(tuple(row['event']) for row in rec['inserted'])
        erased = []
        for row in rec['removed']:
            event = tuple(row['event'])
            if duplicates[event]:
                duplicates[event] -= 1
            else:
                erased.append(row)
        rec['net_erased_rows'] = erased
        rec['net_erased_by_opcode'] = Counter(row['event'][0] for row in erased)
        rec['net_erased_arithmetic_rows'] = sum(row['event'][0] in ('ADD', 'SCALE', 'COPY') for row in erased)
        rec['public_endpoint_difference'] = [r for r, (x, y) in enumerate(zip(replays[a]['endpoint'], replays[b]['endpoint'])) if x != y]
        for row in rec['removed'] + rec['inserted']:
            e = row['event']
            if e[0] == 'MOVE':
                pair_set.add(tuple(e[2:4]))
        out['literal_comparisons'][a+'-to-'+b] = rec
    require(all(not rec['public_endpoint_difference'] for rec in out['literal_comparisons'].values()),
            'complete arbitrary-input public linear action')
    for label, rec in replays.items():
        require(len(rec['clears']) == 74 and [e[2:] for e in rec['clears']] == [e[2:] for e in replays['7605']['clears']],
                ('74 literal CLEAR operand rows and terminal owners', label))
        require([e[2:] for e in rec['private_moves']] == [e[2:] for e in replays['7605']['private_moves']],
                ('ordered private move and return operands', label))
    for (a, b), rec in zip(comparisons, out['literal_comparisons'].values()):
        require(rec['matched_ordered_private_reads'] == len(replays[a]['private']) == len(replays[b]['private']) and
                not rec['changed_aligned_private_reads'], ('ordered private reads and ownership', a, b))
    require(replays['combined']['first922'], 'first chart-922 reads exist')
    out['contact_922'] = contact_operands(words, replays)
    require(out['contact_922']['same_after_complete_contact'], 'chart-922 row agrees after the complete contact for arbitrary inputs')
    out['private_ordered_reads_combined'] = [
        {'index': i, 'event': words['combined']['program'][i], 'operands': render_versions(rows, True)}
        for i, rows in sorted(replays['combined']['private'].items())]
    copy_terminal = [r for r in out['private_ordered_reads_combined'] if r['event'][0] == 'COPY']
    require(len(copy_terminal) == 1 and not copy_terminal[0]['operands']['destination_before']['terms'],
            'unique literal COPY zero guard')
    out['mutation_controls'] = {'chart_operand': contact_mutation(words['combined'], replays['combined'], out['contact_922']['combined'][0]),
                                'copy_operand': mutation_word(words['combined'], replays['combined'])}
    print('caller and invoice', flush=True)
    bind = caller_binding(caller, words['combined'])
    out['caller'] = bind
    invs = {k: load(p) for k, p in [('7643', args.invoice7643), ('7644', args.invoice7644)]}
    for label, path in [('7643', args.invoice7643), ('7644', args.invoice7644)]:
        inv = invs[label]
        require(inv['schema'] == 'integer-mult-recursive-invoice/v1' and inv['contract']['ambient_rank'] == bind['ambient'], ('invoice schema', label))
        out['inputs'][label+'-invoice'] = {'path': str(path), 'file_sha256': sha256(path.read_bytes()).hexdigest(), 'canonical_sha256': digest(inv)}
    require(invs['7643']['contract'] == invs['7644']['contract'] and invs['7643']['targets'] == invs['7644']['targets'], 'shared caller invoice contract and targets')
    stages = bind['stages']
    natives = {k: v['accounting']['rank_sites'] for k, v in replays.items()}
    residuals = {k: delta(charge(natives[k], {}, stages), hist(invs[k]['paid'])) for k in invs}
    require(residuals['7643'] == residuals['7644'] and all(x > 0 for x in residuals['7644'].values()), 'two complete paid anchors agree on common caller charges')
    common = bind['direct_paid_ranks']
    require(common == residuals['7644'], 'concrete caller rank sites agree with both complete paid anchors')
    target_common = delta(charge(bind['helper_targets_per_stage'], {}, stages), hist(invs['7644']['targets']))
    require(bind['root_target_ranks'] == target_common, 'literal caller diagonal target owners agree with complete anchors')
    invoice = dict(invs['7644'], paid=charge(natives['combined'], common, stages),
                   targets=charge(bind['helper_targets_per_stage'], bind['root_target_ranks'], stages))
    out['invoice'] = {'complete_combined': invoice, 'caller_paid_rank_sites': common,
                      'caller_productive_rank_owners': bind['root_target_ranks'],
                      'independent_target_and_paid_anchors_agree': True,
                      'native_paid': {k: hist(v) for k, v in natives.items()},
                      'combined_minus_7644_paid': delta(hist(invs['7644']['paid']), invoice['paid']),
                      'combined_minus_7643_paid': delta(hist(invs['7643']['paid']), invoice['paid']),
                      'paid_calls': sum(invoice['paid'].values()), 'target_calls': sum(invoice['targets'].values())}
    route_indices = {row['index'] for row in out['literal_comparisons']['7605-to-combined']['inserted']
                     if row['event'][0] == 'MOVE'}
    moved = next(r for r in replays['combined']['routes'] if r[0] in route_indices)
    without = Counter(common)
    for stage in range(1, stages+1):
        for row in replays['combined']['routes']:
            if (stage, row[0]) != (1, moved[0]):
                without[row[5]] += 1
    require(delta(invoice['paid'], hist(without)) == {moved[5]: -1}, 'single literal omitted rank charge')
    try:
        require(hist(without) == invoice['paid'], 'complete invoice disagrees with mutated concrete charge tape')
    except Rejected as exc:
        out['mutation_controls']['charge'] = {'original_site': words['combined']['program'][moved[0]],
            'native_index': moved[0], 'stage': 1, 'rank': moved[5], 'removed_instances': 1, 'rejected_by': str(exc)}
    else:
        raise Rejected('missing literal paid site accepted')
    account = {k: v['accounting'] for k, v in replays.items()}
    cand, prev = account['combined'], account['7644']
    out['native_ordinary_precision_tape'] = {
        'opcode_delta_vs_7644': delta(prev['opcodes'], cand['opcodes']),
        'ordinary_logical_arithmetic_sites': {op: stages*cand['opcodes'][op] for op in ('ADD', 'SCALE', 'COPY')},
        'precision': {key: cand[key] for key in ('odd_grid_lcm', 'dyadic_height', 'maximum_scaled_mass', 'odd_divisions')},
        'literal_tape_occurrences': {'stages': stages, 'forward_paid_routes': stages*cand['opcodes']['MOVE'],
            'adjoint_paid_routes': stages*cand['opcodes']['MOVE'], 'clear_ownership_records': stages*cand['lifetimes']},
        'scope': 'Logical native opcode and coordinate-grid ledgers. Full physical ordinary bit bound, precision constant, and allocated signed tape require the separate application.'}
    print('directed crossings', flush=True)
    primitive_root = args.primitives / 'retained' / 'role902'
    files = {'interval': primitive_root / 'engines' / 'interval_gate.py',
             'compiler': primitive_root / 'independent' / 'engines' / 'clifford_exact.py',
             'interpreter': primitive_root / 'independent' / 'engines' / 'native_verify.py'}
    out['primitives'] = {k: {'path': str(p), 'sha256': sha256(p.read_bytes()).hexdigest()} for k, p in files.items()}
    interval = runpy.run_path(str(files['interval']))
    roots = {k: directed(inv, interval) for k, inv in dict(invs, combined=invoice).items()}
    out['directed_kappa'] = {k: r for k, (_, r) in roots.items()}
    worst = max(roots[k][0][1] for k in invs)
    lower = roots['combined'][0][0]
    require(lower > worst, 'combined directed crossing strictly above both anchors')
    middle = (lower+worst)/2
    out['directed_kappa']['separation'] = {'minimum_gap': str(lower-worst), 'test_point': str(middle),
        'moments_at_test_point': {k: interval['show'](interval['moment'](
            delta(hist(inv['paid']), hist(inv['targets'])), middle)) for k, inv in dict(invs, combined=invoice).items()}}
    print('exact forward and adjoint routes', flush=True)
    checked, phase = exact_physical(pair_set, baseline['frames'], runpy.run_path(str(files['compiler'])),
                                    runpy.run_path(str(files['interpreter'])))
    out['physical_changed_routes'] = checked
    out['mutation_controls']['phase'] = phase
    out['status'] = 'PASS_INDEPENDENT_FINITE_CHECK_SIGNED_OBLIGATIONS_OPEN'


def cli():
    parser = argparse.ArgumentParser(description=__doc__)
    for k in ('7605', '7642', '7643', '7644'):
        parser.add_argument('--word'+k, type=Path, required=True)
    for k in ('combined', 'caller', 'invoice7643', 'invoice7644', 'primitives', 'out'):
        parser.add_argument('--'+k, type=Path, required=True)
    parser.add_argument('--comparator-final', type=Path)
    args = parser.parse_args()
    out = {'schema': 'blind-independent-finite-scientific-audit/1', 'status': 'INCOMPLETE',
           'model': MODEL, 'reasoning': 'high', 'source_heads_as_supplied': HEADS,
           'argv': list(getattr(sys, 'orig_argv', [sys.executable, *sys.argv])), 'cwd': str(Path.cwd()),
           'checker_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
           'scope': 'Complete frozen words, exact public-linear replay and private lifetimes, changed native route maps, caller-site rank invoice, and fixed-invoice price crossings.',
           'blindness_note': 'During primitive discovery excerpts from retained #7605 physical and price wrappers and older audit wrappers were displayed. The checker uses its own proof program and the listed generic primitives, with no combined builder or application code.',
           'open_obligations': ['Full signed application across all caller operators and fresh spectator coordinates',
                                'Full ordinary bit bound, precision constant, and allocated physical tape from the signed application',
                                'Outer recurrence, compiler constants, and theorem-level multiplication claim']}
    try:
        require(not sys.flags.optimize, 'assertions required in the credited primitives')
        main(args, out)
        return 0
    except Exception as exc:
        out['status'] = 'FAIL_OR_UNRESOLVED'
        out['failure'] = {'type': type(exc).__name__, 'message': str(exc)}
        raise
    finally:
        args.out.write_text(json.dumps(out, indent=2, sort_keys=True)+'\n')


if __name__ == '__main__':
    raise SystemExit(cli())
