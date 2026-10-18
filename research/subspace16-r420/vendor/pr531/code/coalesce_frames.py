"""Raise gate frames inside their two successors to coalesce paid climbs.

The scalar operations, register inventory, helper entrance frames, A/B cut,
center frames, target levels, and cleanup coefficients remain fixed.  Every
accepted move is a monotone frame promotion, checked on both incident
register chains.  This is a local entropy-fee descent, not an optimality proof.
"""
import argparse
import copy
import gzip
import hashlib
import json
import math
import time
from collections import Counter
from functools import lru_cache
from pathlib import Path


def basis(vectors):
    b = {}
    for x in vectors:
        for p in sorted(b, reverse=True):
            if x >> p & 1:
                x ^= b[p]
        if x:
            p = x.bit_length() - 1
            for q in b:
                if b[q] >> p & 1:
                    b[q] ^= x
            b[p] = x
    return tuple(b[p] for p in sorted(b, reverse=True))


@lru_cache(None)
def span(F):
    s = {0}
    for x in F:
        s |= {y ^ x for y in s}
    return frozenset(s)


@lru_cache(None)
def intersection(F, G):
    return basis(span(F) & span(G))


def contained(F, G):
    return basis(F + G) == G


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--word', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--coupled-seconds', type=float, default=0,
                    help='Optional bounded prefix search with successor propagation.')
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=False)
    source = a.word.read_bytes()
    w = json.loads(gzip.decompress(source))
    before = copy.deepcopy(w)
    V, R, h = len(w['ports']), w['report']['R'], w['report']['h']
    m = w['report'].get('m', 8*h+1)
    FULL = basis([1 << i for i in range(h)])
    hyper = lambda p: basis([x for x in range(1, 1 << h) if not (x & p).bit_count() % 2])
    n = 2*V+R
    starts = [(p,) for p in w['ports']] + [()]*(V+R)
    for r, F in w.get('start_extra', {}).items():
        starts[int(r)] = basis(F)
    levels = {int(t): basis(F) for t, F in w.get('target_levels', {}).items()}
    nodes = []
    chains = [[] for _ in range(n)]

    def node(regs, F, section=None, index=None):
        k = len(nodes)
        nodes.append(dict(regs=list(regs), F=basis(F), section=section, index=index))
        for r in regs:
            chains[r].append(k)
        return k

    initial = [node([r], F) for r, F in enumerate(starts)]
    mutable = []
    for section in ('A', 'B'):
        if section == 'B':
            for r, F in zip(w['centers'], w['center_frames']):
                node([r], F, 'center_barrier')
            for t in range(V):
                node([V+t], levels.get(t, ()), 'target_barrier')
        for i, e in enumerate(w[section]):
            regs = e[1:3] if e[0] == 'add' else e[1:2]
            mutable.append(node(regs, e[-1], section, i))
    for r in range(n):
        node([r], hyper(w['ports'][r-V]) if V <= r < 2*V else FULL, 'final')
    prev = {}; nxt = {}
    for r, chain in enumerate(chains):
        for x, y in zip(chain, chain[1:]):
            nxt[x, r] = y
            prev[y, r] = x

    def profile():
        H = Counter()
        for r, chain in enumerate(chains):
            for x, y in zip(chain, chain[1:]):
                F, G = nodes[x]['F'], nodes[y]['F']
                assert contained(F, G), ('frame violation', r, x, y, F, G)
                if nodes[y]['section'] in ('center_barrier', 'target_barrier'):
                    assert F == G, ('changed cut frame', r, F, G)
                if len(G) > len(F):
                    H[len(G)-len(F)] += 1
        for r, F in zip(w['centers'], w['center_frames']):
            served = sorted({levels.get(e[1]-V, ()) for e in w['cut'] if e[2] == r}, key=lambda G: -len(G))
            F = basis(F)
            for G in served:
                assert contained(G, F)
                if len(F) > len(G):
                    H[len(F)-len(G)] += 1
                F = G
        return H

    H0 = profile()
    expected = Counter({int(r): z for r, z in w['report']['local_profile'].items()})
    assert H0 == expected, ('input profile disagreement', H0, expected)
    fee = lambda H: sum(r*z*math.log(m/r) for r, z in H.items())
    moves = []
    passes = 0
    while True:
        changed = 0
        passes += 1
        for k in reversed(mutable):
            z = nodes[k]
            F = z['F']
            G = FULL
            for r in z['regs']:
                G = intersection(G, nodes[nxt[k, r]]['F'])
            assert contained(F, G)
            if F == G:
                continue
            dh = Counter()
            for r in z['regs']:
                p = len(nodes[prev[k, r]]['F'])
                q = len(nodes[nxt[k, r]]['F'])
                for d, count in ((len(F)-p,-1),(q-len(F),-1),(len(G)-p,1),(q-len(G),1)):
                    if d:
                        dh[d] += count
            dh = Counter({r: z for r, z in dh.items() if z})
            delta = fee(dh)
            if not dh or delta < -1e-9:
                moves.append(dict(section=z['section'], index=z['index'], old_frame=list(F),
                                  new_frame=list(G), profile_delta=dict(sorted(dh.items())),
                                  local_entropy_delta=delta, pass_number=passes))
                z['F'] = G
                changed += 1
        if not changed:
            break
    coupled_attempts = 0
    coupled_groups = 0
    if a.coupled_seconds > 0:
        deadline = time.monotonic() + a.coupled_seconds
        native_start = next((i for i,e in enumerate(w['A'])
                             if any(r < V for r in (e[1:3] if e[0]=='add' else e[1:2]))), len(w['A']))
        prefix = [k for k in mutable if nodes[k]['section']=='A' and nodes[k]['index'] < native_start]

        def closure(k, G):
            lifted = {}
            queue = [(k,G)]
            while queue:
                j, want = queue.pop()
                old = lifted.get(j, nodes[j]['F'])
                new = basis(old + want)
                if new == old:
                    continue
                if nodes[j]['section'] not in ('A','B'):
                    return None
                lifted[j] = new
                for r in nodes[j]['regs']:
                    q = nxt[j,r]
                    if not contained(new,lifted.get(q,nodes[q]['F'])):
                        queue.append((q,new))
            return lifted

        def profile_delta(lifted):
            edges = set()
            for j in lifted:
                for r in nodes[j]['regs']:
                    edges.add((prev[j,r],j))
                    edges.add((j,nxt[j,r]))
            # The same gate pair can be consecutive on two registers.  The
            # register identity must remain part of the edge multiplicity.
            edges = {(prev[j,r],j,r) for j in lifted for r in nodes[j]['regs']} | \
                    {(j,nxt[j,r],r) for j in lifted for r in nodes[j]['regs']}
            dh = Counter()
            for p,q,r in edges:
                old = len(nodes[q]['F'])-len(nodes[p]['F'])
                new = len(lifted.get(q,nodes[q]['F']))-len(lifted.get(p,nodes[p]['F']))
                if old: dh[old] -= 1
                if new: dh[new] += 1
            return Counter({r:z for r,z in dh.items() if z})

        repeat = True
        while repeat and time.monotonic() < deadline:
            repeat = False
            for k in reversed(prefix):
                if time.monotonic() >= deadline:
                    break
                F = nodes[k]['F']
                options = []
                for r in nodes[k]['regs']:
                    opts = [];j = nxt[k,r];steps=0
                    while True:
                        G = nodes[j]['F']
                        if G not in opts: opts.append(G)
                        if len(opts)>=4 or len(G)>=4 or (j,r) not in nxt or steps>=128:
                            break
                        j=nxt[j,r];steps+=1
                    options.append(opts)
                candidates = set(options[0]) if len(options)==1 else \
                    {intersection(F1,F2) for F1 in options[0] for F2 in options[1]}
                best = None
                for G in sorted(candidates,key=lambda E:(len(E),E)):
                    if not len(F)<len(G)<=min(4,len(F)+3):
                        continue
                    coupled_attempts += 1
                    lifted = closure(k,G)
                    if not lifted:
                        continue
                    dh = profile_delta(lifted)
                    delta = fee(dh)
                    if delta < -1e-9 and (best is None or delta < best[0]):
                        best = (delta,lifted,dh)
                if best is None:
                    continue
                delta,lifted,dh = best
                coupled_groups += 1
                for j,G in sorted(lifted.items()):
                    z=nodes[j]
                    moves.append(dict(section=z['section'],index=z['index'],old_frame=list(z['F']),
                                      new_frame=list(G),coupled_group=coupled_groups,
                                      group_entropy_delta=delta,group_profile_delta=dict(sorted(dh.items()))))
                    z['F']=G
                repeat = True
    H1 = profile()
    for k in mutable:
        z = nodes[k]
        w[z['section']][z['index']][-1] = list(z['F'])
    for section in ('A', 'B'):
        assert [e[:-1] for e in w[section]] == [e[:-1] for e in before[section]]
    for key in ('ports','cut','cleanup','precondition','centers','center_frames','scatter','start_extra','target_levels'):
        assert w.get(key) == before.get(key)
    assert sum(r*z for r,z in H0.items()) == sum(r*z for r,z in H1.items())
    w['report']['local_profile'] = dict(sorted(H1.items()))
    w['report']['status'] = 'FRAME_COALESCED_SCALAR_WORD_UNCHANGED'
    w['report']['frame_coalescing'] = dict(moves=len(moves), passes=passes,
        local_entropy_before=fee(H0), local_entropy_after=fee(H1))
    encoded = json.dumps(w,sort_keys=True,separators=(',',':')).encode()
    (a.out/'FULL-WORD.json.gz').write_bytes(gzip.compress(encoded,mtime=0))
    receipt = dict(status='EXACT_MONOTONE_FRAME_PROMOTIONS',input_sha256=hashlib.sha256(source).hexdigest(),
        input_word=str(a.word),v=V,R=R,local_profile_before=dict(sorted(H0.items())),
        local_profile_after=dict(sorted(H1.items())),local_entropy_before=fee(H0),local_entropy_after=fee(H1),
        local_entropy_saving=fee(H0)-fee(H1),moves=len(moves),passes=passes,trace=moves,
        coupled_attempts=coupled_attempts,coupled_groups=coupled_groups,
        scalar_operations_unchanged=True,center_and_target_cut_frames_unchanged=True,
        helper_entrance_and_exit_frames_unchanged=True,
        limitation='Local entropy descent only. No global hosting or newly introduced Clifford phase recipe is certified here.')
    (a.out/'COALESCING.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:receipt[k] for k in ('status','R','local_profile_after','moves','passes','local_entropy_saving')},sort_keys=True))


if __name__ == '__main__':
    main()
