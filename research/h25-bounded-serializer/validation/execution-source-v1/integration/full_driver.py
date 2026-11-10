"""Four fixed finite serializer operations under the unchanged parent guard.

Trusted finite host, no hostile concurrent mutation. This authenticates declared
files/origins, not arbitrary process memory or original complete H25 custody.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import sys

STAGE = Path(__file__).resolve().parents[1]
PACKAGE = STAGE / "package"
PACKAGE_SHA256 = "5cbf632753d81558487f453e2ac9b92a02a0b26c0f6da59b28c71c6db415ae1e"
LOCAL = ("component_consumer", "reference", "bounded_serialization", "serialization_controls")
ENV = {"PYTHONHASHSEED": "0", "LC_ALL": "C.UTF-8", "TZ": "UTC",
       "PYTHONDONTWRITEBYTECODE": "1", "PYTHONNOUSERSITE": "1", "PYTHONSAFEPATH": "1"}
LANES = {"serializer-controls": "controls", "serializer-baseline-2048": "baseline",
         "serializer-candidate-2048": "candidate"}


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def small(path):
    with path.open("rb") as stream:
        raw = stream.read(1048577)
    need(len(raw) <= 1048576, "Custody metadata exceeded 1MiB")
    return raw


def identity(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns)


def file_pin(path):
    need(path.is_absolute() and path.resolve() == path, "Pin path must be resolved absolute")
    before = path.lstat()
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb", buffering=0) as stream:
        opened = os.fstat(stream.fileno())
        need(stat.S_ISREG(opened.st_mode), "Pin is not a regular file")
        count, hasher = 0, hashlib.sha256()
        while count < opened.st_size:
            raw = stream.read(min(1048576, opened.st_size - count))
            need(bool(raw), "Pinned file ended early")
            hasher.update(raw)
            count += len(raw)
        after = os.fstat(stream.fileno())
    need(identity(before) == identity(opened) == identity(after) == identity(path.lstat()),
         "Pinned file changed while hashing")
    return {"bytes": count, "sha256": hasher.hexdigest()}


def origins(runtime):
    observed = {}
    for name, module in tuple(sys.modules.items()):
        filename = getattr(module, "__file__", None)
        if filename is None:
            continue
        actual = str(Path(filename).resolve())
        if name == "__main__":
            expected = str(Path(__file__).resolve())
        elif name in LOCAL:
            expected = str(PACKAGE / (name + ".py"))
        else:
            expected = runtime["module_paths"].get(name)
        need(actual == expected, "Unadmitted file-backed module origin: " + name)
        observed[name] = actual
    return observed


def custody(anchor):
    need(small(STAGE / "RUNTIME-PINS.sha256") == anchor, "Runtime anchor changed")
    expected_runtime = anchor.decode("ascii").strip()
    need(len(expected_runtime) == 64 and all(c in "0123456789abcdef" for c in expected_runtime),
         "Malformed parent runtime anchor")
    runtime_raw = small(STAGE / "RUNTIME-PINS.json")
    need(hashlib.sha256(runtime_raw).hexdigest() == expected_runtime,
         "Runtime manifest differs from independent parent anchor")
    runtime = json.loads(runtime_raw)
    need(runtime["schema"] == "serializer-finite-runtime-pins-v1", "Runtime schema differs")
    need(runtime["python_version"] == sys.version and
         runtime["executable_realpath"] == str(Path(sys.executable).resolve()) == "/usr/bin/python3.12",
         "Interpreter differs from parent runtime")
    need(runtime["environment"] == ENV and all(os.environ.get(k) == v for k, v in ENV.items()),
         "Finite environment differs")
    need(not any(name in os.environ for name in
         ("PYTHONPATH", "PYTHONOPTIMIZE", "PYTHONINSPECT", "PYTHONSTARTUP", "PYTHONPYCACHEPREFIX")),
         "Forbidden Python startup environment")
    need(sys.flags.no_user_site == 1 and sys.flags.safe_path and sys.dont_write_bytecode,
         "Required finite startup flags absent")
    package_raw = small(PACKAGE / "SOURCE-PINS.json")
    need(hashlib.sha256(package_raw).hexdigest() == PACKAGE_SHA256, "Serializer manifest changed")
    package = json.loads(package_raw)
    expected_paths = set(package["files"]) | {"SOURCE-PINS.json"}
    actual_paths = set()
    for path in PACKAGE.rglob("*"):
        need(not path.is_symlink(), "Symlink in frozen serializer")
        if path.is_file():
            actual_paths.add(str(path.relative_to(PACKAGE)))
    need(actual_paths == expected_paths, "Serializer file inventory changed")
    for relative, pin in package["files"].items():
        path = PACKAGE / relative
        need(file_pin(path) == {"bytes": pin["bytes"], "sha256": pin["sha256"]} and
             oct(stat.S_IMODE(path.stat().st_mode)) == pin["mode_octal"],
             "Serializer payload changed: " + relative)
    for filename, pin in runtime["files"].items():
        need(file_pin(Path(filename)) == pin, "Runtime file changed: " + filename)
    return {"runtime_manifest_sha256": expected_runtime, "runtime_file_count": len(runtime["files"]),
            "serializer_manifest_sha256": PACKAGE_SHA256, "serializer_payload_files": len(package["files"]),
            "module_origins": origins(runtime), "assumptions": runtime["assumptions"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--lanes", choices=tuple(LANES), required=True)
    parser.add_argument("--finite-only", action="store_true")
    args = parser.parse_args()
    need(args.finite_only, "This adapter admits only fixed finite operations")
    mode = LANES[args.lanes]
    need(sys.flags.optimize in ((0, 1) if mode == "controls" else (0,)), "Undeclared optimization mode")
    need(not args.output.exists(), "Refusing earlier adapter evidence")
    args.output.mkdir(parents=True)
    boundary = {"scope": "Supported finite serializer host only; no full H25 custody/performance claim",
                "mode": mode, "fixture_rows": None if mode == "controls" else 2048,
                "python_version": sys.version, "executable": sys.executable,
                "executable_realpath": str(Path(sys.executable).resolve()),
                "optimization": sys.flags.optimize, "no_user_site": sys.flags.no_user_site,
                "safe_path": sys.flags.safe_path, "dont_write_bytecode": sys.dont_write_bytecode,
                "environment": {key: os.environ.get(key) for key in ENV}, "status": "STARTED"}
    primary, post_error, anchor = None, None, None
    try:
        anchor = small(STAGE / "RUNTIME-PINS.sha256")
        boundary["before"] = custody(anchor)
        need(not any(name in sys.modules for name in LOCAL), "Component module preloaded")
        sys.path.insert(0, str(PACKAGE))
        import component_consumer
        need(Path(component_consumer.__file__).resolve() == PACKAGE / "component_consumer.py",
             "Actual consumer source differs")
        receipt = component_consumer.run_component(mode, args.output / "component", rows=2048)
        boundary["component_status"] = receipt["status"]
        boundary["status"] = "FINITE_COMPONENT_RETURNED"
    except BaseException as error:
        primary = error
        boundary["status"] = "PRIMARY_ERROR"
        boundary["primary_error_type"] = type(error).__name__
        raise
    finally:
        try:
            need(anchor is not None, "Runtime anchor was not obtained")
            boundary["after"] = custody(anchor)
        except BaseException as error:
            post_error = error
            boundary["postcheck_error_type"] = type(error).__name__
            if primary is None:
                boundary["status"] = "POSTCHECK_ERROR"
        try:
            (args.output / "adapter-boundary.json").write_text(json.dumps(boundary, sort_keys=True, indent=2)
                                                              + "\n", encoding="utf-8")
        except BaseException:
            if primary is None and post_error is None:
                raise
        if primary is None and post_error is not None:
            raise post_error
    print(json.dumps({"status": boundary["status"], "mode": mode,
                      "optimization": sys.flags.optimize}, sort_keys=True))


if __name__ == "__main__":
    main()
