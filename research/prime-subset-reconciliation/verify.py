#!/usr/bin/env python3
"""Close historical prime-subset provenance and independently replay its scope.

Source-closure/isolation pattern follows woklerx's PR970 package, with
attribution in README.md. New harmonic arithmetic is in independent.py.
OpenAI Codex for the requesting contributor; substantial AI assistance.
Apache-2.0. No new multiplication exponent or full-theorem proof.
"""
import argparse
import ast
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from independent import check_historical, exclusion, require

ENTRY = "scripts/audit_prime_subset_limits.py"
REFERENCE = "certificates/prime-subset-limits.json"


def read_json(data):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "Duplicate JSON key: " + key)
            result[key] = value
        return result
    return json.loads(data, object_pairs_hook=unique)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True).encode("ascii")


def checked_path(root, relative):
    name = PurePosixPath(relative)
    require(name.as_posix() == relative and not name.is_absolute()
            and ".." not in name.parts and "\\" not in relative
            and ":" not in relative, "Nonlocal source path")
    result = root.joinpath(*name.parts)
    require(result.resolve().is_relative_to(root.resolve()), "Escaping source path")
    cursor = root
    for part in name.parts:
        cursor /= part
        require(not cursor.is_symlink(), "Symlink source path")
    return result


def import_graph(blobs):
    graph = {}
    for path, data in sorted(blobs.items()):
        if not path.startswith("scripts/") or not path.endswith(".py"):
            continue
        dependencies = set()
        for node in ast.walk(ast.parse(data, filename=path)):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                require(node.level == 0, "Unexpected relative import")
                names = [node.module] if node.module else []
            else:
                continue
            for name in names:
                candidate = "scripts/" + name.replace(".", "/") + ".py"
                if candidate in blobs:
                    dependencies.add(candidate)
                else:
                    require(name.split(".")[0] in sys.stdlib_module_names,
                            "Unpinned local or third-party import: " + name)
        graph[path] = sorted(dependencies)
    return graph


def validate_inputs(root, manifest):
    require(manifest["entrypoint"] == ENTRY and manifest["certificate"] == REFERENCE,
            "Changed producer or certificate")
    blobs = {}
    for path, expected in manifest["files"].items():
        data = checked_path(root, path).read_bytes()
        require(sha256(data).hexdigest() == expected, "Source hash mismatch: " + path)
        blobs[path] = data
    graph = import_graph(blobs)
    require(graph == manifest["local_import_graph"], "Local import closure differs")
    visited, pending = set(), [ENTRY]
    while pending:
        path = pending.pop()
        if path not in visited:
            visited.add(path)
            pending.extend(graph[path])
    require(visited == set(graph), "Disconnected source inventory")
    upstream = read_json(blobs["upstream/manifest.json"])
    require(upstream["commit"] == manifest["upstream_commit"], "Upstream pin differs")
    for path, info in upstream["files"].items():
        full = "upstream/" + path
        require(full in blobs and sha256(blobs[full]).hexdigest() == info["sha256"],
                "Unpinned upstream input: " + full)
    reference = read_json(blobs[REFERENCE])
    require(reference["upstream_commit"] == upstream["commit"], "Certificate upstream differs")
    for path, expected in reference["source_sha256"].items():
        require(path in blobs and sha256(blobs[path]).hexdigest() == expected,
                "Historical source hash differs")
    return blobs, reference


RUNNER = '''import json, runpy, sys
from pathlib import Path
root = Path(__file__).resolve().parent
sys.path.insert(0, str(root / "scripts"))
runpy.run_path(str(root / "scripts/audit_prime_subset_limits.py"), run_name="__main__")
local = sorted({Path(m.__file__).resolve().relative_to(root).as_posix()
    for m in list(sys.modules.values()) if getattr(m, "__file__", None)
    and Path(m.__file__).resolve().is_relative_to(root / "scripts")})
print("LOCAL_IMPORTS=" + json.dumps(local))
'''


