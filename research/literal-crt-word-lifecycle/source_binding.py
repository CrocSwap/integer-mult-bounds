"""Source-level seam for the pinned current CRT caller.

The higher Python controller is retained. This adapter replaces only its
allocation/copy/free services and the #7596 reservation methods. Finite
returned tags name existing Words; no host free-stack selects an output.
"""
from collections.abc import Set
import hardware


class LiveView(Set):
    def __init__(self, owner):
        self.owner = owner

    def __contains__(self, slot):
        return isinstance(slot, int) and 0 <= slot < 64 and self.owner.is_live(slot)

    def __iter__(self):
        for slot in range(64):
            if self.owner.is_live(slot):
                yield slot

    def __len__(self):
        return sum(1 for _ in self)


class Owner:
    def __init__(self, arena, program, stack, source_selector, output_selector):
        if len(arena.words) != 64 or arena.capacity != 64:
            raise ValueError("exact eager current64 inventory")
        if any(word.slot != i or word.arena is not arena for i, word in enumerate(arena.words)):
            raise ValueError("fixed physical Word identities")
        if set(arena.live) != set(range(8)) or list(arena.available) != list(reversed(range(8, 64))):
            raise ValueError("fresh current Entry live/free contract")
        self.arena, self.program = arena, program
        self.ports = tuple(hardware.WordPort(word) for word in arena.words) + (
            hardware.WordPort(arena.template), stack, source_selector, output_selector)
        self.answers = {f"ALLOC_{slot}": arena.words[slot] for slot in range(8, 64)}
        self.operations = []  # Erasable verifier observation; never read by execution.
        self._run("INIT", "READY")
        parent = type(arena)
        owner = self

        class ManagedArena(parent):
            @property
            def live(self):
                return LiveView(owner)

            @property
            def available(self):
                raise ValueError("host free-stack access is unavailable")

            def zero(self):
                return owner.allocate("ZERO")

            def copy(self, source):
                owner.bind(source)
                return owner.allocate("COPY")

            def free(self, word):
                owner.bind(word)
                owner._run("FREE", "FREED")

        arena.__class__ = ManagedArena
        arena.__dict__.pop("live", None)
        arena.__dict__.pop("available", None)

    def _run(self, entry, expected=None):
        result = self.program.run(self.ports, entry)
        self.operations.append((entry, result["status"], result["instructions"]))
        if expected is not None and result["status"] != expected:
            raise ValueError(f"lifecycle rejected: {result['status']}")
        return result["status"]

    def bind(self, word):
        slot = word.slot
        if not isinstance(slot, int) or not 0 <= slot < 64 or word is not self.arena.words[slot] or word.arena is not self.arena:
            raise ValueError("typed bound current Word")
        self._run(self.program.metadata["setters"][slot], "BOUND")

    def is_live(self, slot):
        self._run(self.program.metadata["setters"][slot], "BOUND")
        result = self._run("IS_LIVE")
        if result not in ("LIVE", "FREE"):
            raise ValueError("lifecycle live query rejected")
        return result == "LIVE"

    def allocate(self, kind="TAKE"):
        status = self._run(kind)
        if status not in self.answers:
            raise ValueError(f"lifecycle allocation rejected: {status}")
        word = self.answers[status]
        self.arena.meter.allocations += 1
        return word

    def reserve(self, arena, left, right, count):
        if arena is not self.arena or count not in (0, 1, 2):
            raise ValueError("one exact Arena and finite result count")
        for word in (left, right):
            if (word.arena is not arena or not isinstance(word.slot, int)
                    or not 0 <= word.slot < 64 or word is not arena.words[word.slot]
                    or not self.is_live(word.slot)):
                raise ValueError("bound live arithmetic input")
        if count == 2 and left is right:
            raise ValueError("division requires distinct inputs")
        return tuple(self.allocate("TAKE") for _ in range(count))

    def close(self):
        self._run("CLOSE", "RETIRED")


def arithmetic_binding(Parent, lifecycle_owner):
    """Replace the two exact #7596 allocation seams; numerical graph is unchanged.

    Replacing reserve removes the old coarse metadata invoice at that seam.
    A joined receipt must add these physical instructions explicitly; this
    adapter does not claim the predecessor's exact receipt format.
    """
    class Binding(Parent):
        def reserve(self, arena, left, right):
            return lifecycle_owner.reserve(arena, left, right, 2)

        def reserve_simple(self, arena, left, right, output):
            result = lifecycle_owner.reserve(arena, left, right, int(bool(output)))
            return result[0] if result else None

    return Binding
