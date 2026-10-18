"""Complete generated child on one packet, with separately charged frame work.

The parent's frozen fields are the child's old directory. The unused U
coordinate alone supplies fresh rows; address spectators are never borrowed.
"""
from cardinal_counts import Count
from children import extend
from controller import Callback
from directory import Context, append_tape
from packet import read_prefix
from plan import Request
from records import Fields, Program
from words import Arena, RIGHT, Ring, Unsigned, need

REGISTER_CAPACITY=1 << 24


def copy_word(source,arena):
    """Copy an encoded value to a separate frame bank without decoding it."""
    out=arena.zero()
    source.rewind()
    try:
        while source.read()!=RIGHT:
            need(out.read()!=RIGHT,"equal frame word extents")
            out.write(source.read());source.step(1);out.step(1)
        need(out.read()==RIGHT,"complete frame word copy")
        out.rewind();return out
    except ValueError:
        arena.free(out);raise
    finally:source.rewind()


class Frame:
    def __init__(self,parent,program,event):
        # bits describes the existing physical word template, not a decoded
        # width, residue or address. Both frames have identical templates.
        self.arena=Arena(parent.context.arena.bits,REGISTER_CAPACITY)
        self.indices=Arena(parent.indices.bits,REGISTER_CAPACITY)
        self.modulus=self.ring=self.context=self.program=self.size=self.depth=self.node=None
        try:
            self.modulus=copy_word(parent.context.ring.modulus,self.arena)
            self.ring=Ring(self.modulus)
            self.context=Context(self.ring,parent.context.codes)
            self.program=Program(self.indices,self.arena,program.code_bits)
            append_tape(program.tape,self.program.tape);self.program.tape.rewind()
            self.size=copy_word(event.width,self.indices)
            self.depth=copy_word(event.depth,self.indices)
            from node import SelectedNode
            self.node=SelectedNode(self.context,self.indices,self.program,self.size,self.depth,
                                   parent.specifications.catalogue,parent.specifications)
        except BaseException:
            # The caller cannot close a constructor that never returned.
            # These are fresh, separate banks, so every remaining word belongs
            # to this failed frame, including partial child initialization.
            if self.program is not None:self.program.tape.clear()
            if self.context is not None:self.context.close()
            if self.ring is not None:self.ring.close()
            self.indices.rollback(frozenset())
            self.arena.rollback(frozenset())
            raise

    def close(self):
        self.program.tape.clear()
        self.indices.free_many(self.size,self.depth)
        self.context.close();self.ring.close();self.arena.free(self.modulus)
        need(not self.indices.live and not self.arena.live,"recursive frame numerical restoration")


def child_call(parent,source,event,layout,directory,prefixes,fields,stock,before):
    need(stock is not None and before is not None,"independent child row-stock and spectators")
    context,indices=parent.context,parent.indices
    need(event.parent_identity is parent.program and event.source_code==layout.geometry.source_code,
         "recursive call belongs to the frozen parent")
    raw=Unsigned(indices)
    need(raw.compare(event.width,parent.parent_size)<0,"strict recursive contraction")
    extents=layout.child_extents(event.first,event.second,event.width,before=before)
    extended=frame=callback=result=None
    returned=False
    first=None
    try:
        directory.rewind();first=read_prefix(directory,fields);directory.rewind()
        prefix=Fields(indices,context.arena,context.codes.bits);prefix.tape=first
        callback=Callback(context.ring,indices,parent.program,prefix,parent.specifications,
                          event.source_code,allow_fallback=True)
        zero=indices.zero()
        try:
            request=Request("child",zero,child_kind=event.child_kind,field=event.field,
                            reverse=event.reverse,half=event.half)
            extended=extend(callback,request)
        finally:indices.free(zero)
        callback.close();callback=None
        # Descriptor depends only on ancestor program and the finite branch;
        # the representative high prefix is not used to pick children.
        frame=Frame(parent,extended,event)
        extended.tape.clear();extended=None
        first.clear();first=None
        from scheduler import Invocation
        result=yield Invocation(frame.node.run_generator(source,directory,prefixes,stock,*extents))
        need(source.head==result.head==directory.head==parent.program.tape.head==1,
             "completed recursive return restores caller heads")
        returned=True
        return result
    finally:
        if result is not None and result is not source and not returned:result.clear()
        if callback is not None:callback.abort()
        if frame is not None:frame.close()
        if extended is not None:extended.tape.clear()
        if first is not None:first.clear()
        for extent in extents:extent.close()
        directory.rewind();source.rewind();parent.program.tape.rewind()
