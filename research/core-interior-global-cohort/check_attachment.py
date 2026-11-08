"""Literal physical attachment witness: actual first H, paid gather and return.

This executes one actual emitted prefix, not the whole 1,105-stage cohort.
Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
"""
from hashlib import sha256
import json
from pathlib import Path
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parent))
from cohort_sources import opened as source_opened,need
from core_layout import Layout
from core_caller import prepare
from physical_loader import opened as physical_opened
from physical_adapter import PreparedOuter,owner
from fixture_tools import certified_floors


class ActualPrefix:
    def __init__(self,program,event_type):
        self.program = program
        self.event = next(program.events())
        need(isinstance(self.event,event_type) and self.event.step == 0,
             'actual first global H source event')
        self.stages,self.h_count,self.diagonal_count = 1,1,0

    def __getattr__(self,key):
        return getattr(self.program,key)

    def validate(self):
        self.program.validate()
        need(next(self.program.events()) == self.event,'same literal actual source prefix')

    def events(self):
        self.validate()
        yield self.event


def rejected(action,label):
    try:
        action()
    except ValueError:
        return label
    raise ValueError('accepted physical attachment control: '+label)


def main():
    started = time.monotonic()
    with source_opened() as runtime:
        ref = runtime.reference.Reference(runtime.raw,63,1,3,1,1,160)
        layout = Layout((1,6),(1,),5)
        program = prepare(runtime,layout,[ref],['narrow'],[2],
                          [[False],[True],[False],[True]],target=6,radius_bits=1)
        types = (runtime.global_compiler.Hadamard,runtime.global_compiler.Diagonal)
        prefix = ActualPrefix(program,types[0])
        input_values = [(0,0)]*program.records
        input_values[1],input_values[4],input_values[11] = (1,0),(0,1),(-1,1)
        # Independent original-coordinate H on actual selected axis bit 1.
        expected = [list(z) for z in input_values]
        stride = 1 << layout.starts[layout.selected[0]]
        for base in range(0,len(expected),2*stride):
            for low in range(stride):
                i,j = base+low,base+low+stride
                a,b = input_values[i],input_values[j]
                expected[i] = [(a[k]+b[k]) << program.bits for k in (0,1)]
                expected[j] = [(a[k]-b[k]) << program.bits for k in (0,1)]
    with physical_opened() as state:
        from records import Tape
        from session import erase_marker
        from physical_controls import emit_signed
        from check_support import bits,no_decode
        from words import BLANK
        import check_composed
        root,visits = check_composed.fixture('standard',False)
        consumer = owner(root)
        prepared = PreparedOuter(prefix,state,types)
        payload = Tape()
        for pair in input_values:
            for value in pair:
                emit_signed(payload,value,prepared.full.metadata['incoming_width'])
        payload.rewind()
        borrowed = (payload,prepared.forward,prepared.inverse,prepared.full.code,
                    *(x.tape for x in (*prepared.parameters,*prepared.full.parameters)))
        saved = [(bytes(t.cells),t.head) for t in borrowed]
        controls=[rejected(lambda:prepared.run(consumer,consumer.output),
                           'outer private protected payload port'),
                  rejected(lambda:consumer.run(payload,payload,prepared.inverse,prepared.full.code,
                           *prepared.parameters,*prepared.full.parameters),
                           'aliased payload and forward route code')]
        need(saved == [(bytes(t.cells),t.head) for t in borrowed],
             'pre-traffic alias rejection preserves every external port')
        bases = (program.axes,len(layout.gather),program.data_width,
                 program.data_width+program.axes,program.data_width+2*program.axes)
        try:
            with certified_floors(bases) as (floors,calls,misses):
                with no_decode():
                    returned = prepared.run(consumer,payload)
                result = bits(returned)
                need(result == check_composed.encode(expected,program.data_width),
                     'physical original-coordinate source prefix endpoint')
                wrong=[list(z) for z in input_values]
                for i in range(0,len(wrong),2):
                    a,b=input_values[i],input_values[i+1]
                    wrong[i]=[(a[k]+b[k]) << program.bits for k in (0,1)]
                    wrong[i+1]=[(a[k]-b[k]) << program.bits for k in (0,1)]
                need(result != check_composed.encode(wrong,program.data_width),
                     'omitted original-coordinate gather changes observed endpoint')
                controls.append('omitted gather applies H to spectator bit')
                need(saved == [(bytes(t.cells),t.head) for t in borrowed],
                     'all original borrowed payload control and metadata heads restored')
                consumer.idle()
                need(consumer.closed and consumer.current is None and not consumer.pool.live,
                     'closed original-coordinate wrapper')
                need(all(t.head == 1 and all(x == BLANK for x in t.cells)
                         for t in (*consumer.pool.tapes,*consumer.full.pool.tapes)),
                     'complete owned wrapper body and marker erasure')
                need(not misses,'complete finite metadata specialization domain')
                need(all(v==0 for v in consumer.calls.values()),
                     'production wrapper diagnostics remain finite null counters')
                receipt = dict(status='PASS_ACTUAL_CORE_PHYSICAL_PREFIX',records=program.records,
                    full_source_stages=program.stages,executed_source_events=1,
                    complete_global_cohort_executed=False,layout=layout.record(),
                    grid=program.bits,width=program.data_width,prefix_mask=prefix.event.positions,
                    input_source_directions=program.directions,output_sha256=sha256(result).hexdigest(),
                    output_bits=len(result),metadata_bases=sorted(set(bases)),
                    metadata_floor_calls=len(calls),borrowed_tapes=len(borrowed),
                    negative_controls=controls,
                    native_fixture='unchanged standard q2 fixture; no production rate claim',
                    actual_elapsed_seconds=time.monotonic()-started)
                print(json.dumps(receipt,sort_keys=True),flush=True)
                returned.clear()
                erase_marker(returned)
        finally:
            prepared.close()
            payload.clear()
            erase_marker(payload)


if __name__ == '__main__':
    main()
