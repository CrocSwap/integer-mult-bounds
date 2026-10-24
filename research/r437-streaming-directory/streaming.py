"""Complete source-order high-prefix streaming with fixed emission roles.

JoyboyBrian; substantial OpenAI Codex assistance; Apache-2.0.
The source old-prefix reader, odometer and packet primitives retain their authors.
"""
from types import FunctionType,SimpleNamespace
from cardinal_counts import Count,positive
from records import Tape,RECORD_END,append_finite,append_word
from stream import Counter
from words import BLANK,need
import directory,packet_engine,episode


def visit(old,old_fields,old_count,code,context,consume):
    """Synchronously consume every complete produced prefix; callback is read-only.

    The callback must restore the current prefix head and must not retain its
    physical identity after returning. Source validation is retained unchanged.
    """
    need(0<=code<context.codes.limit,'new compiled source code')
    positive(old_count)
    highs=Count(context.highs)
    try:
        positive(highs);expected=Count.product(old_count,highs)
    finally:highs.close()
    emitted=Count.literal(0)
    outer=Counter(old_count);saved,prefix,reader_tape=Tape(),Tape(),Tape()
    high=None;returned=False
    init=FunctionType(Counter.__init__.__code__,dict(Counter.__init__.__globals__,Tape=lambda:reader_tape))
    def reader_count(word):
        obj=object.__new__(Counter);init(obj,word);return obj
    read=FunctionType(directory.old_prefix.__code__,dict(directory.old_prefix.__globals__,
         Tape=lambda:saved,Counter=reader_count))
    old.rewind()
    try:
        high=directory.Odometer(context)
        while not outer.finished:
            read(old,old_fields,context)
            while not high.finished:
                directory.append_tape(saved,prefix)
                append_finite(prefix,code,context.codes.bits)
                for row in high.digits:
                    for digit in row:append_word(prefix,digit)
                prefix.append(RECORD_END);prefix.rewind()
                consume(prefix)
                prefix.clear();emitted.increment();high.advance()
            # Original carry leaves every high digit zero at the terminal edge.
            high.finished=False;saved.clear();outer.decrement()
        need(old.read()==BLANK and emitted.equals(expected),'complete streamed raw directory')
        returned=True
        return expected
    finally:
        old.rewind();saved.clear();prefix.clear();reader_tape.clear()
        if high is not None:high.close()
        outer.close();emitted.close()
        if not returned:expected.close()


def run(source,target,events,layout,old,old_fields,old_count,code,context,coefficient,observe=None):
    """Full producer -> actual prefix-local leaf -> actual XOR consumer."""
    need(len({id(source),id(target),id(old)})==3,'distinct streamed borrowed roles')
    fibre,single,output=layout.fibre(),Count.literal(1),Tape()
    one=old_fields.arena.literal(1)
    # old_fields is an index Word; increment with its actual encoded arithmetic.
    from words import Unsigned
    field_count,carry=Unsigned(old_fields.arena).add(old_fields,one)
    old_fields.arena.free(one)
    need(not carry,'streamed field-count margin')
    source.rewind();target.rewind();returned=False
    def consume(prefix):
        left,right=Tape(),Tape();result=consumed=None
        try:
            from bitstream import copy_bits
            copy_bits(source,left,fibre);copy_bits(target,right,fibre)
            left.rewind();right.rewind()
            result=packet_engine.run(left,events(),layout,prefix,single,field_count,coefficient)
            if observe is not None:observe(result)
            consumed=episode.xor_packet(result,right,SimpleNamespace(highs=single),single,fibre)
            copy_bits(consumed,output,fibre)
            need(consumed.read()==BLANK,'complete streamed local XOR result')
        finally:
            if consumed is not None:consumed.clear()
            if result is not None and result is not left:result.clear()
            left.clear();right.clear();prefix.rewind()
    try:
        count=visit(old,old_fields,old_count,code,context,consume)
        count.close()
        need(source.read()==target.read()==BLANK,'complete streamed payload packet')
        output.rewind();returned=True;return output
    finally:
        source.rewind();target.rewind();fibre.close();single.close();old_fields.arena.free(field_count)
        if not returned:output.clear()
