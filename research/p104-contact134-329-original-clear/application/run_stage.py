"""Record one bounded native or signed candidate replay."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time


def utc():
    return datetime.now(timezone.utc).isoformat()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("native", "signed"))
    parser.add_argument("--overlay", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--bootstrap", action="store_true")
    args = parser.parse_args()
    command = [sys.executable, "-I", "-B", str(args.overlay.resolve() / "application.py"),
               "--stage", args.stage, "--work", str(args.work.resolve())]
    if args.bootstrap:
        command.append("--bootstrap")
    started = utc()
    timestamp = time.monotonic()
    base = args.work.parent / f"{args.work.name}-stage"
    cap = 480
    with base.with_suffix(".stdout").open("x") as out, base.with_suffix(".stderr").open("x") as err:
        runner = subprocess.Popen(command, stdout=out, stderr=err, start_new_session=True)
        try:
            status = runner.wait(timeout=cap)
        except subprocess.TimeoutExpired:
            os.killpg(runner.pid, signal.SIGTERM)
            runner.wait(timeout=10)
            status = 124
    result = {"stage": args.stage, "started_utc": started, "finished_utc": utc(),
              "seconds": time.monotonic() - timestamp, "exit": status, "cap_seconds": cap,
              "python": sys.version.split()[0], "bootstrap": args.bootstrap}
    base.with_suffix(".json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))
    raise SystemExit(status)


if __name__ == "__main__":
    main()
