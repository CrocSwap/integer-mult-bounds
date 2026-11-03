"""Absolute-path adapter for the frozen NEW literal-control harness only.

The registered runner substitutes a relative package path. Resolve this adapter's
own directory, authenticate the harness, and invoke its main in a non-main module.
This does not authorize helper.main, actual images, decoders or native execution.
"""
from pathlib import Path
import hashlib
import json
import stat
import sys
import types

HARNESS_SHA = "cbbe3139f6d67d2da653f5aaf4a62f0ab108f5a1cde37e0f444f3ef826ae9ed6"
HARNESS_BYTES = 8023
HELPER_SHA = "56b44235f55685d61e5c8b8099d825b4ec5a53987910f506dffad309c12ffb53"

class AdapterRefusal(ValueError):
    pass

def need(ok, reason):
    if not ok:
        raise AdapterRefusal(reason)

def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    need(not args, "adapter accepts no arguments")
    package = Path(__file__).resolve().parent
    path = package / "controls-v1/test_literal_candidates_v1.py"
    info = path.lstat()
    need(stat.S_ISREG(info.st_mode) and info.st_size == HARNESS_BYTES,
         "harness type/size pin")
    raw = path.read_bytes()
    need(len(raw) == HARNESS_BYTES and hashlib.sha256(raw).hexdigest() == HARNESS_SHA,
         "harness byte/hash pin")
    module = types.ModuleType("frozen_literal_export_harness_" + HARNESS_SHA[:16])
    module.__file__ = str(path)
    # Compile only the SAME authenticated bytes, after every harness pin check.
    exec(compile(raw, str(path), "exec"), module.__dict__)
    need(module.__name__ != "__main__", "non-main harness namespace")
    return module.main(["--helper", str(package / "repair-v2/passive_image_candidates_v2.py"),
                        "--sha256", HELPER_SHA])

if __name__ == "__main__":
    try:
        result = main()
    except Exception as exc:
        print(json.dumps({"status": "ADAPTER_PREFLIGHT_REFUSAL", "case_count": 0,
                          "passed_count": 0, "failed_count": 0,
                          "error": type(exc).__name__ + ": " + str(exc)[:400],
                          "actual_image_pass": False, "full_C05": False,
                          "full_V03": False}, sort_keys=True), file=sys.stderr)
        result = 2
    raise SystemExit(result)
