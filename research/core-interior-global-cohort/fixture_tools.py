"""Finite certified metadata folding, solely for bounded physical witnesses.

Same exact finite specialization as the published global caller's verifier.
Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
"""
from contextlib import contextmanager
from unittest.mock import patch
from cohort_sources import need


@contextmanager
def certified_floors(bases):
    import active_plan,composed_plan
    from cardinal_counts import Count
    from encoded import compare
    from router_metadata import owned
    table = {}
    for a,b in ((997,1000),(1,500)):
        for n in sorted(set(bases)):
            target,lo,hi = n**a,0,n+1
            while hi-lo > 1:
                mid = (lo+hi)//2
                if mid**b <= target:
                    lo = mid
                else:
                    hi = mid
            need(lo**b <= target < (lo+1)**b,'exact finite metadata floor')
            table[a,b,n] = lo
    calls,misses = [],[]
    original_a,original_c = active_plan.floor_power,composed_plan.floor_power
    def dispatch(value,a,b,original):
        for n in sorted(set(bases)):
            if (a,b,n) in table:
                with owned(Count.literal(n)) as (candidate,):
                    if compare(value,candidate) == 0:
                        calls.append((a,b,n))
                        return Count.literal(table[a,b,n])
        misses.append((a,b))
        return original(value,a,b)
    with patch.object(active_plan,'floor_power',lambda x,a,b:dispatch(x,a,b,original_a)), \
         patch.object(composed_plan,'floor_power',lambda x,a,b:dispatch(x,a,b,original_c)):
        yield table,calls,misses
