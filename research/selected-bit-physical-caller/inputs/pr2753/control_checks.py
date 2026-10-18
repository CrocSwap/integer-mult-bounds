"""Concrete lost-update witnesses and malformed boundary controls."""
import ast
from dataclasses import replace
from pathlib import Path

from cardinal_counts import Count
from catalogue import Catalogue, Specifications
from check_runtime import Tracker, destination
from check_support import audit, bits, inspect_count, no_decode, reject
from control import LocalState
from directory import Context
import driver
import fresh_rows
import model
import node
from records import Program, Tape
from scheduler import complete
from words import Arena, Ring, need


def stale_controls():
    catalogue=model.Catalogue();topology=model.Topology(catalogue)
    arena,indices=Arena(3),Arena(8)
    mod=arena.input(3);ring=Ring(mod);context=Context(ring,catalogue.codes)
    size,depth=indices.input(2),indices.input(0);program=object()
    incoming=model.Incoming(context,indices,(2,1))
    consumer=model.Consumer(context,indices,program,size,depth,catalogue,incoming)
    count,before,gap,suffix,fibre=(Count.literal(x) for x in (1,1,2,1,162))
    old=Tape();tracker=Tracker();source=tracker.source(4*48*162)
    original=bytes(source.cells);call=topology.call(0,0)
    identity=((1,0),(0,1));swap=((0,1),(1,0));ordinal=catalogue.codes.rank(identity)
    witnesses={}
    with tracker.install(),no_decode():
        families=fresh_rows.split(source,context,4,count,fibre)
        active=driver.Driver(context,topology,consumer,old,count,before,gap,suffix,fibre)
        complete(active.local(families,call,swap));complete(active.local(families,call,identity))
        for low in (identity,swap):
            number=catalogue.codes.rank(low)
            for address in range(162):
                target=destination(address,2,3,(2,1),2)
                old_index=number*162+address
                need(families[0].origins.get(number*162+target+1)==1<<old_index,
                     "current state composes both alias invocations")
        for tape in families.values():tape.clear()

        families=fresh_rows.split(source,context,4,count,fibre)
        parked=fresh_rows.split(source,context,4,count,fibre)
        active=driver.Driver(context,topology,consumer,old,count,before,gap,suffix,fibre)
        complete(active.local(families,call,swap))
        by_identity={id(tape):family for family,tape in families.items()}
        original_gather=driver.gather
        def stale_gather(tape,*args,**kwargs):
            return original_gather(parked[by_identity[id(tape)]],*args,**kwargs)
        driver.gather=stale_gather
        try:complete(active.local(families,call,identity))
        finally:driver.gather=original_gather
        old_index=ordinal*162+18;correct_index=ordinal*162+3
        need(families[0].origins.get(correct_index+1)!=1<<old_index and
             families[0].origins.get(old_index+1)==1<<old_index,"stale second-low snapshot loses the first map")
        witnesses["stale_low_gather"]={"source":old_index,"correct":correct_index,"wrong":old_index}
        for tape in list(families.values())+list(parked.values()):tape.clear()

        families=fresh_rows.split(source,context,4,count,fibre)
        parked=fresh_rows.split(source,context,4,count,fibre)
        class StaleScatter(driver.Driver):
            def commit(self,current,family,low,packet):
                previous=current[family]
                current[family]=driver.scatter(parked[family],packet,self.context,self.old_count,low,self.fibre)
                previous.clear()
        active=StaleScatter(context,topology,consumer,old,count,before,gap,suffix,fibre)
        complete(active.local(families,call,identity))
        old_index=ordinal*162+54;correct_index=ordinal*162+2
        need(families[0].origins.get(correct_index+1)!=1<<old_index and
             families[0].origins.get(old_index+1)==1<<old_index,"stale family scatter drops an earlier returned role")
        witnesses["stale_family_scatter"]={"source":old_index,"correct":correct_index,"wrong":old_index}
        for tape in list(families.values())+list(parked.values()):tape.clear()
    need(tracker.live=={source} and bytes(source.cells)==original,"closed lost-update controls")
    source.clear();old.clear();incoming.close()
    for value in (count,before,gap,suffix,fibre):value.close()
    context.close();ring.close();arena.free(mod);indices.free_many(size,depth);audit(arena);audit(indices)
    return witnesses


def bridge_and_exchange():
    catalogue=model.Catalogue();topology=model.Topology(catalogue)
    arena=Arena(3);mod=arena.input(3);ring=Ring(mod);context=Context(ring,catalogue.codes)
    count,one,fibre=Count.literal(1),Count.literal(1),Count.literal(81)
    old=Tape();tracker=Tracker();family_size=48*81;source=tracker.source(4*family_size)
    with tracker.install(),no_decode():
        families=fresh_rows.split(source,context,4,count,fibre)
        topology.schedule=({"kind":"bridge","dst":0,"src":1,"coefficient":1},)
        drive=driver.Driver(context,topology,None,old,count,one,one,one,fibre)
        complete(drive.global_word(families))
        for family in range(4):
            for row in range(family_size):
                expected=1<<(family*family_size+row)
                if family==0:expected^=1<<(2*family_size+row)
                if family==3:expected^=1<<(family_size+row)
                need(families[family].origins.get(row+1)==expected,"native bridge has reversed Y direction")
        for tape in families.values():tape.clear()
        families=fresh_rows.split(source,context,4,count,fibre)
        topology.schedule=({"kind":"exchange"},)
        complete(drive.global_word(families))
        for family in range(4):
            for row in range(family_size):
                need(families[family].origins.get(row+1)==1<<((family^1)*family_size+row),
                     "terminal exchange keeps the within-family body address")
        for tape in families.values():tape.clear()
    need(tracker.live=={source},"closed native global controls")
    source.clear();old.clear();count.close();one.close();fibre.close();context.close();ring.close();arena.free(mod);audit(arena)
    return {"bridge_columns":4*family_size,"exchange_columns":4*family_size}


