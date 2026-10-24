"""Codec checks using independent integer convolution as a boundary fixture."""
from hashlib import sha256
from fft_word_sources import require


def geometry(width):
    b = (width-1).bit_length()
    q = (width+b-1)//b
    ell = (2*q-1).bit_length()
    return b, q, ell, 1 << ell, 2*b+ell


def fixtures(a, b, width):
    from check_composed import encode
    digit_bits, q, ell, r, p = geometry(width)
    mask = (1 << digit_bits)-1
    left = [(a >> (i*digit_bits)) & mask for i in range(q)]
    right = [(b >> (i*digit_bits)) & mask for i in range(q)]
    packets = [encode([(v << (p-digit_bits), 0) for v in digits]
                      + [(0, 0)]*(2*r-q), p+2) for digits in (left, right)]
    coefficients = [0]*r
    for i, x in enumerate(left):
        for j, y in enumerate(right):
            coefficients[i+j] += x*y
    require(max(coefficients) < 1 << (p-1), "independent coefficient headroom")
    returned = encode([(v, 0) for v in coefficients]+[(0, 0)]*r, p+2)
    return packets, returned, (digit_bits, q, ell, r, p)


def packet(a, b, width):
    from cardinal_counts import Count
    from check_support import no_decode
    from fft_word_codec import pack, unpack
    from fft_word_plan import WordPlan
    from records import Tape
    from ring_check_words import body, tape, word_bits
    from scratch_pool import ScratchPool
    from session import OuterScope, borrowed_tape, erase_marker, sealed_constructors
    from words import BLANK
    expected, raw, shape = fixtures(a, b, width)
    counts = tuple(Count.literal(v) for v in (a, b, width))
    saved = tuple((bytes(v.tape.cells), v.tape.head) for v in counts)
    source, output = tape(raw), Tape()
    pool = ScratchPool(128)
    scope = OuterScope(pool)
    plan = WordPlan(counts[2])
    try:
        with sealed_constructors(), scope.installed():
            try:
                with no_decode():
                    plan.compile()
                for value, wanted in zip(counts[:2], expected):
                    with no_decode():
                        packed = pack(value, plan, pool)
                    try:
                        require(body(borrowed_tape(packed)) == wanted, "sequential radix-grid packing")
                    finally:
                        packed.clear()
                with no_decode():
                    unpack(source, output, plan)
                require(body(output) == word_bits(a*b, 2*width), "sequential exact carries and output padding")
            finally:
                plan.close()
                pool.empty()
        require(saved == tuple((bytes(v.tape.cells), v.tape.head) for v in counts)
                and body(source) == raw, "codec preserves borrowed inputs")
        require(all(t.head == 1 and all(v == BLANK for v in t.cells[1:]) for t in pool.tapes),
                "codec scratch restoration")
        return {"width": width, "operand_bits": [a.bit_length(), b.bit_length()],
                "digit_bits": shape[0], "digits": shape[1], "ell": shape[2], "p": shape[4],
                "output_sha256": sha256(body(output)).hexdigest(), "pool_peak": pool.peak,
                "scope": "codec only; the ring return comes from independent integer convolution"}
    finally:
        output.clear()
        erase_marker(output)
        for value in counts:
            value.close()
        for value in pool.tapes:
            erase_marker(value)


def run():
    records = []
    for width in (2, 3, 5, 17, 21, 65, 257, 1024):
        maximum = (1 << width)-1
        records.append(packet(maximum, maximum-2, width))
    records.append(packet(1, (1 << 65)-7, 65))
    records.append(packet(0, (1 << 257)-1, 257))
    return {"packets": records}
