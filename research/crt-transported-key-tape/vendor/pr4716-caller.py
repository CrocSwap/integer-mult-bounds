"""Current-state CRT controls with modulus-only inverses hoisted explicitly.

FixedCRT(left_moduli, target_modulus, right_prefix=1, inverse=...) prepares m+1 inverses
once, then evaluate(residues) performs no modular inversion. RootCaller binds
that evaluator to one actual balanced-tree root axis, transported through the
three disjoint exchanges of the retained reservoir construction. Callers pass
already authenticated crt, allocator and Word modules; this module loads no
files, prints nothing, and performs no I/O.

The root fixture uses widths (4,4,5,5), moduli (11,13,17,19), target axis 2,
reservoir axis 3, L=18, and H=G=1, K=5. These are proper declared widths for
the prime moduli, but the geometry is below the production size cutoff. The
fixture tests actual CRT control semantics, not the production constants or
a machine-time bound. Optional memoization is by the CURRENT y argument.

Cinna Davis supplies the CRT/network construction; PR4169/4174 supply the
inverse and placement interfaces; PR4377/4409 motivate the query-budget
audit. Hiroki KUMAZAKI (@kumagi), with substantial OpenAI Codex assistance.
Apache-2.0. See README and PROOF for the complete attribution and limits.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from math import prod


def require(condition, message):
    if not condition:
        raise ValueError(message)


def modular_inverse(value, modulus):
    return pow(value, -1, modulus)


@dataclass(frozen=True)
class CRTValue:
    residues: tuple[int, ...]
    valid: bool
    k_A: int
    offset: int


class FixedCRT:
    """Locally scaled CRT reconstruction for fixed pairwise-coprime moduli.

    If P_i is the product of the left moduli preceding i, the current input
    residue is k_A/P_i modulo s_i. Each term therefore uses
    ((residue_i * P_i) mod s_i) * (S/s_i) * (S/s_i)^(-1) mod s_i.
    The target offset is k_A * (S*right_prefix)^(-1) modulo target_modulus.

    setup_inverse_calls, evaluation_calls and reconstruction_calls are host
    operation counters, not bit-step costs. The first counts exactly the
    actual modular-inverse provider calls below. The optional inverse keyword
    accepts a two-argument provider; by default it is pow(value,-1,modulus).
    evaluate invokes no inverse helper. The setup inversions themselves check
    that the required fixed moduli and target prefix are coprime.
    Invalid padded residues disable the node's shift, as in CRT.md section 1.
    """

    def __init__(self, left_moduli, target_modulus, right_prefix=1, *, inverse=None):
        self.left_moduli = tuple(left_moduli)
        require(self.left_moduli and all(type(m) is int and m >= 2 for m in self.left_moduli),
                "nonempty left group of integer moduli at least two")
        require(type(target_modulus) is int and target_modulus >= 2, "positive target modulus")
        require(type(right_prefix) is int and right_prefix >= 1, "positive right-child prefix")
        inverse = modular_inverse if inverse is None else inverse
        require(callable(inverse), "modular inverse implementation must be callable")
        self.target_modulus = target_modulus
        self.right_prefix = right_prefix
        self.product = prod(self.left_moduli)
        self.setup_inverse_calls = 0
        self.evaluation_calls = 0
        self.reconstruction_calls = 0
        self.terms = []
        prefix = 1
        for modulus in self.left_moduli:
            complement = self.product // modulus
            coefficient_inverse = inverse(complement, modulus)
            self.setup_inverse_calls += 1
            require(type(coefficient_inverse) is int
                    and complement * coefficient_inverse % modulus == 1,
                    "left complements must be invertible modulo their own moduli")
            self.terms.append((modulus, prefix, complement, coefficient_inverse))
            prefix *= modulus
        self.terms = tuple(self.terms)
        self.prefixes = tuple(term[1] for term in self.terms)
        self.complements = tuple(term[2] for term in self.terms)
        self.target_inverse = inverse(self.product * right_prefix, target_modulus)
        self.setup_inverse_calls += 1
        require(type(self.target_inverse) is int
                and self.product * right_prefix * self.target_inverse % target_modulus == 1,
                "target prefix must be invertible")

    def evaluate(self, residues):
        """Read current residues and return the node's current valid/offset state."""
        residues = tuple(residues)
        require(len(residues) == len(self.left_moduli)
                and all(type(value) is int and value >= 0 for value in residues),
                "one nonnegative current residue per left modulus")
        self.evaluation_calls += 1
        valid = all(value < modulus for value, modulus in zip(residues, self.left_moduli))
        if not valid:
            return CRTValue(residues, False, 0, 0)
        self.reconstruction_calls += 1
        total = 0
        for value, (modulus, prefix, complement, inverse) in zip(residues, self.terms):
            total += ((value * prefix) % modulus) * complement * inverse
        integer = total % self.product
        return CRTValue(residues, True, integer,
                        integer * self.target_inverse % self.target_modulus)

    def check_reference(self, value, crt):
        """Verification-only comparison with the passed retained decode_group."""
        reference = crt.decode_group(value.residues, self.left_moduli) if value.valid else 0
        require(reference == value.k_A, "fixed-inverse reconstruction differs from source")
        require(value.offset == reference * self.target_inverse % self.target_modulus,
                "fixed-inverse target offset differs from source")
        return True


