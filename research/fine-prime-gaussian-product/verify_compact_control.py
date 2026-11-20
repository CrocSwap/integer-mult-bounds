"""Compare compact continuation dispatch with the immutable physical source."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def load():
    from compact_ordinary import load_cohort
    load_cohort()


def fixture():
    import check_nested_model as model
    from check_join import Binding
    from compact_execution import CompactOrdinary
    from compact_machine import CompactProgram
    from directory import Context
    from macro_code import compile_node
    from words import Arena, Ring

    catalogue = model.Catalogue()
    topology = model.Topology(catalogue)
    arena, indices = Arena(3), Arena(8)
    modulus = arena.literal(2)
    ring = Ring(modulus)
    context = Context(ring,catalogue.codes)
    plans = model.compile_coefficients(catalogue, context, indices, model.UnitIncoming(context))
    binding = Binding(catalogue,plans)
    old = compile_node(topology, binding)
    program = CompactProgram(topology,binding)
    expected = old.operations
    pc = 0
    for target in expected:
        operation, following = program.step(pc)
        if operation != target or following <= pc:
            raise ArithmeticError("closed cursor differs from source compilation")
        pc = following
    if pc != program.extent or old.staged_roles != program.staged_roles:
        raise ArithmeticError("complete source program coverage")
    print("source_opcodes",len(expected),"reserved_labels",pc,flush=True)
    context.close()
    ring.close()
    arena.free(modulus)
    return CompactOrdinary(2,binding,topology,(program,),capacity=128,fixture_index_floor=64)


def check_digits():
    from compact_digits import digit_swap
    from cardinal_counts import Count
    from itertools import product
    from records import Tape
    from words import BLANK
    for q in (2,3,5,6,7,8,11):
        ext = (2,3,2)
        counts = [Count.literal(x) for x in ext]
        addresses = list(product(range(2),range(q),range(3),range(q),range(2)))
        # Every independent input column has a unique binary signature.
        for bit in range((len(addresses)-1).bit_length()):
            t = Tape()
            for i,_ in enumerate(addresses):
                t.append((i >> bit) & 1)
            t.rewind()
            out = digit_swap(t,q,*counts,Tape)
            for prefix,a,middle,b,suffix in addresses:
                value = (((prefix*q+b)*3+middle)*q+a)*2+suffix
                if out.read() != ((value >> bit)&1):
                    raise ArithmeticError("independent digit-swap input column")
                out.step(1)
            if out.read() != BLANK or t.head != 1:
                raise ArithmeticError("digit map boundary")
        for c in counts:
            c.close()
    print("true_q_digit_permutations",7,flush=True)


def check_ranks():
    from math import prod
    from compact_ordinary import Q
    from low_codes import LowCodes
    from compact_machine import RadixCounts
    class Fast(RadixCounts,LowCodes):
        def __init__(self,q,m):
            self.q,self.dimension=q,m
            self.radices=tuple(q**m-q**i for i in range(m))
            self.size=prod(self.radices)
    for q in (3,5,7):
        a,b=LowCodes(q,2),Fast(q,2)
        for i in range(a.size):
            low=b.unrank(i)
            if not (a.unrank(i)==low and b.rank(low)==i):
                raise ArithmeticError('source check failed at 92')
    cases,actual=0,Fast(Q,64)
    for i in (0,actual.size//2,actual.size-1):
        low=actual.unrank(i)
        if not (actual.rank(low)==i):
            raise ArithmeticError('source check failed at 96')
        cases+=1
    print("complete_GL2_primes",3,5,7,"true_GL64_ordinals",cases,"ordinal_bits",actual.size.bit_length(),flush=True)


def check_compiled_backend(packet):
    from time import monotonic
    from compact_ordinary import open_source,Q
    from cardinal_counts import Count
    from macro_binding import SelectedBinding
    from ordinary import unit_program
    from records import Fields, Tape
    from controller import Callback
    from session import erase_marker
    from words import Ring
    t=monotonic()
    engine=open_source(packet,Q)
    native=engine.native
    runtime=native.runtime
    program=runtime.programs[0]
    codes=runtime.binding.codes
    print("authentic_constructed",type(native).__name__,type(runtime).__name__,type(program).__name__,
          "root_slots",len(runtime.roles),"profile",native.profile,"seconds",round(monotonic()-t,3),flush=True)
    if not (native.profile.row_factor == 28416*9475):
        raise ArithmeticError('source check failed at 119')
    if not (native.profile.numerator==1 and native.profile.denominator==574):
        raise ArithmeticError('source check failed at 120')
    if not (runtime.binding.stock_multiple==9475 and runtime.topology.families==28416):
        raise ArithmeticError('source check failed at 121')
    if not (all(not b.words.touched for b in (*native.banks,runtime.arena,runtime.indices))):
        raise ArithmeticError('source check failed at 122')
    if not (type(runtime.binding) is SelectedBinding and codes.q == Q):
        raise ArithmeticError('source check failed at 123')
    print("header_bit_width",runtime.header.widths[2],flush=True)
    # Test the last source occurrence of the very last GL class, without walking its predecessors.
    j=next(i for i,e in enumerate(program.topology.schedule) if e["kind"]=="local_cover_sweep")
    event=program.topology.schedule[j]
    stage=event["stage"]
    entries,starts=program.skeletons[stage]
    start=program.bounds[j]+(program.topology.replicas*program.ngl-1)*starts[-1]
    if not (start>sys.maxsize):
        raise ArithmeticError('source check failed at 131')
    last=codes.unrank(codes.size-1)
    if not (codes.rank(last)==codes.size-1):
        raise ArithmeticError('source check failed at 133')
    operation,next_pc=program.step(start)
    if not (operation[:2]==("gather_route",("stage",0))):
        raise ArithmeticError('source check failed at 135')
    owner=program.topology.call(stage,program.topology.replicas-1).owners[0]
    if not (operation[2]==owner.family and operation[4].target_low==last):
        raise ArithmeticError('source check failed at 137')
    if not (next_pc==start+1):
        raise ArithmeticError('source check failed at 138')
    print("high_ordinal_owner",operation[2],"bits",start.bit_length(),"seconds",round(monotonic()-t,3),flush=True)
    # Test the source's first MOVE (or COPY), including its exact residual header and first closed block.
    r=next(i for i,e in enumerate(entries) if e[0]=="residual")
    pc=start+starts[r]
    op,after=program.step(pc)
    if not (op[0]=="residual_begin" and op[2].low==last):
        raise ArithmeticError('source check failed at 144')
    op2,following=program.step(after)
    if not (op2[0]=="block" and op2[1] is op[2] and following>after):
        raise ArithmeticError('source check failed at 146')
    print("high_ordinal_residual",op[2].identifier,op[2].plan.rank,op2[2][0],flush=True)
    # The physical header itself, including every parked address bit, survives its tape round trip.
    head=Tape()
    labels=(1,0,following,0,1,2,0,1)
    runtime.header.write(head,labels)
    if not (runtime.header.read(head)==labels):
        raise ArithmeticError('source check failed at 152')
    head.clear()
    erase_marker(head)
    # Test the actual selected root ingress with the numerical word extents of (e,w)=(64,1).
    counts=[Count.literal(i) for i in (Q,64)]
    a,idx=runtime.arena,runtime.indices
    with runtime.pool.install():
        a.prepare(counts[0])
        idx.prepare(counts[1])
        modulus=a.load(counts[0])
        size=idx.load(counts[1])
        zero=idx.zero()
        ring=Ring(modulus)
        raw=unit_program(idx,ring,size,zero,codes.bits)
        fields=Fields(idx,a,codes.bits)
        callback=Callback(ring,idx,raw,fields,runtime.binding.specifications,runtime.binding.ambient,
                          allow_fallback=True,leaf=True)
        coord=idx.zero()
        value=callback.weight(coord)
        if not (ring.raw.compare(value,ring.one)==0 and callback.raw.compare(callback.final_size,size)==0):
            raise ArithmeticError('source check failed at 171')
        if not (callback.depth.zero()):
            raise ArithmeticError('source check failed at 172')
        a.free(value)
        idx.free(coord)
        callback.close()
        raw.tape.clear()
        fields.tape.clear()
        ring.close()
        a.free(modulus)
        idx.free_many(size,zero)
        runtime.pool.empty()
        a.erase_owned()
        idx.erase_owned()
    for c in counts:
        c.close()
        erase_marker(c.tape)
    if not (not a.live and not idx.live):
        raise ArithmeticError('source check failed at 187')
    print("source_Q_selected_ROOT",64,1,"root_pool_peak",runtime.pool.peak,
          "numerical_slots",len(a.words.touched),len(idx.words.touched),"seconds",round(monotonic()-t,3),flush=True)


def check_short_input(packet):
    from time import monotonic
    from compact_ordinary import open_source,Q
    from cardinal_counts import Count
    from records import Tape
    from words import Ring
    from ordinary import unit_program
    start=monotonic()
    engine=open_source(packet,Q).native
    runtime=engine.runtime
    codes=runtime.binding.codes
    max_count,size_count,one,rows_count=(Count.literal(x) for x in
       (Q,64,1,28416*9475*codes.size))
    a,idx=engine.banks[0],engine.banks[3]
    a.prepare(max_count)
    idx.prepare(size_count)
    modulus=a.load(max_count)
    size=idx.load(size_count)
    zero=idx.zero()
    ring=Ring(modulus)
    program=unit_program(idx,ring,size,zero,codes.bits)
    runtime.arena.prepare(max_count)
    runtime.indices.prepare(size_count)
    payload, directory=Tape(),Tape()
    print("active_Q_root","rows_bits",(28416*9475*codes.size).bit_length(),"seconds",round(monotonic()-start,3),flush=True)
    try:
        runtime.run(payload,directory,program.tape,modulus,size,zero,one,rows_count,one,one,one)
    except ValueError as error:
        if str(error) != "opaque stream bit":
            raise
        if not (runtime.topology.families==28416 and runtime.binding.stock_multiple==9475):
            raise ArithmeticError('source check failed at 222')
        if not (runtime.pool.peak>=4):
            raise ArithmeticError('source check failed at 223')
        unused = runtime.count("unused")
        expected=Count.literal(9475)
        if not (unused.equals(expected)):
            raise ArithmeticError('source check failed at 226')
        expected.close()
        print("selected_C0_NODE_validated_rejected_truncated_payload",str(error),"macros",runtime.counts["macros"],"seconds",round(monotonic()-start,3),flush=True)
    else:
        raise AssertionError("empty selected C0 payload accepted")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, help="compact_source.py output at the real prime")
    parser.add_argument("--truncated-ingress", action="store_true",
                        help="run the selected NODE until its first absent payload bit")
    parser.add_argument("--physical", action="store_true",
                        help="execute the two complete fitted reduced-source roots")
    args = parser.parse_args()
    if args.truncated_ingress and args.source is None:
        parser.error("--truncated-ingress requires --source")
    load()
    check_ranks()
    check_digits()
    engine = fixture()
    if args.physical:
        from check_engine import check_case
        print(check_case(engine,5,1,1,1,True),flush=True)
        print(check_case(engine,2,2,3,2,False),flush=True)
        if not (all(b.dormant_marker == 4 for b in (*engine.banks, engine.runtime.arena, engine.runtime.indices))):
            raise ArithmeticError('source check failed at 252')
    if args.source:
        check_compiled_backend(args.source)
    if args.truncated_ingress:
        check_short_input(args.source)
