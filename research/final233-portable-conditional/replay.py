"""Verify and materialize the compact final233 inputs without modifying source."""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path, PurePosixPath

HERE = Path(__file__).resolve().parent
FULL = Path("research/h5b-combination-20261117/sol-analysis/full-wrapper")
NATIVE = FULL / "work/producer54/validation_native"
SIGNED = FULL / "work/producer54/validation_signed"

def need(condition, message):
    if not condition:
        raise ValueError(message)

def digest(data):
    return hashlib.sha256(data).hexdigest()

def safe(root, relative):
    p = PurePosixPath(relative)
    need(relative and not p.is_absolute() and ".." not in p.parts
         and "\\" not in relative and ":" not in relative and p.as_posix() == relative,
         "unsafe path")
    out = root.joinpath(*p.parts)
    need(out.resolve().is_relative_to(root.resolve()), "path escapes root")
    need(not any(part.is_symlink() for part in (out, *out.parents) if part.exists()), "symlink")
    return out

def check(upstream_archive=None):
    manifest = json.loads((HERE / "DATA-MANIFEST.json").read_text(encoding="utf-8"))
    pack = (HERE / "data/inputs.tar.gz").read_bytes()
    need(digest(pack) == manifest["pack_sha256"], "data pack hash")
    if upstream_archive is not None:
        need(digest(upstream_archive.read_bytes()) == manifest["big_archive_sha256"],
             "upstream archive hash")
    objects = {}
    with tarfile.open(HERE / "data/inputs.tar.gz", "r:gz") as archive:
        for member in archive:
            need(member.isfile() and member.name.startswith("objects/"), "unexpected archive member")
            key = member.name.removeprefix("objects/")
            need(len(key) == 64 and all(c in "0123456789abcdef" for c in key)
                 and key not in objects, "invalid or duplicate object")
            fileobj = archive.extractfile(member)
            need(fileobj is not None, "missing data object")
            data = fileobj.read()
            need(digest(data) == key, "packed object hash")
            objects[key] = data
    seen = set()
    used = set()
    missing_external = False
    for item in manifest["entries"]:
        name = item["path"]
        safe(HERE, name)
        need(name.casefold() not in seen, "duplicate path")
        seen.add(name.casefold())
        if item["storage"] == "packed":
            key = item["stored"]
            need(key in objects, "missing packed object")
            raw = objects[key]
            used.add(key)
        elif item["storage"] == "external":
            if upstream_archive is None:
                missing_external = True
                continue
            raw = upstream_archive.read_bytes()
        else:
            need(item["storage"] == "plain", "invalid storage")
            raw = safe(HERE, item["stored"]).read_bytes()
        need(len(raw) == item["bytes"] and digest(raw) == item["sha256"], "input mismatch: " + name)
    need(used == set(objects), "unreferenced object")
    return manifest, objects, missing_external

def materialize(work, manifest, objects, upstream_archive):
    work = work.resolve()
    need(not work.exists() and not work.is_relative_to(HERE) and not HERE.is_relative_to(work),
         "work must be new and separate")
    work.mkdir(parents=True, exist_ok=False)
    for item in manifest["entries"]:
        original = item["path"]
        if original.startswith("runtime/"):
            relative = original.removeprefix("runtime/")
        elif original.startswith("evidence/"):
            relative = "_evidence/" + original.removeprefix("evidence/")
        else:
            raise ValueError("unexpected materialization root")
        out = safe(work, relative)
        out.parent.mkdir(parents=True, exist_ok=True)
        if item["storage"] == "packed":
            raw = objects[item["stored"]]
        elif item["storage"] == "external":
            need(upstream_archive is not None, "supply --upstream-archive")
            raw = upstream_archive.read_bytes()
        else:
            raw = safe(HERE, item["stored"]).read_bytes()
        with out.open("xb") as stream:
            stream.write(raw)
        need(digest(out.read_bytes()) == item["sha256"], "materialization mismatch")
    return work

def main():
    need(__debug__, "do not run with -O/-OO")
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("integrity", "materialize", "reconstruct", "native", "signed", "optional-scalar"))
    parser.add_argument("--work", type=Path)
    parser.add_argument("--timeout", type=int, default=570)
    parser.add_argument("--upstream-archive", type=Path)
    args = parser.parse_args()
    manifest, objects, missing_external = check(args.upstream_archive)
    if args.mode == "integrity":
        print("PASS_LOCAL_PACKAGE_INTEGRITY_ONLY", len(manifest["entries"]),
              "EXTERNAL_NOT_CHECKED" if missing_external else "EXTERNAL_VERIFIED")
        return
    need(not missing_external, "supply the pinned --upstream-archive before materialization")
    need(args.work is not None and 1 <= args.timeout <= 570, "new --work and bounded timeout required")
    work = materialize(args.work, manifest, objects, args.upstream_archive)
    if args.mode == "materialize":
        print("PASS_EXACT_BYTE_MATERIALIZATION", len(manifest["entries"]))
        return
    if args.mode == "optional-scalar":
        argv = [sys.executable, "-I", "-B", str(work / "_evidence/independent/verify_finite233.py"),
                "--snapshot", str(work / "_evidence/candidate"), "--output", str(work / "FINITE-RESULT.json")]
    else:
        target = {"reconstruct": NATIVE / "reconstruction_preflight.py",
                  "native": NATIVE / "run.py", "signed": SIGNED / "run.py"}[args.mode]
        argv = [sys.executable, "-I", "-B", str(work / FULL / "macos_py39_shim.py"), str(work / target)]
    env = dict(os.environ)
    env.pop("PYTHONOPTIMIZE", None)
    with tempfile.TemporaryDirectory(prefix="f233-") as temp:
        env.update(TMP=temp, TEMP=temp, TMPDIR=temp, PYTHONDONTWRITEBYTECODE="1")
        with (work / "REPLAY.stdout.log").open("xb") as out:
            result = subprocess.run(argv, cwd=work, env=env, stdout=out, stderr=subprocess.STDOUT,
                                    timeout=args.timeout, check=False)
    record = {"mode": args.mode, "returncode": result.returncode, "stdout_sha256":
              digest((work / "REPLAY.stdout.log").read_bytes())}
    (work / "REPLAY.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    need(result.returncode == 0, "replay failed; inspect REPLAY.stdout.log")
    print(json.dumps(record, sort_keys=True))

if __name__ == "__main__":
    main()
