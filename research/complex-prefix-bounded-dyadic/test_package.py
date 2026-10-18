"""Relocated replay and failure controls for this standalone research package.

Chris Pagolu, with substantial OpenAI Codex assistance. Apache-2.0.
Only a temporary minimal checkout is changed. Run with Python 3.11+.
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
ROOT = HERE.parents[1]
RELATIVE = HERE.relative_to(ROOT)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def main():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    with tempfile.TemporaryDirectory(prefix="bounded dyadic relocation ") as tmp:
        root = Path(tmp)
        package = root / RELATIVE
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
        for filename in pins["files"]:
            target = root / filename
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / filename, target)

        def run(expected=None):
            def snapshot():
                return {p.relative_to(root): hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in root.rglob("*") if p.is_file()}

            before = snapshot()
            result = subprocess.run(
                [sys.executable, "-I", "-O", "-B", str(package / "verify.py")],
                cwd=root, capture_output=True, text=True, timeout=120,
            )
            need(snapshot() == before, "verification changed the minimal checkout")
            if expected is None:
                need(result.returncode == 0 and "PASS_PREFIX_BOUNDED_DYADIC" in result.stdout,
                     "minimal replay failed: " + result.stderr)
            else:
                need(result.returncode != 0 and expected in result.stderr,
                     "mutation not rejected as expected: " + str(result))

        # A gzip wrapper rewrite must not invalidate the mathematical input.
        zipped = next(root / f for f in pins["files"] if f.endswith(".gz"))
        data = gzip.decompress(zipped.read_bytes())
        zipped.write_bytes(gzip.compress(data, compresslevel=1, mtime=23))
        run()
        rejected = []

        def mutate(path, replacement, reason, name):
            original = path.read_bytes()
            try:
                path.write_bytes(replacement)
                run(reason)
                rejected.append(name)
            finally:
                path.write_bytes(original)

        source = root / "research/complex-k492-owner-repair/data/SPEC.json"
        mutate(source, source.read_bytes() + b"\n", "source pin mismatch", "altered_pinned_source")

        reference = package / "vendor/pr696_lower.py"
        mutate(reference, reference.read_bytes() + b"\n# changed\n",
               "vendored PR696 source mismatch", "altered_reference_source")

        certificate = package / "EXPECTED.json"
        report = json.loads(certificate.read_text())
        report["programs"]["jp8/backward"]["saved_vs_pr696"] += 2
        mutate(certificate, json.dumps(report).encode(), "expected certificate mismatch", "inflated_savings")

        compiler = package / "lower.py"
        text = compiler.read_text()
        old = "if n + 1 <= bound:"
        need(text.count(old) == 1, "guard mutation site")
        mutate(compiler, text.replace(old, "if True:").encode(),
               "DP / graph cost disagreement", "removed_intermediate_bound_guard")

        # Default verification is read-only, even with -I -O and a spaced path.
        need(not list(root.rglob("__pycache__")), "unexpected bytecode output")
        print("PASS_PACKAGE_RELOCATION_AND_CONTROLS " + ",".join(rejected))


if __name__ == "__main__":
    main()
