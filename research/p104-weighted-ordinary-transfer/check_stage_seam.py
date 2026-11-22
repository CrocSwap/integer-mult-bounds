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

    baseline = replace(TERMINAL, rank_logs=(8192,129414,524395),kappa=Q(".00389821053"))
    assert TERMINAL.rank_logs==(8192,129406,524403) and TERMINAL.kappa==Q(".00389821057")
    assert TERMINAL.complex_log==baseline.complex_log==483871
    assert sha256((RUNTIME/"strong-bit.json.gz").read_bytes()).hexdigest()==(
        "9e7392c52bcf29c0cc58c54c619f95c28f476394c33e8e0a5aa30c9557d31362")
    old,new=prepare_native(baseline),prepare_native(TERMINAL)
    w=binary_word()
    assert old[0] is new[0] and old[-1] is new[-1]
    assert (len(w.targets),len(w.paid),len(w.cells))==(18906,104652,24)
    assert all(r.targets is w.targets and r.paid is w.paid and r.cells is w.cells
               for r in (*old[:-1],*new[:-1]))

    def upper(ranks):
        rate=Q(0)
        for h in ranks:
            rate=min(TERMINAL.eta,(249*(BINARY_C-Q(11,8*h))+rate)/250)
        return rate

    booked=TERMINAL.ordinary
    assert baseline.ordinary<upper(baseline.rank_logs)<booked<upper(TERMINAL.rank_logs)
    gaussian=GAUSSIAN_C-Q(64944,524288*483871)
    assert booked<gaussian
    smaller=booked-upper((8192,129407,524402))
    assert smaller==Q(949618999849667259182401851,233169615645211570995200000000000000000)
    profiles=[]
    for p,expected in ((baseline,(8290,137768,662227)),(TERMINAL,(8290,137760,662227))):
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
    print("PASS_LITERAL_ORDINARY_TRANSFER",json.dumps(
        {"seven_level_negative_gap":str(smaller),"stage_seams":profiles,"signed_tape":tape},
        sort_keys=True),flush=True)


if __name__=="__main__":
    check()
