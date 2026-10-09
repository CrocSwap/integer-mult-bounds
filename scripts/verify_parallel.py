#!/usr/bin/env python3
"""Run the `make verify` groups concurrently, each in its own snapshot.

Some groups regenerate certificates that other groups read, so the groups
cannot share a working tree. As in CI, each group runs in a separate copy:
a one-commit git snapshot of the current working tree (tracked files with
uncommitted edits, plus untracked files that are not ignored). A group passes
when `make verify-<group>` succeeds and leaves its snapshot unchanged, the
check CI makes with `git diff --exit-code`. Logs go to build/verify-parallel/.
"""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import tempfile
import time

from run_parallel import available_cpus, memory_gib

ROOT = Path(__file__).resolve().parents[1]
LOGS = ROOT/'build'/'verify-parallel'
GIT = ['git', '-c', 'core.autocrlf=false', '-c', 'commit.gpgsign=false',
       '-c', 'user.name=verify-parallel', '-c', 'user.email=verify-parallel@localhost']


def makefile_groups():
    """The groups that `make verify` runs, in order."""
    rule = re.search(r'^verify:\n((?:\t.*\n)+)', (ROOT/'Makefile').read_text(), re.M)
    return re.findall(r'\$\(MAKE\) verify-(\S+)', rule.group(1))


def git(*args, cwd):
    return subprocess.run([*GIT, *args], cwd=cwd, check=True, capture_output=True, text=True).stdout


def snapshot(template):
    """Copy every non-ignored working-tree file into a new one-commit repository."""
    names = git('ls-files', '-z', '--cached', '--others', '--exclude-standard', cwd=ROOT).split('\0')
    for name in filter(None, names):
        source = ROOT/name
        if source.is_file() or source.is_symlink():
            (template/name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, template/name, follow_symlinks=False)
    git('init', '-q', cwd=template)
    git('add', '-A', cwd=template)
    git('commit', '-q', '--no-verify', '-m', 'verify-parallel snapshot', cwd=template)
    if git('status', '--porcelain', cwd=template):
        raise SystemExit('The snapshot is not clean; check line-ending attributes')
    return len(names)


def default_jobs():
    """One group per CPU and per 2 GiB of memory; all 14 groups at once peak near 13 GB."""
    memory = memory_gib()
    return max(1, min(available_cpus(), int(memory//2) if memory else available_cpus()))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('groups', nargs='*', help='groups to run (default: every group of `make verify`)')
    parser.add_argument('-j', '--jobs', type=int, default=default_jobs(),
                        help='groups to run at once (default: %(default)s, from CPUs and memory)')
    parser.add_argument('--keep', action='store_true', help='keep every snapshot, not only failed ones')
    args = parser.parse_args()
    groups = args.groups or makefile_groups()
    LOGS.mkdir(parents=True, exist_ok=True)
    durations_path = LOGS/'durations.json'
    durations = json.loads(durations_path.read_text()) if durations_path.exists() else {}
    # Longest first, using the previous run's times.
    queue = sorted(groups, key=lambda g: -durations.get(g, 0))
    env = {k: v for k, v in os.environ.items() if k not in ('MAKEFLAGS', 'MFLAGS', 'MAKELEVEL')}
    # Groups that run their own scripts concurrently use four processes, as on a
    # CI runner; all of them at once would add about 10 GB of peak memory.
    env.setdefault('JOBS', '4')
    make = os.environ.get('MAKE', 'make')
    work = Path(tempfile.mkdtemp(prefix='verify-parallel-'))
    start = time.monotonic()
    running, results, kept = {}, {}, []
    try:
        count = snapshot(work/'template')
        print(f'Snapshot of {count} files; running {len(groups)} groups, {args.jobs} at a time; '
              'logs in build/verify-parallel/', flush=True)
        while queue or running:
            while queue and len(running) < args.jobs:
                group = queue.pop(0)
                tree = work/group
                git('clone', '-q', str(work/'template'), str(tree), cwd=work)
                log = open(LOGS/f'{group}.log', 'w')
                process = subprocess.Popen([make, f'verify-{group}'], cwd=tree, env=env, stdout=log,
                                           stderr=subprocess.STDOUT, start_new_session=True)
                running[group] = (process, log, time.monotonic())
            time.sleep(0.5)
            for group, (process, log, began) in list(running.items()):
                if process.poll() is None:
                    continue
                del running[group]
                tree = work/group
                changed = git('status', '--porcelain', '--untracked-files=no', cwd=tree) if not process.returncode else ''
                if changed:
                    log.write('\nRegenerated files differ from the snapshot:\n'+changed)
                log.close()
                seconds = time.monotonic()-began
                ok = not process.returncode and not changed
                results[group] = (ok, seconds)
                durations[group] = round(seconds)
                status = 'PASS' if ok else ('FAIL (files changed)' if changed else 'FAIL')
                print(f'[{len(results)}/{len(groups)}] {status} {group} in {seconds/60:.1f} min', flush=True)
                if ok and not args.keep:
                    shutil.rmtree(tree)
                else:
                    kept.append(tree)
    except BaseException:
        for process, _, _ in running.values():
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            process.wait()
        shutil.rmtree(work, ignore_errors=True)
        raise
    finally:
        durations_path.write_text(json.dumps(durations, indent=1, sort_keys=True)+'\n')
    shutil.rmtree(work/'template')
    if not kept:
        work.rmdir()
    failed = sorted(g for g, (ok, _) in results.items() if not ok)
    for group in failed:
        tail = (LOGS/f'{group}.log').read_text(errors='replace').splitlines()[-30:]
        print(f'\n--- {group}: last lines of build/verify-parallel/{group}.log', *tail, sep='\n')
    if kept:
        print(f'\nKept snapshots under {work}')
    total = (time.monotonic()-start)/60
    if failed:
        raise SystemExit(f'FAILED {len(failed)} of {len(groups)} groups in {total:.1f} min: '+', '.join(failed))
    print(f'PASS all {len(groups)} groups in {total:.1f} min')


if __name__ == '__main__':
    main()
