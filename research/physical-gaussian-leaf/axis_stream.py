"""Complete encoded C-axis split, coefficient traversal and merge."""
import leaf_sources
leaf_sources.activate()
from cardinal_counts import Count
from compact_counts import copy_bits,power_two
from encoded import compare,subtract
from session import borrowed_tape
from signed_linear import c_pair
from stream import Counter
from words import BLANK,need


def c_axis(source,plan,position,width,coefficients,outer_rows,factory,inverse=False):
    need(compare(position,plan.bits) < 0, "selected C address bit exists")
    one = Count.literal(1)
    tail = subtract(plan.bits,position)
    after_bits = subtract(tail,one)
    before,after = power_two(position),power_two(after_bits)
    suffix,pair_count = Count.product(after,plan.record_bits),Count.product(after,coefficients)
    for value in (one,tail,after_bits,after):
        value.close()
    left,right,out_left,out_right,output = (factory() for _ in range(5))
    buffers = tuple(factory() for _ in range(4))
    rows,prefixes,pairs = Counter(outer_rows),None,None
    source.rewind()
    try:
        while not rows.finished:
            prefixes = Counter(before)
            while not prefixes.finished:
                copy_bits(source,left,suffix)
                copy_bits(source,right,suffix)
                left.rewind()
                right.rewind()
                pairs = Counter(pair_count)
                while not pairs.finished:
                    c_pair(left,right,out_left,out_right,width,buffers,inverse)
                    pairs.decrement()
                pairs.close()
                pairs = None
                need(left.read() == right.read() == BLANK, "complete paired C suffixes")
                for tape in (left,right):
                    borrowed_tape(tape).clear()
                for tape in (out_left,out_right):
                    tape.rewind()
                    copy_bits(tape,output,suffix)
                    need(tape.read() == BLANK, "complete C output suffix")
                    borrowed_tape(tape).clear()
                prefixes.decrement()
            prefixes.close()
            prefixes = None
            rows.decrement()
        need(source.read() == BLANK, "complete C-axis row packet")
        source.clear()
        output.rewind()
        return output
    except BaseException:
        output.clear()
        raise
    finally:
        for value in (before,suffix,pair_count,rows,prefixes,pairs):
            if value is not None:
                value.close()
        for tape in (left,right,out_left,out_right,*buffers):
            tape.clear()
