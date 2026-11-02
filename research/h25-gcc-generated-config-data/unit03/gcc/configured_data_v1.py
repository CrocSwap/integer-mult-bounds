"""Bounded passive Debian/GCC configured-data readers. No source execution.

Published generated headers remain data. This parser does not preprocess C,
execute make or shell commands, or return an effective GCC configuration.
"""
from __future__ import annotations
import hashlib
import io
import re
import tarfile
import gzip
import lzma
import bz2
from dataclasses import dataclass

MAX_COMPRESSED = 64 * 1024 * 1024
MAX_DECOMPRESSED = 256 * 1024 * 1024
MAX_MEMBERS = 16384
MAX_MEMBER = 64 * 1024 * 1024


class DataRefusal(ValueError):
    pass


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def debian_control(data: bytes) -> dict[str, str]:
    """One unsigned retained control paragraph; duplicate fields are errors.

    Signed wrappers, a second paragraph and malformed continuations are refused.
    This establishes parsing/identity only and never claims signature validity.
    """
    if type(data) is not bytes or len(data) > 1024 * 1024 or b"\0" in data:
        raise DataRefusal("control bound/type")
    try: text = data.decode("utf-8", "strict")
    except UnicodeError as error: raise DataRefusal("control encoding") from error
    if text.startswith("-----BEGIN"):
        raise DataRefusal("signed wrapper needs independent signature/wrapper handling")
    fields, current, ended = {}, None, False
    for number, raw in enumerate(text.split("\n"), 1):
        line = raw[:-1] if raw.endswith("\r") else raw
        if not line:
            if fields: ended = True
            continue
        if ended: raise DataRefusal("multiple control paragraphs")
        if line[0] in " \t":
            if current is None: raise DataRefusal("orphan continuation")
            fields[current] += "\n" + line[1:]
            continue
        match = re.fullmatch(r"([A-Za-z0-9][A-Za-z0-9-]*):(?:[ \t]?)(.*)", line)
        if not match: raise DataRefusal("malformed control field at line " + str(number))
        current = match[1].lower()
        if current in fields: raise DataRefusal("duplicate control field: " + current)
        fields[current] = match[2]
    if not fields: raise DataRefusal("empty control data")
    return fields


def sha256_rows(fields: dict[str, str]) -> dict[str, tuple[int, str]]:
    if "checksums-sha256" not in fields: raise DataRefusal("missing SHA256 section")
    result = {}
    for line in fields["checksums-sha256"].split("\n"):
        if not line.strip(): continue
        match = re.fullmatch(r"([0-9a-f]{64})[ \t]+([0-9]+)[ \t]+([^ \t/]+)", line)
        if not match: raise DataRefusal("malformed SHA256 row")
        hexdigest, raw_size, filename = match.groups()
        if filename in result: raise DataRefusal("duplicate checksum filename: " + filename)
        if filename in (".", "..") or "\0" in filename: raise DataRefusal("unsafe checksum filename")
        size = int(raw_size)
        if size > MAX_DECOMPRESSED: raise DataRefusal("checksum member size bound")
        result[filename] = (size, hexdigest)
    return result


def same_build_package(changes: bytes, buildinfo: bytes, filename: str,
                       expected_source: str, expected_version: str) -> dict:
    first, second = debian_control(changes), debian_control(buildinfo)
    for fields in (first, second):
        if fields.get("source") != expected_source or fields.get("version") != expected_version:
            raise DataRefusal("source/version association differs")
        if "amd64" not in fields.get("architecture", "").split():
            raise DataRefusal("amd64 architecture missing")
    one, two = sha256_rows(first), sha256_rows(second)
    if filename not in one or filename not in two: raise DataRefusal("exact package filename absent")
    if one[filename] != two[filename]: raise DataRefusal("changes/buildinfo package identity disagrees")
    size, hexdigest = one[filename]
    return {"filename": filename, "bytes": size, "sha256": hexdigest,
            "changes_sha256": digest(changes), "buildinfo_sha256": digest(buildinfo),
            "signature_verified": False, "association": "exact matching checksum rows in retained records"}


