#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check the time/space split of the ordinary-bootstrap cutoff (repair (b)).

PR387 PROOF and five-stage FINITE_BIT_ACCOUNTING choose, per bootstrap stage,

    L = ceil(max(1, 36/delta^2, 2*(4+ceil(log2 C))/delta)),

with C dominating "previous ordinary constants" too. The README proves a
restated lemma: the time bound needs no cutoff, because every lower-order toll
is at most M(delta) * e^(1-a_j) for all e >= 1, so the cutoff only has to make
the borrowed stock fit (k < e/2). The fit constant is a stock/reserve
coefficient. The carried time constant C_old*2^(L*Delta a) only enters the next
stage's time constant. This verifier checks, in exact rationals except where noted:

1. the 14 recorded cutoffs reproduce from the pinned receipt and formula;
2. each satisfies the restated (fit-only) rule with a stock coefficient below
   2^512, and the exact headroom (largest log2 stock coefficient it supports);
3. the absorption constant M(delta) = max(2, 2/(e*ln2*delta)) from certified
   rational lower bounds on e and ln 2, plus the 3*sqrt(t) step of the lemma
   (a floating-point check of M at its maximizer is a sanity check only);
4. an explicit finite time-constant chain under the receipt's 512-bit
   assumption on fresh constants; the carried factor 2^(L*Delta a) alone exceeds
   every stage-2..7 headroom (so the lemma as written fails there, as PR1956
   found), while the cutoffs are unaffected.

