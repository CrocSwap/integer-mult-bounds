#!/usr/bin/env python3
"""Finite controls for the written all-workspace lemma, plus replay provenance.

Does not rerun the full C++ exclusion: use replay_r4.py for that cold dependency.
JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import hashlib
import heapq
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def rank(rows):
    basis = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = row
                break
            row ^= basis[pivot]
    return len(basis)


def mm(left, right):
    result = []
    for row in left:
        value = 0
        while row:
            bit = row & -row
            value ^= right[bit.bit_length() - 1]
            row ^= bit
        result.append(value)
    return tuple(result)


def duplicated(vector, roles):
    return sum(3 << (2 * i) for i in range(roles) if vector >> i & 1)


def right_gate(matrix, u, v):
    roles = len(matrix) // 2
    um, vm = duplicated(u, roles), duplicated(v, roles)
    return tuple(row ^ vm if (row & um).bit_count() % 2 else row for row in matrix)


def crossing(matrix):
    mask = sum(1 << i for i in range(0, len(matrix), 2))
    return rank(matrix[i] & mask for i in range(1, len(matrix), 2))


def gl4_rows(prefix=(), span=frozenset((0,))):
    if len(prefix) == 4:
        yield prefix
        return
    for row in range(1, 16):
        if row not in span:
            yield from gl4_rows(prefix + (row,), span | frozenset(x ^ row for x in span))


def grassmann_controls():
    planes = sorted({frozenset((0, a, b, a ^ b))
                     for a in range(1, 16) for b in range(1, 16) if a != b},
                    key=lambda values: tuple(sorted(values)))
    need(len(planes) == 35, 'binary plane inventory')
    distance = lambda a, b: 2 - ((len(a & b)).bit_length() - 1)
    geodesics = strict = 0
    for x, y, z in itertools.product(planes, repeat=3):
        dxy, dyz, dxz = distance(x, y), distance(y, z), distance(x, z)
        need(dxz <= dxy + dyz, 'Grassmann triangle inequality')
        if dxz == dxy + dyz:
            geodesics += 1
            strict += dxy > 0 and dyz > 0
            need(x & z <= y, 'geodesic lost endpoint intersection')
            need(y <= {a ^ b for a in x for b in z}, 'geodesic left endpoint sum')
    return {'planes': 35, 'ordered_triples': 35 ** 3,
            'geodesic_triples': geodesics, 'strict_geodesic_triples': strict}


def peel_controls():
    projectors = [(u, v) for u in range(1, 8) for v in range(1, 8)
                  if (u & v).bit_count() % 2]
    need(len(projectors) == 28, 'rank-one projector inventory')
    matrices = candidates = tight = dirty_tight = 0
    for active in gl4_rows():
        matrices += 1
        current = active + (16, 32)  # arbitrary GL4 active block, one identity spectator
        before = crossing(current)
        for u, v in projectors:
            candidates += 1
            after = right_gate(current, u, v)
            if crossing(after) == before - 1:
                tight += 1
                if (u | v) & 4:
                    dirty_tight += 1
                need(not ((u | v) & 4), 'tight peel used a spectator')
                need(after[-2:] == (16, 32), 'tight peel changed spectator output')
                need(all(row < 16 for row in after[:-2]), 'tight peel read spectator input')
    need(matrices == 20160 and candidates == 564480 and tight > 0,
         'complete GL4 control domain')
    return {'address_dimension': 2, 'active_registers': 2, 'spectator_registers': 1,
            'active_invertible_matrices': matrices, 'rank_one_projectors': 28,
            'peels': candidates, 'tight_peels': tight, 'spectator_tight_peels': dirty_tight}


def boundary_controls():
    identity = (1, 2, 4, 8)
    target = (2, 1, 4, 8)
    dirty_out = right_gate(identity, 3, 1)
    dirty_in = right_gate(identity, 1, 3)
    need(crossing(target) == 1, 'coordinate target control')
    for gate in (dirty_out, dirty_in):
        need(mm(gate, gate) == identity, 'paid gate involution')
        need(crossing(mm(target, gate)) != 0, 'one-sided dirty coupling passed tight peel')
        need(mm(mm(gate, gate), target) == target, 'non-tight restored-scratch control')
    need(crossing(dirty_out) == 1 and dirty_out[-2:] != identity[-2:],
         'changed-endpoint control must violate spectator identity')
    return ['both_projector_sides_required', 'slack_word_can_use_scratch',
            'full_spectator_endpoint_required']


def permutation_controls():
    identity = (0, 1, 2, 3)
    labels = ((1, 0, 2, 3), (0, 2, 1, 3), (0, 1, 3, 2))
    prices = (2, 1, 2)
    comp = lambda a, b: tuple(a[b[i]] for i in range(4))
    best, words, queue = {identity: 0}, {identity: ()}, [(0, identity)]
    while queue:
        cost, old = heapq.heappop(queue)
        if best[old] != cost:
            continue
        for label, price in enumerate(prices):
            new = comp(old, labels[label])
            if cost + price < best.get(new, 1000):
                best[new], words[new] = cost + price, words[old] + (label,)
                heapq.heappush(queue, (cost + price, new))
    targets = tuple(tuple(int(c) - 1 for c in text) for text in ('2143', '3142', '4231', '2143'))
    inv = lambda p: sum(p[i] > p[j] for i in range(4) for j in range(i + 1, 4))
    cuts = [sum(inv(p) for p in targets), sum(p[0] != 0 for p in targets),
            sum(p[3] != 3 for p in targets)]
    need(cuts == [12, 4, 4], 'target cut values')
    allowed = [(a, b, c) for a in range(21) for b in range(21) for c in range(21)
               if 2*a+b+2*c <= 20 and a+b+c >= 12 and a >= 4 and c >= 4]
    need(allowed == [(4, 4, 4)], 'cost-20 count implication')
    direct = []
    for target in targets:
        value = identity
        for label in words[target]:
            value = comp(value, labels[label])
        need(value == target, 'coordinate formal word mismatch')
        direct.append({'target': ''.join(str(x+1) for x in target),
                       'cost': best[target], 'written_labels': [x+1 for x in words[target]]})
    need(sum(item['cost'] for item in direct) == 21, 'direct upper bound')
    for i, s in enumerate(labels):
        positives = {(a, b) for a in range(4) for b in range(a+1, 4)}
        negative = {(s[a], s[b]) for a, b in positives if s[a] > s[b]}
        need(negative == {(i+1, i)}, 'simple label must cross exactly its root pair')
    return {'target_cut_values': cuts, 'cost_at_most_20_counts': allowed,
            'direct_words': direct, 'direct_cost': 21}


def compute():
    return {'scope': 'finite proof controls, not a proof by samples',
            'grassmann': grassmann_controls(), 'tight_peel': peel_controls(),
            'boundaries': boundary_controls(), 'permutations': permutation_controls()}


def validate_finite_dependency():
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    pins = {item['path']: item['sha256'] for item in manifest['files']}
    for item in manifest['files']:
        if item['usage'] == 'input':
            need(hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest() == item['sha256'],
                 'predecessor source mismatch: ' + item['path'])
    previous = ROOT / 'research/s4-mixed-tuple-tight-word-search'
    previous_receipt = json.loads((previous / 'RESULT.json').read_text())
    expectations = previous_receipt['full_replay_expectations']
    receipt = json.loads((HERE / 'finite/REPLAY.json').read_text())
    need(receipt['base'] == manifest['base_commit'], 'replay base mismatch')
    need(len(receipt['records']) == 1, 'one complete independent r4 engine required')
    for record, engine, key in zip(receipt['records'], ('indep',), ('r4_indep',)):
        need(record['engine'] == engine + '.cpp', 'finite engine identity')
        need(record['source_sha256'] == pins[str((previous / record['engine']).relative_to(ROOT))],
             'replay source pin')
        need(record['adapter_sha256'] == hashlib.sha256((HERE / 'compat/bits/stdc++.h').read_bytes()).hexdigest(),
             'header adapter pin')
        need(record['result'] == expectations[key], 'complete r4 exclusion receipt')
        old_run = 'r4_primary' if engine == 'search' else 'r4_independent_engine'
        need(record['run_argv'][1:] == previous_receipt['runs'][old_run]['argv'], 'r4 replay arguments')
        need(record['returncode'] == 0 and record['OMP_NUM_THREADS'] == 1,
             'successful single-thread replay required')
        need(0 < record['elapsed_seconds'] <= record['timeout_seconds'] == 900, 'replay budget')
        for stream in ('stdout', 'stderr'):
            data = (HERE / 'finite' / (engine + '.' + stream)).read_bytes()
            need(hashlib.sha256(data).hexdigest() == record[stream + '_sha256'], 'finite log hash')
        need((HERE / 'finite' / (engine + '.stdout')).read_text().splitlines()[-1] == expectations[key],
             'finite output marker')
    stopped = json.loads((HERE / 'finite/PRIMARY_STOP.json').read_text())
    need(stopped['status'] == 'STOPPED_NOT_A_PASS' and stopped['driver_exit_code'] == 1
         and stopped['processes_absent_after_stop'] is True, 'primary was not a complete replay')
    for stream in ('stdout', 'stderr'):
        data = (HERE / 'finite' / ('search.' + stream)).read_bytes()
        need(hashlib.sha256(data).hexdigest() == stopped[stream + '_sha256'], 'primary stop log hash')
    initial = json.loads((HERE / 'finite/INITIAL_ATTEMPT.json').read_text())
    need(initial['status'] == 'TIMEOUT_NOT_A_PASS' and initial['logs_retained'] is False
         and initial['timeout_seconds'] == 300, 'initial timeout boundary')
    need(initial['timeout_message_sha256'] == hashlib.sha256((HERE / 'finite/search-initial.timeout.txt').read_bytes()).hexdigest(),
         'initial timeout message hash')
    need(initial['source_sha256'] == pins[str((previous / 'search.cpp').relative_to(ROOT))],
         'initial timeout source pin')
    return 1839762


def main():
    nodes = validate_finite_dependency()
    result = compute()
    saved = json.loads((HERE / 'RESULT.json').read_text())
    # Canonical JSON also rejects bool-for-int or list-shape receipt mutations.
    need(json.dumps(result, sort_keys=True) == json.dumps(saved, sort_keys=True), 'proof-control receipt differs')
    print('PASS_S4_SPECTATOR_ELIMINATION controls=564480 arbitrary_workspace=proof '
          'finite_r4_nodes=' + str(nodes) + ' finite_replay=indep_receipt_validated primary=stopped_not_a_pass')


if __name__ == '__main__':
    main()
