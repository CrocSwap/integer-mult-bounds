"""Small-word boundary and repeated use of the exact base owner."""
from fft_word_sources import require


def run():
    from fft_word_engine import FftWord
    from fft_word_check_fft import packet
    owner = FftWord()
    cases = []
    for width in (1, 2, 3, 8, 15, 16):
        maximum = (1 << width)-1
        for a, b in ((0, maximum), (1, maximum), (maximum, maximum)):
            cases.append(packet(owner, a, b, width))
    require(owner.calls == dict(base=len(cases), fft=0), "complete small-word branch coverage")
    return {"packets": len(cases), "widths": [1, 2, 3, 8, 15, 16],
            "last": cases[-1], "calls": owner.calls}
