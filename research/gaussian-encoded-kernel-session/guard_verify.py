"""Cheap actual-class guard calibration; no Axis/page/Core admission evidence.
Adapted from the independent boundary review's ten-port control, with credit
and substantial OpenAI assistance. Apache-2.0.
"""
import importlib.util
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('session_receipt_tools',HERE/'verify.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
v.pins()
sys.path.insert(0,str(v.SOURCE))
import gaussian_sources
cases=[]
with gaussian_sources.opened():
    spec=importlib.util.spec_from_file_location('guard_session_source',HERE/'kernel_session.py')
    service=importlib.util.module_from_spec(spec);spec.loader.exec_module(service)
    from cardinal_counts import Count
    from records import Tape
    from ring_words import Signed
    from scratch_pool import ScratchPool
    for choice in ('pool','output'):
        for index in range(5):
            # Deliberately stop before Axis setup: this tests the real run guard,
            # not successful computation by an incompletely initialized owner.
            owner=service.KernelSession.__new__(service.KernelSession)
            owner.closed=owner.pending=False
            owner.pool=ScratchPool(2);owner.output=Tape()
            resident=owner.pool.tapes[0] if choice=='pool' else owner.output
            values=[Count.literal(3) for _ in range(5)]
            actual=list(values)
            alias=object.__new__(Count);alias.tape=resident;actual[index]=alias
            signed=[]
            for magnitude in actual[3:]:
                value=object.__new__(Signed);value.magnitude=magnitude;value.negative=True;signed.append(value)
            original=Tape.read;traffic=[]
            def audited(tape):
                if tape is resident:traffic.append(tape.head)
                return original(tape)
            Tape.read=audited
            before=(bytes(resident.cells),resident.head)
            try:
                try:owner.run(signed[0],actual[0],signed[1],actual[1],actual[2])
                except ValueError as error:v.need(str(error)=='external session window parameters','exact alias rejection')
                else:raise ValueError('resident alias accepted')
            finally:
                Tape.read=original
                for value in values:value.close()
            v.need(not traffic and before==(bytes(resident.cells),resident.head),'no resident read/head/data mutation')
            cases.append((choice,index))
v.need(len(cases)==10,'all five ports and two resident owners')
print('PASS 10 actual-class guard-only cases; no Axis/page/Core replay')
