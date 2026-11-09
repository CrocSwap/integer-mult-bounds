"""Literal short-field/header operations for one prepared union substream.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from cardinal_counts import Count
from compact_counts import copy_bits
from encoded import compare, subtract
from ring_words import read_signed, write_signed
from router_metadata import indices, owned
from session import borrowed_tape
from words import BLANK, need


def bit(source, *destinations):
    value=source.read();need(value in (0,1),'complete union binary field')
    source.step(1)
    for out in destinations:out.append(value)
    return value


def zeros(destination, length):
    for _ in indices(length):destination.append(0)


def zero_field(source,length):
    for _ in indices(length):need(bit(source)==0,'zero union padding')


def big_field(source,length,raw=None,normal=None,masked=False,zero=False):
    value=Count.literal(0)
    try:
        for _ in indices(length):
            v=bit(source)
            if raw is not None:raw.append(v)
            if normal is not None:normal.append(0 if masked else v)
            need(not zero or v==0,'inactive union ordinal is zero')
            value.multiply_small(2)
            if v:value.increment()
        return value
    except BaseException:value.close();raise


def raw_field(source,length,raw,normal,masked=False,zero=False):
    for _ in indices(length):
        v=bit(source,raw);normal.append(0 if masked else v)
        need(not zero or v==0,'inactive union ordinal is zero')


def same_bits(first,second):
    first.rewind();second.rewind()
    try:
        while first.read() in (0,1):
            need(bit(first)==bit(second),'one common union line header')
        need(first.read()==second.read()==BLANK,'matching union header extents')
    finally:first.rewind();second.rewind()


def canonical_word(source,archive,destination,width,pool):
    raw,canonical=pool.acquire(),pool.acquire()
    try:
        copy_bits(source,raw,width);raw.rewind()
        with owned(read_signed(raw,width)) as (value,):
            write_signed(value,canonical,width)
        need(raw.read()==BLANK,'complete union scalar word')
        canonical.rewind();same_bits(raw,canonical)
        copy_bits(raw,archive,width);copy_bits(canonical,destination,width)
    finally:raw.clear();canonical.clear()


def line(source,archive,real,imaginary,e_table,j_mask,
         axes,coordinate_bits,tag_bits,axis,round_index,length,selected,width,pool):
    """Advance one complete E-line; all metadata remain literal physical bits."""
    first,current,flags=pool.acquire(),pool.acquire(),pool.acquire()
    e_table.rewind();j_mask.rewind()
    try:
        with owned(Count.literal(0),Count.literal(0)) as (selected_seen,previous_coordinate):
            for ordinal in indices(length):
                need(bit(source,archive,current)==0 and bit(source,archive,current)==1,
                     'union record marker 01')
                for i in indices(axes):
                    if compare(i,axis)==0:
                        with owned(big_field(source,coordinate_bits,archive,current,True),
                                   big_field(e_table,coordinate_bits)) as (coordinate,expected):
                            need(compare(coordinate,expected)==0,'union active coordinate matches E table')
                            need(ordinal.zero() or compare(coordinate,previous_coordinate)>0,
                                 'strictly increasing union E table')
                            with owned(subtract(coordinate,previous_coordinate)) as (increment,):
                                previous_coordinate.add(increment)
                    else:raw_field(source,coordinate_bits,archive,current)
                with owned(Count.literal(0),Count.literal(0)) as (ones,earlier):
                    for i in indices(axes):
                        flag=bit(source,archive,current,flags)
                        if flag:
                            ones.increment()
                            if compare(i,axis)<0:earlier.increment()
                        if compare(i,axis)==0:need(flag==1,'active union membership flag')
                    need(compare(earlier,round_index)==0,'current union ascending-axis round')
                    flags.rewind()
                    for i in indices(axes):
                        flag=bit(flags)
                        if compare(i,axis)==0:
                            with owned(big_field(source,coordinate_bits,archive,current,True)) as (rank,):
                                need(compare(rank,ordinal)==0,'consecutive complete union E-line ordinals')
                        else:raw_field(source,coordinate_bits,archive,current,zero=not flag)
                    need(flags.read()==BLANK,'complete union membership flags')
                    with owned(big_field(source,tag_bits,archive,current),
                               big_field(source,tag_bits,archive,current)) as (count,tag):
                        need(compare(count,ones)==0,'union stored flag count')
                        need(compare(tag,axis)==0,'union active tag')
                current.rewind()
                if ordinal.zero():
                    while current.read() in (0,1):bit(current,first)
                    need(current.read()==BLANK,'complete first union header');first.rewind()
                else:same_bits(first,current)
                borrowed_tape(current).clear();borrowed_tape(flags).clear()
                if bit(j_mask):selected_seen.increment()
                canonical_word(source,archive,real,width,pool)
                canonical_word(source,archive,imaginary,width,pool)
            need(e_table.read()==j_mask.read()==BLANK,'complete union E table and J mask')
            need(compare(selected_seen,selected)==0,'union J-mask cardinality')
        real.rewind();imaginary.rewind()
    finally:
        e_table.rewind();j_mask.rewind()
        for tape in (first,current,flags):tape.clear()


def transpose(source,destination,rows,columns,width,pool,inverse=False):
    """B-column short-field lockstep; O(log B) stages, fixed tape roles."""
    work,other,left,right=(pool.acquire() for _ in range(4))
    try:
        with owned(Count.product(rows,columns)) as (entries,):
            with owned(Count.product(entries,width)) as (bits,):
                source.rewind();copy_bits(source,work,bits)
                need(source.read()==BLANK,'complete union transpose source');source.rewind();work.rewind()
        with owned(Count(columns) if inverse else Count.literal(1),
                   Count.literal(1) if inverse else Count(columns)) as (span,groups):
            if inverse:
                need(span.divide_small(2)==0,'dyadic inverse union transpose')
            while (not span.zero() if inverse else compare(span,columns)<0):
                if not inverse:need(groups.divide_small(2)==0,'dyadic union transpose columns')
                with owned(Count.product(span,width)) as (chunk,):
                    with owned(Count.product(rows,chunk)) as (whole,):
                        for _ in indices(groups):
                            if inverse:
                                for _ in indices(rows):
                                    copy_bits(work,left,chunk);copy_bits(work,right,chunk)
                            else:
                                copy_bits(work,left,whole);copy_bits(work,right,whole)
                        need(work.read()==BLANK,'complete union transpose split')
                        left.rewind();right.rewind()
                        for _ in indices(groups):
                            if inverse:
                                copy_bits(left,other,whole);copy_bits(right,other,whole)
                            else:
                                for _ in indices(rows):
                                    copy_bits(left,other,chunk);copy_bits(right,other,chunk)
                        need(left.read()==right.read()==BLANK,'complete union transpose merge')
                borrowed_tape(work).clear();borrowed_tape(left).clear();borrowed_tape(right).clear()
                other.rewind();work,other=other,work
                if inverse:
                    span.divide_small(2);groups.multiply_small(2)
                else:span.multiply_small(2)
            with owned(Count.product(rows,columns)) as (entries,):
                with owned(Count.product(entries,width)) as (bits,):copy_bits(work,destination,bits)
            need(work.read()==BLANK,'complete union transpose result')
        destination.rewind()
    finally:
        source.rewind()
        for tape in (work,other,left,right):tape.clear()


def select_rows(source,destination,j_mask,length,padded,selected_padded,block,width):
    """Extract J from a padded E row-major matrix, retaining column order."""
    source.rewind();j_mask.rewind()
    try:
        with owned(Count.product(block,width)) as (row_bits,),owned(Count.literal(0)) as (seen,):
            for row in indices(padded):
                if compare(row,length)<0:
                    take=bit(j_mask)
                    if take:
                        copy_bits(source,destination,row_bits);seen.increment()
                    else:
                        for _ in indices(row_bits):bit(source)
                else:zero_field(source,row_bits)
            need(source.read()==j_mask.read()==BLANK,'complete selected union rows')
            while compare(seen,selected_padded)<0:zeros(destination,row_bits);seen.increment()
        destination.rewind()
    finally:source.rewind();j_mask.rewind()


def merge_rows(original,selected,destination,j_mask,length,padded,selected_padded,block,width):
    original.rewind();selected.rewind();j_mask.rewind()
    try:
        with owned(Count.product(block,width)) as (row_bits,),owned(Count.literal(0)) as (seen,):
            for row in indices(padded):
                if compare(row,length)<0:
                    if bit(j_mask):
                        for _ in indices(row_bits):bit(original)
                        copy_bits(selected,destination,row_bits);seen.increment()
                    else:copy_bits(original,destination,row_bits)
                else:zero_field(original,row_bits);zeros(destination,row_bits)
            while compare(seen,selected_padded)<0:zero_field(selected,row_bits);seen.increment()
            need(original.read()==selected.read()==j_mask.read()==BLANK,'complete merged union rows')
        destination.rewind()
    finally:original.rewind();selected.rewind();j_mask.rewind()
