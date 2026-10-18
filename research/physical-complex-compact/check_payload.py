"""Complete physical Compact rectangles with independent input-bit columns."""
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
import json
import sys
from time import monotonic
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parent))
import native_sources
_source,reference = native_sources.activate()
from cardinal_counts import Count
from check_support import no_decode
from compact_engine import CompactEngine
from compact_control import Control
from macro_code import Code
from ordinary import Ordinary
from provenance import Provenance
from records import Tape
from session import erase_marker
from words import BLANK,need


def native_fixture(q=2):
    binding = SimpleNamespace(codes=SimpleNamespace(q=q))
    return Ordinary(q,binding,SimpleNamespace(families=0),
                    (Code((("unreachable",),),0),),capacity=64)


def body(tape):
    tape = getattr(tape,"physical",tape)
    return bytes(tape.cells[1:]).rstrip(bytes([BLANK]))


def closed_work(engine):
    native = engine.binary.native
    tapes = [*engine.pool.tapes,*engine.binary.pool.tapes,engine.binary.output,
             *native.pool.tapes,*native.runtime.roles.values(),*native.runtime.handoff.values(),
             *native.runtime.pool.tapes,native.runtime.output,native.output]
    for bank in (*native.banks,native.runtime.arena,native.runtime.indices):
        need(not bank.live and not bank.initialized, "closed numerical backend work")
        tapes.extend(word.tape for word in (*bank.words,bank.template))
    need(engine.closed and engine.binary.closed and native.closed, "completed compact/backend scopes")
    need(all(all(bit == BLANK for bit in tape.cells) for tape in tapes), "complete owned physical erasure")


def one_case(late=False,constant=False,outer=3,record_bits=3,engine=None,
             n=1,K=1,G=1,rho=0,q=2,omit_source=False,consume=True):
    vectors = ((("y",(n+1)*K),) if omit_source else
               (("y",(n+1)*K),("x",(n+1)*K)) if late else
               (("x",(n+1)*K),("y",(n+1)*K)))
    need(not omit_source or constant, "only constant toggle omits the wide source")
    fields = (("u",n*G),("t",n*G))+vectors+(("b",n*G),)
    names = tuple(name for name,_ in fields)
    layout = reference.Layout(fields,record_bits)
    word = reference.Compact(n,K,G,rho,None if constant else "x","y",late)
    if engine is None:
        engine = CompactEngine(names,None if constant else "x","y",late,native_fixture(q))
    widths = tuple(Count.literal(width) for _name,width in fields)
    parameters = [Count.literal(value) for value in (n,K,G,rho,record_bits,outer)]
    borrowed = (*widths,*parameters)
    initial_descriptors = [(bytes(value.tape.cells),value.tape.head) for value in borrowed]
    source = Tape()
    length = outer*layout.records*record_bits
    for address in range(length):
        source.append((address*13 ^ address//5 ^ 3) & 1)
    source.rewind()
    initial = body(source)
    expected,masks = bytearray(length),[0]*length
    guard_expected = {False:0,True:0}
    for row in range(outer):
        for address in range(layout.records):
            state = layout.decode(address)
            guard_expected[word.bad(state)] += 1
            destination = layout.encode(word.ideal(state,True))
            for bit in range(record_bits):
                origin = (row*layout.records+address)*record_bits+bit
                target = (row*layout.records+destination)*record_bits+bit
                expected[target],masks[target] = initial[origin],1<<origin
    observer = Provenance(length)
    observer.mark(source)
    before = dict(engine.calls)
    original_bad,guard_actual = Control.bad,{False:0,True:0}
    def observe_guard(control,state):
        value = original_bad(control,state)
        guard_actual[value] += 1
        return value
    def forbidden(*_args,**_kwargs):
        raise ValueError("indexed reference oracle reached during physical execution")
    with no_decode(),observer.installed(),patch.object(Control,"bad",observe_guard), \
            patch.multiple(reference.Compact,execute=forbidden,offset=forbidden,ideal=forbidden,
                           bad=forbidden,select=forbidden,mask=forbidden):
        returned = engine.run(source,widths,*parameters)
    need(body(returned) == expected and observer.masks(returned,length) == tuple(masks),
         "complete compact endpoint for every independent input bit")
    need(body(source) == initial and source.head == returned.head == 1, "preserved borrowed payload and heads")
    need(initial_descriptors == [(bytes(value.tape.cells),value.tape.head) for value in borrowed],
         "borrowed encoded descriptors preserved")
    closed_work(engine)
    need(guard_actual == guard_expected, "complete good/bad branch census")
    calls = {key:engine.calls[key]-before[key] for key in before}
    need(calls == dict(ordinary=outer*(12 if late else 4),rotations=outer*(10 if late else 4),rows=outer),
         "literal full operation count per outer row")
    result = dict(late=late,constant=constant,outer_rows=outer,record_bits=record_bits,
                  n=n,K=K,G=G,rho=rho,native_q=engine.binary.native.q,
                  columns=length,calls=calls,good_records=guard_actual[False],bad_records=guard_actual[True],
                  peak=engine.pool.peak,output_sha256=sha256(expected).hexdigest())
    if consume:
        returned.clear()
        erase_marker(returned)
    source.clear()
    for value in borrowed:
        value.close()
    return engine,result


def run():
    started = monotonic()
    engine,first = one_case()
    _engine,reused = one_case(outer=2,record_bits=2,engine=engine)
    _engine,late = one_case(late=True,outer=2,record_bits=2)
    _engine,toggle = one_case(constant=True,outer=3,record_bits=1)
    _engine,padded = one_case(q=3,outer=2,record_bits=1)
    print("complete compact rectangle seconds",round(monotonic()-started,2),flush=True)
    return dict(cases=[first,reused,late,toggle,padded],
                scope="Complete n1/K1/G1 rectangles with all dirty fields and arbitrary outer rows; B1 uses its elementary branch")


if __name__ == "__main__":
    print(json.dumps(run(),indent=2,sort_keys=True))
    print("PASS_PHYSICAL_COMPACT_RECTANGLES")
