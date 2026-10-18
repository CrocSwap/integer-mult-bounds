# SPDX-License-Identifier: Apache-2.0
"""Shared helpers of the PR #2751 audit: word parsing with initial corrections, an own exact forward tracker,
exact linear algebra, derived-object hashes and the negative-control bookkeeping.

Model (the lineage's free-operator model, as in the vendored words_check.py of PR2315): every live register is an
independent dirty input symbol, private buffers start at zero, and each warp letter K_k is an abstract invertible
operator (a formal word with adjacent inverse cancellation).  Rows are {(symbol, word): Fraction}; words are tuples of
signed ints, newest letter first.

Initial corrections.  The vendored parser (words_check.parse_borrow) accepts only words without initial
(anticipatory) corrections.  PR2733's and PR2751's words carry 36 of them: {target t, source s, operator_word [k..],
coefficient q} meaning t += q K s before the precondition (PR2226 anticipatory borrowing, here PR2679's pre-life
hosting; the source must be at frame 0 at the start).  parse_word strips them before the vendored parser, validates
them, and correction_items emulates each one EXACTLY inside the vendored replay as the conjugated triple
warp(s, k) ... ; add t += q s ; warp(s, -k) ...: its forward action is t += q K s with s unchanged, and the vendored
dual replay (which processes the same items with t,s,c -> s,t,-c and dual letters) applies the transpose-inverse.
Corrections carry no frame charge (as in PR2679, PR2733 and PR2751); this is recorded, not re-derived.

Controls.  expect() runs one negative control: it records the attempt (audit_common.attempt), runs the mutant through
the given function, and requires it to raise with exactly the named rule id (and, for a replay, at the named stage);
any other exception type propagates and fails the run.  Rule ids: 'wc.<check>' for a vendored words_check rejection
(stage from check_words.reject_stage), the 'rule' prefix of an AuditFail message ('rule: detail'), or a
fill_check80.CheckFailure id.  Standard library only; Python 3.8-compatible syntax.
"""
import copy
import hashlib
import json
from collections import Counter, defaultdict
from fractions import Fraction

import audit_common as AC
import check_words as CW
import fill_check80 as FC
import words_check as WC
from audit_common import AuditFail, need

V, H = 112, 9
FULL_LIST = [1 << b for b in range(H)][::-1]
ONE = Fraction(1)


# --------------------------------------------------------------------------------------------- hashing ---
def canon(obj):
    """Canonical JSON text (sorted keys, no spaces; Fractions and tuples as their JSON-friendly forms)."""
    def conv(x):
        if isinstance(x, Fraction):
            return str(x)
        if isinstance(x, (set, frozenset)):
            return sorted(conv(y) for y in x)
        if isinstance(x, tuple):
            return [conv(y) for y in x]
        if isinstance(x, list):
            return [conv(y) for y in x]
        if isinstance(x, dict):
            return dict((str(k), conv(v)) for k, v in x.items())
        return x
    return json.dumps(conv(obj), sort_keys=True, separators=(',', ':'))


def sha(obj):
    return hashlib.sha256(canon(obj).encode()).hexdigest()


def hist(d):
    """{int rank: count} with string keys sorted numerically (for RESULT.json)."""
    return dict((str(k), d[k]) for k in sorted(d, key=int))


def intkeys(d):
    return dict((int(k), v) for k, v in d.items())


