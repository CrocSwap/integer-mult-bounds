#!/usr/bin/env python3
"""Exact scoped corroboration of the frame-code theorem. Apache-2.0.
Charles Bethin, with substantial OpenAI Codex assistance.
Geometry: Jonathan Lam, PR798; order-three construction: GamingPuzzled, PR620.
Frame exact-cover order: Maximooch, PR1794.
"""
import hashlib
import importlib.util
import json
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
import sys
import independent as I

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def load_geometry():
    pins = json.loads((HERE/'SOURCES.json').read_text())
    for item in pins['files']:
        if item['usage'] == 'input':
            actual = hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()
            require(actual == item['sha256'], 'source hash: '+item['path'])
    spec = importlib.util.spec_from_file_location('geometry', ROOT/'research/eisenstein-clique-copy-bound/geometry.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def partition(G, adj):
    orth = [((1<<40)-1) ^ adj[i] ^ (1<<i) for i in range(40)]
    frames = []
    def visit(left):
        if not left:
            return True
        v = min(G.bits(left), key=lambda t: (orth[t] & left).bit_count())
        for a, b, c in combinations(list(G.bits(orth[v] & left)), 3):
            if (orth[a] >> b)&1 and (orth[a] >> c)&1 and (orth[b] >> c)&1:
                f = (1<<v)|(1<<a)|(1<<b)|(1<<c)
                frames.append(f)
                if visit(left & ~f):
                    return True
                frames.pop()
        return False
    require(visit((1<<40)-1), 'orthogonal cover missing')
    return frames


def syndrome(mask, frames):
    for f in frames:
        if mask & (f & -f):
            mask ^= f
    return mask


def census(G, reps, images, frames):
    flats = G.flats(reps, images)
    low = {}
    for mask, basis, _ in flats:
        rank = len(basis)//2
        if rank >= 4:
            continue
        sub = mask
        while sub:
            low.setdefault(sub, rank)
            sub = (sub-1) & mask
    groups = defaultdict(list)
    for mask, rank in low.items():
        groups[syndrome(mask, frames)].append((mask, rank))
    require(0 not in groups, 'proper support in frame code')
    deficits = [sum(4-r for _, r in members) for members in groups.values()]
    require(max(deficits) == 4, 'coset deficit')
    return low, {'flat_count': len(flats), 'support_count': len(low),
                 'rank_counts': dict(sorted(Counter(low.values()).items())),
                 'coset_count': len(groups),
                 'deficit_counts': dict(sorted(Counter(deficits).items())),
                 'maximum_coset_deficit': max(deficits),
                 'maximum_coset_members': max(map(len, groups.values()))}


def witness(G, reps, images, frames):
    terms = [(f, f) for f in frames]
    f = frames[0]
    p = f & -f
    eleven = [(p, f), (f ^ p, f)] + terms[1:]
    def decode(terms):
        rows = [0]*40
        cost = 0
        for r, a in terms:
            for i in G.bits(r):
                rows[i] ^= a
            rb = G.echelon([v for i in G.bits(r) for v in (reps[i], images[i])])
            ab = G.echelon([v for i in G.bits(a) for v in (reps[i], images[i])])
            cost += G.pairing_rank(rb, ab)
        return rows, cost
    ten_rows, ten_cost = decode(terms)
    eleven_rows, eleven_cost = decode(eleven)
    require(ten_rows == eleven_rows and ten_cost == eleven_cost == 40, 'sharp witnesses')
    # Independent coordinate check of the split: ranks 2+6 over Q, hence 1+3.
    lines = list(zip(reps, images))
    split = [len(I.rref([v for i in range(40) if r >> i & 1 for v in lines[i]], 8)[0])//2
             for r in (p, f ^ p)]
    require(split == [1, 3], 'independent split ranks')
    return {'ten_total_charge': ten_cost, 'eleven_total_charge': eleven_cost,
            'eleven_terms': eleven}


def negative_controls(lines, frames, low):
    bad = frames.copy()
    bad[0] = frames[1]
    try:
        I.check_frames(lines, bad)
    except ValueError:
        pass
    else:
        raise ValueError('duplicate-frame control accepted')
    # Same coset, repeated singleton: deficit six > four. This demonstrates
    # why full-column rank/distinctness is essential; it is not an admissible U.
    singleton = frames[0] & -frames[0]
    require(2*(4-low[singleton]) == 6, 'duplicate-support negative control')
    f = frames[0]
    require(syndrome(singleton, frames) == syndrome(f ^ singleton, frames), 'split coset')
    tampered = dict(low)
    tampered[singleton] = 2
    try:
        I.check_complements(lines, frames, tampered)
    except ValueError as exc:
        require('support rank' in str(exc), 'wrong rank-control failure')
    else:
        raise ValueError('rank tampering accepted')
    return ['duplicate frame rejected', 'repeated support violates distinct-coset deficit',
            'tampered support rank rejected', 'full-span charge checked in direct small model']


def main():
    G = load_geometry()
    reps, images, adj, _, _ = G.geometry()
    frames = partition(G, adj)
    lines = list(zip(reps, images))
    I.check_frames(lines, frames)
    low, primary = census(G, reps, images, frames)
    independent_low, independent_coverage = I.independent_supports(lines)
    require(low == independent_low, 'independent complete support coverage')
    independent = I.check_complements(lines, frames, independent_low)
    result = {'frames': frames, 'primary': primary, 'independent_coverage': independent_coverage, 'coordinate_check': independent,
              'direct_factorizations': I.small_factorizations(),
              'sharp_witness': witness(G, reps, images, frames),
              'negative_controls': negative_controls(lines, frames, low)}
    expected = json.loads((HERE/'EXPECTED.json').read_text())
    require(json.loads(json.dumps(result)) == expected, 'receipt mismatch')
    print(json.dumps({'sys_version': sys.version, 'sys_executable': sys.executable,
                      'result': result}, indent=2))
    print('PASS_EISENSTEIN_ELEVEN_TOTAL')


if __name__ == '__main__':
    main()
