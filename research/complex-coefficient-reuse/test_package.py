"""Check relocation, gzip payload semantics, optimized mode and rejection.

Only temporary copies are mutated. Apache-2.0; OpenAI Codex assistance.
"""

import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
PACKAGE = HERE.relative_to(ROOT)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def inventory(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


def run(root, *args):
    return subprocess.run([sys.executable, "-B", "-O", str(root / PACKAGE / "verify.py"), *args],
                          cwd=root.parent, capture_output=True, text=True, timeout=120)


def main():
    pins = json.loads((HERE / "SOURCES.json").read_text())["payload_sha256"]
    with tempfile.TemporaryDirectory(prefix="coefficient reuse ") as temporary:
        root = Path(temporary) / "minimal checkout with spaces"
        package = root / PACKAGE
        package.mkdir(parents=True)
        for p in HERE.iterdir():
            if p.is_file():
                shutil.copyfile(p, package / p.name)
        for name in pins:
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            raw = (ROOT / name).read_bytes()
            if name.endswith(".gz"):
                # A different container is intentionally valid: exact
                # decompressed bytes, not the gzip header, are the input.
                raw = gzip.compress(gzip.decompress(raw), compresslevel=1, mtime=39)
                require(raw != (ROOT / name).read_bytes(), "recompression did not change container")
            target.write_bytes(raw)
        before = inventory(root)
        passed = run(root)
        require(passed.returncode == 0 and "PASS_JP8_COEFFICIENT_REUSE" in passed.stdout,
                "minimal optimized replay failed: " + passed.stdout + passed.stderr)
        require(inventory(root) == before, "default replay wrote files")
        print("PASS relocated minimal package, recompressed inputs, optimized checks and no writes", flush=True)

        word_name = next(name for name in pins if name.endswith("CANONICAL-WORD.json.gz"))
        word_path = root / word_name
        original_word = word_path.read_bytes()
        word_path.write_bytes(gzip.compress(gzip.decompress(original_word) + b" ", mtime=39))
        output = Path(temporary) / "preserved-output.json"
        output.write_text("existing output must survive failed verification\n")
        rejected = run(root, "--write", str(output))
        require(rejected.returncode != 0 and "source pin mismatch" in rejected.stderr,
                "changed input payload was accepted")
        require(output.read_text() == "existing output must survive failed verification\n",
                "failed verification overwrote output")
        word_path.write_bytes(original_word)
        print("PASS payload mutation rejected and existing output preserved", flush=True)

        expected = package / "EXPECTED.json"
        certificate = json.loads(expected.read_text())
        certificate["programs"]["forward"]["shared_real_primitives"] -= 2
        expected.write_text(json.dumps(certificate))
        rejected = run(root)
        require(rejected.returncode != 0 and "certificate mismatch" in rejected.stderr,
                "optimistic cost certificate was accepted")
        print("PASS understated primitive certificate rejected under -O", flush=True)
    print("PASS_REUSE_PACKAGE_CHECKS")


if __name__ == "__main__":
    main()
