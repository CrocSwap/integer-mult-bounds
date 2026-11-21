"""Use the authenticated source snapshot in a private execution directory."""

from functools import cache
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import sys
import tarfile
from tempfile import TemporaryDirectory


@cache
def activate():
    inputs = Path(__file__).resolve().parent / "inputs"
    pins = json.loads((inputs / "origins.json").read_text())
    packet = (inputs / "runtime.tar.gz").read_bytes()
    if sha256(packet).hexdigest() != pins["archive_sha256"]:
        raise ValueError("The runtime input archive differs from its manifest")
    root = Path(_work().name)
    with tarfile.open(fileobj=BytesIO(packet), mode="r:gz") as archive:
        members = pins["members"]
        digests = {data["sha256"] for data in members.values()}
        if set(archive.getnames()) != digests:
            raise ValueError("The archived source list differs")
        objects = {}
        for item in archive:
            if not item.isfile() or item.name in objects:
                raise ValueError("Unexpected source member")
            content = archive.extractfile(item).read()
            if sha256(content).hexdigest() != item.name:
                raise ValueError("The source binding differs")
            objects[item.name] = content
        for name, data in members.items():
            relative = Path(name)
            if relative.is_absolute() or ".." in relative.parts:
                raise ValueError("Unexpected source path")
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(objects[data["sha256"]])
    prior = root / "research/bounded-general-multiplier"
    sys.path.insert(0, str(prior))
    return prior, root


@cache
def _work():
    return TemporaryDirectory(prefix="native-stock-inputs-")
