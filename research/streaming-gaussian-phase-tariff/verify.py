#!/usr/bin/env python3
"""Compare exact coefficient values, source endpoints and complete tape invoices."""
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
import phase
from streams import Tape,Meter,need
from compact import Layout
import monomial as old


def units(m):return m.reads+m.writes+m.moves+m.erases


def encode(pair,b):return bytes((x>>i)&1 for x in pair for i in range(b))


def decode(raw,b):return tuple(sum(bit<<i for i,bit in enumerate(raw[j*b:(j+1)*b])) for j in range(2))


def rotate(pair,k,b):
    x,y=pair
    return tuple(v%(1<<b) for v in ((x,y),(-y,x),(-x,-y),(y,-x))[k%4])


def independent_phase(recipe,state,f,K,rho):
    result=f*recipe["phase"]
    for j in range(f):
        bits=[(state["v"+str(i)]>>(rho+j*K))&1 for i in range(len(recipe["matrix_rows"]))]
        result+=sum(a*x for a,x in zip(recipe["linear_Z4"],bits))
        result+=2*sum(bits[i]*bits[k] for i in range(len(bits)) for k in range(i+1,len(bits))
                      if recipe["quadratic_rows"][i]>>k&1)
    return result%4


def phase_case(layout,recipe,f,K,rho,b,raw,inverse=False,head=0):
    new_meter,old_meter=Meter(),Meter()
    new_input,old_input=Tape(new_meter,raw),Tape(old_meter,raw)
    new_input.head=old_input.head=head
    new=phase.phase_pass(new_input,layout,recipe,f,K,rho,b,inverse)
    prior=old.phase_pass(old_input,layout,recipe,f,K,rho,b,inverse)
    expected=bytearray();odd=0
    for i in range(layout.records):
        k=independent_phase(recipe,layout.decode(i),f,K,rho)
        if inverse:k=-k%4
        odd+=(k%2)*layout.record_bits
        for j in range(layout.record_bits//(2*b)):
            at=i*layout.record_bits+j*2*b
            expected.extend(encode(rotate(decode(raw[at:at+2*b],b),k,b),b))
    need(new.data==prior.data==expected,"phase endpoint disagreement")
    need(not new_input.data and not old_input.data and new.head==prior.head==0,"retirement or head failure")
    V=len(raw)
    need(units(new_meter)==9*V+9*odd//2+head,"new exact tariff")
    need(units(old_meter)==18*V+head,"source exact tariff")
    need(new_meter.control_evaluations==old_meter.control_evaluations==layout.records,
         "control coverage changed")
    return {"volume":V,"odd_volume":odd,"new_transitions":units(new_meter),
            "old_transitions":units(old_meter),"output_sha256":sha256(new.data).hexdigest()}


def replay():
    for item in json.loads((HERE/"SOURCES.json").read_text())["files"]:
        if item["usage"]=="input":need(sha256((ROOT/item["path"]).read_bytes()).hexdigest()==item["sha256"],"source hash mismatch")
    coefficient_pairs=cases=0
    for b in range(2,7):
        pairs=list(product(range(1<<b),repeat=2))
        raw=b"".join(encode(x,b) for x in pairs)
        layout=Layout((("v0",1),),len(raw)//2)
        for k in range(4):
            rec={"matrix_rows":[1],"offset":0,"quadratic_rows":[0],"linear_Z4":[0],"phase":k}
            phase_case(layout,rec,1,1,0,b,raw)
            coefficient_pairs+=len(pairs);cases+=1
    pattern_cases=0
    for f in (1,2,3):
        layout=Layout((("v0",f),("v1",f),("tag",1)),16)
        raw=bytes((i*17+i//7)%2 for i in range(layout.records*layout.record_bits))
        for c,a,b,q in product(range(4),range(4),range(4),range(2)):
            rec={"matrix_rows":[1,2],"offset":0,"quadratic_rows":[q<<1,0],"linear_Z4":[a,b],"phase":c}
            for inverse in (False,True):
                phase_case(layout,rec,f,1,0,4,raw,inverse,head=7)
                pattern_cases+=1
    fixture=json.loads((ROOT/"research/complex-four-base-packet/FIXTURE.json").read_text())
    layout=Layout(tuple(("v"+str(i),1) for i in range(9))+(("tag",1),),32)
    raw=b"".join(encode((i-512,511-i),16) for i in range(layout.records))
    actual={}
    for name in ("right","left"):
        rec=fixture["recipe"][name]
        actual[name]=phase_case(layout,rec,1,1,0,16,raw)
        for inverse in (False,True):
            a=phase.execute_monomial(Tape(Meter(),raw),layout,rec,1,1,1,0,16,inverse)
            b=old.execute_monomial(Tape(Meter(),raw),layout,rec,1,1,1,0,16,inverse)
            need(a.data==b.data,"actual complete monomial mismatch")
            need(units(b.meter)-units(a.meter)==actual[name]["old_transitions"]-actual[name]["new_transitions"],
                 "actual monomial saving mismatch")
    layout=Layout((("u",1),("t",1),("v0",2),("v1",2),("b",1)),16)
    rec={"matrix_rows":[3,2],"offset":3,"quadratic_rows":[2,0],"linear_Z4":[3,1],"phase":1}
    raw=bytes((i+i//5)%2 for i in range(layout.records*layout.record_bits))
    for inverse in (False,True):
        a=phase.execute_monomial(Tape(Meter(),raw),layout,rec,2,1,1,0,4,inverse)
        b=old.execute_monomial(Tape(Meter(),raw),layout,rec,2,1,1,0,4,inverse)
        need(a.data==b.data and a.meter.ordinary_calls==b.meter.ordinary_calls,"compact composition mismatch")
        back=phase.execute_monomial(a,layout,rec,2,1,1,0,4,not inverse)
        need(back.data==raw,"complete tensor roundtrip")
    controls=0
    layout=Layout((("v0",1),),4)
    rec={"matrix_rows":[1],"offset":0,"quadratic_rows":[0],"linear_Z4":[0],"phase":1}
    pair=(1,2)
    need(rotate(pair,1,3)!=rotate(pair,3,3),"inverse-phase control");controls+=1
    need(rotate(pair,2,3)!=(pair[0]^7,pair[1]^7),"negation carry control");controls+=1
    need(rotate(pair,1,3)!=tuple(reversed(pair)),"odd-phase sign control");controls+=1
    for data,width in ((bytes(7),2),(bytes(9),2),(bytes(8),1)):
        try:phase.phase_pass(Tape(Meter(),data),layout,rec,1,1,0,width)
        except ValueError:controls+=1
    need(controls==6,"invalid input accepted")
    return {"status":"PASS_STREAMING_GAUSSIAN_PHASE_TARIFF_NO_NEW_KAPPA",
            "coefficient_cases":cases,"coefficient_pairs":coefficient_pairs,"pattern_cases":pattern_cases,
            "actual_recipe_phase_receipts":actual,"actual_monomial_cases":4,"compact_tensor_cases":2,
            "controls":controls,"worst_case_payload_saving":"1/4","even_phase_payload_saving":"1/2"}


if __name__=="__main__":
    result=replay()
    if "--record" in sys.argv:(HERE/"RESULT.json").write_text(json.dumps(result,indent=2)+"\n")
    else:need(json.dumps(result,sort_keys=True)==json.dumps(json.loads((HERE/"RESULT.json").read_text()),sort_keys=True),"typed receipt mismatch")
    print(json.dumps(result,sort_keys=True))
