#!/usr/bin/env python3
"""Derive the fixed caller invoice from literal events and declared endpoints."""
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from hashlib import sha1, sha256
from pathlib import Path
import gzip
import json

ROOT = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def rank(rows):
    pivots = {}
    for row in rows:
        while row:
            p = row.bit_length()
            if p not in pivots:
                pivots[p] = row
                break
            row ^= pivots[p]
    return len(pivots)


def histogram(counter):
    return {str(k): v for k, v in sorted(counter.items()) if v}


def stage_axes(selected):
    need(selected and len(set(selected)) == len(selected), 'distinct nonempty idle stages')
    need(all(type(s) is int and 1 <= s <= 17 for s in selected), 'idle stage range')
    return [1 << (9 + 8 * (s - 1) + j) for s in selected for j in range(8)]


def derive(caller, word):
    need(caller['stages'] == 17 and caller['ambient_rank'] == 145, 'fixed caller dimensions')
    types = caller['types']
    need(set(types) == {'A', 'B'} and caller['roles'] == 72, 'two caller types')
    roles = {k: set(range(d['offset'], d['offset'] + d['roles'])) for k, d in types.items()}
    need(not (roles['A'] & roles['B']) and roles['A'] | roles['B'] == set(range(72)), 'disjoint complete caller roles')
    ports = [pi for d in types.values() for pi in d['ports']]
    need(sorted(ports) == list(range(104)), 'disjoint complete port partition')
    hosted = word['hosted']
    need(types['A']['ports'] == hosted['Dports'], 'second-plane ports')
    need(len(word['ports']) == len(word['live']) == 104, 'native port inventory')
    need(all(type(q) is int and 0 < q < 512 for q in word['ports']), 'nonzero central queries')
    need((hosted['alpha'], hosted['beta'], hosted['alpha2'], hosted['beta2']) == ('-1', '1/2', '-1', '0'), 'native scalar interface')
    need(len(hosted['Dports']) == len(hosted['X2']) == len(hosted['Y2']), 'second-plane inventory')
    native_main = set(word['live']) | {r + 112 for r in word['live']} | set(hosted['X2']) | set(hosted['Y2'])
    need(len(native_main) == 400 and native_main <= set(range(word['public'])), 'native main inventory')
    root_owners = {(pi, r) for k, d in types.items() for pi in d['ports'] for r in roles[k]}
    paid, targets, weighted = Counter(), Counter(), Counter()
    by_operation, occurrences, target_rows, stages_seen = {}, [], [], []
    for ci, event in enumerate(caller['events']):
        if event[0] == 'J':
            need(len(event) == 4, 'native event shape')
            _, stage, a, b = event
            stages_seen.append(stage)
            need(len(a) == 4 and len(set(a)) == 4 and set(a) <= roles['A'], 'distinct A native owners')
            need(len(b) == 4 and len(set(b[:2])) == 2 and set(b[:2]) <= roles['B'], 'distinct B native owners')
            need(b[2:] == ['-1', '1/2'], 'B native scalar interface')
            owners = [(pi, r) for k, d in types.items() for pi in d['ports'] for r in (a if k == 'A' else b[:2])]
            need(len(owners) == len(set(owners)) == len(native_main), 'injective native main contact')
            need(set(owners) <= root_owners, 'native main contact exists')
            continue
        ty, op, dest, *args = event
        need(ty in types and dest in roles[ty], 'caller destination')
        d = types[ty]
        if op in ('ADD', 'SWAP', 'QUERY'):
            need(args and args[0] in roles[ty] and args[0] != dest, 'distinct same-type source')
        if op == 'ADD':
            need(len(args) == 2, 'ADD shape')
            Fraction(args[1])
        elif op == 'SWAP':
            need(len(args) == 1, 'SWAP shape')
        elif op == 'SCALE':
            need(len(args) == 1 and Fraction(args[0]) != 0, 'invertible scalar')
        elif op == 'LAMBDA':
            need(len(args) == 1 and args[0] in (-1, 1), 'normalizer sign')
        elif op == 'QUERY':
            need(len(args) == 2 and args[1] in (-1, 1), 'query sign')
        elif op == 'IDLE_ONE':
            need(len(args) == 1, 'ordinary idle shape')
        elif op == 'IDLE_ODD':
            need(len(args) == 2 and args[1] == -1 and len(args[0]) == 1, 'signed idle shape')
        else:
            raise ValueError('unknown caller operation: ' + op)
        weighted[ty + ':' + op] += len(d['ports'])
        if op not in ('QUERY', 'IDLE_ONE', 'IDLE_ODD'):
            continue
        for pi in d['ports']:
            axes = [] if op == 'QUERY' else stage_axes(args[0])
            if op in ('QUERY', 'IDLE_ODD'):
                axes = [word['ports'][pi]] + axes
            cost = rank(axes)
            paid[cost] += 1
            by_operation.setdefault(ty + ':' + op, Counter())[cost] += 1
            owner = ['query_scratch', ci, pi] if op == 'QUERY' else ['main', pi, dest]
            occurrences.append([ci, op, owner, cost])
    need(stages_seen == list(range(1, 18)), 'complete ordered native stages')
    for ty, d in types.items():
        need(len(d['diagonal']) == d['roles'], 'one declared endpoint per root owner')
        for local, diagonal in enumerate(d['diagonal']):
            need(len(diagonal) == 19, 'endpoint shape')
            q_sign, zero, *mask = diagonal
            need(q_sign in (-1, 0, 1) and zero == 0 and set(mask) <= {0, 1}, 'signed endpoint form')
            axes = stage_axes([i + 1 for i, active in enumerate(mask) if active])
            for pi in d['ports']:
                target_rank = rank(([word['ports'][pi]] if q_sign else []) + axes)
                targets[target_rank] += 1
                target_rows.append([pi, d['offset'] + local, target_rank])
    need({tuple(r[:2]) for r in target_rows} == root_owners and len(target_rows) == len(root_owners), 'distinct root target owners')
    canonical = lambda x: json.dumps(x, separators=(',', ':'), sort_keys=True).encode()
    return {
        'native_calls': 17, 'caller_events': len(caller['events']), 'root_owners': len(root_owners),
        'native_public_helpers_per_call': word['public'] - len(native_main),
        'K_paid': histogram(paid), 'K_T_declared_roots': histogram(targets),
        'caller_paid_positions': sum(paid.values()),
        'caller_rank_surplus': sum(r * n for r, n in targets.items()) - sum(r * n for r, n in paid.items()),
        'paid_by_operation': {k: histogram(v) for k, v in sorted(by_operation.items())},
        'weighted_operation_counts': dict(sorted(weighted.items())),
        'paid_occurrence_sha256': sha256(canonical(occurrences)).hexdigest(),
        'declared_target_owner_sha256': sha256(canonical(target_rows)).hexdigest(),
    }


