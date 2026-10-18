"""Check the standalone receipt interface in a new directory with no Git data."""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def run(package, cwd):
    return subprocess.run([sys.executable, "-I", "-O", "-B", str(package / "verify.py")],
                          cwd=cwd, capture_output=True, text=True, check=False)


def main():
    checked = []
    with TemporaryDirectory(prefix="native boundary package ") as folder:
        base = Path(folder)
        package = base / "copied package"
        shutil.copytree(ROOT, package)
        result = run(package, base)
        require(result.returncode == 0 and result.stdout.startswith("PASS_NATIVE_QUERY_BOUNDARY "),
                "standalone optimized replay failed: " + result.stderr)
        checked.append("relocated_optimized_replay")

        source = package / "vendor/pr840-proof.md"
        original_source = source.read_bytes()
        source.write_bytes(original_source + b"\nChanged source.\n")
        result = run(package, base)
        require(result.returncode != 0 and "source hash: vendor/pr840-proof.md" in result.stderr,
                "changed pinned source was not rejected by its hash guard")
        source.write_bytes(original_source)
        checked.append("changed_pinned_source_rejected")

        manifest = package / "SOURCES.json"
        original_manifest = manifest.read_bytes()
        changed = json.loads(original_manifest)
        changed["sources"][0]["commit"] = "0" * 40
        manifest.write_text(json.dumps(changed))
        result = run(package, base)
        require(result.returncode != 0
                and "certificate does not match exact replay" in result.stderr,
                "changed source identity was not rejected by the receipt")
        manifest.write_bytes(original_manifest)
        checked.append("changed_source_identity_rejected")

        certificate = package / "CERTIFICATE.json"
        original_certificate = certificate.read_bytes()
        mutations = (("child_volume_rejected", "child_volume_per_call", "V/3"),
                     ("boolean_count_rejected", "genuine_rows", True))
        for name, key, value in mutations:
            changed = json.loads(original_certificate)
            changed["two_block_escape"][key] = value
            certificate.write_text(json.dumps(changed))
            result = run(package, base)
            require(result.returncode != 0
                    and "certificate does not match exact replay" in result.stderr,
                    "changed receipt was not rejected by exact replay: " + name)
            checked.append(name)
        certificate.write_bytes(original_certificate)
    print("PASS_NATIVE_QUERY_PACKAGE " + " ".join(checked))


if __name__ == "__main__":
    main()
