"""Independent root-generated supports versus hyperplanes of the bulk span."""

import json
from itertools import combinations

from common import basis, geometry, require, span


def compute():
    g = geometry()
    roots, _, _, coordinates = g.root_data()
    labels = tuple(
        1 | sum((int(x) % 2) << (j + 1) for j, x in enumerate(c)) for c in coordinates
    )
    a = roots[0]
    b = next(r for r in roots if not g.dot(a, r))
    axis = tuple(j for j, r in enumerate(roots) if g.dot(a, r) and not g.dot(b, r))
    bulk = tuple(j for j in axis if roots[j] != a)
    mapping = {x: j for j, x in enumerate(span(tuple(labels[i] for i in bulk)))}
    high = set()
    for normal in range(1, 128):
        mask = sum(
            1 << k
            for k, j in enumerate(axis)
            if labels[j] in mapping
            and not (mapping[labels[j]] & normal).bit_count() % 2
        )
        if mask.bit_count() > 16:
            high.add(mask)
    require(
        len(high) == 16 and {x.bit_count() for x in high} == {20},
        "independent high-six inventory",
    )
    # A support with >=9 leading-one labels has rank>=5. Every rank-five
    # support therefore has a five-root basis among these bounded subsets.
    closures = set()
    subsets = 0
    for selected in combinations(tuple(labels[j] for j in axis), 5):
        subsets += 1
        generators = basis(selected)
        if len(generators) != 5:
            continue
        generated = set(span(generators))
        mask = sum(1 << k for k, j in enumerate(axis) if labels[j] in generated)
        if mask.bit_count() >= 9:
            closures.add(mask)
    require(subsets == 237336, "all five-root subsets")
    maximum = max((left | right).bit_count() for left in closures for right in high)
    require(maximum == 26, "independent critical pair union")
    return {
        "status": "PASS_INDEPENDENT_CUT33_PAIR_BOUND",
        "five_root_subsets": subsets,
        "critical_five_closures": len(closures),
        "high_six_closures": len(high),
        "union_maximum": maximum,
        "other_cases_upper": 28,
        "limits": "outside-bulk six-spaces covered by primary complete enumeration",
    }


if __name__ == "__main__":
    print(json.dumps(compute(), sort_keys=True))
