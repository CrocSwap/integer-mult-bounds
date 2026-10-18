"""Authenticate and export the complete immutable predecessor before imports."""

import json
import sys
import tarfile
from contextlib import contextmanager
from hashlib import sha1, sha256
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory

PACKAGE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate(package=PACKAGE):
    manifest = json.loads((package / "PREDECESSOR.json").read_text())
    archive = package / "predecessor.tar.gz"
    require(archive.stat().st_size <= 200_000, "bounded source archive")
    require(
        sha256(archive.read_bytes()).hexdigest() == manifest["archive_sha256"],
        "immutable source archive SHA256",
    )
    expected = {item["path"]: item for item in manifest["files"]}
    require(
        len(expected) == len(manifest["files"]) == 84,
        "complete 84-file source inventory",
    )
    files = {}
    with tarfile.open(archive, "r:gz") as stream:
        for member in stream:
            name = member.name
            require(
                member.isfile() and name in expected and name not in files,
                "declared regular source file, once",
            )
            require(
                PurePosixPath(name).as_posix() == name
                and not PurePosixPath(name).is_absolute()
                and ".." not in PurePosixPath(name).parts,
                "canonical source path",
            )
            item = expected[name]
            require(member.size == item["size"] <= 100_000, "bounded source member")
            opened = stream.extractfile(member)
            require(opened is not None, "source member exists")
            with opened:
                data = opened.read(100_001)
            require(
                len(data) == item["size"]
                and sha256(data).hexdigest() == item["sha256"],
                "source bytes match immutable pin",
            )
            git_object = b"blob " + str(len(data)).encode() + b"\0" + data
            require(
                sha1(git_object, usedforsecurity=False).hexdigest() == item["git_blob"],
                "source bytes match Git blob pin",
            )
            files[name] = data
    require(files.keys() == expected.keys(), "no omitted source files")
    return manifest, files


@contextmanager
def installed():
    manifest, files = authenticate()
    old_path = list(sys.path)
    with TemporaryDirectory(prefix="compatible-rows-") as temporary:
        root = Path(temporary).resolve()
        for name, data in files.items():
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        roots = (root, root / "predecessor", root / "predecessor" / "vendor")
        module_names = {
            path.stem for path in (root / "predecessor" / "vendor").glob("*.py")
        }
        module_names |= {path.stem for path in (root / "predecessor").glob("*.py")}
        module_names |= {path.stem for path in root.glob("*.py")}
        require(
            not module_names.intersection(sys.modules),
            "no preloaded predecessor modules",
        )
        sys.path[:0] = [str(path) for path in roots]
        try:
            yield manifest, root
        finally:
            sys.path[:] = old_path
            for name in module_names:
                module = sys.modules.get(name)
                if module is not None and str(
                    getattr(module, "__file__", "")
                ).startswith(str(root)):
                    del sys.modules[name]
