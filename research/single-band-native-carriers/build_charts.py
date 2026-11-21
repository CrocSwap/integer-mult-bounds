"""Generate only the Clifford charts newly required by the changed native source."""

from functools import cache
from pathlib import Path
import argparse
import gzip
import json
import sys

from strong_complex import digest, load_changed, required_pairs


def build(grade, engine, data):
    sys.path.insert(0, str(engine))
    import clifford_exact
    from raw48 import read_json

    graph, layout = load_changed(data)
    old = read_json(grade / "complex-atlas.json.gz")
    have = {(a, b) for a, b, _ in old["pairs"]}
    needed = required_pairs(graph, layout)

    @cache
    def chart(i):
        return clifford_exact.canonical_frame(9, tuple(graph["frames"][i]))

    extra = []
    for a, b in sorted(needed - have):
        rec = clifford_exact.lower_child(chart(a).adjoint().then(chart(b)))[0]
        extra.append((a, b, rec))
    return extra


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ("grade", "engine", "data", "out"):
        parser.add_argument(key, type=Path)
    args = parser.parse_args()
    result = build(args.grade, args.engine, args.data)
    encoded = json.dumps(result, separators=(",", ":"), sort_keys=True).encode()
    args.out.write_bytes(gzip.compress(encoded, mtime=0))
    print("additional Clifford pairs", len(result), digest(result))
