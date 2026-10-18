"""Full small payload rectangles for the charged sequential interpreter."""
from dataclasses import asdict
from hashlib import sha256
from random import Random

from streams import Tape,Meter,need,bit_key
from compact import Compact,Layout,execute,repair


def labelled(layout):
    need(layout.record_bits>=layout.bits,"unique test record labels")
    return bytearray(b for i in range(layout.records) for b in bit_key(i,layout.record_bits))


def direct(raw,layout,word,raw_word=False):
    """Dense test oracle only; production movement never seeks by address."""
    out=bytearray(len(raw));seen=set();r=layout.record_bits
    for index in range(layout.records):
        state=layout.decode(index)
        target=word.execute(state,layout) if raw_word else word.ideal(state,True)
        destination=layout.encode(target)
        need(destination not in seen,"independent address bijection");seen.add(destination)
        out[destination*r:(destination+1)*r]=raw[index*r:(index+1)*r]
    return out


def case(n,K,G,rho,late=False,constant=False,controls=False):
    fields=(("u",n*G),("t",n*G))+(("y",(n+1)*K),("x",(n+1)*K)) if late else (
           ("u",n*G),("t",n*G),("x",(n+1)*K),("y",(n+1)*K))
    fields=fields+(("b",n*G),)
    layout=Layout(fields,sum(width for _,width in fields))
    word=Compact(n,K,G,rho,None if constant else "x","y",late)
    raw=labelled(layout);meter=Meter()
    out=execute(Tape(meter,raw),layout,word)
    expected=direct(raw,layout,word)
    need(out.data==expected,"complete repaired compact payload")
    need(len(meter.ordinary_calls)==(12 if late else 4) and
         meter.rotation_passes==(10 if late else 4),"literal compact operation counts")
    rejected=[]
    if controls:
        for name,options in (("omitted_repair",{"omit_repair":True}),
                             ("omitted_inverse_key",{"wrong_inverse":True})):
            wrong=execute(Tape(Meter(),raw),layout,word,**options)
            need(wrong.data!=expected,"semantic negative control: "+name)
            rejected.append(name)
    return {"n":n,"K":K,"G":G,"rho":rho,"late":late,"constant_toggle":constant,
            "records":layout.records,"record_bits":layout.record_bits,"payload_bits":len(raw),
            "output_sha256":sha256(out.data).hexdigest(),"meter":asdict(meter),"controls":rejected}


def sparse_repair_controls(full=False):
    """Repair both regimes, optionally over the entire wide-source rectangle.

    The bounded replay fixes the nine ignored source bits to zero. The raw
    word, ideal map and repair preserve that fibre because they fix x.
    """
    n,K,G=1,5,1
    fields=(("u",1),("t",1),("x",10 if full else 1),("y",10),("b",1))
    # One-bit opaque records bound the optional full 2^23-address experiment.
    layout=Layout(fields,1);word=Compact(n,K,G,0,"x","y")
    raw=bytearray((i^(i>>3)^(i>>8)).bit_count()&1 for i in range(layout.records))
    after=bytearray(len(raw));expected=bytearray(len(raw));bad=0
    for i in range(layout.records):
        state=layout.decode(i);bad+=word.bad(state)
        after[layout.encode(word.execute(state,layout))]=raw[i]
        expected[layout.encode(word.ideal(state))]=raw[i]
    need(0<bad<layout.records,"nonempty good and bad sets")
    meter=Meter();out=repair(Tape(meter,after),layout,word)
    need(out.data==expected,"sparse exact repair with untouched good records")
    need(meter.repair_records==bad,"actual extracted exceptional count")
    return {"records":layout.records,"record_bits":1,"bad_records":bad,
            "good_records":layout.records-bad,"output_sha256":sha256(out.data).hexdigest(),
            "scope":("Full wide-source rectangle" if full else "Invariant fibre with nine ignored source bits fixed")+
                    "; repair executes sequentially; raw word and expected map use address oracles.",
            "meter":asdict(meter)}


def address_crosscheck(old):
    rng=Random(2238);checks=0;good=bad=0
    for n,K,G,rho in ((1,5,1,0),(2,7,2,6),(3,9,3,8)):
        for late in (False,True):
            order,_=old.program(n,K,rho,G,late)
            fields=tuple((name,(n+1)*K if name in ("x","y") else n*G) for name in order)
            layout=Layout(fields,1);word=Compact(n,K,G,rho,"x","y",late)
            for _ in range(100):
                state={name:rng.randrange(1<<width) for name,width in fields}
                actual=word.execute(state,layout)
                need(actual==old.execute(state,n,K,rho,G,late=late),"retained raw word agreement")
                need(word.execute(actual,layout,True)==state,"complete inverse word")
                need(word.bad(state)==old.exceptional(state,n,K,rho,G,late),"retained sufficient guard")
                need(word.bad(actual)==word.bad(state),"raw bad-set invariance")
                checks+=1;bad+=word.bad(state);good+=not word.bad(state)
    need(good and bad,"both regimes in exact control comparison")
    return {"cases":checks,"good":good,"bad":bad}


def run(old,large=False):
    result={"status":"PASS_SEQUENTIAL_COMPACT_REPAIR",
            "retained_address_crosscheck":address_crosscheck(old),
            "cases":[case(1,1,1,0),case(1,1,1,0,True),
                     case(1,2,1,1,controls=True),case(1,2,1,1,True,controls=True),
                     case(1,2,1,1,constant=True,controls=True),case(2,2,1,1,True)],
            "mixed_guard_repair":sparse_repair_controls(large)}
    return result
