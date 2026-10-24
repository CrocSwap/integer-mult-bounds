"""Encoded global tensor shape, common Gaussian policy and restoration guard."""
from tensor_sources import active
active()
from cardinal_counts import Count, positive
from compact_counts import read_fixed, write_fixed
from encoded import compare, subtract
from expansion_geometry import ProductionBlock
from expansion_records import Fields
from gaussian_rationals import read_count, write_count
from ring_words import power_two
from router_metadata import ceiling_log, indices, owned
from twiddle_setup import quotient
from words import BLANK, need


def band(precision, u):
    with owned(Count(precision)) as (numerator,):
        numerator.multiply_small(16)
        with owned(quotient(numerator, u, True)) as (target,):
            root = Count.literal(0)
            try:
                while True:
                    with owned(Count.product(root, root)) as (square,):
                        if compare(square, target) >= 0:
                            break
                    root.increment()
                root.increment()
                root.increment()
                return root
            except BaseException:
                root.close()
                raise


class Policy(Fields):
    def __init__(self, p, alpha):
        super().__init__()
        try:
            self.keep("block", ProductionBlock(p, alpha))
            for name in ("P", "sigma", "radius"):
                self.keep(name, Count(getattr(self.block, name)))
            with owned(Count.product(p, p)) as (square,):
                self.keep("halo", Count.product(square, p))
                self.halo.multiply_small(4096)
                with owned(Count.product(square, square)) as (fourth,):
                    with owned(Count.product(fourth, fourth)) as (eighth,):
                        self.keep("inner_bits", ceiling_log(eighth))
            self.keep("expansion_capacity", power_two(self.inner_bits))
            self.keep("w", band(p, self.block.u))
        except BaseException:
            self.close()
            raise


class TensorHeader(Fields):
    names = ("version", "mode", "p", "ell", "axes", "alpha", "inner_bits", "P",
             "sigma", "radius", "expansion_capacity", "halo", "w")

    def __init__(self, page):
        super().__init__()
        try:
            for name in self.names:
                self.keep(name, read_count(page))
            with owned(Count.literal(1)) as (one,):
                need(compare(self.version, one) == 0 and compare(self.mode, one) <= 0,
                     "tensor catalogue version and production mode")
        except BaseException:
            self.close()
            raise

    @classmethod
    def dump(cls, plan, page):
        for name in cls.names:
            write_count(getattr(plan, name), page)


class AxisRow(Fields):
    names = ("s", "t", "width", "tiles")

    def __init__(self, source):
        super().__init__()
        try:
            for name in self.names:
                self.keep(name, read_count(source))
        except BaseException:
            self.close()
            raise


