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
    sys.path.append(str(Path(__file__).resolve().parent.parent/"tiered-native-multiplier"/"source"))
    from activation import resource_receipt
    from band_product import prepare_native
    from installations import ENTRY, TERMINAL, BINARY_C, GAUSSIAN_C, activation
    from outer_budget import qualify
    from raw_binary_stage import binary_word
    from staged_carriers import entrance_logs

    # GAMED: this profile lifts the self-imposed recurring cap 318292011.
    ORDINARY=Q(1420718,2**20)       # floor retune + child tariff + no 256/255
    GAUSSIAN=Q(1039017,2**23)
    STOP=Q(1,10**18)
    TOTAL=427339440
    PREMIUM=746
    ranks=tuple(TERMINAL.rank_logs)
    assert ranks==(8192,36093,570250) and TERMINAL.complex_log==1048575==2**20-1
    assert TERMINAL.kappa==Q(".003898348449639")

    def ordinary_upper(heights,debit=ORDINARY):
        r=Q(0)
        for i,h in enumerate(heights):
            u=min(TERMINAL.eta,(249*(BINARY_C-debit/h)+r)/250)
            r=u if i==len(heights)-1 else Q((u*10**21).__floor__()-1,10**21)
        return r

    def gaussian_upper(h):
        return GAUSSIAN_C-GAUSSIAN/h

    def rejected(function,label):
        try:
            function()
        except (AssertionError,ArithmeticError,ValueError):
            return label
        raise AssertionError(f"Negative control {label} was not rejected")

    paid=TERMINAL.kappa+5*STOP
    assert TERMINAL.ordinary==paid
    assert ordinary_upper(ranks)>paid and gaussian_upper(TERMINAL.complex_log)>paid
    # The largest 20-bit Gaussian height: the stated install is the 15-digit floor of its rate.
    assert TERMINAL.kappa<=gaussian_upper(2**20-1)-5*STOP<TERMINAL.kappa+Q(1,10**15)
    assert all(8192<=h<2**20 for h in ranks) and 1024<=TERMINAL.complex_log<2**20
    assert TERMINAL.eta==Q(39,10000) and TERMINAL.eta*8192-1>30
    assert 2660000*(30+2)<2**30 and 17**16*10**(21*16)<2**1182

    stock=resource_receipt(TERMINAL)
    cuts=tuple(stock["binary_cuts"])
    assert tuple(entrance_logs(ranks))==cuts
    assert all(cuts[i-1]+2<ranks[i] for i in range(1,len(ranks)))
    assert activation(TERMINAL)==stock["public_exponent_A"]
    assert stock["retimed_first_stripe_margin"]>1024 and stock["retimed_all_size_margin_floor"]>1024
    signed=qualify(TERMINAL.kappa,STOP,paid,gaussian_upper(TERMINAL.complex_log))
    assert (signed["strict"],signed["functional"])==(54,4)
    logB=128+3*len(ranks)+320*sum(ranks)
    late=1602+220*TERMINAL.complex_log+logB
    conversion=((TERMINAL.kappa-ENTRY.kappa)*activation(TERMINAL)).__ceil__()
    assert conversion==PREMIUM
    assert 1+max(125660246+conversion,late)==TOTAL
    assert TOTAL>318292011

    h1,h2,h3=ranks
    def require_funding(proposed,gaussian):
        if ordinary_upper(proposed)<=paid or gaussian_upper(gaussian)<=paid:
            raise ArithmeticError("Profile does not fund the terminal price")
    def require_budget(cap):
        if 1+max(125660246+conversion,late)>cap:
            raise ArithmeticError("The full recurring invoice exceeds the declared cap")
    capped=((8192,101729,524288),524288)
    controls=[
        rejected(lambda:require_funding((h1,h2-1,h3),TERMINAL.complex_log),"second-ordinary-height-minus-one"),
        rejected(lambda:require_funding((h1,h2,h3-1),TERMINAL.complex_log),"third-ordinary-height-minus-one"),
        rejected(lambda:require_funding(*capped),"capped-combined-profile-at-new-rate"),
        rejected(lambda:require_funding(ranks,TERMINAL.complex_log-1),"gaussian-height-minus-one"),
        rejected(lambda:require_funding(ranks,TERMINAL.complex_log) or require_budget(318292011),"inherited-cap-318292011"),
        rejected(lambda:qualify(TERMINAL.kappa,STOP,paid-STOP,gaussian_upper(TERMINAL.complex_log)),"outer-ordinary-margin-removed"),
        rejected(lambda:resource_receipt(replace(TERMINAL,rank_logs=(h1,cuts[0]+2,h3))),"prefix-height-at-previous-cut"),
        rejected(lambda:require_budget(TOTAL-1),"recurring-bound-minus-one"),
    ]
    # A 21-bit Gaussian height would need a fresh setup census.
    assert (2**20).bit_length()==21

    # Economical ordinary heights: Cauchy relaxation (as in #8078), our debit.
    m=sum(ranks)-1; hmin=8192; w1=Q(1,62500)
    r=Q(6324555320336758663997787088865437067439,10**41)
    assert r*r<Q(1,250)<(r+Q(1,10**41))**2
    assert w1/hmin**2<(1+r)**2/(m-hmin)**2
    relaxed=BINARY_C*(1-Q(1,250**3))-Q(249,250)*ORDINARY*(w1/hmin+(1+r)**2/(m-hmin))
    assert relaxed<paid

    assert sha256((RUNTIME/"strong-bit.json.gz").read_bytes()).hexdigest()==(
        "9e7392c52bcf29c0cc58c54c619f95c28f476394c33e8e0a5aa30c9557d31362")
    old=replace(TERMINAL,rank_logs=capped[0],complex_log=capped[1],kappa=Q(".003898230327195"))
    old_native,new_native=prepare_native(old),prepare_native(TERMINAL)
    word=binary_word()
    assert (len(word.targets),len(word.paid),len(word.cells))==(18906,104652,24)
    assert old_native[0] is new_native[0]
    assert old_native[-1].targets is new_native[-1].targets and old_native[-1].cells is new_native[-1].cells
    assert all(v.level_floor==4474 and v.targets is word.targets and v.paid is word.paid and v.cells is word.cells
               for v in (*old_native[:-1],*new_native[:-1]))
    def round_up(n):
        return ((n+9999)//10000)*10000
    direct=[verify_stage(TERMINAL,cuts,i,round_up(cuts[i-1])) for i in (2,3)]
    compiled=[verify_stage(TERMINAL,cuts,i,round_up(9*ranks[i-1])) for i in (2,3)]
    assert all(x["direct"] for x in direct) and not any(x["direct"] for x in compiled)
    tape=[verify_tape(1,[0,1],[2,1]),verify_tape(2,[1,7],[3,1])]
    print("PASS_HEIGHT_LIFT_20BIT_PROFILE",json.dumps({
        "kappa":str(TERMINAL.kappa),"heights":ranks,"gaussian_height":TERMINAL.complex_log,
        "binary_cuts":cuts,"signed":signed,"conversion_bits":conversion,"log2_B":logB,
        "complete_log2_C":TOTAL,"stock":stock,"controls":controls,
        "relaxed_smaller_sum_shortfall":str(paid-relaxed),
        "direct_stage_seams":direct,"compiled_stage_seams":compiled,"signed_tape":tape},sort_keys=True,default=str),flush=True)


if __name__=="__main__":
    check()
