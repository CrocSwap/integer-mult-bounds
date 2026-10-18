#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Pinned κ ledger of the T74 handoff line: transcribed numeric statements and release gates re-checked exactly.

Standard library only. For each PR in PINS.json the script reads the claimed κ from the PR's own pinned claim file at
the exact head (git blob id and sha256; PR2265, the external baseline, uses its outer/LEDGER.json row). It then:
  1. lists the line in κ order, with the exact difference to the previous entry;
  2. re-checks every statement in STATEMENTS.json (transcribed verbatim from PR bodies and pinned READMEs):
       difference   "exceeds PR#### by X"      X versus κ(source) - κ(target)
       percent      "X% of κ"                  X versus 100 (κ(source) - κ(target)) / κ(base)
       kappa_quote  "PR#### ... kappa X"       X versus κ(target)
     with exact rational arithmetic. A number is CONSISTENT when the true value, rounded half-even or half-up to the
     printed digits of X, equals X ("about"/"approximately" get no slack). A kappa quote is CONSISTENT when X is a
     prefix or a correct rounding of κ(target); it is also reported as AMBIGUOUS when X fits other pinned κ too.
     Otherwise the statement is FLAGGED, and the script reports which pinned pair (or κ) the printed X does match;
  3. checks every README quote at the pinned head (blob pinned): the whole whitespace-normalised quote, or, where the
     transcriber elided text with an ellipsis, its fragments in order within a short window. Each quote must contain
     its stated number, and must name its target PR or carry a 'context' naming it that precedes the quote closely;
  4. parses every predecessor gate `if Fraction(kappa_decimal) <= Fraction(...): raise SystemExit(...)` in each
     pinned verify_release.py (the parse must account for every such line). Each gate is attributed to the PR named
     in its message, else in its comment, else to a pinned PR whose κ equals its literal exactly. Its literal is
     compared with that PR's pinned κ (EXACT, ABOVE = conservative, BELOW), the source κ must exceed both, and a
     comment naming a different PR than the message is reported as a label slip;
  5. runs negative controls through the same functions (perturbed numbers, altered quotes, wrong pins, synthetic
     gates) and positive controls (each suggested correction must be CONSISTENT).
The flagged set with its explanations, the ambiguous set, the BELOW gates and the label slips are asserted.

--live (network, GitHub CLI) compares each pinned head with refs/pull/N/head and each transcribed body quote and body
hash (BODIES.json) with the current PR body. Drift ends with DRIFT_T74_CLAIM_LEDGER and exit status 3. It checks the
pinned PRs only and cannot discover new PRs or comments.

