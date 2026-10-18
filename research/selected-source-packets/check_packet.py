"""Complete two-digit body packet through owner route, producer and residual."""
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
import sys
from time import monotonic

import bitstream
import cardinality
from check_caller import SmallResidual, expected_rows
from check_sources import encoded_old
from check_support import Origins, audit, bits, no_decode
from counts import Count
from directory import Context, produce
from low_codes import LowCodes
import oracle
import packet
import stream
from routes import compile_route, inverse_rational, route_packet
from words import Arena, Ring, need


def complete_packet():
    started=monotonic()
    codes=LowCodes(3,2,2)
    arena,indices=Arena(5),Arena(8)
    mod=arena.input(9);ring=Ring(mod);context=Context(ring,codes)
    low=((1,1),(0,1))
    chart=((F(1,2),F(1)),(F(-1),F(2)))
    owner_low=tuple(map(tuple,oracle.multiply(low,oracle.reduce_rational(inverse_rational(chart),3),3)))
    route=compile_route(owner_low,chart,codes)
    code=codes.encode(1,True,low)
    fields,size=indices.input(1),indices.input(2)
    count,fibre=Count.literal(1),Count.literal(9**4)
    old=encoded_old(context,[((codes.encode(0,False,((1,0),(0,1))),(2,1,0,2)),)])
    original_old=bytes(old.cells)
    origins=Origins();source=origins.source(81*9**4);original=bytes(source.cells)
    with no_decode():
        routed=route_packet(source,route,context,count,fibre,origins.factory)
        directory,prefixes=produce(old,fields,count,code,context)
    original_directory=bytes(directory.cells)
    print("complete owner route and directory",round(monotonic()-started,3),file=sys.stderr,flush=True)
    residual=SmallResidual(context,indices,fields,size,code,low,origins.factory)
    previous=bitstream.Tape,cardinality.Tape,stream.Tape,packet.Tape
    bitstream.Tape=origins.factory
    cardinality.Tape=stream.Tape=packet.Tape=origins.control_factory
    try:
        with no_decode():output=residual(routed,directory,prefixes)
    finally:bitstream.Tape,cardinality.Tape,stream.Tape,packet.Tape=previous
    print("complete produced packet residual",round(monotonic()-started,3),file=sys.stderr,flush=True)
    body=9**4
    for old_prefix,high in enumerate(product(range(3),repeat=4)):
        native=[[owner_low[i][j]+3*high[2*i+j] for j in range(2)] for i in range(2)]
        common=oracle.multiply(native,oracle.reduce_rational(chart,9),9)
        prefix=0
        for row in common:
            for value in row:prefix=3*prefix+value//3
        projector=oracle.multiply([[row[0]] for row in common],oracle.inverse(common,9)[:1],9)
        matrix=expected_rows(projector,(2,2),9)
        for address,digits in enumerate(product(range(9),repeat=4)):
            destination=0
            for row in matrix:destination=9*destination+sum(x*y for x,y in zip(row,digits))%9
            before,after=old_prefix*body+address,prefix*body+destination
            need(output.origins.get(after+1)==before and output.cells[after+1]==original[before+1],
                 "complete routed/produced/residual bit origin")
    need(origins.live=={source,routed,output} and bytes(source.cells)==original and
         bytes(old.cells)==original_old and bytes(directory.cells)==original_directory,
         "source, fields and local work ownership")
    need(all(tape.head==1 for tape in (source,routed,output,old,directory)) and
         residual.calls==1 and residual.boundaries=={"enter":1,"return":1},
         "whole-packet entry and return")
    result={"dimension":2,"width":2,"highs":81,"bits":81*body,"old_fields":1,
            "child_entries":1,"child_returns":1,"erased_scratch_tapes":origins.erased,
            "payload_sha256":sha256(bits(output)).hexdigest(),
            "directory_sha256":sha256(original_directory).hexdigest()}
    for tape in (source,routed,output,old,directory):tape.clear()
    prefixes.close();count.close();fibre.close();residual.close();context.close();ring.close()
    arena.free(mod);indices.free_many(fields,size);audit(arena);audit(indices)
    return result
