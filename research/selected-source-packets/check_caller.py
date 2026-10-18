"""Complete small physical caller and selected address/source checks."""
from collections import Counter
from dataclasses import replace
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
import json

from binding import selected_episode
from check_sources import encoded_old
from check_support import audit, bits, no_decode, payload
from counts import Count
from directory import Context, produce
import episode as caller
from forms import fallback_form, good_form
from low_codes import LowCodes
from matrices import Matrices
from numeric import Geometry, Page, selected_page, selected_coefficient
import oracle
import packet
from plan import compile_plan
from records import BLANK, RECORD_END, Fields, Program, Tape, read_finite, read_word, seek_record
from routes import compile_route, inverse_rational
from sources import Template, compile_specification
from trace import execute
from words import Arena, Ring, need


def expected_rows(projector, weights, modulus):
    """Independent direct R(P), before normalizer or trace construction."""
    size = len(projector)
    rows = [[0]*(2*size) for _ in range(2*size)]
    for i in range(size):
        for j in range(size):
            p,inv = projector[i][j],pow(weights[j],-1,modulus)
            rows[i][j] = (int(i==j)-weights[i]*p*inv) % modulus
            rows[i][2*size-1-j] = weights[i]*p % modulus
            rows[2*size-1-i][j] = p*inv % modulus
            rows[2*size-1-i][2*size-1-j] = (int(i==j)-p) % modulus
    return rows


class SmallResidual:
    """Use the retained complete trace/leaf interpreter, with a GL2 fixture."""
    def __init__(self,context,indices,depth,parent_size,code,low,factory=Tape):
        self.context,self.indices,self.depth,self.parent_size = context,indices,depth,parent_size
        self.code,self.low = code,low
        self.factory = factory
        p = oracle.multiply([[row[0]] for row in low],oracle.inverse(low,context.q)[:1],context.q)
        self.plan = compile_plan(p,1,context.q,True)
        self.columns = indices.input(1)
        self.spectators = Arena(2)
        self.one = self.spectators.input(1)
        self.geometry = Geometry(self.plan,indices,self.columns,depth,code,object())
        self.boundaries = Counter()
        self.calls = 0
        self.transported_differs = False

    def coefficient(self,fields,request):
        context,arena = self.context,self.context.arena
        seek_record(fields,self.depth)
        need(read_finite(fields,context.codes.bits) == self.code, "produced common field reaches residual")
        high = [[read_word(fields,arena) for _ in range(2)] for _ in range(2)]
        need(fields.read() == RECORD_END, "complete produced current high field")
        fields.step(1)
        need(fields.read() == BLANK, "current raw field is last")
        fields.rewind()
        matrices = Matrices(context.ring)
        header = matrices.raw_header(self.low,high,context.q)
        projector = matrices.projector(header,1)
        form = good_form(projector,1,context.ring)
        page = Page(self.plan,form,context.ring,self.indices,self.columns,
                    lambda _coordinate: arena.literal(2),self.depth,self.code,self.geometry.parent_identity)
        value = page.evaluate(request)
        page.close()
        matrices.free(high);matrices.free(header);matrices.free(projector)
        return value

    def __call__(self,source,directory,prefixes):
        self.calls += 1
        one = self.indices.literal(1)
        fields,carry = self.geometry.raw.add(self.depth,one)
        self.indices.free(one)
        need(not carry,"small fixture field extent")
        padded = prefixes.marginal()
        try:
            result = packet.run(source,self.geometry,self.parent_size,self.context.ring,self.context.q,
                                self.one,self.one,padded,fields,directory,self.coefficient,self.factory,
                                boundary_observer=lambda kind:self.boundaries.update([kind]))
            self.transported_differs = bits(result) != bits(source)
            return result
        finally:
            padded.close();self.indices.free(fields)

    def close(self):
        self.geometry.close();self.indices.free(self.columns)
        self.spectators.free(self.one);audit(self.spectators)


