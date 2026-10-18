#!/usr/bin/env python3
"""Exact shortest unit-shear paths in SL(2,Z), with a separate meet-in-middle.

The optimality claim fixes the signed triangle and exactly one dirt-signature
switch at every nonzero single-visit cube vertex. It is not unrestricted synthesis.
Apache-2.0. conorholds with substantial OpenAI Codex assistance.
"""
from collections import deque
from itertools import permutations, product
import json
from pathlib import Path

IDENTITY = (1, 0, 0, 1)
GENERATORS = tuple(product((0, 1), (-1, 1)))
PAIRS = (((1, 0, 0, 1), (1, -1, 0, 1)),
         ((0, 1, -1, 0), (-1, 1, -1, 0)),
         ((-1, 0, 1, -1), (0, -1, 1, -1)))
HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def step(frame, port, sign):
    a, b, c, d = frame
    return (a + sign*c, b + sign*d, c, d) if port == 0 else (a, b, c + sign*a, d + sign*b)


def ball(radius):
    seen = {IDENTITY: ()}
    pending = deque([IDENTITY])
    while pending:
        frame = pending.popleft()
        word = seen[frame]
        if len(word) == radius:
            continue
        for port, sign in GENERATORS:
            following = step(frame, port, sign)
            if following not in seen:
                seen[following] = word + ((port, sign),)
                pending.append(following)
    return seen


def multiply(a, b):
    return tuple(sum(a[2*i+k]*b[2*k+j] for k in range(2))
                 for i in range(2) for j in range(2))


def inverse(a):
    x, y, z, w = a
    need(x*w-y*z == 1, 'unit determinant required')
    return (w, -y, -z, x)


def independent_half_ball(radius):
    # Enumerate all literal words rather than using BFS deduplication to grow.
    matrices = ((1, -1, 0, 1), (1, 1, 0, 1), (1, 0, -1, 1), (1, 0, 1, 1))
    distances = {IDENTITY: 0}
    for length in range(1, radius + 1):
        for word in product(matrices, repeat=length):
            frame = IDENTITY
            for matrix in word:
                frame = multiply(matrix, frame)
            distances.setdefault(frame, length)
    return distances


def verify():
    radius = 8
    primary = ball(radius)
    halves = independent_half_ball(radius//2)
    frames = {IDENTITY}
    for pair in PAIRS:
        frames.update(pair)
        frames.update(tuple(-x for x in frame) for frame in pair)
    distances = {}
    for start, end in product(sorted(frames), repeat=2):
        relative = multiply(end, inverse(start))
        need(relative in primary, 'declared radius does not cover a frame pair')
        distance = len(primary[relative])
        # relative = right * left, with both factors in the radius-four ball.
        independent = min(halves[left] + halves[right] for left in halves
                          if (right := multiply(relative, inverse(left))) in halves)
        need(distance == independent, 'BFS / literal-half-word disagreement')
        actual = start
        for port, sign in primary[relative]:
            actual = step(actual, port, sign)
        need(actual == end, 'wrong chronological shear path')
        distances[start, end] = distance
    scores = []
    for order in permutations(range(3)):
        for choices in product(range(4), repeat=3):
            endpoints = []
            for phase, choice in zip(order, choices):
                sign = 1 if choice < 2 else -1
                entry = choice % 2
                pair = PAIRS[phase]
                endpoints.append((tuple(sign*x for x in pair[entry]),
                                  tuple(sign*x for x in pair[1-entry])))
            boundaries = [(IDENTITY, endpoints[0][0]),
                          (endpoints[0][1], endpoints[1][0]),
                          (endpoints[1][1], endpoints[2][0]),
                          (endpoints[2][1], IDENTITY)]
            scores.append(sum(distances[edge] for edge in boundaries))
    need(len(scores) == 384 and min(scores) == 7, 'geometry optimum changed')
    # Literal constructor's four, two and one closing shears attain seven.
    need(distances[PAIRS[0][1], PAIRS[1][0]] == 4, 'first closure floor')
    need(distances[PAIRS[1][1], tuple(-x for x in PAIRS[2][1])] == 2, 'second closure floor')
    need(distances[tuple(-x for x in PAIRS[2][0]), IDENTITY] == 1, 'final closure floor')
    bad = (1, 0, 0, -1)
    need(bad not in primary, 'determinant-minus-one frame accepted')
    try:
        inverse(bad)
    except ValueError:
        pass
    else:
        raise ValueError('non-SL2 inverse accepted')
    return {'schema': 'signed-triangle-frames-v1', 'generators': [list(g) for g in GENERATORS],
            'complete_BFS_radius': radius, 'BFS_states': len(primary),
            'independent_half_word_radius': radius//2, 'independent_half_states': len(halves),
            'endpoint_frames': len(frames), 'frame_pairs': len(distances),
            'geometry_cases': len(scores), 'minimum_boundary_transfers': min(scores),
            'total_transfer_formula': 'sum(2^block_size)+4',
            'coefficient_alphabet': 'integer unit shears only; no coordinate/height cutoff',
            'scope': 'Fixed zero-sum triangle; all phase orders/signs/entry signatures, single cube visit and exactly one signature switch per nonzero vertex. Not unrestricted source-walk or frame optimality.'}


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-receipt', action='store_true')
    args = parser.parse_args()
    result = verify()
    path = HERE/'FRAME-RECEIPT.json'
    if args.write_receipt:
        path.write_text(json.dumps(result, indent=2)+'\n')
    else:
        need(json.loads(path.read_text()) == result, 'frame receipt differs')
    print(f"PASS_SIGNED_TRIANGLE_FRAMES cases={result['geometry_cases']} "
          f"pairs={result['frame_pairs']} boundary_min=7 two_engines=checked")


if __name__ == '__main__':
    main()
