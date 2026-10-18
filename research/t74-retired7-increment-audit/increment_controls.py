#!/usr/bin/env python3
"""Negative controls for increment_audit.py: each mutant of the pinned inputs must be rejected by its named rule.

Word mutants carry an inverse-reverse cleanup re-derived from their own forward program, so a stale cleanup is never
the reason for a rejection.  Some controls also state which rules must ACCEPT the mutant ('must_accept') or the exact
set of rules that reject it ('exact_failing').  These expectations make the occupancy observations machine-checked: a
lender's dead write (after the lender's last read) moved past its alias warp is invisible to both scalar replays, and at
frame FULL also to the frame chain, the recount, the refits, the stage records, the fill and the price (C4d/C4e); a moved
lender read (C4f) or a moved write that precedes the lender's last read (C4g) is rejected by both replays and accepted by
the frame chain, fill and price.  A control counts only if every expectation holds and no rule crashed.

Prepared by thakrarsagar with substantial AI assistance from Claude (Anthropic, Claude Opus 5.5). Apache-2.0.
"""
import copy
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import increment_audit as A  # noqa: E402

FULLL = [256, 128, 64, 32, 16, 8, 4, 2, 1]
# rules re-run on every mutant: all except the parent positive control, the stage-chain and attribution rules and the
# above-floor neutrality rule, which rebuild, reprice or vary unmutated inputs (they run once on the pinned inputs)
SKIP = ('POSITIVE-PARENT', 'S1-STAGE-CHAIN', 'ATTRIBUTION', 'S3-ABOVE-FLOOR')
REPLAYS = ('S2-REPLAY-FREE-%s', 'S2-REPLAY-MATRIX-%s')
# every per-word rule on the pricing path: replays, frame chain, second recount, refits, stage records
PRICED = REPLAYS + ('S3S4-FRAMES-PROFILE-%s', 'S4-FRAMES-RREF-%s', 'S3-REFIT-EXACT-%s', 'S1-STAGE-RECORDS-%s')
# and the global ones: fill with word-derived R, fill transform, complete profile, mass and root
PRICED_GLOBAL = ('S5-FILL-WORD-DERIVED-R', 'S5-FILL-TRANSFORM', 'S6-PROFILE-MASS-ROOT')


def rederive(w):
    ev = A.program(w)
    der, _ = A.derive_cleanup(w, ev)
    w['cleanup'] = [list(x) + [FULLL] for x in der]
    return w


def relabel_B(w, start, a, b, stop=None):
    for i in range(start, len(w['B']) if stop is None else stop):
        e = w['B'][i]
        if e[0] == 'add':
            if e[1] == a:
                e[1] = b
            if e[2] == a:
                e[2] = b
        elif e[1] == a:
            e[1] = b


def last_A(w, r, role):
    """index of register r's last A event in role 'write' (r is the written register), 'read' (r is an add's source) or
    'prewrite' (the last write to r that precedes r's last read, i.e. a write whose value is still read in A)"""
    def ok(e, rl):
        if e[0] == 'warp':
            return False
        if rl == 'write':
            return e[1] == r
        return e[0] == 'add' and e[2] == r
    if role == 'prewrite':
        lr = last_A(w, r, 'read')
        return max(i for i, e in enumerate(w['A']) if i < lr and ok(e, 'write'))
    return max(i for i, e in enumerate(w['A']) if ok(e, role))


