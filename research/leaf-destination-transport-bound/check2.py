"""Exact finite checks for PROOF.md (free noncommutative algebra, PR628 balanced dirty word).

Checks, per size n and word generator `mode`:
  INV   word(n,-s) is word(n,s) reversed with every leaf sign negated              (Lemma I)
  L1    exit column of every injection: entries 0 or +-monomial, source entry 0     (PROOF.md L1)
  X     exit support <= floor(log2 n)+1, its scratch part <= floor(log2 n); both tight (Lemma X)
  CASE  top-call LCA table equals the closed forms of PROOF.md section 3, both signs (Thm 1 cases)
  E     full census E(n) == max(1, floor(log2 n))                                    (Thm 1 + Thm 2)
  P     sign +: at the V-chain cut, row y depends on x and on every scratch level   (Lemma P)
  FAM   explicit family interval has mass floor(log2 n), no cancellation            (Thm 2)
Modes: ok (PR628), and mutations unrev (sign - not reversed), swap (B = ceil half), drop (top
call omits its last phase).  Usage: python3 check2.py MODE LO HI [famHI]
"""
import sys

NAMES_P = ('U', 'V', "U'", "V'")


def gen(n, sign=1, x=0, y=1, depth=2, off=0, path=(), mode='ok'):
    """Leaves ((src,dst,factor,sign), path) in time order; path = tuple of phase names."""
    if n == 1:
        return [((x, y, off, sign), path)]
    b = n // 2 if mode != 'swap' else n - n // 2
    ops = [(x, depth, off, b, 1, 'U'), (depth, y, off + b, n - b, 1, 'V'),
           (x, depth, off, b, -1, "U'"), (depth, y, off + b, n - b, -1, "V'")]
    if sign == -1:
        ops = [(s, d, o, k, -g, nm) for s, d, o, k, g, nm in (ops if mode == 'unrev' else reversed(ops))]
    ops = [(s, d, o, k, g, nm[0] + ('' if g == 1 else "'")) for s, d, o, k, g, nm in ops]  # name = letter + sign
    if mode == 'drop' and depth == 2:
        ops = ops[:-1]
    out = []
    for s, d, o, k, g, nm in ops:
        out += gen(k, g, s, d, depth + 1, o, path + (nm,), mode if mode != 'drop' else 'ok')
    return out


def fl(n):
    return n.bit_length() - 1


def step(col, x, y, j, s):
    cx = col.get(x)
    if not cx:
        return None
    cy = col.setdefault(y, {})
    for m, c in cx.items():
        k = (j,) + m
        v = cy.get(k, 0) + s * c
        if v:
            cy[k] = v
        else:
            del cy[k]
    return cy


def mass(p):
    return sum(abs(c) for c in p.values())


def expected_case(m, s, a, b):
    if (s, a, b) in ((1, 'U', 'V'), (1, 'U', "V'"), (1, "U'", "V'"), (-1, 'U', "V'")):
        return max(1, fl(m))
    if (a, b) == ('U', "U'"):
        return max(1, fl(m) - 1)
    if a not in ('V', "V'"):
        return None                      # phase pair absent from the PR628 schedule
    return max(1, fl(m + 1) - 1)


def full_pass(n, mode):
    """One exact pass over all (injection, later cut) pairs for both orientations."""
    fails = []
    E = 1
    Xmax = Xs = 0
    for s in (1, -1):
        W = gen(n, s, mode=mode)
        w = [e for e, _ in W]
        ph = [p[0] if p else None for _, p in W]
        L = len(w)
        case = {}
        for p in range(L):
            col = {w[p][1]: {(): 1}}
            prev_ph = ph[p]
            for t in range(p + 1, L):
                cy = step(col, *w[t])
                if ph[t] != prev_ph:          # first cut in a new top phase: scan all registers
                    prev_ph = ph[t]
                    cur = max(mass(v) for v in col.values())
                else:
                    cur = mass(cy) if cy is not None else 0
                if cur > E:
                    E = cur
                if ph[t] != ph[p]:
                    k = (ph[p], ph[t])
                    if cur > case.get(k, 0):
                        case[k] = cur
            # exit column of the whole call (Lemma L1 / Lemma X)
            sup = [r for r, v in col.items() if v]
            if any(mass(v) > 1 for v in col.values()) or col.get(0):
                fails.append(('L1', s, p))
            Xmax = max(Xmax, len(sup))
            Xs = max(Xs, len([r for r in sup if r >= 2]))
        if n >= 2:
            for k, v in sorted(case.items()):
                if v != expected_case(n, s, *k):
                    fails.append(('CASE', s, k, v, expected_case(n, s, *k)))
    if Xmax != fl(n) + 1 or Xs != fl(n):
        fails.append(('X', Xmax, Xs, fl(n) + 1, fl(n)))
    if E != max(1, fl(n)):
        fails.append(('E', E, max(1, fl(n))))
    return E, Xmax, Xs, fails


