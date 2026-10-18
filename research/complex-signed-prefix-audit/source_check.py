#!/usr/bin/env python3
"""Replay the byte-pinned original local driver, including all 25 controls.

Gareth Davidson, with OpenAI Codex assistance. Apache-2.0.
This is separate from the independent signed-prefix verifier.
"""
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify as audit


def run():
    audit.pins()
    with tempfile.TemporaryDirectory(prefix="signed-prefix-source-") as temp:
        work = Path(temp)
        with tarfile.open(audit.ROOT / audit.ARCHIVE) as archive:
            for name in ("CANONICAL-WORD.json.gz", "LOCAL-PROGRAMS.json.gz"):
                (work / name).write_bytes(archive.extractfile(audit.BASE + name).read())
            retained = json.loads(archive.extractfile(audit.BASE + "INDEPENDENT-LOCAL-REPLAY.json").read())
        # -I ignores PYTHONOPTIMIZE; no -O is passed. All original asserts run.
        proc = subprocess.run([sys.executable, "-I", "-B", str(audit.ROOT / audit.LOCAL_CHECKER), str(work)],
                              text=True, capture_output=True, timeout=180)
        audit.need(proc.returncode == 0, "original driver failed:\n" + proc.stdout + proc.stderr)
        fresh = json.loads((work / "INDEPENDENT-LOCAL-REPLAY.json").read_text())
        audit.need(fresh == retained, "complete original local receipt changed")
        audit.need(len(fresh["negative_controls_rejected"]) == 25, "original control coverage")
        print("PASS_ORIGINAL_LOCAL_DRIVER", "orientations=2 columns=704 controls=25 receipt_identical")
        print("receipt_sha256=" + audit.digest(audit.canonical(fresh)))


if __name__ == "__main__":
    run()