def rejections_and_counts(catalogue=None):
    model_catalogue=model.Catalogue();topology=model.Topology(model_catalogue);call=topology.call(0,0)
    rejected=[]
    def check(candidate):
        state=LocalState(candidate)
        for position in range(len(candidate.events)):state.accept(position)
        state.finish()
    events=list(call.events);events[2]=(1,2,2,1,0,0)
    rejected.append(reject(lambda:check(replace(call,events=tuple(events))),"self_XOR"))
    events=list(call.events);events[2]=(1,3,2,1,0,0)
    rejected.append(reject(lambda:check(replace(call,events=tuple(events))),"write_private"))
    forbidden=replace(call,start=(1,1,0),end=(1,1,0),events=((2,0,3,1,0,1,0),(1,0,1,1,1,0)),requests=(1,None))
    rejected.append(reject(lambda:check(forbidden),"write_copied_source"))
    events=list(call.events);events[4]=(3,1,3,1,0,0,0)
    rejected.append(reject(lambda:check(replace(call,events=tuple(events))),"wrong_ERASE_source"))
    events=list(call.events);events[2]=(1,2,3,1,1,0)
    rejected.append(reject(lambda:check(replace(call,events=tuple(events))),"wrong_ADD_frame"))
    arena,indices=Arena(3),Arena(8);mod=arena.input(3);ring=Ring(mod);context=Context(ring,model_catalogue.codes)
    for width in (0,1):
        size,depth=indices.input(width),indices.input(0)
        rejected.append(reject(lambda:node.Node(context,indices,object(),size,depth,topology,None,None),"node_range_"+str(width)))
        indices.free_many(size,depth)
    for rows in (1,4*48-1,4*48+1,4*47):
        value=Count.literal(rows)
        rejected.append(reject(lambda:fresh_rows.quotient(value,context,4),"incomplete_stock_"+str(rows)));value.close()
    products=0
    for a in (0,1,3,127,(1<<521)-1):
        for b in (0,1,17,(1<<300)+7):
            left,right=Count.literal(a),Count.literal(b)
            with no_decode():out=Count.product(left,right);left.add(right)
            need(inspect_count(out)==a*b and inspect_count(left)==a+b,"unbounded spectator arithmetic")
            left.close();right.close();out.close();products+=1
    context.close();ring.close();arena.free(mod);audit(arena);audit(indices)
    high_arena=Arena(5);high_mod=high_arena.input(9);high_ring=Ring(high_mod)
    high_context=Context(high_ring,model_catalogue.codes);bad_high=Count.literal(4*48*80)
    rejected.append(reject(lambda:fresh_rows.quotient(bad_high,high_context,4),"incomplete_high_stock"))
    bad_high.close();high_context.close();high_ring.close();high_arena.free(high_mod);audit(high_arena)

    catalogue=Catalogue(3) if catalogue is None else catalogue
    selected_arena,selected_indices=Arena(3),Arena(8)
    selected_mod=selected_arena.input(3);selected_ring=Ring(selected_mod)
    selected_context=Context(selected_ring,catalogue.codes)
    exact=Count.literal(269241600*catalogue.codes.size)
    with no_decode():unused=fresh_rows.quotient(exact,selected_context,28416)
    need(inspect_count(unused)==9475,"actual selected unused compatibility factor")
    unused.close();exact.close()
    physical=Count.literal(28425*catalogue.codes.size)
    rejected.append(reject(lambda:fresh_rows.quotient(physical,selected_context,28416),"physical_inventory_denominator"))
    physical.close()
    selected_size,selected_depth=selected_indices.input(64),selected_indices.input(0)
    program=Program.fixture(selected_indices,selected_arena,64,1,[],catalogue.codes.bits)
    evaluator=node.SelectedNode(selected_context,selected_indices,program,selected_size,selected_depth,
                                catalogue,Specifications(catalogue))
    insufficient=Count.literal(28416*catalogue.codes.size);one=Count.literal(1);empty=Tape()
    with no_decode():
        rejected.append(reject(lambda:evaluator.run(empty,empty,one,insufficient,one,one,one),"selected_compatibility_stock"))
    insufficient.close();one.close();empty.clear();program.tape.clear()
    selected_context.close();selected_ring.close();selected_arena.free(selected_mod)
    selected_indices.free_many(selected_size,selected_depth);audit(selected_arena);audit(selected_indices)
    here=Path(__file__).resolve().parent
    runtime=("cardinal_counts.py","layout.py","packet_engine.py","consumer.py","peel.py","fresh_rows.py",
             "control.py","driver.py","node.py","topology.py","linear_sign.py","recursive_call.py","scheduler.py")
    for name in runtime:
        path=here/name if (here/name).exists() else here/"predecessor"/name
        for item in ast.walk(ast.parse(path.read_text())):
            if isinstance(item,ast.Attribute):need(item.attr not in ("inspect","cells","from_bytes"),"no runtime word decoding")
            if isinstance(item,ast.Call) and isinstance(item.func,ast.Name):
                need(item.func.id not in ("float","eval","exec"),"no runtime numerical escape")
    return {"rejections":rejected,"cardinality_cases":products,"maximum_product_bits":822,
            "selected_unused_factor":9475,"runtime_modules":list(runtime)}
