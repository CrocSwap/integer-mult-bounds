"""Test a non-stopped paid packet and a complete raw-compiler root on opaque records."""

import argparse
from io import BytesIO
from pathlib import Path
import sys

from check_module_atoms import expected_packet, payload


def check(predecessor):
    sys.path.insert(0, str(predecessor.resolve()))
    from growing_binary import Weighted
    from module_atoms import balanced_widths
    from streaming_routes import cold_swap_tape

    prior = {}

    def charged(s, t, w, p, g, block):
        prior[w] = prior.get(w, 0) + 1
        cold_swap_tape(s, t, w, p, g, block)

    core = Weighted(2, balanced_widths(1), charged)
    assert core.owners == 1 and core.stock == 48
    dims = (48, 3, 3, 3, 3, 3, 3, 3, 3)
    data = payload(48 * 3**8)
    got = BytesIO()
    low = (1, 1, 1, 2)
    core.exposed_leaf(BytesIO(data), got, low, 2, 48, 1, 1, 4, lambda row, i: (1, 2, 2, 1)[i])

    def direct(future, *digits):
        h = list(digits[:4])
        t = list(reversed(digits[4:]))
        a = (1, 2, 2, 1)
        for j in range(2):
            # g E00 g^-1 has both rows (2,2) for this low over F3.
            v = 2 * sum(t[i] - a[i] * h[i] for i in (j, 2 + j))
            for i in (j, 2 + j):
                h[i] = (h[i] + a[i] * v) % 3
                t[i] = (t[i] - v) % 3
        return (future, *h, *reversed(t))

    assert got.getvalue() == expected_packet(data, dims, direct)
    assert core.last_storage[0] == 15
    print(
        "non-stopped two-column leaf",
        len(data) // 4,
        "records",
        prior,
        "spools/moves/high-water",
        core.last_storage,
        flush=True,
    )

    dims = (48, 2, 3, 3, 3, 2, 3, 3, 3)
    data = payload(48 * 2 * 2 * 3**6)
    got = BytesIO()
    prior.clear()
    core.body_ordinary(BytesIO(data), got, 3, 48, 2, 2, 4)
    assert got.getvalue() == expected_packet(
        data,
        dims,
        lambda row, old, h0, h1, h2, g, t0, t1, t2: (row, old, t0, t1, t2, g, h0, h1, h2),
    )
    assert core.last_storage[0] == 15
    print(
        "full coarse return, odd native remainder and two-F wrapper",
        len(data) // 4,
        "records",
        prior,
        "spools/moves/high-water",
        core.last_storage,
        flush=True,
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("predecessor", type=Path)
    check(p.parse_args().predecessor)
