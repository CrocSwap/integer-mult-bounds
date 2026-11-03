"""Serial bounded Linux measurements; preserve the complete frozen precision contract."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import platform
import signal
import statistics
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
SOURCE = HERE
CLOSURE = ('frozen.py','primitive_profile.py','guard.py','dispatch.py','inputs/PR5848.tar','../feasibility/fraction_table.py','../feasibility/finite.py','/usr/lib/python3.12/fractions.py','../feasibility/actual_audit.py')
TIMEOUT = 180
RSS_CAP = 1024**3
OUTPUT_CAP = 2*1024**2
AGGREGATE = 600
PREVIOUS_WALL_SECONDS = 0

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def inventory():
    result = {}
    for name in CLOSURE:
        path = SOURCE / name
        if path.is_symlink() or not path.is_file():
            raise ValueError('Regular complete runtime file: ' + name)
        result[name] = [sha(path.read_bytes()), path.stat().st_mode & 0o777]
    return result

def group_rss(group):
    total = 0
    count = 0
    for p in Path('/proc').iterdir():
        if not p.name.isdigit():
            continue
        try:
            raw = (p/'stat').read_text()
            fields = raw[raw.rfind(')')+2:].split()
            if int(fields[2]) == group:
                total += int(fields[21])*os.sysconf('SC_PAGE_SIZE')
                count += 1
        except (FileNotFoundError, ProcessLookupError, PermissionError):
            pass
    return total, count

def run(label, script, optimized=False):
    records = HERE/'runs'
    records.mkdir(exist_ok=True)
    prior = list(records.glob('*/receipt.json'))
    spent = PREVIOUS_WALL_SECONDS + sum(json.loads(p.read_bytes())['wall_seconds'] for p in prior)
    if spent >= AGGREGATE:
        raise ValueError('Aggregate budget consumed')
    folder = records/label
    folder.mkdir()
    before = inventory()
    env = os.environ.copy()
    for key in ('PYTHONPATH','PYTHONOPTIMIZE','PYTHONINSPECT','PYTHONSTARTUP','PYTHONPYCACHEPREFIX'):
        env.pop(key,None)
    env.update(PYTHONHASHSEED='0', LC_ALL='C.UTF-8', TZ='UTC')
    usage = folder/'usage.json'
    with tempfile.TemporaryDirectory(prefix='linux5757-bytecode-') as cache:
        command = ['/usr/bin/python3.12', '-B', '-X', 'pycache_prefix='+cache]
        if optimized:
            command.append('-O')
        command.append(str(SOURCE/script))
        timed = ['/usr/bin/time','-f','{"user_seconds":%U,"system_seconds":%S,"kernel_max_rss_kib":%M,"exit":%x}', '-o', str(usage),'--',*command]
        start = time.monotonic()
        peak = 0
        stop = None
        with (folder/'stdout.txt').open('wb') as out, (folder/'stderr.txt').open('wb') as err:
            p = subprocess.Popen(timed, cwd=SOURCE, env=env, stdout=out, stderr=err, start_new_session=True)
            try:
                while p.poll() is None:
                    rss, _ = group_rss(p.pid)
                    peak = max(peak,rss)
                    elapsed = time.monotonic()-start
                    if rss > RSS_CAP:
                        stop='sampled_group_rss_cap'
                    elif elapsed > min(TIMEOUT,AGGREGATE-spent):
                        stop='wall_or_aggregate_cap'
                    elif max((folder/'stdout.txt').stat().st_size,(folder/'stderr.txt').stat().st_size)>OUTPUT_CAP:
                        stop='output_cap'
                    if stop:
                        os.killpg(p.pid,signal.SIGKILL)
                        break
                    time.sleep(0.05)
                code=p.wait()
            finally:
                try: os.killpg(p.pid,signal.SIGKILL)
                except ProcessLookupError: pass
                p.wait()
        elapsed = time.monotonic()-start
    stdout=(folder/'stdout.txt').read_bytes()
    stderr=(folder/'stderr.txt').read_bytes()
    after=inventory()
    measurement=None
    if usage.exists():
        try: measurement=json.loads(usage.read_bytes())
        except json.JSONDecodeError: measurement={'raw':usage.read_text()}
    receipt={'label':label,'script':script,'optimized':optimized,'wall_seconds':elapsed,
             'exit':code,'termination':stop,'sampled_process_group_rss_bytes':peak,
             'usage':measurement,'stdout_sha256':sha(stdout),'stdout_bytes':len(stdout),
             'stderr_sha256':sha(stderr),'stderr_bytes':len(stderr),
             'source_inventory_sha256':sha(json.dumps(before,sort_keys=True,separators=(',',':')).encode()),
             'source_bytes_and_modes_unchanged':before==after,
             'python':sys.version,'platform':platform.platform(),
             'runner_sha256':sha(Path(__file__).read_bytes()),'runtime_policy_sha256':sha(json.dumps(CLOSURE).encode())}
    receipt['status']='PASS' if code==0 and stop is None and not stderr and before==after else 'STOP'
    (folder/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps(receipt,sort_keys=True),flush=True)
    if receipt['status']!='PASS':
        raise SystemExit(1)
    return receipt