def complete_episode():
    selected = selected_episode()
    # The finite Boolean model retains the55-XOR lifetime pattern and physical
    # family labels, while replacing the64-dimensional rank7 residual by GL2
    # rank1. The selected literal/source check is separate.
    chart = ((F(1),F(1)),(F(0),F(1)))
    records = list(selected.records)
    records[0] = (2,473,661,1,0,1,0)
    records[-1] = (3,473,661,1,0,0,0)
    template = Template(3,1,("generic-rank-one",),((F(1),F(0)),(F(0),F(0))),
                        ((F(1),F(0)),(F(0),F(1))),((F(1),F(0)),(F(0),F(1))))
    model = replace(selected,records=tuple(records),chart=chart,template=template,
                    sha256=sha256(json.dumps(records,separators=(",",":")).encode()).hexdigest())
    arena,indices = Arena(3),Arena(8)
    mod = arena.input(3);ring=Ring(mod);codes=LowCodes(3,2,2);context=Context(ring,codes)
    low = ((1,1),(0,1)); owner_low = ((1,0),(0,1))
    source_route = compile_route(owner_low,chart,codes)
    code = codes.encode(1,True,low)
    old_fields,parent_size = indices.input(1),indices.input(2)
    old_count,fibre = Count.literal(2),Count.literal(3**4)
    old = encoded_old(context,[((codes.encode(0,False,owner_low),(0,0,0,0)),),
                               ((codes.encode(0,True,low),(0,0,0,0)),)])
    old_original = bytes(old.cells)
    families = {family:payload(2*48*3**4,family%7) for family in (527,)+model.target_families}
    originals = {family:bits(tape) for family,tape in families.items()}
    residual = SmallResidual(context,indices,old_fields,parent_size,code,low)
    with no_decode():
        outputs = caller.physical(families,model,source_route,code,context,old,old_fields,
                                  old_count,fibre,residual)
    p = oracle.multiply([[row[0]] for row in low],oracle.inverse(low,3)[:1],3)
    matrix = expected_rows(p,(2,2),3)
    owner_ordinal,common_ordinal = codes.rank(owner_low),codes.rank(low)
    changed_cells = 0
    for family in model.target_families:
        expected = bytearray(originals[family])
        for prefix in range(2):
            for address,digits in enumerate(product(range(3),repeat=4)):
                transformed = 0
                for row in matrix:
                    transformed = 3*transformed+sum(x*y for x,y in zip(row,digits)) % 3
                dst = (prefix*48+common_ordinal)*81+address
                src = (prefix*48+owner_ordinal)*81+transformed
                expected[dst] ^= originals[527][src]
                changed_cells += 1
        need(bits(outputs[family]) == expected,"complete dirty physical COPY/XOR/ERASE endpoint")
    need(all(bits(tape) == originals[family] and tape.head == 1 for family,tape in families.items()),
         "preserved arbitrary dirty inputs")
    need(bytes(old.cells) == old_original and old.head == 1,"preserved older physical fields")
    need(residual.calls == 1 and residual.boundaries == {"enter":1,"return":1},
         "one completed residual and child across the packet")
    need(residual.transported_differs,"untransported ERASE equality is the wrong guard")
    result = {"dimension":2,"rank":1,"width":1,"old_prefixes":2,"families":56,
              "input_bits":sum(map(len,originals.values())),"target_cells_checked":changed_cells,
              "literal_XORs":55,"residual_calls":residual.calls,"child_entries":1,
              "transported_differs_from_source":residual.transported_differs,
              "outputs_sha256":sha256(b"".join(bits(outputs[f]) for f in sorted(outputs))).hexdigest()}
    for tape in list(families.values())+list(outputs.values()):tape.clear()
    old.clear();old_count.close();fibre.close();residual.close();context.close();ring.close()
    arena.free(mod);indices.free_many(old_fields,parent_size);audit(arena);audit(indices)
    return result


def selected_columns():
    episode = selected_episode()
    codes = LowCodes(3,64,2)
    low = tuple(map(tuple,oracle.eye(64)));code=codes.encode(1,True,low)
    spec = compile_specification(code,episode.template,low)
    arena,indices = Arena(5),Arena(8)
    mod=arena.input(9);ring=Ring(mod)
    program=Program.fixture(indices,arena,64,2,[],codes.bits)
    fields=Fields.fixture(indices,arena,[(code,[[0]*64 for _ in range(64)])],codes.bits)
    p=oracle.projector(episode.template,low,[[0]*64 for _ in range(64)],2)
    plan=compile_plan([[x%3 for x in row] for row in p],7,3,spec.good)
    with no_decode():page,frame=selected_page(plan,ring,indices,program,fields,{code:spec},code)
    rows=[{i:1} for i in range(128)]
    counts=Counter();serial=0;iterator=execute(page)
    while True:
        try:
            with no_decode():event=next(iterator)
        except StopIteration:break
        counts[event.kind]+=1
        if event.kind in ("enter","return"):continue
        a=event.first.inspect();b=event.second.inspect() if event.second is not None else None
        if event.kind=="atom_swap":rows[a],rows[b]=rows[b],rows[a]
        elif event.kind=="sign":rows[a]={k:-v%9 for k,v in rows[a].items()}
        else:
            with no_decode():value=page.evaluate(event.request)
            scalar=value.inspect()
            if event.request.kind=="child" and serial<3:
                with no_decode():actual=selected_coefficient(plan,ring,indices,program,fields,{code:spec},code,event.request)
                need(actual.inspect()==scalar,"large-code serialized selected child")
                arena.free(actual);serial+=1
            arena.free(value)
            for column,weight in rows[b].items():
                after=(rows[a].get(column,0)+scalar*weight)%9
                if after:rows[a][column]=after
                else:rows[a].pop(column,None)
    expected=expected_rows(p,[2]*64,9)
    observed=[[row.get(j,0) for j in range(128)] for row in rows]
    expected_children = 1 if plan.good else sum(command.kind=="child" for command in plan.commands)
    need(observed==expected and counts["enter"]==counts["return"]==expected_children,
         "complete selected COPY511 address operator")
    result={"selected_columns":128,"branch":"good" if spec.good else "fallback",
            "events":dict(counts),"serialized_children":serial,
            "large_source_code_bits":codes.bits,"operator_sha256":sha256(bytes(x for row in observed for x in row)).hexdigest()}
    page.close();indices.free(page.columns);frame.close();program.tape.clear();fields.tape.clear()
    ring.close();arena.free(mod);audit(arena);audit(indices)
    return result


