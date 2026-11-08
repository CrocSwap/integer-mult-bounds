#!/usr/bin/env python3
"""Source-native acceptance using the independent exact trace mechanism."""
from __future__ import annotations

from collections import Counter
from functools import lru_cache
import hashlib
import json

from gauss_trace import adjoint, binary_inverse, equal, require


def canonical(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def transpose(rows: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(sum(((row >> j) & 1) << i for i, row in enumerate(rows)) for j in range(len(rows)))


def span(vectors: list[int] | tuple[int, ...], n: int = 9) -> frozenset[int]:
    out = {0}
    for value in vectors:
        require(type(value) is int and 0 < value < 1 << n and value not in out, 'independent binary frame')
        out |= {x ^ value for x in tuple(out)}
    return frozenset(out)


def extended_columns(vectors: tuple[int, ...], n: int) -> tuple[int, ...]:
    """The source's ordered greedy extension, reimplemented without imports."""
    result, reached = [], {0}
    for value in vectors+tuple(1 << i for i in range(n)):
        if value not in reached:
            result.append(value)
            reached |= {x ^ value for x in tuple(reached)}
    require(len(result) == n and len(reached) == 1 << n, 'complete source frame extension')
    return tuple(result)


def gaussian(rank: int) -> tuple[tuple, ...]:
    return tuple(('C', 1 << i, 1) for i in range(rank))


@lru_cache(maxsize=None)
def frame(vectors: tuple[int, ...], n: int = 9) -> tuple[tuple, ...]:
    span(vectors, n)
    rank = len(vectors)
    if rank == 0:
        return ()
    if rank == n:
        return gaussian(n)
    matrix = transpose(extended_columns(vectors, n))
    inverse_columns = transpose(binary_inverse(matrix))
    quadratic = tuple((1 << i) ^ sum(((a & b).bit_count() % 2) << j
                                   for j, b in enumerate(inverse_columns))
                      for i, a in enumerate(inverse_columns))
    linear = tuple((row >> i) & 1 for i, row in enumerate(quadratic))
    conjugator = (('P', matrix), ('D', quadratic, linear))
    return adjoint(conjugator)+gaussian(rank)+conjugator


def monomial(record: dict) -> tuple[tuple, ...]:
    require(type(record) is dict and set(record) == {'matrix_rows', 'offset', 'quadratic_rows', 'linear_Z4', 'phase'},
            'complete monomial record')
    matrix = tuple(record['matrix_rows'])
    quadratic = tuple(record['quadratic_rows'])
    linear = tuple(record['linear_Z4'])
    require(len(matrix) == len(quadratic) == len(linear) == 9, 'source monomial dimension')
    binary_inverse(matrix)
    return (('D', quadratic, linear), ('P', matrix), ('X', record['offset']), ('phase', record['phase']))


def lowered(record: dict) -> tuple[tuple, ...]:
    require(type(record) is dict and set(record) == {'rank', 'left', 'right'}, 'complete lowered record')
    rank = record['rank']
    require(type(rank) is int and 0 <= rank <= 9, 'source child rank')
    if rank == 0:
        require(record['right'] is None, 'rank-zero right convention')
        return monomial(record['left'])
    return monomial(record['right'])+gaussian(rank)+monomial(record['left'])


def inventory(word: dict) -> tuple[set[tuple[int, int]], list[int], list[tuple[str, int, int]]]:
    main = set(word['live']) | {r+112 for r in word['live']}
    helpers = [r for r in range(word['public']) if r not in main]
    pairs = {(event[2], event[3]) for event in word['program'] if event[0] == 'MOVE'}
    pairs |= {(word['initial'][r], word['final'][r]) for r in helpers}
    adapters = [(kind, r, q) for r, q in zip(word['live'], word['ports'], strict=True)
                for kind in ('input', 'output')]
    return pairs, helpers, adapters


def check_native(word: dict, source_result: dict, candidates: dict, progress=False) -> dict:
    pairs, helpers, adapter_ids = inventory(word)
    require(set(candidates) == {'schema', 'pairs', 'adapters', 'source_word_sha256', 'recipe_payload_sha256'},
            'complete native candidate envelope')
    require(candidates['schema'] == 'selected-native-tensor-closure/1', 'candidate schema')
    require(candidates['source_word_sha256'] == '7834725d9e34ee846a9ccc615221ea81e0201613938afa185d2eda0c9a6c232f',
            'candidate source word binding')
    records = {(a, b): record for a, b, record in candidates['pairs']}
    require(len(records) == len(candidates['pairs']) and set(records) == pairs, 'exact MOVE/helper recipe coverage')
    require(all(set(item) == {'kind', 'role', 'port', 'recipe'} for item in candidates['adapters']),
            'complete main adapter records')
    require([(item['kind'], item['role'], item['port']) for item in candidates['adapters']] == adapter_ids,
            'complete ordered main adapter coverage')
    payload = candidates['pairs']+[item['recipe'] for item in candidates['adapters']]
    digest = hashlib.sha256(canonical(payload)).hexdigest()
    require(digest == source_result['native']['recipe_payload_sha256'] == candidates['recipe_payload_sha256'],
            'full selected recipe payload hash')
    charts = [frame(tuple(vectors)) for vectors in word['frames']]
    max_branches = 0
    traces = []
    for count, (a, b) in enumerate(sorted(pairs)):
        expected = adjoint(charts[a])+charts[b]
        actual = lowered(records[a, b])
        require(records[a, b]['rank'] == abs(len(word['frames'][a])-len(word['frames'][b])), 'paid or helper source rank')
        trace = equal(9, actual, expected, f'frame pair {a}:{b}')
        max_branches = max(max_branches, sum(g[0] == 'C' for g in actual+expected))
        traces.append([a, b, *trace])
        if progress and count % 500 == 0:
            print('trace_pairs', count, len(pairs), flush=True)
    adapters = {}
    for item in candidates['adapters']:
        kind, r, q = item['kind'], item['role'], item['port']
        if kind == 'input':
            expected = (('C', q, -1),)+charts[word['initial'][r]]
        else:
            expected = adjoint(charts[word['final'][r+112]])+(('C', q, -1),)+gaussian(9)
        require(item['recipe']['rank'] == 0, 'ordinary intrinsic adapter')
        actual = lowered(item['recipe'])
        equal(9, actual, expected, f'main {kind} {r}')
        adapters[kind, r] = actual

    # Join the logical endpoint X'=X, Y'=Y+X to all three canonical paths.
    main_paths = 0
    for r, q in zip(word['live'], word['ports'], strict=True):
        ix, iy = word['initial'][r], word['initial'][r+112]
        ox, oy = word['final'][r], word['final'][r+112]
        require(word['frames'][ix] == [q] and word['frames'][iy] == [] and len(word['frames'][ox]) == 9,
                'actual main entrance and full source exit')
        entry, exit_ = adapters['input', r], adapters['output', r]
        d0 = (('C', q, -1),)+gaussian(9)
        paths = [
            (entry+adjoint(charts[ix])+charts[ox], d0, 'source diagonal'),
            (adjoint(charts[iy])+charts[oy]+exit_, d0, 'target diagonal'),
            (entry+adjoint(charts[ix])+charts[oy]+exit_, (('C', q, -1),)+d0, 'positive cross'),
        ]
        for actual, expected, name in paths:
            equal(9, actual, expected, f'local {name} {r}')
            main_paths += 1
        equal(9, (('C', q, 1), ('C', q, 1)), (('X', q),), 'central square absolute phase')

    helper_pairs = {(word['initial'][r], word['final'][r]) for r in helpers}
    helper_profile = Counter()
    for a, b in sorted(helper_pairs):
        rec = records[a, b]
        require(rec['rank'] > 0, 'positive productive helper')
        complete = adjoint(monomial(rec['right']))+adjoint(charts[a])+charts[b]+adjoint(monomial(rec['left']))
        equal(9, complete, gaussian(rec['rank']), f'complete helper normalization {a}:{b}')
    for r in helpers:
        helper_profile[records[word['initial'][r], word['final'][r]]['rank']] += 1
    require(dict(sorted(helper_profile.items())) == {int(k): v for k, v in source_result['native']['helpers'].items()},
            'selected arbitrary helper census')
    return {'distinct_native_pairs': len(pairs), 'distinct_move_pairs': len({(e[2], e[3]) for e in word['program'] if e[0] == 'MOVE'}),
            'main_adapters': len(adapters), 'complete_main_paths': main_paths, 'central_squares': len(word['ports']),
            'helper_normalized_pairs': len(helper_pairs), 'arbitrary_helpers': len(helpers), 'helper_profile': dict(sorted(helper_profile.items())),
            'maximum_closed_trace_branches': max_branches, 'complete_trace_digest': hashlib.sha256(canonical(traces)).hexdigest(),
            'selected_recipe_payload_sha256': digest, 'method': 'exact constrained quadratic Gauss sum; no tableau or distinguished column'}
