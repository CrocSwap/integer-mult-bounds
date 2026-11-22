"""Replay both halves of every split through the literal native call on zero rows."""

from upstream import HERE, install

_, _, _, source = install()
from check_strong_raw_word import Axes, Field
from periodic import Job
from raw48 import ComplexRaw
from retimed_supplier import Raw, source_ranks
from strong_complex import artifacts, word


class Original(Field):
    def __init__(self, stock):
        super().__init__(stock)
        self.writes = 0

    def replace(self, other):
        super().replace(other)
        self.writes += 1


def check():
    a = artifacts(source / "research/grade14-native-realization", HERE / "inputs")
    w = word(a.graph, a.layout)
    sizes, paid = source_ranks(w)
    stock = [0, 0]
    fields = {i: Original(stock) for i in range(len(sizes))}
    inputs = [Job(i, range(2 * k)) for i, k in enumerate(sizes)]
    machine = ComplexRaw(a, fields, Axes(), low=0, bundle=1, slots=2448)
    # A zero Clifford field stays zero under every phase and permutation. The
    # full raw iterator still issues the same true chart, scale and move calls.
    calls = 0
    it = Raw(w, machine).native(inputs, 2)
    for grade in paid:
        request = next(it)
        assert request.owner in fields and len(request.axes) == 2 * grade
        assert len(set(request.axes)) == len(request.axes)
        calls += 1
    assert next(it, None) is None and len(fields) == len(inputs)
    assert stock[0] == len(inputs)
    assert set(fields) == set(range(len(inputs)))
    assert all(f.live and f.writes and f.data is None for f in fields.values())
    assert 2*sum(sizes) == 13440384 and sum(f.writes for f in fields.values()) == 143616
    print("original output owners, selected axes, physical writes", len(fields), 2*sum(sizes), sum(f.writes for f in fields.values()))
    for owned in fields.values():
        owned.retire()
    assert stock[0] == 0
    print("complete two-column raw path", len(sizes), calls, stock[1])


if __name__ == "__main__":
    check()