def mutants(js):
    st = {s: js['ST_%s_base' % s] for s in A.STAGES}
    out = []

    def word(name, expect, f, tag='base', must_accept=(), exact_failing=None):
        w = copy.deepcopy(js['W_' + tag])
        f(w)
        rederive(w)
        m = dict(js)
        m['W_' + tag] = w
        out.append((name, expect, m, dict(must_accept=list(must_accept), exact_failing=exact_failing)))

    # C1 refit7 undone (B911 back to its previous dim-6 frame)
    prev = {(s, i): F for s, i, F in st['refit7']['previous_frames']}
    word('C1 refit7 B911 undone', 'S3S4-FRAMES-PROFILE-base', lambda w: w['B'][911].__setitem__(-1, prev[('B', 911)]))

    # C2 hostee move of warp 30 reverted: record back to 401 at 941 and the hostee's gates back on 401
    def c2(w):
        mv = st['hostmove2']['moves'][0]
        w['warps'][29] = copy.deepcopy(mv['old_record'])
        relabel_B(w, mv['old_pos'], 564, 401)
    word('C2 hostee move 401->564 reverted (401 then hosts follower 667 and hostee 30 at once)', 'OCC-TIMELINE-base', c2)

    # C3 early alias warp for a B-retired lender: warp 66 (606<-550) placed before 550's last gate B901
    word('C3 alias warp 66 moved before lender 550 last gate (B901)', 'OCC-TIMELINE-base', lambda w: w['warps'][65].__setitem__(0, 901))

    # C4a-C4g: an A-retired lender's A event moved past its alias warp.  Lender 401 (alias warp 71 at B259) on the
    # base word; lender 403 (alias warp 72 at B262) on the extra word.
    def into_B(r, pos):
        def f(w):
            g = w['A'].pop(last_A(w, r, 'write'))
            w['B'].insert(pos, g)
            for rec in w['warps']:
                if rec[0] > pos:
                    rec[0] += 1
        return f

    def to_restore(r, role, full):
        def f(w):
            g = w['A'].pop(last_A(w, r, role))
            if full:
                g = list(g[:-1]) + [FULLL]
            w['restore'].append(g)
        return f
    word('C4a lender 401: last A write (A3175) moved into B right after alias warp 71, own frame', 'S3S4-FRAMES-PROFILE-base',
         into_B(401, 259), must_accept=[x % 'base' for x in REPLAYS])
    word('C4b lender 401: last A write moved to the end of restore, own frame', 'OCC-TIMELINE-base',
         to_restore(401, 'write', False), must_accept=[x % 'base' for x in REPLAYS])
    word('C4c lender 403 (extra word): last A write (A3174) moved into B right after alias warp 72, own frame',
         'S3S4-FRAMES-PROFILE-extra', into_B(403, 262), tag='extra', must_accept=[x % 'extra' for x in REPLAYS])
    word('C4d lender 401: last A write moved to the end of restore at frame FULL', 'OCC-TIMELINE-base',
         to_restore(401, 'write', True), must_accept=[x % 'base' for x in PRICED] + list(PRICED_GLOBAL),
         exact_failing=['OCC-TIMELINE-base', 'S1-DIFF-base', 'X-2818-SAME-CONSTRUCTION'])
    word('C4e lender 403 (extra word): last A write moved to the end of restore at frame FULL', 'OCC-TIMELINE-extra',
         to_restore(403, 'write', True), tag='extra', must_accept=[x % 'extra' for x in PRICED] + list(PRICED_GLOBAL),
         exact_failing=['OCC-TIMELINE-extra', 'S1-DIFF-extra', 'X-2818-SAME-CONSTRUCTION'])
    # C4f/C4g change what is computed: both replays reject them, while the frame chain, recount, refits, stage records,
    # fill and price accept them (they price the moved gate at FULL exactly as C4d does)
    computed = [x % 'base' for x in PRICED if x not in REPLAYS] + list(PRICED_GLOBAL)
    changed = ['S2-REPLAY-FREE-base', 'S2-REPLAY-MATRIX-base', 'OCC-TIMELINE-base', 'S1-DIFF-base', 'X-2818-SAME-CONSTRUCTION']
    word('C4f lender 401: last A read (an add with source 401) moved to the end of restore at frame FULL', 'S2-REPLAY-FREE-base',
         to_restore(401, 'read', True), must_accept=computed, exact_failing=changed)
    word('C4g lender 401: last A write before its last read (A3158) moved to the end of restore at frame FULL',
         'S2-REPLAY-MATRIX-base', to_restore(401, 'prewrite', True), must_accept=computed, exact_failing=changed)

    # C5 alias warp after the follower's first gate (the replacement control of #2802), A-retired lender 401
    word('C5 alias warp 71 after follower 667 first gate (B260)', 'OCC-TIMELINE-base', lambda w: w['warps'][70].__setitem__(0, 260))

    # C6 wrong G on alias warp 71
    def c6(w):
        g = w['warps'][70][2]
        g[0] ^= g[1]
    word('C6 wrong G on warp 71', 'S3S4-FRAMES-PROFILE-base', c6)

    # C7 U is not the lender's propagated frame: consistent pair (U', G(U')) with a different U'
    def c7(w):
        rec = w['warps'][70]
        U2 = [1, 2, 4, 8]
        rec[3] = U2
        rec[4] = [A.gapply(rec[2], u) for u in U2]
    word("C7 warp 71 with G(U')=E' for a U' that is not 401's propagated frame", 'S3S4-FRAMES-PROFILE-base', c7)

    # C8 keep removed follower 667 (both words): the word-derived R becomes 409 while the providers still say 408
    m = dict(js)
    for tag in ('base', 'extra'):
        w = copy.deepcopy(js['W_' + tag])
        w['removed'] = [h for h in w['removed'] if h != 667]
        m['W_' + tag] = rederive(w)
    out.append(('C8 removed follower 667 kept as a live helper (R self-reference)', 'S5-FILL-WORD-DERIVED-R', m, {}))

    # C9 swap the two alias lenders of warps 71/72 (declaration conformance: each alias warp sits on its declared lender)
    def c9(w):
        w['warps'][70][1], w['warps'][71][1] = w['warps'][71][1], w['warps'][70][1]
    word('C9 alias lenders of warps 71/72 swapped (declaration conformance)', 'OCC-TIMELINE-base', c9)

    # C10 drop one restore read
    word('C10 first restore gate dropped', 'S2-REPLAY-FREE-base', lambda w: w['restore'].pop(0))

    # C11 R + 1 in the fill: one extra helper index per call
    m = dict(js)
    f = copy.deepcopy(js['FILL'])
    extra = [[t, 408, o, c, p, off] for (t, h, o, c, p, off) in f['rows'] if h == 407]
    f['rows'] = f['rows'] + extra
    m['FILL'] = f
    out.append(('C11 fill inflated to R+1 helper indices', 'S5-FILL-WORD-DERIVED-R', m, {}))

    # C12 one hostee gate left on the old lender 401
    def c12(w):
        i = next(i for i in range(941, len(w['B'])) if 564 in A.regs(w['B'][i]))
        relabel_B(w, i, 564, 401, stop=i + 1)
    word('C12 first hostee gate of warp 30 left on old lender 401', 'S1-DIFF-base', c12)

    # C13 undeclared frame change on a gate outside every refit list
    def c13(w):
        declared = {(s, i) for x in ('refit5', 'refit5c', 'refit7', 'refit7c') for s, i, _ in st[x]['frames']}
        i = next(i for i in range(1500, len(w['B'])) if ('B', i) not in declared and w['B'][i][0] == 'add' and len(w['B'][i][-1]) < 9)
        w['B'][i][-1] = FULLL
    word('C13 undeclared frame raise on a B gate', 'S1-DIFF-base', c13)

    # C14 #2818 copy of the base word altered by one coefficient
    m = dict(js)
    x = copy.deepcopy(js['X_W_base'])
    x['B'][0][3] = -x['B'][0][3]
    m['X_W_base'] = x
    out.append(('C14 #2818 base word differs by one sign', 'X-2818-SAME-CONSTRUCTION', m, {}))
    return out