Scope: consolidation of stated numbers. No κ is re-derived, and no construction is checked here.
Prepared with substantial AI assistance (Claude Code, Anthropic); Apache-2.0.
Usage: python3 -I -B ledger.py [--repo PATH] [--fetch] [--remote URL] [--live] [--out]
"""

import argparse
import hashlib
import json
import math
import os
import re
import subprocess
import sys
from decimal import Decimal, getcontext
from fractions import Fraction

if not __debug__:
    sys.stdout.write('FAIL_T74_CLAIM_LEDGER refusing to run under python -O\n')
    sys.exit(2)
getcontext().prec = 60
HERE = os.path.dirname(os.path.abspath(__file__))
REPO_DEFAULT = os.path.dirname(os.path.dirname(HERE))
REMOTE_DEFAULT = 'https://github.com/CrocSwap/integer-mult-bounds'
GH_REPO = 'CrocSwap/integer-mult-bounds'
QUOTE_WINDOW = 400   # an elided quote's fragments must lie within this many characters of each other
CONTEXT_WINDOW = 800  # a quote must start within this many characters after its context
# id -> (reason, what the printed value matches, suggested correction (stated, target))
EXPECTED_FLAGGED = {
    '2302b2': ('difference names PR2269 but is PR2302-PR2288', ['PR2302-PR2288'], ('1.48628E-7', 2269)),
    '2374b3': ('difference names PR2312 but is PR2374-PR2349', ['PR2374-PR2349'], ('3.03884E-7', 2312)),
    '2435b2': ('difference names PR2312 but is PR2435-PR2374', ['PR2435-PR2374'], ('1.62028E-6', 2312)),
    '2374r5': ('README repeats 2374b3', ['PR2374-PR2349'], ('3.03884E-7', 2312)),
    '2435r4': ('README repeats 2435b2', ['PR2435-PR2374'], ('1.62028E-6', 2312)),
    '2435r1': ("kappa quoted as PR2374's is PR2435's own", ['PR2435'], ('0.0016971949509017704', 2374)),
    '2447r1': ("kappa quoted as PR2435's is PR2447's own", ['PR2447'], ('0.0016985113436976293', 2435)),
    '2474r1': ("kappa quoted as PR2462's is PR2474's own", ['PR2474'], ('0.0017035523129795943854', 2462)),
    '2288r6': ('copied "about 1.28e-5" is PR2269/PR2281-PR2265, not PR2288-PR2265', ['PR2269-PR2265', 'PR2281-PR2265'],
               ('1.29e-5', 2265)),
    '2302r6': ('copied "about 1.28e-5" is PR2269/PR2281-PR2265, not PR2302-PR2265', ['PR2269-PR2265', 'PR2281-PR2265'],
               ('1.30e-5', 2265)),
    '2312r8': ('copied "about 1.28e-5" is PR2269/PR2281-PR2265, not PR2312-PR2265', ['PR2269-PR2265', 'PR2281-PR2265'],
               ('1.35e-5', 2265)),
}
# kappa quotes of PR2269 that also fit PR2281 (the two agree to 90 digits)
EXPECTED_AMBIGUOUS = {'2281r1', '2288r1'}
EXPECTED_GATES_BELOW = {2265}            # its published 43-digit kappa, a truncation of the pinned value
EXPECTED_GATE_LABEL_SLIPS = {(n, 2363, 2322) for n in (2374, 2435, 2447, 2462, 2474)}  # (source, comment, message)
GATE_LINE = 'if Fraction(kappa_decimal) <= Fraction('
GATE = re.compile(r"((?:[ \t]*#[^\n]*\n)*)[ \t]*if Fraction\(kappa_decimal\) <= Fraction\("
                  r"(?:'([0-9.]+)'|(\d+), 10 \*\* (\d+))\):\n[ \t]*raise SystemExit\('([^']*)'\)")


class Fail(Exception):
    pass


def need(cond, what):
    if not cond:
        raise Fail(what)


def git(repo, *args):
    return subprocess.run(['git', '-C', repo] + list(args), capture_output=True)


def blob_id(data):
    return hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest()


def show_pinned(repo, head, path, blob, sha=None):
    r = git(repo, 'show', head + ':' + path)
    need(r.returncode == 0, 'absent %s:%s (rerun with --fetch)' % (head[:8], path))
    need(blob_id(r.stdout) == blob and (sha is None or hashlib.sha256(r.stdout).hexdigest() == sha),
         'pin %s:%s' % (head[:8], path))
    return r.stdout


def lookup(data, key):
    for k in (key if isinstance(key, list) else [key]):
        data = data[k]
    return data


def norm(s):
    return ' '.join(s.split())


def sci(x):
    return '%.10E' % (Decimal(x.numerator) / Decimal(x.denominator)) if x else '0'


def agrees(stated_text, actual):
    """True when actual (a Fraction), rounded half-even or half-up to the printed digits of stated_text, equals it."""
    d = Decimal(stated_text)
    unit = Fraction(10) ** d.as_tuple().exponent
    q, want = actual / unit, Fraction(d) / unit
    sign = -1 if q < 0 else 1
    return want in (round(q), sign * math.floor(abs(q) + Fraction(1, 2)))


def kappa_fits(stated_text, raw, value):
    return raw.startswith(stated_text) or agrees(stated_text, value)


def evaluate(s, K, raw, claims, stated=None, target=None):
    """Status, true value and pinned matches of statement s (optionally with another stated number or target)."""
    stated = (s['stated'] if stated is None else stated).lstrip('+')
    tgt = s['target'] if target is None else target
    if s['kind'] == 'kappa_quote':
        matches = sorted(m for m in K if kappa_fits(stated, raw[m], K[m]))
        status = 'FLAGGED' if tgt not in matches else 'AMBIGUOUS' if len(matches) > 1 else 'CONSISTENT'
        return status, K[tgt], ['PR%d' % m for m in matches]
    tk = Fraction(lookup(claims[tgt], s['target_key'])) if 'target_key' in s and tgt == s['target'] else K[tgt]
    actual = K[s['source']] - tk
    if s['kind'] == 'percent':
        actual = 100 * actual / K[s['percent_base']]
        return ('CONSISTENT' if agrees(stated, actual) else 'FLAGGED'), actual, []
    ok = agrees(stated, actual)
    matches = [] if ok else ['PR%d-PR%d' % (a, b) for a in sorted(K) for b in sorted(K)
                             if a != b and agrees(stated, K[a] - K[b])]
    return ('CONSISTENT' if ok else 'FLAGGED'), actual, matches


def find_quote(quote, text):
    """Start offset of the normalised quote in text (whole, else elided fragments in order within a window)."""
    q = norm(quote)
    if q in text:
        return text.index(q)
    frags = [f.strip() for f in re.split(r'\.\.\.|…', q) if f.strip()]
    for m in re.finditer(re.escape(frags[0]), text):
        pos, ok = m.end(), True
        for f in frags[1:]:
            j = text.find(f, pos)
            if j < 0 or j - pos > QUOTE_WINDOW:
                ok = False
                break
            pos = j + len(f)
        if ok:
            return m.start()
    return -1


def check_quote(s, text):
    need(s['stated'] in s['quote'] or s['stated'].lstrip('+') in s['quote'], '%s: stated number not in quote' % s['id'])
    at = find_quote(s['quote'], text)
    need(at >= 0, '%s: quote not found in its source' % s['id'])
    refs = ('PR%d' % s['target'], '#%d' % s['target'])
    if not any(r in s['quote'] for r in refs):
        need('context' in s and any(r in s['context'] for r in refs), '%s: quote does not name its target' % s['id'])
        c = norm(s['context'])
        need(any(0 <= at - m.start() <= CONTEXT_WINDOW for m in re.finditer(re.escape(c), text)),
             '%s: context not found just before the quote' % s['id'])


def parse_gates(text, K, raw):
    """Gates of one release script attributed to pinned PRs, and the number of gates naming no pinned PR."""
    text = text.replace('\r\n', '\n')  # some of these scripts are stored with CRLF line ends
    found = GATE.findall(text)
    need(len(found) == text.count(GATE_LINE), 'gate parse incomplete: %d of %d' % (len(found), text.count(GATE_LINE)))
    gates, other = [], 0
    for comment, lit, num, exp, msg in found:
        value = Fraction(lit) if lit else Fraction(int(num), 10 ** int(exp))
        in_msg = [int(x) for x in re.findall(r'PR(\d{4})', msg)]
        in_comment = [int(x) for x in re.findall(r'PR(\d{4})', (comment.strip().splitlines() or [''])[-1])]
        named = [n for n in in_msg + in_comment if n in K][:1] or [n for n in K if K[n] == value][:1]
        if not named or (in_msg and in_msg[0] not in K):
            other += 1
            continue
        n = named[0]
        gates.append(dict(named=n, by='message' if in_msg else 'comment' if in_comment else 'literal',
                          comment_pr=in_comment[0] if in_comment else None, literal=value,
                          literal_text=lit or '%s/10^%s' % (num, exp),
                          relation='EXACT' if value == K[n] else 'ABOVE' if value > K[n] else 'BELOW'))
    return gates, other


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default=REPO_DEFAULT)
    ap.add_argument('--fetch', action='store_true')
    ap.add_argument('--remote', default=REMOTE_DEFAULT)
    ap.add_argument('--live', action='store_true')
    ap.add_argument('--out', action='store_true')
    args = ap.parse_args()
    pins = json.load(open(os.path.join(HERE, 'PINS.json')))
    statements = json.load(open(os.path.join(HERE, 'STATEMENTS.json')))
    bodies = json.load(open(os.path.join(HERE, 'BODIES.json')))
    K, raw, claims, readmes, scripts = {}, {}, {}, {}, {}
    for n, p in pins.items():
        if git(args.repo, 'cat-file', '-e', p['head'] + '^{commit}').returncode and args.fetch:
            r = git(args.repo, 'fetch', '-q', args.remote, 'refs/pull/%s/head' % n)
            if r.returncode or git(args.repo, 'cat-file', '-e', p['head'] + '^{commit}').returncode:
                git(args.repo, 'fetch', '-q', args.remote, p['head'])
        n = int(n)
        claims[n] = json.loads(show_pinned(args.repo, p['head'], p['path'], p['git_blob'], p['sha256']))
        raw[n] = lookup(claims[n], p['key'])
        need(isinstance(raw[n], str) and raw[n].startswith('0.00'), 'PR%d kappa field' % n)
        K[n] = Fraction(raw[n])
        readmes[n] = norm(show_pinned(args.repo, p['head'], p['readme'], p['readme_git_blob']).decode())
        if 'release_script' in p:
            scripts[n] = show_pinned(args.repo, p['head'], p['release_script'], p['release_script_git_blob']).decode()
    order = sorted(K, key=lambda n: K[n])
    print('T74 handoff line, pinned claim files, in kappa order:')
    for i, n in enumerate(order):
        role = pins[str(n)].get('role', '')
        print('  PR%d  kappa %s...  %s%s' % (n, raw[n][:24], '' if i == 0 else '(+%s over PR%d)' % (
            sci(K[n] - K[order[i - 1]]), order[i - 1]), '  [%s]' % role if role else ''))

    # 2-3. statements and their quotes
    rows, flagged, ambiguous = [], {}, set()
    for s in statements:
        need(s['source'] in K and s['target'] in K, '%s: PR%d -> PR%d not pinned' % (s['id'], s['source'], s['target']))
        if s['where'] == 'README':
            check_quote(s, readmes[s['source']])
        status, actual, matches = evaluate(s, K, raw, claims)
        if status == 'FLAGGED':
            flagged[s['id']] = matches
        if status == 'AMBIGUOUS':
            ambiguous.add(s['id'])
        rows.append(dict(id=s['id'], source=s['source'], where=s['where'], kind=s['kind'], target=s['target'],
                         stated=s['stated'], actual=raw[s['target']][:30] if s['kind'] == 'kappa_quote' else sci(actual),
                         status=status, stated_value_matches=matches, quote=s['quote']))
    print('Statements (%d), flagged:' % len(rows))
    for r in rows:
        if r['status'] == 'FLAGGED':
            print('  %-7s PR%d %-6s %-11s target PR%d: stated %s, true %s -> printed value matches %s' % (
                r['id'], r['source'], r['where'], r['kind'], r['target'], r['stated'], r['actual'][:24],
                ', '.join(r['stated_value_matches']) or 'no pinned value'))
    need(flagged == {k: v[1] for k, v in EXPECTED_FLAGGED.items()}, 'flagged set changed: %s' % sorted(flagged.items()))
    need(ambiguous == EXPECTED_AMBIGUOUS, 'ambiguous set changed: %s' % sorted(ambiguous))

    # 4. release gates
    gates, other = [], 0
    for n, text in sorted(scripts.items()):
        g, o = parse_gates(text, K, raw)
        other += o
        for x in g:
            need(K[n] > max(x['literal'], K[x['named']]), 'PR%d gate on PR%d does not pass' % (n, x['named']))
            x['source'] = n
        gates += g
    below = {g['named'] for g in gates if g['relation'] == 'BELOW'}
    slips = {(g['source'], g['comment_pr'], g['named']) for g in gates
             if g['by'] == 'message' and g['comment_pr'] is not None and g['comment_pr'] != g['named']}
    need(below == EXPECTED_GATES_BELOW, 'BELOW gates changed: %s' % sorted(below))
    need(slips == EXPECTED_GATE_LABEL_SLIPS, 'gate label slips changed: %s' % sorted(slips))
    rel = {r: sum(1 for g in gates if g['relation'] == r) for r in ('EXACT', 'ABOVE', 'BELOW')}
    distinct = len({(g['named'], g['literal']) for g in gates})
    gap = min(g['literal'] - K[g['named']] for g in gates)
    print('release gates attributed to pinned PRs: %d (%d distinct named literals) in %d of %d scripts: EXACT %d, '
          'ABOVE %d, BELOW %d (PR2265, gap %s); %d by literal only; all pass; label slips %d; %d gates name other PRs'
          % (len(gates), distinct, len({g['source'] for g in gates}), len(scripts), rel['EXACT'], rel['ABOVE'],
             rel['BELOW'], sci(gap), sum(1 for g in gates if g['by'] == 'literal'), len(slips), other))

    # 5. controls through the same functions
    neg = rej = 0
    for s, r in zip(statements, rows):
        txt = s['stated'].lstrip('+')
        if r['status'] == 'CONSISTENT':
            if s['kind'] == 'kappa_quote':
                bads = [txt[:-1] + str((int(txt[-1]) + 5) % 10)]
            else:
                d = Decimal(txt)
                u = Decimal(1).scaleb(d.as_tuple().exponent)
                bads = [str(d + u), str(d - u)]
            for bad in bads:
                neg, rej = neg + 1, rej + (evaluate(s, K, raw, claims, stated=bad)[0] == 'FLAGGED')
            if s['kind'] == 'difference':  # the same number attributed to the wrong target
                wrong = [m for m in K if m not in (s['source'], s['target'])][0]
                neg, rej = neg + 1, rej + (evaluate(s, K, raw, claims, target=wrong)[0] == 'FLAGGED')
        if s['where'] == 'README':
            q = s['quote']
            i = max(j for j, ch in enumerate(q) if ch.isdigit())
            alt = dict(s, quote=q[:i] + str((int(q[i]) + 1) % 10) + q[i + 1:])
            alt['stated'] = alt['quote'][alt['quote'].find(txt[:-1]):][:len(txt)] if txt in q else s['stated']
            try:
                check_quote(alt, readmes[s['source']])
                hit = True
            except Fail:
                hit = False
            neg, rej = neg + 1, rej + (not hit)
    for n, p in pins.items():
        for path in [p['path'], p['readme']] + ([p['release_script']] if 'release_script' in p else []):
            try:
                show_pinned(args.repo, p['head'], path, '0' * 40)
                hit = True
            except Fail:
                hit = False
            neg, rej = neg + 1, rej + (not hit)
    top = order[-1]
    synthetic = [
        ('# PR%d\n    if Fraction(kappa_decimal) <= Fraction(%d, 10 ** 30):\n        raise SystemExit(\'x PR%d\')\n'
         % (top, int(K[top] * 10 ** 30) + 1, top), 'gate above the source kappa must fail'),
        ('    if Fraction(kappa_decimal) <= Fraction(\'0.001\') + 0:\n        raise SystemExit(\'x PR2269\')\n',
         'unparsed gate shape must fail'),
    ]
    for text, _ in synthetic:
        try:
            g, _o = parse_gates(text, K, raw)
            for x in g:
                need(K[top] > max(x['literal'], K[x['named']]), 'gate')
            hit = True
        except Fail:
            hit = False
        neg, rej = neg + 1, rej + (not hit)
    g, _o = parse_gates('# PR2363 exact\n    if Fraction(kappa_decimal) <= Fraction(1697147064845350, 10 ** 18):\n'
                        '        raise SystemExit(\'does not exceed PR2322\')\n', K, raw)
    neg, rej = neg + 1, rej + (len(g) == 1 and g[0]['comment_pr'] == 2363 and g[0]['named'] == 2322)
    need(neg == rej, 'negative controls: %d of %d rejected' % (rej, neg))
    pos = 0
    by_id = {s['id']: s for s in statements}
    for k, (_reason, _m, (stated, target)) in EXPECTED_FLAGGED.items():
        need(evaluate(by_id[k], K, raw, claims, stated=stated, target=target)[0] == 'CONSISTENT',
             'suggested correction for %s' % k)
        pos += 1
    print('controls: %d/%d negative (perturbed numbers, wrong targets, altered quotes, wrong pins, synthetic gates) '
          'rejected; %d/%d suggested corrections consistent' % (rej, neg, pos, len(EXPECTED_FLAGGED)))

    live = None
    if args.live:
        live = dict(head_drift=[], body_drift=[], missing_body_quotes=[])
        for n, p in pins.items():
            r = subprocess.run(['git', 'ls-remote', args.remote, 'refs/pull/%s/head' % n], capture_output=True, text=True)
            need(r.returncode == 0 and r.stdout.strip(), 'ls-remote PR%s' % n)
            if r.stdout.split()[0] != p['head']:
                live['head_drift'].append('PR%s %s' % (n, r.stdout.split()[0][:8]))
        text = {}
        for n in bodies:
            r = subprocess.run(['gh', 'pr', 'view', n, '--repo', GH_REPO, '--json', 'body', '-q', '.body'],
                               capture_output=True)
            need(r.returncode == 0, 'gh pr view %s' % n)
            if hashlib.sha256(r.stdout.rstrip(b'\n')).hexdigest() != bodies[n]['sha256']:
                live['body_drift'].append('PR%s' % n)
            text[int(n)] = norm(r.stdout.decode())
        for s in statements:
            if s['where'] == 'body':
                try:
                    check_quote(s, text[s['source']])
                except Fail as e:
                    live['missing_body_quotes'].append(str(e))
        print('live: head drift %s; body drift %s; body quotes not found %d' % (
            live['head_drift'] or 'none', live['body_drift'] or 'none', len(live['missing_body_quotes'])))
    out = dict(object='T74 handoff-line kappa ledger: stated numbers and release gates',
               kappas={'PR%d' % n: raw[n] for n in order}, statements=rows,
               flagged={k: dict(reason=EXPECTED_FLAGGED[k][0], printed_value_matches=v,
                                suggested=EXPECTED_FLAGGED[k][2][0]) for k, v in sorted(flagged.items())},
               ambiguous=sorted(ambiguous),
               release_gates=[dict(source=g['source'], named=g['named'], by=g['by'], comment_pr=g['comment_pr'],
                                   literal=g['literal_text'][:40], relation=g['relation'],
                                   gap=sci(g['literal'] - K[g['named']])) for g in gates],
               controls=dict(negative=neg, rejected=rej, corrections=pos), python=sys.version.split()[0])
    if live is not None:
        out['live'] = live
    if args.out:
        with open(os.path.join(HERE, 'ledger.receipt.json'), 'w') as f:
            f.write(json.dumps(out, indent=1, sort_keys=True, ensure_ascii=False) + '\n')
    nb = sum(1 for r in rows if r['where'] == 'body')
    line = ('T74_CLAIM_LEDGER prs=%d statements=%d (body %d, README %d) consistent=%d (ambiguous %d) flagged=%s '
            'gates=%d' % (len(K), len(rows), nb, len(rows) - nb, len(rows) - len(flagged), len(ambiguous),
                          ','.join(sorted(flagged)), len(gates)))
    drift = 0 if live is None else sum(len(v) for v in live.values())
    if drift:
        print('DRIFT_' + line + ' live_drift=%d' % drift)
        return 3
    print('PASS_' + line + ('' if live is None else ' live_drift=0'))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Fail as e:
        sys.stdout.write('FAIL_T74_CLAIM_LEDGER %s\n' % e)
        sys.exit(1)
