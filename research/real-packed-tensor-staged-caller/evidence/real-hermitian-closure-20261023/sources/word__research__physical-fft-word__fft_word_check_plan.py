"""Encoded geometry, including large metadata-only widths."""
from fft_word_sources import require


def run():
    from cardinal_counts import Count
    from check_support import no_decode
    from fft_word_plan import WordPlan
    from ring_check_words import decode
    records = []
    for width in (2, 3, 5, 16, 17, 19, 21, 33, 65, 257, 1024, (1 << 33)+7, (1 << 257)+7):
        n = Count.literal(width)
        saved = bytes(n.tape.cells), n.tape.head
        plan = WordPlan(n)
        try:
            with no_decode():
                plan.compile()
            b = (width-1).bit_length()
            q = (width+b-1)//b
            ell = (2*q-1).bit_length()
            r, p = 1 << ell, 2*b+ell
            expected = dict(one=1, b=b, q=q, ell=ell, r=r, p=p, component=p+2,
                            shift=p-b, output_bits=2*width,
                            padding_bits=2*(2*r-q)*(p+2), dummy_bits=2*r*(p+2),
                            coefficient_limit=1 << (p-1))
            require({key: decode(value) for key, value in plan.fields.items()} == expected,
                    "exact encoded radix geometry")
            require(2*q <= r < 4*q and r*b >= 2*width and ell < p
                    and p == 2*b+ell, "no-wrap and exact-grid invariants")
            require((bytes(n.tape.cells), n.tape.head) == saved, "preserved width descriptor")
            records.append({"width": str(width), "b": b, "q": str(q), "ell": ell,
                            "p": p, "metadata_only": True})
        finally:
            plan.close()
            n.close()
    for width in (0, 1):
        n = Count.literal(width)
        plan = WordPlan(n)
        try:
            try:
                plan.compile()
            except ValueError as error:
                require("extent at least two" in str(error), "FFT geometry excludes width zero or one")
            else:
                raise ValueError("missing FFT geometry admission rejection")
        finally:
            plan.close()
            n.close()
    return {"plans": records, "rejected_widths": [0, 1]}
