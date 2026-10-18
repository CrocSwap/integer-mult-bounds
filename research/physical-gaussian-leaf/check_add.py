"""Aligned signed Gaussian ADD/subtract with exact final-fit guards."""
from hashlib import sha256
from itertools import product
from pathlib import Path
from random import Random
import json
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
import leaf_sources
leaf_sources.activate()
from cardinal_counts import Count
from check_support import no_decode
from coefficient_engine import CoefficientEngine
from leaf_test_support import body,closed_work,encode,packet,snapshot
from records import Tape
from scratch_pool import ScratchPool
from session import erase_marker,sealed_constructors
from signed_linear import CoefficientDomainError,linear_word
from words import need


def run():
    inputs,output,pool = (Tape(),Tape()),Tape(),ScratchPool(32)
    valid,rejected,digest,rng = 0,0,sha256(),Random(18693087)
    for bits in (2,3,4,17,65):
        width = Count.literal(bits)
        limit = 1<<(bits-1)
        edge = (-limit,-limit+1,-1,0,1,limit-2,limit-1)
        cases = product(range(-limit,limit),repeat=2) if bits <= 4 else (
            list(product(edge,repeat=2))+[(rng.randrange(-limit,limit),rng.randrange(-limit,limit)) for _ in range(64)])
        with no_decode(),sealed_constructors(),pool.install():
            for x,y in cases:
                raw = (encode(x,bits),encode(y,bits))
                for tape,word in zip(inputs,raw):
                    for bit in word:
                        tape.append(bit)
                    tape.rewind()
                for subtract in (False,True):
                    expected = x-y if subtract else x+y
                    fits = -limit <= expected < limit
                    try:
                        linear_word(inputs,output,width,(1,-1) if subtract else (1,1))
                    except CoefficientDomainError as error:
                        need(not fits and "headroom" in str(error), "exact signed addition rejection")
                        rejected += 1
                    else:
                        need(fits and body(output) == encode(expected,bits), "exact signed addition value")
                        valid += 1
                    need(tuple(body(tape) for tape in inputs) == raw and all(tape.head == 1 for tape in inputs),
                         "addition component borrows preserved")
                    digest.update(json.dumps((bits,x,y,subtract,expected,fits),separators=(",",":")).encode())
                    output.clear()
                    pool.empty()
                for tape in inputs:
                    tape.clear()
        width.close()

    engine = CoefficientEngine(("v0",),"v0")
    width,count = Count.literal(17),Count.literal(37)
    left_values = [((i*31)%1001)-500 for i in range(74)]
    right_values = [((i*17)%101)-50 for i in range(74)]
    left_raw,right_raw = packet(left_values,17),packet(right_values,17)
    for tape,raw in zip(inputs,(left_raw,right_raw)):
        for bit in raw:
            tape.append(bit)
        tape.rewind()
    saved = snapshot((width,count))
    for subtract in (False,True):
        expected = packet([x-y if subtract else x+y for x,y in zip(left_values,right_values)],17)
        with no_decode():
            returned = engine.run_add(*inputs,width,count,subtract)
        need(body(returned) == expected and tuple(body(tape) for tape in inputs) == (left_raw,right_raw) and
             all(tape.head == 1 for tape in inputs) and snapshot((width,count)) == saved,
             "complete aligned Gaussian addition and preservation")
        closed_work(engine)
        returned.clear()
        erase_marker(returned)
    for tape in inputs:
        tape.clear()
    width.close()
    count.close()
    return dict(valid=valid,rejected=rejected,word_peak=pool.peak,packet_gaussians=37,
                packet_peak=engine.pool.peak,sha256=digest.hexdigest(),
                scope="Exhaust signed widths2/3/4 and17/65 boundary probes; preserved aligned operands in both directions")


if __name__ == "__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
    print("PASS_PHYSICAL_GAUSSIAN_ADD")
