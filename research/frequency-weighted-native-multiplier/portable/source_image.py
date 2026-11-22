"""Restore the public fixed compiler with a sequential unified-diff reader."""

import json
import re
import tarfile
from hashlib import sha256
from io import BytesIO
from pathlib import Path


def verify(data, digest):
    if sha256(data).hexdigest() != digest:
        raise ValueError("incorrect source digest")
    return data


def source_tar(data, manifest):
    files = {}
    with tarfile.open(fileobj=BytesIO(data), mode="r|gz") as archive:
        for rec in archive:
            key = rec.name
            if (
                not rec.isfile()
                or key not in manifest
                or key in files
                or Path(key).is_absolute()
                or ".." in Path(key).parts
            ):
                raise ValueError("invalid archive member")
            files[key] = verify(archive.extractfile(rec).read(), manifest[key])
    if files.keys() != manifest.keys():
        raise ValueError("incomplete source archive")
    return files


def apply(files, diff):
    lines = diff.splitlines(keepends=True)
    i = 0
    header = re.compile(rb"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
    while i < len(lines):
        if lines[i].startswith(
            (b"diff --git ", b"index ", b"new file mode ", b"old mode ", b"new mode ")
        ):
            i += 1
            continue
        old = lines[i].split()[1]
        new = lines[i + 1].split()[1]
        assert (
            lines[i].startswith(b"--- ")
            and lines[i + 1].startswith(b"+++ ")
            and new.startswith(b"b/")
        )
        name = new[2:].decode()
        assert old == b"/dev/null" or old == b"a/" + new[2:]
        rows = files.get(name, b"").splitlines(keepends=True)
        i += 2
        cursor = 0
        output = []
        while i < len(lines) and lines[i].startswith(b"@@ "):
            m = header.match(lines[i])
            assert m is not None
            start = m[1]
            old_count = int(m[2] or 1)
            new_count = int(m[4] or 1)
            pos = int(start) - (1 if old_count else 0)
            assert cursor <= pos <= len(rows)
            output.extend(rows[cursor:pos])
            cursor = pos
            i += 1
            old_used = new_used = 0
            while old_used < old_count or new_used < new_count:
                opcode = lines[i][:1]
                value = lines[i][1:]
                i += 1
                if i < len(lines) and lines[i].startswith(
                    b"\\ No newline at end of file"
                ):
                    value = value.removesuffix(b"\n")
                    i += 1
                assert opcode in (b"+", b"-", b" ")
                if opcode != b"+":
                    assert rows[cursor] == value
                    cursor += 1
                    old_used += 1
                if opcode != b"-":
                    output.append(value)
                    new_used += 1
            assert old_used == old_count and new_used == new_count
        output.extend(rows[cursor:])
        files[name] = b"".join(output)


def image(root):
    meta = json.loads((root / "SOURCES.json").read_bytes())
    source = {
        s: verify((root / s).read_bytes(), h)
        for s, h in meta["archive_and_overlay_sha256"].items()
    }
    a = source_tar(source["source/installer.tar.gz"], meta["installer_files"])
    amid = json.loads(a["SOURCES.json"])
    b = source_tar(
        verify(a["retimed-source.tar.gz"], amid["precursor_archive_sha256"]),
        amid["precursor_files"],
    )
    bmid = json.loads(b["predecessor/SOURCES.json"])["offline_predecessor"]
    fs = source_tar(
        verify(b["predecessor/" + bmid["archive"]], bmid["archive_sha256"]),
        {k: r["sha256"] for k, r in bmid["files"].items()},
    )
    for name, r in json.loads(b["predecessor/OVERLAY.json"]).items():
        text = verify(fs[name], r["old_sha256"]).decode()
        for old, new in r["edits"]:
            assert text.count(old) == 1
            text = text.replace(old, new)
        fs[name] = verify(text.encode(), r["new_sha256"])
    apply(fs, b["machine.patch"])
    apply(fs, b["receiver.patch"])
    for stem in (
        "five_exchange",
        "installations",
        "raw_binary_stage",
        "retimed_supplier",
        "transport",
        "unpowered_price",
        "fiscal_scans",
        "check_nonzero_eight",
    ):
        fs[stem + ".py"] = b[stem + ".py"]
    for name, r in amid["runtime_patch_sha256"].items():
        verify(fs[name], r["before"])
    apply(fs, verify(a["production.patch"], amid["production_patch_sha256"]))
    for name, r in amid["runtime_patch_sha256"].items():
        verify(fs[name], r["after"])
    for name in (
        "gauss_phase.py",
        "phase_atlas.py",
        "sparse_helpers.py",
        "clock_ports.py",
    ):
        fs[name] = a[name]
    for name, r in meta["runtime"].items():
        verify(fs[name], r["before"])
    apply(fs, source["runtime.patch"])
    fs["strong-bit.json.gz"] = source["source/strong-bit-k7.json.gz"]
    for name in ("installations.py", "grades.py"):
        fs[name] = source[name]
    for name, r in meta["runtime"].items():
        verify(fs[name], r["after"])
    return fs


def write_image(archive, destination, weighted=None):
    dest = Path(destination)
    files = image(Path(archive))
    if weighted is not None:
        root = Path(weighted)
        pins = json.loads((root / "SOURCES.json").read_bytes())
        assert pins["predecessor"] == "7b48187d99525ad59f560de3921ec7e48382484c"
        source = {
            key: verify((root / key).read_bytes(), digest)
            for key, digest in pins["local_sources"].items()
        }
        for key, row in pins["runtime_images"].items():
            verify(files[key], row["before"])
        apply(files, source["runtime.patch"])
        for key in ("typed_raw.py", "typed_transport.py", "grades.py"):
            files[key] = source[key]
        for key, row in pins["runtime_images"].items():
            verify(files[key], row["after"])
    for key, data in files.items():
        path = dest / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
