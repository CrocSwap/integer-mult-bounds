"""Input-independent physical emission of certified coefficient pages.

Prepared for @CubeJerry with OpenAI Codex assistance. Apache-2.0.
Host integers here are the separately charged preparation result, never an
online right-hand side. Every emitted Signed bit uses the pinned word ABI.
"""
from gaussian_sources import active
active()
from cardinal_counts import Count
from records import Tape
from ring_words import Signed, write_signed
from router_metadata import owned
from session import erase_marker


NAMES = ("Finv", "F", "mu_minus", "mu_plus", "residual_minus", "residual_plus")


def emit_stream(values, width):
    result = Tape()
    try:
        for value in values:
            with owned(Signed(Count.literal(abs(value)), value < 0)) as (word,):
                write_signed(word, result, width)
        result.rewind()
        return result
    except BaseException:
        result.clear(); erase_marker(result)
        raise


class EncodedPages:
    """Six persistent streams and four canonical descriptors, prepared once."""
    def __init__(self, bundle):
        self.counts, self.streams = (), ()
        try:
            p = bundle.plan
            for value in (p.n, p.L, p.W, p.f):
                self.counts += (Count.literal(value),)
            for name in NAMES:
                self.streams += (emit_stream(bundle.streams[name], self.counts[2]),)
        except BaseException:
            self.close()
            raise

    def close(self):
        for tape in self.streams:
            tape.clear(); erase_marker(tape)
        self.streams = ()
        for count in self.counts:
            count.close(); erase_marker(count.tape)
        self.counts = ()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
