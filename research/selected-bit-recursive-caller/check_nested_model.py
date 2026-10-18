"""A complete two-level physical caller, over a deliberately small toy source.

This checker alone uses q=2, dimension/cutoff 2, one family and the two
complementary rank-one MOVE residuals. The root uses coordinate projectors;
every child uses all conjugated GL2 projectors and their full good/fallback
normal forms. It executes every GL2(F2) low class,
all 36 fresh root rows, and all 256 body addresses.  It is not the selected
odd-prime source and does not certify the GL64 endpoint by finite execution.
The production Node, Driver, recursive packet engine, trace, projected
layout, directory, row split/merge and physical primitives execute unchanged.
Only the source, coefficient grammar and fixed leaf cutoff are toy inputs.
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import sys
from time import monotonic

sys.path.insert(0,str(Path(__file__).resolve().parent))
import bootstrap
from cardinal_counts import Count
from check_runtime import Tracker, destination
from check_support import no_decode
from directory import Context, produce
from forms import fallback_form, good_form
from layout import Layout
from low_codes import LowCodes
from matrices import Matrices
from model import I, S, Request
from node import Node
from numeric import Geometry, Page
import oracle
import packet_engine
from plan import Plan, compile_plan
from records import Tape
from scheduler import Invocation
from topology import Call, Owner
from trace import child as child_trace, execute
from words import Arena, Ring, Unsigned, need


class ToyCodes(LowCodes):
    def __init__(self):
        # Fixed checker vocabulary.  Production LowCodes keeps its q>=3 guard.
        self.q,self.dimension,self.requests=2,2,2
        self.radices=(3,2)
        self.size,self.limit,self.bits=6,24,5


class Catalogue:
    def __init__(self):
        self.codes=ToyCodes()
        self.requests=(Request("MOVE",0,0),Request("MOVE",1,0))

    def low_classes(self):
        for ordinal in range(6):yield self.codes.unrank(ordinal)


class Topology:
    families=replicas=1
    schedule=({"kind":"local_cover_sweep","stage":0},)

    def __init__(self,catalogue):self.catalogue=catalogue

    def call(self,stage,replica):
        need(stage==replica==0,"toy single selected sweep")
        return Call(0,0,(Owner(0,I),),(0,),(2,),
                    ((0,0,0,1,1,0),(0,0,1,2,1,0)),(0,1),False)

    @staticmethod
    def matrix(chart):return chart


class UnitIncoming:
    """The only nonzero coefficient over F2 is one, for every frozen prefix."""
    def __init__(self,context):self.context=context
    def weight(self,index):return self.context.arena.copy(self.context.ring.one)
    def coefficient(self,prefix,request):
        need(request.kind=="incoming","toy incoming request")
        return self.weight(request.coordinate)


class Consumer:
    recursive=True

    def __init__(self,context,indices,program,size,depth,catalogue,topology,
                 incoming,plans,tracker,counters,root_axes=False,root_level=False):
        self.context,self.indices,self.program=context,indices,program
        self.size,self.depth=size,depth
        self.catalogue,self.topology,self.incoming=catalogue,topology,incoming
        self.plans,self.tracker,self.counters=plans,tracker,counters
        self.root_axes=root_axes
        self.root_level=root_level

    def apply(self,source,identifier,common,low,old_directory,old_count,
              before,gap,suffix,observe=None,child_stock=None,child_before=None):
        need(common and identifier in (0,1),"toy bound MOVE source")
        context,indices=self.context,self.indices
        expected_stock=Count.literal(6 if self.root_level else 1)
        try:
            need(child_stock is not None and expected_stock.equals(child_stock),
                 "nested model exact independent unused stock")
            self.counters["root_stock_checks" if self.root_level else "child_stock_checks"]+=1
        finally:expected_stock.close()
        plan,constants=self.plans[(identifier,low)]
        if self.root_axes:plan=Plan(2,1,True,())
        code=context.codes.encode(identifier,common,low)
        directory,prefixes=produce(old_directory,self.depth,old_count,code,context)
        divisor,one=indices.literal(2),indices.literal(1)
        columns,remainder=Unsigned(indices).divmod(self.size,divisor)
        indices.free_many(divisor,remainder)
        geometry=Geometry(plan,indices,columns,self.depth,code,self.program)
        # A checker-only scale reduction makes width two an actual internal
        # call. Production Geometry's cutoff remains exactly64.
        indices.free(geometry.leaf_cutoff)
        geometry.leaf_cutoff=indices.literal(2)
        fields=geometry.plus(self.depth,one);indices.free(one)
        layout=Layout(geometry,self.size,context.ring,context.q,before,gap,suffix)

        def coefficient(prefix,request):
            # At fixed q=2,w=1 all high fields are zero and all unit weights
            # are one. These finite coefficients were compiled beforehand.
            if request.kind=="child":return context.arena.copy(context.ring.one)
            key=(request.reference,request.reverse_adapter)
            return context.arena.literal(constants[key])

        def invoke(current,event):
            self.counters["internal_calls"]+=1
            need(child_stock is not None and child_before is not None,"toy separate unused stock")
            extents=layout.child_extents(event.first,event.second,event.width,before=child_before)
            child_program=object()
            child=Consumer(context,indices,child_program,event.width,event.depth,
                           self.catalogue,self.topology,self.incoming,self.plans,
                           self.tracker,self.counters)
            node=Node(context,indices,child_program,event.width,event.depth,
                      self.topology,child,self.incoming)
            frozen=bytes(directory.cells)
            try:
                result=yield Invocation(node.run_generator(current,directory,prefixes,
                                                          child_stock,*extents))
                need(bytes(directory.cells)==frozen,"toy frozen parent directory preserved")
                need(current.head==result.head==directory.head==1,"toy complete child heads")
                self.counters["internal_returns"]+=1
                return result
            finally:
                for extent in extents:extent.close()

        def boundary(kind):self.counters[kind]+=1
        try:
            self.counters["residuals"]+=1
            # Two direct coordinate-projector normal forms keep the outer
            # fixture economical. Every real internal child still executes
            # all 12 conjugated GL2 good/fallback normal forms unchanged.
            if self.root_axes:
                first=geometry.raw.times_small(columns,identifier)
                second=geometry.raw.times_small(columns,3-identifier)
                events=child_trace(geometry,first,second,indices.copy(columns),"good")
            else:events=execute(geometry)
            return (yield from packet_engine.run_generator(source,events,layout,
                         directory,prefixes,fields,coefficient,factory=self.tracker.payload,
                         observe=boundary,invoke=invoke))
        finally:
            layout.close();geometry.close();indices.free_many(columns,fields)
            directory.clear();prefixes.close();old_directory.rewind()


def compile_coefficients(catalogue,context,indices,incoming):
    """Fixed 12-member toy source table; host decoding occurs only here."""
    plans={}
    ring=context.ring
    matrices=Matrices(ring)
    for low in catalogue.low_classes():
        for identifier in (0,1):
            prepared=oracle.multiply(low,oracle.reduce_rational(I if identifier==0 else S,2),2)
            projector=oracle.multiply([[row[0]] for row in prepared],
                                     oracle.inverse(prepared,2)[:1],2)
            good=projector[0][0]!=0
            plan=compile_plan(projector,1,2,good)
            encoded=matrices.constants(projector)
            form=good_form(encoded,1,ring) if good else fallback_form(encoded,ring)
            columns,depth=indices.literal(1),indices.literal(0)
            page=Page(plan,form,ring,indices,columns,incoming.weight,depth,0,object())
            constants={}
            for command in plan.commands:
                if command.kind!="add":continue
                for reverse in (False,True):
                    value=page.coefficient(command.reference,depth,reverse)
                    constants[(command.reference,reverse)]=value.inspect()
                    context.arena.free(value)
            page.close();matrices.free(encoded);indices.free_many(columns,depth)
            plans[(identifier,low)]=(plan,constants)
    return plans


def run():
    start=monotonic()
    catalogue=Catalogue();topology=Topology(catalogue)
    arena,indices=Arena(3),Arena(8)
    modulus=arena.input(2);ring=Ring(modulus);context=Context(ring,catalogue.codes)
    incoming=UnitIncoming(context)
    plans=compile_coefficients(catalogue,context,indices,incoming)
    size,depth=indices.input(4),indices.input(0)
    program=object();tracker=Tracker();counters=Counter()
    consumer=Consumer(context,indices,program,size,depth,catalogue,topology,
                      incoming,plans,tracker,counters,root_axes=True,root_level=True)
    node=Node(context,indices,program,size,depth,topology,consumer,incoming)
    source=tracker.source(36*256,linear=False);original=bytes(source.cells)
    old=Tape();old_count=Count.literal(1);rows=Count.literal(36)
    before,gap,suffix=Count.literal(1),Count.literal(1),Count.literal(1)
    with tracker.install(), no_decode():
        output=node.run(source,old,old_count,rows,before,gap,suffix)
    try:
        need(bytes(source.cells)==original,"nested model read-only source")
        need(source.head==output.head==old.head==1,"nested model restored heads")
        for address in range(36*256):
            wanted=destination(address,4,2,(1,1,1,1))
            need(output.origins.get(wanted+1)==address,"nested model exact complete F endpoint")
        need(len(output.origins)==36*256,"nested model exact output extent")
        need(counters["internal_calls"]==counters["internal_returns"]>0,
             "nested model actual internal returns")
        need(counters["internal_calls"]==12 and counters["residuals"]==156
             and counters["root_stock_checks"]==12 and counters["child_stock_checks"]==144,
             "complete two-level GL2 source and stock coverage")
        need(counters["enter"]==counters["return"],"nested model all child brackets close")
        need(tracker.live=={source,output},"nested model all tracked work erased")
        record={"domain":"toy q=2, dimension=2, cutoff=2, one family; not selected GL64",
                "root_normal_forms":"coordinate projectors",
                "root_width":4,"root_rows":36,"complete_addresses":36*256,
                "child_fresh_rows":6,"leaf_unused_rows":1,
                "low_classes":6,"counts":dict(sorted(counters.items())),
                "output_sha256":sha256(bytes(output.cells)).hexdigest(),
                "tracked_work_erased":tracker.erased}
    finally:
        output.clear();source.clear();old.clear()
        for value in (old_count,rows,before,gap,suffix):value.close()
        indices.free_many(size,depth);context.close();ring.close();arena.free(modulus)
    need(not indices.live and not arena.live,"nested model numerical restoration")
    print("nested model completed in %.2fs"%(monotonic()-start),flush=True)
    return record


if __name__=="__main__":
    import json
    print(json.dumps(run(),sort_keys=True))
