# SPDX-License-Identifier: Apache-2.0
# Prepared by Sagar Thakrar with substantial Anthropic Claude assistance.
"""Differential tests: every replaced primitive against the pinned module's own function.

Compared for each case: the exception (type and message) or, on success, the exact values, the value types' rational
equality, and the key order of every row.  Run: python3 -I -B tests/test_exactness.py [--public-fraction]
"""
import copy
import gzip
import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
CODE = ROOT / 'research/complex-sw4-frame8/vendor/pr635/research/complex-571-cold14-st2/code'
sys.path.insert(0, str(CODE))
sys.path.insert(0, str(HERE))
import hpe_audit_and_transport as atc          # noqa: E402  (pinned, never installed into in this process)
import fast_hpe_transport as fh                # noqa: E402


def outcome(fn, *args):
    try:
        return ('ok', fn(*args))
    except Exception as e:                     # noqa: BLE001  - exception parity is the point
        return ('raise', type(e).__name__, str(e))


def rows_equal(a, b):
    return len(a) == len(b) and all(x == y and list(x) == list(y) for x, y in zip(a, b))


def random_gate(rng, m, malformed):
    if malformed and rng.random() < 0.3:
        return rng.choice([
            ['add', rng.randrange(m), rng.randrange(m)],                       # short gate
            ['add', 0, 0, 1, 1, []],                                           # target == source
            ['add', m + 3, rng.randrange(m), 1, 1, []],                        # out-of-range target
            ['add', -1, rng.randrange(m - 1), 1, 2, []],                       # negative target
            ['add', 'x', 0, 1, 1, []],                                         # non-int target
            ['add', 0, 1, 1, 0, []],                                           # b = 0
            ['add', 0, 1, 1.0, 2, []],                                         # float coefficient
            ['add', 0, 1, True, 2, []],                                        # bool coefficient
            ['add', 0, 1, '1', 2, []],                                         # str coefficient
            ['scale', rng.randrange(m), 0, 1, []],                             # zero scale
            ['scale', rng.randrange(m), 3, 0, []],                             # b = 0 scale
            ['scale', m + 5, 1, 2, []],                                        # out-of-range scale
            ['add', 1, 0, 0, 1, []],                                           # zero coefficient
        ])
    if rng.random() < 0.15:
        return ['scale', rng.randrange(m), rng.choice([1, -1, 2, -2, 4, 3, -8]), rng.choice([1, 2, 4, 3, -2]), []]
    t = rng.randrange(m)
    s = rng.choice([x for x in range(m) if x != t])
    return ['add', t, s, rng.choice([1, -1, 2, -2, 3, -5, 0, 7]), rng.choice([1, 1, 2, 4, 8, 3, 6, -4]), []]


def dyadic_gate(rng, m):
    if rng.random() < 0.1:
        return ['scale', rng.randrange(m), rng.choice([1, -1, 2, -2, 4, -8]), rng.choice([1, 2, 4, 8]), []]
    t = rng.randrange(m)
    s = rng.choice([x for x in range(m) if x != t])
    return ['add', t, s, rng.choice([1, -1, 2, -3, 5, -7, 1]), rng.choice([1, 2, 4, 8, 64, 1 << 30]), []]


def check_apply(apply_under_test, trials=4000, seed=11):
    rng = random.Random(seed)
    for trial in range(trials):
        m = rng.randint(2, 7)
        start = rng.choice(['identity', 'empty', 'fraction'])
        if start == 'identity':
            base = [{r: F(1)} for r in range(m)]
        elif start == 'empty':
            base = [{} if r % 2 else {r: F(1)} for r in range(m)]
        else:
            base = [{r: F(rng.randint(-3, 3) or 1, rng.choice([1, 2, 3, 4]))} for r in range(m)]
        rows0 = copy.deepcopy(base)
        rows1 = [{j: fh.Qx(x.numerator, x.denominator) if trial % 2 else x for j, x in r.items()} for r in base]
        for _ in range(rng.randint(1, 40)):
            e = random_gate(rng, m, malformed=trial % 3 == 0)
            r0 = outcome(atc.apply, copy.deepcopy(e), rows0)
            r1 = outcome(apply_under_test, copy.deepcopy(e), rows1)
            if r0 != r1 or not rows_equal(rows0, rows1):
                return dict(ok=False, trial=trial, gate=e, pinned=r0, fast=r1)
            if r0[0] == 'raise':
                break
    return dict(ok=True, trials=trials)


