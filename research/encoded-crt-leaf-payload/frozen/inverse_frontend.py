"""Encoded descending balanced levels through the existing frontend hook.

Prepared for Jerry Chen / CubeJerry with substantial OpenAI assistance.
Apache-2.0. See SEAMS.json for the exact inherited interface.
"""
from types import SimpleNamespace


def bind(forward):
    """Bind one fixed provider; no geometry or numeric value is an argument."""
    class Iterator(forward.Iterator):
        def __init__(self, words, records, entry, numeric, owner, canonical, source):
            super().__init__(words, records, entry, numeric, owner, canonical, source)
            # The inherited shape proof gives k depth tokens and half=1.
            # Skip one token, then double once per remaining token: d/2.
            depth = self.counters['depth']
            depth.step(1)
            while depth.read() == self.w.ONE:
                forward.Iterator._double_half(self)
                depth.step(1)
            self.w.need(depth.read() == self.w.RIGHT, 'complete reverse depth')
            depth.rewind()

        def _double_half(self):
            """Compatibility hook: the inherited next-level call now halves.

            Startup calls the base doubling method explicitly; every call
            through this hook is a descending transition after a level ends.
            """
            w = self.w
            half = self.counters['half']
            temporary = self.counters['double']
            odd = False
            while half.read() == w.ONE:
                odd = not odd
                if not odd:
                    temporary.append(w.ONE)
                half.step(1)
            w.need(half.read() == w.RIGHT and not odd, 'even reverse half size')
            temporary.append(w.RIGHT)
            temporary.rewind()
            w.need(temporary.read() == w.ONE, 'nonempty next reverse half')
            half.clear()
            while temporary.read() == w.ONE:
                half.append(w.ONE)
                temporary.step(1)
            w.need(temporary.read() == w.RIGHT, 'complete halved size')
            half.append(w.RIGHT)
            half.rewind()
            temporary.clear()

    return SimpleNamespace(Iterator=Iterator)
