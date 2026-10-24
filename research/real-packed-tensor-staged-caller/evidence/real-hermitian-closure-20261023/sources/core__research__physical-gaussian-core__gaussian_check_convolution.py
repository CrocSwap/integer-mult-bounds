"""Actual signed packed products against separate integer convolution."""
from hashlib import sha256
from gaussian_sources import require


def run():
    from cardinal_counts import Count
    from check_support import no_decode
    from gaussian_convolution import Convolution
    from records import Tape
    from ring_check_words import body, decode
    from ring_words import Signed, read_signed, write_signed
    from router_metadata import owned
    from session import erase_marker
    from words import BLANK
    owner = Convolution()
    cases = (([-7, 3, 11, -2], [2, -5, -3, 9], 3, 12),
             ([0, 0, 0], [17, -33, 8], 4, 16),
             ([31, -31, 31, -31, 31], [-31, -31, 31, 31, -31], 5, 16),
             ([1], [-1], 0, 4))
    records = []
    for first, second, bits, field in cases:
        left, right = Tape(), Tape()
        with owned(Count.literal(len(first)), Count.literal(field), Count.literal(bits)) as (n, width, precision):
            try:
                for source, tape in ((first, left), (second, right)):
                    for value in source:
                        with owned(Signed(Count.literal(abs(value)), value < 0)) as (signed,):
                            write_signed(signed, tape, width)
                    tape.rewind()
                saved = tuple((bytes(t.cells), t.head) for t in (left, right))
                calls = dict(owner.word.calls)
                with no_decode():
                    output = owner.run(left, right, n, width, precision)
                raw = body(output)
                actual = []
                for _ in first:
                    with owned(read_signed(output, width)) as (value,):
                        actual.append((-1 if value.negative else 1)*decode(value.magnitude))
                expected = []
                for i in range(len(first)):
                    value = sum(first[j]*second[i-j] for j in range(i+1))
                    expected.append((-1 if value < 0 else 1)*(abs(value) >> bits))
                require(actual == expected and output.read() == BLANK,
                        "complete signed convolution and one final truncation")
                require(saved == tuple((bytes(t.cells), t.head) for t in (left, right)),
                        "signed convolution preserves borrowed streams")
                require(owner.closed and not owner.pool.live, "closed signed-convolution owner")
                owner.idle()
                require(all(t.head == 1 and all(v == BLANK for v in t.cells) for t in owner.pool.tapes),
                        "signed convolution restores owned roles")
                delta = {key: owner.word.calls[key]-calls[key] for key in calls}
                require(sum(delta.values()) == 4, "four actual integer products")
                records.append({"length": len(first), "precision": bits, "width": field,
                                "values": actual, "sha256": sha256(raw).hexdigest(),
                                "word_calls": delta, "pool_peak": owner.pool.peak})
                output.clear()
                erase_marker(output)
            finally:
                for value in (left, right):
                    value.clear()
                    erase_marker(value)
    return {"packets": records, "convolutions": owner.calls,
            "word_crossover": owner.word.base_bits,
            "scope": "actual complete convolution; these widths use the fixed base branch of the authenticated word API"}
