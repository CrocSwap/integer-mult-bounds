"""Enumerate edge multisets rather than counting arbitrary decompositions into flows."""
from collections import Counter
from functools import cache
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import read_word, require, span
from check_prices import price


def main():
    w, _, _, _ = read_word()
    spaces = list(map(span,w['frames']))
    ranks = [len(f) for f in w['frames']]
    interval = {i for i,s in enumerate(spaces) if spaces[278] <= s <= spaces[127]}

    @cache
    def chains(u):
        if u == 127:
            return [(127,)]
        return [(u,)+p for v in interval if spaces[u]<spaces[v] for p in chains(v)]

    paths = chains(278)
    through = [p for p in paths if 288 in p]
    require((len(paths),len(through)) == (933,10),'all interval chains and side pickups')
    edge = {(u,v):i for i,(u,v) in enumerate((u,v) for u in sorted(interval)
                                              for v in sorted(interval) if spaces[u]<spaces[v])}
    grades = [ranks[v]-ranks[u] for u,v in edge]
    def encoded(path):
        return [edge[u,v] for u,v in zip(path,path[1:])]
    plain = [encoded(p) for p in paths]
    side = [encoded(p) for p in through]
    topo = {tuple(sorted(a+b)) for a in plain for b in side}
    profiles = Counter(tuple(sorted(grades[i] for i in t)) for t in topo)
    require(len(topo)==9275 and len(profiles)==43,'distinct feasible networks and profiles')
    require(Counter(map(len,topo)) == dict(enumerate((1,59,498,1668,2741,2510,1346,404,48),3)),
            'distribution by number of paid edges')
    require(all(sum(p)==14 for p in profiles),'minimum total grade')
    best,second = (2,5,7),(1,1,5,7)
    def bound(seq,i):
        return sum(price(g)[i] for g in seq)
    require(profiles[best]==profiles[second]==1 and bound(best,1)<bound(second,0) and
            all(bound(second,1)<bound(k,0) for k in profiles if k not in (best,second)),
            'ranking and attained prices on the complete feasible class')
    print('PASS 933 chains, 10 side chains, 9,275 feasible edge multisets and '
          '43 paid profiles at grade 14; unique cheapest and runner-up.')


if __name__ == '__main__':
    main()
