"""Execute the two isolated, bounded complete verifier stages in order."""
from pathlib import Path
from datetime import datetime, timezone
import json
from subprocess import run, TimeoutExpired
from sys import argv, executable
from time import monotonic

ROOT = Path(argv[1]).resolve()
STAGES = (
    ("native", "producer54/validation_native/run.py", 480, "PASS_COMPOSED_7481_7542_COMPLETE_NATIVE"),
    ("signed", "producer54/validation_signed/composed_run.py", 495, "PASS_COMPOSED_7481_7542_COMPLETE_SIGNED_APPLICATION"),
)


def utc():
    return datetime.now(timezone.utc).isoformat()


def main():
    assert __debug__
    receipts = ROOT / "receipts"
    for name, script, cap, marker in STAGES:
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