def run(js, log=print):
    res = {}
    ok = True
    for name, expect, m, exp in mutants(js):
        r = A.run_all(m, log=lambda s: None, skip=SKIP)
        failing = sorted(k for k, v in r['rules'].items() if not v['ok'])
        crashed = sorted(k for k, v in r['rules'].items() if not v['ok'] and str(v['info']).startswith('ERROR'))
        good = expect in failing and not str(r['rules'][expect]['info']).startswith('ERROR')
        acc = list(exp.get('must_accept', ()))
        acc_ok = all(k in r['rules'] and r['rules'][k]['ok'] for k in acc)
        exact = exp.get('exact_failing')
        exact_ok = exact is None or failing == sorted(exact)
        this = good and acc_ok and exact_ok and not crashed
        ok &= this
        entry = dict(expected_rule=expect, rejected_by_expected_rule=good, failing_rules=failing,
                     expected_rule_message=r['rules'][expect]['info'] if expect in r['rules'] else None,
                     crashed_rules=crashed, control_ok=this)
        if acc:
            entry.update(must_accept=acc, accepted_as_expected=acc_ok)
        if exact is not None:
            entry.update(exact_failing=sorted(exact), exact_failing_ok=exact_ok)
        res[name] = entry
        log('%s %-80s expected %-28s failing=%s' % ('REJECTED' if this else 'CONTROL-FAILURE', name[:80], expect, ','.join(failing)))
    return ok, res


if __name__ == '__main__':
    repo = sys.argv[1]
    js = A.load_all(repo, None)
    ok, res = run(js)
    if len(sys.argv) > 2:
        with open(sys.argv[2], 'w') as fh:
            json.dump(res, fh, indent=1, sort_keys=True, default=str)
    print('ALL_CONTROLS_REJECTED' if ok else 'CONTROL_FAILURE')
    sys.exit(0 if ok else 1)
