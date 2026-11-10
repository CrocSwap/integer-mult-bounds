"""Certified source-bound pages for one ordinary Gaussian run.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Offline integer/interval preparation has a separately proved bit tariff.
No full-run similarity weight or Reference entry is produced here.
"""
from dataclasses import dataclass
from fractions import Fraction as F
from hashlib import sha256
import json


def need(ok, why):
    if not ok:
        raise ValueError(why)


def ceildiv(a, b):
    need(type(a) is int and type(b) is int and b > 0, "integer ceiling domain")
    return -(-a // b)


def ceiling(x):
    x = F(x)
    return ceildiv(x.numerator, x.denominator)


def ceil_log2(x):
    need(type(x) is int and x >= 1, "positive integer logarithm")
    return (x - 1).bit_length()


def phase(theta, index):
    x = theta * index + F(1, 2)
    return x.numerator // x.denominator


def pair(x):
    x = F(x)
    return [x.numerator, x.denominator]


@dataclass(frozen=True)
class Plan:
    n: int
    L: int
    W: int
    f: int
    start: int
    source_size: int
    excess: int
    alpha: int
    phase: int
    radius: int
    accuracy_bits: int
    recurrence_bound: int
    stage_radius: int
    gauge_bits: int
    gauge_bound: int
    partial_radius: int
    interval_bits: int
    source_spec: tuple
    ideal_error: F
    reference_norm_error: F
    reference_action_error: F
    reference_gap: F
    ideal_gap: F
    residual_tail: F

    @property
    def theta(self):
        return F(self.excess, self.source_size)

    @property
    def rho(self):
        return 1 + self.theta

    @property
    def coefficient_error(self):
        return F(2, 1 << self.f)

    @property
    def total_error(self):
        return self.ideal_error + self.reference_action_error

    def blocks(self):
        for k in range(0, self.n, self.L):
            b = min(self.L, self.n - k)
            begin = max(0, k - self.L)
            yield k, b, begin, k + b - begin

    def receipt(self):
        result = dict(vars(self))
        for key, value in tuple(result.items()):
            if isinstance(value, F):
                result[key] = pair(value)
        result.update(coefficient_error=pair(self.coefficient_error),
                      total_error=pair(self.total_error),
                      target_start=self.start + self.phase)
        return result


@dataclass(frozen=True)
class Pages:
    plan: Plan
    streams: dict
    preparation: dict

    def receipt(self):
        encoded = json.dumps(self.streams, sort_keys=True, separators=(",", ":"))
        return {"plan": self.plan.receipt(), "preparation": dict(self.preparation),
                "stream_lengths": {k: len(v) for k, v in self.streams.items()},
                "stream_sha256": sha256(encoded.encode("ascii")).hexdigest()}


def make_plan(reference, start, length, radius, accuracy_bits):
    """Admit a fixed pinned Reference once; never change its precision."""
    need(all(type(v) is int for v in (start, length, radius, accuracy_bits)),
         "integer run plan fields")
    spec = reference.spec
    size, excess, alpha = spec.source_size, spec.excess, spec.alpha
    need(0 <= start and length >= 1 and start + length <= size,
         "ordinary nonwrapping source interval")
    need(2 * (length - 1) < size, "ordinary run has unique zero lifts")
    need(radius >= 1 and accuracy_bits >= 0, "positive radius and requested accuracy")
    theta = F(excess, size)
    first_phase = phase(theta, start)
    need(phase(theta, start + length - 1) == first_phase, "one original phase interval")
    reference.require_narrow_gap()
    d_ref = F(reference.narrow_gap)
    e_ref = F(reference.errors["narrow"])
    d_ideal = d_ref + e_ref
    eps = F(1, 1 << (accuracy_bits + 1))
    reference_error = radius * e_ref / (d_ref * d_ideal)
    need(reference_error <= eps, "fixed Reference error exceeds run allocation")
    k_min = ceiling(1 + 1 / (3 * alpha * alpha * theta))
    bound = 1 << ceil_log2(k_min)
    z = 128 * bound * bound * (radius + 1)
    requirement = 672 * bound * bound * z * (1 << (accuracy_bits + 1))
    chosen = max(1, ceildiv(ceil_log2(requirement), 6 * alpha * alpha) - 1)
    block = min(length, chosen)
    tail = F(0) if block >= length - 1 else F(3, 1 << (6 * alpha * alpha * (block + 1)))
    need(tail * z <= eps / (224 * bound * bound), "residual tail allocation")
    h = ceiling(8 * alpha * alpha * theta * block * block)
    gauge = 1 << h
    e0 = max(bound * bound * (z + 3), gauge * ((block + 5) * z + 8), z + 2)
    precision = max(3, ceil_log2(448 * bound * bound * e0 * (1 << (accuracy_bits + 1))))
    need(F(2, 1 << precision) <= eps / (224 * bound * bound * e0),
         "coefficient and completed-round allocation")
    partial = 8 * gauge * bound * (z + 1)
    width = max(precision + ceil_log2(partial + 1) + 2,
                ceil_log2(length + 1) + 2)
    internal = precision + 2 * h + 2 * ceil_log2(length + 1) + 16
    return Plan(length, block, width, precision, start, size, excess, alpha,
                first_phase, radius, accuracy_bits, bound, z, h, gauge, partial,
                internal, (size, excess, alpha, spec.source_halfwidth,
                           spec.target_halfwidth, spec.entry_bits),
                eps, e_ref, reference_error, d_ref, d_ideal, tail)


class Producer:
    """Outward fixed-grid interval calculation; scalar operations are priced."""

    def __init__(self, reference, plan):
        self.reference, self.plan = reference, plan
        self.bits, self.scale = plan.interval_bits, 1 << plan.interval_bits
        self.Interval = reference.exp.oracle.Interval
        self.one = self.Interval(self.scale, self.scale, self.bits)
        self.counts = {"decays": 0, "interval_products": 0, "reciprocals": 0,
                       "quantizations": 0, "maximum_interval_width_units": 0,
                       "maximum_parameter_height": 1}
        self.maximum_exponent = F(0)

    def decay(self, exponent):
        exponent = F(exponent)
        need(exponent >= 0, "nonnegative local decay exponent")
        self.counts["decays"] += 1
        self.maximum_exponent = max(self.maximum_exponent, exponent)
        self.counts["maximum_parameter_height"] = max(
            self.counts["maximum_parameter_height"],
            abs(exponent.numerator).bit_length(), exponent.denominator.bit_length())
        if exponent == 0:
            return self.one
        box = self.reference.exp.decay_box(exponent, 2 * self.bits + 32)
        shift = 1 << (box.bits - self.bits)
        result = self.Interval(box.lo // shift, ceildiv(box.hi, shift), self.bits)
        need(0 <= result.lo <= result.hi <= self.scale, "decay interval range")
        need(result.hi - result.lo <= 3, "decay rescaling width")
        return result

    def multiply(self, first, second):
        self.counts["interval_products"] += 1
        return first * second

    def reciprocal(self, box):
        self.counts["reciprocals"] += 1
        need(box.lo > 0, "positive reciprocal denominator")
        return box.reciprocal()

    def quantize(self, box, negative=False):
        need(box.bits == self.bits and 0 <= box.lo <= box.hi,
             "nonnegative coefficient enclosure")
        unit = 1 << (self.bits - self.plan.f)
        need(box.hi - box.lo <= unit, "coefficient interval below one data unit")
        value = box.lo // unit
        need(box.hi - value * unit <= 2 * unit, "two-unit inward coefficient receipt")
        need(value < 1 << (self.plan.W - 1), "signed coefficient representability")
        self.counts["quantizations"] += 1
        self.counts["maximum_interval_width_units"] = max(
            self.counts["maximum_interval_width_units"], box.hi - box.lo)
        return -value if negative and value else value

    def build(self):
        p = self.plan
        alpha2 = p.alpha * p.alpha
        q = self.decay(alpha2 * p.rho)
        need(q.hi * 2 <= self.scale, "small q source domain")
        q2 = self.multiply(q, q)
        power = self.one
        fboxes = [self.one]
        for index in range(1, p.n):
            power = self.multiply(power, q2)
            need(power.hi - power.lo <= 10 * index, "power interval width")
            following = self.multiply(fboxes[-1], self.one - power)
            need(following.lo * 2 >= self.scale and following.hi <= self.scale,
                 "positive bounded finite F product")
            need(following.hi - following.lo <= 6 * p.n * p.n, "F interval width")
            fboxes.append(following)
        inverses = [self.reciprocal(box) for box in fboxes]
        for box in inverses:
            need(box.hi - box.lo <= 26 * p.n * p.n, "inverse F interval width")
        streams = {
            "Finv": tuple(self.quantize(box) for box in inverses),
            "F": tuple(self.quantize(box) for box in fboxes),
        }
        largest_offset = min(p.L, p.n - 1)
        gauge_boxes = [self.decay(alpha2 * p.theta * index * index)
                       for index in range(largest_offset + 1)]
        for box in gauge_boxes:
            need(2 * p.gauge_bound * box.lo >= self.scale,
                 "local inverse gauge safely above underflow")
        inverse_gauges = tuple(self.quantize(box) for box in gauge_boxes)
        positive_gauges = tuple(self.quantize(self.reciprocal(box)) for box in gauge_boxes)
        need(all(value > 0 for value in (*inverse_gauges, *positive_gauges)),
             "positive serialized local gauges")
        scale_out = 1 << p.f
        for sigma, name in ((1, "minus"), (-1, "plus")):
            def original_index(offset):
                return p.start + (offset if sigma == 1 else p.n - 1 - offset)
            mus = [0]
            for offset in range(1, p.n):
                index = original_index(offset)
                beta = p.theta * index - p.phase
                previous_beta = p.theta * (index - sigma) - p.phase
                exponent = alpha2 * (p.rho - sigma * (beta + previous_beta))
                need(exponent >= alpha2 * p.theta, "stable local recurrence exponent")
                coefficient = self.quantize(self.decay(exponent))
                need(coefficient * p.recurrence_bound <= (p.recurrence_bound - 1) * scale_out,
                     "inward recurrence contraction")
                mus.append(coefficient)
            streams["mu_" + name] = tuple(mus)
            residual = []
            for offset, size, begin, window in p.blocks():
                anchor = original_index(offset)
                beta = p.theta * anchor - p.phase
                for position in range(begin, offset + size):
                    residual.append(inverse_gauges[abs(position - offset)])
                for distance in range(window):
                    if distance > p.L:
                        residual.append(0)
                        continue
                    exponent = alpha2 * (3 * p.rho - 2 * sigma * beta) * distance
                    numerator = self.decay(exponent)
                    box = self.multiply(numerator, inverses[distance])
                    need(box.hi - box.lo <= 34 * p.n * p.n, "residual kernel interval width")
                    residual.append(self.quantize(box, bool(distance % 2)))
                for position in range(size):
                    residual.append(positive_gauges[position])
            streams["residual_" + name] = tuple(residual)
        expected_residual = sum(2 * window + size for _, size, _, window in p.blocks())
        need(all(len(streams[key]) == p.n for key in ("Finv", "F", "mu_minus", "mu_plus")),
             "complete global factor streams")
        need(all(len(streams[key]) == expected_residual
                 for key in ("residual_minus", "residual_plus")), "complete residual stream extents")
        records = sum(map(len, streams.values()))
        need(records <= 14 * p.n, "linear page record count")
        self.counts.update(
            serialized_records=records, serialized_record_bits=records * p.W,
            maximum_decay_exponent=pair(self.maximum_exponent),
            interval_bits=self.bits, decay_working_bits=2 * self.bits + 32,
            scope="Input-independent certified integer/interval macros; not measured tape steps",
        )
        height = max(16, self.bits, alpha2, p.source_spec[-1],
                     self.counts["maximum_parameter_height"], p.source_size.bit_length(),
                     p.radius.bit_length())
        self.counts.update(preparation_parameter=height,
                           preparation_time_bound="O(n B^8)",
                           preparation_space_bound="O(n B+B^2)",
                           reference_entry_queries=0)
        return Pages(p, streams, self.counts)


def prepare(reference, start, length, radius, accuracy_bits):
    """Return six integer-numerator streams and an admitted common plan.

    The physical serializer must use the pinned Signed write_signed ABI;
    its emitted bits are charged in addition to this preparation.
    """
    plan = make_plan(reference, start, length, radius, accuracy_bits)
    return Producer(reference, plan).build()
