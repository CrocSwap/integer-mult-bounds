#!/usr/bin/env python3
"""Replay the historical bit-compression screen from its pinned local inputs.

No predecessor file is regenerated in the checkout. This is a provenance and
finite-replay check, not a proof of the full multiplication theorem.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path, PurePosixPath
import platform
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ENTRY = "scripts/audit_bit_compression.py"
CERTIFICATE = "certificates/bit-compression-audit.json"
MANIFEST = HERE / "SOURCES.json"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True).encode("ascii")


def read_json(data):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, f"Duplicate JSON key: {key}")
            result[key] = value
        return result
    return json.loads(data, object_pairs_hook=unique)


def checked_path(root, relative):
    path = PurePosixPath(relative)
    require(path.as_posix() == relative and not path.is_absolute()
            and ".." not in path.parts and "\\" not in relative
            and ":" not in relative, f"Nonlocal input path: {relative}")
    target = root.joinpath(*path.parts)
    require(target.resolve().is_relative_to(root.resolve()),
            f"Input escapes root: {relative}")
    cursor = root
    for part in path.parts:
        cursor = cursor / part
        require(not cursor.is_symlink(), f"Symlink input: {relative}")
    return target


def import_graph(blobs):
    """Conservative static closure, including function-local imports.

    The pinned sources have no relative/dynamic local imports. Only known
    source bytes are parsed; missing modules cannot be added by this scan.
    """
    graph = {}
    for path, data in sorted(blobs.items()):
        if not path.startswith("scripts/") or not path.endswith(".py"):
            continue
        dependencies = set()
        for node in ast.walk(ast.parse(data, filename=path)):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                require(node.level == 0, f"Unexpected relative import in {path}")
                names = [node.module] if node.module else []
            else:
                continue
            for name in names:
                candidate = "scripts/" + name.replace(".", "/") + ".py"
                if candidate in blobs:
                    dependencies.add(candidate)
                else:
                    require(name.split(".")[0] in sys.stdlib_module_names,
                            f"Unpinned local or third-party import: {name} in {path}")
        graph[path] = sorted(dependencies)
    return graph


def validate_inputs(root, manifest):
    require(manifest["entrypoint"] == ENTRY, "Changed entrypoint")
    require(manifest["certificate"] == CERTIFICATE, "Changed reference certificate")
    blobs = {}
    for path, expected in manifest["files"].items():
        data = checked_path(root, path).read_bytes()
        require(digest(data) == expected, f"Source hash mismatch: {path}")
        blobs[path] = data
    require(import_graph(blobs) == manifest["local_import_graph"],
            "Static local import inventory changed")
    local = set(manifest["local_import_graph"])
    require(ENTRY in local, "Missing driver pin")
    reachable, pending = set(), [ENTRY]
    while pending:
        path = pending.pop()
        if path not in reachable:
            reachable.add(path)
            pending.extend(manifest["local_import_graph"][path])
    require(reachable == local, "Disconnected or missing local source")
    upstream = read_json(blobs["upstream/manifest.json"])
    require(upstream["commit"] == manifest["upstream_commit"], "Upstream commit mismatch")
    for relative, info in upstream["files"].items():
        path = "upstream/" + relative
        require(path in blobs and digest(blobs[path]) == info["sha256"],
                f"Missing or changed upstream input: {path}")
    expected = read_json(blobs[CERTIFICATE])
    for path, expected_hash in expected["source_sha256"].items():
        require(path in blobs and digest(blobs[path]) == expected_hash,
                f"Historical source pin mismatch: {path}")
    return blobs, expected


def stage_inputs(destination, blobs):
    for relative, data in blobs.items():
        target = checked_path(destination, relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)


# -I ignores Python environment overrides; -S excludes installed site packages.
# The only added module search directory is this fresh, source-verified copy.
BOOTSTRAP = r'''
import json, pathlib, runpy, sys
root = pathlib.Path(sys.argv[1]).resolve()
sys.path.insert(0, str(root / "scripts"))
runpy.run_path(str(root / "scripts/audit_bit_compression.py"), run_name="__main__")
loaded = {}
for name, module in tuple(sys.modules.items()):
    source = getattr(module, "__file__", None)
    if source:
        source = pathlib.Path(source).resolve()
        if source.is_relative_to(root):
            loaded[name] = source.relative_to(root).as_posix()
(root / "loaded-modules.json").write_text(json.dumps(loaded, sort_keys=True), encoding="utf-8")
'''


def compare_certificate(actual, expected):
    # Preserve every field, including the historical two source hashes. JSON
    # whitespace/key ordering is the only normalization; 1 and true differ.
    require(canonical(actual) == canonical(expected), "Historical certificate payload differs")


def replay(blobs, expected):
    with tempfile.TemporaryDirectory(prefix="bit-compression-provenance-") as directory:
        root = Path(directory)
        stage_inputs(root, blobs)
        # The expected certificate is an input to our comparison, never a
        # pre-existing output that could conceal an omitted producer write.
        (root / CERTIFICATE).unlink()
        started = time.monotonic()
        proc = subprocess.run([sys.executable, "-I", "-S", "-B", "-c", BOOTSTRAP, str(root)],
                              cwd=root, capture_output=True, text=True, encoding="utf-8")
        elapsed = time.monotonic() - started
        require(proc.returncode == 0, f"Historical producer failed:\n{proc.stdout}\n{proc.stderr}")
        require((root / CERTIFICATE).is_file(), "Producer omitted the fresh certificate")
        actual = read_json((root / CERTIFICATE).read_bytes())
        compare_certificate(actual, expected)
        loaded = read_json((root / "loaded-modules.json").read_bytes())
        require(set(loaded.values()) == set(import_graph(blobs)) - {ENTRY},
                "Runtime local imports differ from the static inventory")
        for path, data in blobs.items():
            if path != CERTIFICATE:
                require((root / path).read_bytes() == data, f"Replay modified input: {path}")
        return {"status": "PASS", "seconds": round(elapsed, 6),
                "stdout": proc.stdout.strip().splitlines(),
                "stderr": proc.stderr.strip().splitlines(),
                "loaded_local_modules": loaded,
                "all_certificate_fields_equal": True}


def arithmetic_check(certificate):
    # Import only this contribution's independent implementation, not the
    # historical producer or its arithmetic helpers.
    sys.path.insert(0, str(HERE))
    from independent_arithmetic import check
    return check(certificate)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true",
                        help="check inputs and independent arithmetic; do not claim a fresh producer replay")
    parser.add_argument("--output", type=Path, help="write a new receipt; existing files are refused")
    args = parser.parse_args()
    require(not sys.flags.optimize, "Historical assertions must remain enabled")
    if args.output:
        require(not args.output.exists(), "Receipt path already exists")
    manifest = read_json(MANIFEST.read_bytes())
    blobs, expected = validate_inputs(ROOT, manifest)
    result = {"status": "INPUTS_AND_ARITHMETIC_ONLY" if args.check_only else "PASS",
              "base_commit": manifest["base_commit"], "assignment_seed": 99,
              "source_manifest_sha256": digest(MANIFEST.read_bytes()),
              "python": platform.python_version(), "platform": platform.platform(),
              "input_count": len(blobs), "local_python_files": len(import_graph(blobs)),
              "historical_source_pin_count": len(expected["source_sha256"]),
              "historical_certificate_sha256": digest(blobs[CERTIFICATE]),
              "canonical_certificate_sha256": digest(canonical(expected)),
              "independent_arithmetic": arithmetic_check(expected)}
    if not args.check_only:
        print("Replaying unchanged historical producer in an isolated directory...", flush=True)
        result["producer_replay"] = replay(blobs, expected)
    output = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(output)
    print(f"{result['status']}: {len(blobs)} pinned inputs; "
          f"{len(import_graph(blobs))} local Python files; no new kappa.")


if __name__ == "__main__":
    main()
