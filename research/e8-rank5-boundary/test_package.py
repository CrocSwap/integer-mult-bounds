#!/usr/bin/env python3
"""Relocation, certificate tampering and source-binding controls (stdlib).

Philipp (@mightyOil), with substantial OpenAI Codex assistance. Apache-2.0.
"""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def run(package, script, arguments=(), failure=None):
    result = subprocess.run([sys.executable, "-I", "-O", "-B", str(package / script), *arguments],
                            cwd=package.parent, text=True, capture_output=True)
    if failure is None:
        if result.returncode:
            raise ValueError(result.stdout + result.stderr)
    elif result.returncode == 0 or failure not in result.stderr:
        raise ValueError("wrong mutation outcome: " + result.stdout + result.stderr)


def main():
    with tempfile.TemporaryDirectory(prefix="e8-boundary-package-") as temporary:
        package = Path(temporary) / "relocated"
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
        certificate = package / "CERTIFICATE.json"
        original = certificate.read_bytes()
        run(package, "verify.py")
        run(package, "independent_check.py", ["--check", str(certificate)])
        regenerated = package / "regenerated.json"
        run(package, "verify.py", ["--write", str(regenerated)])
        if regenerated.read_bytes() != original:
            raise ValueError("relocated certificate is not byte-identical")
        changed = json.loads(original)
        changed["independent_summary"]["punctures"][0]["star_cost"] -= 1
        certificate.write_text(json.dumps(changed))
        run(package, "verify.py", failure="certificate mismatch")
        run(package, "independent_check.py", ["--check", str(certificate)],
            failure="independent_summary differs")
        changed = json.loads(original)
        changed["equality_orbit_size"] -= 1
        certificate.write_text(json.dumps(changed))
        run(package, "verify.py", failure="certificate mismatch")
        certificate.write_bytes(original)
        source = package / "sources" / "pr631" / "README.md"
        source.write_bytes(source.read_bytes() + b"\nsource mutation\n")
        protected = package / "protected-output.json"
        protected.write_bytes(b"existing output must survive\n")
        run(package, "verify.py", ["--write", str(protected)], failure="predecessor source hash")
        if protected.read_bytes() != b"existing output must survive\n":
            raise ValueError("failed validation overwrote output")
    print("PASS_E8_BOUNDARY_PACKAGE: isolated relocation; byte-identical receipt; "
          "cost and orbit mutations rejected; source mutation rejected before output write")


if __name__ == "__main__":
    main()
