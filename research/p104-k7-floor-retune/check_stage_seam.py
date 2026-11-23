"""Replay literal ordinary dispatch and bounded signed bank returns."""
from dataclasses import replace
from fractions import Fraction as Q
from hashlib import sha256
from io import BytesIO
from itertools import product
import json
from pathlib import Path
import sys

RUNTIME = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(RUNTIME))
from upstream import install

install()


class DyadicWidth(int):
    """Speed up exact exponentiation of a mathematically dyadic test width."""
    def __pow__(self, exponent):
        assert self.bit_count() == 1 and exponent >= 0
        return 1 << ((self.bit_length() - 1) * exponent)


def verify_stage(profile, cuts, number, log_width):
    import ordinary_carrier as carrier

    calls = []
    base = DyadicWidth(1 << log_width)
    prev = 1 << cuts[number-2]
    power = 1 << (log_width//250)
    assert log_width % 10000 == 0
    width = max(prev+1, power)
    component = 1 << (39*log_width//10000)
    count = -(-width//component)
    short, longer = divmod(width,count)
    expected_layout = (longer, short+1, count-longer, short)
    rank = 1 << profile.rank_logs[number-1]
    expect_direct = -(-base//width) <= 1 << (8*profile.rank_logs[number-1])

    def root(value, degree):
        assert value.bit_count() == 1
        quotient, remainder = divmod(value.bit_length()-1,degree)
        assert not remainder
        return 1 << quotient

    def receiver(dimension, layout, previous, *, direct, profile):
        assert dimension == rank and layout == expected_layout and direct == expect_direct
        assert previous.func is carrier.ternary
        assert previous.keywords == {"maximum": number-1, "profile": profile}
        return number

    def body(source,target,digits,prefix,gap,suffix,backend):
        assert digits==base and (prefix,gap,suffix)==(1,3,5) and backend==number
        calls.append((digits.bit_length()-1,backend))

    actual = carrier.ceil_root, carrier.Receiver, carrier.root_body
    try:
        carrier.ceil_root, carrier.Receiver, carrier.root_body = root, receiver, body
        carrier.ternary(None,None,base,1,3,5,maximum=number,profile=profile)
    finally:
        carrier.ceil_root, carrier.Receiver, carrier.root_body = actual
    assert calls == [(log_width,number)]
    return {"stage":number,"scanned_log":log_width,"rank_log":rank.bit_length()-1,
            "predecessor_cut":cuts[number-2],"direct":expect_direct,
            "component_log":component.bit_length()-1}


def verify_tape(width, u, v):
    from five_exchange import same_order_line
    from growing_binary import Weighted
    from same_order_body import SameOrderBody
    from streaming_routes import cold_swap_tape
    from ternary_leaf import select_pivot

    class Core(SameOrderBody, Weighted):
        def __init__(self):
            super().__init__(2,(1,width,0,0),cold_swap_tape)
            self.stock=self.owners
            self.calls=0

        def weighted(self,*args,**kwargs):
            assert kwargs["atoms"]==1<self.n
            self.calls+=1
            return super().weighted(*args,**kwargs)

    core = Core()
    modulus=core.modulus
    assert modulus==3**width and core.atom==modulus
    assert sum(a*b for a,b in zip(u,v,strict=True))%modulus==1
    weight=lambda row,j: (2,4)[j]
    inverse = tuple(pow(weight(0,j),-1,modulus) for j in range(2))
    dims = (modulus,)*4

    def dense(sign):
        out=bytearray(len(raw))
        size=modulus**4
        for x0,x1,y0,y1 in product(range(modulus),repeat=4):
            delta=sum(v[j]*(y-inverse[j]*x)
                      for j,(x,y) in enumerate(zip((x0,x1),(y0,y1),strict=True)))%modulus
            target=((x0+sign*2*u[0]*delta)%modulus,(x1+sign*4*u[1]*delta)%modulus,
                    (y0-sign*u[0]*delta)%modulus,(y1-sign*u[1]*delta)%modulus)
            i=((x0*modulus+x1)*modulus+y0)*modulus+y1
            k=0
            for value in target:
                k=k*modulus+value
            assert 0<=k<size
            out[4*k:4*k+4]=raw[4*i:4*i+4]
        return bytes(out)

    raw=b"".join(i.to_bytes(4,"little") for i in range(modulus**4))
    source,destination=BytesIO(raw),BytesIO()
    same_order_line(core,source,destination,pivot=select_pivot(u,v),factors=lambda _: (u,v),
                    f=1,unused=1,heights=1,older=1,gap=1,suffix=4,weight=weight)
    assert source.getvalue()==raw and source.tell()==len(raw)
    assert destination.getvalue()==dense(1)
    assert destination.getvalue()!=dense(-1), "wrong signed return was accepted"
    assert 1<=core.calls<=5
    return {"component_width":width,"modulus":modulus,"records":modulus**4,
            "paid_exchanges":core.calls,"wrong_signed_return_rejected":True}


def check():
    from band_product import prepare_native
    from installations import BINARY_C, GAUSSIAN_C, TERMINAL
    from ordinary_carrier import stage_for_width_log
    from raw_binary_stage import binary_word
    from staged_carriers import entrance_logs

    # Comparator: #8073 at 18960 with the 8/L suffix and debit 11204/8192.
    baseline = replace(TERMINAL, rank_logs=(8192,117168,524288),
                       complex_log=501831,kappa=Q(".003898219753506"))
    assert TERMINAL.rank_logs==(8192,110461,524288) and TERMINAL.kappa==Q(".003898224460300")
    assert TERMINAL.complex_log==511587
    assert TERMINAL.kappa-baseline.kappa==Q(2353397,500000000000000)
    assert max(*TERMINAL.rank_logs,TERMINAL.complex_log)==524288
    assert sha256((RUNTIME/"strong-bit.json.gz").read_bytes()).hexdigest()==(
        "9e7392c52bcf29c0cc58c54c619f95c28f476394c33e8e0a5aa30c9557d31362")
    old,new=prepare_native(baseline),prepare_native(TERMINAL)
    w=binary_word()
    assert old[0] is new[0] and all(recipe.level_floor==4474 for recipe in (*old[:-1],*new[:-1]))
    assert old[-1].targets is new[-1].targets and old[-1].cells is new[-1].cells
    assert (len(w.targets),len(w.paid),len(w.cells))==(18906,104652,24)
    assert all(r.targets is w.targets and r.paid is w.paid and r.cells is w.cells
               for r in (*old[:-1],*new[:-1]))

    def upper(ranks,debit,round_ticks=False):
        rate=Q(0)
        for i,h in enumerate(ranks,1):
            rate=min(TERMINAL.eta,(249*(BINARY_C-debit/h)+rate)/250)
            if round_ticks and i<len(ranks):
                rate=Q((rate*10**21).__floor__()-1,10**21)
        return rate

    booked=TERMINAL.ordinary
    stop=Q(5,10**18)
    debit=Q(1430037,2**20)
    k7_suffix_debit=Q(11204,8192)
    prior_debit=Q(11239,8192)
    historical_debit=Q(1405,1024)

    def positive(height):
        return GAUSSIAN_C-Q(64939,524288*height)

    def capped_shape(height,cap):
        ranks=(8192,(cap-1731-220*height)//320-8192-524288,524288)
        assert 8192<=ranks[1]<=524288
        return ranks

    def integer_optimum(ranks,charged_debit):
        # Relax clamps and ticks for an upper bound. For a distinct feasible
        # integer vector d relative to ranks, alpha*d1+beta*d2+gamma*d3
        # loses at least one positive unit of slope. The true tick loss is
        # smaller, so no distinct competitor reaches this actual ceiling.
        multiplier=Q(249,250)
        weights=(Q(1,62500),Q(1,250),Q(1))
        ideal=upper(ranks,charged_debit)
        assert ideal==multiplier*sum(w*(BINARY_C-charged_debit/h)
                                     for w,h in zip(weights,ranks,strict=True))
        alpha,beta,gamma=(w/h**2 for w,h in zip(weights,ranks,strict=True))
        assert 0<alpha<beta<gamma
        actual=upper(ranks,charged_debit,True)
        tangent_loss=multiplier*charged_debit*min(beta-alpha,gamma-beta,beta)
        assert 0<ideal-actual<tangent_loss
        return actual

    # Preserve the #8070 exact family control and the #8071 fixed profile.
    prior_height=490638
    prior_ranks=(8192,124864,524288)
    assert prior_ranks==capped_shape(prior_height,318292451)
    prior_ordinary=integer_optimum(prior_ranks,historical_debit)
    assert positive(prior_height-1)<prior_ordinary<positive(prior_height)
    prior_family_ceiling=prior_ordinary-stop
    assert prior_family_ceiling==Q(523209442801521766233321100177,134217728000000000000000000000000)

    historical_profile=(8192,124863,524288)
    historical_booked=Q(".00389821412325")+stop
    historical_gaussian=positive(490639)
    assert historical_booked<historical_gaussian<upper(historical_profile,prior_debit,True)
    assert historical_gaussian-stop==Q(6417673946269416969859534601,1646311296204800000000000000000)

    cap=318292011
    # The #8072 comparator, as in #8073.
    p8072=((8192,124649,524288),490950)
    assert p8072[0]==capped_shape(p8072[1],cap)
    ordinary_8072=integer_optimum(p8072[0],prior_debit)
    assert positive(p8072[1]-1)<ordinary_8072<positive(p8072[1])
    assert ordinary_8072-stop==Q(523209464347189355219919950737,134217728000000000000000000000000)

    # #8073 under its own booking is its exact capped family ceiling.
    assert baseline.rank_logs==capped_shape(baseline.complex_log,cap)
    old_ordinary=integer_optimum(baseline.rank_logs,k7_suffix_debit)
    assert positive(baseline.complex_log-1)<baseline.ordinary<old_ordinary<positive(baseline.complex_log)
    assert old_ordinary<booked
    comparator_ceiling=old_ordinary-stop
    assert comparator_ceiling==Q(523210198560303585338978849681,134217728000000000000000000000000)
    assert TERMINAL.kappa-comparator_ceiling>0

    # The two adjacent heights bound the full capped three-stage family.
    height=TERMINAL.complex_log
    ranks=TERMINAL.rank_logs
    assert ranks==capped_shape(height,cap)==capped_shape(height,318291991)
    assert capped_shape(height-1,cap)==(8192,110461,524288)
    assert capped_shape(height+1,cap)==(8192,110460,524288)
    new_ordinary=integer_optimum(ranks,debit)
    new_gaussian=positive(height)
    assert positive(height-1)<booked<new_ordinary<new_gaussian
    family_ceiling=new_ordinary-stop
    assert family_ceiling-TERMINAL.kappa>0
    assert 1731+320*sum(ranks)+220*height==318291991
    underfunded=booked-positive(height-1)
    overfunded=booked-integer_optimum(capped_shape(height+1,cap),debit)
    assert underfunded>0 and overfunded>0
    prior_booking_shortfall=booked-upper(ranks,k7_suffix_debit,True)
    assert prior_booking_shortfall>0

    smaller=Q(".00389821057")+stop-upper((8192,129407,524402),Q(11,8))
    assert smaller==Q(949618999849667259182401851,233169615645211570995200000000000000000)
    historical=Q(".00389821126")+stop-upper((8192,129406,523443),Q(703,512))
    assert historical==Q(131786329075081068292016650499,77580469414725995724800000000000000000)
    prior_gaussian_debit=Q(".0038982141226643")+stop-(GAUSSIAN_C-Q(64944,524288*prior_height))
    assert prior_gaussian_debit==Q(5290830738777425573,274384656793600000000000000000)>0
    historical_ordinary_shortfall=historical_booked-upper(historical_profile,historical_debit,True)
    assert historical_ordinary_shortfall==Q(25132665927681050851,26843545600000000000000000000000)>0
    historical_height_shortfall=historical_booked-positive(prior_height)
    assert historical_height_shortfall==Q(354613496784311279,823153970380800000000000000000)>0

    profiles=[]
    for p,expected in ((baseline,(8290,125522,649874)),(TERMINAL,(8290,118815,643167))):
        cuts=tuple(entrance_logs(p.rank_logs))
        assert cuts==expected
        for i,c in enumerate(cuts,1):
            assert [stage_for_width_log(c+d,3,p.rank_logs) for d in (-1,0,1)]==[i-1,i,i]
            assert stage_for_width_log(c+1,i-1,p.rank_logs)==i-1
        direct=[verify_stage(p,cuts,2,140000),verify_stage(p,cuts,3,670000)]
        compiled=[verify_stage(p,cuts,2,1100000),verify_stage(p,cuts,3,4400000)]
        assert all(s["direct"] for s in direct) and not any(s["direct"] for s in compiled)
        profiles.append({"ranks":p.rank_logs,"cuts":cuts,"direct":direct,"compiled":compiled})
    tape=[verify_tape(1,[0,1],[2,1]),verify_tape(2,[1,7],[3,1])]
    print("PASS_LITERAL_K7_FLOOR_RETUNE",json.dumps(
        {"historical_ordinary_negative_gap":str(historical),"seven_level_negative_gap":str(smaller),
         "historical_gaussian_negative_gap":str(prior_gaussian_debit),
         "historical_debit_shortfall":str(historical_ordinary_shortfall),
         "historical_height_shortfall":str(historical_height_shortfall),
         "lower_adjacent_gaussian_shortfall":str(underfunded),
         "higher_adjacent_ordinary_shortfall":str(overfunded),
         "prior_ordinary_booking_shortfall":str(prior_booking_shortfall),
         "candidate_ordinary_slack":str(new_ordinary-booked),"candidate_gaussian_slack":str(new_gaussian-booked),
         "new_family_ceiling":str(family_ceiling),"comparator_family_ceiling":str(comparator_ceiling),
         "prior_family_ceiling":str(prior_family_ceiling),"stage_seams":profiles,"signed_tape":tape},
        sort_keys=True),flush=True)


if __name__=="__main__":
    check()
