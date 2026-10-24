"""Exact principal-window and old-H Schur setup, then structured page emission."""
from gaussian_sources import active
active()
from cardinal_counts import Count, positive
from compact_counts import append_bits
from encoded import compare, divide, subtract
from gaussian_boundary import prepare_bands
from gaussian_interior import InteriorFactors
from gaussian_matrix import Matrix, inverse, lu
from gaussian_rationals import Rational, read_count, write_count
from ring_words import Signed, add, difference, write_signed
from router_metadata import ceiling_log, indices, owned
from words import BLANK, need


class NumberList:
    def __init__(self, pool):
        self.tape = pool.acquire()
        self.length = Count.literal(0)

    def append(self, value):
        self.tape.rewind()
        while self.tape.read() != BLANK:
            self.tape.step(1)
        write_count(value, self.tape)
        self.length.increment()
        self.tape.rewind()

    def get(self, index):
        need(compare(index, self.length) < 0, "setup position-list index")
        self.tape.rewind()
        try:
            for _ in indices(index):
                read_count(self.tape).close()
            return read_count(self.tape)
        finally:
            self.tape.rewind()

    def close(self):
        self.tape.clear()
        self.length.close()


def signed_residue(value, modulus):
    quotient, remainder = divide(value.magnitude, modulus)
    try:
        if value.negative and not remainder.zero():
            quotient.increment()
            result = subtract(modulus, remainder)
            remainder.close()
            remainder = result
        return remainder, Signed(quotient, value.negative)
    except BaseException:
        quotient.close()
        remainder.close()
        raise


def same_signed(first, second):
    return first.negative == second.negative and compare(first.magnitude, second.magnitude) == 0