Standard library only. The chain and receipt binding follow PR1956
(research/bootstrap-cutoff-carry). Prepared by Josie Elliston with Claude Code
(Claude Opus 5.5) assistance.
"""
import hashlib
import io
import json
import math
import sys
import tarfile
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ASSEMBLY = 'research/community-frontier1094-audit/ASSEMBLY.json'
FBA = 'research/five-stage-source527-banks/proof/FINITE_BIT_ACCOUNTING.md'
ROWS = 'research/five-stage-source527-banks/proof/three-stage-cover-rows.tex'
PR387 = 'research/bootstrap-depth-audit/sources/pr387/PROOF.md'
TARBALL = 'research/complex-t16-rare-pattern-exchanges/upstream1087.tar.gz'
ALLOWANCE = 512          # ceil(log2 C) hard-coded by the selected assembler
A0 = Q(384599, 10**10)   # completed ordinary starting saving
ETA = BETA = Q(1, 10**24)
BRANCHES = (('bootstrap', 'complex_lower'),
            ('conservative_bootstrap', 'conservative_complex_lower'))
LN2_LO = Q(693, 1000)    # claimed rational lower bounds, certified below
E_LO = Q(2718, 1000)


class AuditError(Exception):
    pass


def require(ok, msg):
    if not ok:
        raise AuditError(msg)


def ceil(x):
    return -(-x.numerator // x.denominator)


def floor(x):
    return x.numerator // x.denominator


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def load_sources():
    sources = json.loads((HERE / 'SOURCES.json').read_text())
    data = {}
    for f in sources['files']:
        if f['usage'] != 'input':
            continue
        raw = (ROOT / f['path']).read_bytes()
        require(sha256(raw) == f['sha256'], f"source pin {f['path']}")
        data[f['path']] = raw
    require(set(data) == {ASSEMBLY, FBA, ROWS, PR387, TARBALL}, 'input set')
    return data


def bind_text(data):
    """The lemma as written, the fit condition it serves, and the assembler formula."""
    fba, pr387 = data[FBA].decode(), data[PR387].decode()
    for text in (fba, pr387):
        require('previous ordinary constants' in text, 'C dominates the previous constant')
        require('36/delta^2' in text, 'quadratic cutoff term')
    require('borrowed high part fits' in fba, 'the cutoff also serves the fit')
    require('C_large+C_old*2^(L*(a_(j+1)-a_j))' in fba, 'next-constant rule (FBA)')
    require('1-c (for row fitting)' in fba, 'stock gap among the minimum')
    require('- stock: 1-s.' in pr387, 'stock gap among the minimum (PR387)')
    rows = data[ROWS].decode()
    for needle in (r'\log_qS(e,w)=O(w\log e)', 'For sufficiently large $e$, $k<e/2$',
                   'logarithmic reserve', 'Small widths use the retained supplier directly'):
        require(needle in rows, f'fit statement: {needle}')
    with tarfile.open(fileobj=io.BytesIO(data[TARBALL])) as tar:
        src = tar.extractfile('code/assemble.py').read().decode()
    require('cut=max(ceil(36/gap**2),ceil(2*(4+512)/gap))' in src, 'selected assembler formula')
    require('chain=[Q(384599,10**10)]' in src and 'for _ in range(7)' in src, 'chain start/depth')


def certify_constants(ln2_lo=LN2_LO, e_lo=E_LO):
    """Rational enclosures: ln2 = sum 1/(k 2^k), e = sum 1/k!, with tail bounds."""
    lo, n = Q(0), 40
    for k in range(1, n + 1):
        lo += Q(1, k * 2**k)
    hi = lo + Q(1, (n + 1) * 2**n)           # tail <= sum_{k>n} 2^-k/(n+1)
    require(lo <= hi and ln2_lo <= lo, 'ln2 lower bound')
    elo, f = Q(0), 1
    for k in range(0, 25):
        f = f * k if k else 1
        elo += Q(1, f)
    require(e_lo <= elo, 'e lower bound')
    # log2(1+t) <= 3 sqrt(t) for t >= 0: 2^(3u) >= 1 + (3u ln2)^2/2 >= 1 + u^2.
    require(9 * ln2_lo**2 / 2 >= 1, '3*sqrt(t) step')
    return dict(ln2=(lo, hi))


def clog2(x):
    """Least integer n with 2^n >= x, for a positive rational x."""
    n = x.numerator.bit_length() - x.denominator.bit_length()
    while Q(2)**n < x:
        n += 1
    while Q(2)**(n - 1) >= x:
        n -= 1
    return n


def m_bar(delta):
    """sup_{t>=0} (1+t) 2^(-delta t) <= max(2, 2/(e ln2 delta)); proof in README."""
    return max(Q(2), 2 / (E_LO * LN2_LO * delta))


def float_sanity(delta, bound):
    """Not a certificate: the proved bound dominates the true sup at its maximizer."""
    d, ln2 = float(delta), math.log(2)
    ts = [0.0, 1.0, max(0.0, 1 / (d * ln2) - 1)] + [10.0**k for k in range(0, 16)]
    for t in ts:
        require(math.log1p(t) - d * t * ln2 <= math.log(float(bound)) + 1e-12, f'sup bound at t={t}')


def chain(bit, complex_):
    s = min(bit, (1 - BETA) * complex_) - Q(1, 10**27)
    require(0 < s < Q(1, 2), 'common saving below 1/2')
    a, rows = A0, []
    for _ in range(7):
        old, a = a, (1 - s) * s + s * a
        gaps = (s - a, 1 - a - s, 1 - a - s * (1 - old), 1 - s)
        require(all(g > 0 for g in gaps), 'positive gaps')
        rows.append(dict(old=old, new=a, gap=min(gaps), stock=1 - s))
    return s, rows


def recorded_cutoff(gap, ell):
    return max(ceil(36 / gap**2), ceil(2 * (4 + ell) / gap))


def fit_ok(L, gap, ell):
    """Restated rule: e >= 2^L makes C(1+log2 e)e^-gap <= 1/16 for log2 C <= ell."""
    return L >= 2 and L * gap**2 >= 36 and L * gap >= 2 * (4 + ell)


def audit_branch(record, name, side):
    s, rows = chain(Q(record['bit_lower']), Q(record[side]))
    rec = record[name]
    require(len(rec) == 7, f'{name}: seven stages')
    out = []
    for i, (row, item) in enumerate(zip(rows, rec)):
        require(Q(item['exponent']) == row['new'] and Q(item['gap']) == row['gap'], f'{name}[{i}] chain')
        L = int(item['cutoff_log2'])
        require(L == recorded_cutoff(row['gap'], ALLOWANCE), f'{name}[{i}] recorded formula')
        require(row['gap'] <= row['stock'], f'{name}[{i}] stock gap covered by delta')
        require(fit_ok(L, row['gap'], ALLOWANCE), f'{name}[{i}] fit-only rule')
        headroom = floor(L * row['gap'] / 2) - 4
        require(fit_ok(L, row['gap'], headroom) and not fit_ok(L, row['gap'], headroom + 1),
                f'{name}[{i}] exact headroom')
        out.append(dict(L=L, gap=row['gap'], dA=row['new'] - row['old'], headroom=headroom))
    return out


def time_chain(stages, fresh=ALLOWANCE):
    """Upper bounds on log2 C_j when fresh time constants and multiplicities are < 2^fresh.

    C_j <= max(K_j (4 + M), C_(j-1) 2^(L Delta a)), K_j <= 2^fresh + 2^fresh C_(j-1).
    """
    ell, out = fresh, []
    for st in stages:
        M = m_bar(st['gap'])
        k = max(fresh, fresh + ell) + 1
        large = k + clog2(4 + M)
        carry = ell + ceil(st['L'] * st['dA'])
        out.append(dict(prev=ell, large=large, carry=carry))
        ell = max(large, carry) + 1
    out.append(dict(prev=ell))
    return out


def summarize(record):
    result = {}
    for name, side in BRANCHES:
        stages = audit_branch(record, name, side)
        tc = time_chain(stages)
        for st in stages:
            float_sanity(st['gap'], m_bar(st['gap']))
        # The lemma as written puts the previous time constant into C. Stage 1: C_0 < 2^512
        # (receipt). Later stages: log2 C_old >= L_(i-1)*Delta a_(i-1) (C_old >= 1, carry alone).
        written = [fit_ok(stages[0]['L'], stages[0]['gap'], ALLOWANCE)]
        written += [not (prev['L'] * prev['dA'] > st['headroom']) for prev, st in zip(stages, stages[1:])]
        require(written[0] and not any(written[1:]), f'{name}: written rule fails exactly at stages 2-7')
        result[name] = dict(
            cutoff_digits=[len(str(st['L'])) for st in stages],
            stock_headroom_log2=[st['headroom'] for st in stages],
            m_bar_log2_ceil=[clog2(m_bar(st['gap'])) for st in stages],
            time_log2C_digits=[len(str(x['prev'])) for x in tc],
            time_log2C_final_sha256=sha256(str(tc[-1]['prev']).encode()),
            written_rule_holds=written,
        )
    return result


def controls(record):
    rejected = []

    def expect(name, fn):
        try:
            fn()
        except AuditError:
            rejected.append(name)
        else:
            raise SystemExit(f'control accepted: {name}')

    def tampered():
        r = json.loads(json.dumps(record))
        r['bootstrap'][4]['cutoff_log2'] = str(int(r['bootstrap'][4]['cutoff_log2']) - 1)
        audit_branch(r, 'bootstrap', 'complex_lower')
    expect('recorded_cutoff_minus_one', tampered)

    def over_headroom():
        st = audit_branch(record, 'conservative_bootstrap', 'conservative_complex_lower')[2]
        require(fit_ok(st['L'], st['gap'], st['headroom'] + 1), 'stock coefficient above headroom')
    expect('stock_coefficient_above_headroom', over_headroom)

    def quarter_bound():
        st = audit_branch(record, 'bootstrap', 'complex_lower')[6]
        float_sanity(st['gap'], m_bar(st['gap']) / 4)
    expect('absorption_constant_quartered', quarter_bound)

    expect('ln2_lower_bound_too_high', lambda: certify_constants(ln2_lo=Q(6932, 10000)))
    expect('e_lower_bound_too_high', lambda: certify_constants(e_lo=Q(2719, 1000)))

    def written_rule():
        stages = audit_branch(record, 'bootstrap', 'complex_lower')
        carry = floor(stages[0]['L'] * stages[0]['dA'])
        require(fit_ok(stages[1]['L'], stages[1]['gap'], carry), 'carried time constant in C')
    expect('carried_time_constant_in_fit', written_rule)

    def tampered_gap():
        r = json.loads(json.dumps(record))
        r['bootstrap'][0]['gap'] = str(Q(r['bootstrap'][0]['gap']) * 2)
        audit_branch(r, 'bootstrap', 'complex_lower')
    expect('tampered_gap', tampered_gap)
    return rejected


def main():
    data = load_sources()
    bind_text(data)
    certify_constants()
    record = json.loads(data[ASSEMBLY])
    result = summarize(record)
    result['controls_rejected'] = controls(record)
    expected_path = HERE / 'RESULT.json'
    if '--write' in sys.argv:
        expected_path.write_text(json.dumps(result, indent=1) + '\n')
    require(json.loads(expected_path.read_text()) == result, 'RESULT.json matches')
    fails = sum(not x for b, _ in BRANCHES for x in result[b]['written_rule_holds'])
    print(f'PASS_BOOTSTRAP_TIME_SPACE_SPLIT recorded=14 fit_only_valid=14 written_rule_fails={fails} '
          f'time_constant_finite=2 controls_rejected={len(result["controls_rejected"])}')


if __name__ == '__main__':
    try:
        main()
    except AuditError as e:
        raise SystemExit(f'FAIL: {e}')
