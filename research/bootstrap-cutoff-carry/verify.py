#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Audit the selected record's finite bootstrap cutoffs against their own lemma.

The ordinary-bootstrap cutoff rule (PR387 PROOF; five-stage FINITE_BIT_ACCOUNTING)
chooses, at each stage,

    L = ceil(max(1, 36/delta^2, 2*(4+ceil(log2 C))/delta)),

where C dominates that stage's constants *including the previous ordinary
constant*, and fixes the next constant as C_large + C_old*2^(L*(a_(j+1)-a_j)).
The selected assembly records L with ceil(log2 C) = 512 at every stage. This
verifier checks, with exact rationals only:

1. the 14 recorded cutoffs reproduce from the pinned receipt and formula;
2. from stage 2 on, every recorded cutoff fails the rule once the carried factor
   2^(L*(a_(j+1)-a_j)) enters the next stage's C, even with C_old = 1, C_large = 1
   and the recorded (smaller) previous cutoff;
3. the closed-form reason: delta' = s*delta and Delta a = (1-s)*delta/s exactly,
   so the quadratic cutoff can never pay the carry while s < 1/2;
4. an exact corrected cutoff chain that satisfies the rule at every stage, least
   under the receipt's own 512-bit bound on each stage's fresh constants;
5. the numerical kappa calculation does not read the cutoffs (the pinned outer
   engine has no cutoff input, and kappa reproduces from the chain end alone).
   The bootstrap proof obligation itself is not discharged here.

