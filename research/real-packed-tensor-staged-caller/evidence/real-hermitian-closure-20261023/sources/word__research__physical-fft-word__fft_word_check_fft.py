"""Complete default-crossover FFT multiplication against exact integers."""
from hashlib import sha256
from fft_word_sources import require


def packet(owner, a, b, width, consume=True):
    from cardinal_counts import Count
    from check_support import no_decode
    from ring_check_words import body, word_bits
    from session import erase_marker
    from word_product import WordProduct
    from words import BLANK
    values = tuple(Count.literal(v) for v in (a, b, width))
    saved = tuple((bytes(v.tape.cells), v.tape.head) for v in values)
    calls = dict(owner.calls)
    products = owner.product.arithmetic.products
    nodes = owner.product.word.calls["nodes"]
    try:
        with no_decode():
            output = owner.run(*values)
        actual = body(output)
        require(actual == word_bits(a*b, 2*width), "complete exact FFT-word product")
        require(saved == tuple((bytes(v.tape.cells), v.tape.head) for v in values),
                "FFT-word preserves all borrowed numerical ports")
        owner.idle()
        require(owner.closed and not owner.pool.live and owner.a is owner.b is None,
                "closed FFT-word owner")
        require(type(owner.product.word) is WordProduct and type(owner.base) is WordProduct,
                "acyclic retained Karatsuba dependencies")
        require(all(t.head == 1 and all(bit == BLANK for bit in t.cells)
                    for t in (*owner.pool.tapes, *owner.canonical)), "FFT-word owned restoration")
        delta = {key: owner.calls[key]-calls[key] for key in calls}
        require(delta == (dict(base=1, fft=0) if width <= owner.base_bits else dict(base=0, fft=1)),
                "actual default word crossover")
        result = {"width": width, "bits": len(actual), "calls": delta,
                  "sha256": sha256(actual).hexdigest(), "pool_peak": owner.pool.peak,
                  "ring_word_products": owner.product.arithmetic.products-products,
                  "ring_word_nodes": owner.product.word.calls["nodes"]-nodes}
        if consume:
            output.clear()
            erase_marker(output)
        return result
    finally:
        for value in values:
            value.close()


def signed_consumer(owner):
    from cardinal_counts import Count
    from check_support import no_decode
    from fft_arithmetic import Arithmetic
    from ring_check_words import decode, word_bits
    from ring_words import Signed
    from scratch_pool import ScratchPool
    from session import OuterScope, erase_marker, sealed_constructors
    from words import BLANK
    width, a, b = 19, 1, (1 << 19)-15
    values = tuple(Count.literal(v) for v in (a, b, width))
    left, right = Signed(values[0], True), Signed(values[1])
    saved = tuple((bytes(v.tape.cells), v.tape.head) for v in values)
    pool = ScratchPool(32)
    scope = OuterScope(pool)
    arithmetic = Arithmetic(owner, scope)
    before = dict(owner.calls)
    products = owner.product.arithmetic.products
    result = None
    try:
        with sealed_constructors(), scope.installed():
            try:
                with no_decode():
                    result = arithmetic.multiply(left, right, values[2])
                magnitude = decode(result.magnitude)
                require(result.negative and magnitude == a*b, "retained signed consumer with actual FFT word")
                require(owner.output.read() == BLANK and arithmetic.products == 1,
                        "signed consumer consumes the complete protected raw word")
                owner.idle()
            finally:
                if result is not None:
                    result.close()
                pool.empty()
        require(saved == tuple((bytes(v.tape.cells), v.tape.head) for v in values),
                "signed integration preserves borrowed magnitudes and width")
        delta = {key: owner.calls[key]-before[key] for key in before}
        require(delta == dict(base=0, fft=1), "signed integration executes the default FFT branch")
        return {"consumer": "retained Arithmetic.multiply", "width": width, "negative": True,
                "canonical_short_operand": a, "calls": delta,
                "raw_product_sha256": sha256(word_bits(magnitude, 2*width)).hexdigest(),
                "ring_word_products": owner.product.arithmetic.products-products,
                "caller_pool_peak": pool.peak}
    finally:
        for value in values:
            value.close()
        for value in pool.tapes:
            erase_marker(value)


def run():
    from fft_word_engine import FftWord
    owner = FftWord()
    return {"packets": [packet(owner, (1 << 17)-1, (1 << 17)-33, 17),
                        packet(owner, (1 << 16)-1, (1 << 16)-3, 16),
                        signed_consumer(owner)]}
