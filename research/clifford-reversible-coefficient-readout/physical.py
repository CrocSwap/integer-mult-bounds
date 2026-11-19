"""Local lowering and exact head-motion metering on ten binary tracks."""
from collections import Counter
from dataclasses import dataclass

TRACKS = 10


def loc(logical):
    return TRACKS*(logical//8)+logical%8


def segments(gate):
    """Route distant controls in independent clean tracks, then erase both routes."""
    sites = [w//TRACKS for w in gate]
    if max(sites)-min(sites)<=1:
        return (),gate
    target = sites[-1]
    routes = []
    controls = []
    for i,(w,site) in enumerate(zip(gate[:-1],sites[:-1],strict=True)):
        if site==target:
            controls.append(w)
            continue
        track = 8+i
        routes.append((w,site,target,track))
        controls.append(TRACKS*target+track)
    return tuple(routes),tuple(controls)+(gate[-1],)


def route_gates(route,back):
    w,a,b,t = route
    d = 1 if b>a else -1
    pairs = range(a,b,d)
    if not back:
        yield w,TRACKS*a+t
    for k in reversed(pairs) if back else pairs:
        yield TRACKS*k+t,TRACKS*(k+d)+t
    if back:
        yield w,TRACKS*a+t


def lower(gate):
    routes,middle = segments(gate)
    for route in routes:
        yield from route_gates(route,False)
    yield middle
    for route in reversed(routes):
        yield from route_gates(route,True)


class Meter:
    def __init__(self):
        self.gates = Counter()
        self.moves = 0
        self.head = 0

    def visit(self,first,last):
        self.moves += abs(self.head-first)+abs(last-first)
        self.head=last

    def local(self,g):
        sites = [w//TRACKS for w in g]
        if max(sites)-min(sites)>1 or len(set(g))!=len(g):
            raise ValueError("Invalid local gate")
        self.visit(min(sites),min(sites))
        self.gates[len(g)]+=1

    def run_route(self,route,back):
        _,a,b,_ = route
        lo = a if a<b else a-1
        hi = b-1 if a<b else b
        if back:
            self.visit(hi,lo)
            self.visit(a,a)
        else:
            self.visit(a,a)
            self.visit(lo,hi)
        self.gates[2] += 1+abs(b-a)

    def logical(self,g):
        routes,middle=segments(g)
        for route in routes:
            self.run_route(route,False)
        self.local(middle)
        for route in reversed(routes):
            self.run_route(route,True)
