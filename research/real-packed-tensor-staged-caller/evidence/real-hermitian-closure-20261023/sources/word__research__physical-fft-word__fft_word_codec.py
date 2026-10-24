"""Sequential magnitude packing and exact radix carries on encoded tapes."""
from fft_word_sources import active
active()
from cardinal_counts import Count
from encoded import compare
from ring_words import read_signed, right_shift
from router_metadata import indices, owned
from stream import Counter
from words import BLANK, RIGHT, need


def pack(source, plan, pool):
    output = pool.acquire()
    source.rewind()
    try:
        for _ in indices(plan.q):
            for _ in indices(plan.shift):
                output.append(0)
            for _ in indices(plan.b):
                ended = source.read() == RIGHT
                bit = 0 if ended else source.read()
                need(bit in (0, 1), "canonical packed word digit")
                output.append(bit)
                if not ended:
                    source.step(1)
            for _ in range(2):
                output.append(0)
            for _ in indices(plan.component):
                output.append(0)
        need(source.read() == RIGHT, "complete declared-width word packing")
        for _ in indices(plan.padding_bits):
            output.append(0)
        output.rewind()
        return output
    except BaseException:
        output.clear()
        raise
    finally:
        source.rewind()


def unpack(source, output, plan):
    source.rewind()
    carry = Count.literal(0)
    try:
        with owned(Counter(plan.output_bits)) as (remaining,):
            for _ in indices(plan.r):
                with owned(read_signed(source, plan.component)) as (real,):
                    with owned(read_signed(source, plan.component)) as (imaginary,):
                        need(not real.negative and imaginary.magnitude.zero(),
                             "nonnegative real digit-convolution coefficient")
                        need(compare(real.magnitude, plan.coefficient_limit) < 0,
                             "digit-convolution coefficient headroom")
                        total = real.magnitude
                        total.add(carry)
                        total.rewind()
                        for _ in indices(plan.b):
                            ended = total.read() == RIGHT
                            bit = 0 if ended else total.read()
                            need(bit in (0, 1), "canonical carried word digit")
                            if remaining.finished:
                                need(bit == 0, "zero high product padding")
                            else:
                                output.append(bit)
                                remaining.decrement()
                            if not ended:
                                total.step(1)
                        following = right_shift(total, plan.b)
                        carry.close()
                        carry = following
            need(remaining.finished and carry.zero(), "complete exact word output and zero final carry")
        for _ in indices(plan.dummy_bits):
            need(source.read() == 0, "zero second product record")
            source.step(1)
        need(source.read() == BLANK, "complete normalized word-product packet")
    finally:
        carry.close()
        source.rewind()
