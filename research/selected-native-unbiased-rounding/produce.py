"""Read the source word and run both unchanged native representations."""

import gzip
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main():
    if not __debug__:
        raise RuntimeError("source assertions must remain enabled")
    for item in json.loads((HERE / "SOURCES.json").read_text())["files"]:
        if item["usage"] == "input":
            if hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest() != item["sha256"]:
                raise ValueError("source mismatch: " + item["path"])
    word = json.loads(gzip.decompress((ROOT / "research/p104-helper470-twin-rung-removal/WORD.json.gz").read_bytes()))
    first = next((j, e) for j, e in enumerate(word["program"]) if e[0] == "MOVE")
    if first != (9896, ["MOVE", 236, 3, 7, False]) or word["frames"][3] != [] or word["frames"][7] != [21]:
        raise ValueError("selected native boundary changed")
    source = ROOT / "research/staged544-mixed-fourth-entry/native/vendor/native/new/code/borrow"
    sys.path.insert(0, str(source))
    sys.path.insert(0, str(source / "vendor/clifford"))
    import bw_gauss
    from clifford_exact import canonical_frame, lower_child
    recipe, compiled = lower_child(canonical_frame(9, [21]))
    if recipe["rank"] != 1:
        raise ValueError("the selected MOVE is not rank one")
    real, imag, exponent = bw_gauss.frame(bw_gauss.eye(9), [21], 9)
    if exponent != 1:
        raise ValueError("unexpected oracle denominator")
    for j in range(512):
        values, exp = compiled.zero_state(j)
        if any((a * 2 != int(real[i, j]) * (1 << exp) or
                b * 2 != int(imag[i, j]) * (1 << exp))
               for i, (a, b) in enumerate(values)):
            raise ValueError("compiler and coordinate oracle disagree")
    out = Path(sys.argv[1])
    np.savez(out / "oracle.npz", real=real, imag=imag)
    (out / "source.json").write_text(json.dumps({
        "event_index": first[0], "event": first[1], "frames": [[], [21]],
        "word_events": len(word["program"]), "recipe": recipe,
        "assertions_enabled": __debug__, "oracle_columns": 512,
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()
