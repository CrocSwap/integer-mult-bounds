"""Certified input-independent source tables for the #4100 cached chirp.

The caller supplies the pinned certified-gaussian-recovery intervals module;
this file uses no floating-point trigonometry and inspects no payload.
@CubeJerry, with substantial OpenAI assistance. Apache-2.0.
"""

from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
import json

CANONICAL_BASE = "7c49fe32c55de02c2c873655c804b16e4c3fef0a"
INTERVAL_SOURCE = "research/certified-gaussian-recovery/intervals.py"
INTERVAL_SHA256 = "159d2a7d32a8cc7c8f56632a8ef127308b984a0a6753c9d6bdccacc6e7d6d4df"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value, name, lower=None):
    need(type(value) is int, name + " must be an integer")
    if lower is not None:
        need(value >= lower, name + " is below its permitted range")
    return value


def ceil_log2(value):
    integer(value, "logarithm argument", 1)
    return (value - 1).bit_length()


@dataclass(frozen=True)
class Plan:
    radices: tuple
    slopes: tuple
    normalized_slopes: tuple
    radius: int
    target: int
    incoming_precision: int
    f: int
    W: int
    work_bits: int
    table_component_error: Fraction
    cache_l1_error: Fraction
    payload_l1_error: Fraction

    @property
    def d(self):
        return len(self.radices)

    @property
    def phase_records(self):
        return sum(self.radices)

    @property
    def table_payload_bits(self):
        return 2 * self.W * self.phase_records

    @property
    def shape_symbols(self):
        return sum(t.bit_length() for t in self.radices)


@dataclass(frozen=True)
class Bundle:
    plan: Plan
    tables: tuple
    exact_quarter_entries: int
    interval_entries: int
    maximum_component_enclosure_units: int

    def receipt(self):
        p = self.plan
        numerical = {"radices": p.radices, "slopes": p.slopes,
                     "normalized_slopes": p.normalized_slopes,
                     "radius": p.radius, "target": p.target,
                     "incoming_precision": p.incoming_precision,
                     "f": p.f, "W": p.W, "work_bits": p.work_bits,
                     "tables": self.tables}
        encoded = json.dumps(numerical, separators=(",", ":"), sort_keys=True)
        return {"source_sha": CANONICAL_BASE,
                "interval_path": INTERVAL_SOURCE,
                "interval_sha256": INTERVAL_SHA256,
                "data_sha256": sha256(encoded.encode("ascii")).hexdigest(),
                "radices": list(p.radices), "slopes": list(p.slopes),
                "f": p.f, "W": p.W, "work_bits": p.work_bits,
                "table_component_error": str(p.table_component_error),
                "cache_l1_error": str(p.cache_l1_error),
                "payload_l1_error": str(p.payload_l1_error),
                "exact_quarter_entries": self.exact_quarter_entries,
                "interval_entries": self.interval_entries,
                "maximum_component_enclosure_units": self.maximum_component_enclosure_units,
                "table_payload_bits": p.table_payload_bits,
                "shape_symbols": p.shape_symbols}


def allocation(radices, slopes, radius, target, incoming_precision=0):
    radices, slopes = tuple(radices), tuple(slopes)
    need(radices and len(radices) == len(slopes), "one nonempty slope per axis")
    for t in radices:
        integer(t, "radix", 2)
        need(t & (t - 1) == 0, "dyadic radix")
    for s in slopes:
        integer(s, "slope")
        need(s % 2 == 1, "odd slope")
    need(radices[0] == max(radices), "axis zero must have largest radix")
    integer(radius, "radius", 1)
    integer(target, "target", 0)
    integer(incoming_precision, "incoming precision", 0)
    d = len(radices)
    constant = 2 * (radius * (3*d - 1) + 1)
    f = max(incoming_precision, target + ceil_log2(constant), 2)
    W = max(f + ceil_log2(radius + 1) + 2,
            max(t.bit_length() - 1 for t in radices) + 2,
            ceil_log2(d + 1) + 2)
    h = Fraction(1, 1 << f)
    return Plan(radices, slopes, tuple(s % (2*t) for s, t in zip(slopes, radices)),
                radius, target, incoming_precision, f, W, 2*f + 32,
                2*h, 2*(3*d - 1)*h, constant*h)


def certified_inner_point(box, precision, oracle):
    """Check a conservative two-ulp component certificate for inward output."""
    need(len(box) == 2, "complex enclosure")
    bits = box[0].bits
    need(bits >= precision and box[1].bits == bits, "one sufficiently fine grid")
    step = 1 << (bits - precision)
    need(all(z.hi - z.lo <= step for z in box), "source enclosure too wide")
    point, reported_l1 = oracle.inward_quantize(box, precision)
    errors = tuple(max(abs(c*step - z.lo), abs(c*step - z.hi))
                   for c, z in zip(point, box))
    need(all(e <= 2*step for e in errors), "component certificate exceeds two ulps")
    need(reported_l1 == Fraction(sum(errors), 1 << bits), "inconsistent interval receipt")
    need(oracle.in_disk(point, precision), "source point outside unit disk")
    return point, max(z.hi - z.lo for z in box)


def prepare(radices, slopes, radius, target, *, oracle, incoming_precision=0):
    """Return input-independent, axis-ordered integer phase tables.

    ``oracle`` must be an authenticated instance of the pinned source.
    Use a fresh module namespace, or charge retained prior cache storage.
    Source loading/authentication is offline, never a payload operation.
    """
    p = allocation(radices, slopes, radius, target, incoming_precision)
    scale = 1 << p.f
    quarters = ((scale, 0), (0, scale), (-scale, 0), (0, -scale))
    tables = []
    exact_count = interval_count = max_width = 0
    for t, s in zip(p.radices, p.normalized_slopes):
        modulus = 2*t
        table = []
        for x in range(t):
            phase = (-s*x*x) % modulus
            if (4*phase) % modulus == 0:
                value = quarters[(4*phase) // modulus]
                exact_count += 1
            else:
                box = oracle.root_of_unity(phase, modulus, p.work_bits)
                value, width = certified_inner_point(box, p.f, oracle)
                max_width = max(max_width, width)
                interval_count += 1
            need(all(-(1 << (p.W-1)) <= c < (1 << (p.W-1)) for c in value),
                 "phase carrier overflow")
            table.append(value)
        need(table[0] == (scale, 0), "exact initial chirp phase")
        tables.append(tuple(table))
    need(p.payload_l1_error <= Fraction(1, 1 << p.target), "precision allocation")
    return Bundle(p, tuple(tables), exact_count, interval_count, max_width)
