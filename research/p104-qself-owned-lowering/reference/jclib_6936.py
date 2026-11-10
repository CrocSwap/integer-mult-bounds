"""Library of check_caller_blocks.py: constant-block rewrite of the joint caller (idea and method: CubeJerry #6912; the code is this package's).

Mathematics.  A constant block is a maximal run of ADD / SCALE(-1) / SWAP events of one port type between two
nonconstant events of that type (LAMBDA, IDLE_ONE, QUERY) or a joint contact J.  Applied to the role vector it is
left-multiplication by one integer matrix M in GL_n(Z) (n = 40 for type A, 38 for type B).  Replace the block by any other
constant block with the same matrix M: then, by induction over the anchors, the whole caller is the same operator for every
substitution of the anchor operators (the anchors are not touched and each block is a left factor between them).
Type A rows (0..39) and type B rows (40..77) are disjoint, so an A block commutes with every B event: its position inside the
window between the same two A-anchors is immaterial.  Nothing but the constant-gate count changes."""
import json, random
from fractions import Fraction as Q

CONST = ('ADD', 'SCALE', 'SWAP')
OFF = {'A': 0, 'B': 40}
NR = {'A': 40, 'B': 38}


def need(ok, msg):
    if not ok:
        raise ValueError(msg)


def ev_roles(e):
    """role indices an event reads or writes (joint indexing); J returns both types' roles"""
    if e[0] == 'J':
        return list(e[2]) + list(e[3][:2])
    op = e[1]
    if op in ('ADD', 'SWAP', 'QUERY'):
        return [e[2], e[3]]
    return [e[2]]


def check_disjoint(C):
    """every A event touches only roles 0..39, every B event only 40..77 (J is the only coupling)"""
    for e in C['events']:
        if e[0] == 'A':
            need(all(0 <= r < 40 for r in ev_roles(e)), 'A event leaves its roles: %r' % (e,))
        elif e[0] == 'B':
            need(all(40 <= r < 78 for r in ev_roles(e)), 'B event leaves its roles: %r' % (e,))
        else:
            need(e[0] == 'J', 'unknown tag')
    return True


def is_const(e, ty):
    return e[0] == ty and e[1] in CONST


def is_anchor(e, ty):
    """nonconstant event of the type's own stream: its nonconstant events and every joint contact"""
    return (e[0] == ty and e[1] not in CONST) or e[0] == 'J'


def slots(events, ty):
    """list of (indices of the constant events of slot k); slot k lies between anchors k-1 and k.  Also returns the
    global index of the anchor that closes each slot (len(events) for the last)."""
    out, closes, cur = [], [], []
    for i, e in enumerate(events):
        if is_const(e, ty):
            cur.append(i)
        elif is_anchor(e, ty):
            out.append(cur); closes.append(i); cur = []
    out.append(cur); closes.append(len(events))
    return out, closes


def apply_const(rows, e):
    """act on the matrix of accumulated rows exactly as the caller replay does: rows[i] += c*rows[j] etc (joint indices)"""
    op = e[1]
    if op == 'ADD':
        c = Q(e[4]); need(c.denominator == 1, 'integer ADD'); c = int(c)
        rows[e[2]] = [a + c * b for a, b in zip(rows[e[2]], rows[e[3]])]
    elif op == 'SCALE':
        c = Q(e[3]); need(c == -1, 'SCALE -1'); rows[e[2]] = [-a for a in rows[e[2]]]
    elif op == 'SWAP':
        rows[e[2]], rows[e[3]] = rows[e[3]], rows[e[2]]
    else:
        raise ValueError('nonconstant')


def block_matrix(block, ty):
    """exact integer matrix of a constant block (list of full joint events), n x n in type-local indices"""
    n, off = NR[ty], OFF[ty]
    rows = {off + i: [int(i == j) for j in range(n)] for i in range(n)}
    for e in block:
        need(e[0] == ty and e[1] in CONST, 'block holds a nonconstant or foreign event')
        for r in ([e[2], e[3]] if e[1] != 'SCALE' else [e[2]]):
            need(off <= r < off + n, 'role outside type')
        apply_const(rows, e)
    return [rows[off + i] for i in range(n)]


