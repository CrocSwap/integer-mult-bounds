"""Reject a later C/add field, erase owned work and reuse the same inventory."""
from pathlib import Path
import json
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
import leaf_sources
leaf_sources.activate()
from cardinal_counts import Count
from check_support import no_decode
from coefficient_engine import CoefficientEngine
from compact_counts import append_bits
from leaf_test_support import body,closed_work,oracle,packet,snapshot
from records import Tape
from scratch_pool import ScratchPool
from session import OuterScope,borrowed_count,borrowed_tape,erase_marker,sealed_constructors
from signed_linear import CoefficientDomainError
from words import BLANK,need


def fill(tape,raw):
    tape.clear()
    for bit in raw:
        tape.append(bit)
    tape.rewind()


def nested_handoff():
    engine = CoefficientEngine(("v0",),"v0")
    parent = ScratchPool(64)
    scope = OuterScope(parent)
    raw = packet([3,3,3,3],3)
    with no_decode(),sealed_constructors(),scope.installed():
        width = Count.literal(1)
        args = tuple(Count.literal(value) for value in (1,1,0,3,1,1))
        gaussians = Count.literal(2)
        saved = snapshot((width,*args,gaussians))
        payload = parent.acquire()
        for bit in raw:
            payload.append(bit)
        payload.rewind()
        with scope.suspended():
            returned = engine.run_leaf(borrowed_tape(payload),(borrowed_count(width),),
                                       *(borrowed_count(value) for value in args))
        first = parent.acquire()
        append_bits(returned,first)
        first.rewind()
        returned.clear()
        erase_marker(returned)
        need(body(first) == raw and body(payload) == raw and snapshot((width,*args,gaussians)) == saved,
             "leaf handoff preserves live parent objects")
        closed_work(engine,True)
        with scope.suspended():
            returned = engine.run_add(borrowed_tape(first),borrowed_tape(payload),
                                      borrowed_count(args[3]),borrowed_count(gaussians),True)
        second = parent.acquire()
        append_bits(returned,second)
        second.rewind()
        returned.clear()
        erase_marker(returned)
        need(body(second) == packet([0]*4,3) and body(first) == body(payload) == raw and
             snapshot((width,*args,gaussians)) == saved, "aligned-add handoff preserves live parent objects")
        closed_work(engine,True)
        for tape in (payload,first,second):
            tape.clear()
        for value in (width,*args,gaussians):
            value.close()
        parent.empty()
    for tape in parent.tapes:
        erase_marker(tape)
    need(all(all(cell == BLANK for cell in tape.cells) for tape in parent.tapes), "closed parent handoff work")
    return dict(parent_peak=parent.peak,child_peak=engine.pool.peak,live_parent_counts=8,
                scope="Suspended parent factories, physical borrowed views, copied protected returns and valid original leases")


def run():
    fields = (("before",1),("v0",1),("tail",1))
    engine = CoefficientEngine(tuple(name for name,_ in fields),"v0")
    widths = tuple(Count.literal(width) for _name,width in fields)
    args = [Count.literal(value) for value in (1,1,0,3,2,2)]
    saved = snapshot((*widths,*args))
    source,other = Tape(),Tape()
    outcomes = []
    # Final row/prefix, final tail address and coefficient field: records13/15.
    for bad_left,bad_right,message in (((1,0),(0,0),"inexact"),((3,-3),(3,3),"headroom")):
        values = [0]*64
        values[54:56],values[62:64] = bad_left,bad_right
        raw = packet(values,3)
        fill(source,raw)
        for inverse in (False,True):
            with no_decode():
                try:
                    engine.run_leaf(source,widths,*args,inverse=inverse)
                except CoefficientDomainError as error:
                    need(message in str(error), "named C coefficient rejection")
                else:
                    raise ValueError("invalid last C coefficient accepted")
            need(body(source) == raw and source.head == 1 and snapshot((*widths,*args)) == saved,
                 "C rejection preserves borrowed packet and descriptors")
            closed_work(engine,True)
            outcomes.append((message,inverse))
    good = packet([3]*64,3)
    fill(source,good)
    with no_decode():
        returned = engine.run_leaf(source,widths,*args)
    need(body(returned) == oracle(good,fields,"v0",1,1,0,3,2,2) == good,
         "valid C retry after parity and overflow rejection")
    closed_work(engine)
    returned.clear()
    erase_marker(returned)

    gaussian_count = Count.literal(2)
    add_saved = snapshot((args[3],gaussian_count))
    for left_values,right_values,subtract in (([0,0,3,0],[0,0,1,0],False),
                                              ([0,0,-4,0],[0,0,1,0],True)):
        left_raw,right_raw = packet(left_values,3),packet(right_values,3)
        fill(source,left_raw)
        fill(other,right_raw)
        with no_decode():
            try:
                engine.run_add(source,other,args[3],gaussian_count,subtract)
            except CoefficientDomainError as error:
                need("headroom" in str(error), "named aligned-add rejection")
            else:
                raise ValueError("invalid later aligned component accepted")
        need(body(source) == left_raw and body(other) == right_raw and source.head == other.head == 1 and
             snapshot((args[3],gaussian_count)) == add_saved, "aligned rejection preserves both borrowed operands")
        closed_work(engine,True)
    fill(source,packet([-4]*4,3))
    fill(other,packet([-4]*4,3))
    with no_decode():
        returned = engine.run_add(source,other,args[3],gaussian_count,True)
    need(body(returned) == packet([0]*4,3), "most-negative subtraction retry without separate negation")
    closed_work(engine)
    returned.clear()
    erase_marker(returned)
    source.clear()
    other.clear()
    for value in (*widths,*args,gaussian_count):
        value.close()
    return dict(C_rejections=outcomes,add_rejections=2,reused=True,peak=engine.pool.peak,handoff=nested_handoff(),
                scope="Later-field named parity/headroom rejections preserve borrows, erase partial outputs and allow C/add cross-method reuse")


if __name__ == "__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
    print("PASS_GAUSSIAN_COEFFICIENT_REJECTION")
