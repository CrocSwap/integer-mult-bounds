"""Exercise the binary handoff through two fitted preceding-stage roots."""
from pathlib import Path
import json
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
import native_sources
native_sources.activate()
from cardinal_counts import Count
from check_engine import fixture_engine,toy_plan
from check_payload import body,closed_work
from check_support import no_decode
from compact_counts import append_bits
from compact_engine import CompactEngine
from compact_layout import Layout
from provenance import Provenance
from records import Tape
from session import erase_marker,sealed_constructors
from words import need


def run():
    native,trace = fixture_engine(),[]
    class FittedFixture:
        def __getattr__(self,name):
            return getattr(native,name)
        def run(self,payload,width,before,middle,suffix):
            need(engine.scope.manager is None, "compact factory scope suspended at fitted entry")
            trace.append("native-entry")
            return native.execute_plan(payload,width,before,middle,suffix,toy_plan)
    engine = CompactEngine(("front","back"),None,"back",False,FittedFixture())
    def observe(stage,_payload,_returned):
        need(engine.scope.manager is None, "both C0 roots preserve the suspended parent scope")
        trace.append(stage)
    native.observe = observe
    widths,record = (Count.literal(5),Count.literal(5)),Count.literal(1)
    source = Tape()
    for address in range(1024):
        source.append((address*13 ^ address//7 ^ 5)&1)
    source.rewind()
    initial = body(source)
    observer = Provenance(1024)
    observer.mark(source)
    engine.rearm()
    with no_decode(),observer.installed(),sealed_constructors(),engine.scope.installed():
        plan = Layout(engine.names,widths,record)
        live = (*plan.radices.values(),plan.bits,plan.records,plan.row_bits,*widths,record)
        def snapshot():
            return [(id(value.tape),bytes(getattr(value.tape,"physical",value.tape).cells),value.tape.head) for value in live]
        saved = snapshot()
        owned = engine.pool.acquire()
        append_bits(source,owned)
        owned.rewind()
        output = engine.swap(owned,plan,"front","back")
        expected,masks = bytearray(1024),[0]*1024
        for address,bit in enumerate(initial):
            left,right = divmod(address,32)
            expected[right*32+left],masks[right*32+left] = bit,1<<address
        need(body(output) == expected and observer.masks(output.physical,1024) == tuple(masks),
             "complete fitted binary handoff for independent input columns")
        need(snapshot() == saved and body(source) == initial and source.head == 1,
             "fitted backend preserves live parent words and borrowed root")
        output.clear()
        plan.close()
        engine.pool.empty()
    for tape in engine.pool.tapes:
        erase_marker(tape)
    engine.closed = True
    closed_work(engine)
    need(trace == ["native-entry","before","after","before","after"], "two completed fitted C0 roots")
    result = dict(columns=1024,trace=trace,parent_peak=engine.pool.peak,native_roots=native.runtime.completed_roots,
                  scope="Declared reduced fitted B1 through the actual binary interface; isolated compact interchange seam")
    erase_marker(engine.output)
    source.clear()
    for value in (*widths,record):
        value.close()
    return result


if __name__ == "__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
    print("PASS_COMPACT_FITTED_BINARY_HANDOFF")
