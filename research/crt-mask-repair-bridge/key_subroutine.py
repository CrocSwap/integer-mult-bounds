"""Direct reverse-word key evaluator: an explicit PREMISE, not a tape program.

For one repaired Benes layer (compact word u2,t2,y8, one target, guard K=6) this computes
the repair key  T(S^-1(q))  at ONE address q by running the ten modular shears of the compact
word in reverse with negated offsets, each source load reading the CURRENT y (kumagi,
PR4169 ``Word.run(..., inverse=True)``), then applying the ideal controlled switch T.
It has no inverse table, no address loop and no good-set test.

It is plain Python integer arithmetic. It is NOT a literal tape evaluator. The bridge pays
only the tape actions that hand it the address cells and write back the key cells; the
address -> key arithmetic is the "one key costs E(p, ell)" premise of CRT.md section 4
(counted for general p, ell by PR4377, not realised on tapes here).

The non-"correct" modes are the wrong-key negative controls named in PR4169/PR4328; the
verifier feeds them through the real repair program.
"""

MODES = ("correct", "ideal_of_current", "inverse_only", "stale_source", "guarded_identity")


def source_function(table):
    """Switch-control source f(y). ``table`` is either a 32-entry Benes control table indexed by
    (a << 3) | b with a=(y>>3)&3, b=y&7 (the actual caller), or a callable y -> bit that omits
    the target bit (negative-control fixtures)."""
    if callable(table):
        return table
    return lambda y: table[(((y >> 3) & 3) << 3) | (y & 7)]


class ReverseWordKey:
    def __init__(self, target, table, mode="correct"):
        if mode not in MODES:
            raise ValueError("unknown key mode")
        self.target = target
        self.source = source_function(table)
        self.mode = mode
        self.addresses = []  # observer log; the tape program never reads it

    def run(self, state, inverse, frozen=None):
        """Ten shears of the compact word (forward) or their reverse negations."""
        u, t, y = state
        target = self.target
        sign = -1 if inverse else 1
        for step in (reversed(range(10)) if inverse else range(10)):
            if step in (4, 9):
                bit = self.source(y) if frozen is None else frozen
                u = (u + sign * (bit if step == 4 else -bit)) & 3
                continue
            shear = step if step < 4 else step - 5
            z = u & 1
            digit = t & 3
            bit = (y >> target) & 1
            if shear == 0:
                y = (y + sign * ((2 * z * digit) << target)) & 255
            elif shear == 1:
                t = (t + sign * bit) & 3
            elif shear == 2:
                y = (y + sign * ((z * (1 - 2 * digit)) << target)) & 255
            else:
                t = (t + sign * (-(bit ^ z))) & 3
        return u, t, y

    def ideal(self, state):
        u, t, y = state
        return u, t, y ^ (self.source(y) << self.target)

    def key_of(self, address_bits):
        """MSB-first '0'/'1' string of the 12-bit address -> 12-bit key string."""
        address = 0
        for symbol in address_bits:
            address = (address << 1) | (1 if symbol == "1" else 0)
        self.addresses.append(address)
        state = (address >> 10, (address >> 8) & 3, address & 255)
        if self.mode == "correct":
            out = self.ideal(self.run(state, True))
        elif self.mode == "ideal_of_current":
            out = self.ideal(state)
        elif self.mode == "inverse_only":
            out = self.run(state, True)
        elif self.mode == "stale_source":
            out = self.ideal(self.run(state, True, frozen=self.source(state[2])))
        else:  # guarded_identity: the good-set identity used as the bad inverse
            out = self.ideal(self.ideal(state))
        u, t, y = out
        return format((u << 10) | (t << 8) | y, "012b")
