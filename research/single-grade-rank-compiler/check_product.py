"""Run the raw product, specialization, splits and full-rank compiler together."""

from collections import Counter
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_schedule import Arrays, need, reject
from product import Native, specialize
from schedule import expand


def raw(machine, owners, c):
    # Independent outputs have ranks one and three. The second travels through an owned bank.
    x, y = owners
    tmp = machine.zero()
    machine.add(tmp, y, 1)
    machine.add(x, tmp, 1)
    first = tuple(range(c))
    other = tuple(range(c, 3*c))
    yield x, first
    yield tmp, first
    machine.add(x, tmp, -1)
    yield tmp, other
    machine.fields[y], machine.fields[tmp] = machine.fields[tmp], machine.fields[y]
    del machine.fields[tmp]


class ProductArrays(Arrays):
    def __init__(self, width, n, lift, program, fault):
        super().__init__(width, n, lift)
        self.program = program
        self.fault = fault
        self.discarded = 0
        self.allocations = 0
        self.reused = None

    def zero(self):
        idx = self.next_field
        self.next_field += 1
        self.fields[idx] = {}
        self.allocations += 1
        if self.fault == "alias":
            if self.reused is None:
                self.reused = idx
            return self.reused
        return idx

    def retire_zero(self, idx):
        need(not self.fields[idx], "a discarded target had an arbitrary-input dependency")
        del self.fields[idx]
        self.discarded += 1

    def native(self, owners, columns):
        yield from self.program(self, owners, columns)


def check(n, lift, fault=None):
    def changed_raw(machine, owners, c):
        yield from raw(machine, owners, c)
        if fault == "leak":
            x, y = owners
            machine.add(x, y, 1)
    source = Native(4, (1, 3), (1, 1, 2), changed_raw)
    word, native = specialize(source, {"1": 1, "3": 1}, 2)
    need((word.ambient, word.grade, word.roles) == (16, 3, 2), "product grade and actual role count")
    need(Counter(word.paid) == {1: 4, 2: 6}, "one split on the rank-four product")
    machine = ProductArrays(word.root_width(n), n, lift, native, fault)
    expand(word, n, list(range(machine.width)), machine)
    machine.check()
    need(machine.leaves == machine.width * word.leaves_per_array(n), "complete raw-to-root bill")
    need(machine.discarded > 0 and machine.allocations > machine.discarded, "owned fields executed")
    return machine.discarded, machine.leaves


if __name__ == "__main__":
    runs = [check(n, f) for n in (16, 17, 23, 32, 35) for f in (1, 2)]
    reject(lambda: check(17, 1, "alias"))
    reject(lambda: check(17, 1, "leak"))
    source = Native(4, (1, 3), (1, 1, 2), raw)
    single, _ = specialize(source, {"1": 0, "3": 2}, 2)
    need((single.grade, single.roles) == (9, 1), "zero-count grades in a serialized type")
    for bad in ({"1": 0}, {"3": -1}, {"03": 1}, {3: 1, "3": 1}, {"3": True}):
        reject(lambda: specialize(source, bad, 1))
    print("PASS_RAW_TO_ROOT cases=10 discarded=" + str(sum(x for x, _ in runs))
          + " paid_leaves=" + str(sum(y for _, y in runs)) + " mutations=7")
