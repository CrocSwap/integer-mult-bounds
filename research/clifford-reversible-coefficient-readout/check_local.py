"""Replay the fully lowered head program and compare every output and its physical invoice."""
from itertools import product
from pathlib import Path
from random import Random
import json
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from readout import evaluate,toggle
from physical import Meter,TRACKS,lower
from check_values import exact,request


def routes():
    rng=Random(919)
    for _ in range(220):
        sites=rng.randrange(3,81)
        k=rng.randrange(1,4)
        wires=rng.sample([TRACKS*s+t for s in range(sites) for t in range(8)],k)
        short=Meter()
        full=Meter()
        head=rng.randrange(sites)
        short.head=full.head=head
        short.logical(wires)
        for g in lower(wires):
            full.local(g)
        if (short.head,short.moves,short.gates)!=(full.head,full.moves,full.gates):
            raise ValueError("Route receipt mismatch")
        for values in product(range(2),repeat=k):
            a=bytearray(TRACKS*sites)
            for i,w in enumerate(wires):
                a[w]=values[i]
            b=a.copy()
            for g in lower(wires):
                toggle(g,a)
            toggle(wires,b)
            if a!=b:
                raise ValueError("Ancilla not restored or routed gate incorrect")


def main():
    routes()
    req=json.loads((HERE/'example.json').read_text())
    receipt=evaluate(req,literal=True)
    if receipt!=evaluate(req):
        raise ValueError("Head and gate counts differ between replay modes")
    want=[round(v*(1<<req['precision'])) for v in exact(req)]
    if receipt['grid_integers']!=want or receipt!=dict(grid_integers=[0,-1701],precision=48,
            sites=458,not_gates=97574,cnot_gates=849046,toffoli_gates=171478,head_moves=1353992):
        raise ValueError(receipt)
    terms=[exact(dict(req,terms=[v])) for v in req['terms']]
    if [sum(round(v[i]*(1<<48)) for v in terms) for i in (0,1)]==want:
        raise ValueError("Missing early-rounding negative control")
    rng=Random(8207)
    for m,p in [(1,0),(2,10),(3,19),(2,37)]:
        req=request(rng,m)
        req['precision']=p
        actual=evaluate(req)
        if actual['grid_integers'] != [round(v*(1<<p)) for v in exact(req)]:
            raise ValueError(("Precision",p))
    print("PASS lowered gates and home-to-home motion, clean inputs/output signs, coarser and finer precision.")
    print(json.dumps(receipt,sort_keys=True))


if __name__=='__main__':
    main()