def check_inv(n, mode):
    a = [e for e, _ in gen(n, 1, mode=mode)]
    b = [e for e, _ in gen(n, -1, mode=mode)]
    return b == [(x, y, j, -g) for x, y, j, g in reversed(a)]


def call_sign(path, top=1):
    """Sign of the call at `path`: a phase's name carries its own sign (prime = negative)."""
    return top if not path else (-1 if path[-1].endswith("'") else 1)


def check_P(n, mode, s=1):
    """Lemma P: at the cut after the V-chain leaf of word(n,s), row y has x and all scratch levels."""
    W = gen(n, s, mode=mode)
    w = [e for e, _ in W]
    R = max(2, (n - 1).bit_length() + 2)
    vrule = lambda sg: 'V' if sg == 1 else "V'"
    try:
        t = find_leaf_signed(W, (), vrule, s)
    except Exception:
        return False
    cols = {v: {v: {(): 1}} for v in range(R)}
    for e in w[:t + 1]:
        for v in range(R):
            step(cols[v], *e)
    return all(cols[v].get(1) for v in [0] + list(range(2, R)))


def find_leaf_signed(W, prefix, rule, top):
    path = prefix
    for _ in range(64):
        hits = [i for i, (_, p) in enumerate(W) if p == path]
        if hits:
            return hits[0]
        path = path + (rule(call_sign(path, top)),)
    raise ValueError('no leaf')


def family(n, mode='ok'):
    """Explicit extremal interval (top sign +): inject at the alternating B-chain leaf of U,
    read row y at the cut after the V-chain leaf of V.  Returns (mass, #terms, exit ok)."""
    W = gen(n, 1, mode=mode)
    w = [e for e, _ in W]
    urule = lambda sg: "U'" if sg == 1 else 'U'
    vrule = lambda sg: 'V' if sg == 1 else "V'"
    p = find_leaf_signed(W, ('U',), urule, 1)
    t = find_leaf_signed(W, ('V',), vrule, 1)
    col = {w[p][1]: {(): 1}}
    endU = max(i for i, (_, q) in enumerate(W) if q[:1] == ('U',))
    for e in w[p + 1:endU + 1]:
        step(col, *e)
    ex = {r: v for r, v in col.items() if v}
    lens = sorted(len(next(iter(v))) for v in ex.values())
    exit_ok = (len(ex) == fl(n) and all(len(v) == 1 for v in ex.values())
               and len(set(lens)) == len(lens))
    for e in w[endU + 1:t + 1]:
        step(col, *e)
    row = col.get(1, {})
    return mass(row), len(row), exit_ok, (p + 1, t + 1), row


if __name__ == '__main__':
    mode, lo, hi = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    famhi = int(sys.argv[4]) if len(sys.argv) > 4 else hi
    bad = 0
    for n in range(lo, hi + 1):
        inv = check_inv(n, mode)
        P = check_P(n, mode, 1)          # Lemma P is a sign + statement
        E, Xm, Xs, fails = full_pass(n, mode)
        if not inv:
            fails.append(('INV',))
        if not P:
            fails.append(('P',))
        if n >= 2:
            fm, nt, eok, iv, _ = family(n, mode)
            if not (fm == nt == fl(n) and eok):
                fails.append(('FAM', fm, nt, eok))
        bad += bool(fails)
        print(mode, n, 'E', E, 'X', Xm, 'Xs', Xs, 'INV', inv, 'P', P, 'FAIL' if fails else 'ok',
              fails[:3], flush=True)
    for n in range(max(hi + 1, 2), famhi + 1):
        fm, nt, eok, iv, _ = family(n, mode)
        ok = fm == nt == fl(n) and eok
        bad += not ok
        print(mode, n, 'FAM-only', fm, nt, eok, iv, 'ok' if ok else 'FAIL', flush=True)
    print('SUMMARY', mode, lo, hi, famhi, 'failing sizes', bad)
