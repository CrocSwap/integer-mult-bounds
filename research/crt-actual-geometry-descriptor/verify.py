#!/usr/bin/env python3
"""Exact split-axis color obstruction for PR4174's production fixture.

This is a source-bound geometry verifier, not a paid descriptor frontend.
JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from __future__ import annotations

import argparse
import ast
from bisect import bisect_right
import hashlib
from itertools import islice
import json
from pathlib import Path
import sys
import types

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def authenticated_sources():
    manifest = json.loads((PACKAGE / 'SOURCES.json').read_text())
    data = {}
    for row in manifest['files']:
        if row['usage'] == 'input':
            content = (ROOT / row['path']).read_bytes()
            need(hashlib.sha256(content).hexdigest() == row['sha256'],
                 'source SHA256 mismatch: ' + row['path'])
            need(hashlib.sha1(f'blob {len(content)}\0'.encode() + content).hexdigest()
                 == row['git_blob'], 'source blob mismatch')
            data[row['path']] = content
    return data


def load_allocator(data):
    path = 'research/crt-reservoir-placement/allocator.py'
    module = types.ModuleType('crt_geometry_source_allocator')
    module.__file__ = str(ROOT / path)
    sys.modules[module.__name__] = module
    exec(compile(data[path], module.__file__, 'exec'), module.__dict__)
    return module


def production_layout(allocator, data):
    """Execute only the owning fixture's setup, never its production census."""
    path = 'research/crt-reservoir-placement/verify.py'
    tree = ast.parse(data[path], filename=path)
    source = next(node for node in tree.body
                  if isinstance(node, ast.FunctionDef) and node.name == 'production_census')
    setup = []
    for node in source.body:
        need(isinstance(node, ast.Assign), 'unexpected production setup before Layout')
        setup.append(node)
        if any(isinstance(target, ast.Name) and target.id == 'layout'
               for target in node.targets):
            break
    else:
        raise ValueError('source production Layout setup missing')
    namespace = {'allocator': allocator}
    exec(compile(ast.Module(body=setup, type_ignores=[]), path, 'exec'), namespace)
    return namespace['layout']


