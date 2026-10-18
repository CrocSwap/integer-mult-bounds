"""Sampled distinct high fields through one shared gapped residual trace."""
from collections import Counter
from hashlib import sha256

from cardinal_counts import Count
from check_runtime import Tracker
from check_support import audit, bits, no_decode
from directory import Context
from forms import good_form
from layout import Layout
from matrices import Matrices
import model
from numeric import Geometry, Page
import oracle
import packet_engine
from plan import compile_plan
from records import BLANK, RECORD_END, Tape, append_finite, append_word, read_finite, read_word
from trace import execute
from words import Arena, Ring, need


def residual_address(address,projector,weights,modulus,gap):
    size=len(weights);bank=modulus**size
    rest,tail=divmod(address,bank);head,g=divmod(rest,gap)
    h,d=[0]*size,[0]*size
    for i in range(size-1,-1,-1):head,h[i]=divmod(head,modulus);tail,d[i]=divmod(tail,modulus)
    vector=[(d[size-1-i]-pow(weights[i],-1,modulus)*h[i])%modulus for i in range(size)]
    applied=[sum(a*b for a,b in zip(row,vector))%modulus for row in projector]
    for i in range(size):
        h[i]=(h[i]+weights[i]*applied[i])%modulus
        d[size-1-i]=(d[size-1-i]-applied[i])%modulus
    head=tail=0
    for a,b in zip(h,d):head=modulus*head+a;tail=modulus*tail+b
    return (head*gap+g)*bank+tail


def sampled_packet():
    catalogue=model.Catalogue();arena,indices=Arena(5),Arena(8)
    mod=arena.input(9);ring=Ring(mod);context=Context(ring,catalogue.codes)
    size,depth,columns,field_count=(indices.input(x) for x in (2,0,1,1))
    low=((1,1),(0,1));highs=((0,0,0,0),(0,0,1,0));code=catalogue.codes.encode(0,True,low)
    before,gap,suffix,prefixes=(Count.literal(x) for x in (1,3,1,2))
    incoming=model.Incoming(context,indices,(2,1))
    low_p=oracle.multiply([[row[0]] for row in low],oracle.inverse(low,3)[:1],3)
    plan=compile_plan(low_p,1,3,True);program=object()
    geometry=Geometry(plan,indices,columns,depth,code,program)
    layout=Layout(geometry,size,ring,3,before,gap,suffix)
    directory=Tape()
    for high in highs:
        append_finite(directory,code,catalogue.codes.bits)
        for value in high:
            word=arena.input(value);append_word(directory,word);arena.free(word)
        directory.append(RECORD_END)
    directory.rewind();original_directory=bytes(directory.cells)
    def coefficient(prefix,reference):
        need(read_finite(prefix,catalogue.codes.bits)==code,"sampled current source field")
        high=[[read_word(prefix,arena) for _ in range(2)] for _ in range(2)]
        need(prefix.read()==RECORD_END,"sampled high record boundary")
        prefix.step(1);need(prefix.read()==BLANK,"complete sampled prefix");prefix.rewind()
        matrices=Matrices(ring)
        header=matrices.raw_header(low,high,3);projector=matrices.projector(header,1)
        page=Page(plan,good_form(projector,1,ring),ring,indices,columns,incoming.weight,depth,code,program)
        value=page.evaluate(reference);page.close()
        for matrix in (high,header,projector):matrices.free(matrix)
        return value
    tracker=Tracker();body=3*9**4;source=tracker.source(2*body,linear=False)
    original=bytes(source.cells);boundaries=Counter()
    with tracker.install(),no_decode():
        output=packet_engine.run(source,execute(geometry),layout,directory,prefixes,field_count,coefficient,
                                 observe=lambda kind:boundaries.update([kind]))
    for position,high in enumerate(highs):
        raw=[[low[i][j]+3*high[2*i+j] for j in range(2)] for i in range(2)]
        projector=oracle.multiply([[row[0]] for row in raw],oracle.inverse(raw,9)[:1],9)
        for address in range(body):
            target=residual_address(address,projector,(2,1),9,3)
            old_index,new_index=position*body+address,position*body+target
            need(output.origins.get(new_index+1)==old_index and output.cells[new_index+1]==original[old_index+1],
                 "per-prefix coefficients and gapped high-packet endpoint")
    need(boundaries=={"enter":1,"return":1} and tracker.live=={source,output} and
         bytes(source.cells)==original and bytes(directory.cells)==original_directory,
         "one sampled whole-packet child and closed scratch")
    result={"dimension":2,"width":2,"high_prefixes":2,"complete_high_cube":False,"gap":3,
            "bits":2*body,"children":dict(boundaries),"erased_tapes":tracker.erased,
            "payload_sha256":sha256(bits(output)).hexdigest()}
    source.clear();output.clear();directory.clear();incoming.close();layout.close();geometry.close()
    for value in (before,gap,suffix,prefixes):value.close()
    context.close();ring.close();arena.free(mod);indices.free_many(size,depth,columns,field_count)
    audit(arena);audit(indices)
    return result
