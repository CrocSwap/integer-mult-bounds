"""Complete PR2915 routes; original column oracle plus physical I/O observer.

Uses Jose Manuel's unchanged check_routes.one_case and provenance oracle.
Adds schedule substitution, occupied scratch roles, and disjoint native tolls.
"""
from fractions import Fraction as F
from time import perf_counter
from unittest.mock import patch

import bindings
from frames import scheduled_registry, need


def run_case(case, optimized):
    bindings.activate()
    import check_routes as old
    from records import Tape
    from words import BLANK

    class DirtyPool(old.ScratchPool):
        def __init__(self, capacity):
            super().__init__(capacity)
            self.borrowed = []
            for i in range(3):
                lease = self.acquire()
                for bit in (i & 1, 1, 0, 1, (i+1) & 1):
                    lease.append(bit)
                lease.rewind()
                lease.step(1)
                self.borrowed.append((lease, bytes(lease.physical.cells), lease.physical.head))

        def empty(self):
            for lease, data, head in self.borrowed:
                need(bytes(lease.physical.cells) == data and lease.physical.head == head,
                     "occupied scratch bytes and heads restored")
                need(self.live.get(lease.slot) is lease, "occupied lease ownership")
                lease.clear()
            self.borrowed.clear()
            super().empty()

    class CheckedAdapter(old.Adapter):
        def close(self):
            super().close()
            need(not self.high_bank.live, "high numerical bank empty")
            need(all(x == BLANK for w in (*self.high_bank.words, self.high_bank.template)
                     for x in w.tape.cells), "high numerical roles erased")

    counts = dict(reads=0, writes=0, moves=0)
    native = dict(reads=0, writes=0, moves=0, calls=0)
    elapsed = []
    original_route = old.route_packet

    def observed_route(*args, **kwargs):
        methods = {"reads":Tape.read, "writes":Tape.write, "moves":Tape.step}
        def wrap(key):
            def call(*a, **kw):
                counts[key] += 1
                return methods[key](*a, **kw)
            return call
        original_native = old.Ordinary.run
        def observed_native(*a, **kw):
            before = counts.copy()
            result = original_native(*a, **kw)
            for k in counts:
                native[k] += counts[k]-before[k]
            native["calls"] += 1
            return result
        with patch.object(Tape,"read",wrap("reads")), \
             patch.object(Tape,"write",wrap("writes")), \
             patch.object(Tape,"step",wrap("moves")), \
             patch.object(old.Ordinary,"run",observed_native):
            start = perf_counter()
            result = original_route(*args, **kwargs)
            elapsed.append(perf_counter()-start)
            return result

    registry = scheduled_registry(old.Registry) if optimized else old.Registry
    with patch.object(old,"Registry",registry), patch.object(old,"ScratchPool",DirtyPool), \
         patch.object(old,"Adapter",CheckedAdapter), patch.object(old,"route_packet",observed_route):
        result = old.one_case(**case)
    need(native["calls"] == result["calls"]["swaps"], "all complete B1 intervals counted")
    total = sum(counts.values())
    paid_native = sum(native[k] for k in counts)
    need(total >= paid_native, "nonoverlapping paid intervals")
    result.update(physical=counts, native=native, total=total,
                  outside_native=total-paid_native, dirty_roles=3)
    return result, sum(elapsed)


def cases():
    word = (("add",0,1,F(1,2)), ("scale",1,1,F(-2)), ("swap",0,1,F(1)))
    dense = (("add",0,1,F(-4)), ("scale",1,1,F(-1,2)),
             ("add",0,1,F(1,2)), ("add",1,0,F(2)), ("swap",0,1,F(1)))
    return [
        dict(q=3,width=2,low=((1,2),(2,2)),word=(("add",0,1,F(1)),)*9,
             old_prefixes=2,fibre_value=3),
        dict(q=3,width=2,low=((1,2),(2,2)),word=word,old_prefixes=2,fibre_value=3),
        dict(q=5,width=2,low=((1,4),(2,1)),word=word,old_prefixes=1,fibre_value=1),
        dict(q=3,width=1,low=((1,2),(2,2)),word=dense,old_prefixes=2,fibre_value=3),
        dict(q=3,width=3,low=((2,1),(1,1)),word=word,old_prefixes=1,fibre_value=1),
        dict(q=3,width=2,low=((2,1),(1,1)),word=dense,old_prefixes=1,fibre_value=3),
    ]


def run():
    results = []
    for index, case in enumerate(cases()):
        before, _ = run_case(case, False)
        after, _ = run_case(case, True)
        need(before["columns"] == after["columns"], "same complete input")
        need(after["calls"]["swaps"] <= before["calls"]["swaps"], "complete route call bill")
        results.append(dict(case=index, before=before, after=after))
    need(results[0]["after"]["total"] < results[0]["before"]["total"],
         "physical saving on repeated reversed ADD fixture")
    return results