# --------------------------------------------------------------------------------- parse and replay ---
def parse_word(w):
    """check_words.parse_ext on the word without its initial corrections; the corrections are validated and kept as
    P['corrections'] = [(t, s, q, word)] (rule words.corrections)."""
    w2 = dict(w)
    corr = w.get('initial_corrections', [])
    need(isinstance(corr, list), 'words.corrections: initial_corrections is not a list')
    w2['initial_corrections'] = []
    P = CW.parse_ext(w2)
    out = []
    for i, c in enumerate(corr):
        need(isinstance(c, dict) and sorted(c) == ['coefficient', 'operator_word', 'source', 'target'],
             'words.corrections: correction %d fields' % i)
        t, s, word = c['target'], c['source'], c['operator_word']
        q = Fraction(c['coefficient'])
        need(WC.is_int(t) and V <= t < 2 * V, 'words.corrections: correction %d target is not a target' % i)
        need(WC.is_int(s) and s in P['start'] and not (V <= s < 2 * V) and s in set(P['live']),
             'words.corrections: correction %d source is not a live non-target' % i)
        need(P['start'][s] == (), 'words.corrections: correction %d source %d is not at frame 0 at the start' % (i, s))
        need(q != 0 and WC.dyadic(q), 'words.corrections: correction %d coefficient is not a non-zero dyadic' % i)
        need(isinstance(word, list) and len(word) > 0 and all(WC.is_int(k) and 1 <= abs(k) <= len(P['warps'])
                                                               for k in word),
             'words.corrections: correction %d operator word' % i)
        out.append((t, s, q, tuple(word)))
    P['corrections'] = out
    return P


def correction_items(corrections):
    """The conjugated triples (vendored internal item format) emulating t += q K s, K = K_w0 K_w1 ... (rightmost
    letter applied first)."""
    items = []
    for t, s, q, word in corrections:
        pre = [('warp', s, k) for k in reversed(word)]
        post = [('warp', s, -k) for k in word]
        items += pre + [('add', t, s, q, ())] + post
    return items


def with_corrections(P):
    Q = dict(P)
    Q['pre'] = correction_items(P['corrections']) + list(P['pre'])
    return Q


def replay(P, dual):
    """check_words.run_replay (the vendored words_check.replay, orientation recorded) with the corrections."""
    return CW.run_replay(with_corrections(P), dual)


def rederive_cleanup(w):
    return CW.rederive_cleanup(w)


def forge(w):
    """Mutant helper: make the word's self-reported fields (report.local_profile, report.width_inventory) equal its own
    frame recount, so that only the independent checks can reject it.  Returns the recount."""
    fr = CW.frame_recount(parse_word(w))
    w['report'] = dict(w['report'], local_profile=hist(fr['paid']), width_inventory=hist(fr['inventory']))
    return fr


def forge_providers(prov, key, fr):
    """A PROVIDERS.json copy whose entry `key` carries the recount fr (paid profile, ordered widths)."""
    p = copy.deepcopy(prov)
    p[key] = dict(p[key], actual_paid_profile=hist(fr['paid']), widths=list(fr['helper_widths']))
    return p


def delete_B(w, j):
    """Delete B[j]; every warp record stays attached to the B item it preceded."""
    del w['B'][j]
    for rec in w['warps']:
        if rec[0] > j:
            rec[0] -= 1


def insert_B(w, j, items):
    """Insert items before B[j]; warp records at positions > j move with their items, those at j stay before the
    inserted items."""
    w['B'][j:j] = items
    for rec in w['warps']:
        if rec[0] > j:
            rec[0] += len(items)


# ---------------------------------------------------------------------------------------- own tracker ---
def name(x):
    if isinstance(x, tuple):
        return '%s%d' % x
    return 'X%d' % x if x < V else ('Y%d' % (x - V) if x < 2 * V else 'H%d' % x)


def fmt(row):
    if not row:
        return '0'
    def key(kv):
        return (str(kv[0][0]), kv[0][1])
    return ' + '.join('%s*%s%s' % (v, ('K%s.' % '.'.join(map(str, w))) if w else '', name(x))
                      for (x, w), v in sorted(row.items(), key=key))


def nregs(w):
    return 2 * V + w['report']['R']


def init_rows(w):
    """Every live register its own symbol; every private buffer (helper_final key + n) zero."""
    n = nregs(w)
    removed = set(w['removed'])
    rows = dict((r, {(r, ()): ONE}) for r in range(n) if r not in removed)
    for k in w['helper_final']:
        rows[int(k) + n] = {}
    return rows


