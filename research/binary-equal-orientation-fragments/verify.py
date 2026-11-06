#!/usr/bin/env python3
"""Self-contained source-bound replay of the caller and complete invoice.

Jerry Chen / @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
No predecessor implementation is imported or executed.
"""
from hashlib import sha1, sha256
from pathlib import Path
import json
import runpy
import sys

HERE = Path(__file__).resolve().parent
EXPECTED = {
    "frozen/caller6726.py", "frozen/economics-pricing6726.py",
    "frozen/economics-result6726.json", "frozen/HEADER-SATURATION6764.md",
    "frozen/ROOT6726.json", "frozen/concurrent-NOTICE",
    "frozen/concurrent-construct.py",
    "frozen/LICENSE", "frozen/NOTICE",
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def main():
    need(not sys.argv[1:], "This replay accepts no arguments")
    sources = json.loads((HERE / "SOURCES.json").read_text())
    retained = sources["retained_sources"]
    need(len(retained) == len(EXPECTED), "Complete retained source inventory")
    need({row["local_path"] for row in retained} == EXPECTED,
         "Unexpected or missing retained source")
    for row in retained:
        raw = (HERE / row["local_path"]).read_bytes()
        need(sha256(raw).hexdigest() == row["sha256"],
             "Retained source SHA256: " + row["local_path"])
        blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
        need(sha1(blob).hexdigest() == row["git_blob"],
             "Retained source Git blob: " + row["local_path"])
    for name in ("verify_caller.py", "compare_callers.py", "verify_economics.py"):
        runpy.run_path(str(HERE / name), run_name="__main__")
    print("PASS_BINARY_EQUAL_ORIENTATION_FRAGMENT_PACKAGE")


if __name__ == "__main__":
    main()
