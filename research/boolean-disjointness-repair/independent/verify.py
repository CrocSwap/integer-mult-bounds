"""Count each kernel without row reduction over F_2."""

import json
from pathlib import Path


def columns(h, proper):
    masks = range(1, (1 << h) - 1) if proper else range(1 << h)
    return [sum(((u == v) ^ (not (u & v))) << i
                for i, u in enumerate(masks)) for v in masks]


def images(cols):
    # Gray code changes one input bit at each step.
    image = 0
    previous = 0
    for i in range(1 << len(cols)):
        gray = i ^ (i >> 1)
        if i:
            changed = gray ^ previous
            image ^= cols[changed.bit_length() - 1]
        yield gray, image
        previous = gray


def product(cols, value):
    image = 0
    for i, col in enumerate(cols):
        if (value >> i) & 1:
            image ^= col
    return image


rows = []
for h in range(2, 5):
    b = columns(h, proper=True)
    m = columns(h, proper=False)
    ones = (1 << len(b)) - 1
    b_kernel = [x for x, y in images(b) if y == 0]
    m_kernel = [x for x, y in images(m) if y == 0]
    preimages = [x for x, y in images(b) if y == ones]
    assert all(x.bit_count() % 2 == 0 for x in b_kernel)
    assert preimages and all(x.bit_count() % 2 == 1 for x in preimages)
    assert len(m_kernel) == 2 * len(b_kernel)
    assert product(b, ones) == 0
    for i in range(len(b)):
        first = b[i]
        second = product(b, first)
        third = product(b, second)
        assert first ^ second ^ third == ones
        w = (1 << i) ^ first ^ second
        assert product(b, w) == ones
        assert w.bit_count() % 2 == 1
    for size in (len(b_kernel), len(m_kernel)):
        assert size & (size - 1) == 0
    rank_b = len(b) - (len(b_kernel).bit_length() - 1)
    rank_m = len(m) - (len(m_kernel).bit_length() - 1)
    expected = ((1 << (h + 1)) - 2 * (-1) ** h - 3) // 3
    assert rank_b == expected
    assert rank_m == rank_b + 1
    rows.append(dict(h=h, proper_dimension=len(b),
                     inputs_checked_b=1 << len(b),
                     inputs_checked_m=1 << len(m),
                     kernel_size_b=len(b_kernel),
                     kernel_size_m=len(m_kernel), rank_b=rank_b,
                     rank_m=rank_m,
                     maximal_deficit=2 * len(b) - 3 * rank_b))

result = dict(status="PASS", method="Exhaustive input enumeration by Gray code; no Gaussian elimination.",
              scope="Exact checks for h=2,3,4 support the separate proof for all h>=2.", rows=rows)
path = Path(__file__).with_name("RESULT.json")
path.write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
