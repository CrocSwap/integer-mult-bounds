"""Later-field rejection, policy reuse and a live parent handoff."""
from pathlib import Path
import json
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
import scalar_sources
scalar_sources.activate()
from cardinal_counts import Count
from check_support import no_decode
from compact_counts import append_bits
from records import Tape
from scalar_engine import ScalarEngine
from scalar_test_support import body,closed_work,fill,packet,snapshot
from scratch_pool import ScratchPool
from session import (OuterScope,borrowed_count,borrowed_tape,erase_marker,
                     sealed_constructors)
from signed_linear import CoefficientDomainError
from words import BLANK,need


def handoff():
    engine = ScalarEngine((("scale",-1,2,"scratch"),("add",1,2,"source_walk")))
    parent = ScratchPool(64)
    scope = OuterScope(parent)
    xs,ys = (64,-64,128,-128),(128,64,-64,-128)
    xraw,yraw = packet(xs,9),packet(ys,9)
    with no_decode(),sealed_constructors(),scope.installed():
        width,count,sentinel = Count.literal(9),Count.literal(2),Count.literal(12345)
        saved = snapshot((width,count,sentinel))
        left,right = parent.acquire(),parent.acquire()
        for tape,raw in ((left,xraw),(right,yraw)):
            for bit in raw:
                tape.append(bit)
            tape.rewind()
        with scope.suspended():
            returned = engine.run(borrowed_tape(left),None,borrowed_count(width),borrowed_count(count))
        middle = parent.acquire()
        append_bits(returned,middle)
        middle.rewind()
        returned.clear()
        erase_marker(returned)
        closed_work(engine,True)
        engine.select(("add",1,2,"source_walk"))
        with scope.suspended():
            returned = engine.run(borrowed_tape(middle),borrowed_tape(right),borrowed_count(width),borrowed_count(count))
        result = parent.acquire()
        append_bits(returned,result)
        result.rewind()
        returned.clear()
        erase_marker(returned)
        need(body(result) == packet([(y-x)//2 for x,y in zip(xs,ys)],9), "nested scalar macro endpoint")
        need(body(left) == xraw and body(right) == yraw and snapshot((width,count,sentinel)) == saved,
             "scalar handoff preserves live parent objects")
        closed_work(engine,True)
        for tape in (left,right,middle,result):
            tape.clear()
        for value in (width,count,sentinel):
            value.close()
        parent.empty()
    for tape in parent.tapes:
        erase_marker(tape)
    need(all(all(bit == BLANK for bit in tape.cells) for tape in parent.tapes), "erased scalar caller work")
    return dict(parent_peak=parent.peak,scalar_peak=engine.pool.peak,live_parent_counts=3)


def run():
    literals = (("scale",-1,2,"scratch"),("scale",1,2,"scratch"),
                ("add",1,2,"target_walk"),("add",1,2,"source_walk"),("add",3,4,"source_walk"))
    engine = ScalarEngine(literals)
    width,count = Count.literal(3),Count.literal(2)
    saved = snapshot((width,count))
    left,right = Tape(),Tape()
    cases = ((literals[0],[0,0,0,-4],None,"headroom"),
             (literals[1],[0,0,0,3],None,"inexact"),
             (literals[2],[0,0,0,2],[0,0,0,0],"headroom"),
             (literals[4],[0,0,0,0],[0,0,0,2],"inexact"))
    for literal,xs,ys,category in cases:
        xraw,yraw = packet(xs,3),None if ys is None else packet(ys,3)
        fill(left,xraw)
        if yraw is not None:
            fill(right,yraw)
        engine.select(literal)
        with no_decode():
            try:
                engine.run(left,right if ys is not None else None,width,count)
            except CoefficientDomainError as error:
                need(category in str(error), "named later-field scalar rejection")
            else:
                raise ValueError("invalid later scalar prefix accepted")
        need(body(left) == xraw and left.head == 1 and
             (yraw is None or (body(right) == yraw and right.head == 1)) and snapshot((width,count)) == saved,
             "scalar rejection preserves original complete operands")
        closed_work(engine,True)
    # The previous target-walk fixture has a valid endpoint but an invalid
    # doubling prefix. The source-walk policy accepts those same operands.
    fill(left,packet([0,0,0,2],3))
    fill(right,packet([0,0,0,0],3))
    engine.select(literals[3])
    with no_decode():
        returned = engine.run(left,right,width,count)
    need(body(returned) == packet([0,0,0,2],3), "valid policy retry after scalar rejection")
    closed_work(engine)
    returned.clear()
    erase_marker(returned)
    left.clear()
    right.clear()
    width.close()
    count.close()
    return dict(later_rejections=len(cases),valid_policy_retry=True,peak=engine.pool.peak,handoff=handoff(),
                scope="Named later-field prefix rejection, input/descriptor preservation, closed output and nested parent reuse")


if __name__ == "__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
    print("PASS_PHYSICAL_SCALAR_RETURNS")
