"""Close the retained header-router ordinary calls without a new route invoice."""
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
import json

from controlled_stream import Tape
from provider import need
from leaf import LeafMeter
from header_streams import add,scale_affine,ordinary_fields,finite_classes
import qadic_streams as old_stream
import route_catalog as old_routes


def inherited_routes(catalogue,root):
    names=(old_routes.GEOMETRY,old_routes.TEMPLATE,old_routes.GLOBAL,old_routes.WORD,
           old_routes.EXPECTED,old_routes.ASSEMBLY)
    routes,_=old_routes.compile_catalog({p:(root/p).read_bytes() for p in names})
    alphabet=set();checks=0
    for chart in catalogue.charts:
        if chart.kind=="data":
            key=f"data:{chart.port}:{chart.stage}"
        elif chart.kind=="host":
            key="host:"+",".join(map(str,chart.axes))+(f":{chart.port}" if chart.port>=0 else "")
        else:
            continue
        word=[(kind,i,j,F(c)) for kind,i,j,c in routes[key]["word"]]
        inverse=[(kind,i,j,1/c if kind=="scale" else -c if kind=="add" else c)
                 for kind,i,j,c in reversed(word)]
        expected=[list(row) for row in catalogue.chart_matrix(chart)]
        need(old_routes.replay(inverse)==expected,"provider chart equals inverse retained route")
        alphabet.update(c for _,_,_,c in word+inverse)
        checks+=1
    need(checks==1123,"retained physical route types")
    for c in alphabet:
        a,b=abs(c.numerator),c.denominator
        need(a and a&(a-1)==0 and b&(b-1)==0,"finite fixed dyadic alphabet")
    return {"credited_PR2157_route_types":checks,
            "static_coefficients":[str(c) for c in sorted(alphabet)],
            "scope":"Reuse of retained fixed words and directions; no new per-call route census or finite invoice."}


def raw_records(records,bits):
    need(records<2**bits,"unique header record labels")
    return [(i>>b)&1 for i in range(records) for b in range(bits)]


def affine_case(q,width,coefficient,reversed_fields):
    high=q**(width-1);modulus=q**width
    before,middle,suffix=2,3,13;low_x,low_y=q-1,1
    raw=raw_records(before*high*middle*high,suffix);meter=LeafMeter()
    out,new_low=add(Tape(meter.movement,raw),q,width,low_x,low_y,coefficient,
                    before,middle,suffix,meter,reversed_fields)
    expected=[None]*len(raw);c=coefficient.numerator*pow(coefficient.denominator,-1,modulus)%modulus
    for a,first,z,second in product(range(before),range(high),range(middle),range(high)):
        x,y=(second,first) if reversed_fields else (first,second)
        target=((low_y+q*y+c*(low_x+q*x))%modulus-new_low)//q
        new_first,new_second=(target,x) if reversed_fields else (x,target)
        src=(((a*high+first)*middle+z)*high+second)*suffix
        dst=(((a*high+new_first)*middle+z)*high+new_second)*suffix
        expected[dst:dst+suffix]=raw[src:src+suffix]
    need(out.bits==expected and out.head==0,"full-ring header affine endpoint")
    need(meter.opaque_child_calls==0,"no inherited ordinary oracle")
    need(meter.digit_swaps==(2*(width-1) if reversed_fields and width>1 else 0),
         "actual header ordinary digit bill")
    if width>1:
        wrong_meter=LeafMeter()
        wrong,_=add(Tape(wrong_meter.movement,raw),q,width,low_x,low_y,coefficient,
                    before,middle,suffix,wrong_meter,reversed_fields,True)
        # Some low pairs have zero carry; retain only distinguishing controls.
        carry_control=wrong.bits!=expected
    else:
        carry_control=False
    return {"q":q,"width":width,"coefficient":str(coefficient),"reversed_fields":reversed_fields,
            "payload_bits":len(raw),"elementary_digit_swaps":meter.digit_swaps,
            "ordinary_atom_swaps":meter.ordinary_atom_swaps,"opaque_child_calls":0,
            "carry_omission_distinguishes":carry_control}


def compound_case():
    q,width=3,3;high=q**(width-1);modulus=q**width
    before,middle,suffix=2,2,13;x0,y0=2,1
    raw=raw_records(before*high*middle*high,suffix);meter=LeafMeter()
    source,new_x=scale_affine(Tape(meter.movement,raw),q,width,x0,F(2),before,
                             middle*high*suffix,meter)
    source,new_y=add(source,q,width,new_x,y0,F(-1,2),before,middle,suffix,meter)
    source=ordinary_fields(source,q,width-1,before,middle,suffix,meter)
    final_low=(new_y,new_x);expected=[None]*len(raw)
    for a,x,z,y in product(range(before),range(high),range(middle),range(high)):
        X,Y=x0+q*x,y0+q*y
        first=((Y-X)%modulus-final_low[0])//q
        second=((2*X)%modulus-final_low[1])//q
        src=(((a*high+x)*middle+z)*high+y)*suffix
        dst=(((a*high+first)*middle+z)*high+second)*suffix
        expected[dst:dst+suffix]=raw[src:src+suffix]
    need(source.bits==expected and source.head==0,"updated low carry through a fixed route word")
    # At width one the high route disappears, but the low-class map remains.
    raw_low=raw_records(2*3*7,6);low_meter=LeafMeter()
    out=finite_classes(Tape(low_meter.movement,raw_low),2,3,7*6,[2,0,1],low_meter)
    direct=[]
    for prefix in range(2):
        for new in range(3):
            old=[2,0,1].index(new);start=(prefix*3+old)*7*6
            direct.extend(raw_low[start:start+7*6])
    need(out.bits==direct and out.bits!=raw_low and out.head==0,"nontrivial low permutation at width one")
    return {"q":q,"width":width,"payload_bits":len(raw),"final_low":final_low,
            "digit_swaps":meter.digit_swaps,"opaque_child_calls":0,
            "width_one_low_permutation_bits":len(raw_low)}


def run(catalogue,root):
    def forbidden(*_args,**_kwargs):
        raise ValueError("an old completed-swap oracle was called")
    old_stream.completed_swap_oracle=forbidden
    routes=inherited_routes(catalogue,root)
    cases=[affine_case(q,w,c,reverse) for q,w in ((3,1),(3,2),(3,3),(5,2))
           for c in (F(1,2),F(-2)) for reverse in (False,True)]
    need(any(x["carry_omission_distinguishes"] for x in cases),"physical carry controls")
    return {"status":"PASS_ELEMENTARY_HEADER_ROUTING_BASE","retained_routes":routes,
            "affine_cases":cases,"compound_route":compound_case()}
