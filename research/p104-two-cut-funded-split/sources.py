# SPDX-License-Identifier: Apache-2.0
"""Authenticate the literal predecessor and reuse its retained source closure."""

from contextlib import contextmanager
from hashlib import sha1, sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import gzip
import importlib.util
import json
import sys
import tarfile

HERE = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if raw.startswith(b"\x1f\x8b") else raw)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@contextmanager
def parent_archive():
    pin = read(HERE / "INPUTS.json")
    archive = HERE / pin["archive"]
    need(sha256(archive.read_bytes()).hexdigest() == pin["archive_sha256"], "Exact predecessor archive")
    files = {x["path"]: x for x in pin["files"]}
    need(len(files) == len(pin["files"]), "Unique pinned archive paths")
    with TemporaryDirectory(prefix="p104-stationary-source-") as tmp:
        root = Path(tmp)
        seen = set()
        with tarfile.open(archive) as payload:
            for member in payload:
                if member.isdir():
                    continue
                name = member.name
                target = root / name
                need(member.isfile() and name in files and name not in seen
                     and target.resolve().is_relative_to(root), "Exact regular archive inventory")
                raw = payload.extractfile(member).read()
                row = files[name]
                blob = sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
                need((len(raw), sha256(raw).hexdigest(), blob) ==
                     (row["size"], row["sha256"], row["git_blob"]), "Predecessor member " + name)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raw)
                seen.add(name)
        need(seen == set(files), "All predecessor bytes retained")
        yield root / pin["prefix"]


# The runner installs this file as source.py in a private stage directory.
# The exact parent archive stays read-only throughout the stage.
def stage_parent():
    return Path((HERE / "PARENT-DIRECTORY.txt").read_text().strip())


def reference():
    root = HERE / "reference"
    pins = read(HERE / "REFERENCE.json")
    need(pins["source_head"] == "e3f8d39c43b07063dfc5b800f71c5d21015259e6", "Exact comparator head")
    need(set(pins["files"]) == {p.name for p in root.iterdir()}, "Complete comparator inventory")
    for name, digest in pins["files"].items():
        need(sha256((root / name).read_bytes()).hexdigest() == digest, "Exact comparator file " + name)
    word = read(root / "WORD.json.gz")
    need(sha256(canonical(word)).hexdigest() == read(root / "NATIVE-RESULT.json")["word_canonical_sha256"],
         "Exact #7161 native word")
    return root, word


@contextmanager
def sources():
    parent = stage_parent()
    root, word = reference()
    source = load("two_cut_parent_native_sources", parent / "source.py")
    with source.sources() as (vendor, audit, rank9, bundle, _, _):
        yield vendor, audit, rank9, bundle, root, word


@contextmanager
def bundles():
    parent = stage_parent()
    root, _ = reference()
    source = load("two_cut_parent_caller_sources", parent / "source.py")
    with source.bundles() as (parts, _, temporary):
        yield parts, root, temporary
