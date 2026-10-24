"""Encoded structured-page framing for the complete normalized core."""
from gaussian_sources import active
active()
from cardinal_counts import Count, positive
from encoded import compare, subtract
from gaussian_rationals import read_count
from ring_words import power_two
from router_metadata import ceiling_log, indices, owned
from words import need


def skip_bits(source, length):
    for _ in indices(length):
        need(source.read() in (0, 1), "complete Gaussian page bit field")
        source.step(1)


class Header:
    names = ("version", "p", "P", "width", "m", "target_length", "core_offset", "core_length",
             "boundary_length", "band", "cell_count")

    def __init__(self, page):
        self.fields = {}
        try:
            for name in self.names:
                self.keep(name, read_count(page))
            for name in self.names:
                if name != "core_offset":
                    positive(getattr(self, name))
            with owned(Count.literal(1)) as (one,):
                need(compare(self.version, one) == 0, "Gaussian page version")
            need(compare(self.p, self.P) <= 0 and compare(self.P, self.width) < 0,
                 "Gaussian page precision order")
            need(compare(self.boundary_length, self.m) <= 0 and compare(self.cell_count, self.m) <= 0,
                 "Gaussian page row counts")
            self.keep("core_end", Count(self.core_offset))
            self.core_end.add(self.core_length)
            need(compare(self.core_end, self.m) <= 0, "Gaussian page core range")
            self.keep("w", Count(self.band))
            need(self.w.divide_small(2) == 0 and not self.w.zero(), "positive two-sided Gaussian boundary width")
            with owned(Count(self.p)) as (maximum_band,):
                maximum_band.multiply_small(2)
                need(compare(self.band, maximum_band) <= 0, "Gaussian boundary width within precision allowance")
            with owned(Count(self.m), Count.literal(2)) as (maximum_target, two):
                maximum_target.multiply_small(2)
                maximum_target.add(two)
                need(compare(self.m, self.target_length) <= 0
                     and compare(self.target_length, maximum_target) <= 0, "near-one complete Gaussian selection volume")
            self.keep("input_width", Count(self.p))
            self.input_width.increment()
            self.input_width.increment()
            self.keep("shift", subtract(self.P, self.p))
            self.keep("normal_shift", Count(self.P))
            self.normal_shift.multiply_small(2)
            with owned(subtract(self.normal_shift, self.p), Count(self.p)) as (base, scaled_p):
                scaled_p.multiply_small(32)
                with owned(ceiling_log(scaled_p)) as (j,):
                    self.normal_shift.close()
                    self.fields["normal_shift"] = Count(base)
                    self.normal_shift.add(j)
            self.keep("work_unit", power_two(self.P))
            with owned(Count(self.p)) as (twice_p,):
                twice_p.multiply_small(2)
                self.keep("norm_bound", power_two(twice_p))
            self.keep("prefix_bits", Count.product(self.w, self.width))
            with owned(Count.product(self.band, self.band)) as (entries,):
                self.keep("coupling_bits", Count.product(entries, self.width))
            with owned(Count.product(self.boundary_length, self.band)) as (entries,):
                self.keep("lower_bits", Count.product(entries, self.width))
            with owned(Count(self.band)) as (columns,):
                columns.increment()
                with owned(Count.product(self.boundary_length, columns)) as (entries,):
                    self.keep("upper_bits", Count.product(entries, self.width))
        except BaseException:
            self.close()
            raise

    def keep(self, name, value):
        need(name not in self.fields, "one Gaussian page role")
        self.fields[name] = value
        return value

    def __getattr__(self, name):
        return self.fields[name]

    def close(self):
        for value in reversed(tuple(self.fields.values())):
            value.close()
        self.fields.clear()

    def repeat(self, page):
        page.rewind()
        for name in self.names:
            with owned(read_count(page)) as (value,):
                need(compare(value, getattr(self, name)) == 0, "unchanged Gaussian page header")

    def skip_selection(self, page):
        for _ in indices(self.m):
            read_count(page).close()


class Cell:
    def __init__(self, page, header):
        self.length = self.inside = self.boundary = self.bits = self.inside_bits = self.boundary_bits = None
        try:
            self.length, self.inside, self.boundary = (read_count(page) for _ in range(3))
            positive(self.length)
            positive(self.boundary)
            with owned(Count(self.inside), Count(header.band), Count(header.p)) as (total, four_w, maximum):
                total.add(self.boundary)
                four_w.multiply_small(2)
                maximum.multiply_small(5)
                need(compare(total, self.length) == 0 and compare(self.length, maximum) <= 0,
                     "Gaussian cell row count and source length bound")
                if self.inside.zero():
                    need(compare(self.length, four_w) <= 0, "short clipped cell has only boundary rows")
                else:
                    need(compare(self.inside, header.band) > 0
                         and compare(self.boundary, header.band) == 0, "separate interior edge buffers")
            self.bits = Count.product(self.length, header.width)
            self.inside_bits = Count.product(self.inside, header.width)
            self.boundary_bits = Count.product(self.boundary, header.width)
        except BaseException:
            self.close()
            raise

    def close(self):
        for value in (self.length, self.inside, self.boundary, self.bits, self.inside_bits, self.boundary_bits):
            if value is not None:
                value.close()
        self.length = self.inside = self.boundary = self.bits = self.inside_bits = self.boundary_bits = None
