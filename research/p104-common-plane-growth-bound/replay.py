"""Replay two exact common-plane growth bounds on the same fixed sample."""
from hashlib import sha256
from json import loads
from pathlib import Path, PurePosixPath
from subprocess import run
from sys import executable, implementation, version_info

ROOT = Path(__file__).resolve().parent


def unique(pairs):
    values = dict(pairs)
    assert len(values) == len(pairs), "duplicate JSON key"
    return values


def read(name):
    return loads((ROOT / name).read_bytes(), object_pairs_hook=unique)


def main():
    assert __debug__ and implementation.name == "cpython" and version_info[:2] == (3, 12)
    manifest = read("PINS.json")
    files = {f.relative_to(ROOT).as_posix() for folder in ("inputs", "receipts")
             for f in (ROOT / folder).iterdir() if f.is_file()}
    assert set(manifest) == files | {"PROVENANCE.json", "lead.py", "independent.py"}
    for name, digest in manifest.items():
        path = PurePosixPath(name)
        assert not path.is_absolute() and ".." not in path.parts
        assert sha256((ROOT / path).read_bytes()).hexdigest() == digest, name

    results = {}
    for mode in ("lead", "independent"):
        output = run([executable, "-I", "-B", str(ROOT / (mode + ".py"))],
                     check=True, capture_output=True, timeout=65).stdout
        actual = loads(output, object_pairs_hook=unique)
        if mode == "lead":
            for name in ("cut_flow.py", "reverse_inventory.py"):
                assert actual["inputs"].pop(name) == manifest["inputs/" + name]
        assert actual == read("receipts/" + mode.upper() + ".json")
        results[mode] = actual
    lead, ind = results["lead"], results["independent"]
    assert lead["seed_vectors"] == ind["seed_vectors"] == [365,244,327,371]
    assert lead["planes_checked"] == ind["planes_checked"] == 1014
    assert lead["records"] == ind["records"] and all(value == 0 for _, value in lead["records"])
    assert lead["total_planes"] == ind["total_planes"] == 511*510//6 == 43435
    assert ind["untested_planes"] == 42421 and ind["eligible_groups"] == 482 and ind["incident_edges"] == 2292
    assert not lead["capped"] and lead["witness"] is None and lead["max_upper_scaled"] == ind["max_upper_scaled"] == 0
    print("PASS_COMMON_PLANE_GROWTH: 1014 sampled planes, exact upper zero, 42421 untested")


if __name__ == "__main__":
    main()
