#!/usr/bin/env python3
"""Install the pinned official actionlint release into an explicit directory."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import platform
import tarfile
import urllib.request

MANIFEST = Path(__file__).resolve().parents[1] / ".github/actionlint.json"


def install(directory: Path) -> Path:
    manifest = json.loads(MANIFEST.read_text())
    system = platform.system().lower()
    machine = {"x86_64": "amd64", "aarch64": "arm64"}.get(
        platform.machine(), platform.machine())
    target = f"{system}_{machine}"
    if target not in manifest["sha256"]:
        raise ValueError(f"unsupported platform: {target}; see docs/workflow-validation.md")
    version = manifest["version"]
    url = (f"https://github.com/rhysd/actionlint/releases/download/v{version}/"
           f"actionlint_{version}_{target}.tar.gz")
    with urllib.request.urlopen(url, timeout=60) as response:
        archive = response.read()
    if hashlib.sha256(archive).hexdigest() != manifest["sha256"][target]:
        raise ValueError("actionlint archive checksum mismatch; refusing to install")
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tar:
        member = tar.getmember("actionlint")
        if not member.isfile():
            raise ValueError("actionlint archive entry is not a regular file")
        binary = tar.extractfile(member).read()
    directory.mkdir(parents=True, exist_ok=True)
    destination = directory / "actionlint"
    # Replace atomically; never follow a pre-existing destination symlink.
    temporary = directory / "actionlint.download"
    with temporary.open("xb") as stream:
        stream.write(binary)
    temporary.chmod(0o755)
    temporary.replace(destination)
    return destination.resolve()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    args = parser.parse_args()
    print(install(args.directory))


if __name__ == "__main__":
    main()