Standard library only. Prepared by Josie Elliston with Claude Code
(Claude Opus 5.5) assistance.
"""
import ast
import hashlib
import io
import json
import sys
import tarfile
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PINS = {
    'research/community-frontier1094-audit/ASSEMBLY.json':
        '1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045',
    'research/complex-allcold/engines/outer.py':
        'c1ebb52163a7219504c728a5c2b098bf1e50bf20148a2879c5a74c3cadc7c03c',
    'research/complex-t16-rare-pattern-exchanges/upstream1087.tar.gz': None,
    'research/five-stage-source527-banks/proof/FINITE_BIT_ACCOUNTING.md': None,
    'research/bootstrap-depth-audit/sources/pr387/PROOF.md': None,
}
ALLOWANCE = 512          # ceil(log2 C) hard-coded by the selected assembler
A0 = Q(384599, 10**10)   # completed ordinary starting saving
ETA = BETA = Q(1, 10**24)
BRANCHES = (('bootstrap', 'complex_lower'),
            ('conservative_bootstrap', 'conservative_complex_lower'))


class AuditError(Exception):
    pass


def require(ok, msg):
    if not ok:
        raise AuditError(msg)


def ceil(x):
    return -(-x.numerator // x.denominator)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def load_sources():
    sources = json.loads((HERE / 'SOURCES.json').read_text())
    pinned = {f['path']: f['sha256'] for f in sources['files']}
    data = {}
    for path, fixed in PINS.items():
        raw = (ROOT / path).read_bytes()
        require(sha256(raw) == pinned[path], f'source pin {path}')
        require(fixed is None or sha256(raw) == fixed, f'fixed pin {path}')
        data[path] = raw
    return data


def bind_text(data):
    """The rule, the 512 allowance and the cutoff-free outer engine, as written."""
    fba = data['research/five-stage-source527-banks/proof/FINITE_BIT_ACCOUNTING.md'].decode()
    pr387 = data['research/bootstrap-depth-audit/sources/pr387/PROOF.md'].decode()
    for text in (fba, pr387):
        require('previous ordinary constants' in text, 'C dominates the previous constant')
        require('36/delta^2' in text, 'quadratic cutoff term')
    require('C_large+C_old*2^(L*(a_(j+1)-a_j))' in fba, 'next-constant rule (FBA)')
    require('C_large+C_old*2^(L*(a_j-a_(j-1)))' in pr387, 'next-constant rule (PR387)')
    with tarfile.open(fileobj=io.BytesIO(
            data['research/complex-t16-rare-pattern-exchanges/upstream1087.tar.gz'])) as tar:
        src = tar.extractfile('code/assemble.py').read().decode()
    require('cut=max(ceil(36/gap**2),ceil(2*(4+512)/gap))' in src, 'selected assembler formula')
    require("chain=[Q(384599,10**10)]" in src and 'for _ in range(7)' in src, 'selected chain start/depth')
    return check_outer(data['research/complex-allcold/engines/outer.py'].decode())


def check_outer(outer):
    fn = [n for n in ast.parse(outer).body if isinstance(n, ast.FunctionDef) and n.name == 'assembly']
    require(len(fn) == 1, 'one outer assembly')
    args = [a.arg for a in fn[0].args.args]
    require(args == ['bit_saving', 'complex_saving', 'bridge', 'kappa', 'eta', 'beta'], 'outer signature')
    require('cutoff' not in outer.lower(), 'outer engine never reads a cutoff')
    return args


def chain(bit, complex_):
    s = min(bit, (1 - BETA) * complex_) - Q(1, 10**27)
    require(0 < s < Q(1, 2), 'common saving below 1/2')
    a, rows = A0, []
    for _ in range(7):
        old, a = a, (1 - s) * s + s * a
        gap = min(s - a, 1 - a - s, 1 - a - s * (1 - old), 1 - s)
        rows.append(dict(old=old, new=a, gap=gap))
    return s, rows


def recorded_cutoff(gap, ell):
    return max(ceil(36 / gap**2), ceil(2 * (4 + ell) / gap))


def lemma_ok(L, gap, ell):
    """Both sufficient inequalities of the cutoff lemma, for log2 C <= ell."""
    return L >= 1 and L * gap**2 >= 36 and L * gap >= 2 * (4 + ell)


def audit_branch(record, name, side):
    s, rows = chain(Q(record['bit_lower']), Q(record[side]))
    rec = record[name]
    require(len(rec) == 7, f'{name}: seven stages')
    cuts = []
    for i, (row, item) in enumerate(zip(rows, rec)):
        require(Q(item['exponent']) == row['new'] and Q(item['gap']) == row['gap'], f'{name}[{i}] chain')
        L = int(item['cutoff_log2'])
        require(L == recorded_cutoff(row['gap'], ALLOWANCE), f'{name}[{i}] recorded cutoff formula')
        require(lemma_ok(L, row['gap'], ALLOWANCE), f'{name}[{i}] fixed-allowance rule')
        # closed form: the binding gap is s - a_(i+1) = s*(s - a_i)
        require(row['gap'] == s - row['new'] == s * (s - row['old']), f'{name}[{i}] binding gap')
        require(row['new'] - row['old'] == (1 - s) * row['gap'] / s, f'{name}[{i}] step identity')
        if i:
            require(row['gap'] == s * rows[i - 1]['gap'], f'{name}[{i}] gap ratio s')
        cuts.append(L)
    # kappa from the chain end only
    q = rows[-1]['new'] * (1 - 2 * ETA)
    ticks = (1 - ETA) * q / (1 + q) * 10**18
    k = Q((ticks.numerator - 1) // ticks.denominator, 10**18)
    key = 'kappa' if name == 'bootstrap' else 'conservative_kappa'
    require(k == Q(record[key]), f'{name}: kappa from chain end')
    return s, rows, cuts


def carry_failures(s, rows, cuts):
    """Stages whose recorded cutoff cannot pay even the minimal carried constant."""
    out = []
    for i in range(1, 7):
        prev, row = rows[i - 1], rows[i]
        carry = ceil(cuts[i - 1] * (prev['new'] - prev['old']))  # log2 of 2^(L*Delta a), C_old >= 1
        ok = lemma_ok(cuts[i], row['gap'], carry)
        # general reason: ceil(36/d^2)*d < 36/d + d < 8 + 72(1-s)/d whenever s < 1/2 and d < 8
        quad = ceil(36 / row['gap']**2)
        if quad >= ceil(2 * (4 + ALLOWANCE) / row['gap']):
            require(quad * row['gap'] < 8 + 72 * (1 - s) / row['gap'], 'closed-form bound')
        need = Q(2 * (4 + carry), 1) / (cuts[i] * row['gap'])
        out.append(dict(stage=i + 1, carry_bits_lower_bound=carry, recorded_pays=ok,
                        shortfall_ratio=need))
    return out


def corrected_chain(rows, carry=True):
    """Least cutoffs meeting the rule with C_old carried; fresh constants < 2^512."""
    ell, out = ALLOWANCE, []
    for row in rows:
        L = recorded_cutoff(row['gap'], ell)
        require(lemma_ok(L, row['gap'], ell), 'corrected rule')
        require(L == 1 or not lemma_ok(L - 1, row['gap'], ell), 'corrected minimal')
        out.append(dict(L=L, ell=ell))
        if carry:
            ell = max(ALLOWANCE, ell + ceil(L * (row['new'] - row['old']))) + 1
    return out


def summarize(record):
    result = {}
    for name, side in BRANCHES:
        s, rows, cuts = audit_branch(record, name, side)
        fails = carry_failures(s, rows, cuts)
        fixed = corrected_chain(rows)
        nocarry = corrected_chain(rows, carry=False)
        require([x['L'] for x in nocarry] == cuts, f'{name}: dropping the carry reproduces the receipt')
        result[name] = dict(
            two_one_minus_s=str(2 * (1 - s)),
            recorded_cutoff_digits=[len(str(L)) for L in cuts],
            stages_failing_carry=[f['stage'] for f in fails if not f['recorded_pays']],
            shortfall_ratio_floor_1e6=[f['shortfall_ratio'].numerator * 10**6 // f['shortfall_ratio'].denominator
                                       for f in fails],
            carry_bits_lower_bound_digits=[len(str(f['carry_bits_lower_bound'])) for f in fails],
            corrected_cutoff_digits=[len(str(x['L'])) for x in fixed],
            corrected_cutoff_sha256=sha256(','.join(str(x['L']) for x in fixed).encode()),
            corrected_log2C_digits=[len(str(x['ell'])) for x in fixed],
        )
    return result


def controls(record, outer_src):
    rejected = []

    def expect(name, fn):
        try:
            fn()
        except AuditError:
            rejected.append(name)
        else:
            raise SystemExit(f'control accepted: {name}')

    def bump(rec):
        r = json.loads(json.dumps(rec))
        r['bootstrap'][3]['cutoff_log2'] = str(int(r['bootstrap'][3]['cutoff_log2']) + 1)
        return r

    expect('tampered_recorded_cutoff', lambda: audit_branch(bump(record), 'bootstrap', 'complex_lower'))

    def wrong_kappa():
        r = json.loads(json.dumps(record))
        r['kappa'] = str(Q(r['kappa']) + Q(1, 10**18))
        audit_branch(r, 'bootstrap', 'complex_lower')
    expect('next_grid_kappa', wrong_kappa)

    def wrong_start():
        global A0
        old, A0 = A0, A0 + Q(1, 10**10)
        try:
            audit_branch(record, 'bootstrap', 'complex_lower')
        finally:
            A0 = old
    expect('shifted_starting_saving', wrong_start)

    def corrected_minus_one():
        _, rows, _ = audit_branch(record, 'bootstrap', 'complex_lower')
        fixed = corrected_chain(rows)
        i = 3
        require(lemma_ok(fixed[i]['L'] - 1, rows[i]['gap'], fixed[i]['ell']), 'corrected L-1 fails')
    expect('corrected_cutoff_minus_one', corrected_minus_one)

    def recorded_with_carry():
        s, rows, cuts = audit_branch(record, 'bootstrap', 'complex_lower')
        fails = carry_failures(s, rows, cuts)
        require(all(f['recorded_pays'] for f in fails), 'recorded cutoffs pay the carry')
    expect('recorded_cutoffs_with_carry', recorded_with_carry)

    def outer_with_cutoff():
        src = outer_src.replace('def assembly(bit_saving,complex_saving,bridge,kappa,',
                                'def assembly(bit_saving,complex_saving,bridge,kappa,cutoffs,')
        require(src != outer_src, 'mutation applied')
        check_outer(src)
    expect('outer_engine_with_cutoff_input', outer_with_cutoff)

    # positive control: the corrected cutoffs, substituted in memory, pay the carry
    s, rows, _ = audit_branch(record, 'bootstrap', 'complex_lower')
    fixed = [x['L'] for x in corrected_chain(rows)]
    fails = carry_failures(s, rows, fixed)
    require(all(f['recorded_pays'] for f in fails), 'corrected cutoffs pay the carry')
    return rejected


def main():
    data = load_sources()
    bind_text(data)
    record = json.loads(data['research/community-frontier1094-audit/ASSEMBLY.json'])
    result = summarize(record)
    rejected = controls(record, data['research/complex-allcold/engines/outer.py'].decode())
    result['controls_rejected'] = rejected
    expected_path = HERE / 'RESULT.json'
    if '--write' in sys.argv:
        expected_path.write_text(json.dumps(result, indent=1) + '\n')
    require(json.loads(expected_path.read_text()) == result, 'RESULT.json matches')
    n = sum(len(result[b]['stages_failing_carry']) for b, _ in BRANCHES)
    print(f'PASS_BOOTSTRAP_CUTOFF_CARRY_AUDIT recorded=14 fail_with_carry={n} '
          f'stage1_valid=2 corrected=14 kappa_independent=1 controls_rejected={len(rejected)}')


if __name__ == '__main__':
    try:
        main()
    except AuditError as e:
        raise SystemExit(f'FAIL: {e}')
