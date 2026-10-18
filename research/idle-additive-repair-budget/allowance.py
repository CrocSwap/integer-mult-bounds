"""Independent integer-root checks and excluded-invoice controls.

Prepared by Ross Richardson with substantial OpenAI Codex mathematical-specialist
assistance; adapted from that independent review. Apache-2.0. These endpoint
calculations support, but do not replace, the all-parameter written proof.
"""
from fractions import Fraction as Q


def require(ok, why):
    if not ok:
        raise ValueError(why)


def power(rank):
    scale=10**12
    value=rank**399*scale**400
    lo=0
    hi=1<<((value.bit_length()+399)//400)
    while hi-lo>1:
        mid=(lo+hi)//2
        if mid**400<=value:
            lo=mid
        else:
            hi=mid
    require(lo**400<=value<(lo+1)**400,'integer root enclosure')
    return Q(lo,scale),Q(lo if lo**400==value else lo+1,scale)


def run():
    powers={r:power(r) for r in range(52)}
    unit51=tuple(v/51 for v in powers[51])
    gaps={r:(powers[r][0]-r*unit51[1],powers[r][1]-r*unit51[0]) for r in powers}
    require(all(gaps[19][0]>gaps[r][1] for r in powers if r!=19),'endpoint integer maximizer')
    gain=tuple(20*v for v in gaps[19])
    require(gain[1]<Q(153,160),'endpoint allowance bound')
    controls={
        '22_original_slots':tuple(22*v-1 for v in gaps[19]),
        'half_an_actual_repair_call':tuple(v-Q(1,2) for v in gain),
        'one_repair_shared_by_two_groups':tuple(2*v-1 for v in gain),
        'repair_rank_credited_against_residual_mass':(gain[0]-1+unit51[0],gain[1]-1+unit51[1]),
    }
    require(all(bounds[0]>0 for bounds in controls.values()),'excluded relaxed invoice gain')
    return {'method':'integer-power rational bisection; endpoint a=1/400 only',
            'ranks_checked':[0,51],'integer_gap_maximizer':19,
            'twenty_slot_gain':list(map(str,gain)),
            'positive_relaxed_gain_outside_the_model':{k:list(map(str,v)) for k,v in controls.items()},
            'operator_feasibility_of_excluded_invoice_controls':'not asserted'}
