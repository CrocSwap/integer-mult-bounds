"""Independent gap, peel and generated-weight endpoint checks."""
from hashlib import sha256
from itertools import product
import sys
from time import monotonic

from cardinal_counts import Count
from catalogue import Catalogue, Specifications
from check_runtime import Tracker, destination
from check_support import audit, bits, inspect_count, no_decode
from consumer import IncomingWeights
from directory import Context
from layout import Layout
import model
from numeric import Geometry
import oracle
import peel
from plan import Plan
from records import Fields, Program, Tape
from words import Arena, Ring, need


def extents():
    arena,indices=Arena(5),Arena(11)
    mod=arena.input(9);ring=Ring(mod)
    columns,depth=indices.input(1),indices.input(0)
    before,gap,suffix=Count.literal(2),Count.literal(5),Count.literal(7)
    checks=0
    for n in (64,65,95,127):
        size=indices.input(n)
        geometry=Geometry(Plan(64,1,True,()),indices,columns,depth,0,object())
        layout=Layout(geometry,size,ring,3,before,gap,suffix)
        for a,b in ((0,1),(0,127),(63,64),(64,65),(126,127)):
            first,second=indices.input(a),indices.input(b)
            with no_decode():result=layout.extents(first,second)
            x=a if a<64 else a+2*(n-64)
            y=b if b<64 else b+2*(n-64)
            expected=[2*9**x*(5 if x>=n else 1),9**(y-x-1)*(5 if x<n<=y else 1),
                      7*9**(2*n-1-y)*(5 if y<n else 1)]
            need([inspect_count(value) for value in result]==expected,"independent gap placement in each extent")
            need(expected[0]*9*expected[1]*9*expected[2]==2*5*7*9**(2*n),"complete gapped fibre volume")
            for value in result:value.close()
            indices.free_many(first,second);checks+=1
        for a in (0,63,64,127):
            first=indices.input(a)
            with no_decode():result=layout.extents(first)
            x=a if a<64 else a+2*(n-64)
            need([inspect_count(value) for value in result]==
                 [2*9**x*(5 if x>=n else 1),7*9**(2*n-1-x)*(5 if x<n else 1)],
                 "independent sign gap placement")
            for value in result:value.close()
            indices.free(first);checks+=1
        layout.close();geometry.close();indices.free(size)
    before.close();gap.close();suffix.close();ring.close();arena.free(mod)
    indices.free_many(columns,depth);audit(arena);audit(indices)
    return {"geometry_cases":checks,"widths":[64,65,95,127],"gap":5}


def complete_gapped():
    started=monotonic()
    catalogue=model.Catalogue();arena,indices=Arena(3),Arena(8)
    mod=arena.input(3);ring=Ring(mod);context=Context(ring,catalogue.codes)
    size,depth=indices.input(3),indices.input(0);program=object()
    incoming=model.Incoming(context,indices,(1,2,2))
    consumer=model.Consumer(context,indices,program,size,depth,catalogue,incoming)
    old=Tape();old_count,rows=Count.literal(1),Count.literal(1)
    before,gap,suffix=Count.literal(6),Count.literal(5),Count.literal(2)
    length=6*3**6*5*2;tracker=Tracker();source=tracker.source(length,linear=False)
    original=bytes(source.cells)
    with tracker.install(),no_decode():
        current=peel.run(source,context,indices,size,depth,program,old,old_count,rows,before,gap,suffix,incoming)
    for address in range(length):
        target=destination(address,3,3,(1,2,2),5,2,active=(2,))
        need(current.origins.get(target+1)==address,"complete peeled middle and gap endpoint")
    print("complete gapped peel",round(monotonic()-started,3),file=sys.stderr,flush=True)
    with tracker.install(),no_decode():
        for identifier in (6,7):
            following=consumer.apply(current,identifier,False,((1,0),(0,1)),old,old_count,before,gap,suffix)
            current.clear();current=following
    for address in range(length):
        target=destination(address,3,3,(1,2,2),5,2)
        need(current.origins.get(target+1)==address and current.cells[target+1]==original[address+1],
             "complete gap-aware peel and complementary core")
    need(destination(39125,3,3,(1,2,2),5,2)==43689,"independent nontrivial spectator marker")
    need(tracker.live=={source,current} and bytes(source.cells)==original and
         source.head==current.head==old.head==1,"gapped source and scratch ownership")
    result={"bank_atoms":3,"core_atoms":2,"before":6,"gap":5,"suffix":2,"bits":length,
            "peel_pairs":1,"marker":[39125,43689],"children":dict(consumer.children),
            "payload_sha256":sha256(bits(current)).hexdigest(),"erased_tapes":tracker.erased}
    source.clear();current.clear();old.clear();incoming.close()
    for count in (old_count,rows,before,gap,suffix):count.close()
    context.close();ring.close();arena.free(mod);indices.free_many(size,depth);audit(arena);audit(indices)
    print("complete gapped endpoint",round(monotonic()-started,3),file=sys.stderr,flush=True)
    return result


