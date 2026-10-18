"""Narrow reversible triangular shears. Ross Richardson / OpenAI Codex.

Apache-2.0. These are modular-add gates, not admitted recursive children.
The finite reference accepts d<=256 and power-of-two q<=256.
"""

from collections import Counter


def need(condition, message):
    if not condition:
        raise ValueError(message)


class Reducer:
    def __init__(self, rows, modulus):
        need(type(modulus) is int and 1 <= modulus <= 256, "modulus range")
        need(modulus & (modulus - 1) == 0, "power-of-two modulus")
        self.q = modulus
        self.g = modulus.bit_length() - 1
        self.d = len(rows)
        need(1 <= self.d <= 256, "dimension range")
        need(all(len(row) == self.d for row in rows), "square basis")
        need(all(type(x) is int for row in rows for x in row), "integer basis")
        self.h = [rows[i][i] for i in range(self.d)]
        need(all(h > 0 and modulus % h == 0 for h in self.h), "diagonal divides q")
        need(all(rows[i][j] == 0 for i in range(self.d) for j in range(i)),
             "upper triangular")
        need(all(0 <= rows[i][j] < self.h[i]
                 for i in range(self.d) for j in range(i + 1, self.d)),
             "reduced HNF rows")
        self.e = [h.bit_length() - 1 for h in self.h]
        self.columns = [tuple((i, rows[i][j]) for i in range(j + 1)
                              if rows[i][j]) for j in range(self.d)]
        self.ops = tuple((j, i, shift, self.e[j])
                         for j in reversed(range(self.d)) if self.h[j] < modulus
                         for i, coefficient in self.columns[j] if i < j
                         for shift in range(self.g) if coefficient >> shift & 1)
        self.bits = sum(self.e)
        for j in range(self.d):
            generator = [modulus * int(i == j) for i in range(self.d)]
            need(not any(self.ordinary(generator)), "qZ^d is not in HZ^d")

    def ordinary(self, value):
        """Unrestricted integer division; independent of modular gates."""
        need(len(value) == self.d and all(type(x) is int for x in value),
             "integer vector")
        result = list(value)
        for j in reversed(range(self.d)):
            quotient = result[j] // self.h[j]
            for i, coefficient in self.columns[j]:
                result[i] -= quotient * coefficient
        return result

    def apply(self, words, inverse=False):
        """Mutate g-bit words by a literal reversible modular-add program."""
        need(type(inverse) is bool, "inverse flag")
        need(len(words) == self.d and
             all(type(x) is int and 0 <= x < self.q for x in words),
             "modular register range")
        operations = reversed(self.ops) if inverse else self.ops
        sign = 1 if inverse else -1
        for source, target, shift, exponent in operations:
            mask = (1 << (self.g - shift)) - 1
            addend = (words[source] >> exponent) & mask
            high = ((words[target] >> shift) + sign * addend) & mask
            words[target] = (words[target] & ((1 << shift) - 1)) | (high << shift)
        return words

    def residues(self, words):
        return [x % h for x, h in zip(words, self.h, strict=True)]

    def packed(self, words):
        output = 0
        offset = 0
        for value, h, exponent in zip(words, self.h, self.e, strict=True):
            output |= (value % h) << offset
            offset += exponent
        return output

    def bit_groups(self, inverse=False):
        """Expand an add into controlled increments; subtraction reverses it."""
        operations = reversed(self.ops) if inverse else self.ops
        for source, target, shift, exponent in operations:
            width = self.g - shift
            length = min(self.g - exponent, width)
            group = []
            for k in range(length):
                for i in reversed(range(k, width)):
                    controls = ((source, exponent+k),) + tuple(
                        (target, shift+j) for j in range(k, i))
                    group.append((controls, (target, shift+i)))
            yield group if inverse else reversed(group)

    @staticmethod
    def flip(state, controls, target):
        if all((state[word] >> bit) & 1 for word, bit in controls):
            word, bit = target
            state[word] ^= 1 << bit

    def apply_bits(self, words, inverse=False):
        """CNOT/Toffoli and max(g-2,0) clean reusable bits, all restored."""
        need(type(inverse) is bool, "inverse flag")
        need(len(words) == self.d and
             all(type(x) is int and 0 <= x < self.q for x in words),
             "modular register range")
        state = list(words) + [0]*max(0, self.g-2)
        for group in self.bit_groups(inverse):
            for controls, target in group:
                count = len(controls)
                if count <= 2:
                    self.flip(state, controls, target)
                    continue
                chain = [(controls[:2], (self.d, 0))]
                for k in range(2, count-1):
                    chain.append((((self.d+k-2, 0), controls[k]), (self.d+k-1, 0)))
                for pair, helper in chain:
                    self.flip(state, pair, helper)
                self.flip(state, (chain[-1][1], controls[-1]), target)
                for pair, helper in reversed(chain):
                    self.flip(state, pair, helper)
                need(not any(state[self.d:]), "adder helper restoration")
        words[:] = state[:self.d]
        return words

    def oracle(self, value, target, work, bit_gates=False):
        """Retain signed value; XOR canonical low bits; restore clean work."""
        need(len(value) == self.d and all(type(x) is int for x in value),
             "signed input")
        need(type(target) is int and 0 <= target < (1 << self.bits),
             "arbitrary target range")
        need(work is not value, "source/work alias")
        need(type(bit_gates) is bool, "bit gate flag")
        need(len(work) == self.d and all(type(x) is int and x == 0 for x in work),
             "clean work required")
        for j, x in enumerate(value):
            work[j] ^= x & (self.q - 1)
        apply = self.apply_bits if bit_gates else self.apply
        apply(work)
        target ^= self.packed(work)
        apply(work, inverse=True)
        for j, x in enumerate(value):
            work[j] ^= x & (self.q - 1)
        need(not any(work), "work restoration")
        return target

    def invoice(self):
        histogram = Counter(self.g - op[2] for op in self.ops)
        controls = Counter(len(c) for group in self.bit_groups() for c, _ in group)
        toffoli = sum((2*k-3)*v for k, v in controls.items() if k >= 2)
        off_diagonal = sum(len(column) - 1 for column in self.columns)
        return {
            "dimension": self.d, "modulus": self.q,
            "residue_bits": self.bits, "retained_quotient_bits": self.g*self.d-self.bits,
            "modular_adds_per_pass": len(self.ops),
            "modular_add_width_histogram": {str(k): histogram[k] for k in sorted(histogram)},
            "target_bit_positions_per_pass": sum(k*v for k, v in histogram.items()),
            "canonical_xor_oracle_modular_adds": 2*len(self.ops),
            "canonical_xor_oracle_bit_xors": 2*self.g*self.d+self.bits,
            "clean_work_bits": self.g*self.d,
            "controlled_not_histogram_per_pass": {str(k): controls[k] for k in sorted(controls)},
            "canonical_xor_oracle_cnot": 2*controls[1]+2*self.g*self.d+self.bits,
            "canonical_xor_oracle_toffoli": 2*toffoli,
            "reusable_clean_adder_bits": max(0, max(controls, default=0)-2),
            "off_diagonal_coefficients": off_diagonal,
            "direct_public_table_bits": off_diagonal*(2*(self.d-1).bit_length()+self.g)
            + self.d*self.g.bit_length(),
        }
