"""Fail-closed source boundaries and large binary cardinalities, also under -O."""
import ast
from dataclasses import replace
from fractions import Fraction as F
from pathlib import Path

from binding import selected_episode
from check_sources import encoded_old
from check_support import audit, inspect_count, no_decode, reject
from counts import Count, high_power
from directory import Context, produce
import episode
from low_codes import LowCodes
from records import Tape, append_finite
from routes import compile_route, high_key
from matrices import Matrices
from words import Arena, Ring, need


def run():
    rejections=[]
    codes=LowCodes(3,2,2)
    rejections.append(reject(lambda:codes.rank(((1,2),(1,2))),"singular_low"))
    rejections.append(reject(lambda:codes.unrank(codes.size),"low_ordinal_overflow"))
    rejections.append(reject(lambda:codes.decode(codes.limit),"source_code_overflow"))
    large=LowCodes(3,64,2)
    huge_code=large.encode(1,True,large.unrank(large.size-1))
    tape=Tape()
    rejections.append(reject(lambda:append_finite(tape,huge_code,16),"sixteen_bit_source_truncation"))
    tape.clear()
    rejections.append(reject(lambda:compile_route(((1,0),(0,1)),((1,1),(1,1)),codes),"singular_chart"))
    arena,indices=Arena(5),Arena(8)
    mod=arena.input(9);ring=Ring(mod);context=Context(ring,codes)
    fields=indices.input(1);one=Count.literal(1)
    valid_code=codes.encode(1,True,((1,0),(0,1)))
    for name,old in (
        ("old_source_code",encoded_old(context,[((codes.limit,(0,0,0,0)),)])),
        ("old_high_digit",encoded_old(context,[((0,(3,0,0,0)),)])),
        ("trailing_old_field",encoded_old(context,[((0,(0,0,0,0)),(0,(0,0,0,0)))])),
    ):
        with no_decode():rejections.append(reject(lambda:produce(old,fields,one,valid_code,context),name))
        need(old.head==1,"rejected source head restoration")
        old.clear()
    zero=Count.literal(0);empty=Tape();no_fields=indices.input(0)
    with no_decode():
        rejections.append(reject(lambda:produce(empty,no_fields,zero,valid_code,context),"empty_old_domain"))
    zero.close();empty.clear();indices.free(no_fields)
    source=selected_episode()
    chart=((F(1),F(1)),(F(0),F(1)))
    model=replace(source,chart=chart)
    route=compile_route(((1,0),(0,1)),chart,codes)
    # These fail before any family lookup, directory generation or payload read.
    def physical(code, candidate=route):
        return episode.physical({},model,candidate,code,context,Tape(),fields,one,one,None)
    rejections.append(reject(lambda:physical(codes.encode(1,False,route.target_low)),"owner_code_after_route"))
    rejections.append(reject(lambda:physical(codes.encode(0,True,route.target_low)),"wrong_request_tag"))
    rejections.append(reject(lambda:physical(codes.encode(1,True,((1,0),(0,1)))),"stale_current_low"))
    wrong_route=compile_route(((1,0),(0,1)),((1,0),(0,1)),codes)
    rejections.append(reject(lambda:physical(codes.encode(1,True,wrong_route.target_low),wrong_route),"wrong_owner_chart"))
    broken=replace(source,targets=(source.source,)+source.targets[1:])
    rejections.append(reject(lambda:episode.staged(Tape(),{},broken,context,one,one,None),"copied_source_as_target"))
    values=(0,1,2,3,(1<<521)-1,(1<<522)+17)
    cases=[]
    for value in values:
        count=Count.literal(value)
        with no_decode():
            count.increment()
            high_power(count,ring,3,2)
        expected=(value+1)*81
        need(inspect_count(count)==expected,"unbounded source cardinality and carry")
        cases.append(expected.bit_length());count.close()
    with no_decode():rejections.append(reject(mod.inspect,"runtime_word_decode"))
    one.close();context.close();ring.close();arena.free(mod);indices.free(fields);audit(arena);audit(indices)
    here=Path(__file__).resolve().parent
    runtime=("counts.py","directory.py","routes.py","selection.py","episode.py","residual.py")
    for name in runtime:
        tree=ast.parse((here/name).read_text())
        for node in ast.walk(tree):
            if isinstance(node,ast.Attribute):
                need(node.attr not in ("inspect","cells","from_bytes"),"runtime source decoding barrier")
            if isinstance(node,ast.Call) and isinstance(node.func,ast.Name):
                need(node.func.id not in ("float","eval","exec"),"runtime numerical shortcut barrier")
    return {"rejections":rejections,"cardinality_cases":len(cases),"maximum_result_bits":max(cases),
            "runtime_modules_scanned":list(runtime)}
