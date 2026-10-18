#!/usr/bin/env python3
"""Source binding and finite controls; Lean compilation is check_lean.py.

Apache-2.0. Prepared for commdata2338 with substantial OpenAI Codex assistance.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections import Counter, defaultdict, deque
from fractions import Fraction
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
WITNESS = 'research/p104-native-channel/inputs/LOWRANK-WITNESS.json'
PIN = '0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def span(vectors):
    out = {0}
    for v in vectors:
        require(type(v) is int and 0 < v < 512, 'invalid binary frame label')
        out |= {x ^ v for x in tuple(out)}
    return frozenset(out)


def dim(space):
    return len(space).bit_length() - 1


def extract(w):
    """Reconstruct every frame and check complete original event coverage."""
    require(set(w) == {'initial_frames', 'final_frames', 'program'}, 'witness schema')
    initial = {r: span(v) for r, v in w['initial_frames'].items()}
    frames = dict(initial)
    all_frames = set(frames.values())
    transports = []
    operations = Counter()
    for i, event in enumerate(w['program']):
        kind = event[0]
        operations[kind] += 1
        if kind == 'transport':
            _, r, before, after, rank = event
            a, b = span(before), span(after)
            require(frames.get(r) == a, f'entrance frame at {i}')
            require(a < b or b < a, f'nonnested transport at {i}')
            require(type(rank) is int and rank == abs(dim(a)-dim(b)), f'rank at {i}')
            transports.append((i, r, a, b, rank))
            frames[r] = b
            all_frames.update((a, b))
        elif kind in ('add', 'copy'):
            if kind == 'add':
                _, dst, src, coefficient, basis = event
                require(Fraction(coefficient) != 0, f'zero ADD at {i}')
            else:
                _, dst, src, basis = event
                require(dst == 'C', 'unexpected private COPY')
            chart = span(basis)
            require(dst != src and frames.get(dst) == frames.get(src) == chart,
                    f'cross-frame uncounted operation at {i}')
        elif kind == 'zero':
            _, r, basis = event
            require(r == 'C' and r not in frames, f'informative or reused initialization at {i}')
            frames[r] = span(basis)
            all_frames.add(frames[r])
        elif kind == 'erase':
            _, r, basis = event
            require(r == 'C' and frames.get(r) == span(basis), f'erasure frame at {i}')
            del frames[r]
        else:
            raise ValueError(f'unknown event {kind}')
    final = {r: span(v) for r, v in w['final_frames'].items()}
    require(frames == final, 'final frames')
    sources = [initial[f'X{i}'] for i in range(104)]
    targets = [final[f'Y{i}'] for i in range(104)]
    removed = [t for t in transports if t[1] == 'C' and dim(t[2]) > dim(t[3])]
    require(len(removed) == 8 and all(t[4] == 7 for t in removed), 'eight private descents')
    cut_ids = {t[0] for t in removed}
    graph = defaultdict(set)
    for i, _, a, b, _ in transports:
        if i not in cut_ids:
            graph[a].add(b)
    reachable = set(sources)
    queue = deque(sources)
    while queue:
        for b in graph[queue.popleft()]:
            if b not in reachable:
                reachable.add(b)
                queue.append(b)
    require(not set(targets) & reachable, 'original source-target separation')
    inward = [i for i, _, a, b, _ in transports if a in reachable and b not in reachable]
    require(inward == sorted(cut_ids), 'crossing inventory')
    return {
        'schema_version': 1,
        'source_sha256': PIN,
        'events': len(w['program']),
        'event_counts': dict(sorted(operations.items())),
        'persistent_registers': len(initial),
        'canonical_frames': len(all_frames),
        'source_side_frames': len(reachable),
        'outside_frames': len(all_frames - reachable),
        'source_arrays': len(sources),
        'target_arrays': len(targets),
        'original_transports': len(transports),
        'original_inward_events': inward,
        'original_inward_native_ranks': [t[4] for t in removed],
        'source_sides': [s in reachable for s in sources],
        'target_sides': [s in reachable for s in targets],
        'transport_sides': [[a in reachable, b in reachable] for _, _, a, b, _ in transports],
    }


def lean_data(receipt):
    """Finite Bool certificate: kernel reduction, never native_decide."""
    boolean = lambda b: 'true' if b else 'false'
    def vec(name, values):
        return f'def {name} : List Bool := [' + ', '.join(map(boolean, values)) + ']\n'
    pairs = ['(' + boolean(a) + ', ' + boolean(b) + ')' for a, b in receipt['transport_sides']]
    chunks = [', '.join(pairs[i:i+12]) for i in range(0, len(pairs), 12)]
    text = '''import Std

/- Source-bound finite premise, regenerated by verify.py from every event.
   true = source-side frame; false = outside. Apache-2.0. -/
set_option maxRecDepth 10000
set_option maxHeartbeats 1000000
namespace SourceCut
'''
    text += vec('sourceSides', receipt['source_sides'])
    text += vec('targetSides', receipt['target_sides'])
    text += 'def transportSides : List (Bool × Bool) := [\n  ' + ',\n  '.join(chunks) + ']\n'
    text += '''
def inwardCount : Nat := (transportSides.filter (fun p => p.1 && !p.2)).length

theorem source_count : sourceSides.length = 104 := by decide
theorem target_count : targetSides.length = 104 := by decide
theorem source_entrances : sourceSides.all id = true := by decide
theorem target_exits : targetSides.all (! ·) = true := by decide
theorem transport_count : transportSides.length = 1410 := by decide
theorem inward_count : inwardCount = 8 := by decide

#print axioms source_count
#print axioms target_count
#print axioms source_entrances
#print axioms target_exits
#print axioms transport_count
#print axioms inward_count
end SourceCut
'''
    return text


def matrix_mul(a, b):
    return [[sum((x*y for x, y in zip(row, col)), Fraction(0))
             for col in zip(*b)] for row in a]


def matrix_add(a, b):
    return [[x+y for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]


def rank(a):
    a = [[Fraction(x) for x in r] for r in a]
    row = 0
    for col in range(len(a[0])):
        pivot = next((k for k in range(row, len(a)) if a[k][col]), None)
        if pivot is None:
            continue
        a[row], a[pivot] = a[pivot], a[row]
        q = a[row][col]
        a[row] = [v/q for v in a[row]]
        for k in range(len(a)):
            if k != row:
                q = a[k][col]
                a[k] = [x-q*y for x, y in zip(a[k], a[row])]
        row += 1
        if row == len(a):
            break
    return row


def finite_controls():
    """Independent direct matrices test feedback, copying and the trust boundary."""
    # Two independent scalar inputs. First crossing transmits a.
    x = [[1, 0], [0, 1]]
    first = [[1, 0], [0, 0]]
    copied = matrix_mul([[1, 0], [7, 0]], first)
    require(rank(copied) == 1, 'copy amplified rank')
    # Free return traffic changes the next source-side read to b+3a.
    inside = matrix_add(x, matrix_mul([[3, 0], [0, 0]], first))
    read = matrix_mul([[0, 1]], inside)
    read = matrix_add(read, matrix_mul([[3, 0]], first))
    transcript = [first[0], read[0]]
    decoder = [[1, 0], [-3, 1]]
    require(matrix_mul(decoder, transcript) == x, 'feedback decoder order')
    require(rank(transcript) == 2, 'two-crossing attainment')
    wrong = [[1, 0], [3, 1]]
    require(matrix_mul(wrong, transcript) != x, 'wrong feedback inverse escaped')
    # Exact counterexamples to omitted model hypotheses, not admitted programs.
    require(rank(x) > 0, 'source-dependent initialization witness')
    require(rank(x) > 1, 'one oversized message witness')
    require(rank(matrix_add(first, [[0, 0], [0, 1]])) > 1,
            'uncounted source-to-target read witness')
    # Two d=2 messages, with genuinely noncommuting ordered block recovery.
    a, ai = [[1, 1], [0, 1]], [[1, -1], [0, 1]]
    b, c, ci = [[1, 0], [1, 1]], [[2, 1], [1, 1]], [[1, -1], [-1, 2]]
    encoded = [row + [0, 0] for row in a] + [b[i]+c[i] for i in range(2)]
    lower = [[-v for v in row] for row in matrix_mul(matrix_mul(ci, b), ai)]
    decoded = [row + [0, 0] for row in ai] + [lower[i]+ci[i] for i in range(2)]
    identity4 = [[int(i == j) for j in range(4)] for i in range(4)]
    require(matrix_mul(decoded, encoded) == identity4, 'ordered d=2 recovery')
    wrong_lower = [[-v for v in row] for row in matrix_mul(matrix_mul(ai, b), ci)]
    wrong_block = [row + [0, 0] for row in ai] + [wrong_lower[i]+ci[i] for i in range(2)]
    require(matrix_mul(wrong_block, encoded) != identity4, 'reordered block decoder escaped')
    require(rank(encoded[:2]) == 2 and rank(encoded) == 4, 'whole-array capacity')
    return {
        'positive': ['copy_rank_one', 'feedback_two_crossings_attain_two', 'ordered_d2_recovery'],
        'rejected_relaxations': ['wrong_feedback_inverse', 'informative_initialization',
                                 'oversized_message', 'uncounted_source_read', 'reordered_block_decoder'],
        'feedback_transcript': [[int(x) for x in r] for r in transcript],
        'feedback_decoder': decoder,
        'block_transcript': encoded,
        'block_decoder': [[int(x) for x in r] for r in decoded],
    }



def source_controls(w):
    mutants = []
    for name, change in [
        ('rank_mismatch', lambda z: z['program'][417].__setitem__(4, 2)),
        ('common_chart_leak', lambda z: z['program'][0].__setitem__(2, 'X0')),
        ('source_chart_corruption', lambda z: z['initial_frames']['X0'].__setitem__(0, 1)),
        ('private_initialization_alias', lambda z: z['program'][2461].__setitem__(1, 'X0')),
    ]:
        z = copy.deepcopy(w)
        change(z)
        try:
            extract(z)
        except (ValueError, KeyError):
            mutants.append(name)
        else:
            raise ValueError(f'source mutation accepted: {name}')
    return mutants


def compute():
    raw = (ROOT / WITNESS).read_bytes()
    require(hashlib.sha256(raw).hexdigest() == PIN, 'immutable witness hash')
    w = json.loads(raw)
    receipt = extract(w)
    receipt['finite_controls'] = finite_controls()
    receipt['source_controls'] = source_controls(w)
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', type=Path, help='exclusively write a candidate receipt')
    parser.add_argument('--emit-lean', type=Path, help='exclusively write the generated finite premise')
    args = parser.parse_args()
    receipt = compute()
    payload = json.dumps(receipt, indent=2) + '\n'
    if args.write:
        with args.write.open('x') as f:
            f.write(payload)
    else:
        require(json.dumps(receipt, sort_keys=True) ==
                json.dumps(json.loads((PACKAGE/'EXPECTED.json').read_text()), sort_keys=True),
                'receipt mismatch')
    generated = lean_data(receipt)
    if args.emit_lean:
        with args.emit_lean.open('x') as f:
            f.write(generated)
    else:
        require(generated == (PACKAGE/'SourceCut.lean').read_text(), 'Lean source binding mismatch')
    print('PASS_TRANSPORT_CUT_BINDING sources=104 crossings=8 transports=1410 controls=12 formal_not_run')


if __name__ == '__main__':
    main()
