#!/usr/bin/env python3
"""Acceptance and rejection controls of the odd-scalar verifier (standard library).
python3 -I -B controls.py        (writes mutated words only into a temporary directory that is removed at exit)
Runs verify_host3_odd.py on data/word.json.gz at the declared certificate S = 1125 and on mutated copies, and verify_host3_dyadic.py (the predecessor alphabet) for comparison.
Every line is 'expected' against 'got'; any mismatch ends the run with FAIL.  Ends PASS_ODD_CONTROLS."""
import gzip, json, os, subprocess, sys, tempfile, copy
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
data = lambda n: os.path.join(HERE, 'data', n)
W = json.load(gzip.open(data('word.json.gz'), 'rt')); P = W['program']; n = len(W['initial'])
tmp = tempfile.TemporaryDirectory(); res = []
def run(word, S=None, ver='verify_host3_odd.py'):
    r = subprocess.run([sys.executable, '-I', '-B', os.path.join(HERE, ver), word] + ([str(S)] if S is not None else []), capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip().splitlines()
    return ('PASS' if 'PASS_HOST3' in r.stdout else 'REJECT'), (out[-1][:100] if out else '')
def save(w, name):
    p = os.path.join(tmp.name, name + '.json.gz')
    with gzip.open(p, 'wt') as f: json.dump(w, f)
    return p
def go(name, word, S, expect, ver='verify_host3_odd.py'):
    got, last = run(word, S, ver); res.append((name, got == expect))
    print('%-4s %-70s S=%-5s expected %-6s got %-6s %s' % ('ok' if got == expect else 'FAIL', name, S, expect, got, last), flush=True)
adds = [i for i, e in enumerate(P) if e[0] == 'ADD']; scs = [i for i, e in enumerate(P) if e[0] == 'SCALE']
def mutate(i, k, v):
    w = copy.deepcopy(W); w['program'][i][k] = v; return w
W0 = data('word.json.gz'); BASE = data('prior_word_6931.json.gz')
go('word at the declared certificate', W0, 1125, 'PASS')
for s in (375, 225, 75, 45, 15, 25, 9, 1): go('word with a smaller certificate', W0, s, 'REJECT')
go('word with a larger certificate (3 * 1125, sufficient not minimal)', W0, 3375, 'PASS')
go('word with S = 7 * 1125 (S must be 3^e 5^g)', W0, 7 * 1125, 'REJECT')
go('word, default certificate S = 1', W0, None, 'REJECT')
go('ADD coefficient 1/7 (not in A)', save(mutate(adds[10], 3, '1/7'), 'c17'), 1125, 'REJECT')
go('SCALE by 1/7 (not a unit of A)', save(mutate(scs[0], 2, '1/7'), 's17'), 1125, 'REJECT')
go('SCALE by 7 (not a unit of A)', save(mutate(scs[0], 2, '7'), 's7'), 1125, 'REJECT')
go('SCALE by 3/2 (a unit of A, rows leave the grid)', save(mutate(scs[0], 2, '3/2'), 's32'), 1125, 'REJECT')
go('ADD coefficient 65536 (|q|+1 >= 2^16)', save(mutate(adds[10], 3, '65536'), 'q65536'), 1125, 'REJECT')
go('ADD coefficient 65535 (|q|+1 = 2^16)', save(mutate(adds[10], 3, '65535'), 'q65535'), 1125, 'REJECT')
X2s, Y2s = set(W['hosted']['X2']), set(W['hosted']['Y2']); mains = set(W['live']) | {r + 112 for r in W['live']} | X2s | Y2s
h = next(r for r in range(n) if r not in mains)
w = copy.deepcopy(W); w['program'].append(['SCALE', h, '1/3', W['final'][h]]); p = save(w, 'npr')
go('non-dyadic public row (a final SCALE 1/3 on a helper)', p, 1125, 'REJECT')
go('the same word with S = 1', p, 1, 'REJECT')
def pair(q):
    w = copy.deepcopy(W); i = adds[10]; a = list(w['program'][i]); b = list(a); a[3] = q; b[3] = str(-__import__('fractions').Fraction(q)); w['program'][i:i] = [a, b]; return w
go('cancelling pair of ADDs 1/7 and -1/7', save(pair('1/7'), 'p17'), 1125, 'REJECT')
go('cancelling pair of ADDs 65536 and -65536', save(pair('65536'), 'p65536'), 1125, 'REJECT')
go('cancelling pair of ADDs 3/5 and -3/5 (legal, in A)', save(pair('3/5'), 'p35'), 1125, 'PASS')
go('cancelling pair of ADDs 65534 and -65534 (legal, bound kept)', save(pair('65534'), 'p65534'), 1125, 'PASS')
go('dyadic word (the #6931 word), S = 1 control', BASE, 1, 'PASS')
go('dyadic word (the #6931 word), default certificate', BASE, None, 'PASS')
go('dyadic word (the #6931 word) under the dyadic verifier', BASE, None, 'PASS', 'verify_host3_dyadic.py')
go('this word under the dyadic verifier (the predecessor rule rejects it)', W0, None, 'REJECT', 'verify_host3_dyadic.py')
tmp.cleanup()
bad = [nm for nm, ok in res if not ok]
if bad: raise SystemExit('FAIL ' + str(bad))
print('PASS_ODD_CONTROLS %d controls' % len(res))
