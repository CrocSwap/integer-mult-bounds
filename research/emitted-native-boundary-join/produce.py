"""Run the unchanged source compiler and emit an independent matrix oracle."""

import gzip
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main():
    if not __debug__:
        raise RuntimeError("the predecessor compiler requires assertions")
    output = Path(sys.argv[1])
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    for item in manifest["files"]:
        if item["usage"] == "input":
            data = (ROOT / item["path"]).read_bytes()
            if hashlib.sha256(data).hexdigest() != item["sha256"]:
                raise ValueError("source mismatch: " + item["path"])
    predecessor = ROOT / "research/staged544-mixed-fourth-entry"
    source = predecessor / "native/vendor/native/new/code/borrow"
    sys.path.insert(0, str(source))
    import bw_adapters
    import bw_gauss as oracle
    from clifford_exact import canonical_frame, lower_child

    compressed = (predecessor / "evidence/NATIVE-CANONICAL-base.json.gz").read_bytes()
    canonical = json.loads(gzip.decompress(compressed))
    retained = json.loads((predecessor / "evidence/NATIVE-LOCAL-base.json").read_text())
    with tempfile.TemporaryDirectory(prefix="native-boundary-emitter-") as folder:
        directory = Path(folder)
        (directory / "CANONICAL-WORD.json.gz").write_bytes(compressed)
        subprocess.run(
            [sys.executable, "-I", "-B", str(source / "bw_emit.py"), str(directory)],
            check=True, capture_output=True, text=True, timeout=120,
        )
        programs = json.loads(gzip.decompress((directory / "LOCAL-PROGRAMS.json.gz").read_bytes()))
    forward = programs["forward"]
    digest = hashlib.sha256(json.dumps(forward, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if digest != retained["forward"]["sha256"] or len(forward) != retained["forward"]["events"]:
        raise ValueError("emitted forward stream differs from retained source")
    events = forward[6683:6686]
    if events != [
        ["warp", ["L", 83], 52, 85, 137],
        ["climb", "A", 126, 0, 137, 1],
        ["scalar", ["add", ["L", 126], ["L", 83], -1, 2], 137],
    ]:
        raise ValueError("the claimed source boundary changed")
    frames = canonical["frames"]
    columns = next(w["G_columns"] for w in canonical["warps"] if w["op"] == 52)
    first = canonical_frame(9, frames[85])
    last = canonical_frame(9, frames[137])
    warp, _ = lower_child(first.adjoint().then(bw_adapters.Kop(columns)).then(last))
    child, _ = lower_child(last)
    if warp["rank"] != 0 or child["rank"] != 1:
        raise ValueError("unexpected native rank")

    # This oracle uses coordinate matrices, not the compiler's serialized recipes.
    initial_source = oracle.frame(oracle.eye(9), frames[85], 9)
    final_source = oracle.frame(
        oracle.apply_mono(oracle.eye(9), oracle.monomial(columns, 9)), frames[137], 9
    )
    final_target = oracle.frame(oracle.eye(9), frames[137], 9)
    arrays = {}
    for name, (real, imag, exponent) in [
        ("initial_source", initial_source), ("final_source", final_source),
        ("final_target", final_target),
    ]:
        if max(int(np.max(np.abs(real))), int(np.max(np.abs(imag)))) > 4:
            raise ValueError("oracle exceeded its exact small-integer bound")
        arrays[name + "_real"] = real
        arrays[name + "_imag"] = imag
        arrays[name + "_exp"] = np.array(exponent, dtype=np.int64)
    np.savez(output / "oracle.npz", **arrays)
    (output / "native.json").write_text(json.dumps({
        "events": events, "forward_events": len(forward), "forward_sha256": digest,
        "frames": {str(i): frames[i] for i in (0, 85, 137)},
        "G_columns": columns, "warp": warp, "child": child,
        "predecessor_assertions_enabled": __debug__,
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()
