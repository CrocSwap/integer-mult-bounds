"""Universal affine certificates for the actual compact-body families.

Nonnegative variables represent arbitrary integer widths, remainders and root
slack. Finite labels are enumerated; numerical widths are not enumerated.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from dataclasses import dataclass
from hashlib import sha256
import json
from margin_sources import need


@dataclass(frozen=True)
class Affine:
    constant: int = 0
    width: int = 0
    remainder: int = 0
    root_slack: int = 0

    def __add__(self, other):
        other = other if isinstance(other, Affine) else Affine(other)
        return Affine(*(a+b for a, b in zip(self.row(), other.row())))

    __radd__ = __add__

    def __neg__(self):
        return Affine(*(-a for a in self.row()))

    def __sub__(self, other):
        return self + (-other if isinstance(other, Affine) else -int(other))

    def __rsub__(self, other):
        return -self + other

    def __mul__(self, scalar):
        need(type(scalar) is int, 'integer affine scalar')
        return Affine(*(scalar*a for a in self.row()))

    __rmul__ = __mul__

    def row(self):
        return (self.constant, self.width, self.remainder, self.root_slack)


class Certificates:
    def __init__(self):
        self.count = 0
        self.digest = sha256()

    def nonnegative(self, value, label):
        need(isinstance(value, Affine), 'affine proposition')
        need(all(type(x) is int and x >= 0 for x in value.row()),
             'universal nonnegative coefficient certificate: ' + label)
        self.count += 1
        self.digest.update(json.dumps([label, value.row()], separators=(',', ':')).encode())
        self.digest.update(b'\n')

    def equal(self, left, right, label):
        need(left.row() == right.row(), 'universal affine identity: ' + label)
        self.nonnegative(left-right, label)

    def interval(self, value, upper, label):
        self.nonnegative(value, label + ':lower')
        self.nonnegative(upper-value, label + ':upper')


def certify(*, gap_multiple=2, good_tail_shift=0, depth_increment=1):
    need(all(type(x) is int for x in (gap_multiple, good_tail_shift, depth_increment)),
         'integer structural parameters')
    cert = Certificates()
    delta, slack = Affine(remainder=1), Affine(root_slack=1)
    family_counts = {'good': 0, 'pair': 0, 'orientation': 0, 'point': 0}

    def chunks(f, first, second, width, first_bank, second_bank, label):
        n = 64*f + delta
        n0 = n + slack
        total, core = 2*n, 64*f
        for value, name in ((first, 'first'), (second, 'second'), (width-1, 'positive_width')):
            cert.nonnegative(value, label + ':' + name)
        cert.nonnegative(second-first-width, label + ':disjoint')
        cert.nonnegative(n-width-1, label + ':proper_child')
        cert.nonnegative(n0-depth_increment, label + ':root_depth_extension')
        cert.nonnegative(n-depth_increment, label + ':max_history_extension')
        cert.nonnegative(n-width-depth_increment, label + ':descendant_history')
        starts = []
        for start, bank, side in ((first, first_bank, 'left'), (second, second_bank, 'right')):
            cert.nonnegative(start-bank*core, label + ':' + side + ':bank_start')
            cert.nonnegative((bank+1)*core-start-width, label + ':' + side + ':bank_end')
            physical = start + bank*gap_multiple*delta
            last, end = physical + width-1, physical + width
            for value, name in ((physical, 'physical'), (last, 'last'), (end, 'end')):
                cert.interval(value, total, label + ':' + side + ':' + name)
            cert.equal((start+width-1)+bank*gap_multiple*delta, last,
                       label + ':' + side + ':last_mapping')
            starts.append(physical)
        a, b = starts
        cert.interval(b-a-width, total, label + ':between')
        cert.interval(total-b-width, total, label + ':after')
        cert.interval(total-a-1, total, label + ':primitive_after')
        cert.interval(b-a-1, total, label + ':primitive_middle')
        cert.interval(2*n, 2*n0, label + ':root_word_bound')

    f = Affine(constant=1, width=1)
    n = 64*f + delta
    for rank in range(1, 43):
        chunks(f, Affine(), (128-rank+good_tail_shift)*f, rank*f, 0, 1,
               'good:' + str(rank))
        family_counts['good'] += 1
    for i in range(128):
        for k in range(i+1, 128):
            chunks(f, i*f, k*f, f, i//64, k//64, 'pair:' + str(i) + ':' + str(k))
            family_counts['pair'] += 1
    u = Affine(constant=1, width=1)
    for epsilon in (0, 1):
        half_f = 2*u+epsilon
        for k in range(128):
            chunks(half_f, k*half_f, (k+1)*half_f-u, u, k//64, k//64,
                   'orientation:' + str(epsilon) + ':' + str(k))
            family_counts['orientation'] += 1
    for row in range(128):
        for j in (Affine(), f-1):
            point = row*f + (j if row<64 else f-1-j)
            cert.interval(point, 128*f-1, 'point:' + str(row) + ':' + str(j.row()))
            family_counts['point'] += 1
    for x in (64*f, n-1):
        cert.interval(x, 2*n, 'peel_coordinate:' + str(x.row()))
        cert.interval(2*n-1-x, 2*n, 'peel_opposite:' + str(x.row()))
    cert.interval(n, 2*n, 'peel_terminal_increment')
    cert.interval(f, n, 'column_terminal_increment')
    cert.nonnegative(n-(depth_increment+1), 'leaf_after_record')
    return dict(method='nonnegative integer affine coefficients; finite source labels only',
                certificates=cert.count, digest=cert.digest.hexdigest(), families=family_counts,
                arbitrary_parameters=['f>=1', 'delta>=0', 'n0-n>=0',
                                      'half_u>=1 and epsilon in {0,1}'],
                physical_remainder_domain='0<=delta<64 retained; geometric bounds are stronger')


def controls():
    failures = []
    for label, arguments in (
        ('extra_gap_copy', {'gap_multiple': 3}),
        ('good_child_past_core', {'good_tail_shift': 1}),
        ('depth_increment_65', {'depth_increment': 65}),
        ('boolean_structural_multiplier', {'gap_multiple': True}),
    ):
        try:
            certify(**arguments)
        except ValueError:
            failures.append(label)
        else:
            raise ValueError('invalid universal certificate accepted: ' + label)
    return failures
