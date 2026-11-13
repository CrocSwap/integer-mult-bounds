"""Execute the two isolated, bounded complete verifier stages in order."""
from pathlib import Path
from datetime import datetime, timezone
import json
from subprocess import run, TimeoutExpired
from sys import argv, executable
from time import monotonic

ROOT = Path(__file__).resolve().parent
STAGES = (
    ("native", "producer54/validation_native/run.py", 480, "PASS_ROLE902_COMPLETE_NATIVE"),
    ("signed", "producer54/validation_signed/role902_run.py", 495, "PASS_ROLE902_COMPLETE_SIGNED_APPLICATION"),
)


def utc():
    return datetime.now(timezone.utc).isoformat()


def main():
    assert __debug__ and len(argv) <= 2
    stages = STAGES if len(argv) == 1 else tuple(stage for stage in STAGES if stage[0] == argv[1])
    assert stages, "unknown replay stage"
    receipts = ROOT / "receipts"
    for name, script, cap, marker in stages:
        started = utc()
        timer = monotonic()
        stdout = receipts / (name + ".stdout")
        with stdout.open("x") as output, (receipts / (name + ".stderr")).open("x") as error:
            print("START", name, started, "cap", cap, flush=True)
            try:
                result = run([executable, "-I", "-B", script], cwd=ROOT, stdout=output, stderr=error, timeout=cap)
                code = result.returncode
            except TimeoutExpired:
                code = 124
        if code == 0:
            assert marker in stdout.read_text(), marker
        receive = dict(argv=["python3.12", "-I", "-B", script], start_utc=started, end_utc=utc(),
                       elapsed_seconds=monotonic()-timer, exit=code, cap_seconds=cap, expected_marker=marker)
        (receipts / (name + ".json")).write_text(json.dumps(receive,sort_keys=True,indent=2)+"\n")
        print("END", name, code, receive["elapsed_seconds"], flush=True)
        if code:
            raise SystemExit(code)


if __name__ == "__main__":
    main()
