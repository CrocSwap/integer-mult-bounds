"""Exact ambient-cap chronological compiler metadata; Apache-2.0.

Prepared for CubeJerry with substantial OpenAI assistance. Adapted from
PR #7345 at 022461f115369efd988ef8c459907f5544bb8bb3; see NOTICE.md. This reference
evaluates integers, not native programs. PROOF.md prices indexed arithmetic
and a separately described sequential implementation.
"""
from dataclasses import dataclass
from math import comb, gcd


class BudgetError(ValueError):
    """The bounded executable refuses an unevaluated larger instance."""


@dataclass(frozen=True)
class Limits:
    max_rank: int = 4096
    max_records: int = 200000
    max_bits: int = 16384

    def __post_init__(self):
        if any(type(x) is not int or x < 1 for x in
               (self.max_rank, self.max_records, self.max_bits)):
            raise ValueError("positive integer capacities required")

    def integer(self, value):
        if abs(value).bit_length() > self.max_bits:
            raise BudgetError("integer bit capacity")
        return value

    def records(self, count):
        if count > self.max_records:
            raise BudgetError("local record capacity")


@dataclass(frozen=True)
class Rule:
    ambient: int
    targets: tuple
    paid: tuple

    def __post_init__(self):
        for alphabet in (self.targets, self.paid):
            if type(alphabet) is not tuple or not alphabet:
                raise ValueError("nonempty tuple histograms required")
            previous = 0
            for entry in alphabet:
                if type(entry) is not tuple or len(entry) != 2:
                    raise ValueError("rank/count pairs required")
                rank, count = entry
                if (type(rank) is not int or type(count) is not int or
                        rank <= previous or count < 1):
                    raise ValueError("sorted distinct positive ranks/counts required")
                previous = rank
        if self.targets[0][0] < 2 or self.paid[-1][0] >= self.targets[0][0]:
            raise ValueError("strict separation required")
        if type(self.ambient) is not int or self.ambient < self.m:
            raise ValueError("integer ambient at least maximum target required")

    @property
    def m(self):
        return self.targets[-1][0]

    @property
    def kmin(self):
        return self.targets[0][0]

    @property
    def bits(self):
        def gamma_length(v):
            return 2 * v.bit_length() - 1
        total = gamma_length(self.ambient)
        for alphabet in (self.targets, self.paid):
            total += gamma_length(len(alphabet))
            total += sum(gamma_length(x) for row in alphabet for x in row)
        return total


@dataclass(frozen=True)
class Row:
    replication: int
    width: int
    leaves: int
    units: int


@dataclass(frozen=True)
class Census:
    rank: int
    height: int
    units: int
    sources: tuple
    exits: tuple


@dataclass
class Work:
    product_records: int = 0
    candidate_pairs: int = 0
    source_contributions: int = 0
    complement_constraints: int = 0
    exit_constraints: int = 0
    completed_rows: int = 0


@dataclass(frozen=True)
class Library:
    rule: Rule
    rows: tuple
    work: Work


def height(rule, rank):
    if rank < rule.ambient:
        raise ValueError("height requires a nonbase rank")
    threshold = rule.ambient
    result = 0
    while threshold * rule.kmin <= rank:
        threshold *= rule.kmin
        result += 1
    return result


def merge_records(records, limits):
    """Deterministic sort/add; input length and temporary integers charged."""
    limits.records(len(records))
    records.sort(key=lambda item: item[0])
    result = []
    key, value = None, 0
    for next_key, next_value in records:
        if key is not None and next_key != key:
            if value < 0:
                raise ValueError("negative aggregate")
            if value:
                result.append((key, value))
            value = 0
        key = next_key
        value = limits.integer(value + next_value)
    if key is not None:
        if value < 0:
            raise ValueError("negative aggregate")
        if value:
            result.append((key, value))
    return tuple(result)


def product_tables(alphabet, degree, limits, work):
    tables = [((1, 1),)]
    for _ in range(degree):
        limits.records(len(tables[-1]) * len(alphabet))
        candidates = []
        for product, count in tables[-1]:
            for rank, multiplicity in alphabet:
                candidates.append((limits.integer(product * rank),
                                   limits.integer(count * multiplicity)))
        work.product_records += len(candidates)
        tables.append(merge_records(candidates, limits))
    return tuple(tables)


def census(rule, rank, targets, paid, limits, work):
    gmax = height(rule, rank)
    d, q = len(rule.targets), len(rule.paid)
    bound = (d + q) * comb(gmax + d + q - 1, d + q - 1)
    limits.records(bound)
    contributions = []
    units = 0
    for depth in range(gmax + 1):
        for rho, paths in paid[depth]:
            for column, words in targets[gmax - depth]:
                work.candidate_pairs += 1
                size = limits.integer(rho * column)
                if limits.integer(rule.ambient * size) > rank:
                    continue
                copies = limits.integer(paths * words)
                units = limits.integer(units + copies)
                for k, multiplicity in rule.targets:
                    contributions.append((limits.integer(size * k),
                                          limits.integer(copies * multiplicity)))
                if depth < gmax:
                    for r, multiplicity in rule.paid:
                        contributions.append((limits.integer(size * r),
                                              -limits.integer(copies * multiplicity)))
    work.source_contributions += len(contributions)
    sources = merge_records(contributions, limits)
    if not sources or any(not rank < rule.ambient * s <= rule.m * rank
                          for s, _ in sources):
        raise ValueError("source band failure")
    exits = paid[gmax + 1]
    if any(not 0 < e * rule.ambient <= (rule.ambient - 1) * rank for e, _ in exits):
        raise ValueError("exit contraction failure")
    return Census(rank, gmax, units, sources, exits)