def combine_with_native(caller_report, word, reported):
    frames = word['frames']
    dims = [rank(f) for f in frames]
    need(all(d == len(f) for d, f in zip(dims, frames)), 'independent native frame bases')
    native_paid, native_targets = Counter(), Counter()
    for event in word['program']:
        if event[0] != 'MOVE':
            continue
        _, role, before, after, owned = event
        need(0 <= role < word['public'] + word['owned_fields'] and owned == (role >= word['public']), 'native paid owner class')
        joined = rank(frames[before] + frames[after])
        need(joined == max(dims[before], dims[after]) and dims[before] != dims[after], 'nested native MOVE')
        native_paid[abs(dims[before] - dims[after])] += 1
    main = set(word['live']) | {x + 112 for x in word['live']} | set(word['hosted']['X2']) | set(word['hosted']['Y2'])
    for r in set(range(word['public'])) - main:
        start, end = word['initial'][r], word['final'][r]
        need(rank(frames[start] + frames[end]) == dims[end] and dims[end] > dims[start], 'positive nested helper target')
        native_targets[dims[end] - dims[start]] += 1
    result = {}
    for name, local, native in [('paid', 'K_paid', native_paid), ('target', 'K_T_declared_roots', native_targets)]:
        total = Counter({int(k): v for k, v in caller_report[local].items()})
        total.update({r: 17 * n for r, n in native.items()})
        need(histogram(total) == reported[name], 'reported complete ' + name + ' invoice')
        result[name] = histogram(total)
    result['paid_positions'] = sum(result['paid'].values())
    result['productive_fields'] = sum(result['target'].values())
    return result


