"""Reconstruct the unchanged native tariff from the installed #8072 runtime."""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys

WORD = "38d2b3a2311a9ba5fee091cc7aa204c7ed95651aec95d75184b2391df090cbfb"
LAYOUT = "0ce3f9e383fc4bfdd22612b9e34fc9759d97204215937b82d23aec2cedd9b8ee"
HEAD = "75f7e1c44f48c43983016bcf8878c4d9e5e87c62"


def capture(runtime):
    pins = {
        "strong_complex.py": "b0f18924be837173ccbbd1b7814a7a9a27228d68ff0dcbaf44a90a2065d0574c",
        "inputs/triangular/inputs/retained.json": "4d0dd81eb156c97403d752a3dc654d85a93b0284aed8cfa5eed840259f6abd88",
        "inputs/triangular/inputs/retained.tar.gz": "77742c09b088f27e8742c3fad7b7148d3397e4d51b95312106f39a8970165903",
    }
    for path, expected in pins.items():
        assert sha256((runtime / path).read_bytes()).hexdigest() == expected, path
    sys.path.insert(0, str(runtime))
    from strong_complex import digest, load_changed
    from upstream import install
    src = install()[-1] / "research/grade14-native-realization/retained"
    graph, layout = load_changed(runtime / "inputs")
    assert (digest(graph), digest(layout)) == (WORD, LAYOUT)
    public = set(layout["live"]) | {x + 112 for x in layout["live"]}
    public.update(layout["hosted"]["X2"])
    public.update(layout["hosted"]["Y2"])
    assert len(public) == 400
    dimensions = list(map(len, graph["frames"]))
    paid = Counter(abs(dimensions[a] - dimensions[b]) for _, a, b in graph["moves"])
    productive = Counter(dimensions[b] - dimensions[a] for i, (a, b) in
                         enumerate(zip(graph["initial"], graph["final"], strict=True)) if i not in public)
    assert min(paid) >= 1 and min(productive) >= 1
    paths = ("mixed_caller.py", "closed_caller.py", "mixed_grid.py",
             "data/CALLER.json.gz", "data/CONJUGATE-CALLER.json.gz")
    return {
        "head": HEAD, "word_sha256": WORD, "layout_sha256": LAYOUT,
        "public_slots": len(public), "native_paid_per_invocation": dict(sorted(paid.items())),
        "native_productive_per_invocation": dict(sorted(productive.items())),
        "caller_source_sha256": {n: sha256((src / n).read_bytes()).hexdigest() for n in paths},
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: capture_native.py PATH_TO_INSTALLED_8072_RUNTIME")
    print(json.dumps(capture(Path(sys.argv[1]).resolve()), indent=2))
