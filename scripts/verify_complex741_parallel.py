#!/usr/bin/env python3
"""Concurrent cold replay of the pinned #741 complex supplier.

Executes research/complex-sw4-frame8/verify.py itself, statement by statement.
Each run(...) call is handed to verify.py's own run function on a worker thread
once the stages it depends on (STAGE_DEPS) have passed. Statements that read
stage outputs run unchanged, in their original order, after every stage has
passed. Stage commands, environment, logs, post-checks and receipts are
verify.py's own; only the order of independent stages changes. STAGE_DEPS is
checked against a recorded per-stage file-access trace
(research/complex741-parallel-replay/ACCESS.json).
"""
import argparse
import ast
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
import hashlib
import os
from pathlib import Path
import sys
import threading
import types

ROOT = Path(__file__).resolve().parents[1]
VERIFY = ROOT / 'research/complex-sw4-frame8/verify.py'
VERIFY_SHA256 = '7706065e3d2934ea493910638b40e6285348d337507e0fb695d8d1e536926637'

# Direct prerequisites of each verify.py stage, in verify.py's order.
STAGE_DEPS = {
    'ancestral558-fresh': (),
    'gauge44-exact-construction': (),
    'notri56-construction': ('gauge44-exact-construction',),
    'notri-control-g44': ('gauge44-exact-construction',),
    'layered66-construction': ('gauge44-exact-construction', 'notri56-construction'),
    'p6n-cold72-construction': ('layered66-construction',),
    'four-promotions': ('p6n-cold72-construction',),
    'promotion-controls': ('p6n-cold72-construction',),
    'sw4-read-exchanges': ('four-promotions',),
    'eight-B-frame-construction': ('sw4-read-exchanges',),
    'all728-columns-native': ('eight-B-frame-construction',),
    'both-native-ledgers': ('all728-columns-native',),
    'independent-native-controls': ('both-native-ledgers',),
    'residual-wrappers': ('independent-native-controls',),
    'all-native-phase-edges': ('residual-wrappers',),
    'independent-scalar-frames-cones': ('eight-B-frame-construction',),
    'inherited-cold-controls': ('eight-B-frame-construction',),
    'eight-frame-controls': ('eight-B-frame-construction',),
    'owner-construction-controls': (),
    'strict-global-admission': ('all-native-phase-edges',),
    'independent-literal-map-moment': ('strict-global-admission',),
    'independent-two-engine-outer47': ('strict-global-admission',),
}
# verify.py's ancestral linkage loop reads the fresh ancestral replay. Sequentially it
# runs right after that stage; here it runs after all stages, so it must not
# conflict with any later stage.
DEFERRED_DEPS = {'ancestral-link': ('ancestral558-fresh',)}


def check_pin(path):
    digest = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    if digest != VERIFY_SHA256:
        raise SystemExit(f'{path} has sha256 {digest}, not the pinned {VERIFY_SHA256}; '
                         're-derive STAGE_DEPS before scheduling a changed verify.py')


def _run_call(stmt):
    return (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call)
            and isinstance(stmt.value.func, ast.Name) and stmt.value.func.id == 'run')


def _pure(stmt):
    """An assignment that only combines paths and literals (str() allowed): no file access."""
    return isinstance(stmt, ast.Assign) and not any(
        isinstance(n, ast.Call) and not (isinstance(n.func, ast.Name) and n.func.id == 'str')
        for n in ast.walk(stmt))


def stage_names(source):
    return [s.value.args[0].value for s in ast.parse(source).body if _run_call(s)]


def stage_commands(source, package, work):
    """Script and arguments of every run(...) call, as verify.py would pass them."""
    ns, cmds = {'P': Path(package), 'O': Path(work)}, {}
    ns['run'] = lambda name, script, *args: cmds.setdefault(name, [str(script), *map(str, args)])
    for stmt in ast.parse(source).body:
        if _run_call(stmt) or _pure(stmt):
            exec(compile(ast.Module([stmt], []), 'verify.py', 'exec'), ns)
    return cmds


