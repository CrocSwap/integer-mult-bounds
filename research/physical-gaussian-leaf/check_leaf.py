"""Complete dirty Gaussian leaf packets and one-inventory reuse."""
from hashlib import sha256
from pathlib import Path
from time import monotonic
import json
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
import leaf_sources
leaf_sources.activate()
from cardinal_counts import Count
from check_support import no_decode
from coefficient_engine import CoefficientEngine
from leaf_test_support import body,closed_work,oracle,packet,snapshot
from records import Tape
from session import erase_marker
from words import need


def one_case(engine,f,K,rho,bits,coefficients,rows,boundary=False):
    fields = (("u",1),("v0",f*K),("dirty",1),("b",1))
    widths = tuple(Count.literal(width) for _name,width in fields)
    parameters = [Count.literal(value) for value in (f,K,rho,bits,coefficients,rows)]
    saved = snapshot((*widths,*parameters))
    records = 1<<sum(width for _name,width in fields)
    values = []
    for row in range(rows):
        for address in range(records):
            for field in range(coefficients):
                values.extend((3,3) if boundary else
                              ((1<<(2*f))*((17*address+13*row+5*field)%29-14),
                               (1<<(2*f))*((11*address-7*row+3*field)%31-15)))
    raw = packet(values,bits)
    expected = oracle(raw,fields,"v0",f,K,rho,bits,coefficients,rows)
    source,back = Tape(),Tape()
    for bit in raw:
        source.append(bit)
    source.rewind()
    with no_decode():
        returned = engine.run_leaf(source,widths,*parameters)
        need(body(returned) == expected, "complete encoded C leaf forward")
        need(body(source) == raw and source.head == returned.head == 1 and
             snapshot((*widths,*parameters)) == saved, "leaf forward borrowed preservation")
        closed_work(engine)
    for bit in body(returned):
        back.append(bit)
    back.rewind()
    returned.clear()
    erase_marker(returned)
    with no_decode():
        returned = engine.run_leaf(back,widths,*parameters,inverse=True)
        need(body(returned) == raw, "complete encoded C leaf inverse")
        need(body(back) == expected and back.head == returned.head == 1 and
             snapshot((*widths,*parameters)) == saved, "leaf inverse borrowed preservation")
        closed_work(engine)
    if boundary:
        need(raw == expected, "equal maximum signed Gaussian fields remain fixed")
    returned.clear()
    erase_marker(returned)
    source.clear()
    back.clear()
    for value in (*widths,*parameters):
        value.close()
    return dict(f=f,K=K,rho=rho,component_bits=bits,coefficient_fields=coefficients,
                outer_rows=rows,records_per_row=records,payload_bits=len(raw),peak=engine.pool.peak,
                forward_sha256=sha256(expected).hexdigest(),boundary=boundary)


def run():
    started = monotonic()
    engine = CoefficientEngine(("u","v0","dirty","b"),"v0")
    result = [one_case(engine,2,2,1,13,3,3),
              one_case(engine,3,1,0,15,2,2),
              one_case(engine,1,1,0,3,2,2,True)]
    print("complete encoded leaf seconds",round(monotonic()-started,2),flush=True)
    return dict(cases=result,scope="Complete spaced/tensor leaves, dirty labels, multiple fields/outer rows, reverse axes and smaller-boundary reuse; O(fV) direct leaf only")


if __name__ == "__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
    print("PASS_PHYSICAL_GAUSSIAN_LEAF")
