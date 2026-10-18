#!/usr/bin/env python3
"""Source-binding, receipt, and read-only export failure controls."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(ok, why):
    if not ok:
        raise ValueError(why)


def hashes(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


def main():
    with tempfile.TemporaryDirectory(prefix="one-buffer-controls-") as temporary:
        root = Path(temporary)
        package = root / "research/r439-one-buffer-packet"
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        live = [x for x in json.loads((HERE / "SOURCES.json").read_text())["files"]
                if x["usage"] == "input"]
        for item in live:
            target = root / item["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / item["path"], target)
        spec = importlib.util.spec_from_file_location("exported_verifier", package / "verify.py")
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        retained = json.loads((package / "PREDECESSORS.json").read_text())["files"]
        rejected = 0
        for location, records, field, reason in (
                (package, retained, "local_path", "retained source SHA256"),
                (root, live, "path", "source SHA256:")):
            for item in records:
                path = location / item[field]
                original = path.read_bytes()
                path.write_bytes(original + b"\ncorruption-control\n")
                try:
                    try:
                        verifier.load_source()
                    except ValueError as exc:
                        require(str(exc).startswith(reason), "wrong source failure: " + str(exc))
                        rejected += 1
                    else:
                        raise ValueError("corrupted source accepted: " + str(path))
                finally:
                    path.write_bytes(original)

        receipt = package / "RESULT.json"
        original = receipt.read_bytes()
        changed = json.loads(original)
        changed["forward"]["meter"]["packet_exchanges"] -= 1
        receipt.write_text(json.dumps(changed))
        command = [sys.executable, "-I", "-O", "-B", str(package / "verify.py")]
        bad = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=180)
        require(bad.returncode != 0 and "receipt mismatch" in bad.stderr, "corrupt invoice accepted")
        receipt.write_bytes(original)

        before = hashes(root)
        try:
            for path in root.rglob("*"):
                path.chmod(0o555 if path.is_dir() else 0o444)
            root.chmod(0o555)
            good = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=180)
            require(good.returncode == 0 and "PASS_R439_ONE_BUFFER_PACKET" in good.stdout,
                    "read-only Git-free export: " + good.stderr[-2000:])
            require(hashes(root) == before, "read-only replay changed export")
        finally:
            root.chmod(0o700)
            for path in root.rglob("*"):
                path.chmod(0o700 if path.is_dir() else 0o600)
        print(json.dumps({"status": "PASS_ONE_BUFFER_PACKAGE_CONTROLS",
                          "retained_corruptions_rejected": len(retained),
                          "live_corruptions_rejected": len(live),
                          "total_source_rejections": rejected,
                          "changed_invoice_rejected": True,
                          "optimized_read_only_git_free_replay": True}, sort_keys=True))


if __name__ == "__main__":
    main()
