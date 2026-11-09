"""Paid source-bank scanning, dense membership production and odometer headers.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from cardinal_counts import Count, positive
from compact_counts import copy_bits
from encoded import compare, subtract
from router_metadata import indices, owned
from words import BLANK, LEFT, need
from boundary_pages import ceiling_division
from fast_boundary import dyadic
from union_bits import (PART_END, BLOCK_START, BLOCK_END, bit, symbol, move,
                            skip_bits, big, put_big, read_count, zeros)


def page_extents(length, block, width):
    if length.zero():
        return Count.literal(0), Count.literal(0)
    with owned(ceiling_division(length, block), Count.product(block, block),
               Count.literal(1)) as (blocks, square, one):
        with owned(Count.product(square, width), subtract(blocks, one)) as (tile, preceding):
            return Count.product(blocks, tile), Count.product(preceding, tile)


def axis_metadata(bank, side):
    symbol(bank, BLOCK_START)
    a = n = block = None
    try:
        a = read_count(bank)
        n = read_count(bank)
        block = read_count(bank)
        need(compare(a, side) <= 0 and compare(n, a) <= 0, 'bounded catalogue row counts')
        need(a.zero() == n.zero(), 'empty exposed axis exactly when empty boundary')
        with owned(Count.literal(2)) as (two,):
            need(compare(block, two) >= 0, 'complex bank block at least two')
        dyadic(block)
        return a, n, block
    except BaseException:
        for value in (a, n, block):
            if value is not None:
                value.close()
        raise


def axis_body(bank, a, n, block, h, width, e_table, mask=None, pages=None):
    with owned(Count.literal(0), Count.literal(0)) as (seen, previous):
        for rank in indices(a):
            with owned(big(bank, h)) as (coordinate,):
                need(rank.zero() or compare(coordinate, previous) > 0,
                     'strict source exposed coordinates')
                with owned(subtract(coordinate, previous)) as (delta,):
                    previous.add(delta)
                put_big(coordinate, e_table, h)
        symbol(bank, PART_END)
        for _ in indices(a):
            flag = bit(bank)
            if mask is not None:
                mask.append(flag)
            if flag:
                seen.increment()
        symbol(bank, PART_END)
        need(compare(seen, n) == 0, 'source J-mask cardinality')
    e_table.rewind()
    if mask is not None:
        mask.rewind()
    with owned(*page_extents(a, block, width), *page_extents(n, block, width)) as (ed, ec, jd, jc):
        extents = (ed, ec, ed, ec, jd, jc, jd, jc)
        for role, extent in enumerate(extents):
            if pages is None:
                skip_bits(bank, extent)
            else:
                copy_bits(bank, pages[role], extent)
                pages[role].rewind()
            symbol(bank, PART_END)
    symbol(bank, BLOCK_END)


def build_membership(bank, destination, e_table, axes, side, h, width):
    """Bank is after its context prefix. Build g dense ordered lookup blocks."""
    for _ in indices(axes):
        with owned(*axis_metadata(bank, side)) as (a, n, block):
            axis_body(bank, a, n, block, h, width, e_table)
            destination.append(BLOCK_START)
            next_coordinate = None
            with owned(Count.literal(0), Count.literal(0)) as (rank, zero):
                try:
                    if not a.zero():
                        next_coordinate = big(e_table, h)
                    for coordinate in indices(side):
                        member = next_coordinate is not None and compare(coordinate, next_coordinate) == 0
                        if next_coordinate is not None:
                            need(compare(coordinate, next_coordinate) <= 0,
                                 'source E coordinate occurs in the current core')
                        destination.append(int(member))
                        put_big(rank if member else zero, destination, h)
                        destination.append(PART_END)
                        if member:
                            rank.increment()
                            next_coordinate.close()
                            next_coordinate = None
                            if compare(rank, a) < 0:
                                next_coordinate = big(e_table, h)
                    need(next_coordinate is None and compare(rank, a) == 0 and e_table.read() == BLANK,
                         'complete source E merge with local coordinates')
                finally:
                    if next_coordinate is not None:
                        next_coordinate.close()
            destination.append(BLOCK_END)
            e_table.clear()
    need(bank.read() == BLANK, 'exact axis bank inventory')
    destination.rewind()


def axis_start(tape):
    while tape.read() != BLOCK_START:
        need(tape.read() in (0, 1, PART_END, BLOCK_END), 'within dense axis catalogue')
        tape.step(-1)
    tape.step(1)


def axis_end(tape):
    while tape.read() != BLOCK_END:
        need(tape.read() in (0, 1, PART_END), 'within dense axis body')
        tape.step(1)


def cell_next(tape, h):
    bit(tape)
    skip_bits(tape, h)
    symbol(tape, PART_END)


def state_init(catalogue, state, axes, h):
    catalogue.rewind()
    with owned(Count.literal(0)) as (zero,):
        for _ in indices(axes):
            symbol(catalogue, BLOCK_START)
            state.append(BLOCK_START)
            put_big(zero, state, h)
            bit(catalogue, state)
            copy_bits(catalogue, state, h)
            symbol(catalogue, PART_END)
            state.append(BLOCK_END)
            axis_end(catalogue)
            catalogue.step(1)
    need(catalogue.read() == BLANK, 'complete state catalogue')
    catalogue.step(-1)
    axis_start(catalogue)


def overwrite_state(state, catalogue, coordinate, h):
    """State head is at its coordinate; catalogue head at the selected cell."""
    put_big(coordinate, state, h, overwrite=True)
    state.write(bit(catalogue))
    state.step(1)
    for _ in indices(h):
        state.write(bit(catalogue))
        state.step(1)
    need(state.read() == BLOCK_END and catalogue.read() == PART_END,
         'matching state/cell field extents')
    with owned(Count(h)) as (distance,):
        distance.increment()
        move(catalogue, distance, -1)


def advance(catalogue, state, side, h):
    """Return true exactly at final carry. No L^g counter is ever constructed."""
    need(state.read() == BLANK, 'odometer state append end')
    state.step(-1)
    with owned(Count.literal(0), Count.literal(0)) as (carried, zero):
        while True:
            need(state.read() == BLOCK_END, 'last current odometer axis')
            while state.read() != BLOCK_START:
                state.step(-1)
            state.step(1)
            with owned(big(state, h)) as (coordinate,):
                move(state, h, -1)
                if not carried.zero():
                    for _ in indices(coordinate):
                        cell_next(catalogue, h)
                coordinate.increment()
                if compare(coordinate, side) < 0:
                    cell_next(catalogue, h)
                    overwrite_state(state, catalogue, coordinate, h)
                    for _ in indices(carried):
                        axis_end(catalogue)
                        catalogue.step(1)
                        symbol(catalogue, BLOCK_START)
                    while state.read() != BLANK:
                        state.step(1)
                    return False
                need(compare(coordinate, side) == 0, 'bounded odometer carry')
                axis_start(catalogue)
                overwrite_state(state, catalogue, zero, h)
            while state.read() != BLOCK_START:
                state.step(-1)
            state.step(-1)
            if state.read() == LEFT:
                state.step(1)
                while state.read() != BLANK:
                    state.step(1)
                return True
            catalogue.step(-1)
            need(catalogue.read() == BLOCK_START, 'reset catalogue start')
            catalogue.step(-1)
            need(catalogue.read() == BLOCK_END, 'preceding catalogue axis')
            axis_start(catalogue)
            carried.increment()


def header(state, target, axes, h, tag_bits):
    """Exactly the unchanged #4583 marker/coordinate/flag/ordinal/count layout."""
    target.append(0)
    target.append(1)
    with owned(Count.literal(0)) as (count,):
        for part in (0, 1, 2):
            state.rewind()
            for _ in indices(axes):
                symbol(state, BLOCK_START)
                if part == 0:
                    copy_bits(state, target, h)
                else:
                    skip_bits(state, h)
                flag = bit(state)
                if part == 1:
                    target.append(flag)
                    if flag:
                        count.increment()
                if part == 2:
                    copy_bits(state, target, h)
                else:
                    skip_bits(state, h)
                symbol(state, BLOCK_END)
            need(state.read() == BLANK, 'complete odometer header state')
        put_big(count, target, tag_bits)
        put_big(axes, target, tag_bits)
        target.rewind()
        return not count.zero()