class Window:
    def __init__(self, axis, target_start, target_length, core_start, core_length, target_precision, pool):
        self.axis, self.pool = axis, pool
        self.fields = {}
        self.sources = self.targets = self.cells = self.source_cells = self.interior = self.boundary = None
        self.principal = self.kernel_inverse = self.schur = self.rounded_schur = None
        self.lower = self.upper = self.page = None
        try:
            positive(target_length)
            positive(core_length)
            positive(target_precision)
            need(compare(target_precision, axis.P) <= 0, "Gaussian work precision covers target grid")
            self.keep("target_start", target_start.copy())
            self.keep("target_length", Count(target_length))
            self.keep("core_start", core_start.copy())
            self.keep("core_length", Count(core_length))
            self.keep("p", Count(target_precision))
            self.keep("start", self.source_endpoint(target_start))
            with owned(Signed(Count(target_length))) as (length,):
                with owned(add(target_start, length)) as (end,):
                    self.keep("end", self.source_endpoint(end))
            with owned(difference(self.end, self.start)) as (length,):
                need(not length.negative and not length.magnitude.zero(), "nonempty Gaussian principal window")
                self.keep("m", Count(length.magnitude))
            with owned(Count(self.m)) as (covered,):
                covered.add(axis.w)
                need(compare(covered, axis.s) < 0, "Gaussian principal complement gap exceeds bandwidth")
            with owned(difference(core_start, self.start)) as (offset,):
                need(not offset.negative, "Gaussian core starts inside its source window")
                self.keep("core_offset", Count(offset.magnitude))
            with owned(Count(self.core_offset)) as (end,):
                end.add(core_length)
                need(compare(end, self.m) <= 0, "Gaussian core ends inside its source window")
            self.keep("band", Count(axis.w))
            self.band.multiply_small(2)
            self.keep("width", Count(axis.P))
            with owned(Count(self.p), Count(self.p), Count.literal(34)) as (guard, p_plus_two, constant):
                guard.multiply_small(8)
                p_plus_two.increment()
                p_plus_two.increment()
                with owned(ceiling_log(p_plus_two)) as (logarithm,):
                    logarithm.multiply_small(8)
                    self.width.add(guard)
                    self.width.add(logarithm)
                    self.width.add(constant)
            self.keep("cell_count", Count.literal(0))
            self.sources, self.targets, self.cells, self.source_cells, self.interior, self.boundary = (
                NumberList(pool) for _ in range(6))
            self.prepare_positions()
            self.principal = Matrix(self.m, self.m, pool, self.principal_entry)
            self.prepare_schur()
            self.compile_page()
            self.close_dense()
        except BaseException:
            self.close()
            raise

    def keep(self, name, value):
        need(name not in self.fields, "one Gaussian window setup role")
        self.fields[name] = value
        return value

    def __getattr__(self, name):
        return self.fields[name]

    def close_dense(self):
        for name in ("principal", "kernel_inverse", "schur", "rounded_schur", "lower", "upper"):
            value = getattr(self, name)
            if value is not None:
                value.close()
                setattr(self, name, None)

    def close(self):
        self.close_dense()
        for name in ("sources", "targets", "cells", "source_cells", "interior", "boundary"):
            value = getattr(self, name)
            if value is not None:
                value.close()
                setattr(self, name, None)
        if self.page is not None:
            self.page.clear()
            self.page = None
        for value in reversed(tuple(self.fields.values())):
            value.close()
        self.fields.clear()

    def source_endpoint(self, target):
        with owned(target.copy(), Signed(Count.literal(1))) as (twice, one):
            twice.magnitude.multiply_small(2)
            with owned(difference(twice, one)) as (shifted,):
                numerator = Signed(Count.product(shifted.magnitude, self.axis.s), shifted.negative)
        denominator = Count(self.axis.t)
        denominator.multiply_small(2)
        with owned(Rational(numerator, denominator)) as (value,):
            return value.integer_part(True)

    def lifted_nearest(self, source):
        residue, period = signed_residue(source, self.axis.s)
        try:
            with owned(self.axis.field(residue, 4)) as (nearest,):
                with owned(Signed(Count.product(period.magnitude, self.axis.t), period.negative)) as (offset,):
                    result = add(nearest.numerator, offset)
            return residue, period, result
        except BaseException:
            residue.close()
            period.close()
            raise

    def prepare_positions(self):
        previous_period = previous_phase = None
        cell_start = Count.literal(0)
        previous_offset = None
        try:
            for position in indices(self.m):
                with owned(Signed(Count(position))) as (offset,):
                    with owned(add(self.start, offset)) as (source,):
                        residue, period, nearest = self.lifted_nearest(source)
                with owned(residue, period, nearest):
                    with owned(difference(nearest, self.target_start)) as (offset,):
                        need(not offset.negative and compare(offset.magnitude, self.target_length) < 0,
                             "complete Gaussian C selection lies in its target halo")
                        need(previous_offset is None or compare(previous_offset, offset.magnitude) < 0,
                             "strictly increasing Gaussian C selection")
                        if previous_offset is not None:
                            previous_offset.close()
                        previous_offset = Count(offset.magnitude)
                        self.targets.append(offset.magnitude)
                    self.sources.append(residue)
                    with owned(self.axis.field(residue, 2)) as (phase,):
                        if previous_period is not None and (not same_signed(period, previous_period)
                                                            or phase.compare(previous_phase) != 0):
                            with owned(subtract(position, cell_start)) as (length,):
                                self.emit_cell(cell_start, length)
                            cell_start.close()
                            cell_start = Count(position)
                        if previous_period is not None:
                            previous_period.close()
                            previous_phase.close()
                        previous_period, previous_phase = period.copy(), phase.copy()
            with owned(subtract(self.m, cell_start)) as (length,):
                self.emit_cell(cell_start, length)
            with owned(Signed(Count.literal(1))) as (one,):
                with owned(difference(self.start, one)) as (before,):
                    residue, period, nearest = self.lifted_nearest(before)
                with owned(residue, period, nearest):
                    with owned(difference(self.target_start, nearest)) as (gap,):
                        need(not gap.negative and not gap.magnitude.zero(), "complete left Gaussian selection endpoint")
            residue, period, nearest = self.lifted_nearest(self.end)
            with owned(residue, period, nearest):
                with owned(Signed(Count(self.target_length))) as (length,):
                    with owned(add(self.target_start, length)) as (target_end,):
                        with owned(difference(nearest, target_end)) as (gap,):
                            need(not gap.negative, "complete right Gaussian selection endpoint")
        finally:
            cell_start.close()
            for value in (previous_period, previous_phase, previous_offset):
                if value is not None:
                    value.close()

    def emit_cell(self, start, length):
        positive(length)
        with owned(Count(self.axis.w)) as (four_w,):
            four_w.multiply_small(4)
            long = compare(length, four_w) > 0
        interior = subtract(length, self.band) if long else Count.literal(0)
        boundary = Count(self.band if long else length)
        try:
            for value in (start, length, interior, boundary):
                self.cells.append(value)
            with owned(subtract(length, self.axis.w) if long else Count.literal(0)) as (last_start,):
                for offset in indices(length):
                    self.source_cells.append(self.cell_count)
                    with owned(Count(start)) as (position,):
                        position.add(offset)
                        if not long or compare(offset, self.axis.w) < 0 or compare(offset, last_start) >= 0:
                            self.boundary.append(position)
                        else:
                            self.interior.append(position)
            self.cell_count.increment()
        finally:
            interior.close()
            boundary.close()

    def principal_entry(self, row, column):
        with owned(self.sources.get(row)) as (first,):
            with owned(self.sources.get(column)) as (second,):
                return self.axis.matrix.get(first, second)

    def prepare_schur(self):
        if not self.interior.length.zero():
            # Invert OLD truncated G in each cell. Exact similarity weights
            # cancel inside each Schur correction and return once at the end.
            self.kernel_inverse = Matrix(self.interior.length, self.interior.length, self.pool)
            self.cells.tape.rewind()
            with owned(Count.literal(0)) as (base,):
                for _ in indices(self.cell_count):
                    with owned(read_count(self.cells.tape), read_count(self.cells.tape),
                               read_count(self.cells.tape), read_count(self.cells.tape)) as (_, _length, inside, _boundary):
                        if inside.zero():
                            continue
                        block = Matrix(inside, inside, self.pool, self.kernel_entry)
                        inverted = None
                        try:
                            inverted = inverse(block)
                            for i in indices(inside):
                                with owned(Count(base)) as (row,):
                                    row.add(i)
                                    for j in indices(inside):
                                        with owned(Count(base)) as (column,):
                                            column.add(j)
                                            with owned(inverted.get(i, j)) as (value,):
                                                self.kernel_inverse.set(row, column, value)
                        finally:
                            block.close()
                            if inverted is not None:
                                inverted.close()
                        base.add(inside)
                need(compare(base, self.interior.length) == 0, "complete old-kernel interior inverse bank")
            self.cells.tape.rewind()
        self.schur = Matrix(self.boundary.length, self.boundary.length, self.pool, self.schur_entry)
        def rounded(i, j):
            with owned(self.schur.get(i, j)) as (value,):
                return Rational(value.rounded(self.axis.P), Count(self.axis.unit))
        self.rounded_schur = Matrix(self.boundary.length, self.boundary.length, self.pool, rounded)
        for i in indices(self.boundary.length):
            for j in indices(self.boundary.length):
                with owned(Signed(Count(i)), Signed(Count(j))) as (left, right):
                    with owned(difference(left, right)) as (distance,):
                        if compare(distance.magnitude, self.band) > 0:
                            with owned(self.schur.get(i, j)) as (entry,):
                                need(entry.numerator.magnitude.zero(), "principal Schur has no nonlocal band fill")
        self.lower, self.upper = lu(self.rounded_schur)

    def kernel_entry(self, i, j):
        with owned(Signed(Count(i)), Signed(Count(j))) as (left, right):
            with owned(difference(left, right)) as (distance,):
                if compare(distance.magnitude, self.axis.w) > 0:
                    return Rational.literal(0)
                return self.axis.kernel.get(distance.magnitude, self.axis.zero)

    def schur_entry(self, i, j):
        with owned(self.boundary.get(i)) as (row,):
            with owned(self.boundary.get(j)) as (column,):
                result = self.principal.get(row, column)
                correction = None
                try:
                    with owned(self.source_cells.get(row)) as (cell,):
                        with owned(self.source_cells.get(column)) as (other,):
                            same_cell = compare(cell, other) == 0
                        if same_cell:
                            correction = Rational.literal(0)
                            for a in indices(self.interior.length):
                                with owned(self.interior.get(a)) as (source,):
                                    with owned(self.source_cells.get(source)) as (source_cell,):
                                        if compare(source_cell, cell) != 0:
                                            continue
                                    with owned(self.kernel_entry(row, source)) as (first,):
                                        if first.numerator.magnitude.zero():
                                            continue
                                        for b in indices(self.interior.length):
                                            with owned(self.interior.get(b)) as (target,):
                                                with owned(self.source_cells.get(target)) as (target_cell,):
                                                    if compare(target_cell, cell) != 0:
                                                        continue
                                                with owned(self.kernel_entry(target, column)) as (second,):
                                                    if second.numerator.magnitude.zero():
                                                        continue
                                                    with owned(self.kernel_inverse.get(a, b)) as (middle,):
                                                        with owned(first.times(middle)) as (partial,):
                                                            with owned(partial.times(second)) as (product,):
                                                                following = correction.plus(product)
                                                    correction.close()
                                                    correction = following
                            with owned(self.sources.get(row)) as (global_row,):
                                with owned(self.sources.get(column)) as (global_column,):
                                    with owned(self.axis.field(global_row, 0)) as (a_row,):
                                        with owned(self.axis.field(global_column, 0)) as (a_column,):
                                            with owned(a_row.over(a_column)) as (ratio,):
                                                with owned(correction.times(ratio)) as (weighted,):
                                                    following = result.minus(weighted)
                            result.close()
                            result = following
                    value, result = result, None
                    return value
                finally:
                    if result is not None:
                        result.close()
                    if correction is not None:
                        correction.close()

    def edge_position(self, start, length, offset, interior=False):
        if compare(offset, self.axis.w) < 0:
            result = Count(start)
            if interior:
                result.add(self.axis.w)
        else:
            with owned(Count(self.axis.w)) as (deduction,):
                deduction.multiply_small(3 if interior else 2)
                result = subtract(length, deduction)
            result.add(start)
        result.add(offset)
        return result

    def compile_page(self):
        self.page = self.pool.acquire()
        with owned(Count.literal(1)) as (version,):
            for value in (version, self.p, self.axis.P, self.width, self.m, self.target_length,
                          self.core_offset, self.core_length, self.boundary.length, self.band, self.cell_count):
                write_count(value, self.page)
        self.targets.tape.rewind()
        for _ in indices(self.m):
            with owned(read_count(self.targets.tape)) as (position,):
                write_count(position, self.page)
        self.targets.tape.rewind()
        self.cells.tape.rewind()
        with owned(self.axis.kernel.get(self.axis.one, self.axis.zero)) as (q,):
            with owned(q.rounded(self.axis.P)) as (q_grid,):
                for _ in indices(self.cell_count):
                    with owned(read_count(self.cells.tape)) as (start,):
                        with owned(read_count(self.cells.tape)) as (length,):
                            with owned(read_count(self.cells.tape)) as (inside,):
                                with owned(read_count(self.cells.tape)) as (boundary,):
                                    for value in (length, inside, boundary):
                                        write_count(value, self.page)
                                    if not inside.zero():
                                        self.write_local_factors(start, inside, q_grid.magnitude)
                                        for transpose in (False, True):
                                            for i in indices(self.band):
                                                with owned(self.edge_position(start, length, i, transpose)) as (row,):
                                                    for j in indices(self.band):
                                                        with owned(self.edge_position(start, length, j, not transpose)) as (column,):
                                                            with owned(self.principal.get(row, column)) as (value,):
                                                                with owned(value.rounded(self.axis.P)) as (rounded,):
                                                                    write_signed(rounded, self.page, self.width)
                                    for offset in indices(length):
                                        with owned(Count(start)) as (position,):
                                            position.add(offset)
                                            with owned(self.sources.get(position)) as (global_index,):
                                                with owned(self.axis.field(global_index, 3)) as (diagonal,):
                                                    with owned(diagonal.rounded(self.axis.P)) as (rounded,):
                                                        write_signed(rounded, self.page, self.width)
        self.cells.tape.rewind()
        first, second = prepare_bands(self.lower, self.upper, self.band, self.width, self.axis.P, self.pool)
        try:
            append_bits(first, self.page)
            append_bits(second, self.page)
        finally:
            first.clear()
            second.clear()
        self.page.rewind()

    def write_local_factors(self, start, length, q):
        weights = self.pool.acquire()
        factors = None
        try:
            for offset in indices(length):
                with owned(Count(start)) as (position,):
                    position.add(self.axis.w)
                    position.add(offset)
                    with owned(self.sources.get(position)) as (global_index,):
                        with owned(self.axis.field(global_index, 0)) as (weight,):
                            with owned(weight.rounded(self.axis.P)) as (rounded,):
                                write_signed(rounded, weights, self.width)
            weights.rewind()
            factors = InteriorFactors(length, self.width, self.axis.P, self.pool)
            factors.prepare(q, weights)
            factors.dump(self.page)
        finally:
            if factors is not None:
                factors.close()
            weights.clear()