def physical_axis(axis, d):
    """Independent closed form for the source's 24,23 periodic width word."""
    prefix = lambda n: 47 * (n // 2) + 24 * (n % 2)
    length = prefix(d)
    return length - prefix(axis + 1), length - prefix(axis)


def translated_fragments(interval, swaps):
    """Refine by all boundaries and apply the three exchanges in order."""
    lo, hi = interval
    cuts = sorted({lo, hi} | {v for pair in swaps for block in pair for v in block
                             if lo < v < hi})
    result = []
    for start, stop in zip(cuts, cuts[1:]):
        left, right = start, stop
        for source, destination in swaps:
            if source[0] <= left and right <= source[1]:
                delta = destination[0] - source[0]
            elif destination[0] <= left and right <= destination[1]:
                delta = source[0] - destination[0]
            else:
                delta = 0
            left, right = left + delta, right + delta
        result.append((left, right))
    return result


def positive_distances(first, second):
    """Inclusive intervals of possible absolute integer-point differences."""
    out = []
    for a, b in first:
        for c, d in second:
            lo, hi = a - d + 1, b - c - 1
            if hi >= 1:
                out.append((max(1, lo), hi))
            if lo <= -1:
                out.append((max(1, -hi), -lo))
    return out


def merge(intervals):
    out = []
    for lo, hi in sorted(intervals):
        if out and lo <= out[-1][1] + 1:
            out[-1][1] = max(hi, out[-1][1])
        else:
            out.append([lo, hi])
    return out


def contains_multiple(intervals, period):
    need(period > 0, 'positive color period')
    return any(((lo + period - 1) // period) * period <= hi for lo, hi in intervals)


def rank_in_region(axis, d, level, partition):
    if level == d.bit_length() - 1:
        lo = d // 2 + partition * (d // 4)
        return axis - lo if lo <= axis < lo + d // 4 else None
    lo, width = partition * (d // 2), 1 << level
    if not lo <= axis < lo + d // 2 or axis % width < width // 2:
        return None
    return (axis - lo) // width * (width // 2) + axis % width - width // 2


def verify():
    data = authenticated_sources()
    allocator = load_allocator(data)
    layout = production_layout(allocator, data)
    constants = [layout.d, layout.ell, layout.p, layout.L, layout.G,
                 layout.K, layout.r_max, layout.H]
    need(constants == [65536, 24, 9240576, 1540096, 3072, 196608, 5, 15360],
         'changed owning production layout')
    need(all(physical_axis(i, layout.d) == layout.axis_interval(i)
             for i in range(layout.d)), 'periodic interval formula')
    rows, candidate_axes, exact_pairs = [], set(), 0
    stale_detected = False
    for level in range(1, layout.levels + 1):
        for partition, stream, reservoir in allocator._regions(layout, level):
            active = tuple(islice(stream, layout.r_max))
            prototype = allocator._make_plan(layout, level, partition, 0, active, reservoir)
            # Sources lie in the reservoir; active axes cannot intersect them.
            for cut in prototype.cuts:
                if layout.is_axis_boundary(cut):
                    continue
                axis = bisect_right(layout.prefix, layout.L - cut) - 1
                rank = rank_in_region(axis, layout.d, level, partition)
                if rank is None:
                    continue
                candidate_axes.add(axis)
                batch = rank // layout.r_max
                source_stream = next(s for p, s, _ in allocator._regions(layout, level)
                                     if p == partition)
                active = tuple(islice(source_stream, batch * layout.r_max,
                                      (batch + 1) * layout.r_max))
                need(axis in active, 'rank formula disagrees with owning active stream')
                plan = allocator._make_plan(layout, level, partition, batch, active, reservoir)
                need(plan.cuts == prototype.cuts, 'placement depends on batch unexpectedly')
                own = physical_axis(axis, layout.d)
                need(own[0] < cut < own[1], 'not a strict split-axis cut')
                fragments = {}
                for member in active:
                    original = physical_axis(member, layout.d)
                    images = translated_fragments(original, plan.swaps)
                    owner = [p.image_interval for p in plan.map_interval(*original)]
                    need(images == owner, 'independent sequential interval exchange mismatch')
                    oracle_points = {v for lo, hi in images for v in range(lo, hi)}
                    owner_points = {plan.map_position(v) for v in range(*original)}
                    need(oracle_points == owner_points, 'map_position mismatch')
                    stale_detected |= oracle_points != set(range(*original))
                    fragments[member] = images
                intervals, literal = [], set()
                for other in active:
                    if other == axis:
                        continue
                    intervals += positive_distances(fragments[axis], fragments[other])
                    for x in range(*own):
                        for y in range(*physical_axis(other, layout.d)):
                            literal.add(abs(plan.map_position(x) - plan.map_position(y)))
                            exact_pairs += 1
                cover = merge(intervals)
                need(literal == {v for lo, hi in cover for v in range(lo, hi + 1)},
                     'difference interval coverage is not exact')
                need(not contains_multiple(cover, layout.K),
                     'same-color split-axis pair exists')
                rows.append({'level': level, 'partition': partition, 'batch': batch,
                             'cut': cut, 'split_axis': axis, 'active_axes': list(active),
                             'all_bit_pair_distances': cover})
    need(len(rows) == 26 and candidate_axes == {653, 64228, 64882},
         'split-axis candidate coverage changed')
    need(stale_detected, 'stale-position control did not reach a moved axis')
    # These calibrate interval arithmetic only; they are not invented CRT callers.
    need(contains_multiple([(196607, 196608)], layout.K), 'inclusive endpoint control')
    need(contains_multiple([(196608, 196609)], layout.K), 'lower endpoint control')
    need(not contains_multiple([(1, 196607)], layout.K), 'no-zero-multiple control')
    need(contains_multiple(rows[0]['all_bit_pair_distances'], 1),
         'wrong-color-period control must admit pairs')
    need(positive_distances([(5, 7)], [(1, 3)]) == [(3, 5)],
         'half-open integer interval control')
    return {'scope': 'The exact PR4174 production_census layout only; all levels and '
            'both partitions, every active split-axis target bit and every other '
            'same-batch axis bit. No full-guard filter is needed: no same color exists.',
            'constants': dict(zip(('d', 'ell', 'p', 'L', 'G', 'K', 'r_max', 'H'), constants)),
            'candidate_count': len(rows), 'candidate_split_axes': sorted(candidate_axes),
            'literal_bit_pairs': exact_pairs, 'same_color_pairs': 0, 'candidates': rows,
            'controls': ['independent periodic axis formula', 'owning stream rank coverage',
                         'sequential interval exchange versus map_position/map_interval',
                         'exact inclusive difference cover versus all bit pairs',
                         'stale source positions differ', 'both multiple interval endpoints',
                         'zero excluded', 'wrong period admits pairs', 'half-open endpoints']}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-result', action='store_true')
    args = parser.parse_args()
    result = verify()
    if args.write_result:
        (PACKAGE / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
    else:
        need(result == json.loads((PACKAGE / 'RESULT.json').read_text()), 'frozen result mismatch')
    print('PASS_CRT_PRODUCTION_SPLIT_COLOR_OBSTRUCTION', result['candidate_count'],
          result['literal_bit_pairs'], result['same_color_pairs'])


if __name__ == '__main__':
    main()
