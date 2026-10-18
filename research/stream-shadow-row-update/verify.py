#!/usr/bin/env python3
"""Build and inspect the Lean proof of the scalar-shadow row recurrence."""
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}
FORBIDDEN = re.compile(
    r"\b(sorry|admit|axiom|native_decide|implemented_by|extern|unsafe|opaque)\b"
    r"|set_option\s+(?!maxHeartbeats|maxRecDepth)"
)
DEADLINE = None


def fail(message):
    print("FAIL", message, flush=True)
    raise SystemExit(1)


def strip_comments(source):
    source = re.sub(r"/-.*?-[/]", " ", source, flags=re.S)
    return re.sub(r"--[^\n]*", " ", source)


def run(argv):
    print("$", " ".join(argv), flush=True)
    remaining = DEADLINE - time.monotonic()
    if remaining <= 1:
        fail("the 580-second replay budget is exhausted")
    try:
        result = subprocess.run(
            argv, cwd=HERE, text=True, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, timeout=remaining - 1, check=False
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        fail(f"command could not complete: {exc}")
    if result.returncode:
        print(result.stdout[-6000:], flush=True)
        fail(f"{argv[0]} exited {result.returncode}")
    return result.stdout


def main():
    global DEADLINE
    DEADLINE = time.monotonic() + 580
    sources = sorted(HERE.glob("*.lean"))
    if not sources:
        fail("no Lean source files")
    for path in sources:
        match = FORBIDDEN.search(strip_comments(path.read_text(encoding="utf-8")))
        if match:
            fail(f"forbidden token {match.group(0)!r} in {path.name}")
    print(f"sources: no admitted axioms or unsafe declarations in {len(sources)} files", flush=True)

    run(["lake", "exe", "cache", "get"])
    build = run(["lake", "build"])
    for line in build.splitlines():
        if "warning" in line.lower() or "error" in line.lower() or "Build completed" in line:
            print(line, flush=True)

    output = run(["lake", "env", "lean", "PrintAxioms.lean"])
    print(output.strip(), flush=True)
    reports = {}
    for match in re.finditer(r"'([\w.']+)' depends on axioms: \[([^\]]*)\]", output):
        reports[match.group(1)] = {name.strip() for name in match.group(2).split(",") if name.strip()}
    for match in re.finditer(r"'([\w.']+)' does not depend on any axioms", output):
        reports[match.group(1)] = set()
    for name in (
        "StreamShadowRowUpdate.scalRun_append",
        "StreamShadowRowUpdate.S_append_event",
    ):
        if name not in reports:
            fail(f"missing axiom report for {name}")
        extra = reports[name] - ALLOWED_AXIOMS
        if extra:
            fail(f"{name} uses unapproved axioms: {sorted(extra)}")
    print("PASS_STREAM_SHADOW_ROW_UPDATE", flush=True)


if __name__ == "__main__":
    main()
