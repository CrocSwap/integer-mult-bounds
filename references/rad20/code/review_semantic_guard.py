#!/usr/bin/env python3
"""Independent fixed-fine-grid controls for an exact semantic child guard.

No Fraction arithmetic, producer imports, value compaction or inner
truncation is used by the executed recursive operator. A deliberately
cancellation-heavy toy recursion has the same exact C^e child boundary;
it is not a replay of the large finite phase network.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from itertools import product
import json
from pathlib import Path
import random
import resource
import subprocess
import time


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def neg(a):
    return -a[0], -a[1]


def sub(a, b):
    return add(a, neg(b))


def mul(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def unit(a, power):
    power %= 4
    return (a, (-a[1], a[0]), neg(a), (a[1], -a[0]))[power]


def gaussian_power(a, n):
    out = (1, 0)
    for _ in range(n):
        out = mul(out, a)
    return out


def v2(x):
    if not x:
        return None
    x = abs(x)
    return (x & -x).bit_length()-1


class FixedGrid:
    def __init__(self, width, incoming_depth, incoming_magnitude):
        self.width = width
        self.depth = incoming_depth
        self.magnitude = incoming_magnitude
        self.halvings = self.visited = 0
        self.maximum_grid = self.maximum_l1_bits = 0
        self.completed = self.inverse_calls = 0
        self.transient_examples = []

    def observe(self, values):
        for a in values:
            self.visited += 1
            for x in a:
                valuation = v2(x)
                if valuation is not None:
                    self.maximum_grid = max(self.maximum_grid, self.width-valuation)
            self.maximum_l1_bits = max(self.maximum_l1_bits,
                                       (abs(a[0])+abs(a[1])).bit_length())

    def halve(self, a):
        require(a[0] % 2 == a[1] % 2 == 0,
                'Fixed-grid halving would discard a nonzero bit')
        self.halvings += 1
        out = (a[0]//2, a[1]//2)
        self.observe((out,))
        return out

    def pair(self, u, v):
        common = add(u, v)
        difference = unit(sub(u, v), 1)
        first, second = add(common, difference), sub(common, difference)
        self.observe((common, difference, first, second))
        return self.halve(first), self.halve(second)

    def leaf(self, values, selected):
        values = list(values)
        for bit in selected:
            mask = 1 << bit
            for j in range(len(values)):
                if j & mask:
                    continue
                values[j], values[j | mask] = self.pair(values[j], values[j | mask])
        return values

    def completed_bound(self, values, original, f):
        minimum = min((v2(x) for a in original for x in a if x), default=self.width)
        require(all(not x or v2(x) >= minimum-f for a in values for x in a),
                'Completed child fails its coarser-grid bound')
        old_norm = max((abs(a[0])+abs(a[1]) for a in original), default=0)
        require(max((abs(a[0])+abs(a[1]) for a in values), default=0)
                <= (1 << f)*old_norm, 'Completed child row norm bound failed')
        self.completed += 1

    def recursive(self, values, selected, inverse=False):
        selected = tuple(selected)
        original = list(values)
        f = len(selected)
        if inverse:
            self.inverse_calls += 1
            # Exactly (-i)^f Z^f C^f Z^f, not separately rounded kernels.
            values = [neg(a) if sum((j >> b) & 1 for b in selected) % 2 else a
                      for j, a in enumerate(values)]
            values = self.recursive(values, selected)
            values = [unit(neg(a) if sum((j >> b) & 1 for b in selected) % 2 else a, -f)
                      for j, a in enumerate(values)]
            self.observe(values)
            self.completed_bound(values, original, f)
            return values
        if f <= 1:
            values = self.leaf(values, selected)
        else:
            require(f % 2 == 0, 'Toy recursion requires a power-of-two axis group')
            slots = selected[:f//2], selected[f//2:]
            # Six exact scalar operations produce an actual fine-grid
            # excursion whose completed effect is the identity.
            values = list(values)
            for _ in range(3):
                values = [self.halve(a) for a in values]
            for _ in range(3):
                values = [add(a, a) for a in values]
                self.observe(values)
            # Four cancellation-heavy recursive calls, followed by the
            # two required slots. s=6; all calls use arbitrary current input.
            for _ in range(2):
                before = list(values)
                values = self.recursive(values, slots[0])
                values = self.recursive(values, slots[0], inverse=True)
                require(values == before, 'Completed forward/inverse cancellation failed')
            for slot in slots:
                values = self.recursive(values, slot)
        self.observe(values)
        self.completed_bound(values, original, f)
        return values


def closed_tensor(values, selected, inverse=False):
    """Independent integer numerator of the closed tensor coefficient map."""
    selected = tuple(selected)
    out = []
    f = len(selected)
    denominator = 1 << f
    mask = sum(1 << b for b in selected)
    for row in range(len(values)):
        total = (0, 0)
        for column, value in enumerate(values):
            if (row ^ column) & ~mask:
                continue
            distance = ((row ^ column) & mask).bit_count()
            same, different = ((1, -1), (1, 1)) if inverse else ((1, 1), (1, -1))
            coefficient = mul(gaussian_power(same, f-distance),
                              gaussian_power(different, distance))
            total = add(total, mul(coefficient, value))
        require(total[0] % denominator == total[1] % denominator == 0,
                'Closed tensor does not fit fixed fine grid')
        out.append((total[0]//denominator, total[1]//denominator))
    return out


def controls():
    rng = random.Random(503)
    basis = arbitrary = entries = divisions = visited = 0
    examples = []
    for f in (1, 2, 4, 8):
        # B=6+20 and 2B*f is a deliberately loose semantic guard.
        common_width = 13+3+52*f
        n = 1 << f
        probes = []
        if f <= 4:
            for column in range(n):
                probes.append((0, [(int(j == column), 0) for j in range(n)], 'basis'))
        for grid_depth in (0, 3, 13):
            probes.append((grid_depth,
                           [(rng.randrange(-8, 9), rng.randrange(-8, 9)) for _ in range(n)],
                           'arbitrary'))
        for depth, integers, kind in probes:
            incoming = [(a << (common_width-depth), b << (common_width-depth))
                        for a, b in integers]
            for inverse in (False, True):
                machine = FixedGrid(common_width, depth, 5)
                machine.observe(incoming)
                result = machine.recursive(incoming, range(f), inverse=inverse)
                reference = closed_tensor(incoming, range(f), inverse=inverse)
                require(result == reference, 'Recursive fixed-grid C differs from closed tensor')
                require(machine.maximum_grid <= depth+52*f,
                        'Observed temporary grid exceeds semantic linear guard')
                require(machine.maximum_l1_bits <= common_width+5+52*f+1,
                        'Observed temporary magnitude exceeds semantic guard')
                restored = machine.recursive(result, range(f), inverse=not inverse)
                require(restored == incoming, 'Fixed-grid recursive inverse failed')
                entries += n
                divisions += machine.halvings
                visited += machine.visited
                basis += kind == 'basis'
                arbitrary += kind == 'arbitrary'
                if kind == 'arbitrary' and depth == 13:
                    completed_depth = max((common_width-v2(x) for a in result for x in a if x), default=0)
                    examples.append(dict(axes=f, inverse=inverse,
                        stored_fractional_bits=common_width, incoming_grid=depth,
                        maximum_observed_grid=machine.maximum_grid,
                        completed_grid=completed_depth,
                        completed_grid_upper=depth+f,
                        completed_child_checks=machine.completed,
                        internal_inverse_calls=machine.inverse_calls))
    # Deliberately lossy child boundary. At p=5 this maps the nonzero
    # exact C impulse to zero if both halves are rounded to the p grid.
    p = 5
    correct = ((1, 1), (1, -1))  # Numerators on grid 2^-(p+1).
    def truncate(x):
        return (-1 if x < 0 else 1)*(abs(x)//2)*2
    truncated = tuple((truncate(a), truncate(b)) for a, b in correct)
    require(truncated != correct, 'Negative eager truncation control did not discriminate')
    return dict(forward_inverse_basis_probes=basis, arbitrary_grid_probes=arbitrary,
                exact_output_values=entries, exact_fixed_grid_halvings=divisions,
                intermediate_integer_components_observed=2*visited,
                transient_examples=examples,
                negative_eager_child_truncation=dict(p=p,
                    exact_grid='2^-(p+1)', exact_numerators=correct,
                    truncated_numerators=truncated, rejected=True))


def recurrences():
    cases = 0
    samples = []
    for m, s, E, threshold in product((3, 5, 11), (7, 32, 1007), (16, 4096), (1, 7, 119)):
        B = s+E
        C0 = 32*m*B*B
        for exponent in range(11):
            e = m**exponent
            size = e
            scalar = completed = levels = 0
            while size >= m and size >= threshold:
                completed += s*(size//m)
                scalar += E
                levels += 1
                size //= m
            bound = 8*size+completed+scalar
            require(bound*(m-1) <= (8*(m-1)+s+E*(m-1))*e,
                    'Geometric semantic recurrence failed')
            require(bound <= 2*B*e, 'Internal semantic bound exceeds 2Be')
            require(bound+18*e < C0*e, 'Whole layer semantic guard constant failed')
            cases += 1
            if exponent == 10 and len(samples) < 6:
                samples.append(dict(m=m,s=s,E=E,axes=e,threshold=threshold,
                    internal_levels=levels,exact_unroll=bound,linear_upper=2*B*e,C0=C0))
    return dict(stopped_cases=cases, samples=samples)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), 'Use a fresh output path')
    start = time.monotonic()
    revision = subprocess.run(['git','-C',str(args.reference),'rev-parse','HEAD'],
                              capture_output=True,text=True,check=True).stdout.strip()
    require(revision == 'bcd4ebde8692383539f8a48734e5fbf3a18a32c2', 'Original input revision differs')
    sections = {name: hashlib.sha256((args.reference/'upstream/build/sections'/name).read_bytes()).hexdigest()
                for name in ('03-motifs.tex','05-layers.tex')}
    result = dict(status='PASS independent exact fixed-fine-grid semantic controls',
        generated_at=datetime.now(timezone.utc).isoformat(),seed=503,
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        original_revision=revision,original_section_sha256=sections,
        controls=controls(),recurrences=recurrences(),
        scope=['No Fraction simplification or inner truncation in executed operator',
               'Toy cancellation-heavy six-child recursion, not large finite phase-network replay',
               'All-size transfer uses retained exact arbitrary-input child interface'],
        seconds=time.monotonic()-start,
        peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS',result['controls']['exact_fixed_grid_halvings'],'exact fine-grid halvings;',
          result['recurrences']['stopped_cases'],'stopped cases',flush=True)


if __name__ == '__main__':
    main()
