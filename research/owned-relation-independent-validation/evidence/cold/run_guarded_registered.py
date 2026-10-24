#!/usr/bin/env python3
"""One bounded serial registered replay; local review orchestration only."""
from pathlib import Path
import datetime, hashlib, json, os, signal, subprocess, sys, time

HERE = Path(__file__).resolve().parent
REPO = HERE / 'snapshot'
PACKAGE = 'research/kappa-owned-relation-20261023'
LIMIT_SECONDS = 1260
LIMIT_KIB = 1024 * 1024

def hashes():
    return {str(p.relative_to(REPO)): hashlib.sha256(p.read_bytes()).hexdigest()
            for root in ('research', 'scripts', 'docs')
            for p in sorted((REPO / root).rglob('*')) if p.is_file()}

def descendants(pid):
    found = set()
    todo = [pid]
    while todo:
        current = todo.pop()
        if current in found:
            continue
        found.add(current)
        try:
            raw = Path('/proc', str(current), 'task', str(current), 'children').read_text()
            todo.extend(map(int, raw.split()))
        except (FileNotFoundError, ProcessLookupError):
            pass
    return found

def rss(pid):
    try:
        lines = Path('/proc', str(pid), 'status').read_text().splitlines()
        return next((int(x.split()[1]) for x in lines if x.startswith('VmRSS:')), 0)
    except (FileNotFoundError, ProcessLookupError):
        return 0

def main():
    before = hashes()
    (HERE / 'PRE-RUN-HASHES.json').write_text(json.dumps(before, indent=2) + '\n')
    env = {k: v for k, v in os.environ.items()
           if not k.startswith('GIT_') and k not in ('PYTHONPATH', 'PYTHONOPTIMIZE', 'LEAN_AUDIT_BIN')}
    env.update(PYTHONDONTWRITEBYTECODE='1', PYTHONUNBUFFERED='1',
               GIT_NO_REPLACE_OBJECTS='1', GIT_NO_LAZY_FETCH='1', GIT_GRAFT_FILE=os.devnull)
    scratch = HERE / 'scratch'
    scratch.mkdir(exist_ok=False)
    env['TMPDIR'] = str(scratch)
    command = [sys.executable, '-B', 'scripts/research_package.py', '--package', PACKAGE]
    started = time.monotonic()
    peak = 0
    stop = None
    samples = []
    with (HERE / 'REGISTERED-COLD.stdout.log').open('wb') as out, (HERE / 'REGISTERED-COLD.stderr.log').open('wb') as err:
        process = subprocess.Popen(command, cwd=REPO, env=env, stdout=out, stderr=err,
                                   start_new_session=True)
        (HERE / 'LIVE-HANDLE.json').write_text(json.dumps({'pid': process.pid, 'argv': command,
            'cwd': str(REPO), 'utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}, indent=2) + '\n')
        while process.poll() is None:
            seconds = time.monotonic() - started
            members = descendants(process.pid)
            total = sum(rss(pid) for pid in members)
            peak = max(peak, total)
            samples.append({'seconds': seconds, 'rss_kib': total, 'pids': sorted(members)})
            if seconds > LIMIT_SECONDS:
                stop = 'total_timeout'
            if total > LIMIT_KIB:
                stop = 'aggregate_descendant_rss'
            if stop:
                os.killpg(process.pid, signal.SIGKILL)
                break
            time.sleep(0.1)
        code = process.wait()
    after = hashes()
    (HERE / 'POST-RUN-HASHES.json').write_text(json.dumps(after, indent=2) + '\n')
    changed = sorted(k for k in before.keys() | after.keys() if before.get(k) != after.get(k))
    result = {'status': 'PASS_COMPLETE_REGISTERED_NORMAL_AND_OPTIMIZED' if code == 0 and stop is None and not changed else 'FAIL_OR_INCOMPLETE',
              'argv': command, 'cwd': str(REPO), 'exit': code, 'resource_stop': stop,
              'seconds': time.monotonic() - started, 'peak_sampled_descendant_rss_kib': peak,
              'total_timeout_seconds': LIMIT_SECONDS, 'rss_limit_kib': LIMIT_KIB,
              'per_registered_command_timeout_seconds': 600, 'scientific_bytes_changed': changed,
              'hash_inventory_files': len(before), 'samples': samples,
              'scope': 'One own execution of the registered normal then optimized commands; no independent reviewer script rerun, Lean, native build or historical archive replay.'}
    (HERE / 'BOUNDED-REGISTERED-RUN.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'samples'}), flush=True)
    return 0 if result['status'].startswith('PASS_') else 1

if __name__ == '__main__':
    raise SystemExit(main())
