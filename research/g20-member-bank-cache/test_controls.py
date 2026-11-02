"""Real relocated CLI, source corruption and missing-installation controls.

Produced by Nick Petalas. Apache-2.0. Temporary copies only.
"""

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
SUCCESS = b"PASS independent complete normalized G20 census receipt\n"


def inventory(root):
    files = sorted(p for p in root.rglob("*") if p.is_file())
    if len(files) > 64:
        raise ValueError("Control export file bound")
    return {str(p.relative_to(root)): [hashlib.sha256(p.read_bytes()).hexdigest(),
                                     p.stat().st_mode & 0o777] for p in files}


def execute(root, optimized=False):
    command = [sys.executable, "-I", "-W", "error", "-B"]
    if optimized:
        command.append("-O")
    command.append(str(root / "replay.py"))
    env = dict(os.environ, PATH="", PYTHONOPTIMIZE="")
    return subprocess.run(command, cwd=root, env=env, capture_output=True, timeout=120, check=False)


def require_failure(root, message):
    result = execute(root, optimized=True)
    if result.returncode == 0 or message.encode() not in result.stderr or result.stdout:
        raise ValueError("Actual CLI failure control did not reject: " + message)


def main():
    with tempfile.TemporaryDirectory(prefix="g20-cache-controls-") as folder:
        destination = Path(folder) / "export"
        shutil.copytree(ROOT, destination)
        before = inventory(destination)
        for path in destination.rglob("*"):
            if path.is_file():
                path.chmod(0o444)
        readonly = inventory(destination)
        for optimized in (False, True):
            result = execute(destination, optimized)
            if result.returncode != 0 or result.stdout != SUCCESS or result.stderr:
                raise ValueError("Relocated read-only replay failed: " + result.stderr.decode())
            if inventory(destination) != readonly:
                raise ValueError("Read-only replay changed bytes or modes")
        path = destination / "frozen" / "sources" / "FRAMES.json"
        original = path.read_bytes()
        path.chmod(0o644)
        path.write_bytes(original + b"\n")
        require_failure(destination, "Frozen sha256")
        path.write_bytes(original)
        manifest = destination / "FROZEN.json"
        original = manifest.read_bytes()
        manifest.chmod(0o644)
        manifest.write_bytes(original + b"\n")
        require_failure(destination, "Frozen manifest digest")
        manifest.write_bytes(original)
        adapter = destination / "replay.py"
        original = adapter.read_text()
        anchor = '    kernel["contains"] = memo\n'
        if original.count(anchor) != 1:
            raise ValueError("Installation mutation anchor")
        adapter.chmod(0o644)
        adapter.write_text(original.replace(anchor, ""))
        require_failure(destination, "Containment reuse must execute")
        for path in destination.rglob("*"):
            if path.is_file():
                path.chmod(0o644)
        if set(inventory(destination)) != set(before):
            raise ValueError("Control export file inventory changed")
    print(json.dumps({"status": "PASS_G20_CACHE_CLI_CONTROLS", "readonly_runs": 2,
                      "rejected": 3, "git_required": False, "path_empty": True}, sort_keys=True))


if __name__ == "__main__":
    main()
