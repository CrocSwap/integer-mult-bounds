"""Emit one fixed fourteen-tape graph for the closed switch query.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The builder and ABI come from Jerry Chen's PR7593. Initialization below
adapts that source. Nick Petalas supplied the endpoint formulas.
All Python loops emit fixed code; no fixture value reaches an instruction.
"""

from sources import load

source = load("source_switch_builder", "retained/pr7593/switch.py")
B, L, E = source.B, source.L, source.E
H_IN, S_IN, A_IN, J_IN, X_IN, OUT = range(6)
COUNT, WIDTH, S, A, J, X, LAST, TEMP = range(6, 14)
PRIVATE = tuple(range(6, 14))
NUMBERS = S, A, J, X, LAST, TEMP


class Builder(source.Builder):
    def compact(self, tape):
        """Remove high zero digits and move END next to the highest one."""
        scan, advance, end, trim, zero, one, empty, done = [self.fresh() for _ in range(8)]
        self.mark(scan); self.read(tape, {0: advance, 1: advance, E: end})
        self.mark(advance); self.op('M', tape, 1); self.jump(scan)
        self.mark(end); self.op('W', tape, B); self.op('M', tape, -1)
        self.mark(trim); self.read(tape, {0: zero, 1: one, L: empty})
        self.mark(zero); self.op('W', tape, B); self.op('M', tape, -1); self.jump(trim)
        self.mark(one); self.op('M', tape, 1); self.op('W', tape, E)
        self.rewind(tape); self.jump(done)
        self.mark(empty); self.op('M', tape, 1); self.op('W', tape, E)
        self.mark(done)

    def compact_decrement(self, tape):
        """Decrement a positive canonical word and keep its shortened END."""
        loop, zero, one, top, inside, done = [self.fresh() for _ in range(6)]
        self.mark(loop); self.read(tape, {0: zero, 1: one})
        self.mark(zero); self.op('W', tape, 1); self.op('M', tape, 1); self.jump(loop)
        self.mark(one); self.op('W', tape, 0); self.op('M', tape, 1)
        self.read(tape, {0: inside, 1: inside, E: top})
        self.mark(top); self.op('W', tape, B); self.op('M', tape, -1)
        self.op('W', tape, E); self.rewind(tape); self.jump(done)
        self.mark(inside); self.rewind(tape)
        self.mark(done)

    def binary(self, target, other, subtract=False):
        """Add or subtract equal-width unsigned words without overflow."""
        loops = [self.fresh() for _ in range(2)]
        done = self.fresh(); self.jump(loops[0])
        for carry in range(2):
            self.mark(loops[carry])
            first = [self.fresh() for _ in range(2)]; end = self.fresh()
            self.read(target, {0: first[0], 1: first[1], E: end})
            for left in range(2):
                self.mark(first[left]); second = [self.fresh() for _ in range(2)]
                self.read(other, {0: second[0], 1: second[1]})
                for right in range(2):
                    self.mark(second[right])
                    value = left - right - carry if subtract else left + right + carry
                    next_carry = int(value < 0) if subtract else value // 2
                    self.op('W', target, value & 1)
                    self.op('M', target, 1); self.op('M', other, 1); self.jump(loops[next_carry])
            self.mark(end); self.read(other, {E: done if carry == 0 else 'reject'})
        self.mark(done); self.rewind(target); self.rewind(other)

    def copy_suffix(self, origin, target):
        """Copy from the current source head and put END at the new frontier."""
        loop, zero, one, done = [self.fresh() for _ in range(4)]
        self.mark(loop); self.read(origin, {0: zero, 1: one, E: done})
        for value, label in ((0, zero), (1, one)):
            self.mark(label); self.op('W', target, value)
            self.op('M', origin, 1); self.op('M', target, 1); self.jump(loop)
        self.mark(done); self.op('W', target, E)
        self.rewind(origin); self.rewind(target)


