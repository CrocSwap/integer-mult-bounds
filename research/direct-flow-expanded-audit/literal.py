#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Expand the finite compiler's call tree and count its actual records.

This is a counting traversal, not a claimed physical execution schedule.
Small tests visit every raw instance, routing slot, rank-one leaf and child
invocation.  DAG mode evaluates the same repeated call tree by memoization;
it is explicitly distinct from a literal traversal.  Neither mode derives
any returned count from a telescoping or moment identity.
"""
from collections import Counter
import forest


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def build_plan(targets, paid, maximum):
    """Build independently batched local calls with nested divisible widths.

    The returned plain dictionaries can be copied and modified by semantic
    rejection controls.  No source compiler code is imported or executed.
    """
    targets, paid = forest.profile(targets, 'target'), forest.profile(paid, 'paid')
    m = max(targets)
    need(type(maximum) is int and maximum >= 0, 'nonnegative maximum rank')
    need(min(targets) >= 2 and max(paid) < m, 'strict recursive rank contract')
    nodes = []
    for n in range(maximum + 1):
        if n < m:
            nodes.append({'rank': n, 'width': 1, 'base_leaves': n,
                          'replication': 0, 'raw_columns': {},
                          'routing_slots_per_copy': 0, 'children': []})
            continue
        f = forest.forest(targets, paid, n)
        replication = nodes[n - 1]['width']
        width = replication * f['source_count']
        children = []
        for kind, inventory in (('complement', f['sources']), ('exit', f['exits'])):
            for rank, count in inventory.items():
                child_rank = n - rank if kind == 'complement' else rank
                need(0 <= child_rank < n, 'strict child rank descent')
                child_width = nodes[child_rank]['width']
                jobs = replication * count
                need(jobs % child_width == 0, 'whole child batch divisibility')
                children.append({'kind': kind, 'rank': child_rank, 'jobs': jobs,
                                 'width': child_width, 'copies': jobs // child_width})
        nodes.append({'rank': n, 'width': width, 'replication': replication,
                      'source_count': f['source_count'], 'sources': f['sources'],
                      'exits': f['exits'], 'raw_columns': f['units_by_column'],
                      'routing_slots_per_copy': f['routing_slots'], 'children': children})
    return {'ambient': m, 'maximum': maximum, 'nodes': nodes}


def _check_node(plan, n):
    nodes = plan['nodes']
    need(type(n) is int and 0 <= n < len(nodes), 'call rank in plan')
    node = nodes[n]
    need(node['rank'] == n and type(node['width']) is int and node['width'] > 0,
         'uniform node identity and width')
    if n < plan['ambient']:
        need(type(node['base_leaves']) is int and node['base_leaves'] >= 0,
             'base leaves nonnegative integer')
        return node
    a = node['replication']
    need(type(a) is int and a > 0, 'positive batch replication')
    need(all(type(c) is int and c > 0 and type(k) is int and k >= 0
             for c, k in node['raw_columns'].items()), 'raw instance inventory')
    need(type(node['routing_slots_per_copy']) is int and node['routing_slots_per_copy'] >= 0,
         'routing slot inventory')
    for child in node['children']:
        r, copies, jobs = child['rank'], child['copies'], child['jobs']
        need(type(r) is int and 0 <= r < n, 'strict child rank descent')
        need(type(copies) is int and copies >= 0 and type(jobs) is int and jobs >= 0,
             'whole child batch counts')
        need(child['width'] == nodes[r]['width'] and jobs == copies * child['width'],
             'whole child batch divisibility')
    return node


def walk_plan(plan, rank=None, *, mode='literal', max_events=300000):
    """Count a plan either by visiting every record or by exact DAG reuse."""
    if rank is None:
        rank = plan['maximum']
    need(mode in ('literal', 'dag'), 'known traversal mode')
    need(type(max_events) is int and max_events > 0, 'positive traversal budget')
    fields = ('leaves', 'raw_units', 'raw_columns', 'routing_slots', 'uniform_calls', 'zero_calls')

    if mode == 'literal':
        total = Counter({key: 0 for key in fields})
        calls = Counter()
        events = 0

        def emit(kind, value=1):
            nonlocal events
            events += 1
            need(events <= max_events, 'literal expanded-event limit')
            if kind == 'raw':
                total['raw_units'] += 1
                total['raw_columns'] += value
            else:
                total[kind] += 1

        def visit(n):
            node = _check_node(plan, n)
            emit('uniform_calls')
            calls[n] += 1
            if n < plan['ambient']:
                if n == 0:
                    total['zero_calls'] += 1
                for _ in range(node['base_leaves']):
                    emit('leaves')
                return
            for _ in range(node['replication']):
                for column, count in node['raw_columns'].items():
                    for _ in range(count):
                        emit('raw', column)
                for _ in range(node['routing_slots_per_copy']):
                    emit('routing_slots')
            for child in node['children']:
                for _ in range(child['copies']):
                    visit(child['rank'])

        visit(rank)
        total = dict(total)
    else:
        table, call_table = [], []
        for n in range(rank + 1):
            node = _check_node(plan, n)
            row = Counter({key: 0 for key in fields})
            row['uniform_calls'] = 1
            rank_calls = Counter({n: 1})
            if n < plan['ambient']:
                row['leaves'] = node['base_leaves']
                row['zero_calls'] = int(n == 0)
            else:
                a = node['replication']
                row['raw_units'] = a * sum(node['raw_columns'].values())
                row['raw_columns'] = a * sum(c * count for c, count in node['raw_columns'].items())
                row['routing_slots'] = a * node['routing_slots_per_copy']
                for child in node['children']:
                    r, copies = child['rank'], child['copies']
                    for key in fields:
                        row[key] += copies * table[r][key]
                    for child_rank, count in call_table[r].items():
                        rank_calls[child_rank] += copies * count
            table.append(row)
            call_table.append(rank_calls)
        total, calls = dict(table[rank]), call_table[rank]
        events = sum(total[key] for key in ('leaves', 'raw_units', 'routing_slots', 'uniform_calls'))
    return {'rank': rank, 'width': plan['nodes'][rank]['width'], **total,
            'events': events, 'rank_call_counts': dict(sorted(calls.items())), 'mode': mode}


def compile_counts(targets, paid, maximum, *, mode='literal', max_events=300000):
    return walk_plan(build_plan(targets, paid, maximum), mode=mode, max_events=max_events)