def controls(caller, word, result):
    passed = []
    def reject(label, changed):
        try:
            derive(changed, word)
        except ValueError:
            passed.append(label)
        else:
            raise ValueError('control accepted: ' + label)
    changed = deepcopy(caller)
    changed['types']['A']['ports'].append(changed['types']['A']['ports'][0])
    reject('duplicate port', changed)
    changed = deepcopy(caller)
    changed['types']['B']['diagonal'].pop()
    reject('missing declared output', changed)
    changed = deepcopy(caller)
    e = next(e for e in changed['events'] if e[0] == 'J')
    e[2][1] = e[2][0]
    reject('aliased native owners', changed)
    changed = deepcopy(caller)
    next(e for e in changed['events'] if e[0] == 'J')[1] = 2
    reject('wrong stage order', changed)
    changed = deepcopy(caller)
    e = next(e for e in changed['events'] if e[1] == 'IDLE_ONE')
    e[3].append(e[3][0])
    reject('repeated idle axis block', changed)
    changed = deepcopy(caller)
    next(e for e in changed['events'] if e[1] == 'IDLE_ODD')[4] = 1
    reject('wrong signed-idle coefficient', changed)
    changed = deepcopy(caller)
    query = next(e for e in changed['events'] if e[1] == 'QUERY')
    weight = len(changed['types'][query[0]]['ports'])
    changed['events'].remove(query)
    expect = dict(result['K_paid'])
    expect['1'] -= weight
    need(derive(changed, word)['K_paid'] == expect, 'missing query delta')
    passed.append('missing query changes rank-one cost')
    changed = deepcopy(caller)
    idle = next(e for e in changed['events'] if e[1] == 'IDLE_ODD')
    weight = len(changed['types'][idle[0]]['ports'])
    idle[1] = 'IDLE_ONE'
    idle.pop()
    expect = dict(result['K_paid'])
    expect['8'] += weight
    expect['9'] -= weight
    need(derive(changed, word)['K_paid'] == expect, 'signed query-axis cost delta')
    passed.append('omitted signed query axis moves rank-nine cost to rank eight')
    changed = deepcopy(caller)
    row = next(row for row in changed['types']['A']['diagonal'] if 0 in row[2:])
    old_rank = abs(row[0]) + 8 * sum(row[2:])
    row[next(i for i in range(2, len(row)) if row[i] == 0)] = 1
    expect = Counter({int(k): v for k, v in result['K_T_declared_roots'].items()})
    weight = len(changed['types']['A']['ports'])
    expect[old_rank] -= weight
    expect[old_rank + 8] += weight
    need(derive(changed, word)['K_T_declared_roots'] == histogram(expect), 'changed endpoint rank delta')
    passed.append('changed endpoint moves its distinct-owner target multiplicity')
    return passed


def main():
    for source in json.loads((ROOT / 'VENDORED.json').read_text())['files']:
        raw = (ROOT / source['path']).read_bytes()
        need(sha256(raw).hexdigest() == source['sha256'], 'source SHA256: ' + source['path'])
        need(sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == source['git_blob'], 'source Git blob: ' + source['path'])
    raw = (ROOT / 'source/CALLER.json').read_bytes()
    caller = json.loads(raw)
    word = json.loads(gzip.decompress((ROOT / 'source/WORD.json.gz').read_bytes()))
    result = derive(caller, word)
    reported = json.loads((ROOT / 'source/REPORTED.json').read_text())
    need(sha256(raw).hexdigest() == reported['caller_sha256'], 'reported caller bytes')
    need(sha256(json.dumps(word, separators=(',', ':'), sort_keys=True).encode()).hexdigest()
         == reported['source_word_sha256'], 'reported native word bytes')
    result['combined_source_invoice'] = combine_with_native(result, word, reported)
    result['semantic_controls'] = controls(caller, word, result)
    need(result == json.loads((ROOT / 'RESULT.json').read_text()), 'complete checked result')
    print('PASS_CALLER_DERIVED_RESIDUALS ' + json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
