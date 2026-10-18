"""The one-column path does not scan an arbitrarily long unused G tape."""
from pathlib import Path
import json
import sys
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parent))
import phase_sources
phase_sources.activate()
from cardinal_counts import Count
from gaussian_test_support import body,closed_work,encode_word,native_fixture,oracle,snapshot
from monomial_engine import MonomialEngine
from records import Tape
from session import erase_marker
from words import need


def run():
    literal = dict(matrix_rows=[1],offset=1,phase=1,linear_Z4=[1],quadratic_rows=[0])
    fields = (("u",0),("t",0),("v0",1),("b",0))
    engine = MonomialEngine(tuple(name for name,_ in fields),("v0",),literal,native_fixture())
    widths = tuple(Count.literal(width) for _name,width in fields)
    parameters = [Count.literal(value) for value in (1,1,(1<<4096)+1,0,3,1,1)]
    saved = snapshot((*widths,*parameters))
    source = Tape()
    raw = encode_word(1,3)+encode_word(-1,3)+encode_word(2,3)+encode_word(1,3)
    for bit in raw:
        source.append(bit)
    source.rewind()
    tape,visited = parameters[2].tape,[]
    original_read = tape.read
    def guarded_read():
        visited.append(tape.head)
        need(tape.head <= 2, "unused G scanned beyond its positive test")
        return original_read()
    with patch.object(tape,"read",guarded_read):
        returned = engine.run(source,widths,*parameters)
    need(body(returned) == oracle(raw,fields,("v0",),literal,1,1,0,3,1,1), "one-column endpoint with unused large G")
    need(body(source) == raw and snapshot((*widths,*parameters)) == saved, "unused descriptor remains borrowed")
    closed_work(engine)
    returned.clear()
    erase_marker(returned)
    source.clear()
    for value in (*widths,*parameters):
        value.close()
    return dict(G_binary_digits=4097,maximum_visited_position=max(visited),payload_bits=len(raw),
                scope="Owned work/time is independent of unused G digits; borrowed descriptor storage remains part of total input storage")


if __name__ == "__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
    print("PASS_UNUSED_COMPACT_PARAMETER_LOCALITY")