def events(w, cleanup=False, corrections=True):
    """The chronological forward program as (section, index, item): corrections (as warp/add/warp), precondition,
    compensation, A, cut, B with every warp record placed before B[pos] in record order ('Bwarp', op, ['warp',
    lender, op, U, E]), restore, and optionally cleanup."""
    ev = []
    if corrections:
        for i, c in enumerate(w.get('initial_corrections', [])):
            q = Fraction(c['coefficient'])
            for k in reversed(c['operator_word']):
                ev.append(('corr', i, ['warp', c['source'], k]))
            ev.append(('corr', i, ['add', c['target'], c['source'], q.numerator, q.denominator, []]))
            for k in c['operator_word']:
                ev.append(('corr', i, ['warp', c['source'], -k]))
    for sec in ('precondition', 'compensation', 'A', 'cut'):
        ev += [(sec, i, g) for i, g in enumerate(w[sec])]
    by_pos = defaultdict(list)
    for op, rec in enumerate(w['warps'], 1):
        by_pos[rec[0]].append((op, rec))
    for p in range(len(w['B']) + 1):
        for op, rec in by_pos[p]:
            ev.append(('Bwarp', op, ['warp', rec[1], op, rec[3], rec[4]]))
        if p < len(w['B']):
            ev.append(('B', p, w['B'][p]))
    ev += [('restore', i, g) for i, g in enumerate(w['restore'])]
    if cleanup:
        ev += [('cleanup', i, g) for i, g in enumerate(w['cleanup'])]
    return ev


def apply(rows, g):
    """Forward action of one raw item: ['add', t, s, num, den, F]: t += (num/den) s; ['scale', t, num, den, F];
    ['warp', reg, k, ...]: prefix the letter k on every term of reg, cancelling a leading -k."""
    kind = g[0]
    if kind == 'add':
        t, s, c = g[1], g[2], Fraction(g[3], g[4])
        need(t in rows and s in rows and t != s, 'tracker.item: add on an unknown register %r' % (g[:3],))
        dst = rows[t]
        for key, val in list(rows[s].items()):
            nv = dst.get(key, 0) + c * val
            if nv:
                dst[key] = nv
            else:
                dst.pop(key, None)
    elif kind == 'scale':
        need(g[1] in rows, 'tracker.item: scale on an unknown register')
        c = Fraction(g[2], g[3])
        rows[g[1]] = dict((k, v * c) for k, v in rows[g[1]].items() if v * c)
    elif kind == 'warp':
        reg, k = g[1], g[2]
        need(reg in rows and k != 0, 'tracker.item: warp on an unknown register')
        rows[reg] = dict(((var, word[1:] if word and word[0] == -k else (k,) + word), val)
                         for (var, word), val in rows[reg].items())
    else:
        raise AuditFail('tracker.item: unknown item %r' % (kind,))


def run(w, evs, rows=None, stop=None):
    """Apply evs to rows (default init_rows(w)); stop(section, index, item) -> True halts before that event."""
    rows = init_rows(w) if rows is None else rows
    for sec, i, g in evs:
        if stop is not None and stop(sec, i, g):
            return rows
        apply(rows, g)
    return rows


def own_symbol(r):
    return {(r, ()): ONE}


def target_final(t):
    return {(V + t, ()): ONE, (t, ()): ONE}


# ------------------------------------------------------------------------------------- linear algebra ---
def det(M):
    """Exact determinant (Gaussian elimination over Fractions)."""
    A = [list(map(Fraction, r)) for r in M]
    n, d = len(A), Fraction(1)
    for c in range(n):
        p = next((r for r in range(c, n) if A[r][c] != 0), None)
        if p is None:
            return Fraction(0)
        if p != c:
            A[c], A[p] = A[p], A[c]
            d = -d
        d *= A[c][c]
        for r in range(c + 1, n):
            f = A[r][c] / A[c][c]
            if f:
                A[r] = [a - f * b for a, b in zip(A[r], A[c])]
    return d


def rank(M):
    A = [list(map(Fraction, r)) for r in M]
    rk, nrows, ncols = 0, len(A), (len(A[0]) if A else 0)
    for c in range(ncols):
        p = next((r for r in range(rk, nrows) if A[r][c] != 0), None)
        if p is None:
            continue
        A[rk], A[p] = A[p], A[rk]
        for r in range(nrows):
            if r != rk and A[r][c] != 0:
                f = A[r][c] / A[rk][c]
                A[r] = [a - f * b for a, b in zip(A[r], A[rk])]
        rk += 1
    return rk


