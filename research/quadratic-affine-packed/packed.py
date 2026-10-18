"""Exact column-parallel Gaussian orthogonality rows, using Python integers.

Copyright 2026 Curtis Dransfield. Apache-2.0.
Prepared with substantial OpenAI Codex assistance. rank_witness preserves
Douglas Colkitt's original validation, elimination and receipt fields.
"""
from fractions import Fraction
from hashlib import sha256


def require(condition, message):
    if not condition:
        raise ValueError(message)


class PackedRows:
    """Immutable snapshot of a nonempty sequence of D-coordinate phase vectors.

    Coordinates are 0, 1, i, -1, -i; masks encode (support, low, high).
    One byte per column is sufficient for D <= 32. See README for the
    signed-lane and zero-byte proofs. This class does not assert rank.
    """

    def __init__(self, vectors, dimension):
        require(type(dimension) is int and 1 <= dimension <= 32,
                'Packed dimension must be in 1..32')
        self.dimension = dimension
        self.vectors = tuple(tuple(v) for v in vectors)
        require(bool(self.vectors), 'Empty packed sample')
        for v in self.vectors:
            self._validate(v)
        self.count = len(self.vectors)
        unit = int.from_bytes(b'\x01' * self.count, 'little')
        self.offset = dimension * unit
        self.low = 127 * unit
        self.high = 128 * unit
        self.real = []
        self.imag = []
        for k in range(dimension):
            real_pos, real_neg, imag_pos, imag_neg = (bytearray(self.count) for _ in range(4))
            for j, (support, lo, hi) in enumerate(self.vectors):
                if support >> k & 1:
                    phase = ((lo >> k) & 1) + 2 * ((hi >> k) & 1)
                    (real_pos, imag_pos, real_neg, imag_neg)[phase][j] = 1
            self.real.append(int.from_bytes(real_pos, 'little') - int.from_bytes(real_neg, 'little'))
            self.imag.append(int.from_bytes(imag_pos, 'little') - int.from_bytes(imag_neg, 'little'))
        # At step k, collect two k-bit blocks spaced 8*k bits apart.
        self.compaction = []
        k = 1
        while k < self.count:
            groups = (self.count + 2*k - 1) // (2*k)
            stride = 16*k
            repetitions = ((1 << (stride*groups)) - 1) // ((1 << stride) - 1)
            self.compaction.append((7*k, ((1 << (2*k)) - 1) * repetitions))
            k *= 2
        self.row_mask = (1 << self.count) - 1

    def _validate(self, v):
        require(len(v) == 3 and all(type(x) is int and x >= 0 for x in v),
                'Invalid phase masks')
        support, lo, hi = v
        require(support < 1 << self.dimension and not ((lo | hi) & ~support),
                'Phase masks leave support or dimension')

    def products(self, v):
        """Return offset packed real/imaginary parts of conj(v) dot each column."""
        self._validate(v)
        support, lo, hi = v
        real = imag = self.offset
        while support:
            bit = support & -support
            support ^= bit
            k = bit.bit_length() - 1
            phase = ((lo >> k) & 1) + 2 * ((hi >> k) & 1)
            r, i = self.real[k], self.imag[k]
            if phase == 0:
                real += r
                imag += i
            elif phase == 1:
                real += i
                imag -= r
            elif phase == 2:
                real -= r
                imag -= i
            else:
                real -= i
                imag += r
        return real, imag

    def zero_lanes(self, real, imag):
        """Decode products() output; each offset digit must be in [0, 2D]."""
        different = (real ^ self.offset) | (imag ^ self.offset)
        nonzero = (different + self.low) & self.high
        bits = (self.high ^ nonzero) >> 7
        for shift, mask in self.compaction:
            bits = (bits | (bits >> shift)) & mask
        return bits & self.row_mask

    def orthogonality_row(self, v):
        return self.zero_lanes(*self.products(v))

    def central_row(self, index):
        require(type(index) is int and 0 <= index < self.count, 'Invalid packed row index')
        return self.orthogonality_row(self.vectors[index]) | (1 << index)


def rank_witness(original, t, complex_phases, parity, sample, independent_rows,
                 *, compare_rows=False):
    """Original finite rank obligation with only row construction replaced."""
    f = original.family(t, complex_phases, parity)
    require(sample and len(set(sample)) == len(sample) and
            all(type(i) is int and 0 <= i < f['n'] for i in sample),
            'Sample must contain distinct valid labels')
    require(independent_rows and len(set(independent_rows)) == len(independent_rows) and
            all(type(i) is int and 0 <= i < len(sample) for i in independent_rows),
            'Invalid independent row indices')
    rows = PackedRows([original.vector(f, i) for i in sample], f['D'])
    basis = {}
    digest = sha256()
    bytewidth = (len(sample) + 7) // 8
    for i in independent_rows:
        row = rows.central_row(i)
        if compare_rows:
            expected = sum(1 << j for j, v in enumerate(rows.vectors)
                           if i == j or original.inner(rows.vectors[i], v) == (0, 0))
            require(row == expected, 'Packed row differs from original exact row')
        digest.update(row.to_bytes(bytewidth, 'little'))
        x = row
        while x:
            p = x.bit_length() - 1
            if p not in basis:
                basis[p] = x
                break
            x ^= basis[p]
        require(x != 0, 'Claimed rows are linearly dependent')
    r, ell, d, n = len(basis), f['ell'], f['d'], f['n']
    return dict(t=t, complex_phases=complex_phases, parity=parity, n=n, d=d, ell=ell,
                normalized_dimension=Fraction(d, ell), counts_by_support_dimension=f['counts'],
                minor_columns=len(sample), binary_rank_lower=r, independent_row_sha256=digest.hexdigest(),
                positive_deficit_excluded=n*ell <= 6*r*d,
                scope='Only I plus the full orthogonality relation on this exact vector family; no rank upper bound asserted')
