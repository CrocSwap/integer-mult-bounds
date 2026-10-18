"""Exercise source, receipt and output failures through the actual command line."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parent


def run(package, *arguments):
    return subprocess.run([sys.executable, "-I", "-O", "-B", str(package / "verify.py"), *arguments],
                          capture_output=True, text=True, timeout=90)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    with tempfile.TemporaryDirectory(prefix="selected-route-integrity-") as temporary:
        root = Path(temporary)
        exported = root / "package"
        shutil.copytree(PACKAGE, exported, ignore=shutil.ignore_patterns("__pycache__"))
        result = run(exported)
        require(result.returncode == 0 and "PASS_SELECTED_ROUTE_LIVE_VOLUME" in result.stdout,
                "Git-free optimized replay: " + result.stdout + result.stderr)
        for filename in ("routes.py", "records.py", "driver.py"):
            source = exported / "vendor" / filename
            original = source.read_bytes()
            source.write_bytes(original + b"\n# corrupt pin\n")
            result = run(exported, "--check-sources")
            require(result.returncode != 0 and "source SHA256" in result.stderr, "reject source corruption")
            source.write_bytes(original)
        receipt = exported / "RESULT.json"
        data = json.loads(receipt.read_text())
        require(data["cases"][0]["volume"] == 1, "literal bool/int mutation fixture")
        data["cases"][0]["volume"] = True
        receipt.write_text(json.dumps(data))
        result = run(exported)
        require(result.returncode != 0 and "exact typed route receipt" in result.stderr, "reject typed receipt")
        destination = root / "existing.json"
        destination.write_text("preserve me\n")
        result = run(exported, "--write-result", str(destination))
        require(result.returncode != 0 and "already exists" in result.stderr
                and destination.read_text() == "preserve me\n", "refuse receipt overwrite")
        result = run(exported, "--write-result", str(exported / "vendor" / "new.json"))
        require(result.returncode != 0 and "outside the package" in result.stderr
                and not (exported / "vendor" / "new.json").exists(), "refuse internal receipt output")
    print("PASS_ROUTE_INTEGRITY groups=7")


if __name__ == "__main__":
    main()
