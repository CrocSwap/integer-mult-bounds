"""Selected source/chronology certificates and concrete consumer junctions."""
from collections import Counter
from hashlib import sha256

from cardinal_counts import Count
from catalogue import Catalogue, Specifications, canonical
from check_support import audit, no_decode
from consumer import Consumer
from control import LocalState
from directory import Context
from numeric import selected_page
import oracle
import packet_engine
from records import Fields, Program, Tape
from topology import SelectedTopology
from words import Arena, Ring, need


def catalogue_checks(catalogue):
    old=catalogue.old;word=catalogue.word;template=catalogue.template
    programs,digest=old.literal_programs(word,catalogue.dimensions)
    need(programs==template["local_programs"] and digest==template["source_record_sha256"],
         "independent selected literal reconstruction")
    need(all(old.dyadic(p) for p in catalogue.projectors),"fixed odd-prime projector domain")
    local={orientation:old.local_replay(events,word,catalogue.projectors,catalogue.dimensions,orientation=="reverse")
           for orientation,events in programs.items()}
    owners,_remainder=old.ownership(template,word,catalogue.geometry)
    topology=SelectedTopology(catalogue);counts=Counter();binding=sha256()
    for stage in range(9):
        for replica in range(32):
            call=topology.call(stage,replica);state=LocalState(call)
            for position,event in enumerate(call.events):
                opcode,role=state.accept(position);counts[opcode]+=1
                if opcode in (0,2):
                    identifier=call.requests[position];request=catalogue.requests[identifier]
                    need(request.role==role and request.stage==stage and request.position==position and
                         request.kind==("MOVE" if opcode==0 else "COPY"),"concrete literal-to-provider request")
                    if replica==0:binding.update((canonical([stage,position,identifier])+"\n").encode())
            state.finish()
    need(counts=={0:838368,1:6999840,2:2592,3:2592},"complete selected literal controller census")
    bases=Counter()
    for base in catalogue.bases.values():
        basis=base.basis(3)
        need(len(basis)==64,"complete fixed rational split basis")
        bases[base.rank]+=1
    return {"provider":catalogue.receipt(),"literal_counts":dict(counts),"literal_events":sum(counts.values()),
            "literal_source_sha256":digest,"consumer_binding_sha256":binding.hexdigest(),
            "local_certificates":{key:{"records":value["records"],"symbolic_columns":value["symbolic_columns"],
                                       "copies":len(value["copies"]),"profile":value["profile"]} for key,value in local.items()},
            "ownership":owners,"split_basis_ranks":dict(sorted(bases.items()))}


def consumer_probes(catalogue):
    specifications=Specifications(catalogue)
    arena,indices=Arena(3),Arena(8)
    mod=arena.input(3);ring=Ring(mod);context=Context(ring,catalogue.codes)
    size,depth=indices.input(65),indices.input(0)
    program=Program.fixture(indices,arena,65,2,[],catalogue.codes.bits)
    consumer=Consumer(context,indices,program,specifications,size,depth)
    old=Tape();count=Count.literal(1)
    before,gap,suffix=Count.literal(2),Count.literal(5),Count.literal(3)
    result=[];original_run=packet_engine.run
    try:
        for identifier,common in ((0,True),(27825,False)):
            template=catalogue.template_for(identifier,common)
            low=tuple(map(tuple,oracle.inverse(oracle.reduce_rational(template.preparation,3),3)))
            spec=specifications.bind(identifier,common,low)
            need(spec.good,"selected consumer probe good control")
            sampled=set();sentinel=Tape()
            def probe(source,events,layout,directory,prefixes,field_count,coefficient,**_options):
                need(source is sentinel and layout.parent_size is size and layout.gap is gap,
                     "complete selected consumer geometry")
                values=Fields(indices,arena,catalogue.codes.bits);values.tape=directory
                page,frame=selected_page(specifications.plan(spec.code),ring,indices,program,values,specifications,spec.code)
                try:
                    for event in events:
                        if event.kind!="add" or event.request.kind in sampled:continue
                        actual=coefficient(directory,event.request);expected=page.evaluate(event.request)
                        need(ring.raw.compare(actual,expected)==0,"concrete selected callback and source view")
                        arena.free_many(actual,expected);sampled.add(event.request.kind)
                        if len(sampled)==2:break
                finally:
                    events.close();page.close();indices.free(page.columns);frame.close()
                return "source-only-consumer-probe"
            packet_engine.run=probe
            with no_decode():
                observed=consumer.apply(sentinel,identifier,common,low,old,count,before,gap,suffix)
            need(observed=="source-only-consumer-probe" and sampled=={"adapter","child"},"both consumer junctions")
            result.append({"request":identifier,"kind":catalogue.requests[identifier].kind,
                           "common":common,"rank":spec.template.rank,"code_bits":catalogue.codes.bits,
                           "callbacks":sorted(sampled),"full_payload_executed":False})
            sentinel.clear()
    finally:packet_engine.run=original_run
    old.clear();program.tape.clear()
    for value in (count,before,gap,suffix):value.close()
    context.close();ring.close();arena.free(mod);indices.free_many(size,depth);audit(arena);audit(indices)
    return result


def global_scalar(catalogue):
    schedule=catalogue.template["schedule"]
    def run(skip=-1):
        values=[1<<i for i in range(8)];number=0
        for event in schedule:
            kind=event["kind"]
            if kind=="local_cover_sweep":
                pair=event["pair"]
                target,source=(2*pair,2*pair+1) if event["reverse"] else (2*pair+1,2*pair)
                values[target]^=values[source]
            elif kind=="bridge":
                d,s=event["dst"],event["src"]
                for target,source in ((2*d,2*s),(2*s+1,2*d+1)):
                    if number!=skip:values[target]^=values[source]
                    number+=1
            elif kind=="exchange":
                for pair in range(4):values[2*pair],values[2*pair+1]=values[2*pair+1],values[2*pair]
            else:need(kind=="idle","source scalar opcode")
        return values,number
    identity=[1<<i for i in range(8)]
    values,number=run();need(values==identity and number==18,"selected global scalar identity")
    for omitted in range(number):need(run(omitted)[0]!=identity,"single omitted bridge shear changes endpoint")
    return {"global_events":len(schedule),"bridge_shears":18,"omission_controls":18,
            "family_XOR_actions":18*32*111,"terminal_family_pairs":4*32*111}
