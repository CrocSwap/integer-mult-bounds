"""Replay both halves of every split through the literal native call on zero rows."""

from upstream import HERE, install

_, _, _, source = install()
from check_strong_raw_word import Axes, Field
from periodic import Job
from raw48 import ComplexRaw
from retimed_supplier import Raw, source_ranks
from strong_complex import artifacts, word


def check():
    a = artifacts(source / "research/grade14-native-realization", HERE / "inputs")
    w = word(a.graph, a.layout)
    sizes, paid = source_ranks(w)
    stock = [0, 0]
    fields = {i: Field(stock) for i in range(len(sizes))}
    inputs = [Job(i, tuple(range(2 * k))) for i, k in enumerate(sizes)]
    machine = ComplexRaw(a, fields, Axes(), low=0, bundle=1, slots=306)
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
    for owned in fields.values():
        owned.retire()
    assert stock[0] == 0
    print("complete two-column raw path", len(sizes), calls, stock[1])


if __name__ == "__main__":
    check()
