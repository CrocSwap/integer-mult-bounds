"""Replay the integral-fringe construction from the packaged immutable source."""

from argparse import ArgumentParser
from hashlib import sha256
import json
import os
from pathlib import Path, PurePosixPath
from shutil import copyfile, disk_usage
from subprocess import PIPE, run
import sys
from tempfile import TemporaryDirectory, gettempdir


HERE = Path(__file__).resolve().parent
SOURCES = HERE / "source"
HANDOFF = SOURCES / "paired-768"
PERIOD = HANDOFF / "r420/overlay"
FRINGE = HANDOFF / "r428"
WEIGHTED = Path("research/frequency-weighted-native-multiplier")
SCIENTIFIC = ("price", "calendar", "raw", "exterior", "nested", "product")
INPUTS_SHA256 = "36de89cde22bb3fbf6389bba09d9a0855d27a1707e27e41207e5c490dfe58a51"
IMAGE_SHA256 = "6dc565fad3b91bcb43ff71397897afcc54fd5f9d595a8f88b91234994d8e70be"
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


def python(path, *args, env, capture=False):
    reserve(Path(env["TMPDIR"]))
    return run([sys.executable, "-IB", str(path), *map(str, args)], check=True, text=True,
               env=env, stdout=PIPE if capture else None).stdout


def prepare(scratch, env):
    frozen = scratch / "period"
    observed = python(PERIOD / "assemble.py", "--package-root", SOURCES / "peer8094",
                      "--output", frozen, env=env, capture=True)
    if read_json(observed) != read_json((PERIOD / "ASSEMBLY.json").read_bytes()):
        raise ValueError("The independently assembled predecessor differs from its pin")
    destination = scratch / "fringe"
    observed = python(FRINGE / "assemble.py", "--frozen", frozen, "--output", destination,
                      env=env, capture=True)
    expected = read_json((FRINGE / "ASSEMBLY.json").read_bytes())
    if any(read_json(data) != expected for data in (
        observed, (destination / "FRINGE-ASSEMBLY.json").read_bytes()
    )):
        raise ValueError("The independently assembled integral-fringe source differs from its pin")
    return destination / WEIGHTED


def install(peer, runtime, env):
    python(peer / "bootstrap.py", runtime, env=env)
    if sha256((runtime / "installations.py").read_bytes()).hexdigest() != IMAGE_SHA256:
        raise ValueError("The installed source image differs from its pin")


def native(peer, runtime, scratch, env):
    python(HANDOFF / "r417/physical/check.py", "--runtime", runtime, "--relay-receipt",
           HANDOFF / "r416/signed/RECEIPT.json", env=env)
    for kind in (0, 1):
        python(HANDOFF / "r418/typed/check.py", "--runtime", runtime, "--kind", kind,
               "--oracle", HANDOFF / "r418/oracle/RECEIPT.json", env=env)
    setup = scratch / "setup"
    setup.mkdir()
    python(FRINGE / "check_setup.py", "--handoff-root", HANDOFF, "--runtime", runtime,
           "--portable", peer / "portable", "--scratch", setup, env=env)


def main():
    if sys.version_info[:2] != (3, 12) or not __debug__:
        raise RuntimeError("Use CPython 3.12 with assertions enabled")
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("inputs", *SCIENTIFIC, "native", "regenerate"))
    mode = parser.parse_args().mode
    inputs = authenticate()
    if mode == "inputs":
        for name in inputs:
            if name.endswith(".py"):
                compile((HERE / name).read_bytes(), name, "exec")
        print(f"PASS_INTEGRAL_FRINGE_INPUTS {len(inputs)}")
        return
    reserve(Path(gettempdir()))
    with TemporaryDirectory(prefix="p104-k7-integral-fringe-") as temporary:
        scratch = Path(temporary).resolve()
        env = dict(os.environ, **THREAD_ENV, TMPDIR=str(scratch))
        peer = prepare(scratch, env)
        if mode in SCIENTIFIC:
            copyfile(HERE / "RESULT.json", peer / "RESULT.json")
            python(peer / "verify.py", mode, env=env)
        else:
            runtime = scratch / "runtime"
            install(peer, runtime, env)
            if mode == "regenerate":
                python(peer / "receipt.py", runtime, env=env)
                return
            native(peer, runtime, scratch, env)
    print(f"PASS_INTEGRAL_FRINGE_SCOPE {mode}")


if __name__ == "__main__":
    main()
