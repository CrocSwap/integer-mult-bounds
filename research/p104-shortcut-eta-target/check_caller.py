"""Recompute the chronological owners, signed ranks and exact context width."""

from fractions import Fraction
import json
from pathlib import Path
import sys


def audit(runtime, grid):
    sys.path.insert(0, str(runtime))
    from upstream import install

    grade = install()[-1] / "research/grade14-native-realization"
    from check_strong_complex import caller
    from strong_complex import load_changed, GRID
    from installations import ENTRY, TERMINAL

    data = runtime / "inputs"
    graph, layout = load_changed(data)
    assert grid["grid"] == GRID
    out = caller(grade, graph, layout, data, Fraction(grid["peak"]))
    assert (out["targets"], out["paid"]) == (52608, 281328), (
        out["targets"],
        out["paid"],
    )
    assert out["per_context_dyadic"] <= 148 and out["per_context_mass"] <= 436
    for p in ENTRY, TERMINAL:
        assert out["context_guard"] * 128 * (p.complex_log + 1) ** 2 < 2 ** min(
            p.complex_log, 1024
        )
    return out


if __name__ == "__main__":
    if not __debug__:
        raise ValueError("Enable assertions")
    print(
        json.dumps(
            audit(
                Path(sys.argv[1]).resolve(), json.loads(Path(sys.argv[2]).read_bytes())
            ),
            sort_keys=True,
        )
    )