def alphabet_ok(block, limit=2):
    for e in block:
        if e[1] == 'ADD':
            c = Q(e[4]); need(c.denominator == 1 and 0 < abs(c) <= limit, 'ADD coefficient outside alphabet %r' % (e,))
            need(e[2] != e[3], 'self ADD')
        elif e[1] == 'SCALE':
            need(Q(e[3]) == -1, 'SCALE not -1')
        elif e[1] == 'SWAP':
            need(e[2] != e[3], 'self SWAP')
    return True


def splice(C, ty, new_blocks):
    """new_blocks[k] = list of full joint events for slot k of type ty.  New block is written at the position of the first
    old event of its slot (or just before the closing anchor if the old slot was empty).  Everything else keeps its order."""
    sl, closes = slots(C['events'], ty)
    need(len(new_blocks) == len(sl), 'slot count %d != %d' % (len(new_blocks), len(sl)))
    first, drop, ins = {}, set(), {}
    for k, idxs in enumerate(sl):
        if idxs:
            first[idxs[0]] = k; drop.update(idxs[1:])
        elif new_blocks[k]:
            ins.setdefault(closes[k], []).append(k)
    ev = []
    for i, e in enumerate(C['events']):
        for k in ins.get(i, []):
            ev.extend(json.loads(json.dumps(x)) for x in new_blocks[k])
        if i in drop:
            continue
        if i in first:
            ev.extend(json.loads(json.dumps(x)) for x in new_blocks[first[i]])
        elif not is_const(e, ty):
            ev.append(e)
        # a first-index const event is replaced above; other const events of this type are in drop
    for k in ins.get(len(C['events']), []):
        ev.extend(new_blocks[k])
    out = {k: v for k, v in C.items() if k != 'events'}
    out['events'] = ev
    return out


def old_blocks(C, ty):
    sl, _ = slots(C['events'], ty)
    return [[C['events'][i] for i in idxs] for idxs in sl]


def from_6912(after, ty='A'):
    """read #6912's caller-after.json (plain A-stream events, no tag) as data: list of per-slot blocks, tagged joint events.
    slots are delimited by its nonconstant events (everything that is not ADD/SCALE/SWAP)."""
    blocks, cur, anchors = [], [], []
    for e in after['events']:
        if e[0] in CONST:
            cur.append([ty] + list(e))
        else:
            blocks.append(cur); cur = []; anchors.append(e)
    blocks.append(cur)
    return blocks, anchors


