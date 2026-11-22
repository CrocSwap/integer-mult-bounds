"""Compare every chronological tag to the independently loaded caller and graph implementation."""

import band_product as bp
from strong_complex import word

sup = bp.production_supplier(19000, 10**21)
atlas = sup.physical
ref = word(atlas.graph, atlas.layout)
assert sup.word.ambient == ref.ambient == 153
for name in ("targets", "paid"):
    left = getattr(sup.word, name)
    right = getattr(ref, name)
    assert len(left) == len(right)
    assert all(a == b for a, b in zip(left, right, strict=True))
    assert all(a == left[i] for i, a in enumerate(right))
    assert tuple(left.ranks()) == tuple(x.rank for x in right)
    assert left[-2:] == tuple(right[-2:])
    for i in (len(left), -len(left) - 1):
        try:
            left[i]
        except IndexError:
            pass
        else:
            raise AssertionError("invalid port ordinal")
    unique = {id(entries): len(entries) for _, entries in left.segments}
    print(
        name,
        "emitted",
        len(left),
        "distinct stored roles",
        sum(unique.values()),
        "segments",
        len(left.segments),
    )
values = [c for row in sup.physical.forms.values() for _, c in row]
assert len({id(x) for x in values}) == len(set(values))
print(
    "exact donor coefficients",
    len(values),
    "distinct immutable values",
    len(set(values)),
)
