"""Source-bound integer row products, produced by Nick Petalas. Apache-2.0."""

import argparse
import hashlib
import json
from pathlib import Path
from types import ModuleType

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = "research/universal-dirty-phase-identities/"
MAX_BYTES = 1_048_576


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def bounded_read(path):
    with path.open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    require(len(raw) <= MAX_BYTES, "input exceeds one MiB")
    return raw


def source_bytes(root=ROOT):
    manifest = json.loads(bounded_read(HERE / "SOURCES.json"))
    rows = [row for row in manifest["files"] if row["usage"] == "input"]
    require(len(rows) == 14, "expected fourteen source inputs")
    result = {}
    for row in rows:
        name = row["path"]
        require(name.startswith(SOURCE) and ".." not in Path(name).parts,
                "unexpected source path")
        path = root / name
        require(not path.is_symlink(), "source must be a regular file")
        raw = bounded_read(path)
        require(hashlib.sha256(raw).hexdigest() == row["sha256"],
                "source SHA256 mismatch: " + name)
        blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
        require(hashlib.sha1(blob).hexdigest() == row["git_blob"],
                "source Git blob mismatch: " + name)
        require(name not in result, "duplicate source")
        result[name] = raw
    return result


def load_module(name, sources, root=ROOT):
    require(name in ("verify", "check_dense", "test_package"), "unknown entry")
    path = SOURCE + name + ".py"
    module = ModuleType("retained_phase_" + name)
    module.__file__ = str(root / path)
    # Execute precisely the authenticated source bytes, bypassing .pyc reads.
    exec(compile(sources[path], module.__file__, "exec"), module.__dict__)
    return module


def multiply(a, b):
    """Multiply the trusted nonempty rectangular integer matrices of the caller."""
    out = [[0] * len(b[0]) for _ in a]
    for i, row in enumerate(a):
        target = out[i]
        for k, coefficient in enumerate(row):
            if coefficient:
                for j, value in enumerate(b[k]):
                    target[j] += coefficient * value
    return out


def scientific(baseline=False, observer=None):
    sources = source_bytes()
    primary = load_module("verify", sources)
    dense = load_module("check_dense", sources)
    original = dense.multiply
    if observer is not None:
        dense.multiply = observer(original)
    elif not baseline:
        dense.multiply = multiply
    results = []
    for module, receipt in ((primary, "CERTIFICATE.json"),
                            (dense, "DENSE-CHECK.json")):
        result = module.run()
        expected = json.loads(sources[SOURCE + receipt])
        require(canonical(result) == canonical(expected), "scientific receipt mismatch")
        results.append(result)
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", action="store_true")
    args = parser.parse_args()
    print(canonical(scientific(args.baseline)).decode())


if __name__ == "__main__":
    main()
