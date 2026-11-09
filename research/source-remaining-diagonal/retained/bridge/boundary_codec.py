"""Finite-control common-grid/normalization bridge for two actual tape codecs.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
Payload routines use only one-symbol reads/writes and unit head motion. Unary
format templates are prepared once; no payload integer or record counter is
decoded by these routines. Native numerical work belongs to the named service.
"""
from dataclasses import dataclass


def require(ok, message):
    if not ok:
        raise ValueError(message)


@dataclass(frozen=True)
class Format:
    external_bits: int       # one sign-magnitude real/imaginary component
    external_grid: int
    native_bits: int         # one little-endian two's-complement component
    native_grid: int
    normalizer_bits: int     # a_total = 2**normalizer_bits

    def __post_init__(self):
        values = tuple(self.__dict__.values())
        require(all(type(x) is int for x in values), "integer format, not Boolean")
        require(self.external_bits >= 2 and self.external_grid >= 0,
                "positive external magnitude carrier")
        require(self.native_grid >= self.external_grid and self.normalizer_bits >= 0,
                "exact incoming grid lift and nonnegative dyadic normalizer")
        require(self.native_bits >= self.external_bits + self.lift,
                "complete native sign and lifted external magnitude")

    @property
    def lift(self):
        return self.native_grid - self.external_grid

    @property
    def drop(self):
        return self.native_grid + self.normalizer_bits - self.external_grid


