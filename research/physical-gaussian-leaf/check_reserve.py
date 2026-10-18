"""Physical realization of PR45's sharp C-tensor binary-grid reserve."""
from hashlib import sha256
from pathlib import Path
import json
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
import leaf_sources
leaf_sources.activate()
from cardinal_counts import Count
from check_support import no_decode
from coefficient_engine import CoefficientEngine
from leaf_test_support import body,closed_work,packet,snapshot
from records import Tape
from session import erase_marker
from signed_linear import CoefficientDomainError
from words import need


def impulse(f,reserve):
    result = []
    for address in range(1<<f):
        real,imag = 1,0
        for bit in range(f):
            sign = -1 if address>>bit&1 else 1
            real,imag = real-sign*imag,imag+sign*real
        denominator = 1<<f
        numerators = real<<reserve,imag<<reserve
        need(all(value%denominator == 0 for value in numerators), "checker sharp tensor grid")
        result.extend(value//denominator for value in numerators)
    return result


def run():
    engine = CoefficientEngine(("v0",),"v0")
    source,back = Tape(),Tape()
    digest,cases,rejected = sha256(),[],0
    for f in range(1,9):
        reserve = (f+1)//2
        bits = reserve+4
        width = Count.literal(f)
        args = [Count.literal(value) for value in (f,1,0,bits,1,1)]
        saved = snapshot((width,*args))
        values = [0]*(2*(1<<f))
        values[0] = 1<<reserve
        raw,expected = packet(values,bits),packet(impulse(f,reserve),bits)
        for bit in raw:
            source.append(bit)
        source.rewind()
        with no_decode():
            returned = engine.run_leaf(source,(width,),*args)
        need(body(returned) == expected and body(source) == raw and source.head == 1 and
             snapshot((width,*args)) == saved, "physical sharp-reserve impulse")
        closed_work(engine)
        for bit in expected:
            back.append(bit)
        back.rewind()
        returned.clear()
        erase_marker(returned)
        with no_decode():
            returned = engine.run_leaf(back,(width,),*args,inverse=True)
        need(body(returned) == raw, "sharp-grid inverse without child re-encoding")
        closed_work(engine)
        returned.clear()
        erase_marker(returned)
        source.clear()
        back.clear()
        values[0] = 1<<(reserve-1)
        bad = packet(values,bits)
        for bit in bad:
            source.append(bit)
        source.rewind()
        with no_decode():
            try:
                engine.run_leaf(source,(width,),*args)
            except CoefficientDomainError as error:
                need("inexact" in str(error), "insufficient tensor reserve rejects exact halving")
                rejected += 1
            else:
                raise ValueError("insufficient uniform tensor reserve accepted")
        need(body(source) == bad and source.head == 1 and snapshot((width,*args)) == saved,
             "sharp-grid rejection preserves borrowed data")
        closed_work(engine,True)
        source.clear()
        digest.update(expected)
        cases.append(dict(axes=f,reserve=reserve,component_bits=bits,records=1<<f))
        for value in (width,*args):
            value.close()
    return dict(cases=cases,rejected=rejected,peak=engine.pool.peak,sha256=digest.hexdigest(),
                scope="Physical prefix execution of credited PR45 ceil(f/2) C reserve; basis-vector necessity controls; normalized Hadamard reserve remains f")


if __name__ == "__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
    print("PASS_PHYSICAL_SHARP_C_RESERVE")
