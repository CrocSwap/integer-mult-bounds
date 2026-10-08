#!/usr/bin/env python3
"""Exact h24 AMV=I and retained-total support identity, on every coefficient.
Zhihao Chen / Codex; repeats the preserved earlier check without path coupling.
"""
import sys
from pathlib import Path
from collections import defaultdict
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'swapnil-round7/independent/complex-twostage'))
from producer import NStar3
def main():
    assert __debug__
    c=NStar3(24);v=len(c.triples);packed={}
    for n in sorted(c.active):
        if c.args[n]:
            a,b=c.args[n];assert not c.sup[a]&c.sup[b]
            assert c.sup[n]==c.sup[a]|c.sup[b];packed[n]=packed[a]+packed[b]
        else:packed[n]=1<<(8*(n-1))
    terms=defaultdict(list)
    for T,n,cf in c.pieces:terms[T].append((n,cf))
    totals=dict(c.retained);star=packed[totals[('*',)]]
    assert c.sup[totals[('*',)]]==(1<<v)-1
    for i in range(23):
        assert c.sup[totals[('E',i)]]==sum(1<<j for j,T in enumerate(c.triples) if i not in T)
    largest=0
    for j,T in enumerate(c.triples):
        value=sum(cf*packed[n] for n,cf in terms[T])
        if 23 not in T:
            value+=2*star-sum(packed[totals[('E',i)]] for i in T);extra=7
        else:
            value-=19*star;value+=sum(packed[totals[('E',i)]] for i in range(23) if i not in T);extra=19+21+2
        bound=sum(abs(cf) for n,cf in terms[T])+extra;assert bound<256
        assert value==2*(1<<(8*j));largest=max(largest,bound)
    print('PASS exact h24 AMV=I:',v*v,'coefficients; digit bound',largest,'<256')
if __name__=='__main__':main()
