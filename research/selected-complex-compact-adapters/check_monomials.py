"""Source-bound monomial compilation and Gaussian record execution."""
from dataclasses import asdict
from fractions import Fraction as F
from hashlib import sha256
from random import Random
import json

from streams import Tape,Meter,need,bit_key,key_value
from compact import Layout
from monomial import (binary_word,column_map,column_phase,columns,tensor_phase,
                      execute_monomial)


def recipes(value):
    if isinstance(value,dict):
        if "matrix_rows" in value:
            yield value
        else:
            for child in value.values():yield from recipes(child)
    elif isinstance(value,list):
        for child in value:yield from recipes(child)


def word_address(word,x):
    for kind,i,k in word:
        if kind=="flip" or x>>k&1:x^=1<<i
    return x


def catalogue(local,old):
    unique={json.dumps(r,sort_keys=True,separators=(",",":")):r
            for name in ("CLIFFORD-RECIPES.json","RESIDUAL-ADAPTERS.json")
            for r in recipes(local[name])}
    checks=0;maximum=0;digest=sha256()
    for key,recipe in sorted(unique.items()):
        word=binary_word(recipe);m=len(recipe["matrix_rows"]);maximum=max(maximum,len(word))
        for x in range(1<<m):
            mapped=word_address(word,x)
            need(mapped==old.mv(recipe["matrix_rows"],x)^recipe["offset"],"compiled affine recipe")
            need(word_address(tuple(reversed(word)),mapped)==x,"inverse affine chronology")
            need(column_phase(recipe,x)==old.qvalue(recipe["quadratic_rows"],recipe["linear_Z4"],x,m),
                 "strict-upper retained phase convention")
            checks+=1
        digest.update((key+"\n").encode())
    return {"unique_monomials":len(unique),"full_column_checks":checks,
            "maximum_binary_operations":maximum,"catalogue_sha256":digest.hexdigest()}


def gaussian_raw(layout,bits):
    out=bytearray();bound=1<<(bits-2)
    for index in range(layout.records):
        for coefficient in range(layout.record_bits//(2*bits)):
            real=(index+3*coefficient)%(2*bound)-bound
            imag=(index//3+coefficient)%(2*bound)-bound
            out.extend(bit_key(real%(1<<bits),bits));out.extend(bit_key(imag%(1<<bits),bits))
    return out


def direct(raw,layout,recipe,f,K,rho,bits,old):
    out=bytearray(len(raw));seen=set();modulus=1<<bits;record=layout.record_bits
    m=len(recipe["matrix_rows"])
    for index in range(layout.records):
        state=layout.decode(index);new=dict(state);phase=0
        for j,x in enumerate(columns(state,m,f,K,rho)):
            y=old.mv(recipe["matrix_rows"],x)^recipe["offset"]
            phase+=recipe["phase"]+old.qvalue(recipe["quadratic_rows"],recipe["linear_Z4"],x,m)
            for i in range(m):
                name="v"+str(i);mask=1<<(rho+j*K)
                new[name]=(new[name]&~mask)|(((y>>i)&1)<<(rho+j*K))
        destination=layout.encode(new);need(destination not in seen,"direct monomial bijection");seen.add(destination)
        for coefficient in range(record//(2*bits)):
            src=index*record+2*bits*coefficient;dst=destination*record+2*bits*coefficient
            real=key_value(raw[src:src+bits]);imag=key_value(raw[src+bits:src+2*bits])
            real,imag=old.mul_i((real,imag),phase)
            out[dst:dst+2*bits]=bit_key(real%modulus,bits)+bit_key(imag%modulus,bits)
    return out


def physical_case(recipe,f,K,G,rho,old,phase_control=False):
    m=len(recipe["matrix_rows"]);bits=5
    fields=(("u",(f-1)*G),("t",(f-1)*G))+tuple(("v"+str(i),f*K) for i in range(m))+(("b",(f-1)*G),)
    layout=Layout(fields,4*bits);raw=gaussian_raw(layout,bits);meter=Meter()
    output=execute_monomial(Tape(meter,raw),layout,recipe,f,K,G,rho,bits)
    expected=direct(raw,layout,recipe,f,K,rho,bits,old)
    need(output.data==expected,"full Gaussian record monomial endpoint")
    result={"dimension":m,"columns":f,"K":K,"G":G,"rho":rho,
            "records":layout.records,"payload_bits":len(raw),"coefficient_bits":bits,
            "output_sha256":sha256(output.data).hexdigest(),"meter":asdict(meter)}
    restored=execute_monomial(output,layout,recipe,f,K,G,rho,bits,True)
    need(restored.data==raw,"physical inverse restores records and dirty compact fields")
    result["both_directions_restore"]=True
    if phase_control:
        wrong=execute_monomial(Tape(Meter(),raw),layout,recipe,f,K,G,rho,bits,
                              omit_tensor_constant=True)
        need(wrong.data!=expected,"tensor constant phase control")
        result["constant_phase_control"]="REJECT"
    return result


def selected_controls(local,old):
    recipe=local["RESIDUAL-ADAPTERS.json"]["recipes"]["0:1000"]["right"]
    need((recipe["phase"],recipe["offset"])==(2,245),"actual affine-phase control recipe")
    state={"v"+str(i):0 for i in range(9)}
    need(tensor_phase(recipe,state,2,1,0)==0 and
         tensor_phase(recipe,state,2,1,0,True)==2,"phase repeats once per column")
    need([column_map(recipe,0)]*2==[245,245],"affine offset repeats instead of cancelling")
    scale=next(e[1] for e in local["LOCAL-PROGRAMS.json.gz"]["forward"]
               if e[0]=="scalar" and e[1][0]=="scale")
    scalar=F(scale[-2],scale[-1])
    need(scalar==F(-1,2) and scalar!=scalar**2,"role scalar does not tensorize")
    child=local["CLIFFORD-RECIPES.json"]["children"][7]
    need((child["old"],child["new"],child["rank"])==(0,9,1),"actual selected transition")
    for name,events in local["LOCAL-PROGRAMS.json.gz"].items():
        need(events[9394]==["climb","A",224,0,9,1] and
             events[9396]==["climb","A",225,0,9,1],"actual selected uses in "+name)
    rng=Random(2238);tests=0
    for f in (2,3,7):
        for _ in range(100):
            state={"v"+str(i):rng.randrange(1<<f) for i in range(9)}
            xs=columns(state,9,f,1,0)
            wanted=sum(recipe["phase"]+old.qvalue(recipe["quadratic_rows"],recipe["linear_Z4"],x,9)
                       for x in xs)%4
            need(tensor_phase(recipe,state,f,1,0)==wanted,"selected multiple-column phase")
            tests+=1
    return {"child_index":7,"events":[9394,9396],"residual_phase_recipe":"0:1000.right",
            "two_zero_columns":[245,245],"two_column_phase":0,"wrong_single_phase":2,
            "unchanged_role_scalar":str(scalar),"tensor_phase_cases":tests}


def run(local,old):
    chosen=local["CLIFFORD-RECIPES.json"]["children"][7]["right"]
    small={"matrix_rows":[3,1],"offset":1,"phase":1,"linear_Z4":[1,2],"quadratic_rows":[2,0]}
    return {"status":"PASS_SELECTED_MONOMIAL_COLUMN_LIFT","catalogue":catalogue(local,old),
            "selected_controls":selected_controls(local,old),
            "physical_cases":[physical_case(chosen,1,1,1,0,old),
                              physical_case(small,2,1,1,0,old,True)]}