class TensorPlan(Fields):
    """Common policy plus the complete source words and target-axis flags."""
    def __init__(self, sources, flags, axes, ell, p, alpha, inner_bits, P, sigma,
                 radius, expansion_capacity, halo, w, factory, production=False):
        super().__init__()
        self.sources = self.flags = self.axis_rows = None
        try:
            need(type(production) is bool, "compiled tensor production policy")
            self.keep("version", Count.literal(1))
            self.keep("mode", Count.literal(int(production)))
            for name, value in (("p", p), ("ell", ell), ("axes", axes), ("alpha", alpha),
                                ("inner_bits", inner_bits), ("P", P), ("sigma", sigma),
                                ("radius", radius), ("expansion_capacity", expansion_capacity),
                                ("halo", halo), ("w", w)):
                self.keep(name, Count(value))
                if name != "sigma":
                    positive(value)
            with owned(Count.literal(16), Count.literal(2)) as (sixteen, two):
                need(compare(p, sixteen) >= 0 and compare(ell, two) >= 0 and compare(ell, p) < 0,
                     "complete tensor chirp precision and exponent")
                need(compare(alpha, two) >= 0, "complete tensor integer alpha")
            need(compare(P, p) >= 0, "tensor work grid covers target grid")
            self.keep("dimensions", Count(axes))
            self.dimensions.increment()
            self.keep("d", Count(self.dimensions))
            self.d.increment()
            self.keep("L", power_two(inner_bits))
            self.keep("u", Count.product(alpha, alpha))
            self.keep("target_halo", Count(halo))
            self.target_halo.multiply_small(2)
            self.target_halo.add(self.L)
            with owned(Count(p)) as (scaled,):
                scaled.multiply_small(32)
                self.keep("j", ceiling_log(scaled))
            with owned(Count(self.u)) as (scale,):
                scale.multiply_small(2)
                scale.add(self.j)
                scale.increment()
                self.keep("gamma", Count.product(self.dimensions, scale))
            self.keep("component_bits", Count(p))
            self.component_bits.increment()
            self.component_bits.increment()
            self.keep("record_bits", Count(self.component_bits))
            self.record_bits.multiply_small(2)
            self.keep("source_product", Count.literal(1))
            self.keep("address_bits", Count.literal(0))
            self.sources, self.flags, self.axis_rows = factory(), factory(), factory()
            sources.rewind()
            flags.rewind()
            for index in indices(self.dimensions):
                flag = 1 if compare(index, axes) == 0 else flags.read()
                need(flag in (0, 1), "complete tensor target flags")
                if compare(index, axes) < 0:
                    self.flags.append(flag)
                    flags.step(1)
                with owned(Count.literal(1)) as (one,):
                    with owned(Count(ell) if flag else subtract(ell, one)) as (width,):
                        need(compare(width, inner_bits) > 0, "at least two complete target tiles per axis")
                        with owned(read_fixed(sources, ell)) as (s,):
                            positive(s)
                            need(s.read() == 1, "odd original tensor source axis")
                            with owned(power_two(width), Count(s)) as (t, twice_s):
                                twice_s.multiply_small(2)
                                need(compare(s, t) < 0 and compare(t, twice_s) < 0, "near-one original tensor axis")
                                with owned(subtract(width, inner_bits)) as (coarse_width,):
                                    with owned(power_two(coarse_width)) as (tiles,):
                                        for value in (s, t, width, tiles):
                                            write_count(value, self.axis_rows)
                                write_fixed(s, self.sources, ell)
                                following = Count.product(self.source_product, s)
                                self.source_product.close()
                                self.fields["source_product"] = following
                                self.address_bits.add(width)
                                if production:
                                    self.production_axis(s, t)
            need(sources.read() == flags.read() == BLANK, "complete tensor source words and flags")
            for tape in (self.sources, self.flags, self.axis_rows):
                tape.rewind()
            self.keep("target_product", power_two(self.address_bits))
            self.keep("outer_bits", subtract(self.address_bits, ell))
            with owned(Count.literal(13)) as (margin,):
                with owned(Count(self.outer_bits)) as (minimum,):
                    minimum.add(margin)
                    need(compare(p, minimum) >= 0, "complete chirp p-A margin")
            self.keep("inner_address_bits", Count.product(self.dimensions, inner_bits))
            self.keep("coarse_address_bits", subtract(self.address_bits, self.inner_address_bits))
            self.keep("coarse_product", power_two(self.coarse_address_bits))
            if production:
                self.production_common()
        except BaseException:
            self.close()
            raise
        finally:
            sources.rewind()
            flags.rewind()

    def production_axis(self, s, t):
        with owned(subtract(t, s)) as (gap,):
            with owned(Count.product(self.d, gap)) as (lower,):
                lower.multiply_small(4)
                need(compare(lower, s) > 0, "production tensor strict lower ratio")
            with owned(Count(self.d), Count.literal(1)) as (twice_d, one):
                twice_d.multiply_small(2)
                with owned(subtract(twice_d, one)) as (factor,):
                    with owned(Count.product(factor, gap)) as (upper,):
                        need(compare(upper, s) < 0, "production tensor strict upper ratio")
        with owned(Count(self.target_halo), Count(self.w)) as (required, bands):
            bands.multiply_small(2)
            required.add(bands)
            required.multiply_small(2)
            need(compare(s, required) > 0, "production tensor period exceeds paired halo")

    def production_common(self):
        with owned(Policy(self.p, self.alpha)) as (expected,):
            for name in ("P", "sigma", "radius", "inner_bits", "expansion_capacity", "halo", "w"):
                need(compare(getattr(self, name), getattr(expected, name)) == 0,
                     "exact production tensor Gaussian policy")
        with owned(Count(self.p)) as (eight_p,):
            eight_p.multiply_small(8)
            with owned(ceiling_log(eight_p)) as (minimum,):
                need(compare(self.u, minimum) >= 0, "production tensor logarithmic concentration")
        with owned(Count.product(self.u, self.d), Count(self.w)) as (weighted, separated):
            separated.multiply_small(4)
            separated.increment()
            separated.increment()
            need(compare(weighted, self.p) <= 0 and compare(self.d, separated) > 0,
                 "production tensor similarity and cell separation")
        with owned(Count.product(self.d, self.halo)) as (needed,):
            needed.multiply_small(64)
            need(compare(self.L, needed) >= 0, "production tensor source-padding room")
        # F <= 2^A*(D*p^2+32+2D). This guard bounds the restored
        # approximation error by 1/256 before narrowing to the disk format.
        with owned(Count.product(self.p, self.p)) as (square,):
            with owned(Count.product(self.dimensions, square), Count(self.dimensions), Count.literal(32)) as (bound, twice_d, constant):
                twice_d.multiply_small(2)
                bound.add(twice_d)
                bound.add(constant)
                with owned(ceiling_log(bound), Count(self.gamma), Count.literal(8)) as (logarithm, required, guard):
                    required.add(self.outer_bits)
                    required.add(logarithm)
                    required.add(guard)
                    need(compare(self.p, required) >= 0, "production restored tensor error margin")

    def axis(self, index):
        self.axis_rows.rewind()
        try:
            need(compare(index, self.dimensions) < 0, "existing tensor axis")
            for _ in indices(index):
                with owned(AxisRow(self.axis_rows)):
                    pass
            return AxisRow(self.axis_rows)
        finally:
            self.axis_rows.rewind()

    def close(self):
        for tape in (self.sources, self.flags, self.axis_rows):
            if tape is not None:
                tape.clear()
        self.sources = self.flags = self.axis_rows = None
        super().close()