# ---------------------------------------------------------------- exact replay of the joint caller mod p
PM = 2147483629
IM = next(pow(g, (PM - 1) // 4, PM) for g in range(2, 99) if pow(g, (PM - 1) // 2, PM) == PM - 1)
HALF = (PM + 1) // 2


def fm(x):
    f = Q(x); return f.numerator % PM * pow(f.denominator, PM - 2, PM) % PM


def replay_matrix(C, qv, Dv):
    """the full 78 x 78 matrix of the joint caller at the point (q, D_1..D_18) over F_PM; semantics as in the package
    (J = HOST2 on the A roles and HOST on the B roles at one stage)."""
    n = C['roles']; R = [[int(i == j) for j in range(n)] for i in range(n)]; qi = pow(qv, PM - 2, PM)
    a2 = fm(C['types']['A']['alpha2'])
    for e in C['events']:
        if e[0] == 'J':
            d = Dv[e[1]]; src, dst, x2, y2 = e[2]
            R[dst] = [(a + qi * b) % PM for a, b in zip(R[dst], R[src])]
            R[x2] = [(a + a2 * qv % PM * b) % PM for a, b in zip(R[x2], R[y2])]
            for r in (src, dst, x2, y2):
                R[r] = [a * d % PM for a in R[r]]
            s, t = e[3][0], e[3][1]; al, be = fm(e[3][2]), fm(e[3][3]); tt = al * be % PM
            ns = [(x + al * qv % PM * y) % PM * d % PM for x, y in zip(R[s], R[t])]
            nd = [(be * qi % PM * x + (1 + tt) * y) % PM * d % PM for x, y in zip(R[s], R[t])]
            R[s], R[t] = ns, nd
            continue
        op = e[1]
        if op == 'ADD':
            R[e[2]] = [(a + fm(e[4]) * b) % PM for a, b in zip(R[e[2]], R[e[3]])]
        elif op == 'SCALE':
            c = fm(e[3]); R[e[2]] = [a * c % PM for a in R[e[2]]]
        elif op == 'SWAP':
            R[e[2]], R[e[3]] = R[e[3]], R[e[2]]
        elif op == 'QUERY':
            c = pow(qv, e[4] % 4, PM); R[e[2]] = [(a + c * b) % PM for a, b in zip(R[e[2]], R[e[3]])]
        elif op == 'LAMBDA':
            s = e[3]; c = ((1 + s * IM) * HALF + (1 - s * IM) * HALF * qv * qv) % PM; R[e[2]] = [a * c % PM for a in R[e[2]]]
        elif op == 'IDLE_ONE':
            c = 1
            for k in e[3]:
                c = c * Dv[k] % PM
            R[e[2]] = [a * c % PM for a in R[e[2]]]
        else:
            raise ValueError('unknown op ' + str(op))
    return R


def target_bad(C, R, qv, Dv):
    n = C['roles']; bad = 0
    for role in range(n):
        t, off = (C['types']['A'], 0) if role < 40 else (C['types']['B'], 40)
        dg = t['diagonal'][role - off]; c = pow(qv, dg[0] % 4, PM)
        for k, bit in enumerate(dg[2:]):
            if bit:
                c = c * Dv[k + 1] % PM
        bad += sum(R[role][j] != (c if j == role else 0) for j in range(n))
    return bad


def random_points(seed=5, k=4):
    r = random.Random(seed); pts = []
    for qv in (1, IM, PM - 1, PM - IM):
        pts.append((qv, {s: r.randrange(2, PM) for s in range(1, 19)}))
    for _ in range(k):
        pts.append((r.randrange(2, PM), {s: r.randrange(2, PM) for s in range(1, 19)}))
    return pts


# ---------------------------------------------------------------- own resynthesis of a constant block (Euclid elimination)
def synth(M, ty):
    """own synthesis: reduce M to I by row operations with a Euclidean algorithm per column, ADD coefficients split into
    +-1,+-2; the op list that rebuilds M is the reversed list of inverses.  Local indices; returns full joint events."""
    n, off = NR[ty], OFF[ty]; M = [r[:] for r in M]; ops = []

    def add(i, j, c):          # row_i += c * row_j   (c in {+-1,+-2} after splitting)
        while c:
            s = 1 if c > 0 else -1; step = s * min(2, abs(c))
            M[i] = [a + step * b for a, b in zip(M[i], M[j])]; ops.append(('ADD', i, j, step)); c -= step
    for col in range(n):
        while True:
            nz = [r for r in range(col, n) if M[r][col]]
            need(nz, 'singular block')
            if len(nz) == 1 and abs(M[nz[0]][col]) == 1:
                break
            p = min(nz, key=lambda r: (abs(M[r][col]), r))
            for r in nz:
                if r != p:
                    qq = round(Q(M[r][col], M[p][col]))
                    if qq:
                        add(r, p, -qq)
        p = nz[0]
        if p != col:
            M[p], M[col] = M[col], M[p]; ops.append(('SWAP', p, col))
        if M[col][col] == -1:
            M[col] = [-a for a in M[col]]; ops.append(('SCALE', col))
        for r in range(n):
            if r != col and M[r][col]:
                add(r, col, -M[r][col])
    need(all(M[i][j] == int(i == j) for i in range(n) for j in range(n)), 'did not reach identity')
    out = []
    for o in reversed(ops):
        if o[0] == 'ADD':
            out.append([ty, 'ADD', o[1] + off, o[2] + off, str(-o[3])])
        elif o[0] == 'SWAP':
            out.append([ty, 'SWAP', o[1] + off, o[2] + off])
        else:
            out.append([ty, 'SCALE', o[1] + off, '-1'])
    return out


# ---------------------------------------------------------------- raw bound (formulas of the package's check.py / ordinary.py)
def swaps(sel):
    wanted = set(range(len(sel))); return len(list(zip(sorted(set(sel) - wanted), sorted(wanted - set(sel)))))


def shim(J, ty):
    t = J['types'][ty]; off = t['offset']; ev = []
    for e in J['events']:
        if e[0] == 'J':
            ev.append(['HOST', e[1]])
        elif e[0] == ty:
            e = list(e[1:])
            if e[0] in ('ADD', 'SWAP', 'QUERY'):
                e[1] -= off; e[2] -= off
            else:
                e[1] -= off
            ev.append(e)
    return dict(events=ev, roles=t['roles'], ambient_rank=J['ambient_rank'], diagonal=t['diagonal'])


def rest_of(C, ports):
    ev = C['events']; roles = C['roles']; amb = C['ambient_rank']; mx = mn = mp = 0
    for role, (qp, zero, *sel) in enumerate(C['diagonal']):
        axes = ([0] if qp else []) + [a for st, y in enumerate(sel, 1) if y for a in range(9 + 8 * (st - 1), 9 + 8 * st)]
        k = swaps(axes); mx += 2 * k * ports; mn += 2 * bool(qp) * ports; mp += int(qp == -1) * ports
    ie = 0; qn = qph = 0
    for e in ev:
        if e[0] == 'IDLE_ONE':
            ie += 2 * swaps([a for st in e[2] for a in range(9 + 8 * (st - 1), 9 + 8 * st)]) * ports
        elif e[0] == 'QUERY':
            qn += 2 * ports; qph += int(e[3] == -1) * ports
    return (32 * roles * ports * len(ev) + sum(e[0] == 'QUERY' for e in ev) * 16 * ports + roles * ports * 26
            + (mx + mn + mp) * 1000 + ie * 1000 + (qn + qph) * 1000)


def word_terms(W):
    """per-call terms of a word: allowance, reviewed upper, routes, public count, nD"""
    from collections import Counter
    H = W['hosted']; nD = len(H['Dports']); n = len(W['initial']); live = set(W['live'])
    main = live | {r + 112 for r in live} | set(H['X2']) | set(H['Y2'])
    dim = [len(b) for b in W['frames']]
    paid = Counter(abs(dim[e[3]] - dim[e[2]]) for e in W['program'] if e[0] == 'MOVE')
    hel = Counter(dim[W['final'][r]] - dim[W['initial'][r]] for r in range(n) if r not in main)
    life = sum(e[0] == 'INIT' for e in W['program']); allow = upper = 0
    for e in W['program']:
        if e[0] in ('INIT', 'CLEAR'):
            allow += 2
        elif e[0] == 'SCALE':
            q = Q(e[2]); a, d = abs(q.numerator), q.denominator
            allow += 2 * (abs(a.bit_length() - d.bit_length()) + int(q < 0)); upper += 4 * (a.bit_length() + d.bit_length() + 1)
        elif e[0] in ('ADD', 'COPY'):
            q = Q(e[3]); a, d = abs(q.numerator), q.denominator
            allow += 2 * (3 + a.bit_length() - 1 + bin(a).count('1') + d.bit_length() - 1); upper += 4 * (a.bit_length() + bin(a).count('1') + d.bit_length() + 1)
    routes = (sum(paid.values()) + 2 * sum(hel.values()) + 208 + 2 * nD + 4 * 104 + 4 * nD + 4 * life) * 1000
    return dict(allow=allow, upper=upper, routes=routes, n=n, nD=nD, paid=paid, hel=hel)


scale_cost = lambda S: 4 * (S.bit_length() + 1 + 1) + 4 * (1 + S.bit_length() + 1)       # one SCALE by S at entry and one by 1/S at exit at the reviewed upper rate: 80 for S = 225, 104 for S = 1125


def raw_all(J, W, S):
    t = word_terms(W); nA, nB = len(J['types']['A']['ports']), len(J['types']['B']['ports'])
    need((nA, nB) == (t['nD'], 104 - t['nD']), 'port split of the caller differs from the word')
    rest = rest_of(shim(J, 'A'), nA) + rest_of(shim(J, 'B'), nB)
    lam = sum(1 for e in J['events'] if e[0] == 'A' and e[1] == 'LAMBDA') * nA + sum(1 for e in J['events'] if e[0] == 'B' and e[1] == 'LAMBDA') * nB
    debit = 1000 * lam; per_in = 18 * t['n'] * scale_cost(S)
    lit = 18 * 10 ** 7 + rest; act = 18 * (t['allow'] + t['routes']) + rest; up = 18 * (t['upper'] + t['routes']) + rest
    return dict(rest=rest, literal=lit, actual=act, upper=up, recharge=up + debit, per_input=up + per_in, per_input_recharge=up + per_in + debit,
                lambda_jobs=lam, debit=debit, per_in=per_in, public=t['n'])
