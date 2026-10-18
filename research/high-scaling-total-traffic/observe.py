"""Meter literal runtime calls and track every payload's original address."""

from types import SimpleNamespace

from source import load
from traffic import require

MAX_VOLUME = 25000
MAX_DIGITS = 4096


def traffic(meter):
    return meter.reads + meter.writes + meter.moves


class Observer:
    def __init__(self, data, mutation=None):
        self.modules, self.doubled = load(data, mutation)
        self.tapes, self.origin = [], None
        observer, original = self, self.modules["records"].Tape

        class ObservedTape(original):
            def __init__(self):
                super().__init__()
                self.payload, self.origins = False, {}
                observer.tapes.append(self)

            def read(self):
                value = super().read()
                if self.payload and value in (0, 1):
                    observer.origin = self.origins[self.head]
                return value

            def write(self, value):
                if self.payload and value in (0, 1):
                    self.origins[self.head] = observer.origin
                super().write(value)

        self.Tape = ObservedTape
        for module in self.modules.values():
            if hasattr(module, "Tape"):
                module.Tape = ObservedTape

    def measured(self, arena):
        return traffic(arena.meter) + sum(traffic(t.meter) for t in self.tapes)

    def factory(self):
        tape = self.Tape()
        tape.payload = True
        return tape

    def prepare(self, modulus, before, suffix, digits, malformed):
        require(type(modulus) is int and 2 <= modulus <= 129, "fixture modulus bound")
        require(
            all(type(n) is int and 1 <= n <= 100 for n in (before, suffix)),
            "fixture spectators",
        )
        volume = modulus * before * suffix
        require(volume <= MAX_VOLUME, "fixture volume bound")
        require(
            type(digits) is int and modulus.bit_length() + 1 <= digits <= MAX_DIGITS,
            "fixture width",
        )
        self.tapes, self.origin = [], None
        words = self.modules["words"]
        arena = words.Arena(digits, capacity=8)
        encoded = arena.input(modulus)
        ring = (
            words.Ring(encoded)
            if digits == modulus.bit_length() + 1
            else SimpleNamespace(modulus=encoded)
        )
        count = self.modules["cardinal_counts"].Count
        bc, sc = count.literal(before), count.literal(suffix)
        tape = self.factory()
        tape.cells.extend((i * 11 ^ i // 3 ^ 5) & 1 for i in range(volume))
        tape.origins = {i + 1: i for i in range(volume)}
        if malformed == "short":
            tape.cells.pop()
        elif malformed == "long":
            tape.cells.append(1)
            tape.origins[volume + 1] = volume
        elif malformed == "non-bit":
            tape.cells[2] = words.RIGHT
        return arena, encoded, ring, bc, sc, tape

    def run(
        self,
        modulus,
        before,
        suffix,
        inverse=False,
        digits=None,
        malformed=None,
        extra=False,
    ):
        digits = modulus.bit_length() + 1 if digits is None else digits
        state = self.prepare(modulus, before, suffix, digits, malformed)
        arena, encoded, ring, bc, sc, tape = state
        extra_zero = arena.input(0) if extra else None
        borrowed = [encoded, bc.tape, sc.tape, tape]
        if extra_zero is not None:
            borrowed.append(extra_zero)
        snapshots = [bytes(word.cells) for word in borrowed]
        protected, output = set(arena.live), None
        started = self.measured(arena)
        started_tapes = len(self.tapes)
        old_inspect = self.modules["words"].Word.inspect

        def forbidden(_word):
            raise ValueError("runtime numerical decoding")

        self.modules["words"].Word.inspect = forbidden
        try:
            if extra:
                output = self.extra_work(tape, ring, bc, sc, inverse, extra_zero)
            else:
                output = self.doubled(tape, ring, bc, sc, self.factory, inverse)
            measured = self.measured(arena) - started
            require(malformed is None, "malformed stream accepted")
            self.check_endpoint(output, tape, modulus, before, suffix, inverse)
            self.check_restoration(
                borrowed, snapshots, arena, protected, (bc.tape, sc.tape, tape, output)
            )
            return {
                "q": modulus,
                "b": before,
                "s": suffix,
                "inverse": inverse,
                "digits": digits,
                "traffic": measured,
                "allocations": len(self.tapes) - started_tapes,
            }
        finally:
            self.modules["words"].Word.inspect = old_inspect
            if output is not None:
                output.clear()
            tape.clear()
            bc.close()
            sc.close()
            if hasattr(ring, "close"):
                ring.close()
            arena.free(encoded)
            if extra_zero is not None:
                arena.free(extra_zero)
            require(not arena.live, "fixture numerical cleanup")

    def check_restoration(self, borrowed, snapshots, arena, protected, retained):
        require(
            [bytes(word.cells) for word in borrowed] == snapshots,
            "borrowed tape content",
        )
        require(all(word.head == 1 for word in borrowed), "borrowed tape heads")
        require(arena.live == protected, "numerical liveness restored")
        private = [word for word in self.tapes if word not in retained]
        blank = self.modules["words"].BLANK
        require(
            all(
                word.head == 1 and all(x == blank for x in word.cells[1:])
                for word in private
            ),
            "private erasure",
        )

    def check_endpoint(self, output, source, modulus, before, suffix, inverse):
        coefficient = pow(2, -1, modulus) if inverse else 2
        expected = [None] * (modulus * before * suffix)
        for address in range(len(expected)):
            block, tail = divmod(address, suffix)
            prefix, value = divmod(block, modulus)
            target = (prefix * modulus + coefficient * value % modulus) * suffix + tail
            expected[target] = address
        require(
            [output.origins[i + 1] for i in range(len(expected))] == expected,
            "complete origin map",
        )
        require(
            bytes(output.cells[1:]) == bytes(source.cells[i + 1] for i in expected),
            "Boolean endpoint",
        )
        require(
            output.head == source.head == 1 and output is not source,
            "distinct rewound output",
        )

    def extra_work(self, source, ring, before, suffix, inverse, zero):
        """Endpoint-preserving mutant; no production source is edited."""
        namespace = self.doubled.__globals__
        rows_namespace = namespace["copy_rows"].__globals__
        original = namespace["copy_bits"]
        counter = self.modules["stream"].Counter

        def inflated(*args):
            unused = counter(zero)
            require(unused.finished, "zero countdown control")
            unused.close()
            return original(*args)

        namespace["copy_bits"] = rows_namespace["copy_bits"] = inflated
        try:
            return self.doubled(source, ring, before, suffix, self.factory, inverse)
        finally:
            namespace["copy_bits"] = rows_namespace["copy_bits"] = original