def child(rows, parent, rank):
    if not 1 <= rank < parent or rank >= len(rows) or rows[rank] is None:
        raise ValueError("positive previously completed child required")
    return rows[rank]


def replication(flow, rows, limits, work):
    result = 1
    for source, count in flow.sources:
        if source == flow.rank:
            continue
        width = child(rows, flow.rank, flow.rank - source).width
        factor = width // gcd(width, count)
        result = limits.integer((result // gcd(result, factor)) * factor)
        work.complement_constraints += 1
    for exit_rank, multiplicity in flow.exits:
        factor = child(rows, flow.rank, exit_rank).width
        result = limits.integer((result // gcd(result, factor)) * factor)
        work.exit_constraints += 1
    return result


def whole_copies(arrays, width):
    copies, remainder = divmod(arrays, width)
    if remainder:
        raise ValueError("nonintegral chronological child batch")
    return copies


def finish_row(flow, rows, scale, limits):
    width = limits.integer(scale * sum(count for _, count in flow.sources))
    leaves = 0
    units = limits.integer(scale * flow.units)
    for source, count in flow.sources:
        if source == flow.rank:
            continue
        old = child(rows, flow.rank, flow.rank - source)
        copies = whole_copies(limits.integer(scale * count), old.width)
        leaves = limits.integer(leaves + limits.integer(copies * old.leaves))
        units = limits.integer(units + limits.integer(copies * old.units))
    for exit_rank, multiplicity in flow.exits:
        old = child(rows, flow.rank, exit_rank)
        per_cut = whole_copies(scale, old.width)
        copies = limits.integer(multiplicity * per_cut)
        leaves = limits.integer(leaves + limits.integer(copies * old.leaves))
        units = limits.integer(units + limits.integer(copies * old.units))
    return Row(scale, width, leaves, units)


def compile_library(rule, maximum, limits=Limits()):
    if type(maximum) is not int or maximum < 1:
        raise ValueError("positive maximum rank required")
    if maximum > limits.max_rank:
        raise BudgetError("maximum rank capacity")
    limits.integer(rule.ambient)
    limits.records(len(rule.targets) + len(rule.paid))
    for alphabet in (rule.targets, rule.paid):
        for record in alphabet:
            for value in record:
                limits.integer(value)
    work = Work()
    rows = [None]  # no B_0 program is constructed or queried
    if maximum >= rule.ambient:
        gmax = height(rule, maximum)
        mt = comb(gmax + len(rule.targets), len(rule.targets))
        mr = comb(gmax + len(rule.paid) + 1, len(rule.paid))
        limits.records(mt + mr)
        targets = product_tables(rule.targets, gmax, limits, work)
        paid = product_tables(rule.paid, gmax + 1, limits, work)
    for rank in range(1, maximum + 1):
        if rank < rule.ambient:
            row = Row(1, 1, rank, 0)
        else:
            flow = census(rule, rank, targets, paid, limits, work)
            scale = replication(flow, rows, limits, work)
            row = finish_row(flow, rows, scale, limits)
        rows.append(row)
        work.completed_rows += 1
    return Library(rule, tuple(rows), work)


def envelope(rule, maximum):
    """Evaluated integer bounds; never exponentiate by a width-bit bound."""
    if type(maximum) is not int or maximum < rule.ambient:
        raise ValueError("nonbase maximum required for this envelope")
    d, q = len(rule.targets), len(rule.paid)
    w = sum(count for _, count in rule.targets)
    p = sum(count for _, count in rule.paid)
    g = height(rule, maximum)
    length = maximum.bit_length()
    cap_length = (maximum // rule.ambient).bit_length()
    ubar = (g + 1) * max(w, p) ** g
    sbar = w * ubar
    factor = 1 + (w + 1) * ubar + p ** (g + 1)
    depth = rule.ambient * cap_length
    generators = sorted(set(k for alphabet in (rule.targets, rule.paid)
                            for k, _ in alphabet if k >= 2))
    visits = rule.ambient * (rule.kmin - 1).bit_length()
    beta = visits * (cap_length + 1) ** len(generators) * sbar.bit_length()
    mt, mr = comb(g + d, d), comb(g + q + 1, q)
    pairs = comb(g + d + q - 1, d + q - 1)
    exits = comb(g + q, q - 1)
    operations = ((rule.bits + length + 1) ** 2 + d * mt + q * mr +
                  (maximum + 1) * ((d + q + 2) * pairs + exits + g + 3))
    combined = beta + rule.ambient.bit_length() + depth * factor.bit_length() + 1
    bit_cap = 8 * (rule.bits + length +
                   (g + 2) * (rule.ambient + w + p + 2).bit_length() +
                   beta + rule.ambient.bit_length() + depth * factor.bit_length() +
                   operations.bit_length() + 2)
    local_records = mt + mr + (d + q + 2) * pairs + exits + g + rule.bits + length + 3
    return {"height": g, "cap_bits": cap_length, "target_records": mt,
            "paid_records": mr, "pairs": pairs, "exit_records": exits,
            "plateau_visit_bound": visits, "plateau_count_bound": (cap_length + 1) ** len(generators),
            "width_log_bound": beta, "combined_output_bits": combined,
            "unit_bound": ubar, "source_bound": sbar, "F": factor, "D": depth,
            "K": operations, "Z": bit_cap, "J": local_records,
            "L_local": local_records * bit_cap}