def initialize(b):
    """Validate and copy the predecessor ABI, with a linear height countdown."""
    for tape in PRIVATE:
        b.op('M', tape, -1); b.op('W', tape, L); b.op('M', tape, 1)
    blank, end = b.fresh(), b.fresh()
    b.read(OUT, {B: blank}); b.mark(blank); b.op('M', OUT, 1)
    b.read(OUT, {B: end}); b.mark(end); b.op('M', OUT, -1)
    h0, h1, put0, put1, copied = [b.fresh() for _ in range(5)]
    b.read(H_IN, {0: put0, 1: put1})
    for bit, put, after in ((0, put0, h0), (1, put1, h1)):
        b.mark(put); b.op('W', COUNT, bit); b.op('M', COUNT, 1)
        b.op('M', H_IN, 1); b.jump(after)
    b.mark(h0); b.read(H_IN, {0: put0, 1: put1})
    b.mark(h1); b.read(H_IN, {0: put0, 1: put1, B: copied})
    b.mark(copied); b.op('W', COUNT, E); b.rewind(COUNT); b.rewind(H_IN)
    b.op('W', WIDTH, 1); b.op('M', WIDTH, 1)
    loop, append, done = [b.fresh() for _ in range(3)]
    b.mark(loop); b.read(COUNT, {0: append, 1: append, E: done})
    b.mark(append); b.op('W', WIDTH, 1); b.op('M', WIDTH, 1)
    b.compact_decrement(COUNT); b.jump(loop)
    b.mark(done); b.op('W', WIDTH, E); b.rewind(WIDTH)
    loop, bit, done = [b.fresh() for _ in range(3)]
    b.mark(loop); b.read(WIDTH, {1: bit, E: done}); b.mark(bit)
    for tape in NUMBERS:
        b.op('W', tape, 0); b.op('M', tape, 1)
    b.op('M', WIDTH, 1); b.jump(loop); b.mark(done)
    for tape in NUMBERS:
        b.op('W', tape, E); b.rewind(tape)
    b.rewind(WIDTH)
    for origin, target in ((S_IN, S), (A_IN, A), (J_IN, J), (X_IN, X)):
        loop, bit, end, done, put0, put1 = [b.fresh() for _ in range(6)]
        b.mark(loop); b.read(WIDTH, {1: bit, E: end})
        b.mark(bit); b.read(origin, {0: put0, 1: put1})
        for value, label in ((0, put0), (1, put1)):
            b.mark(label); b.op('W', target, value)
            for tape in (origin, target, WIDTH): b.op('M', tape, 1)
            b.jump(loop)
        b.mark(end); b.read(origin, {B: done}); b.mark(done)
        for tape in (origin, target, WIDTH): b.rewind(tape)
    loop, put0, put1, done = [b.fresh() for _ in range(4)]
    b.mark(loop); b.read(H_IN, {0: put0, 1: put1, B: done})
    for value, label in ((0, put0), (1, put1)):
        b.mark(label); b.op('W', LAST, value)
        b.op('M', LAST, 1); b.op('M', H_IN, 1); b.jump(loop)
    b.mark(done); b.rewind(H_IN); b.rewind(LAST)
    b.shift_left(LAST); b.decrement(LAST); b.decrement(LAST)
    loop, advance, done = [b.fresh() for _ in range(3)]
    b.mark(loop); b.read(TEMP, {0: advance, E: done})
    b.mark(advance); b.op('M', TEMP, 1); b.jump(loop)
    b.mark(done); b.op('M', TEMP, -1); b.op('W', TEMP, 1); b.rewind(TEMP)
    nonzero, bounded, a_ok, x_ok, domain = [b.fresh() for _ in range(5)]
    b.zero_test(S, 'reject', nonzero); b.mark(nonzero)
    b.compare(S, TEMP, bounded, bounded, 'reject'); b.mark(bounded)
    b.compare(A, S, a_ok, 'reject', 'reject'); b.mark(a_ok)
    b.compare(X, TEMP, x_ok, 'reject', 'reject'); b.mark(x_ok)
    b.compare(J, LAST, domain, domain, 'reject'); b.mark(domain)


