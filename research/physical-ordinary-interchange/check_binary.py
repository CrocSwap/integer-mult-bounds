"""Binary completion over a literal elementary reference backend."""
from pathlib import Path
from types import SimpleNamespace
import json
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import source
source.activate()
from binary import Binary
from cardinal_counts import Count
from check_join import body
from check_support import no_decode
from macro_code import Code
from ordinary import Ordinary
from physical_words import PhysicalWord
from provenance import Provenance
from records import Tape
from session import erase_marker
from words import BLANK, Word, need


class Elementary(Ordinary):
    """Checker backend: force the existing completed elementary branch."""
    def run(self, payload, original, prefixes, gap, suffix):
        return self.execute_plan(payload, original, prefixes, gap, suffix, lambda: dict(fits=False))


def run():
    cases = []
    for q in (2, 3, 5):
        # No reversed call belongs to this elementary reference. Reaching the
        # deliberately absent node binding is a test failure, never an oracle.
        binding = SimpleNamespace(codes=SimpleNamespace(q=q))
        native = Elementary(q, binding, SimpleNamespace(families=0),
                            (Code((("unreachable",),), 0),), capacity=64)
        engine = Binary(native)
        for width, prefix, gap, suffix in ((0, 2, 3, 2), (1, 1, 2, 3), (2, 2, 3, 1),
                                          (3, 1, 1, 2), (0, 1, 2, 1)):
            extent = 2**width
            volume = prefix*extent*gap*extent*suffix
            payload = Tape()
            for address in range(volume):
                payload.append(((address * 13) ^ (address >> 3) ^ 0x53) & 1)
            payload.rewind()
            initial = body(payload)
            count, pre, middle, tail = (Count.literal(value) for value in (width, prefix, gap, suffix))
            provenance = Provenance(volume)
            provenance.mark(payload)
            def forbidden(*_args, **_kwargs):
                raise ValueError("decoded or newly allocated numerical word")
            with no_decode(), provenance.installed(), patch.object(Word, "__init__", forbidden), \
                    patch.object(PhysicalWord, "inspect", forbidden):
                output = engine.run(payload, count, pre, middle, tail)
                masks = [0]*volume
                expected = bytearray(volume)
                for address, bit in enumerate(initial):
                    quotient, last = divmod(address, suffix)
                    quotient, second = divmod(quotient, extent)
                    quotient, between = divmod(quotient, gap)
                    first_prefix, first = divmod(quotient, extent)
                    target = ((((first_prefix*extent+second)*gap+between)*extent+first)*suffix+last)
                    expected[target], masks[target] = bit, 1 << address
                need(body(output) == expected and provenance.masks(output, volume) == tuple(masks),
                     "all binary rectangle columns and spectators")
                need(body(payload) == initial and payload.head == output.head == 1,
                     "binary input ownership and head return")
                need(all(all(bit == BLANK for bit in tape.cells) for tape in engine.pool.tapes),
                     "binary padding workspace erasure")
                need(all(bit == BLANK for bit in native.output.cells), "consumed native output marker erasure")
                output.clear()
                if width == 1:
                    erase_marker(output)
            cases.append(dict(q=q, width=width, spectators=[prefix, gap, suffix], columns=volume))
            payload.clear()
            for value in (count, pre, middle, tail):
                value.close()
    return cases


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
    print("PASS_BINARY_RECTANGLE_COMPLETION")