class Codec:
    """Constant owned roles, shared immutable unary formats, protected output.

    B is exactly the retained first-face transport module. Native tape methods
    are those of the retained Core Tape class. Lifecycle marker operations are
    the actual native session operations. These are source-model parameters,
    never numerical callbacks. The online code has finite-valued local state.
    """

    def __init__(self, B, NativeTape, blank, initialize_marker, erase_marker, fmt):
        self.B = B
        self.blank = blank
        self.initialize_marker = initialize_marker
        self.erase_marker = erase_marker
        # This input-independent setup is charged; no role is made per record.
        self.magnitude_clock = B.Tape("bridge magnitude clock")
        self.lift_clock = B.Tape("bridge lift clock")
        self.pad_clock = B.Tape("bridge pad clock")
        self.native_clock = B.Tape("bridge native clock")
        self.drop_clock = B.Tape("bridge drop clock")
        self.raw = B.Tape("bridge raw component")
        self.absolute = B.Tape("bridge absolute component")
        self.magnitude = B.Tape("bridge final magnitude")
        self.output = B.Tape("bridge protected normalized field")
        self.input = NativeTape()
        erase_marker(self.input)
        self.pending = False
        self.active = False
        self.input_armed = False
        self.reconfigure(fmt)

    @property
    def templates(self):
        return (self.magnitude_clock, self.lift_clock, self.pad_clock,
                self.native_clock, self.drop_clock)

    @property
    def work(self):
        return (self.raw, self.absolute, self.magnitude, self.output)

    def reconfigure(self, fmt):
        """Rebuild formats in the same roles; old visited blanks stay charged."""
        require(not self.active and not self.pending and not self.input_armed,
                "quiescent bridge format change")
        lengths = (fmt.external_bits - 1, fmt.lift,
                   fmt.native_bits - fmt.lift - fmt.external_bits + 1,
                   fmt.native_bits, fmt.drop)
        for tape, length in zip(self.templates, lengths):
            self.B.clear(tape)
            for _ in range(length):
                self.B.append(tape, "1")
            self.B.home(tape)
        self.fmt = fmt

    def bbit(self, tape):
        bit = tape.read()
        require(bit in ("0", "1"), "complete binary external component")
        tape.move(1)
        return bit == "1"

    def cbit(self, tape):
        bit = tape.read()
        require(bit in (0, 1), "complete binary native component")
        tape.step(1)
        return bit == 1

    def lift_component(self, source):
        B = self.B
        sign = self.bbit(source)
        any_one = False
        B.clear(self.raw)
        B.home(self.magnitude_clock)
        while self.magnitude_clock.read() == "1":
            bit = self.bbit(source)
            any_one = any_one or bit
            B.append(self.raw, "1" if bit else "0")
            self.magnitude_clock.move(1)
        require(not sign or any_one, "canonical external zero sign")
        B.home(self.lift_clock)
        while self.lift_clock.read() == "1":
            self.input.append(0)
            self.lift_clock.move(1)
        # raw is at its right terminator: read magnitude from least significant.
        self.raw.move(-1)
        carry = sign
        while self.raw.read() != "^":
            bit = self.raw.read() == "1"
            bit = not bit if sign else bit
            self.input.append(int(bit != carry))
            carry = bit and carry
            self.raw.move(-1)
        B.home(self.pad_clock)
        while self.pad_clock.read() == "1":
            bit = sign
            self.input.append(int(bit != carry))
            carry = bit and carry
            self.pad_clock.move(1)
        B.clear(self.raw)

    def prepare_input(self, source):
        """Lift the complete immutable external stream, exactly and in order."""
        B = self.B
        require(not self.active and not self.pending, "idle source bridge")
        require(source not in (*self.templates, *self.work), "external source owner")
        self.active = True
        self.initialize_marker(self.input)
        self.input_armed = True
        B.home(source)
        try:
            while source.read() != "!":
                self.lift_component(source)
                self.lift_component(source)
                require(source.read() == "#", "one complete complex source record")
                source.move(1)
            self.input.rewind()
        except BaseException:
            self.abort()
            raise
        finally:
            B.home(source)
        return self.input

    def return_component(self, returned):
        B = self.B
        B.clear(self.raw)
        B.home(self.native_clock)
        sign = False
        while self.native_clock.read() == "1":
            sign = self.cbit(returned)
            B.append(self.raw, "1" if sign else "0")
            self.native_clock.move(1)
        # Last native bit is the sign. Absolute value is formed without decoding.
        B.home(self.raw)
        B.clear(self.absolute)
        carry = sign
        while self.raw.read() != "!":
            bit = self.raw.read() == "1"
            bit = not bit if sign else bit
            B.append(self.absolute, "1" if bit != carry else "0")
            carry = bit and carry
            self.raw.move(1)
        B.home(self.absolute)
        B.home(self.drop_clock)
        while self.drop_clock.read() == "1" and self.absolute.read() != "!":
            self.drop_clock.move(1)
            self.absolute.move(1)
        B.clear(self.magnitude)
        B.home(self.magnitude_clock)
        any_one = False
        while self.magnitude_clock.read() == "1":
            bit = self.absolute.read() == "1"
            any_one = any_one or bit
            B.append(self.magnitude, "1" if bit else "0")
            if self.absolute.read() != "!":
                self.absolute.move(1)
            self.magnitude_clock.move(1)
        while self.absolute.read() != "!":
            require(self.absolute.read() == "0", "normalized return fits external magnitude")
            self.absolute.move(1)
        B.append(self.output, "1" if sign and any_one else "0")
        self.magnitude.move(-1)
        while self.magnitude.read() != "^":
            B.append(self.output, self.magnitude.read())
            self.magnitude.move(-1)
        for tape in (self.raw, self.absolute, self.magnitude):
            B.clear(tape)

    def prepare_return(self, returned, source):
        """Normalize once, round toward zero, preserve input, check full count.

        The unchanged original stream supplies the record clock. This avoids a
        host record counter and checks that the native field has the same size.
        """
        B = self.B
        require(self.active and not self.pending, "one active bridge input")
        B.clear(self.output)
        B.home(source)
        returned.rewind()
        try:
            while source.read() != "!":
                for _ in (0, 1):
                    self.bbit(source)
                    B.home(self.magnitude_clock)
                    while self.magnitude_clock.read() == "1":
                        self.bbit(source)
                        self.magnitude_clock.move(1)
                    self.return_component(returned)
                require(source.read() == "#", "unchanged complete input record clock")
                source.move(1)
                B.append(self.output, "#")
            require(returned.read() == self.blank, "no extra native output records")
            B.home(self.output)
            self.pending = True
        except BaseException:
            B.clear(self.output)
            raise
        finally:
            B.home(source)
            returned.rewind()
        return self.output

    def commit(self, transport):
        """Commit only a complete normalized return after the saved-copy phase."""
        B = self.B
        require(self.active and self.pending and transport.phase == "saved",
                "saved originals and complete protected Core return")
        require(transport.source not in (*self.templates, *self.work),
                "distinct destination source owner")
        # No validation remains after this point: a whole sequential clone.
        B.clone(self.output, transport.source)
        B.home(transport.source)
        transport.phase = "core"
        self.abort()

    def abort(self):
        """Erase owned payloads; retained extent and immutable templates remain."""
        B = self.B
        if self.input_armed:
            self.input.clear()
            self.erase_marker(self.input)
            self.input_armed = False
        for tape in self.work:
            B.clear(tape)
        for tape in self.templates:
            B.home(tape)
        self.active = self.pending = False


class BoundCore:
    """The concrete Core run/consume protocol, without a payload callback.

    `core` is the pinned OriginalCore (or the independently scoped CompleteCore
    packed boundary); its prepared immutable source ports are `arguments`.
    The all-size source theorem determines which boundary is being invoked.
    """

    def __init__(self, codec, core, arguments):
        self.codec = codec
        self.core = core
        self.arguments = tuple(arguments)

    def run(self, transport):
        require(transport.phase == "saved", "halo copies precede actual Core")
        succeeded = False
        try:
            payload = self.codec.prepare_input(transport.source)
            returned = self.core.run(payload, *self.arguments)
            self.codec.prepare_return(returned, transport.source)
            self.core.consume()
            self.codec.commit(transport)
            succeeded = True
        finally:
            if getattr(self.core, "pending", False):
                self.core.consume()
            if not succeeded:
                self.codec.abort()
