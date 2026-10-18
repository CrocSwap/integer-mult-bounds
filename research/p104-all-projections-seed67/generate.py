#!/usr/bin/env python3
"""Independent exhaustive finite P104 support projection census (stdlib only).

The source supports are a frozen data pin from PR1125 CERTIFICATE.json,
blob SHA 9a2cd574df48361579167e39aa6198f39059f70c.
"""
import itertools
from collections import Counter, defaultdict

SOURCE_SUPPORTS = (
    3,5,7,10,11,12,13,14,17,19,21,23,27,29,34,35,39,42,43,46,48,49,50,53,58,61,62,63,68,69,71,76,77,78,80,81,83,84,91,92,94,95,103,110,112,113,114,116,118,119,122,124,136,138,139,140,141,142,155,157,160,162,163,167,168,172,173,175,176,177,178,181,184,185,187,188,192,196,197,199,200,202,203,207,208,209,211,212,216,217,218,221,224,226,227,228,229,230,232,238,243,245,250,252
)


def cube_supports():
    """Build supports independently from the cube's adjacency, not the PR enumerator."""
    adj = [sum(1 << (v ^ (1 << k)) for k in range(3)) for v in range(8)]
    result = []
    by_size = Counter()
    for mask in range(1, 256):
        n = mask.bit_count()
        if n < 2 or n > 6:
            continue
        if n == 6:
            # complement of exactly one cube edge
            rem = 255 ^ mask
            if rem.bit_count() != 2:
                continue
            a = (rem & -rem).bit_length() - 1
            if not (adj[a] & rem):
                continue
        else:
            # A subset is an induced tree iff connected and edge count=n-1
            visited = 0
            pending = mask & -mask
            while pending:
                bit = pending & -pending
                pending ^= bit
                if visited & bit:
                    continue
                visited |= bit
                v = bit.bit_length() - 1
                pending |= adj[v] & mask & ~visited
            if visited != mask:
                continue
            edges = sum((adj[v] & mask).bit_count() for v in range(8) if mask >> v & 1) // 2
            if edges != n - 1:
                continue
        by_size[n] += 1
        result.append(mask)
    assert by_size == {2:12,3:24,4:32,5:24,6:12},by_size
    assert tuple(result) == SOURCE_SUPPORTS, (set(result) - set(SOURCE_SUPPORTS),set(SOURCE_SUPPORTS)-set(result))
    return result


def width_certificate(supports):
    """Prove width by both antichain (lower) and chain partition (upper)."""
    nodes = sorted(set(supports))
    n = len(nodes)
    edges = [[j for j,b in enumerate(nodes) if a != b and a & b == a] for a in nodes]
    match_right = [-1] * n
    def augment(i, visited):
        for j in edges[i]:
            if j in visited: continue
            visited.add(j)
            if match_right[j] < 0 or augment(match_right[j],visited):
                match_right[j] = i
                return True
        return False
    for i in range(n):
        augment(i,set())
    match_left = [-1]*n
    for j,i in enumerate(match_right):
        if i>=0: match_left[i] = j
    unmatched_left = [i for i in range(n) if match_left[i]<0]
    # Minimum vertex-cover dual provides a maximum antichain.
    ZL = set(unmatched_left)
    ZR = set()
    stack = unmatched_left[:]
    while stack:
        i = stack.pop()
        for j in edges[i]:
            if match_left[i] == j or j in ZR: continue
            ZR.add(j)
            h = match_right[j]
            if h>=0 and h not in ZL:
                ZL.add(h)
                stack.append(h)
    antichain = [nodes[i] for i in range(n) if i in ZL and i not in ZR]
    # Chain cover follows matched arcs, each chain strictly increasing.
    starts = [j for j in range(n) if match_right[j]<0]
    chains = []
    for root in starts:
        chain = []
        i=root
        while i>=0:
            chain.append(nodes[i]);i=match_left[i]
        chains.append(chain)
    flat=[v for chain in chains for v in chain]
    assert sorted(flat)==nodes
    assert all(a != b and a & b == a for c in chains for a,b in zip(c,c[1:]))
    assert all((a & b != a and a & b != b) for a,b in itertools.combinations(antichain,2))
    assert len(antichain)==len(chains)==n-sum(x>=0 for x in match_right)
    return {'width':len(chains),'antichain':antichain,'chains':chains,'members':n}


def cube_autos():
    autos = []
    for axes in itertools.permutations(range(3)):
        for flip in range(8):
            transform = []
            for v in range(8):
                w=flip
                for j,axis in enumerate(axes): w ^= ((v>>j)&1) << axis
                transform.append(w)
            autos.append(tuple(transform))
    assert len(set(autos))==48
    return autos


def apply_perm(mask,p):
    out=0
    for i,j in enumerate(p):
        if mask>>i & 1: out |= 1<<j
    return out


def build_certificate():
    source = cube_supports()
    autos = cube_autos()
    results = {}
    for K in range(1, 256):
        family = [s & K for s in source if s & K]
        results[K] = width_certificate(family)
    orbits = {}
    for K in range(1, 256):
        representative = min(apply_perm(K,p) for p in autos)
        assert results[K]['width'] == results[representative]['width']
        orbits.setdefault(representative, []).append(K)
    certificate = {
        'schema': 'p104-projection-widths-v1',
        'upstream_base_commit': 'ba82555c64e1879e4b7decce28186f208fcb8262',
        'audited_pr': 1125,
        'audited_head_commit': '9f7c0679d64bab954b7161d8586dc626a59b92ee',
        'audited_blob': '9a2cd574df48361579167e39aa6198f39059f70c',
        'assignment_seed': 67,
        'support_masks': source,
        'orbits': [
            {'representative': rep, 'members': members,
             'width': results[rep]['width'],
             'antichain': results[rep]['antichain'],
             'chains': results[rep]['chains']}
            for rep,members in sorted(orbits.items(), key=lambda z:(-z[0].bit_count(),z[0]))
        ]
    }
    return certificate, results


def main():
    import json
    from pathlib import Path
    certificate, results = build_certificate()
    out = Path(__file__).with_name('CERTIFICATE.json')
    out.write_text(json.dumps(certificate,indent=2,sort_keys=True)+'\n', encoding='utf-8')
    print('GENERATED',out.name,'orbits',len(certificate['orbits']),'subsets',len(results))
    for q in range(8):
        d = Counter(v['width'] for K,v in results.items() if 8-K.bit_count()==q)
        print('q=',q, 'widths=',dict(sorted(d.items())))

if __name__=='__main__':main()