def selected_peel(catalogue=None):
    catalogue=Catalogue(3) if catalogue is None else catalogue
    specifications=Specifications(catalogue)
    identifier=next(i for i,r in enumerate(catalogue.requests) if r.base.rank==5)
    template=catalogue.template_for(identifier,True)
    prepared=oracle.eye(64)
    prepared[4][4],prepared[4][5],prepared[5][4],prepared[5][5]=1,1,3,4
    raw=oracle.multiply(prepared,oracle.inverse(oracle.reduce_rational(template.preparation,9),9),9)
    low=tuple(tuple(x%3 for x in row) for row in raw)
    high=tuple(tuple(x//3 for x in row) for row in raw)
    spec=specifications.bind(identifier,True,low)
    need(spec.good,"generated selected rank-five ancestor")
    arena,indices=Arena(5),Arena(11)
    mod=arena.input(9);ring=Ring(mod);context=Context(ring,catalogue.codes)
    program=Program.fixture(indices,arena,832,2,[(0,spec.code,5,0,False,False)],catalogue.codes.bits)
    fields=Fields.fixture(indices,arena,[(spec.code,high)],catalogue.codes.bits)
    original_program,original_fields=bytes(program.tape.cells),bytes(fields.tape.cells)
    size,depth,columns=indices.input(65),indices.input(1),indices.input(1)
    incoming=IncomingWeights(context,indices,program,specifications,size,depth)
    geometry=Geometry(Plan(64,1,True,()),indices,columns,depth,0,program)
    rows=[{i:1} for i in range(130)];scalars=[];iterator=peel.events(geometry,size)
    while True:
        try:
            with no_decode():event=next(iterator)
        except StopIteration:break
        first=event.first.inspect();second=event.second.inspect() if event.second is not None else None
        if event.kind=="atom_swap":rows[first],rows[second]=rows[second],rows[first]
        elif event.kind=="sign":rows[first]={i:-a%9 for i,a in rows[first].items()}
        else:
            with no_decode():word=incoming.coefficient(fields.tape,event.request)
            coefficient=word.inspect();arena.free(word);scalars.append(coefficient)
            for i,a in rows[second].items():
                value=(rows[first].get(i,0)+coefficient*a)%9
                if value:rows[first][i]=value
                else:rows[first].pop(i,None)
    expected=[{i:1} for i in range(130)];expected[64],expected[65]={65:8},{64:8}
    need(rows==expected and scalars==[8,1,8],"original generated A64 remainder offset")
    from plan import Request
    zero=indices.zero()
    with no_decode():wrong=incoming.coefficient(fields.tape,Request("incoming",zero))
    need(wrong.inspect()==2,"wrong zero offset has a distinct coefficient")
    arena.free(wrong);indices.free(zero)
    need(bytes(program.tape.cells)==original_program and bytes(fields.tape.cells)==original_fields,
         "no child extension or fresh field during peel")
    result={"root_atoms":832,"parent_atoms":65,"ancestor_rank":5,"frozen_fields":1,
            "source_code_bits":catalogue.codes.bits,"peel_scalars":scalars,
            "head64_to_tail0":8,"tail0_to_head64":8,"wrong_offset_weight":2,"columns":130}
    geometry.close();context.close();program.tape.clear();fields.tape.clear();ring.close();arena.free(mod)
    indices.free_many(size,depth,columns);audit(arena);audit(indices)
    return result
