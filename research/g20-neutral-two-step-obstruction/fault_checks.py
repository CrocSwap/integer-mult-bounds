"""Actual source/certificate corruptions in disposable Git-free package copies.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
import gzip
import json
import shutil
import subprocess
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def reject(root, script, optimized, message):
    argv = [sys.executable, "-I", "-W", "error", "-B"]
    if optimized:
        argv.append("-O")
    argv.append(str(root / PACKAGE.relative_to(ROOT) / script))
    result = subprocess.run(argv, cwd=root, capture_output=True, text=True, timeout=90)
    require(result.returncode != 0 and message in result.stderr,
            "mutation did not fail as intended: " + str(argv) + result.stderr[-1000:])


def main():
    sources = json.loads((PACKAGE / "SOURCES.json").read_bytes())
    input_paths = [entry["path"] for entry in sources["files"] if entry["usage"] == "input"]
    rejected = 0
    with tempfile.TemporaryDirectory(prefix="g20-two-step-faults-") as directory:
        root = Path(directory)
        # Disposable copies must be writable even when the exported sources are read-only.
        shutil.copytree(PACKAGE, root / PACKAGE.relative_to(ROOT), copy_function=shutil.copyfile,
                        ignore=shutil.ignore_patterns("__pycache__"))
        for relative in input_paths:
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
        package = root / PACKAGE.relative_to(ROOT)
        for optimized in (False, True):
            for relative in input_paths:
                target = root / relative
                original = target.read_bytes()
                target.write_bytes(original + b"\n")
                for script, message in (("native_verify.py", "source hash:"), ("trace_audit.py", "source mismatch:")):
                    reject(root, script, optimized, message)
                    rejected += 1
                target.write_bytes(original)
            target = package / "CERTIFICATE.json.gz"
            original = target.read_bytes()
            certificate = json.loads(gzip.decompress(original))
            certificate["branches"][0]["outcomes"].pop()
            target.write_bytes(gzip.compress(json.dumps(certificate).encode(), mtime=0))
            reject(root, "trace_audit.py", optimized, "two-step certificate mismatch")
            rejected += 1
            target.write_bytes(original)
            target = package / "NATIVE-CERTIFICATE.json.gz"
            original = target.read_bytes()
            certificate = json.loads(gzip.decompress(original))
            certificate["branches"][0]["outcomes"].pop()
            target.write_bytes(gzip.compress(json.dumps(certificate).encode(), mtime=0))
            reject(root, "native_verify.py", optimized, "native certificate bytes")
            rejected += 1
            target.write_bytes(original)
            target = package / "NATIVE-ONE-STEP.json.gz"
            original = target.read_bytes()
            certificate = json.loads(gzip.decompress(original))
            certificate["counts"]["eligible"] += 1
            target.write_bytes(gzip.compress(json.dumps(certificate).encode(), mtime=0))
            reject(root, "native_verify.py", optimized, "independent one-step certificate bytes")
            rejected += 1
            target.write_bytes(original)
            for filename in ("prefix_invoice.py", "native_floor.py"):
                target = package / filename
                original = target.read_bytes()
                target.write_bytes(original + b"\n")
                reject(root, "native_verify.py", optimized, "implementation bytes:")
                rejected += 1
                target.write_bytes(original)
            target = package / "TRACE-SUMMARY.json"
            original = target.read_bytes()
            summary = json.loads(original)
            summary["distinct_words_including_root"] = 220
            target.write_text(json.dumps(summary))
            reject(root, "trace_audit.py", optimized, "trace summary mismatch")
            rejected += 1
            target.write_bytes(original)
    require(rejected == 36, "fault-control coverage")
    print("PASS_G20_TWO_STEP_FAULTS source_rejections=24 direct_certificate_rejections=2 native_certificate_rejections=2 one_step_rejections=2 implementation_rejections=4 summary_rejections=2")


if __name__ == "__main__":
    main()
