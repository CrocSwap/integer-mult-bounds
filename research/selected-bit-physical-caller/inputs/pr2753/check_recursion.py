"""Independent layout, lifecycle and real-frame junction checks.

The frame test patches only SelectedNode.run_generator with a tiny controlled
consumer. It exercises the real descriptor/Frame/old-directory handoff and
return, not the unmaterialized complete selected GL64 payload or its endpoint.
"""
from collections import Counter
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import sys
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bootstrap
from cardinal_counts import Count
from catalogue import Catalogue, Specifications
from check_support import audit, bits, inspect_count, no_decode
from directory import Context, append_tape
from layout import Layout
import node
from numeric import Geometry
import oracle
import model
from packet import read_prefix
import packet_engine
import peel
from records import Fields, Program, Tape
import recursive_call
from recursive_call import child_call
from scheduler import Invocation, complete
from trace import Event, child, pair_command
from words import Arena, BLANK, RIGHT, Ring


def expected_extents(n, dimension, modulus, first, second, width, before, gap, suffix):
    core = dimension * (n // dimension)
    def physical(i):
        return i if i < core else i + 2 * (n - core)
    a, b = physical(first), physical(second)
    assert physical(first + width - 1) == a + width - 1
    assert physical(second + width - 1) == b + width - 1
    assert a + width <= n or a >= n
    assert b + width <= n or b >= n
    result = [before * modulus ** a, modulus ** (b - a - width),
              suffix * modulus ** (2 * n - b - width)]
    result[0 if a >= n else 2 if b + width <= n else 1] *= gap
    return tuple(result)


def layout_case(n, dimension, modulus, chunk, invalid=False):
    indices = Arena(max(9, (4 * n).bit_length() + 1))
    residues = Arena(modulus.bit_length() + 1)
    m = residues.input(modulus); ring = Ring(m)
    size, columns, zero = (indices.input(v) for v in (n, n // dimension, 0))
    geometry = Geometry(SimpleNamespace(dimension=dimension), indices, columns, zero, 0, zero)
    before, gap, suffix = (Count.literal(v) for v in (2, 5, 3))
    layout = Layout(geometry, size, ring, 3, before, gap, suffix)
    first, second, width = (indices.input(v) for v in chunk)
    output = None
    try:
        try:
            with no_decode():
                output = layout.child_extents(first, second, width, before=before)
        except ValueError:
            if invalid:
                return None
            raise
        assert not invalid, 'invalid projected child accepted'
        result = tuple(inspect_count(v) for v in output)
        assert result == expected_extents(n, dimension, modulus, *chunk, 2, 5, 3)
        assert result[0] * modulus ** (2 * chunk[2]) * result[1] * result[2] == 30 * modulus ** (2 * n)
        return result
    finally:
        if output is not None:
            for value in output: value.close()
        layout.close(); geometry.close()
        indices.free_many(size, columns, zero, first, second, width)
        ring.close(); residues.free(m)
        for value in (before, gap, suffix): value.close()
        audit(indices); audit(residues)


def layouts():
    digest = sha256(); count = invalid = 0
    for dimension, sizes in ((2, (4, 5, 6, 7)), (64, (64, 65, 128, 129, 191, 192, 193, 257))):
        for n in sizes:
            f = n // dimension; rank = min(42, dimension - 1)
            chunks = [(0, (2 * dimension - rank) * f, rank * f)]
            chunks += [(i * f, k * f, f) for i, k in ((0, 1), (0, dimension), (dimension, 2 * dimension - 1))]
            if f // 2:
                chunks += [(k * f, (k + 1) * f - f // 2, f // 2) for k in (1, dimension + 1)]
            for modulus in (3, 9):
                for chunk in chunks:
                    result = layout_case(n, dimension, modulus, chunk)
                    digest.update(json.dumps([n, dimension, modulus, chunk, result]).encode()); count += 1
            core = dimension * f
            for chunk in ((0, 1, 2), (core - 1, core + 2, 2)):
                layout_case(n, dimension, 3, chunk, invalid=True); invalid += 1
    return {'cases':count, 'rejected_overlapping_or_noncontiguous_chunks':invalid,
            'moduli':[3,9], 'spectators':[2,5,3], 'digest':digest.hexdigest()}


def traces():
    result = []
    for n in (128, 4096, 8192):
        indices = Arena((4 * n).bit_length() + 1)
        columns, depth = indices.input(n // 64), indices.input(3)
        program = object()
        page = Geometry(SimpleNamespace(dimension=64), indices, columns, depth, 17, program)
        for label, target, source in (('pair_head',0,1), ('pair_tail',64,65), ('unit_cross',0,64)):
            kind = 'unit' if label == 'unit_cross' else 'pair'
            command = SimpleNamespace(target=target, source=source, reference=SimpleNamespace(kind=kind))
            generator = pair_command(page, command)
            counts = Counter(); boundaries = []
            with no_decode():
                for event in generator:
                    counts[event.kind] += 1
                    if event.kind == 'enter':
                        boundaries.append([event.child_kind, inspect_count(event.width), event.half,
                                           event.field, event.reverse])
            f = n // 64
            expected = 1 if target < 64 <= source else 3
            assert counts['enter'] == counts['return'] == expected
            assert counts['invoke'] == (int(f >= 64) + (2 * int(f // 2 >= 64) if expected == 3 else 0))
            result.append({'parent_width':n, 'kind':label, 'events':dict(counts), 'boundaries':boundaries})
        generator = child(page, indices.zero(), indices.input(86 * (n // 64)),
                          indices.input(42 * (n // 64)), 'good')
        with no_decode():
            kinds = [event.kind for event in generator]
        assert kinds == ['enter', 'invoke', 'return']
        result.append({'parent_width':n, 'kind':'good', 'events':kinds, 'width':42*(n//64)})
        page.close(); indices.free_many(columns, depth); audit(indices)
    return result


def trampoline():
    entered = []; returned = []; closed = []
    def descend(depth, fail=False):
        entered.append(depth)
        try:
            if depth:
                value = yield Invocation(descend(depth - 1, fail))
            else:
                if fail: raise ValueError('deliberate deepest controlled failure')
                value = 0
            returned.append(depth)
            return value + 1
        finally:
            closed.append(depth)
    assert complete(descend(1500)) == 1501
    assert entered == list(range(1500, -1, -1))
    assert returned == closed == list(range(1501))
    entered.clear(); returned.clear(); closed.clear()
    try:
        complete(descend(1100, True))
    except ValueError as error:
        assert str(error) == 'deliberate deepest controlled failure'
    else:
        raise AssertionError('deep child failure was swallowed')
    assert closed == list(range(1101)) and not returned
    def illegal():
        yield 'non-invocation suspension'
    try: complete(illegal())
    except ValueError: pass
    else: raise AssertionError('untyped suspension accepted')
    return {'completed_frames':1501, 'closed_after_failure':1101, 'host_recursion_limit_unchanged':True}


def lifecycle():
    indices = Arena(10); columns, depth = indices.input(2), indices.zero()
    program = object(); page = Geometry(SimpleNamespace(dimension=64), indices, columns, depth, 3, program)
    layout = SimpleNamespace(geometry=page, fibre=lambda:Count.literal(1))
    one = Count.literal(1); fields = indices.zero(); directory = Tape()
    source = Tape(); source.append(1); source.rewind()
    words = [indices.input(v) for v in (0,172,84,1)]
    base = Event('enter', words[0], words[1], width=words[2], depth=words[3],
                 child_kind='good', source_code=3, parent_identity=program)
    invoke_count = []
    def consumer(current, event):
        invoke_count.append(event.child_kind)
        if mode == 'aliased_output':
            if False: yield
            return current
        output = Tape(); append_tape(current, output); output.rewind()
        if False: yield
        return output
    def events(mode):
        yield base
        if mode != 'missing_invoke': yield replace(base, kind='invoke')
        if mode == 'duplicate_invoke': yield replace(base, kind='invoke')
        if mode == 'width_mutation':
            page.raw.increment_in_place(base.width)
        if mode == 'aliased_metadata_mutation':
            base.field = 1
        if mode != 'missing_return':
            yield replace(base, kind='return', field=1 if mode == 'metadata_mutation' else base.field)
    rejected = []
    for mode in ('normal','missing_invoke','duplicate_invoke','missing_return','metadata_mutation',
                 'aliased_output','aliased_metadata_mutation','width_mutation'):
        base.field = 0
        original = bytes(source.cells); output = None
        try:
            with no_decode():
                output = packet_engine.run(source,events(mode),layout,directory,one,fields,None,invoke=consumer)
            assert mode == 'normal', 'malformed recursive lifetime accepted: ' + mode
            assert bits(output) == bytes([1]) and output is not source
        except ValueError:
            assert mode != 'normal'
            rejected.append(mode)
        finally:
            if output is not None and output is not source: output.clear()
        assert bytes(source.cells) == original and source.head == directory.head == 1
    source.clear(); directory.clear(); one.close(); page.close()
    indices.free_many(columns, depth, fields, *words); audit(indices)
    return {'normal_owned_return':True, 'rejected':rejected}


def abort_cleanup():
    """A child exception must erase the parent's already-created output."""
    indices = Arena(10); columns, level = indices.input(1), indices.zero()
    identity = object()
    geometry = Geometry(SimpleNamespace(dimension=64),indices,columns,level,0,identity)
    layout = SimpleNamespace(geometry=geometry,fibre=lambda:Count.literal(1))
    source = Tape(); source.append(1); source.rewind()
    directory = Tape(); prefixes = Count.literal(1); fields = Count.literal(0)
    operands = [indices.input(v) for v in (0,64,64,1)]
    boundary = Event('enter',operands[0],operands[1],width=operands[2],depth=operands[3],
                     parent_identity=identity,child_kind='good')
    created = []
    class Captured(Tape):
        def __init__(self):
            super().__init__(); created.append(self)
    def events():
        yield Event('sign',operands[0])
        yield boundary
        yield replace(boundary,kind='invoke')
        yield replace(boundary,kind='return')
    def fail(current,event):
        if False: yield
        raise ValueError('controlled failed child')
    original_action = packet_engine.action
    packet_engine.action = lambda local,event,layout,coefficient,factory:local
    try:
        try:
            complete(packet_engine.run_generator(source,events(),layout,directory,prefixes,fields,
                                                 None,factory=Captured,invoke=fail))
        except ValueError as error: assert str(error) == 'controlled failed child'
        else: raise AssertionError('child exception swallowed')
        assert created and all(not bits(tape) and tape.head==1 for tape in created)
        assert bits(source)==bytes([1]) and source.head==directory.head==1
    finally:
        packet_engine.action=original_action
        source.clear();directory.clear();prefixes.close();fields.close();geometry.close()
        indices.free_many(columns,level,*operands)
    audit(indices)
    return {'child_failure_propagated':True,'owned_parent_tapes_erased':len(created),
            'scope':'controlled primitive creates owned output before failing child; real packet engine and scheduler'}


def construction_failure():
    """Failed construction cannot leave a frame that the caller cannot own."""
    indices,arena=Arena(10),Arena(3)
    modulus=arena.input(3);ring=Ring(modulus)
    context=Context(ring,SimpleNamespace(q=3,dimension=64,bits=2))
    program=Program.fixture(indices,arena,256,2,[],2)
    width,depth=indices.input(168),indices.input(1)
    parent=SimpleNamespace(context=context,indices=indices,specifications=SimpleNamespace(catalogue=object()))
    event=SimpleNamespace(width=width,depth=depth)
    banks=[];programs=[]
    original_arena,original_program,original_node=recursive_call.Arena,recursive_call.Program,node.SelectedNode
    def bank(*args,**kwargs):
        result=original_arena(*args,**kwargs);banks.append(result);return result
    def copied_program(*args,**kwargs):
        result=original_program(*args,**kwargs);programs.append(result);return result
    def reject_constructor(child_context,child_indices,*args):
        child_context.arena.zero();child_indices.zero()
        raise ValueError('injected child construction failure')
    recursive_call.Arena,recursive_call.Program,node.SelectedNode=bank,copied_program,reject_constructor
    saved=bytes(program.tape.cells)
    try:
        try:
            with no_decode(): recursive_call.Frame(parent,program,event)
        except ValueError as error: assert str(error)=='injected child construction failure'
        else: raise AssertionError('constructor injection was not reached')
        assert len(banks)==2 and len(programs)==1
        for value in banks:audit(value)
        assert not bits(programs[0].tape)
        assert bytes(program.tape.cells)==saved and program.tape.head==1
    finally:
        recursive_call.Arena,recursive_call.Program,node.SelectedNode=original_arena,original_program,original_node
        program.tape.clear();indices.free_many(width,depth);context.close();ring.close();arena.free(modulus)
    audit(indices);audit(arena)
    return {'failed_fresh_banks_erased':2,'copied_program_erased':True,'parent_program_unchanged':True}


def all_size_peel():
    """Lower actual peel.run to independent scalar rows, without dense bits."""
    indices,arena=Arena(10),Arena(5)
    modulus=arena.input(9);ring=Ring(modulus)
    context=SimpleNamespace(dimension=64,q=3,ring=ring,arena=arena)
    size,depth=indices.input(129),indices.zero()
    values=[1]*129;values[64]=2;values[128]=5
    incoming=model.Incoming(context,indices,values)
    source,old=Tape(),Tape()
    old_count,stock,before,gap,suffix=(Count.literal(v) for v in (1,7,2,5,3))
    original_run=packet_engine.run
    def collect(force_legacy_columns):
        rows=[{i:1} for i in range(258)]
        coordinates=[];counts=Counter();positions=set()
        def scalar(source_arg,events,layout,directory,prefixes,fields,coefficient,**kwargs):
            assert source_arg is source and directory is old
            assert inspect_count(layout.geometry.columns)==2 and not layout.embedded
            assert [inspect_count(x) for x in (layout.before,layout.gap,layout.suffix)]==[14,5,3]
            if force_legacy_columns:
                replacement=indices.literal(1);column_word=layout.geometry.columns
                while replacement.read()!=RIGHT:
                    column_word.write(replacement.read());column_word.step(1);replacement.step(1)
                column_word.rewind();replacement.rewind();indices.free(replacement)
            try:
                for event in events:
                    first=inspect_count(event.first);positions.add(first);counts[event.kind]+=1
                    if event.kind=='sign':
                        rows[first]={j:(-value)%9 for j,value in rows[first].items()}
                    else:
                        second=inspect_count(event.second);positions.add(second)
                        if event.kind=='atom_swap': rows[first],rows[second]=rows[second],rows[first]
                        else:
                            assert event.kind=='add'
                            coordinates.append(inspect_count(event.request.coordinate))
                            value=coefficient(old,event.request);scalar_value=inspect_count(value);arena.free(value)
                            for j,entry in rows[second].items():rows[first][j]=(rows[first].get(j,0)+scalar_value*entry)%9
                            rows[first]={j:value for j,value in rows[first].items() if value}
            finally:events.close()
            return source
        packet_engine.run=scalar
        with no_decode():
            assert peel.run(source,context,indices,size,depth,object(),old,old_count,
                            stock,before,gap,suffix,incoming) is source
        return rows,coordinates,counts,positions
    try:
        actual,coordinates,counts,positions=collect(False)
        expected=[{i:1} for i in range(258)];expected[128]={129:5};expected[129]={128:2}
        assert actual==expected and coordinates==[128]*3 and positions=={128,129}
        assert counts=={'atom_swap':4,'add':3,'sign':1}
        legacy,legacy_coordinates,legacy_counts,_=collect(True)
        assert legacy!=expected and legacy_coordinates[0]==64 and legacy_counts['sign']==65
    finally:
        packet_engine.run=original_run
        incoming.close();source.clear();old.clear()
        for value in (old_count,stock,before,gap,suffix):value.close()
        indices.free_many(size,depth);ring.close();arena.free(modulus)
    audit(indices);audit(arena)
    return {'parent_width':129,'dimension':64,'columns':2,'remainder':1,'modulus':9,
            'incoming_weights':{'0':1,'64':2,'128':5},'queried_offsets':coordinates,
            'changed_scalar_rows':{'128':{'129':5},'129':{'128':2}},
            'primitive_counts':dict(counts),'legacy_columns_one_rejected':True,
            'scope':'actual peel.run and incoming callback; independent scalar opcode interpreter; no dense payload'}


def frame_handoff(catalogue=None, mutation=None):
    catalogue = Catalogue(3) if catalogue is None else catalogue
    specifications = Specifications(catalogue)
    identifier = next(i for i,r in enumerate(catalogue.requests) if r.base.rank == 42)
    template = catalogue.template_for(identifier, True)
    low = tuple(map(tuple, oracle.inverse(oracle.reduce_rational(template.preparation, 3), 3)))
    spec = specifications.bind(identifier, True, low)
    assert spec.good and spec.template.rank == 42
    indices, arena = Arena(10), Arena(3)
    modulus = arena.input(3); ring = Ring(modulus); context = Context(ring, catalogue.codes)
    size, depth = indices.input(256), indices.zero()
    program = Program.fixture(indices, arena, 256, 2, [], catalogue.codes.bits)
    root_node=node.SelectedNode(context,indices,program,size,depth,catalogue,specifications)
    parent=root_node.consumer
    # Exercise repeated actual construction: these source caches must not
    # acquire one new self key for every completed recursive frame.
    common_topology=root_node.topology
    common_call=common_topology.call(0,0)
    cache_sizes=(type(common_topology).call.cache_info().currsize,
                 type(common_topology).recipe.cache_info().currsize)
    extra_nodes=[node.SelectedNode(context,indices,program,size,depth,catalogue,specifications)
                 for _ in range(2)]
    for repeated in extra_nodes:
        assert repeated.topology is common_topology
        assert repeated.topology.call(0,0) is common_call
    zero_high = [[0] * 64 for _ in range(64)]
    field = Fields.fixture(indices, arena, [(spec.code, zero_high)], catalogue.codes.bits)
    directory = Tape(); append_tape(field.tape,directory); append_tape(field.tape,directory); directory.rewind()
    field.tape.clear()
    prefixes, stock, before, gap, suffix = (Count.literal(v) for v in (2,11,2,5,3))
    fields = indices.input(1)
    source = Tape()
    original_payload = bytes((i * 7 ^ i // 3) & 1 for i in range(23))
    for bit in original_payload: source.append(bit)
    source.rewind()
    original_program, original_directory = bytes(program.tape.cells), bytes(directory.cells)
    frames = []; handoffs = []; returned = []; outputs = []; injected = []
    protected_indices, protected_residues = set(indices.live), set(arena.live)
    original_run = node.SelectedNode.run_generator

    def controlled_run(self, current, old, count, unused, b, g, s, observe=None):
        # Test instrumentation reads encoded values; production code stays
        # under no_decode and never sees these Python integers.
        level, width = inspect_count(self.depth), inspect_count(self.parent_size)
        frames.append(self)
        assert self.topology is common_topology
        assert self.topology.call(0,0) is common_call
        assert self.indices is not indices and self.context.arena is not arena
        assert unused is stock and inspect_count(unused) == 11 and inspect_count(count) == 2
        assert level in (1,2) and width == {1:168,2:84}[level]
        root_size, root_unit, root_depth = self.program.root()
        assert (inspect_count(root_size),inspect_count(root_unit),inspect_count(root_depth)) == (256,2,level)
        self.indices.free_many(root_size,root_depth); self.context.arena.free(root_unit)
        slot = self.indices.input(level)
        metadata, previous, generated = self.program.step(slot)
        assert metadata == (0,spec.code,42,0,0,0)
        assert (inspect_count(previous),inspect_count(generated)) == ({1:256,2:168}[level],width)
        self.indices.free_many(slot,previous,generated)
        # Every original physical prefix remains present in the same order.
        old.rewind()
        for _ in range(2):
            saved = read_prefix(old,self.depth)
            assert bits(saved) == bits(directory)[:len(bits(directory))//2] * level
            saved.clear()
        assert old.read() == BLANK  # Exactly two complete physical prefixes.
        old.rewind()
        power = {1:176,2:344}[level]
        assert tuple(inspect_count(x) for x in (b,g,s)) == (2,5*3**power,3)
        handoffs.append({'depth':level,'width':width,'prefixes':2,'stock':11,
                         'before':2,'gap':'5*3^'+str(power),'suffix':3})
        original = bytes(current.cells)
        if level == 1:
            new_directory = Tape(); old.rewind()
            new_field = Fields.fixture(self.indices,self.context.arena,[(spec.code,zero_high)],catalogue.codes.bits)
            for _ in range(2):
                old_prefix = read_prefix(old,self.depth)
                append_tape(old_prefix,new_directory); append_tape(new_field.tape,new_directory)
                old_prefix.clear()
            old.rewind(); new_directory.rewind(); new_field.tape.clear()
            child_fields = self.indices.input(2)
            cb,cg,cs = (Count(x) for x in (b,g,s))
            try:
                transformed = yield from invoke(self.consumer,current,new_directory,count,child_fields,unused,cb,cg,cs)
                output = Tape(); outputs.append(output)
                transformed.rewind()
                while transformed.read() in (0,1):
                    output.append(1-transformed.read()); transformed.step(1)
                transformed.rewind(); transformed.clear(); output.rewind()
            finally:
                self.indices.free(child_fields); new_directory.clear()
                for value in (cb,cg,cs):value.close()
        else:
            # Deliberately tiny controlled permutation, not selected BIT.
            values = bits(current); output = Tape(); outputs.append(output)
            for bit in reversed(values): output.append(bit)
            output.rewind()
        assert bytes(current.cells) == original and current.head == old.head == self.program.tape.head == 1
        if level == 2 and mutation is not None:
            injected.append(mutation)
            if mutation == 'source_bit': current.cells[1] ^= 1
            elif mutation == 'directory_bit': old.cells[1] ^= 1
            elif mutation == 'output_head': output.step(1)
            else: raise AssertionError('unknown fixture mutation')
        returned.append(level)
        return output

    def invoke(owner,current,old,count,field_count,unused,b,g,s):
        local_indices=owner.indices; n=inspect_count(owner.parent_size); f=n//64
        columns=local_indices.input(f)
        geometry=Geometry(SimpleNamespace(dimension=64),local_indices,columns,owner.depth,spec.code,owner.program)
        leading=Count.product(unused,b)
        layout=Layout(geometry,owner.parent_size,owner.context.ring,3,leading,g,s)
        operands=[local_indices.input(v) for v in (0,86*f,42*f,inspect_count(owner.depth)+1)]
        event=Event('invoke',operands[0],operands[1],width=operands[2],depth=operands[3],
                    child_kind='good',source_code=spec.code,parent_identity=owner.program)
        saved_source, saved_directory = bytes(current.cells), bytes(old.cells)
        try:
            result = yield from child_call(owner,current,event,layout,old,count,field_count,unused,b)
            assert bytes(current.cells) == saved_source, 'independent checker: frozen source bytes changed'
            assert bytes(old.cells) == saved_directory, 'independent checker: frozen directory bytes changed'
            return result
        finally:
            layout.close();geometry.close();leading.close();local_indices.free_many(columns,*operands)

    node.SelectedNode.run_generator=controlled_run
    rejection = None
    try:
        with no_decode():
            output=complete(invoke(parent,source,directory,prefixes,fields,stock,before,gap,suffix))
        assert bits(output) == bytes(1-bit for bit in reversed(original_payload))
        assert bytes(source.cells)[1:] == original_payload
        assert bytes(directory.cells)==original_directory and bytes(program.tape.cells)==original_program
        assert source.head==output.head==directory.head==program.tape.head==1
        assert returned == [2,1]
        assert mutation is None, 'injected return corruption escaped the checker'
        assert indices.live==protected_indices and arena.live==protected_residues
        for frame in frames:
            audit(frame.indices); audit(frame.context.arena)
            assert not bits(frame.program.tape)
        output.clear()
    except (ValueError, AssertionError) as error:
        if mutation is None or injected != [mutation]: raise
        rejection = str(error)
        expected = {'source_bit':'independent checker: frozen source bytes changed',
                    'directory_bit':'independent checker: frozen directory bytes changed',
                    'output_head':'completed recursive return restores caller heads'}[mutation]
        assert rejection == expected
    finally:
        node.SelectedNode.run_generator=original_run
        for output in outputs: output.clear()
        source.clear();directory.clear();program.tape.clear()
        for value in (prefixes,stock,before,gap,suffix):value.close()
        indices.free_many(size,depth,fields);context.close();ring.close();arena.free(modulus)
    audit(indices);audit(arena)
    assert (type(common_topology).call.cache_info().currsize,
            type(common_topology).recipe.cache_info().currsize)==cache_sizes
    for frame in frames:
        audit(frame.indices); audit(frame.context.arena)
        assert not bits(frame.program.tape)
    if mutation is not None:
        return {'mutation':mutation,'rejection':rejection,'closed_frames':len(frames),
                'check_kind':'runtime head contract' if mutation=='output_head' else 'independent preserved-input oracle'}
    return {'source_request':identifier,'source_rank':42,'depths':2,'widths':[256,168,84],
            'selected_node_constructions':3+len(frames),'shared_topology_instances':1,
            'repeated_call_recipe_cache_growth':0,
            'sampled_old_prefixes':2,'controlled_payload_bits':23,
            'handoffs':handoffs,'return_order':returned,
            'scope':'real selected constructors, Callback.extend, Frame and directory handoff; controlled child consumer only',
            'complete_selected_GL64_payload_executed':False}


def run(catalogue=None):
    catalogue = Catalogue(3) if catalogue is None else catalogue
    return {'status':'PASS_RECURSIVE_JUNCTIONS','layouts':layouts(),'traces':traces(),
            'trampoline':trampoline(),'lifecycle':lifecycle(),'frame_handoff':frame_handoff(catalogue),
            'abort_cleanup':abort_cleanup(),'construction_failure':construction_failure(),
            'all_size_peel':all_size_peel(),
            'frame_mutations':[frame_handoff(catalogue, mutation)
                               for mutation in ('source_bit','directory_bit','output_head')]}


if __name__ == '__main__':
    print(json.dumps(run(),indent=2))