def strict_ar(data: bytes) -> list[dict]:
    if type(data) is not bytes or len(data) > MAX_COMPRESSED or not data.startswith(b"!<arch>\n"):
        raise DataRefusal("ar magic/type/size")
    index, result, seen = 8, [], set()
    while index < len(data):
        header_start = index
        if len(data) - index < 60: raise DataRefusal("truncated ar header")
        header = data[index:index+60]; index += 60
        if header[58:60] != b"`\n": raise DataRefusal("ar header trailer")
        raw_name = header[:16].rstrip(b" ")
        if raw_name.startswith((b"#1/", b"/")): raise DataRefusal("extended ar names unsupported")
        if raw_name.endswith(b"/"): raw_name = raw_name[:-1]
        numeric={}
        for label,field_start,field_end,base in (("timestamp",16,28,10),("uid",28,34,10),
                                     ("gid",34,40,10),("mode",40,48,8)):
            value=header[field_start:field_end].strip()
            pattern=rb"[0-7]+" if base==8 else rb"[0-9]+"
            if not re.fullmatch(pattern,value):raise DataRefusal("ar numeric metadata: "+label)
            numeric[label]=int(value,base)
        try:
            name = raw_name.decode("ascii", "strict")
            size_text = header[48:58].strip()
            if not re.fullmatch(rb"[0-9]+", size_text): raise DataRefusal("ar size syntax")
            size = int(size_text)
        except UnicodeError as error: raise DataRefusal("ar name encoding") from error
        if not re.fullmatch(r"[A-Za-z0-9_.+-]+", name) or name in (".", ".."):
            raise DataRefusal("unsafe ar member")
        if name in seen: raise DataRefusal("duplicate ar member: " + name)
        seen.add(name)
        if size > MAX_COMPRESSED or index + size > len(data): raise DataRefusal("truncated/oversize ar payload")
        payload = data[index:index+size]; index += size
        if size % 2:
            if index >= len(data) or data[index:index+1] != b"\n": raise DataRefusal("ar alignment byte")
            index += 1
        result.append({"name": name, "offset": header_start, "data_offset": header_start+60,
                       "bytes": size, "sha256": digest(payload), "data": payload,
                       "raw_header": header.hex(), **numeric})
    if not result or result[0]["name"] != "debian-binary" or result[0]["data"] != b"2.0\n":
        raise DataRefusal("Debian format/version")
    controls = [r for r in result if r["name"].startswith("control.tar")]
    payloads = [r for r in result if r["name"].startswith("data.tar")]
    if len(result) != 3 or len(controls) != 1 or len(payloads) != 1:
        raise DataRefusal("Debian ar member topology")
    return result


def decompress_member(name: str, data: bytes) -> bytes:
    if len(data) > MAX_COMPRESSED: raise DataRefusal("compressed bound")
    if name.endswith(".xz"): opener = lzma.LZMAFile
    elif name.endswith(".gz"): opener = gzip.GzipFile
    elif name.endswith(".bz2"): opener = bz2.BZ2File
    elif name.endswith(".tar"): return data
    else: raise DataRefusal("unsupported passive compression: " + name)
    with opener(io.BytesIO(data), "rb") as stream:
        result = stream.read(MAX_DECOMPRESSED + 1)
    if len(result) > MAX_DECOMPRESSED: raise DataRefusal("decompressed bound")
    return result


def safe_tar_name(name: str) -> str:
    if "\0" in name or name.startswith("/") or "\\" in name: raise DataRefusal("unsafe tar member path")
    while name.startswith("./"): name = name[2:]
    pieces = name.rstrip("/").split("/")
    if any(piece in ("", ".", "..") for piece in pieces):
        if name in ("", "."): return "."
        raise DataRefusal("unsafe/ambiguous tar member path")
    return "/".join(pieces)


def strict_tar(data: bytes) -> list[dict]:
    """Return raw member kind/alias records; never extract aliases to disk."""
    if type(data) is not bytes or len(data) > MAX_DECOMPRESSED: raise DataRefusal("tar bound/type")
    result, seen, total, used_end = [], set(), 0, 0
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:") as archive:
        for member in archive:
            if len(result) >= MAX_MEMBERS: raise DataRefusal("tar member count")
            name = safe_tar_name(member.name)
            if name in seen: raise DataRefusal("duplicate tar member path: " + name)
            seen.add(name)
            if member.size > MAX_MEMBER: raise DataRefusal("tar member byte bound")
            total += member.size
            if total > MAX_DECOMPRESSED: raise DataRefusal("tar aggregate byte bound")
            kind = "file" if member.isfile() else ("directory" if member.isdir() else
                   ("symlink" if member.issym() else ("hardlink" if member.islnk() else "other")))
            record = {"path": name, "raw_path": member.name, "kind": kind,
                      "typeflag": member.type.hex(), "bytes": member.size,
                      "mode": member.mode, "uid": member.uid, "gid": member.gid,
                      "linkname": member.linkname, "header_offset": member.offset,
                      "data_offset": member.offset_data}
            used_end=max(used_end,member.offset_data+((member.size+511)//512)*512)
            if kind == "file":
                stream = archive.extractfile(member)
                if stream is None: raise DataRefusal("missing regular tar body")
                body = stream.read(member.size + 1)
                if len(body) != member.size: raise DataRefusal("truncated regular tar body")
                record.update(data=body, sha256=digest(body))
            result.append(record)
    # tarfile stops at an end marker. Authenticate that no hidden nonzero tail
    # was silently ignored, retaining the original complete tar bytes in the
    # enclosing package. A valid ustar/GNU archive supplies two zero blocks.
    if len(data)%512 or len(data)-used_end<1024 or any(data[used_end:]):
        raise DataRefusal("tar termination/padding or hidden nonzero tail")
    return result