def strs(M):
    return [[str(x) for x in r] for r in M]


# ------------------------------------------------------------------------------------ control bookkeeping ---
def rule_of(exc):
    """(rule id, stage, message) of an audit rejection; None for any other exception."""
    if isinstance(exc, WC.Reject):
        return 'wc.' + exc.check, CW.reject_stage(exc), exc.msg
    if isinstance(exc, AuditFail):
        msg = str(exc)
        return msg.split(':', 1)[0], None, msg
    if isinstance(exc, FC.CheckFailure):
        return exc.check, None, str(exc)
    return None


def expect(out, name, rule, fn, stage=None, attrs=None, **extra):
    """Negative control: fn() must raise an audit rejection with exactly this rule id (and stage, if given; and, if
    attrs is given, with exception attributes equal to attrs, e.g. the exact set of flipped hypothesis booleans).
    The attempt is counted before fn runs; the record is appended only after the rejecting rule was checked."""
    AC.attempt(name)
    try:
        fn()
    except (WC.Reject, AuditFail, FC.CheckFailure) as e:
        got, where, msg = rule_of(e)
        seen = dict((k, getattr(e, k, None)) for k in sorted(attrs or ()))   # no reference to e is kept (cycles)
    else:
        raise AuditFail('negative control ACCEPTED: ' + name)
    need(got == rule and (stage is None or where == stage),
         'control %s: rejected by %s%s (%s), expected %s%s' % (name, got, '' if where is None else ' at %r' % where,
                                                                 ' '.join(msg.split())[:120], rule,
                                                                 '' if stage is None else ' at %r' % stage))
    if attrs is not None:
        need(seen == dict(attrs), 'control %s: rejected by %s with %r, expected %r' % (name, got, seen, dict(attrs)))
    rec = dict(control=name, expected=rule, rejected_by=got, message=' '.join(msg.split())[:160])
    if stage is not None:
        rec['stage'] = where
    if attrs is not None:
        rec['asserted'] = canonical_json(attrs)
    rec.update(extra)
    out.append(rec)
    return rec


def canonical_json(x):
    return json.loads(canon(x))


def harness_selftest():
    """expect() itself must fail on a mutant rejected by another rule, on an accepted mutant and on a mutant rejected
    by the right rule with other asserted attributes (checked here, then removed from the attempt counter, so they do
    not enter the negative-control counts)."""
    n0 = len(AC.ATTEMPTED)
    out = []
    res = {}

    def wrong_attrs():
        e = AuditFail('selftest.expected: rejected with other attributes')
        e.flipped = ['other']
        raise e
    for case, fn, attrs in (('wrong_rule', lambda: need(False, 'selftest.other: rejected by another rule'), None),
                            ('accepted', lambda: None, None),
                            ('wrong_attrs', wrong_attrs, dict(flipped=['expected']))):
        try:
            expect(out, 'harness self-test ' + case, 'selftest.expected', fn, attrs=attrs)
        except AuditFail as e:
            res[case + '_raises'] = str(e).startswith(('control harness self-test', 'negative control ACCEPTED'))
        else:
            res[case + '_raises'] = False
    del AC.ATTEMPTED[n0:]
    need(all(res.values()) and len(res) == 3 and not out, 'harness.selftest: expect() accepted a bad control %r' % res)
    return res


def mutant(w):
    return copy.deepcopy(w)


# Self-check registry: each self-check / scope-F check called from verify.py records its rule id here after it has
# passed; verify.py requires the counts to equal EXPECTED_SELF_CHECKS (so a check whose call is removed fails the run).
RAN = Counter()


def ran(rule):
    RAN[rule] += 1


def check_self_checks(counts, expected):
    """self_checks.ran: every registered check ran (and passed) exactly as often as expected."""
    need(dict(counts) == dict(expected), 'self_checks.ran: %r != %r' % (dict(counts), dict(expected)))


def counter_delta(a, b):
    """a - b as {rank: change}, zero entries dropped."""
    d = Counter(a)
    d.subtract(Counter(b))
    return dict((k, v) for k, v in sorted(d.items()) if v)
