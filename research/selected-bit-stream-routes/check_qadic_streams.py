"""Dense full-modulus oracles for the sequential payload routines."""
from fractions import Fraction as F
from itertools import product
import json
from qadic_streams import Meter,Tape,need,physical_add,physical_scale


def bits(index,width):
    return [(index>>i)&1 for i in range(width)]


def check_add(q,width,lx,ly,c,reversed_fields):
    high=q**(width-1);before,middle,suffix=2,3,13
    size=before*high*middle*high
    raw=[bit for i in range(size) for bit in bits(3*i+1,suffix)]
    meter=Meter();actual,new=physical_add(Tape(meter,raw),q,width,lx,ly,c,before,middle,suffix,reversed_fields)
    expected=[None]*len(raw);mod=q**width
    coefficient=c.numerator*pow(c.denominator,-1,mod)%mod
    for a,i,z,j in product(range(before),range(high),range(middle),range(high)):
        x,y=(j,i) if reversed_fields else (i,j)
        oldx,oldy=lx+q*x,ly+q*y
        value=(oldy+coefficient*oldx)%mod
        low,newy=value%q,value//q
        need(low==new,"full-width low oracle")
        oi,oj=(newy,x) if reversed_fields else (x,newy)
        src=(((a*high+i)*middle+z)*high+j)*suffix
        dst=(((a*high+oi)*middle+z)*high+oj)*suffix
        expected[dst:dst+suffix]=raw[src:src+suffix]
    need(actual.bits==expected,"opaque payload permutation")
    need(len(meter.ordinary)==(2 if reversed_fields and width>1 else 0),"charged ordinary call count")
    need(meter.reads+meter.writes+meter.moves<=150*len(raw),"linear streaming data movement")
    return len(raw),meter


def check_scale(q,width,low,c):
    high=q**(width-1);before,suffix=3,13
    raw=[bit for i in range(before*high) for bit in bits(5*i+3,suffix)]
    meter=Meter();actual,new=physical_scale(Tape(meter,raw),q,width,low,c,before,suffix)
    expected=[None]*len(raw);mod=q**width
    coefficient=c.numerator*pow(c.denominator,-1,mod)%mod
    for a,y in product(range(before),range(high)):
        value=coefficient*(low+q*y)%mod
        need(value%q==new,"scaling low oracle")
        src=(a*high+y)*suffix;dst=(a*high+value//q)*suffix
        expected[dst:dst+suffix]=raw[src:src+suffix]
    need(actual.bits==expected,"signed scaling payload permutation")
    need(not meter.ordinary,"scaling adds no ordinary interchange")
    need(meter.reads+meter.writes+meter.moves<=150*len(raw),"linear scaling data movement")


def check_primitives():
    additions=scalings=bits_checked=ordinary=0
    for q,width in ((3,1),(3,2),(3,3),(5,2),(5,3),(7,2)):
        for lx,ly in ((0,0),(1,0),(q-1,q-1),(q-2,1)):
            for c in (F(1),F(-1),F(1,2),F(-1,2),F(1,4),F(2)):
                for reverse in (False,True):
                    count,meter=check_add(q,width,lx,ly,c,reverse)
                    additions+=1;bits_checked+=count;ordinary+=len(meter.ordinary)
        for low in (0,1,q-1):
            for c in (F(2),F(-2),F(1,2),F(1,4),F(-1)):
                check_scale(q,width,low,c);scalings+=1
    q,width,c=5,2,F(1,2);high=5;raw=[bit for i in range(high*high) for bit in bits(i+1,7)]
    correct,_=physical_add(Tape(Meter(),raw),q,width,1,0,c,suffix=7)
    wrong,_=physical_add(Tape(Meter(),raw),q,width,1,0,c,suffix=7,omit_carry=True)
    need(correct.bits!=wrong.bits,"carry omission must fail on moved data")
    # w=1 has a nonidentity low permutation and no high-field call.
    meter=Meter();out,new=physical_add(Tape(meter,[1,0,1]),5,1,1,0,F(1,2),suffix=3,reversed_fields=True)
    need(new==3 and out.bits==[1,0,1] and not meter.ordinary,"width-one branch")
    return {"status":"PASS_SEQUENTIAL_QADIC_STREAM_PRIMITIVES","addition_cases":additions,
                      "scaling_cases":scalings,"payload_bits_checked":bits_checked,
                      "charged_ordinary_calls":ordinary,"carry_omission_control":"REJECT",
                      "scope":"Sequential affine data movement with an explicit completed-swap oracle. This does not implement the inherited ordinary kernel."}


if __name__=="__main__":print(json.dumps(check_primitives(),indent=2))