def check_state_maps(trials=300, seed=5):
    orig, fast = atc.state_maps, fh.make_state_maps(atc.state_maps)
    rng = random.Random(seed)
    for trial in range(trials):
        m = rng.randint(2, 8)
        if trial % 4 == 0:          # mixed and malformed programs: exercises every fallback and exception path
            prog = [random_gate(rng, m, malformed=True) for _ in range(rng.randint(0, 60))]
        else:                       # well-formed dyadic programs: exercises the scaled-integer path
            prog = [dyadic_gate(rng, m) for _ in range(rng.randint(0, 120))]
        r0 = outcome(orig, copy.deepcopy(prog), m)
        r1 = outcome(fast, copy.deepcopy(prog), m)
        if r0[0] != r1[0] or (r0[0] == 'raise' and r0 != r1):
            return dict(ok=False, trial=trial, pinned=r0[:3], fast=r1[:3])
        if r0[0] == 'ok' and not all(rows_equal(a, b) for a, b in zip(r0[1], r1[1])):
            return dict(ok=False, trial=trial, reason='rows differ')
    return dict(ok=fast.dyadic_calls >= 3*trials//4, trials=trials, dyadic_path=fast.dyadic_calls)


def real_prefix_state_maps(word_path, routing_path):
    """state_maps on the actual audit prefix of a real word (precondition + compensation + A + cut + B)."""
    word = json.loads(gzip.decompress(Path(word_path).read_bytes()))
    v, n = word['report']['v'], 2*word['report']['v'] + word['report']['R']
    matrix = [{r: F(1)} for r in range(n)]
    main = word['A'] + word['cut'] + word['B']
    for e in main:
        atc.apply(e, matrix)
    dirty = [{} for _ in range(n)]
    for r in range(v, 2*v):
        dirty[r] = {j: x for j, x in matrix[r].items() if j >= 2*v}
    for e in word['precondition']:
        atc.apply(e, dirty)
    compensation = [['add', r, j, -q.numerator, q.denominator, []] for r in range(v, 2*v) for j, q in sorted(dirty[r].items())]
    prefix = word['precondition'] + compensation + main
    P0, I0 = atc.state_maps(prefix, n)
    fast = fh.make_state_maps(atc.state_maps)
    P1, I1 = fast(prefix, n)
    return dict(ok=rows_equal(P0, P1) and rows_equal(I0, I1) and fast.dyadic_calls == 1, gates=len(prefix),
                P_nonzeros=sum(map(len, P0)), Pinv_nonzeros=sum(map(len, I0)))


def check_basis(trials=3000, seed=3):
    memo = fh.make_basis(atc.basis)
    rng = random.Random(seed)
    for trial in range(trials):
        vs = [rng.randrange(1, 512) for _ in range(rng.randint(0, 6))]
        if trial % 10 == 0 and vs:
            vs[0] = rng.choice([float(vs[0]), True, str(vs[0])])
        for _ in range(2):                   # second call exercises the cache
            if outcome(atc.basis, list(vs)) != outcome(memo, list(vs)):
                return dict(ok=False, trial=trial, vectors=vs)
    return dict(ok=True, trials=trials, cached=len(memo.cache))


def check_copy():
    rng = random.Random(7)
    for _ in range(2000):
        e = [rng.choice(['add', 'scale']), rng.randrange(9), rng.randrange(9), rng.randint(-4, 4), 2,
             rng.choice([None, [], [rng.randrange(512) for _ in range(3)], [[1, 2], [3]]])]
        c = fh._deepcopy(e)
        if c != e or c is e or (isinstance(e[-1], list) and c[-1] is e[-1]):
            return dict(ok=False, gate=e)
    other = {'k': [1, (2, 3)]}
    return dict(ok=fh._deepcopy(other) == other and fh._deepcopy(other) is not other)


def nested(depth):
    x = []
    for _ in range(depth):
        x = [x]
    return x


def check_deep_copy():
    """Deep structures must hit the recursion limit exactly as copy.deepcopy does (the fast path is depth <= 2)."""
    rows = []
    for depth in (1, 2, 3, 300, 700, 2000):
        e = ['add', 1, 2, 1, 1, nested(depth), [1, 2]]
        a = outcome(copy.deepcopy, e)
        b = outcome(fh._deepcopy, e)
        rows.append((depth, a[0], b[0]))
        if a[0] != b[0] or (a[0] == 'ok' and a[1] != b[1]) or (a[0] == 'raise' and a[1] != b[1]):
            return dict(ok=False, depth=depth, pinned=a[:2], fast=b[:2])
    return dict(ok=True, cases=rows)


def load_instance(name):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, CODE / 'hpe_audit_and_transport.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_outcome(module, word, routing, out):
    import contextlib
    import io
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            module.run(word, routing, out)
    except Exception as e:                     # noqa: BLE001
        return ('raise', type(e).__name__, repr(e.args))
    text = '\n'.join(ln for ln in (out / 'SCALAR-FRAME-AUDIT.json').read_text().splitlines() if not ln.startswith('  "seconds":'))
    return ('ok', text, (out / 'CANONICAL-WORD.json.gz').read_bytes(), (out / 'FULL-WORD.json.gz').read_bytes())


def check_run_level(word_path, routing_path):
    """run() of a pinned instance versus an accelerated instance on the honest word and deep-nesting variants."""
    pinned, fast = load_instance('hpe_pinned_instance'), load_instance('hpe_fast_instance')
    fh._accelerate(fast, True)
    base = json.loads(gzip.decompress(Path(word_path).read_bytes()))
    variants = {'honest': base}
    for depth in (300, 700):
        w = copy.deepcopy(base)
        w['A'][0] = w['A'][0][:-1] + [nested(depth), w['A'][0][-1]]
        variants['extra_field_depth_%d' % depth] = w
        w = copy.deepcopy(base)
        w['A'][0] = w['A'][0][:-1] + [nested(depth)]
        variants['frame_field_depth_%d' % depth] = w
    rows, tmp = {}, Path(tempfile.mkdtemp())
    try:
        for name, w in variants.items():
            path = tmp / (name + '.json.gz')
            path.write_bytes(gzip.compress(json.dumps(w).encode(), mtime=0))
            a = run_outcome(pinned, path, Path(routing_path), tmp / ('p-' + name))
            b = run_outcome(fast, path, Path(routing_path), tmp / ('f-' + name))
            rows[name] = a[0] if a[0] == 'ok' else a[1]
            if a != b:
                return dict(ok=False, variant=name, pinned=a[:3] if a[0] == 'raise' else 'ok', fast=b[:3] if b[0] == 'raise' else 'ok')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return dict(ok=True, variants=rows)


def check_import_hook():
    """The hook loads whatever file the script's own import rule selects, and accelerates only validated bytes."""
    tmp = Path(tempfile.mkdtemp())
    try:
        sib = tmp / 'sibling'
        sib.mkdir()
        (sib / 'probe.py').write_text(
            'import os, sys\nsys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))\n'
            'import hpe_audit_and_transport as atc\nprint(atc.__file__, getattr(atc, "_fast_hpe_marker", None) is not None)\n')
        shutil.copy(CODE / 'hpe_audit_and_transport.py', sib / 'hpe_audit_and_transport.py')
        env = dict(os.environ, PR635_CODE=str(CODE))
        run = lambda *flags: subprocess.run([sys.executable, '-I', '-B', str(HERE / 'fast_controls.py'), *flags, str(sib / 'probe.py')],
                                            env=env, capture_output=True, text=True)
        same = run('--require-fast')
        with open(sib / 'hpe_audit_and_transport.py', 'a') as f:
            f.write('\n')
        changed = run()
        changed_required = run('--require-fast')
        want = str(sib / 'hpe_audit_and_transport.py')
        ok = (same.returncode == 0 and same.stdout.split() == [want, 'True']
              and changed.returncode == 0 and changed.stdout.split() == [want, 'False'] and 'not validated' in changed.stderr
              and changed_required.returncode != 0 and 'not validated' in changed_required.stderr)
        return dict(ok=ok, sibling_selected_over_PR635_CODE=same.stdout.split()[:1] == [want])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_guard():
    tmp = Path(tempfile.mkdtemp())
    try:
        shutil.copy(CODE / 'hpe_audit_and_transport.py', tmp / 'hpe_audit_and_transport.py')
        with open(tmp / 'hpe_audit_and_transport.py', 'a') as f:
            f.write('\n')
        code = ('import sys; sys.path.insert(0, %r); sys.path.insert(0, %r)\n'
                'import hpe_audit_and_transport as atc, fast_hpe_transport as fh\n'
                'print(fh.install(atc), atc.apply is fh.fast_apply)\n'
                'fh.install(atc, require=True)\n') % (str(tmp), str(HERE))
        r = subprocess.run([sys.executable, '-I', '-B', '-c', code], capture_output=True, text=True)
        return dict(ok=r.stdout.strip() == 'False False' and r.returncode != 0 and 'not validated' in r.stderr)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def sabotaged_apply(e, rows):
    """Negative control: identical to fast_apply but keeps zero entries; check_apply must reject it."""
    if e[0] != 'add':
        return fh.fast_apply(e, rows)
    _, target, source, a, b, *_ = e
    assert target != source
    q = fh.Qx(a, b)
    for j, x in list(rows[source].items()):
        rows[target][j] = rows[target].get(j, 0) + q*x


def main():
    public = '--public-fraction' in sys.argv
    if public and not os.environ.get('FAST_HPE_PUBLIC_FRACTION'):
        env = dict(os.environ, FAST_HPE_PUBLIC_FRACTION='1')
        raise SystemExit(subprocess.call([sys.executable, '-I', '-B', __file__, '--public-fraction'], env=env))
    word = os.environ.get('FAST_HPE_TEST_WORD')
    report = dict(
        fraction_constructor='public' if fh._mk is F else '_from_coprime_ints',
        apply=check_apply(fh.fast_apply),
        apply_sabotage_detected=not check_apply(sabotaged_apply)['ok'],
        zero_coefficient=outcome(fh.fast_apply, ['add', 1, 0, 0, 1, []], [{0: F(1)}, {0: F(2)}]) == ('ok', None),
        state_maps=check_state_maps(),
        basis=check_basis(),
        copy=check_copy(),
        deep_copy=check_deep_copy(),
        import_hook=check_import_hook(),
        guard=check_guard())
    if word:
        report['state_maps_real_prefix'] = real_prefix_state_maps(word, os.environ['FAST_HPE_TEST_ROUTING'])
        report['run_level'] = check_run_level(word, os.environ['FAST_HPE_TEST_ROUTING'])
    ok = all(v['ok'] if isinstance(v, dict) else bool(v) for k, v in report.items() if k != 'fraction_constructor')
    print(json.dumps(report, indent=1, default=str))
    print('PASS_FAST_HPE_EXACTNESS' if ok else 'FAIL_FAST_HPE_EXACTNESS')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
