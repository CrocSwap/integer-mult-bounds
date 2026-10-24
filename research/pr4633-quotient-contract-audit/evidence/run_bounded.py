#!/usr/bin/env python3
"""Run one audit command under a sampled 1 GiB process-group RSS limit."""
import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import time

p = argparse.ArgumentParser()
p.add_argument('--name', required=True)
p.add_argument('--seconds', type=int, default=1200)
p.add_argument('command', nargs=argparse.REMAINDER)
a = p.parse_args()
out = Path(__file__).resolve().parent
start = time.monotonic()
peak = 0
reason = None
with (out / (a.name + '.log')).open('w') as log:
    child = subprocess.Popen(a.command, stdout=log, stderr=subprocess.STDOUT,
                             start_new_session=True)
    while child.poll() is None:
        rss = 0
        for entry in Path('/proc').iterdir():
            if not entry.name.isdigit():
                continue
            try:
                fields = (entry / 'stat').read_text().rsplit(')', 1)[1].split()
                if int(fields[2]) == child.pid:
                    rss += int(fields[21]) * os.sysconf('SC_PAGE_SIZE')
            except (FileNotFoundError, ProcessLookupError, PermissionError):
                pass
        peak = max(peak, rss)
        if peak > 1024**3 or time.monotonic() - start > a.seconds:
            reason = 'memory' if peak > 1024**3 else 'timeout'
            os.killpg(child.pid, signal.SIGKILL)
            break
        time.sleep(.1)
    code = child.wait()
result = dict(command=a.command, cwd=os.getcwd(), exit_code=code,
              elapsed_seconds=round(time.monotonic()-start, 3),
              peak_sampled_group_rss_bytes=peak, stop_reason=reason,
              memory_limit_bytes=1024**3, timeout_seconds=a.seconds)
(out / (a.name + '.receipt.json')).write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result), flush=True)
raise SystemExit(code if code >= 0 else 1)
