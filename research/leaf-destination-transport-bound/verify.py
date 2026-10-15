"""Registered verifier: exact maximum of leaf-destination transport, max(1, floor(log2 n)).

Runs from the repository root (or anywhere): sibling modules are resolved relative to this
file, and the PR628 source is resolved relative to the repository root.
Checks (exact free noncommutative algebra; finite instances of the written proof in PROOF.md):
  0. pinned inputs; census/check2 words equal the literal PR628 `compose` event order, n=1..40;
  1. check2 `ok` over n=1..40 (INV, L1, X, case table, E(n), Lemma P) and family up to n=128;
  2. fam_closed over n=2..200 (closed form of the family row), Lemma P formula k=1..128;
  3. Lemmas L1, L2, S for n<=32, both signs; independent census engine E(n) for n<=24;
  4. two mutation controls (unreversed inverse, ceil-half split) that must be rejected.
Prints PASS_LEAF_DESTINATION_EXACT_MAXIMUM. Standard library only. Apache-2.0.
"""
import ast
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import sys
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PR628 = 'research/dirty-cubic-precision/vendor/628/dirty.py'
sys.path.insert(0, str(HERE))

import census  # noqa: E402
import check2  # noqa: E402
import fam_closed  # noqa: E402
import lemmas  # noqa: E402

fl = check2.fl


def need(ok, message):
    if not ok:
        raise SystemExit('FAIL ' + message)


def pinned_inputs():
    rows = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))['files']
    count = 0
    for row in rows:
        if row['usage'] == 'input':
            data = (ROOT / row['path']).read_bytes()
            need(hashlib.sha256(data).hexdigest() == row['sha256'], 'pinned input drift: ' + row['path'])
            count += 1
    need(count >= 1, 'no pinned PR628 input')


def pr628_compose():
    """Extract the literal `compose` function of PR628 and record its leaf events."""
    path = ROOT / PR628
    tree = ast.parse(path.read_text(encoding='utf-8'))
    functions = [f for f in tree.body if isinstance(f, ast.FunctionDef) and f.name == 'compose']
    need(len(functions) == 1, 'literal PR628 compose function')
    code = compile(ast.Module(body=functions, type_ignores=[]), str(path), 'exec')

    def events(n, sign):
        ports = [[0] for _ in range((n - 1).bit_length() + 2)]
        ids = {id(p): i for i, p in enumerate(ports)}
        out = []

        def leaf(x, y, factor, phases, beta, bits, d, sgn, stats):
            out.append((ids[id(x)], ids[id(y)], factor, sgn))

        def require(ok, message):
            if not ok:
                raise ValueError(message)

        env = {'c': SimpleNamespace(need=require, norm2=lambda t: t * t), 'leaf': leaf}
        exec(code, env)
        env['compose'](ports[0], ports[1], list(range(n)), ports[2:], [1], Fraction(1, 2), 64, 1, sign)
        return out
    return events


def source_words(hi):
    events = pr628_compose()
    for n in range(1, hi + 1):
        for s in (1, -1):
            w = census.word(n, s)
            need(w == events(n, s), 'census word != PR628 compose, n=%d sign=%d' % (n, s))
            need([e for e, _ in check2.gen(n, s)] == w, 'check2 word != census word, n=%d' % n)


def check2_ok(hi, famhi):
    for n in range(1, hi + 1):
        need(check2.check_inv(n, 'ok'), 'Lemma I, n=%d' % n)
        need(check2.check_P(n, 'ok', 1), 'Lemma P, n=%d' % n)
        E, xm, xs, fails = check2.full_pass(n, 'ok')
        need(not fails, 'check2 ok n=%d: %r' % (n, fails[:3]))
        need(E == max(1, fl(n)) and xm == fl(n) + 1 and xs == fl(n), 'E/X values, n=%d' % n)
    for n in range(2, famhi + 1):
        m, nt, exit_ok, _, _ = check2.family(n, 'ok')
        need(m == nt == fl(n) and exit_ok, 'family mass, n=%d' % n)


