"""Reuse the immutable radix validation; retain every original Count multiplier.

JoyboyBrian with substantial OpenAI Codex assistance. Apache-2.0.
Original cardinality/Counter/Tape semantics retain predecessor attribution.
"""

def install(records, stream, words):
    def multiply_atom_power(value, exponent, ring, q):
        cache, count = records.Tape(), None
        try:
            arena=ring.arena
            divisor,power=arena.literal(q),arena.copy(ring.modulus)
            try:
                while ring.raw.compare(power,ring.one)>0:
                    quotient,remainder=ring.raw.divmod(power,divisor)
                    try:
                        words.need(remainder.zero() and not quotient.zero(),
                                   'cardinality prime-power context')
                    except BaseException:
                        arena.free_many(quotient,remainder)
                        raise
                    arena.free_many(power,remainder)
                    power=quotient
                    cache.append(words.ONE)
                words.need(ring.raw.compare(power,ring.one)==0,'complete radix exponent')
            finally:
                arena.free_many(divisor,power)
            cache.append(words.RIGHT)
            cache.rewind()
            count = stream.Counter(exponent)
            while not count.finished:
                while cache.read() != words.RIGHT:
                    words.need(cache.read() == words.ONE, 'cached radix marker')
                    value.multiply_small(q)
                    cache.step(1)
                cache.rewind()
                count.decrement()
        finally:
            if count is not None:
                count.close()
            cache.clear()
    return multiply_atom_power
