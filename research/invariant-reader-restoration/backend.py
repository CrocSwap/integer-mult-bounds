"""Independent integer-scalar compiler and literal fixed-tape interpreter.

No matrix library or certificate generator is used here.  A permutation ``p``
means ``new[j] = old[p[j]]``.  The compiler emits only distinct-port shears
``('add', destination, source, sign)`` with sign +1 or -1.  Scalar ports are
fixed consecutive tape words; port 0 is the data-head origin.

The source register A is a clean scalar outside the tape.  One ADD is executed
as A += memory[source], memory[destination] += sign*A, A -= memory[source].
The tape scratch T used by swaps is a separate word, not a second register A.
Each ADD returns A and the data head to their initial states.  Instruction
descriptors and loop/dispatch preparation are not included in this data-tape
invoice; the accompanying note must price or delimit that control cost.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Any


Instruction = tuple[str, int, int, int]


def _integer(value: object, name: str) -> int:
    """Reject bool as well as non-integral values for ports and coefficients."""
    if type(value) is not int:
        raise ValueError(f"{name} must be an integer (not bool)")
    return value


def _inverse(permutation: Sequence[int]) -> list[int]:
    inverse = [0] * len(permutation)
    for destination, source in enumerate(permutation):
        inverse[source] = destination
    return inverse


def _emit_permutation(
    program: list[Instruction], permutation: Sequence[int], temp: int
) -> None:
    """Realize disjoint gather cycles with adjacent swaps and one clean T."""
    seen: set[int] = set()
    for start in range(len(permutation)):
        if start in seen:
            continue
        cycle: list[int] = []
        cursor = start
        while cursor not in seen:
            cycle.append(cursor)
            seen.add(cursor)
            cursor = permutation[cursor]
        for first, second in zip(cycle, cycle[1:]):
            # (a, b, T=0) -> (b, a, T=0), using no hidden scalar swap.
            program.extend(
                [
                    ("add", temp, first, 1),
                    ("add", first, temp, -1),
                    ("add", first, second, 1),
                    ("add", second, first, -1),
                    ("add", second, temp, 1),
                    ("add", temp, second, -1),
                ]
            )


def compile_batch(
    perms: Sequence[Sequence[int]],
    readers: Sequence[Sequence[int]],
    eager: bool = True,
) -> dict[str, Any]:
    """Compile reads followed by forward permutations and their restoration.

    There must be one reader per permutation and at least one child.  All
    permutations have the same positive width n.  Reader entries are -1, 0,
    or 1.  Input sequences are copied and are never mutated.  Child indices
    in the returned segments are zero-based; the one deferred restoration
    has ``child=None`` because it belongs to the whole batch.

    Ports 0..n-1 hold arbitrary dirty inputs; n+i is child i's distinct output
    accumulator, whose initial value may be arbitrary.  Port n+r is T and
    MUST initially be zero.  Each reader adds its linear functional to its
    output before that child's forward permutation.  Eager mode restores
    each child immediately; deferred mode restores only the final product.
    Compatibility of deferred readers with their prefixes is a caller proof
    obligation, not assumed or silently repaired by this compiler.

    ``composed`` is the gather-index list for G_r ... G_1, even in eager mode.
    ``segments`` delimit half-open instruction intervals for separate pricing.
    Pass the returned ``program`` to :func:`execute`.
    """
    if type(eager) is not bool:
        raise ValueError("eager must be bool")
    permutations = [list(permutation) for permutation in perms]
    rows = [list(reader) for reader in readers]
    if not permutations:
        raise ValueError("at least one child permutation is required")
    n = len(permutations[0])
    if n == 0:
        raise ValueError("permutations must have positive width")
    r = len(permutations)
    if len(rows) != r:
        raise ValueError("there must be one reader per permutation")
    expected = list(range(n))
    for i, permutation in enumerate(permutations):
        if len(permutation) != n:
            raise ValueError(f"permutation {i} has the wrong width")
        for port in permutation:
            _integer(port, f"permutation {i} port")
        if sorted(permutation) != expected:
            raise ValueError(f"permutation {i} is not a permutation of 0..n-1")
    for i, row in enumerate(rows):
        if len(row) != n:
            raise ValueError(f"reader {i} has the wrong width")
        for coefficient in row:
            if _integer(coefficient, f"reader {i} coefficient") not in (-1, 0, 1):
                raise ValueError(f"reader {i} coefficient must be -1, 0, or 1")

    program: list[Instruction] = []
    segments: list[dict[str, Any]] = []
    composed = list(range(n))
    temp = n + r
    for i, (permutation, row) in enumerate(zip(permutations, rows)):
        start = len(program)
        for source, coefficient in enumerate(row):
            if coefficient:
                program.append(("add", n + i, source, coefficient))
        segments.append(
            {"kind": "reader", "child": i, "start": start, "stop": len(program)}
        )
        start = len(program)
        _emit_permutation(program, permutation, temp)
        segments.append(
            {"kind": "forward", "child": i, "start": start, "stop": len(program)}
        )
        # If current[j] = original[composed[j]], applying p gives
        # current[p[j]] = original[composed[p[j]]].
        composed = [composed[source] for source in permutation]
        if eager:
            start = len(program)
            _emit_permutation(program, _inverse(permutation), temp)
            segments.append(
                {"kind": "restore", "child": i, "start": start, "stop": len(program)}
            )
    if not eager:
        start = len(program)
        _emit_permutation(program, _inverse(composed), temp)
        segments.append(
            {"kind": "restore", "child": None, "start": start, "stop": len(program)}
        )
    return {
        "program": program,
        "segments": segments,
        "n": n,
        "outputs": r,
        "temp": temp,
        "composed": composed,
    }


def execute(
    program: Iterable[Instruction], initial: Sequence[int]
) -> tuple[list[int], dict[str, int]]:
    """Execute literal source-load/target-add/source-unload on copied integers.

    ADD is an instruction count, not a unit-price primitive: its invoice has
    two source reads, one target read, one target write, and three scalar
    additions/subtractions.  For fixed tape ports s,d, the data-head walk is
    0 -> s -> d -> s -> 0, costing 2*s + 2*abs(d-s) word transitions.  T's
    tape slot is included whenever a compiled swap accesses it.  This routine
    does not know which port is T; its initial and final cleanliness must be
    checked by the caller against the compiler metadata.
    """
    memory = list(initial)
    for i, value in enumerate(memory):
        _integer(value, f"initial scalar {i}")
    invoice = {
        "add_instructions": 0,
        "source_reads": 0,
        "target_reads": 0,
        "target_writes": 0,
        "scalar_additions": 0,
        "tape_word_travel": 0,
    }
    head = 0
    accumulator = 0
    for position, instruction in enumerate(program):
        if not isinstance(instruction, (tuple, list)) or len(instruction) != 4:
            raise ValueError(f"instruction {position} must have four fields")
        operation, destination, source, sign = instruction
        if operation != "add":
            raise ValueError(f"instruction {position} has an unknown operation")
        destination = _integer(destination, "destination")
        source = _integer(source, "source")
        sign = _integer(sign, "sign")
        if not 0 <= destination < len(memory) or not 0 <= source < len(memory):
            raise ValueError(f"instruction {position} port is outside memory")
        if destination == source:
            raise ValueError(f"instruction {position} needs distinct source and target")
        if sign not in (-1, 1):
            raise ValueError(f"instruction {position} sign must be -1 or 1")

        invoice["tape_word_travel"] += abs(source - head)
        head = source
        accumulator += memory[source]
        invoice["source_reads"] += 1
        invoice["scalar_additions"] += 1

        invoice["tape_word_travel"] += abs(destination - head)
        head = destination
        memory[destination] += sign * accumulator
        invoice["target_reads"] += 1
        invoice["target_writes"] += 1
        invoice["scalar_additions"] += 1

        invoice["tape_word_travel"] += abs(source - head)
        head = source
        accumulator -= memory[source]
        invoice["source_reads"] += 1
        invoice["scalar_additions"] += 1
        invoice["tape_word_travel"] += abs(head)
        head = 0
        invoice["add_instructions"] += 1
        if accumulator != 0:
            raise ValueError(f"instruction {position} failed to clean the source register")
    return memory, invoice
