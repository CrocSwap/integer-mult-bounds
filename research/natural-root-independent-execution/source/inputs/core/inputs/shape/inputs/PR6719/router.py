"""Fixed-control physical split/merge for the delayed-cover batch ABI.

The low-type count L is fixed when compiling this table. Runtime block length
and repeat count enter only as canonical binary tape descriptors. The emitted
program uses no runtime callback, computed address, tape index or host counter.
The seven-symbol machine and binary-to-unary microcode are unchanged sources
by David Arias; the abstract batch layout is Ali Romman's #5829.
New physical lowering: thu-nmrc with substantial OpenAI Codex assistance.
Apache-2.0.
"""
from machine import Assembler, BLANK, LEFT, RIGHT, ZERO, ONE, UNIT
from counters import emit_binary_to_unary, emit_rewind


def ports(low_types):
    if type(low_types) is not int or low_types < 2:
        raise ValueError('The fixed compiled low-type count is at least two')
    return dict(banks=tuple(range(low_types)), source=low_types,
                output=low_types+1, repeats_input=low_types+2,
                block_input=low_types+3, repeats=low_types+4,
                block=low_types+5, binary_work=low_types+6,
                count=low_types+7)


def erase(asm, tape, prefix):
    """Erase a contiguous scratch extent, including its local LEFT marker."""
    loop, more, done = (asm.fresh(prefix+s) for s in ('_loop','_more','_done'))
    asm.label(loop)
    asm.branch(tape, {LEFT: done}, more)
    asm.label(more)
    asm.write(tape, BLANK)
    asm.move(tape, -1)
    asm.goto(loop)
    asm.label(done)
    asm.write(tape, BLANK)


def copy_block(asm, guide, source, target, fail, prefix):
    """Copy exactly the unary-guide length; never consume the opaque source."""
    emit_rewind(asm, guide, prefix+'_guide')
    loop, read, zero, one, advance, done = (
        asm.fresh(prefix+s) for s in ('_loop','_read','_zero','_one','_advance','_done'))
    asm.label(loop)
    asm.branch(guide, {UNIT: read, RIGHT: done}, fail)
    asm.label(read)
    asm.branch(source, {ZERO: zero, ONE: one}, fail)
    for label, value in ((zero,ZERO),(one,ONE)):
        empty=asm.fresh(prefix+'_empty')
        asm.label(label)
        asm.branch(target, {BLANK: empty}, fail)
        asm.label(empty)
        asm.write(target,value)
        asm.goto(advance)
    asm.label(advance)
    asm.move(source,1)
    asm.move(target,1)
    asm.move(guide,1)
    asm.goto(loop)
    asm.label(done)


def build(low_types, merge=False):
    """Compile one table for every positive runtime A,R, V=A*L*R.

    Split: source[a,l,r] -> bank_l[a,r]. Merge is the inverse address map.
    The split source or merge banks remain byte-identical. The new outputs
    are owned copies; they receive no productive credit. All heads return to
    local input/output origins; conversion workspace is physically blanked.
    """
    if type(merge) is not bool:
        raise ValueError('The direction is a fixed compile-time Boolean')
    p=ports(low_types)
    a=Assembler(p['count']); fail=a.fresh('invalid_router_state')
    destinations=(p['output'],) if merge else p['banks']
    scratch=(p['repeats'],p['block'],p['binary_work'])
    for tape in destinations+scratch:
        ok=a.fresh('initialize')
        a.branch(tape,{BLANK:ok},fail);a.label(ok)
        a.write(tape,LEFT);a.move(tape,1)
    emit_binary_to_unary(a,p['repeats_input'],p['binary_work'],p['repeats'],'repeat_count')
    emit_binary_to_unary(a,p['block_input'],p['binary_work'],p['block'],'block_length')
    loop,body,done=(a.fresh('batch_'+s) for s in ('loop','body','done'))
    a.label(loop);a.branch(p['repeats'],{UNIT:body,RIGHT:done},fail)
    a.label(body)
    # Fixed finite unrolling: L is a template constant, never a tape value.
    for low,bank in enumerate(p['banks']):
        source,target=(bank,p['output']) if merge else (p['source'],bank)
        copy_block(a,p['block'],source,target,fail,'type_'+str(low))
    a.move(p['repeats'],1);a.goto(loop)
    a.label(done)
    sources=p['banks'] if merge else (p['source'],)
    for source in sources:
        exact=a.fresh('exact_input_end')
        a.branch(source,{RIGHT:exact},fail);a.label(exact)
    for target in destinations:
        a.write(target,RIGHT)
    for tape in sources+destinations:
        emit_rewind(a,tape,'return_'+str(tape))
    for tape in scratch:
        erase(a,tape,'erase_'+str(tape))
    a.halt();a.label(fail)
    a.reject('batch shape, opaque-bit alphabet, or owned-work invariant')
    return a.finish()


def resource_bound(low_types,repeats,block):
    """Proof annotation only; the emitted controller never evaluates it."""
    if min(low_types,repeats,block)<1 or low_types<2:
        raise ValueError('positive shape and fixed L>=2')
    volume=low_types*repeats*block
    return {'volume':volume, 'microsteps':94*volume,
            'visited_span':13*volume}
