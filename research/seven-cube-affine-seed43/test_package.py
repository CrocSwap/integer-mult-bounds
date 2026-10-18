#!/usr/bin/env python3
"""Receipt/source corruptions and optimized read-only relocation, stdlib only.

Hanson Sun with substantial OpenAI Codex assistance; Apache-2.0.
"""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def check(ok, message):
    if not ok:
        raise RuntimeError(message)


def run(root, expected=None):
    for name in ("verify.py", "independent.py"):
        script = root / "research" / HERE.name / name
        result = subprocess.run([sys.executable, "-I", "-O", "-B", str(script)],
                                cwd=root, capture_output=True, text=True, timeout=180)
        if expected is None:
            check(result.returncode == 0 and "PASS_SEVEN_CUBE" in result.stdout,
                  name + " relocation failed: " + result.stdout + result.stderr)
        else:
            check(result.returncode != 0 and expected in result.stderr,
                  name + " failed to reject the intended mutation: " + result.stdout + result.stderr)


def main():
    with tempfile.TemporaryDirectory(prefix="seven cube exact ") as temp:
        root = Path(temp) / "relocated checkout"
        package = root / "research" / HERE.name
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
        inputs = [s for s in json.loads((HERE / "SOURCES.json").read_text())["files"] if s["usage"] == "input"]
        for source in inputs:
            path = root / source["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / source["path"], path)
        files = [p for p in root.rglob("*") if p.is_file()]
        dirs = sorted([p for p in root.rglob("*") if p.is_dir()] + [root], key=lambda p: len(p.parts), reverse=True)
        try:
            for path in files:
                path.chmod(0o444)
            for path in dirs:
                path.chmod(0o555)
            run(root)
        finally:
            for path in dirs:
                path.chmod(0o755)
            for path in files:
                path.chmod(0o644)
        original = (package / "CERTIFICATE.json").read_bytes()
        mutations = [
            ("rank-underclaim", lambda x: x["rank_orbits"][0].update(rank=63)),
            ("omitted-orbit", lambda x: x["rank_orbits"].pop()),
            ("omitted-assignment", lambda x: x["factor_census"]["4"].update(source_assignments=564479)),
            ("omitted-witness-term", lambda x: x["witnesses"]["four_terms"]["terms"].pop()),
        ]
        for name, mutate in mutations:
            receipt = json.loads(original)
            mutate(receipt)
            (package / "CERTIFICATE.json").write_text(json.dumps(receipt))
            run(root, "certificate differs")
            print("REJECTED " + name, flush=True)
        (package / "CERTIFICATE.json").write_bytes(original)
        source = root / inputs[0]["path"]
        source.write_bytes(source.read_bytes() + b"\nsource mutation\n")
        run(root, "source ")
        print("REJECTED source-corruption", flush=True)
    print("PASS_SEVEN_CUBE_PACKAGE_TESTS readonly_relocation=2 corruption_rejections=10")


if __name__ == "__main__":
    main()
