"""Run the complete binary emitter on the constant-address subspace of each owner."""

from collections import Counter
from periodic import Job
from raw_binary_stage import binary_word
from strong_binary import StrongBinarySource, fixed_binary_charts


class ConstantFields:
    """Each integer is a GF(2) form on independent external data words."""

    def __init__(self, labels):
        self.dimension = 134
        self.data = {i: 1 << i for i in range(labels)}
        self.next = labels
        self.counts = Counter()

    def zero(self):
        owner = self.next
        self.next += 1
        self.data[owner] = 0
        return owner

    def clone(self, parent):
        owner = self.zero()
        self.data[owner] = self.data[parent]
        return owner

    def route(self, owner, word):
        assert owner in self.data
        self.counts["routes"] += 1
        self.counts["elementary_steps"] += len(word)

    def xor(self, dest, src):
        self.data[dest] ^= self.data[src]

    def swap(self, left, right):
        self.data[left], self.data[right] = self.data[right], self.data[left]

    def retire(self, owner, require_zero=False):
        former = self.data.pop(owner)
        if require_zero:
            assert not former


def check():
    source = binary_word()
    n = len(source.targets)
    bank = ConstantFields(n)
    jobs = [Job(i,tuple(range(r))) for i,r in enumerate(source.targets)]
    issued = 0
    for job in source.native(jobs, 1, StrongBinarySource(bank)):
        assert job.owner in bank.data and len(job.axes) == source.paid[issued]
        issued += 1
    assert issued == 104652 and len(bank.data) == n
    assert all(bank.data[i] == (1 << i) for i in range(n))
    charts, ports = fixed_binary_charts()
    print("binary constant-address physical emitter", n, issued, len(charts), len(ports), dict(bank.counts))


if __name__ == "__main__":
    check()