@dataclass(frozen=True)
class Query:
    """One source-function evaluation at its actual current y state.

    target is the reconstructed target-axis value. bit is the Boolean source
    output. local_bit and target_y_bit identify the physical switch target.
    coordinates contains the current axes 0, 1 and 2; omitted axis 3 is dirty.
    """

    current_y: int
    row: int
    coordinates: tuple[int, int, int]
    residues: tuple[int, int]
    valid: bool
    k_A: int
    offset: int
    target: int
    local_bit: int
    target_y_bit: int
    bit: int

    def record(self):
        return asdict(self)


class RootCaller:
    """Fixed real CRT root-axis fixture, with exact transported coordinates.

    root = RootCaller(crt_module, allocator_module, word_module, inverse=...)
    root.rows                       # local rows having a complete compact guard
    root.word(row)                  # retained Word with the transported target
    root.evaluate(row, current_y)   # Query with complete current-state trace
    root.source(row, trace, cache)  # callable y -> (control_bit,)
    root.stale_offset_source(row,c) # deliberately wrong fixed-offset callback

    source(..., cache=True) memoizes Query values by its current y argument;
    it does not retain the first offset for later, different addresses. Such
    finite memoization is a replay accelerator and is not priced as a runtime
    algorithm. The source's networks are cached by their actual offset.
    """

    widths = (4, 4, 5, 5)
    moduli = (11, 13, 17, 19)
    ell = 5
    target_axis = 2
    reservoir_axis = 3
    H = 1
    G = 1
    K = 5

    def __init__(self, crt, allocator, word_module, *, inverse=None):
        self.crt = crt
        self.Word = word_module.Word
        self.L = sum(self.widths)
        self.Y = self.L - 3 * self.H
        self.placement = allocator.Placement(self.L, self.H, ((2, 3), (3, 4), (4, 5)))
        axes = []
        end = self.L
        for width in self.widths:
            axes.append((end - width, end))
            end -= width
        self.axes = tuple(axes)
        self.descriptors = tuple(self.placement.map_interval(*interval) for interval in self.axes)
        self._read_parts = tuple(tuple((self.L - part.image_interval[1],
                                       part.image_interval[1] - part.image_interval[0])
                                      for part in fragments)
                                 for fragments in self.descriptors[:3])
        self.fixed = FixedCRT(self.moduli[:2], self.moduli[self.target_axis], inverse=inverse)
        self._networks = {}
        self.schedule = tuple(bit for bit, table in self.network(0))
        self.rows = tuple(row for row in range(len(self.schedule))
                          if self.target_y_bit(row) + self.K <= self.Y)

    @property
    def setup_inverse_calls(self):
        return self.fixed.setup_inverse_calls

    @property
    def network_builds(self):
        return len(self._networks)

    def network(self, offset):
        require(type(offset) is int and 0 <= offset < self.moduli[self.target_axis],
                "canonical target offset")
        if offset not in self._networks:
            self._networks[offset] = self.crt.benes(self.crt.rotation(
                1 << self.widths[self.target_axis], self.moduli[self.target_axis], offset))
        return self._networks[offset]

    def target_y_bit(self, row):
        require(type(row) is int and 0 <= row < len(self.schedule), "local network row")
        original = self.axes[self.target_axis][1] - 1 - self.schedule[row]
        physical = self.placement.map_position(original)
        require(2 * self.H <= physical < self.L - self.H, "target must be in the middle field")
        return self.L - self.H - 1 - physical

    def word(self, row):
        require(row in self.rows, "row uses the separate tail branch rather than a complete guard")
        return self.Word(self.G, self.H, self.Y, (self.target_y_bit(row),), self.K)

    def coordinates(self, current_y):
        require(type(current_y) is int and 0 <= current_y < (1 << self.Y),
                "complete current middle field")
        placed = current_y << self.H
        result = []
        for parts in self._read_parts:
            value = 0
            for shift, width in parts:
                value = (value << width) | ((placed >> shift) & ((1 << width) - 1))
            result.append(value)
        return tuple(result)

    def evaluate(self, row, current_y):
        target_y_bit = self.target_y_bit(row)
        coordinates = self.coordinates(current_y)
        value = self.fixed.evaluate(coordinates[:2])
        local_bit, table = self.network(value.offset)[row]
        require(local_bit == self.schedule[row], "common retained Beneš schedule")
        return Query(current_y, row, coordinates, value.residues, value.valid,
                     value.k_A, value.offset, coordinates[2], local_bit,
                     target_y_bit, table[coordinates[2]])

    def source(self, row, trace=None, cache=False):
        """Return the actual source; optionally append every callback's Query record."""
        self.target_y_bit(row)
        values = {} if cache else None

        def callback(current_y):
            if values is None:
                query = self.evaluate(row, current_y)
            else:
                if current_y not in values:
                    values[current_y] = self.evaluate(row, current_y)
                query = values[current_y]
            if trace is not None:
                trace.append(query.record())
            return (query.bit,)

        return callback

    def stale_offset_source(self, row, offset):
        """Negative control: query live target values in one incorrectly frozen network."""
        self.target_y_bit(row)
        table = self.network(offset)[row][1]

        def callback(current_y):
            return (table[self.coordinates(current_y)[2]],)

        return callback