def selected_consumer():
    """Probe concrete GL64 consumer wiring; do not simulate its huge payload."""
    from residual import SelectedCopy511
    template=selected_episode().template;codes=LowCodes(3,64,2)
    low=tuple(map(tuple,oracle.inverse(oracle.reduce_rational(template.preparation,3),3)))
    code=codes.encode(1,True,low);spec=compile_specification(code,template,low)
    need(spec.good,"selected consumer good-class control")
    arena,indices,spectators=Arena(3),Arena(8),Arena(2)
    mod=arena.input(3);ring=Ring(mod);context=Context(ring,codes)
    size,depth=indices.input(64),indices.input(0);one=spectators.input(1)
    program=Program.fixture(indices,arena,64,2,[],codes.bits)
    old=Tape();count=Count.literal(1)
    with no_decode():directory,prefixes=produce(old,depth,count,code,context)
    bound=SelectedCopy511(context,indices,program,{},low,size,depth,one,one)
    consumer=bound.residual
    need(bound.code==code and bound.route.target_low==low and
         bound.episode.source_family==527 and bound.episode.template==template,
         "selected physical recipe binds the concrete residual")
    selected_fields=Fields(indices,arena,codes.bits);selected_fields.tape=directory
    with no_decode():page,frame=selected_page(consumer.plan,ring,indices,program,selected_fields,{code:spec},code)
    samples={};original_run=packet.run
    def probe(source,geometry,parent_size,current_ring,q,before,suffix,prefix_count,field_count,fields,coefficient):
        need(source is sentinel and geometry.parent_identity is program,"concrete selected consumer parent")
        iterator=execute(geometry)
        try:
            for event in iterator:
                if event.kind != "add" or event.request.kind in samples:continue
                actual=coefficient(fields,event.request);expected=page.evaluate(event.request)
                need(ring.raw.compare(actual,expected)==0,"concrete selected per-prefix coefficient")
                arena.free_many(actual,expected);samples[event.request.kind]=True
                if len(samples)==2:break
        finally:iterator.close()
        return "selected-consumer-source-probe"
    sentinel=Tape();packet.run=probe
    try:
        with no_decode():result=consumer(sentinel,directory,prefixes)
    finally:packet.run=original_run
    need(result=="selected-consumer-source-probe" and set(samples)=={"adapter","child"},
         "both selected callback junctions")
    original_physical=caller.physical
    def physical_probe(families,episode,route,current_code,current_context,old_directory,
                       old_fields,old_count,fibre,residual):
        need(families=={} and episode is bound.episode and route is bound.route and
             current_code==code and current_context is context and old_directory is old and
             old_fields is depth and old_count is count and fibre is one and residual is consumer,
             "closed selected physical-to-residual binding")
        return "selected-physical-binding-probe"
    caller.physical=physical_probe
    try:
        with no_decode():need(bound({},old,depth,count,one)=="selected-physical-binding-probe",
                              "selected physical wrapper")
    finally:caller.physical=original_physical
    page.close();indices.free(page.columns);frame.close();program.tape.clear();directory.clear();old.clear()
    prefixes.close();count.close();context.close();ring.close();arena.free(mod)
    indices.free_many(size,depth);spectators.free(one);audit(arena);audit(indices);audit(spectators)
    return {"current_fields":1,"selected_callback_kinds":sorted(samples),"full_payload_executed":False}
