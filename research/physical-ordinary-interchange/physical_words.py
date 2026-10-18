"""Fixed register roles whose word templates come from encoded input scans."""
import source
source.activate()
from records import Tape
from words import Arena, BLANK, LEFT, ONE, RIGHT, ZERO, Meter, Word, need


class PhysicalWord:
    def __init__(self, arena, slot):
        self.arena, self.slot, self.tape = arena, slot, Tape()

    @property
    def head(self):
        return self.tape.head

    @property
    def cells(self):
        return self.tape.cells  # Checker observation; arithmetic uses cell methods.

    def read(self):
        self.arena.meter.reads += 1
        return self.tape.read()

    def write(self, symbol):
        need(symbol in (ZERO, ONE, RIGHT, BLANK), "word tape alphabet")
        self.arena.meter.writes += 1
        self.tape.write(symbol)

    def step(self, direction):
        self.arena.meter.moves += 1
        self.tape.step(direction)

    rewind, msb, zero, erase = Word.rewind, Word.msb, Word.zero, Word.erase
    inspect = Word.inspect  # Fixture-only, forbidden by the execution checks.


class PhysicalArena(Arena):
    """Allocate a fixed number of roles before reading any numerical width.

    No bits attribute exists. Arena.zero always takes a preallocated slot and
    copies the encoded template through the retained sequential word methods.
    """
    def __init__(self, capacity):
        need(type(capacity) is int and capacity > 0, "compiled register capacity")
        self.capacity, self.meter = capacity, Meter()
        self.words = [PhysicalWord(self, slot) for slot in range(capacity)]
        self.available = list(reversed(range(capacity)))
        self.live = set()
        self.template = PhysicalWord(self, -1)
        self.initialized = False

    def prepare(self, maximum):
        """Use bitlength(maximum)+1 zero cells, with no decoded bit length."""
        need(not self.live and not self.initialized and self.template.read() == BLANK,
             "fresh word template")
        maximum.rewind()
        positive = False
        while maximum.read() != RIGHT:
            bit = maximum.read()
            need(bit in (ZERO, ONE), "encoded maximum digits")
            positive = positive or bit == ONE
            self.template.write(ZERO)
            self.template.step(1)
            maximum.step(1)
        need(positive, "positive template maximum")
        self.template.write(ZERO)
        self.template.step(1)
        self.template.write(RIGHT)
        self.template.rewind()
        maximum.rewind()
        self.initialized = True

    def load(self, value):
        """Copy a canonical Count into an initialized Word, retaining its margin."""
        result = self.zero()
        value.rewind()
        try:
            while value.read() != RIGHT:
                need(result.read() != RIGHT, "input fits encoded template")
                result.write(value.read())
                result.step(1)
                value.step(1)
            need(result.read() != RIGHT, "input retains a high zero margin")
            result.rewind()
            return result
        except BaseException:
            self.free(result)
            raise
        finally:
            value.rewind()

    def erase_owned(self):
        need(not self.live, "empty numerical roles before final erasure")
        for word in self.words:
            need(word.read() == BLANK, "erased numerical body")
            word.step(-1)
            need(word.read() == LEFT, "owned numerical origin")
            word.write(BLANK)
            word.step(1)
        if self.initialized:
            self.template.erase()
        self.template.step(-1)
        need(self.template.read() == LEFT, "owned template origin")
        self.template.write(BLANK)
        self.template.step(1)
        self.initialized = False
