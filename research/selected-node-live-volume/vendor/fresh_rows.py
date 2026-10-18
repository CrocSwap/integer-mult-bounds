"""Decode the caller's actual fresh row range and restore its original order."""
from cardinal_counts import Count, positive
from cardinality import radix_power
from records import Tape
from routes import copy_rows
from stream import Counter
from words import BLANK, need


def quotient(fresh,context,families):
    positive(fresh)
    unused=Count(fresh)
    try:
        need(unused.divide_small(families)==0,"complete fresh family factor")
        need(unused.divide_small(context.codes.size)==0,"complete fresh GL low factor")
        for _ in range(context.dimension*context.dimension):
            first=True
            for _ in radix_power(context.ring,context.q):
                if first:first=False
                else:need(unused.divide_small(context.q)==0,"complete fresh high factor")
        need(not unused.zero(),"nonempty unused row quotient")
        return unused
    except ValueError:
        unused.close()
        raise


def family_rows(context):
    result=Count(context.highs)
    result.multiply_small(context.codes.size)
    return result


def split(source,context,families,old_count,fibre):
    packets={family:Tape() for family in range(families)}
    rows,outer=family_rows(context),Counter(old_count)
    source.rewind()
    try:
        need(not outer.finished,"positive old physical prefix range")
        while not outer.finished:
            for family in range(families):copy_rows(source,packets[family],rows,fibre)
            outer.decrement()
        need(source.read()==BLANK,"complete row split")
        for tape in packets.values():tape.rewind()
        return packets
    except ValueError:
        for tape in packets.values():tape.clear()
        raise
    finally:rows.close();outer.close();source.rewind()


def merge(packets,context,families,old_count,fibre):
    need(set(packets)==set(range(families)),"complete live family inventory")
    rows,outer,output=family_rows(context),Counter(old_count),Tape()
    for tape in packets.values():tape.rewind()
    try:
        while not outer.finished:
            for family in range(families):copy_rows(packets[family],output,rows,fibre)
            outer.decrement()
        need(all(tape.read()==BLANK for tape in packets.values()),"complete restored family rows")
        output.rewind()
        return output
    except ValueError:
        output.clear()
        raise
    finally:
        rows.close();outer.close()
        for tape in packets.values():tape.rewind()
