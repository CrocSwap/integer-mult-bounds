# SPDX-License-Identifier: Apache-2.0
"""The PR442 hosting windows of the nine-stage PR589 bit template.

The idle schedule follows global_k.py's recipe (K = 4 bank pairs, L = 9 stages): a local cover sweep
per stage, the idle children it inserts, and the bridges. schedule() writes it out here; at run time
it is compared event by event with the schedule obtained by executing the pinned global_k.py's own
recipe() and its idle-insertion if-block (extracted with ast, their asserts included) inside a
transcription of the surrounding loop of global_k.main() (level bookkeeping, the sweep, bridge and
exchange appends, and its stage-order, bridge-level and exchange checks). A child's window is the set of stages whose sweep falls strictly after the child's pair
was last touched and before the child is inserted, on another pair. Three implementations of that
predicate (this one, PR442 hosting_core.windows and audit_hosted_k.windows) are run on the one
shared schedule and must agree; the frozen PR589 hosting selection must lie inside the windows.
Standard library only.
"""
import ast
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VENDOR = ROOT / 'research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/vendor'
HOSTING_CORE = VENDOR / 'idle-axis-hosting/hosting_core.py'
AUDIT_HOSTED = VENDOR / 'e8-r715-eleven-stage-whole/code/audit_hosted_k.py'
SELECTION = ROOT / 'research/e8-bit-p111-tuned/data/selection9-p111.json'
GLOBAL_K = VENDOR / 'e8-r715-eleven-stage-whole/code/global_k.py'
K, L = 4, 9


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def schedule():
    events = [('local', 0, 0)]
    stage = 1
    for j in range(K):
        events.append(('local', stage, j)); stage += 1
        if j < K - 1:
            events.append(('bridge', j, j + 1))
        events.append(('local', stage, j)); stage += 1
        if j < K - 1:
            events.append(('bridge', j, j + 1))
    for j in reversed(range(K - 1)):
        events.append(('bridge', j + 1, j))
    sched, level = [], [-1] * K
    for e in events:
        if e[0] == 'local':
            _, s, p = e
            level[p] = s
            sched.append(dict(kind='local_cover_sweep', stage=s, pair=p))
            if s % 2 == 1 and s <= 2 * K - 3:
                j = (s + 1) // 2; level[j] = s; sched.append(dict(kind='idle', pair=j, rank=7 * (s + 1)))
            elif s % 2 == 0 and 2 <= s <= 2 * K - 2:
                j = s // 2; level[j] = s; sched.append(dict(kind='idle', pair=j, rank=7))
            elif s == 2 * K:
                for j in range(K):
                    sched.append(dict(kind='idle', pair=j, rank=7 * (2 * K - level[j]))); level[j] = 2 * K
        else:
            sched.append(dict(kind='bridge', dst=e[1], src=e[2]))
    sched.append(dict(kind='exchange'))
    i = 0
    for e in sched:
        if e['kind'] == 'idle':
            e['idx'] = i
            i += 1
    return sched


def global_k_schedule(k=K):
    """global_k.py's schedule: its recipe(K) and the idle-insertion if-block of main(), both extracted with
    ast and executed, inside a transcription of the surrounding loop (the scalar replay is not needed)."""
    tree = ast.parse(GLOBAL_K.read_text())
    recipe_fn = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'recipe']
    rules = [n for n in ast.walk(tree) if isinstance(n, ast.If) and ast.unparse(n.test) == 's % 2 == 1 and s <= 2 * K - 3']
    if len(recipe_fn) != 1 or len(rules) != 1:
        raise ValueError('global_k.py: recipe() or the idle-insertion rule not found exactly once')
    ns = {}
    exec(compile(ast.Module(body=recipe_fn, type_ignores=[]), str(GLOBAL_K), 'exec'), ns)
    rule = compile(ast.Module(body=rules, type_ignores=[]), str(GLOBAL_K), 'exec')
    levels, sched = [-1] * k, []
    for e in ns['recipe'](k):
        if e['kind'] == 'local':
            s, p = e['stage'], e['pair']
            if levels[p] != s - 1:
                raise ValueError('global_k.py: stage order')
            levels[p] = s
            sched.append(dict(kind='local_cover_sweep', **{x: v for x, v in e.items() if x != 'kind'}))
            exec(rule, dict(s=s, K=k, levels=levels, schedule=sched))
        elif e['kind'] == 'bridge':
            if levels[e['dst']] != levels[e['src']]:
                raise ValueError('global_k.py: bridge levels')
            sched.append(e)
        else:
            if levels != [2 * k] * k:
                raise ValueError('global_k.py: exchange levels')
            sched.append(e)
    return sched


def _events(sched):
    keys = dict(local_cover_sweep=('stage', 'pair'), idle=('pair', 'rank'), bridge=('dst', 'src'), exchange=())
    return [(e['kind'],) + tuple(e[x] for x in keys[e['kind']]) for e in sched]


def windows(sched):
    out, last, seen = {}, {}, []
    for pos, e in enumerate(sched):
        if e['kind'] == 'local_cover_sweep':
            seen.append((pos, e['stage'], e['pair'])); last[e['pair']] = pos
        elif e['kind'] == 'bridge':
            last[e['dst']] = pos; last[e['src']] = pos
        elif e['kind'] == 'idle':
            out[e['idx']] = (e['pair'], e['rank'],
                             tuple(sorted(s for q, s, p in seen if last.get(e['pair'], -1) < q < pos and p != e['pair'])))
    return out


def three_way(sched):
    """The windows of `sched` after checking that the three predicates agree on it (no anchor)."""
    mine = windows(sched)
    hc = _load('pr442_hosting_core', HOSTING_CORE)
    ah = _load('audit_hosted_k', AUDIT_HOSTED)
    hc_sched = [dict(e, kind='local') if e['kind'] == 'local_cover_sweep' else e for e in sched if e['kind'] != 'exchange']
    theirs = {i: (p, r, tuple(sorted(st))) for i, (p, r, st) in hc.windows(hc_sched).items()}
    W, rank, pair = ah.windows(sched)
    audit = {i: (pair[i], rank[i], tuple(sorted(W[i]))) for i in W}
    if not (mine == theirs == audit):
        raise ValueError('window predicates disagree')
    return mine


def checked_windows(sched=None):
    """{child: (capacity, stages)} for the children that can host, after the schedule is matched with
    global_k.py and the three window predicates agree on it."""
    sched = schedule() if sched is None else sched
    if _events(sched) != _events(global_k_schedule()):
        raise ValueError('schedule differs from the one global_k.py produces')
    mine = three_way(sched)
    win = {i: (r, st) for i, (p, r, st) in mine.items() if r > 0 and st}
    for i, w, s, n in json.loads(SELECTION.read_text())['bit']['stages']:
        if s not in win[i][1]:
            raise ValueError('frozen selection entry outside its window')
    return win
