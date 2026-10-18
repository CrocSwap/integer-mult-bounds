#!/usr/bin/env python3
"""Opt-in source-bound replay; leave all original generators untouched."""
import argparse
from contextlib import contextmanager
from hashlib import sha256
import importlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MANIFEST_SHA256 = "e2be1e7c88e7a6814ec726bd5cd397af261514edac960d1d8ae6590c39c9e608"
COMPATIBILITY_SHA256 = "a5f102c0b90783698d2912fed9ddeb3a6987fd414fb7c7adffbe638cd98bde7a"
COMPATIBILITY_UPSTREAM = "ffbd90dd90dbe0055464f3a1411b25a3a4fdc6b8"
COMPATIBILITY_PATHS = frozenset(("scripts/audit_fused_block.py",
                                 "scripts/exclusion_circuit.py",
                                 "scripts/shared_point_circuit.py"))
sys.path.insert(0, str(HERE))
from cached_xor import CachedXorPermuter


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2) + "\n").encode("utf-8")


def check_sources():
    data = (HERE / "SOURCES.json").read_bytes()
    require(sha256(data).hexdigest() == MANIFEST_SHA256, "Source manifest mismatch")
    manifest = json.loads(data)
    require(manifest["base_commit"] == "2921874911956718fcaaaf9396fe8267b3cfa9f0",
            "Unexpected research base")
    # Preserve the original scientific manifest. Only these three transitive
    # imports use explicitly reviewed current-main bytes; no core/fixture override.
    data = (HERE / "COMPATIBILITY.json").read_bytes()
    require(sha256(data).hexdigest() == COMPATIBILITY_SHA256,
            "Compatibility manifest mismatch")
    compatibility = json.loads(data)
    require(compatibility["upstream_commit"] == COMPATIBILITY_UPSTREAM
            and compatibility["original_manifest_sha256"] == MANIFEST_SHA256,
            "Unexpected compatibility baseline")
    require(set(compatibility["files"]) == COMPATIBILITY_PATHS,
            "Unexpected compatibility paths")
    for relative, record in compatibility["files"].items():
        require(record["original"] == manifest["files"][relative],
                "Compatibility predecessor mismatch: " + relative)
        manifest["files"][relative] = record["current"]
    for relative, record in manifest["files"].items():
        path = (ROOT / relative).resolve()
        require(path.is_relative_to(ROOT), "Source escapes repository")
        require(sha256(path.read_bytes()).hexdigest() == record["sha256"],
                "Source pin mismatch: " + relative)
    for relative, record in manifest["fixtures"].items():
        require(sha256((HERE / relative).read_bytes()).hexdigest() == record["sha256"],
                "Fixture pin mismatch: " + relative)
    return manifest


def load_original():
    check_sources()  # Reject changed source before importing it.
    sys.path.insert(0, str(ROOT / "scripts"))
    audit = importlib.import_module("audit_cube_cores")
    core = importlib.import_module("experiments.cube_core_family")
    return audit, core


@contextmanager
def backend(core, name, coverage=None):
    original = core.xor_permute
    fast = CachedXorPermuter()  # Fresh bounded lifetime for each replay.
    require(name in ("original", "cached", "differential"), "Unknown backend")

    def differential(bits, index, n):
        expected = original(bits, index, n)
        actual = fast(bits, index, n)
        require(actual == expected, f"Row mismatch: n={n}, index={index}")
        if coverage is not None:
            coverage["rows"] += 1
            coverage["coefficients"] += n
        return actual

    if name != "original":
        core.xor_permute = fast if name == "cached" else differential
    try:
        yield
    finally:
        core.xor_permute = original


def run(case, name, coverage=None):
    audit, core = load_original()
    with backend(core, name, coverage):
        if case == "historical":
            value = audit.serializable(audit.certificate())
            expected = ROOT / "certificates/cube-core-family.json"
        elif case == "t6":
            # Supported historical input and UNCHANGED default stopping rule.
            value = core.quadratic_rank_screen(6, maximum_rows=4096)
            expected = HERE / "EXPECTED-T6.json"
        else:
            raise ValueError("Unknown case")
    payload = canonical(value)
    require(payload == expected.read_bytes(), "Complete receipt mismatch: " + case)
    return payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=("historical", "t6"), default="historical")
    parser.add_argument("--backend", choices=("original", "cached", "differential"),
                        default="cached")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    coverage = {"rows": 0, "coefficients": 0}
    payload = run(args.case, args.backend, coverage)
    if args.output:
        with args.output.open("xb") as stream:
            stream.write(payload)
    print(f"PASS_CUBE_XOR_REPLAY case={args.case} backend={args.backend} "
          f"receipt_sha256={sha256(payload).hexdigest()}")
    if args.backend == "differential":
        print(json.dumps(coverage, sort_keys=True))


if __name__ == "__main__":
    main()
