"""Replay the tariff transfer on the ten-shortcut construction from the packaged immutable source."""

from argparse import ArgumentParser
from hashlib import sha256
import json
import os
from pathlib import Path, PurePosixPath
from runpy import run_path
from shutil import copyfile, disk_usage
from subprocess import PIPE, run
import sys
from tempfile import TemporaryDirectory, gettempdir


HERE = Path(__file__).resolve().parent
SOURCES = HERE / "source"
ORIGINAL = SOURCES / "peer8097"
OVERLAY = SOURCES / "transfer"
DOMAIN = SOURCES / "domain"
WEIGHTED = Path("research/frequency-weighted-native-multiplier")
SCIENTIFIC = ("price", "calendar", "raw", "exterior", "nested", "product")
INPUTS_SHA256 = "066765506f21bd204408dcf4feaab9bf41c5a9d38ceb32faaf00d1a05bd60f2a"
IMAGE_SHA256 = "2d55f0269164878a6507c6756f2f27ccd6b3a6d2cbd5b3232e89ebc8e1b7a422"
RESERVE = 8 * 1024**3
THREAD_ENV = dict.fromkeys(("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                           "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS", "NUMEXPR_NUM_THREADS"), "1")


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate input key {key!r}")
        result[key] = value
    return result


def read_json(data):
    return json.loads(data, object_pairs_hook=unique_object)


def authenticate():
    data = (HERE / "INPUTS.json").read_bytes()
    if sha256(data).hexdigest() != INPUTS_SHA256:
        raise ValueError("Unexpected pinned input manifest")
    manifest = read_json(data)
    if manifest["schema_version"] != 1:
        raise ValueError("Unexpected input manifest schema")
    files = manifest["files"]
    actual_sources = {p.relative_to(HERE).as_posix() for p in SOURCES.rglob("*")
                      if p.is_file() or p.is_symlink()}
    if actual_sources != set(files) - {"RESULT.json", "LICENSE"}:
        raise ValueError("Packaged source inventory differs")
    for name, pin in files.items():
        relative = PurePosixPath(name)
        if relative.as_posix() != name or relative.is_absolute() or ".." in relative.parts:
            raise ValueError(f"Unexpected input path {name!r}")
        path = HERE / name
        if not path.is_file() or path.resolve(strict=True) != path:
            raise ValueError(f"Not a regular source input {name!r}")
        content = path.read_bytes()
        if len(content) != pin["size"] or sha256(content).hexdigest() != pin["sha256"]:
            raise ValueError(f"Unexpected packaged bytes at {name!r}")
    return files


def reserve(scratch):
    if min(disk_usage(HERE).free, disk_usage(scratch).free) < RESERVE:
        raise RuntimeError("The 8 GiB native replay reserve is unavailable")


def python(path, *args, env, capture=False, timeout=None):
    reserve(Path(env["TMPDIR"]))
    return run([sys.executable, "-IB", str(path), *map(str, args)], check=True, text=True,
               env=env, timeout=timeout, stdout=PIPE if capture else None).stdout


def prepare(scratch, env):
    frozen = scratch / "peer"
    frozen.mkdir()
    loader = run_path(str(ORIGINAL / "verify.py"))
    old = loader["restore"](frozen)
    run_path(str(ORIGINAL / "prepare.py"))["materialize"](old)
    for name in ("check_cutoff.py", "check_stage_seam.py", "check_ordinary_floor.py", "check_w5664.py"):
        copyfile(ORIGINAL / name, old / name)
    destination = scratch / "transfer"
    observed = python(OVERLAY / "assemble.py", "--frozen", frozen, "--output", destination,
                      env=env, capture=True)
    expected = read_json((OVERLAY / "ASSEMBLY.json").read_bytes())
    if any(read_json(data) != expected for data in (
        observed, (destination / "TRANSFER-ASSEMBLY.json").read_bytes()
    )):
        raise ValueError("The independently assembled tariff transfer differs from its pin")
    narrowed = scratch / "domain"
    observed = python(DOMAIN / "assemble.py", "--frozen", destination, "--output", narrowed,
                      env=env, capture=True)
    expected = read_json((DOMAIN / "ASSEMBLY.json").read_bytes())
    if any(read_json(data) != expected for data in (
        observed, (narrowed / "DOMAIN-ASSEMBLY.json").read_bytes()
    )):
        raise ValueError("The independently assembled domain tariff differs from its pin")
    return narrowed / WEIGHTED

def install(peer, runtime, env):
    python(peer / "bootstrap.py", runtime, env=env)
    if sha256((runtime / "installations.py").read_bytes()).hexdigest() != IMAGE_SHA256:
        raise ValueError("The installed source image differs from its pin")


def setup(peer, runtime, env):
    original = peer.parent / "tiered-native-multiplier"
    python(original / "check_serial_setup.py", env=env)
    install(peer, runtime, env)
    python(peer / "check_w5664.py", runtime, env=env)


def census(peer, runtime, scratch, env):
    install(peer, runtime, env)
    stock = scratch / "census"
    stock.mkdir()
    python(OVERLAY / "check_installed.py", "--profile", "clock", "--runtime", runtime,
           "--portable", peer / "portable", "--scratch", stock, env=env, timeout=150)


def main():
    if sys.version_info[:2] != (3, 12) or not __debug__:
        raise RuntimeError("Use CPython 3.12 with assertions enabled")
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("inputs", *SCIENTIFIC, "setup", "census", "regenerate"))
    mode = parser.parse_args().mode
    inputs = authenticate()
    if mode == "inputs":
        for name in inputs:
            if name.endswith(".py"):
                compile((HERE / name).read_bytes(), name, "exec")
        print(f"PASS_10SHORTCUT_TARIFF_INPUTS {len(inputs)}")
        return
    reserve(Path(gettempdir()))
    with TemporaryDirectory(prefix="p104-10shortcut-child-tariff-") as temporary:
        scratch = Path(temporary).resolve()
        env = dict(os.environ, **THREAD_ENV, TMPDIR=str(scratch))
        peer = prepare(scratch, env)
        if mode in SCIENTIFIC:
            copyfile(HERE / "RESULT.json", peer / "RESULT.json")
            python(peer / "verify.py", mode, env=env)
        elif mode == "setup":
            setup(peer, scratch / "runtime", env)
        elif mode == "census":
            census(peer, scratch / "runtime", scratch, env)
        else:
            runtime = scratch / "runtime"
            install(peer, runtime, env)
            python(peer / "receipt.py", runtime, env=env)
            return
    print(f"PASS_10SHORTCUT_TARIFF_SCOPE {mode}")


if __name__ == "__main__":
    main()