def quotient_pair(b, mutation):
    """Read d low digits for carries, then copy each high quotient once."""
    low = {(u, v): b.fresh() for u in range(2) for v in range(2)}
    high = {(u, v): b.fresh() for u in range(2) for v in range(2)}
    done = b.fresh(); b.jump(low[0, 0])
    for carry_a, carry_b in low:
        more = b.fresh(); b.mark(low[carry_a, carry_b])
        b.read(J, {0: more, 1: more, E: high[carry_a, carry_b]})
        b.mark(more); b.compact_decrement(J)
        ar = [b.fresh() for _ in range(2)]; b.read(A, {0: ar[0], 1: ar[1]})
        for digit_a in range(2):
            b.mark(ar[digit_a]); br = [b.fresh() for _ in range(2)]
            b.read(S, {0: br[0], 1: br[1]})
            for digit_b in range(2):
                b.mark(br[digit_b]); xr = [b.fresh() for _ in range(2)]
                b.read(X, {0: xr[0], 1: xr[1]})
                for digit_x in range(2):
                    b.mark(xr[digit_x])
                    ca = (digit_a + digit_x + carry_a) // 2
                    cb = (digit_b + (digit_x if mutation == 'wrong_complement' else 1-digit_x) + carry_b) // 2
                    if mutation == 'lost_carry': ca = 0
                    for tape in (A, S, X): b.op('M', tape, 1)
                    b.jump(low[ca, cb])
    for carry_a, carry_b in high:
        b.mark(high[carry_a, carry_b])
        ar = [b.fresh() for _ in range(2)]; end = b.fresh()
        b.read(A, {0: ar[0], 1: ar[1], E: end})
        for digit_a in range(2):
            b.mark(ar[digit_a]); br = [b.fresh() for _ in range(2)]
            b.read(S, {0: br[0], 1: br[1]})
            for digit_b in range(2):
                b.mark(br[digit_b]); va, vb = digit_a + carry_a, digit_b + carry_b
                b.op('W', TEMP, va & 1); b.op('W', LAST, vb & 1)
                for tape in (A, S, TEMP, LAST): b.op('M', tape, 1)
                b.jump(high[va // 2, vb // 2])
        b.mark(end); b.read(S, {E: done if carry_a == carry_b == 0 else 'reject'})
    b.mark(done); b.op('W', TEMP, E); b.op('W', LAST, E)
    for tape in (A, S, TEMP, LAST): b.rewind(tape)
    b.copy_suffix(X, A)
    b.copy_suffix(TEMP, S)
    b.binary(S, LAST)


def answer_endpoint(b, mode, mutation):
    """Use A as the shifted wire, TEMP as offset, and S as modulus."""
    left, right = b.fresh(), b.fresh()
    b.zero_test(TEMP, 'answer0', left); b.mark(left)
    if mutation != 'lost_identity': b.zero_test(LAST, 'answer0', right)
    b.mark(right)
    if mode == 'center':
        b.jump('answer1'); return
    if mode == 'first':
        odd, both = b.fresh(), b.fresh()
        b.read(S, {0: 'answer0', 1: odd}); b.mark(odd)
        b.read(TEMP, {0: 'answer0', 1: both}); b.mark(both)
        b.compare(A, S, 'answer0', 'answer1', 'answer0', skip=1)
        return
    even, odd, odd_offset, both, inside = [b.fresh() for _ in range(5)]
    b.read(S, {0: even, 1: odd})
    b.mark(even); b.read(TEMP, {0: 'answer0', 1: odd_offset})
    b.mark(odd_offset); b.compare(A, S, 'answer1', 'answer0', 'answer0')
    b.mark(odd); even_offset = b.fresh()
    b.read(TEMP, {0: even_offset, 1: both})
    b.mark(even_offset); b.compare(A, TEMP, 'answer1', 'answer0', 'answer0')
    b.mark(both); b.compare(A, S, inside, inside, 'answer0'); b.mark(inside)
    b.decrement(TEMP); b.compare(A, TEMP, 'answer0', 'answer1', 'answer1')


def compile_query(mutation=None):
    if mutation not in (None, 'wrong_complement', 'lost_carry', 'lost_identity'):
        raise ValueError('unknown semantic mutation')
    b = Builder(); initialize(b)
    b.mark('query_loop')
    b.binary(S, A, subtract=True)
    b.binary(LAST, J, subtract=True)
    entries = {mode: b.fresh() for mode in ('first', 'center', 'last')}
    b.compare(J, LAST, entries['first'], entries['center'], entries['last'])
    for mode, label in entries.items():
        b.mark(label)
        if mode == 'last': b.copy_word(LAST, J)
        b.compact(J); quotient_pair(b, mutation); answer_endpoint(b, mode, mutation)
    b.mark('answer0'); b.op('W', OUT, 0); b.jump('success')
    b.mark('answer1'); b.op('W', OUT, 1); b.jump('success')
    b.mark('success'); b.cleanup('DONE')
    b.mark('reject'); b.cleanup('REJECT')
    return b.finish(), dict(b.labels)
