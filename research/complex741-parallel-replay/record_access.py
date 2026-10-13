#!/usr/bin/env python3
"""Record which files each stage of the sequential #741 complex replay touches.

  record_access.py --record DIR   runs research/complex-sw4-frame8/verify.py unchanged in a
                                  throwaway venv whose interpreter logs every open, listing,
                                  rename, delete and mkdir (Python audit hooks, also in
                                  -I children), then reduces the log into DIR/ACCESS.json.
  record_access.py --reduce TRACE --work WORK --out ACCESS.json
                                  reduces an existing trace.

Stages run one at a time, so each traced process belongs to the stage whose top-level
command most recently started. Paths are made relative to the replay directory (work/).
Reads outside work/ are dropped after checking that no stage writes there.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import verify_complex741_parallel as par

HOOK = r'''
import os, sys
_here = os.path.dirname(os.path.abspath(__file__))
try:
    with open(os.path.join(_here, 'complex741_trace_target.txt'), encoding='utf-8') as _f:
        _target = _f.read().strip()
except OSError:
    _target = ''
if _target:
    import atexit, json, time
    _seen, _busy = set(), [False]
    _log = open(os.path.join(_target, f'{os.getpid()}.jsonl'), 'a', encoding='utf-8')
    _log.write(json.dumps({'pid': os.getpid(), 'time': time.time(), 'orig_argv': sys.orig_argv, 'cwd': os.getcwd()}) + '\n')
    _WRITE = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_APPEND | os.O_TRUNC
    def _rec(kind, path):
        if isinstance(path, int) or path is None:
            return
        key = (kind, os.path.abspath(os.fsdecode(path)))
        if key not in _seen:
            _seen.add(key)
            _log.write(json.dumps(key) + '\n')
    def _hook(event, args):
        if _busy[0]:
            return
        _busy[0] = True
        try:
            if event == 'open':
                path, mode, flags = args
                w = mode is not None and any(c in mode for c in 'wax+') or mode is None and flags & _WRITE
                _rec('w' if w else 'r', path)
            elif event in ('os.listdir', 'os.scandir'):
                _rec('ls', args[0] if args and args[0] is not None else '.')
            elif event == 'os.rename':
                _rec('w', args[0]); _rec('w', args[1])
            elif event in ('os.remove', 'os.rmdir', 'shutil.rmtree', 'os.mkdir'):
                _rec('w', args[0])
            elif event == 'shutil.copyfile':
                _rec('r', args[0]); _rec('w', args[1])
        finally:
            _busy[0] = False
    atexit.register(_log.flush)
    sys.addaudithook(_hook)
'''


def record(out):
    out = out.resolve()
    out.mkdir(parents=True)
    venv, trace, work = out / 'venv', out / 'trace', out / 'work'
    subprocess.run([sys.executable, '-m', 'venv', '--without-pip', str(venv)], check=True)
    vpy = venv / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    site = Path(subprocess.run([str(vpy), '-c', 'import sysconfig;print(sysconfig.get_paths()["purelib"])'],
                               check=True, capture_output=True, text=True).stdout.strip())
    trace.mkdir()
    (site / 'complex741_trace_hook.py').write_text(HOOK, encoding='utf-8')
    (site / 'complex741_trace.pth').write_text('import complex741_trace_hook\n', encoding='utf-8')
    (site / 'complex741_trace_target.txt').write_text(str(trace), encoding='utf-8')
    subprocess.run([str(vpy), '-B', str(par.VERIFY), '--work', str(work)], cwd=ROOT, check=True)
    (site / 'complex741_trace_target.txt').unlink()
    return reduce(trace, work)


def reduce(trace, work):
    work = Path(work).resolve()
    procs = []
    for f in Path(trace).glob('*.jsonl'):
        for x in map(json.loads, f.read_text(encoding='utf-8').splitlines()):
            if isinstance(x, dict):  # a header; a reused pid appends a new process to the same file
                procs.append((x, []))
            else:
                procs[-1][1].append(x)
    procs.sort(key=lambda p: p[0]['time'])
    parent, children = procs[0], procs[1:]
    argv = parent[0]['orig_argv']
    assert Path(parent[0]['cwd'], argv[argv.index('--work') - 1]).resolve() == par.VERIFY, argv
    cmds = par.stage_commands(par.VERIFY.read_text(encoding='utf-8'), par.VERIFY.parent, work)
    runner = str(par.VERIFY.parent / 'vendor/main/research/complex-k492-owner-repair/vendor/multicold/code/run_portable.py')
    names, owner, k = list(cmds), [], 0
    for head, events in children:
        a = head['orig_argv']
        if k < len(names) and a[1:3] == ['-B', runner] and a[3:] == cmds[names[k]]:
            k += 1
        assert k, ('process before the first stage', a)
        owner.append(names[k - 1])
    assert k == len(names), ('stages without a traced process', names[k:])
    wk, root = os.path.normcase(str(work)) + os.sep, os.path.normcase(str(ROOT)) + os.sep

    def rel(path):
        p = os.path.normcase(path)
        if p.startswith(wk):
            return 'work/' + path[len(wk):].replace(os.sep, '/')
        return ('repo/' + path[len(root):].replace(os.sep, '/')) if p.startswith(root) else None

    stages = {n: {'r': set(), 'w': set(), 'ls': set(), 'mkdir': set()} for n in names}
    outside_writes, temp_writes = {}, {}
    tmp = os.path.normcase(tempfile.gettempdir()) + os.sep
    for name, (head, events) in zip(owner, children):
        for kind, path in events:
            if kind not in ('r', 'w', 'ls'):
                continue
            r = rel(path)
            if kind == 'w' and os.path.isdir(path):
                kind = 'mkdir'
            if r is None or not r.startswith('work/'):
                if kind in ('w', 'mkdir'):
                    if os.path.normcase(path).startswith(tmp):
                        temp_writes[name] = temp_writes.get(name, 0) + 1  # tempfile's unique names
                    else:
                        outside_writes.setdefault(name, set()).add(r or path)
                continue
            stages[name][kind].add(r)
        stages[name]['w'].add(f'work/{name}.log')  # written by the driver for this stage
    link = {'r': set(), 'w': {'work/ANCESTRAL-LINK.json'}}
    for kind, path in parent[1]:
        r = rel(path) if kind == 'r' else None
        if r and r.startswith('work/ancestral558/'):
            link['r'].add(r)
    stages['ancestral-link'] = link
    for name, x in stages.items():
        assert 'work/STAGES.json' not in x.get('r', ()) and 'work' not in x.get('ls', ()), name
    result = {
        'replayed': str(par.VERIFY.relative_to(ROOT).as_posix()),
        'verify_sha256': par.VERIFY_SHA256,
        'processes': len(procs),
        'outside_work_writes': {k: sorted(v) for k, v in outside_writes.items()},
        'temp_dir_writes': temp_writes,
        'stages': {n: {k: sorted(v) for k, v in x.items() if v} for n, x in stages.items()},
    }
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--record', type=Path)
    ap.add_argument('--reduce', type=Path)
    ap.add_argument('--work', type=Path)
    ap.add_argument('--out', type=Path)
    a = ap.parse_args()
    if a.record:
        result, out = record(a.record), a.out or a.record / 'ACCESS.json'
    else:
        result, out = reduce(a.reduce, a.work), a.out
    out.write_text(json.dumps(result, indent=1, sort_keys=True) + '\n', encoding='utf-8')
    deps = dict(par.STAGE_DEPS, **par.DEFERRED_DEPS)
    found = par.conflicts(deps, result['stages'])
    print(f"{result['processes']} processes, {len(result['stages'])} stages, "
          f"outside writes {result['outside_work_writes'] or 'none'}, unordered conflicts {found or 'none'}")
    sys.exit(1 if found or result['outside_work_writes'] else 0)


if __name__ == '__main__':
    main()
