"""Open the pinned predecessor and its own checked source bundle."""

from functools import cache
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import sys
import tarfile
from tempfile import TemporaryDirectory


@cache
def install():
    inputs = Path(__file__).resolve().parent / "inputs"
    manifest = json.loads((inputs / "retained.json").read_text())
    archive = (inputs / "retained.tar.gz").read_bytes()
    if sha256(archive).hexdigest() != manifest["archive_sha256"]:
        raise ValueError("The predecessor archive failed its hash check")
    work = TemporaryDirectory(prefix="triangular-multiplier-")
    root = Path(work.name)
    with tarfile.open(fileobj=BytesIO(archive), mode="r:gz") as packet:
        objects = {}
        for item in packet:
            if not item.isfile() or item.name in objects:
                raise ValueError("Unexpected source archive member")
            content = packet.extractfile(item).read()
            if sha256(content).hexdigest() != item.name:
                raise ValueError("A source member failed its hash check")
            objects[item.name] = content
        if set(objects) != {v["sha256"] for v in manifest["members"].values()}:
            raise ValueError("The predecessor source list differs")
        for name, member in manifest["members"].items():
            relative = Path(name)
            if relative.is_absolute() or ".." in relative.parts:
                raise ValueError("The predecessor member path is invalid")
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(objects[member["sha256"]])
    sys.path.insert(0, str(root))
    from source_inputs import activate

    prior, sources = activate()
    return work, root, prior, sources