def replay(blobs):
    """Run only pinned inputs; the reference output is absent before execution."""
    with tempfile.TemporaryDirectory(prefix="prime subset replay ") as temp:
        root = Path(temp)
        for path, data in blobs.items():
            if path == REFERENCE:
                continue
            target = checked_path(root, path)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        (root / "certificates").mkdir(exist_ok=True)
        runner = root / "runner.py"
        runner.write_text(RUNNER, encoding="utf-8")
        process = subprocess.run([sys.executable, "-I", "-S", "-B", str(runner)],
                                 cwd=root, capture_output=True, text=True,
                                 encoding="utf-8", timeout=90)
        require(process.returncode == 0, "Historical replay failed: " + process.stderr)
        lines = [line for line in process.stdout.splitlines() if line.startswith("LOCAL_IMPORTS=")]
        require(len(lines) == 1, "Missing runtime import inventory")
        local = read_json(lines[0].split("=", 1)[1])
        require(set(local) <= set(import_graph(blobs)), "Runtime imported unpinned local code")
        require(process.stdout.startswith("PASS common-subset prime-power family"),
                "Historical success marker absent")
        result = read_json(checked_path(root, REFERENCE).read_bytes())
        return result, local


def serialization_control(blobs, reference, manifest):
    """Concrete incomplete-binding control; never changes checkout inputs."""
    path = "scripts/prepare_layers.py"
    original = blobs[path]
    needle = b"        return str(value)"
    require(original.count(needle) == 1, "Serialization control source changed")
    changed = dict(blobs)
    changed[path] = original.replace(needle, b"        return str(value + 1)")
    require(path not in reference["source_sha256"], "Control helper is already historically pinned")
    require(all(sha256(changed[p]).hexdigest() == digest
                for p, digest in reference["source_sha256"].items()),
            "Control invalidated a historical source pin")
    require(sha256(changed[path]).hexdigest() != manifest["files"][path],
            "Complete source binding did not detect control")
    corrupted, _ = replay(changed)
    from fractions import Fraction
    require(Fraction(corrupted["envelope"]["target"])
            - Fraction(reference["envelope"]["target"]) == 1,
            "Serialization corruption was not emitted")
    require(corrupted["source_sha256"] == reference["source_sha256"]
            and corrupted["status"] == reference["status"],
            "Control changed the historical success/source fields")
    return {
        "mutated_unpinned_helper": path,
        "mutation": "Fraction serialization returns str(value+1)",
        "historical_source_hashes_still_match": True,
        "historical_producer_success_marker_retained": True,
        "emitted_target_difference": "1",
        "complete_input_binding_detects_change_before_execution": True,
        "scope": "Controlled output corruption; not a mathematical counterexample or corruption of committed evidence",
    }


def report(root=ROOT):
    manifest_bytes = (HERE / "SOURCE-PINS.json").read_bytes()
    manifest = read_json(manifest_bytes)
    blobs, reference = validate_inputs(root, manifest)
    arithmetic = exclusion()
    coverage = check_historical(reference, arithmetic)
    fresh, runtime = replay(blobs)
    require(canonical(fresh) == canonical(reference), "Fresh certificate differs")
    control = serialization_control(blobs, reference, manifest)
    old_sources = set(reference["source_sha256"])
    local = set(manifest["local_import_graph"])
    return {
        "status": "PASS_PRIME_SUBSET_RECONCILIATION_NO_NEW_KAPPA",
        "base_commit": manifest["base_commit"], "assignment_seed": 98,
        "source_manifest_canonical_sha256": sha256(canonical(manifest)).hexdigest(),
        "pinned_inputs": len(blobs), "static_local_modules": len(local),
        "runtime_local_modules": runtime,
        "historical_source_entries": len(old_sources),
        "historically_unpinned_local_modules": sorted(local - old_sources),
        "historical_certificate_canonical_sha256": sha256(canonical(reference)).hexdigest(),
        "fresh_complete_certificate_equal": True,
        "serialization_control": control,
        "historical_coverage": coverage, "harmonic_exclusion": arithmetic,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="Write a fresh exact receipt instead of comparing it")
    args = parser.parse_args()
    result = report()
    if args.out:
        with args.out.open("x", encoding="utf-8", newline="\n") as out:
            out.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        require(canonical(result) == canonical(read_json((HERE / "RESULT.json").read_bytes())),
                "Recorded reconciliation receipt differs")
    print("PASS_PRIME_SUBSET_RECONCILIATION "
          f"{result['historical_coverage']['cases']} historical cases; "
          f"{result['harmonic_exclusion']['finite_cases']} harmonic cases; "
          f"tail h>={result['harmonic_exclusion']['tail_start']}; complete replay equal; no new kappa")


if __name__ == "__main__":
    main()