def fam_closed_ok(lo, hi):
    for n in range(lo, hi + 1):
        m, _, exit_ok, _, row = check2.family(n)
        need(exit_ok and m == fl(n) and row == fam_closed.closed(n), 'family closed form, n=%d' % n)
    bad = [k for k in range(1, 129) if not fam_closed.lemma_P_exact(k)]
    need(not bad, 'Lemma P exact formula fails at %r' % bad[:5])


def lemmas_ok(hi):
    for n in range(1, hi + 1):
        try:
            lemmas.check(n)
        except AssertionError as exc:
            need(False, 'lemma %r' % (exc.args,))


def census_ok(hi):
    for n in range(1, hi + 1):
        peak = max(census.census(n, census.word(n, s))[0] for s in (1, -1))
        need(peak == max(1, fl(n)), 'independent census E(%d)=%d' % (n, peak))


def control_unreversed():
    """Sign - call negates the leaf signs but keeps the phase order (not an inverse)."""
    rejected = []
    for n in range(2, 9):
        _, _, _, fails = check2.full_pass(n, 'unrev')
        if fails or not check2.check_inv(n, 'unrev'):
            rejected.append(n)
    E7 = check2.full_pass(7, 'unrev')[0]
    saved = lemmas.word
    lemmas.word = lambda n, sign=1: [e for e, _ in check2.gen(n, sign, mode='unrev')]
    lemma_fail = []
    try:
        for n in range(2, 9):
            try:
                lemmas.check(n)
            except AssertionError:
                lemma_fail.append(n)
    finally:
        lemmas.word = saved
    need(rejected == list(range(2, 9)) and E7 == 54 and lemma_fail, 'unreversed-inverse control accepted')
    return E7, len(lemma_fail)


def control_ceil_split():
    """B = ceil half instead of floor half: the floor-half export count is what matters."""
    E6, _, _, fails = check2.full_pass(6, 'swap')
    need(E6 == 3 > fl(6) and fails, 'ceil-half split control accepted at n=6')
    misses = sum(check2.family(n, 'swap')[4] != fam_closed.closed(n) for n in range(4, 40))
    need(misses == 32, 'ceil-half family/closed-form control: %d' % misses)
    return E6, misses


def followup_ok():
    import subprocess
    here = os.path.dirname(os.path.abspath(__file__))
    for args, want in ((['fam3.py', '4', '64'], 'failures 0'), (['multi3.py', '1', '16'], 'failing sizes 0')):
        out = subprocess.run([sys.executable, '-B', os.path.join(here, args[0])] + args[1:], cwd=here,
                             capture_output=True, text=True, check=True).stdout
        need(want in out.strip().splitlines()[-1], 'follow-up check %s' % args[0])
    out = subprocess.run([sys.executable, '-B', os.path.join(here, 'multi3.py'), '2', '12', 'swap'], cwd=here,
                         capture_output=True, text=True, check=True).stdout
    need('failing sizes 0' not in out.strip().splitlines()[-1], 'multi-error swap control must fail')


def main():
    need(sys.flags.optimize == 0, 'run without -O: lemmas.py uses assert')
    pinned_inputs()
    source_words(40)
    check2_ok(40, 128)
    fam_closed_ok(2, 200)
    lemmas_ok(32)
    census_ok(24)
    followup_ok()
    e7, lf = control_unreversed()
    e6, misses = control_ceil_split()
    print('controls rejected: unreversed_inverse E(7)=%d, %d lemma failures n<=8; '
          'ceil_half_split E(6)=%d, %d/36 family mismatches' % (e7, lf, e6, misses))
    print('PASS_LEAF_DESTINATION_EXACT_MAXIMUM E(n)=max(1,floor(log2 n)): check2 n=1..40, '
          'family n=2..128, closed form n=2..200, lemmas n<=32, census n<=24, '
          'PR628 word equality n<=40, attainment families (all source-dirty cases) n<=64, multi-error bounds n<=16; finite checks of a written proof, not independently reviewed')


if __name__ == '__main__':
    main()