def run_graph(order, deps, job, workers):
    """Run job(name) for every name once its deps have returned; re-raise the first failure."""
    for i, name in enumerate(order):
        assert set(deps[name]) <= set(order[:i]), (name, deps[name])
    done, results, running, error = set(), {}, {}, None
    with ThreadPoolExecutor(max_workers=workers) as pool:
        while True:
            if error is None:
                for name in order:
                    if (name not in results and name not in running.values()
                            and set(deps[name]) <= done and len(running) < workers):
                        running[pool.submit(job, name)] = name
            if not running:
                break
            finished, _ = wait(running, return_when=FIRST_COMPLETED)
            for future in finished:
                name = running.pop(future)
                try:
                    results[name] = future.result()
                    done.add(name)
                except BaseException as e:
                    error = error or e
                    results[name] = None
    if error is not None:
        raise error
    return results


def _ancestors(deps):
    anc = {}
    for name in deps:
        anc[name] = set()
        for d in deps[name]:
            anc[name] |= {d} | anc.get(d, set())
    return anc


def conflicts(deps, access):
    """Unordered stage pairs where one writes a path the other reads, writes or lists.

    access[stage] has relative POSIX paths under 'r' (read), 'w' (written, renamed or
    deleted), 'ls' (directory listed) and 'mkdir' (directory created).
    """
    anc, names, found = _ancestors(deps), list(deps), []
    def touches(x, other):
        seen = set(other.get('r', ())) | set(other.get('w', ()))
        dirs = tuple(d.rstrip('/') + '/' for d in other.get('ls', ()))
        return ([p for p in x.get('w', ()) if p in seen or p.startswith(dirs)]
                + [p for p in x.get('mkdir', ()) if p.startswith(dirs)])
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if a in anc[b] or b in anc[a]:
                continue
            xa, xb = access.get(a, {}), access.get(b, {})
            for path in sorted(set(touches(xa, xb) + touches(xb, xa))):
                found.append((a, b, path))
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--work', type=Path, required=True)
    ap.add_argument('--jobs', type=int, default=min(8, os.cpu_count() or 1))
    a = ap.parse_args()
    if sys.flags.optimize:
        raise SystemExit('Assertions are required; do not use -O')
    source = VERIFY.read_text(encoding='utf-8')
    check_pin(VERIFY)
    assert stage_names(source) == list(STAGE_DEPS), 'stage table differs from verify.py'
    body = ast.parse(source).body
    ns = {'__name__': '__verify__', '__file__': str(VERIFY), '__builtins__': __builtins__}
    sys.argv = [str(VERIFY), '--work', str(a.work)]
    exec_stmt = lambda s: exec(compile(ast.Module([s], []), str(VERIFY), 'exec'), ns)
    split = next(i for i, s in enumerate(body) if isinstance(s, ast.FunctionDef) and s.name == 'run') + 1
    for stmt in body[:split]:
        exec_stmt(stmt)
    original_run, deferred, calls = ns['run'], [], {}
    ns['run'] = lambda name, script, *args: calls.setdefault(name, (script, args))
    for stmt in body[split:]:
        if _run_call(stmt) or _pure(stmt):
            exec_stmt(stmt)  # registers a stage, or binds a path with no file access
        else:
            deferred.append(stmt)
    assert list(calls) == list(STAGE_DEPS)
    order, O = list(STAGE_DEPS), ns['O']

    records, lock = {}, threading.Lock()
    def job(name):
        # verify.py's run, with private globals so its progress file is written here in stage order.
        g = dict(ns, stages=[], dump=lambda *_: None)
        script, args = calls[name]
        types.FunctionType(original_run.__code__, g)(name, script, *args)
        with lock:
            records[name] = g['stages'][0]
            ns['dump'](O / 'STAGES.json', [records[n] for n in order if n in records])
        return records[name]

    run_graph(order, STAGE_DEPS, job, a.jobs)
    ns['stages'][:] = [records[n] for n in order]
    ns['dump'](O / 'STAGES.json', ns['stages'])
    for stmt in deferred:
        exec_stmt(stmt)


if __name__ == '__main__':
    main()
