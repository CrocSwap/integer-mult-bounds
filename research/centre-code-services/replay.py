#!/usr/bin/env python3
"""Run the seven exact reviews. Keep all frozen source files unchanged."""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import platform
import runpy
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
FROZEN = ROOT / "frozen"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def manifest():
    return json.loads((ROOT / "SOURCE-MANIFEST.json").read_bytes())


def verify_sources():
    entries = manifest()["immutable_inputs"]
    for entry in entries:
        data = (ROOT / entry["path"]).read_bytes()
        require(digest(data) == entry["sha256"], "Source changed: " + entry["path"])
        if "decompressed_sha256" in entry:
            require(digest(gzip.decompress(data)) == entry["decompressed_sha256"],
                    "Payload changed: " + entry["path"])
    return len(entries)


def canonical_receipt(data, copied_source):
    """Change only registered source-path values. Keep all other JSON values."""
    record = manifest()
    paths = {}
    for entry in record["immutable_inputs"]:
        relative = entry["campaign_path"]
        for base in (Path(record["original_campaign_root"]), FROZEN, copied_source):
            paths[str(base / relative)] = entry["path"]

    def convert(value):
        if isinstance(value, dict):
            result = {}
            for key, child in value.items():
                if key == "path":
                    require(child in paths, "Unregistered receipt source path: " + str(child))
                    result[key] = paths[child]
                else:
                    result[key] = convert(child)
            return result
        if isinstance(value, list):
            return [convert(child) for child in value]
        return value

    return (json.dumps(convert(json.loads(data)), sort_keys=True, indent=2) + "\n").encode()


def worker():
    script, output, *arguments = sys.argv[2:]
    output = Path(output).resolve()
    allowed = (ROOT, output, Path(sys.base_prefix).resolve())
    opened = set()

    def audit(event, arguments):
        if event != "open" or not isinstance(arguments[0], (str, bytes, os.PathLike)):
            return
        path = Path(os.fsdecode(arguments[0])).resolve()
        require(path == Path(os.devnull) or any(path.is_relative_to(base) for base in allowed),
                "File access outside the package, output, or Python runtime: " + str(path))
        if path.is_relative_to(ROOT):
            opened.add("package/" + path.relative_to(ROOT).as_posix())
        elif path.is_relative_to(output):
            opened.add("output/" + path.relative_to(output).as_posix())

    sys.addaudithook(audit)
    sys.argv = [script, *arguments]
    runpy.run_path(script, run_name="__main__")
    (output / "FILE-ACCESS.json").write_text(json.dumps(sorted(opened), indent=2) + "\n")


def jobs():
    scripts = json.loads((ROOT / "CHECKS.json").read_bytes())
    return [
        ("moving_entry", scripts["moving_entry"], True,
         ["CHECKS.json", "MOVING-CODE-PROGRAM.json.gz"]),
        ("phase_inverse", scripts["phase_inverse"], True,
         ["CHECKS.json", "PHASE-SECTION-PROGRAM.json.gz"]),
        ("centre_constants", scripts["centre_constants"], False, ["CHECKS.json"]),
        ("clique_grid", scripts["clique_grid"], False, ["CHECKS.json"]),
        ("unnormalised_code", scripts["unnormalised_code"], False,
         ["CHECKS.json", "SOURCE-MANIFEST.json"]),
        ("capture_word", scripts["capture_word"], False,
         ["CHECKS.json", "SOURCE-MANIFEST.json"]),
        ("fixed_reader_services", scripts["fixed_reader_services"], False,
         ["REVIEW-CHECKS.json"]),
    ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    output = parser.parse_args().output.resolve()
    require(not output.exists(), "Use a new output directory")
    require(shutil.disk_usage(ROOT).free >= 3 * 1024**3, "At least 3 GiB of free disk space is required")
    source_count = verify_sources()
    output.mkdir(parents=True)
    reports = []
    for name, relative, writes_beside_source, filenames in jobs():
        for mode in ("normal", "optimized"):
            directory = output / name / mode
            directory.mkdir(parents=True)
            source = directory / "source" if writes_beside_source else FROZEN
            if writes_beside_source:
                shutil.copytree(FROZEN, source)
            script = source / relative
            result = script.parent if writes_beside_source else directory / "result"
            command = [sys.executable, "-I", "-B"] + (["-O"] if mode == "optimized" else [])
            command += [str(ROOT / "replay.py"), "--worker", str(script), str(directory)]
            if not writes_beside_source:
                command += ["--output" if name == "fixed_reader_services" else "--out", str(result)]
            env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1")
            print("RUN", name, mode, flush=True)
            started = time.monotonic()
            with (directory / "stdout.log").open("w") as log:
                completed = subprocess.run(command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
            require(completed.returncode == 0, "Check failed. Read " + str(directory / "stdout.log"))
            matches = {}
            for filename in filenames:
                actual = (result / filename).read_bytes()
                frozen_directory = FROZEN / Path(relative).parent
                if name == "fixed_reader_services":
                    frozen_directory /= "normal"
                frozen = (frozen_directory / filename).read_bytes()
                if filename.endswith(".gz"):
                    actual_checked, frozen_checked = gzip.decompress(actual), gzip.decompress(frozen)
                    method = "decompressed bytes"
                else:
                    actual_checked = canonical_receipt(actual, source)
                    frozen_checked = canonical_receipt(frozen, source)
                    method = "all JSON values, with registered source paths made relative"
                require(actual_checked == frozen_checked, "Frozen result mismatch: " + name + "/" + filename)
                if mode == "optimized":
                    previous = (output / name / "normal" / "canonical" / filename.removesuffix(".gz")).read_bytes()
                    require(actual_checked == previous, "Normal and optimized results differ")
                canonical = directory / "canonical" / filename.removesuffix(".gz")
                canonical.parent.mkdir(exist_ok=True)
                canonical.write_bytes(actual_checked)
                matches[filename] = {"method": method, "checked_sha256": digest(actual_checked),
                                     "new_file_sha256": digest(actual), "frozen_file_sha256": digest(frozen)}
            if writes_beside_source:
                changed = {(Path(relative).parent / filename).as_posix() for filename in filenames}
                for entry in manifest()["immutable_inputs"]:
                    if entry["campaign_path"] not in changed:
                        require(digest((source / entry["campaign_path"]).read_bytes()) == entry["sha256"],
                                "Copied source changed: " + entry["campaign_path"])
                saved = directory / "result"
                saved.mkdir()
                for filename in filenames:
                    shutil.copyfile(result / filename, saved / filename)
                shutil.rmtree(source)
            reports.append({"check": name, "mode": mode, "seconds": round(time.monotonic() - started, 3),
                            "results_equal_frozen": matches, "file_access_confined": True,
                            "checker_sha256": digest((FROZEN / relative).read_bytes())})
            print("PASS", name, mode, flush=True)
    require(verify_sources() == source_count, "Source count changed")
    receipt = {"status": "PASS_CENTRE_CODE_SERVICES", "immutable_inputs": source_count,
               "checks": reports, "normal_optimized_equal": True, "frozen_sources_unchanged": True,
               "python": platform.python_version(), "platform": platform.platform(),
               "replay_sha256": digest(Path(__file__).read_bytes()),
               "source_manifest_sha256": digest((ROOT / "SOURCE-MANIFEST.json").read_bytes()),
               "scope": "Exact local services, conditional code identities, and six forward D25 joins. Native phase files are checked by hash; the spatial phase interpreter is not rerun. No complete caller or kappa claim."}
    (output / "REPLAY.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], flush=True)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--worker":
        worker()
    else:
        main()
