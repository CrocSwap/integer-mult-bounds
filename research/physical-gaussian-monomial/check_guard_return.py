"""A later-field signed rejection preserves input and returns reusable work."""
from pathlib import Path
import json
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
import phase_sources
phase_sources.activate()
from cardinal_counts import Count
from check_support import no_decode
from gaussian_test_support import body,closed_work,encode_word,native_fixture,oracle,snapshot
from monomial_engine import MonomialEngine
from records import Tape
from session import erase_marker
from signed_phase import SignedHeadroomError
from words import need


def run():
    literal = dict(matrix_rows=[1],offset=0,phase=1,linear_Z4=[0],quadratic_rows=[0])
    fields = (("u",0),("t",0),("v0",1),("b",0))
    engine = MonomialEngine(tuple(name for name,_ in fields),("v0",),literal,native_fixture())
    widths = tuple(Count.literal(width) for _name,width in fields)
    arguments = [Count.literal(value) for value in (1,1,1,0,3,2,2)]
    borrowed = (*widths,*arguments)
    saved = snapshot(borrowed)
    source = Tape()
    raw = b"".join(encode_word(0,3)+encode_word(-4 if index == 7 else 1,3) for index in range(8))
    for bit in raw:
        source.append(bit)
    source.rewind()
    with no_decode():
        try:
            engine.run(source,widths,*arguments)
        except SignedHeadroomError:
            pass
        else:
            raise ValueError("later coefficient signed overflow accepted")
    need(body(source) == raw and source.head == 1 and snapshot(borrowed) == saved, "guard rejection preserves borrowed data")
    closed_work(engine,True)
    source.clear()
    good = raw[:-3]+encode_word(-3,3)
    for bit in good:
        source.append(bit)
    source.rewind()
    with no_decode():
        returned = engine.run(source,widths,*arguments)
    expected = oracle(good,fields,("v0",),literal,1,1,0,3,2,2)
    need(body(returned) == expected and body(source) == good and source.head == returned.head == 1,
         "valid reuse after signed rejection")
    closed_work(engine)
    returned.clear()
    erase_marker(returned)
    source.clear()
    for value in borrowed:
        value.close()
    return dict(records=4,coefficient_fields=2,rejected_field_ordinal=7,reused=True,
                peak=engine.pool.peak,scope="Last imaginary component is most-negative at phase i; the valid retry uses the same physical inventory")


if __name__ == "__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
    print("PASS_SIGNED_GUARD_RETURN_AND_REUSE")
