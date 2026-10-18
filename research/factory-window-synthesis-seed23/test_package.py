#!/usr/bin/env python3
"""Offline/optimized replay and source/coverage/receipt rejection controls.

Hanson Sun with substantial OpenAI Codex assistance. Apache-2.0.
"""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RELATIVE = HERE.relative_to(ROOT)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def invoke(root, script, *args, succeed=True, diagnostic=None):
    result = subprocess.run([sys.executable, "-I", "-O", "-B",
                             str(root / RELATIVE / script), *map(str, args)],
                            cwd=root.parent, capture_output=True, text=True, timeout=60)
    require((result.returncode == 0) == succeed,
            f"unexpected exit {script}: {result.stdout}\n{result.stderr}")
    if diagnostic:
        require(diagnostic in result.stdout + result.stderr, "wrong rejection: " + diagnostic)
    return result


def main():
    sources = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))["files"]
    rejected = 0
    with tempfile.TemporaryDirectory(prefix="factory window offline ") as temporary:
        root = Path(temporary) / "minimal checkout with spaces"
        package = root / RELATIVE
        package.mkdir(parents=True)
        for name in ("verify.py", "independent.py", "EXPECTED.json", "SOURCES.json"):
            shutil.copyfile(HERE / name, package / name)
        for source in sources:
            destination = root / source
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / source, destination)
        invoke(root, "verify.py", diagnostic="PASS_FACTORY_WINDOW_SYNTHESIS")
        invoke(root, "independent.py", diagnostic="PASS_FACTORY_WINDOW_MODULAR")
        receipt = package / "EXPECTED.json"
        original = receipt.read_bytes()

        def mutate_receipt(mutation, script="verify.py", diagnostic="receipt mismatch"):
            nonlocal rejected
            data = json.loads(original)
            mutation(data)
            receipt.write_text(json.dumps(data), encoding="utf-8")
            invoke(root, script, succeed=False, diagnostic=diagnostic)
            receipt.write_bytes(original)
            rejected += 1

        mutate_receipt(lambda x: x["windows"].pop())
        mutate_receipt(lambda x: x["windows"].pop(), "independent.py", "window inventory")
        mutate_receipt(lambda x: x["windows"][0]["orientations"].pop("inverse"))
        mutate_receipt(lambda x: x["windows"][0]["orientations"]["forward"]["best"].update(primitives=1))
        mutate_receipt(lambda x: x.update(orientation_cases=True))
        mutate_receipt(lambda x: x["windows"][0]["orientations"]["forward"]["best"].update(macros=4.0))
        mutate_receipt(lambda x: x["frontiers"]["4"].update(distinct_prefix_matrices=1))

        source = root / next(iter(sources))
        saved = source.read_bytes()
        source.write_bytes(saved + b"\n")
        invoke(root, "verify.py", succeed=False, diagnostic="source pin")
        rejected += 1
        source.write_bytes(saved)
        source.unlink()
        invoke(root, "verify.py", succeed=False, diagnostic="FileNotFoundError")
        rejected += 1
        source.write_bytes(saved)

        destination = Path(temporary) / "existing.json"
        destination.write_bytes(b"preserve this output\n")
        invoke(root, "verify.py", "--write", destination, succeed=False, diagnostic="output already exists")
        require(destination.read_bytes() == b"preserve this output\n", "existing output changed")
        rejected += 1
        regenerated = Path(temporary) / "fresh.json"
        invoke(root, "verify.py", "--write", regenerated, diagnostic="WROTE_FACTORY_WINDOW_RECEIPT")
        require(regenerated.read_bytes() == original, "fresh deterministic receipt differs")
    print(f"PASS_FACTORY_WINDOW_PACKAGE optimized_offline_relocation=1 rejections={rejected} "
          "receipt_regeneration=1 output_preserved=1")


if __name__ == "__main__":
    main()
