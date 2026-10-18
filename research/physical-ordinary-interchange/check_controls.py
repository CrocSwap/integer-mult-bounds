"""Rejection controls for source, algebraic provenance and physical ownership."""
from pathlib import Path
import json
import sys
import tempfile
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import source
_loader, padding, _outer = source.activate()
from cardinal_counts import Count
from encoded import atom_width, divide
from physical_words import PhysicalArena
from provenance import Provenance
from records import Tape
from role_parking import transfer
from scratch_pool import ScratchPool
from session import OuterScope, borrowed_tape, sealed_constructors
from words import Arena, BLANK, need


def rejected(function):
    try:
        function()
    except ValueError:
        return
    raise ValueError("negative control accepted")


def run():
    results = []
    read = Path.read_bytes
    with tempfile.TemporaryDirectory() as directory:
        for name in source.ARCHIVES:
            path = source.HERE / "inputs" / (name + ".tar")
            def corrupted(candidate, target=path):
                data = read(candidate)
                return bytes([data[0] ^ 1]) + data[1:] if candidate == target else data
            with patch.object(Path, "read_bytes", corrupted):
                rejected(lambda: source.extract(name, Path(directory)/name))
            results.append("archive corruption: " + name)
    zero, one = Count.literal(0), Count.literal(1)
    rejected(lambda: atom_width(zero))
    rejected(lambda: divide(one, zero))
    zero.close()
    one.close()
    results.extend(("zero original width", "zero divisor"))

    outer, inner = ScratchPool(16), ScratchPool(8)
    scope = OuterScope(outer)
    destination = Tape()
    with sealed_constructors(), scope.installed():
        lease = outer.acquire()
        lease.append(1)
        lease.rewind()
        physical = borrowed_tape(lease)
        need(lease.active and physical is lease.physical, "borrowed view retains outer ownership")
        with scope.suspended():
            rejected(Tape)
            rejected(lambda: Arena(3))
            rejected(lambda: PhysicalArena(4))
            with inner.install():
                temporary = inner.acquire()
                temporary.append(0)
                temporary.rewind()
                temporary.clear()
                inner.empty()
        need(lease.active and lease.read() == 1 and len(outer.live) == 1,
             "inner specialization preserves outer lease")
        need(isinstance(destination, padding.Tape), "padding retains its nominal output type")
        transfer(lease, destination)
        need(lease.active and lease.read() == BLANK, "erasure alone does not release an outer lease")
        lease.clear()
        outer.empty()
    destination.clear()
    results.extend(("sealed Tape", "sealed Arena", "sealed physical bank",
                    "outer lease through inner scope", "explicit final lease release"))

    first, second, output = Tape(), Tape(), Tape()
    for tape in (first, second):
        tape.append(0)
        tape.rewind()
    observer = Provenance(2)
    observer.mark(first)
    observer.cells[(id(second), 1)] = 2
    with observer.installed():
        output.append(second.read())
        output.rewind()
        need(bytes(output.cells) == bytes(first.cells) and observer.masks(output, 1) != (1,),
             "wrong equal-valued origin fails affine provenance")
        output.clear()
        output.append(first.read() ^ first.read())
        output.rewind()
        need(observer.masks(output, 1) == (0,), "cancelling origin is not an independent input")
        output.clear()
        output.append(first.read() ^ 1)
        output.rewind()
        need(observer.masks(output, 1) == (1 ^ observer.constant,), "affine constant remains observable")
    for tape in (first, second, output):
        tape.clear()
    results.extend(("equal-valued wrong origin", "cancelled origin", "affine constant"))
    return dict(controls=results, count=len(results))


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
    print("PASS_ORDINARY_REJECTION_CONTROLS")
