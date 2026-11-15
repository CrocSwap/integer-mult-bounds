#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""PRICEKIT (our lane, vendored unchanged apart from this header): the one canonical exact pricer for P104 caller+native invoices.  Standard library only.

Accounting contract (README.md has the one-page version).  Units:
  rank r job     a paid job of rank r (P[r] += 1) or a productive target of rank r (T[r] += 1).
  S              rank-mass surplus  sum_r r (T_r - P_r)            (= F(0)).
  F(t)           the bill           sum_r (T_r - P_r) r^(1-t).
  kappa          the unique root of F on (0, hi]; certified by an interval enclosure (Decimal, error-bounded signs).
  D0             sum (T-P) r ln r        (= -F'(0); the HOSTCRIB/MAINRETIME/CALLERMAP "D", e.g. #6934 422589.15263423)
  Dk             sum (T-P) r^(1-kappa) ln r  (= -F'(kappa); the DSPLIT/ARCHEQ dk.py/TRADELAW "D(kappa)")

Charging rules (caller events, '#7113 format' = schema mixed-root-caller/1):
  port count      every caller event of type A/B is charged once per port of that type (len(types[t]['ports'])).
  QUERY           P[1]   per port (thin unit / sign query).
  IDLE_ONE s      P[8|s|] per port (one idle over the stage set s).
  IDLE_ODD s      P[8|s|+1] per port.
  LAMBDA          ordinary work, 1000 units per port-use (#6913).  lambda_mode='paid_rank1' charges P[1] per port
                  instead (counterfactual only).
  ADD/SWAP/SCALE  not invoiced (ordinary only).
  diagonal row    T[(q mod 2) + 8*sum(stage bits)] per port: a field of degree d is a target of rank 8d+1 (odd phase)
                  or 8d (even phase).  Hubs are fields with d = #stages (r137 at 17 stages).
  J (one stage)   ONE native word per J event: stage = call = J event = one copy of the native word.  The native word
                  serves all 104 ports internally, so it is NOT multiplied by ports.
Native word (schema p104-accumulated-block-composition/2):
  paid            P[|dim b - dim a|] per MOVE.
  helpers         T[dim final - dim initial] per public register that is not a main.
  mains           live X (r), live Y (r+112), hosted X2, Y2.  A port with a hosted plane (r in hosted.Dports) has 4
                  mains, otherwise 2.  Mains are never in T: their climbs are paid (MOVEs) and their credit is the
                  caller diagonal.  Ledger law: native mains per port per stage == caller slots covered per stage
                  (= mask rank - idle incidences); check_slots() tests it.
Parametric native (native_param): start from a word or a histogram native and
  drop_mains_A/B  k mains per A/B port per call removed, priced by main_unit:
                  'rank1x8' (8 rank-1 jobs, the ARMS/MONOCALLER/SLOT3 unit), 'rank8' (one rank-8 job), or exact via
                  drop_registers() on a real word (preferred; this is not parametric).
  c_A/c_B         extra owned rank-1 paid jobs per A/B port per call (may be a Fraction).
  dT/dP           helper/paid histogram deltas per call.
Every switch is an explicit argument; nothing reads the environment.
"""
import gzip, json, math
from collections import Counter
from decimal import Decimal, localcontext
from fractions import Fraction as Q

VERSION = 'pricekit/1 (2026-11-11)'
NPORTS = 104

# ------------------------------------------------------------------------------------------- io
def load(path):
    op = gzip.open if str(path).endswith('.gz') else open
    with op(path, 'rt') as f:
        return json.load(f)

def hist(d):
    """dict with str/int keys -> Counter{int: int|Fraction}; zero entries dropped."""
    return Counter({int(k): (Q(v) if isinstance(v, str) else v) for k, v in d.items() if v})

def _add(dst, src, mult=1):
    for r, v in src.items():
        dst[r] += mult * v
    return dst

# ------------------------------------------------------------------------------------------- native
def native_from_word(W, verify=False):
    """Exact native invoice of one word (one call).  verify=True also replays the word exactly (slow)."""
    n = len(W['initial']); live = set(W['live']); H = W.get('hosted') or {}
    X2, Y2 = list(H.get('X2', [])), list(H.get('Y2', []))
    main = live | {r + 112 for r in live} | set(X2) | set(Y2)
    dim = [len(b) for b in W['frames']]
    paid = Counter(); main_paid = Counter(); cls = {}
    for r in live: cls[r] = 'X'; cls[r + 112] = 'Y'
    for r in X2: cls[r] = 'X2'
    for r in Y2: cls[r] = 'Y2'
    by_class = {k: Counter() for k in ('X', 'Y', 'X2', 'Y2')}
    for e in W['program']:
        if e[0] == 'MOVE':
            rk = abs(dim[e[3]] - dim[e[2]]); paid[rk] += 1
            if e[1] in cls: by_class[cls[e[1]]][rk] += 1
    helpers = Counter(dim[W['final'][r]] - dim[W['initial'][r]] for r in range(n) if r not in main)
    dports = set(H.get('Dports', []))
    mains_per_port = {p: 2 + 2 * (p in dports and bool(X2)) for p in range(NPORTS)}
    out = dict(T=+helpers, P=+paid, public=n, events=len(W['program']), mains=len(main), main_moves=by_class,
               mains_per_port=mains_per_port, Dports=sorted(dports), source='word')
    if verify:
        out['replay'] = replay(W)['ok']
    return out

def native_from_hist(paid, helpers, Dports=None, mains_A=4, mains_B=2):
    dp = set(Dports) if Dports is not None else None
    mpp = None if dp is None else {p: (mains_A if p in dp else mains_B) for p in range(NPORTS)}
    return dict(T=hist(helpers), P=hist(paid), mains_per_port=mpp, Dports=sorted(dp) if dp else None, source='hist')

def native_param(base, nA, nB, drop_mains_A=0, drop_mains_B=0, main_unit='rank1x8', c_A=0, c_B=0, dT=None, dP=None,
                 allow_negative=False):
    """Parametric native per call.  base = native dict.  Returns a new native dict (source='param')."""
    T = Counter(base['T']); P = Counter(base['P'])
    unit = {'rank1x8': {1: 8}, 'rank8': {8: 1}}[main_unit]
    for ports, k in ((nA, drop_mains_A), (nB, drop_mains_B)):
        for r, v in unit.items():
            P[r] -= ports * k * v
    P[1] += nA * Q(c_A) + nB * Q(c_B)
    _add(T, dT or {}); _add(P, dP or {})
    mpp = base.get('mains_per_port')
    if mpp is not None:
        dp = set(base['Dports'] or [])
        mpp = {p: m - (drop_mains_A if p in dp else drop_mains_B) for p, m in mpp.items()}
    for r in list(P):   # a negative native count is legal only if the caller absorbs it (invoice() re-checks)
        if P[r] < 0 and not allow_negative: raise ValueError('native_param: negative paid count at rank %d' % r)
    return dict(T=T, P=P, mains_per_port=mpp, Dports=base.get('Dports'), source='param',
                param=dict(drop_mains_A=drop_mains_A, drop_mains_B=drop_mains_B, main_unit=main_unit, c_A=str(c_A), c_B=str(c_B)))

# ------------------------------------------------------------------------------------------- exact word replay / pruning
def _span(b):
    return frozenset(b)

def replay(W):
    """Exact replay (Fractions, sparse rows).  Returns dict(ok, rows, frames, problems)."""
    n = W['public']; N = n + W['owned_fields']; frames = W['frames']
    fs = [set(f) for f in frames]
    rows = [{r: Q(1)} if r < n else {} for r in range(N)]
    cur = list(W['initial']) + [None] * W['owned_fields']; owned = set(); bad = []
    for i, e in enumerate(W['program']):
        op, r = e[0], e[1]
        if op == 'MOVE':
            a, b, priv = e[2:]
            if cur[r] != a: bad.append(('move-from', i));
            cur[r] = b
        elif op == 'INIT':
            owned.add(r); rows[r] = {}; cur[r] = e[2]
        elif op == 'CLEAR':
            owned.discard(r); rows[r] = {}; cur[r] = None
        elif op == 'SCALE':
            q = Q(e[2])
            if cur[r] != e[3]: bad.append(('scale-frame', i))
            rows[r] = {k: v * q for k, v in rows[r].items()}
        elif op in ('ADD', 'COPY'):
            s = e[2]; q = Q(e[3]); f = e[4]
            if cur[r] != f or cur[s] != f: bad.append(('add-frame', i))
            if op == 'COPY' and rows[r]: bad.append(('copy-nonzero', i))
            R = rows[r]
            for k, v in rows[s].items():
                nv = R.get(k, 0) + q * v
                if nv: R[k] = nv
                else: R.pop(k, None)
        else:
            bad.append(('op', i, op))
    if owned: bad.append(('owned-alive', len(owned)))
    if cur[:n] != list(W['final']): bad.append(('exit-frames',))
    return dict(ok=not bad, rows=rows, cur=cur, problems=bad[:20], nproblems=len(bad))

def drop_registers(W, drop):
    """Exact dead-code deletion of the public registers in `drop` (e.g. hosted X2/Y2).
    Keeps every event that some kept public output depends on; removes whole owned lifetimes with no live use.
    Refuses (ValueError) if a dropped register feeds a kept output.  Returns (W2, report)."""
    drop = set(drop); n = W['public']; N = n + W['owned_fields']; PR = W['program']
    need_mask = 0
    dem = [0] * N
    for r in range(n):
        if r not in drop: dem[r] = 1 << r
    keep = [False] * len(PR); feeds_dropped = 0
    for i in range(len(PR) - 1, -1, -1):
        e = PR[i]; op, t = e[0], e[1]
        if op in ('INIT', 'CLEAR'):
            dem[t] = 0; continue
        if op == 'MOVE':
            continue
        if dem[t]:
            keep[i] = True
            if op in ('ADD', 'COPY'):
                s = e[2]
                if s in drop: feeds_dropped += 1
                dem[s] |= dem[t]
                if op == 'COPY': dem[t] = 0
    if feeds_dropped:
        raise ValueError('drop_registers: %d kept events read a dropped register' % feeds_dropped)
    # lifetime decisions for owned registers
    life_keep = {}; open_life = {}
    for i, e in enumerate(PR):
        op, t = e[0], e[1]
        if t >= n:
            if op == 'INIT': open_life[t] = i; life_keep[i] = False
            elif op in ('ADD', 'COPY', 'SCALE') and keep[i]: life_keep[open_life[t]] = True
        if op in ('ADD', 'COPY') and keep[i] and e[2] >= n: life_keep[open_life[e[2]]] = True
    life_of = {}; open_life = {}
    for i, e in enumerate(PR):
        op, t = e[0], e[1]
        if t >= n:
            if op == 'INIT': open_life[t] = i
            life_of[i] = open_life[t]
    out = []; dropped_moves = Counter(); dropped_lifetimes = 0; dim = [len(b) for b in W['frames']]
    for i, e in enumerate(PR):
        op, t = e[0], e[1]
        if t in drop:
            if op == 'MOVE': dropped_moves[abs(dim[e[3]] - dim[e[2]])] += 1
            continue
        if t >= n:
            if not life_keep[life_of[i]]:
                if op == 'MOVE': dropped_moves[abs(dim[e[3]] - dim[e[2]])] += 1
                if op == 'INIT': dropped_lifetimes += 1
                continue
            if op in ('INIT', 'CLEAR', 'MOVE') or keep[i]: out.append(e)
            continue
        if op == 'MOVE' or keep[i]: out.append(e)
    W2 = dict(W); W2['program'] = out
    H = dict(W.get('hosted') or {})
    if drop >= set(H.get('X2', [])) | set(H.get('Y2', [])) and H.get('X2'):
        H['X2'] = []; H['Y2'] = []; H['dropped_hosted_plane'] = True
    W2['hosted'] = H
    rep = dict(events_before=len(PR), events_after=len(out), dropped_moves=dict(dropped_moves),
               dropped_owned_lifetimes=dropped_lifetimes)
    return W2, rep

def zero_registers(W, drop):
    """Hard deletion: registers in `drop` cease to exist (rows = 0).  Every event that targets OR reads them is
    removed, then dead code is pruned with drop_registers().  Only valid if verify_drop() shows every kept public row
    unchanged; otherwise the word genuinely uses the dropped registers and a rebuild is needed."""
    drop = set(drop)
    W1 = dict(W); W1['program'] = [e for e in W['program'] if not (e[1] in drop and e[0] != 'MOVE')
                                   and not (e[0] in ('ADD', 'COPY') and e[2] in drop)]
    removed_reads = sum(1 for e in W['program'] if e[0] in ('ADD', 'COPY') and e[2] in drop and e[1] not in drop)
    W2, rep = drop_registers(W1, drop); rep['removed_reads'] = removed_reads
    return W2, rep

def verify_drop(W, W2, drop):
    """Replay both words exactly; every kept public row and exit frame must be unchanged."""
    a = replay(W); b = replay(W2); n = W['public']
    same = all(a['rows'][r] == b['rows'][r] for r in range(n) if r not in set(drop))
    frames = all(b['cur'][r] == W['final'][r] for r in range(n))
    return dict(original_ok=a['ok'], pruned_ok=b['ok'], pruned_problems=b['problems'], kept_rows_equal=same, exit_frames=frames)

# ------------------------------------------------------------------------------------------- caller
def caller_ports(C):
    return {t: len(v['ports']) for t, v in C['types'].items()}

def caller_invoice(C, lambda_mode='ordinary', only=None):
    """Caller part of the invoice (no native).  only='A'/'B' restricts to one port type.
    Returns dict(T, P, nJ, ports, lambda_uses, ops)."""
    assert lambda_mode in ('ordinary', 'paid_rank1')
    ports = caller_ports(C); T = Counter(); P = Counter(); nJ = 0; lam = 0; ops = Counter()
    for e in C['events']:
        if e[0] == 'J':
            nJ += 1; continue
        ty, op = e[0], e[1]
        if only and ty != only: continue
        k = ports[ty]; ops[(ty, op)] += 1
        if op == 'QUERY': P[1] += k
        elif op == 'IDLE_ONE': P[8 * len(e[3])] += k
        elif op == 'IDLE_ODD': P[8 * len(e[3]) + 1] += k
        elif op == 'LAMBDA':
            lam += k
            if lambda_mode == 'paid_rank1': P[1] += k
        elif op in ('ADD', 'SWAP', 'SCALE', 'HOST'): pass
        else: raise ValueError('caller op not in the alphabet: %r' % (op,))
    for ty, t in C['types'].items():
        if only and ty != only: continue
        for dg in t['diagonal']:
            T[int(dg[0]) % 2 + 8 * sum(dg[2:])] += ports[ty]
    T[0] = 0; T = +T
    return dict(T=T, P=+P, nJ=nJ, ports=ports, lambda_uses=lam, ops=ops)

def check_slots(C, native=None):
    """Per type and stage: mask rank, idle incidences, covered = mask - idles.  With a native, compare covered with
    the native's mains per port (the ledger law d = m)."""
    nst = C['stages']; res = {}
    for ty, t in C['types'].items():
        mask = [0] * (nst + 1); idle = [0] * (nst + 1)
        for dg in t['diagonal']:
            for k, b in enumerate(dg[2:], 1):
                if b: mask[k] += 1
        for e in C['events']:
            if e[0] == ty and e[1] in ('IDLE_ONE', 'IDLE_ODD'):
                for k in e[3]: idle[k] += 1
        cov = [mask[k] - idle[k] for k in range(1, nst + 1)]
        res[ty] = dict(mask=mask[1:], idle=idle[1:], covered=cov, header=sum(mask), idle_incidences=sum(idle))
    if native is not None and native.get('mains_per_port'):
        mpp = native['mains_per_port']
        for ty, t in C['types'].items():
            ms = {mpp[p] for p in t['ports']}
            res[ty]['native_mains'] = sorted(ms)
            res[ty]['law_d_eq_m'] = (len(ms) == 1 and all(c == next(iter(ms)) for c in res[ty]['covered']))
    return res

def caller_from_roots(fields, hosts_per_stage_cap, thin, ports, nst):
    """Parametric caller (rule of our #6934 package, check.py outer()).  fields = list of (mask stages, host stages);
    a field of degree d is a target 8d+1; its unhosted mask stages are idled in maximal consecutive runs (P[8*run]);
    a stage hosting more than hosts_per_stage_cap[k] fields pays one rank-8 idle per excess; thin rank-1 queries."""
    T = Counter(); P = Counter(); hc = Counter()
    for ms, host in fields:
        T[8 * len(ms) + 1] += ports
        hs = set(host)
        for k in hs: hc[k] += 1
        run = 0; prev = None
        for k in sorted(ms):
            if k in hs:
                if run: P[8 * run] += ports
                run = 0; prev = None; continue
            if prev is not None and k == prev + 1: run += 1
            else:
                if run: P[8 * run] += ports
                run = 1
            prev = k
        if run: P[8 * run] += ports
    for k in range(nst):
        if hc[k] > hosts_per_stage_cap[k]: P[8] += ports * (hc[k] - hosts_per_stage_cap[k])
    P[1] += ports * thin
    return dict(T=+T, P=+P)

# ------------------------------------------------------------------------------------------- invoice and price
def invoice(caller, native, calls=None):
    """caller: dict from caller_invoice/caller_from_roots; native: native dict.  calls defaults to caller nJ."""
    L = caller.get('nJ') if calls is None else calls
    if not L: raise ValueError('invoice: number of native calls unknown (no J events and calls=None)')
    T = Counter(caller['T']); P = Counter(caller['P'])
    _add(T, native['T'], L); _add(P, native['P'], L)
    for C_ in (T, P):
        for r in list(C_):
            if C_[r] == 0: del C_[r]
            elif C_[r] < 0: raise ValueError('invoice: negative count at rank %d' % r)
    return dict(T=T, P=P, calls=L)

def S_of(T, P):
    return sum(r * (T.get(r, 0) - P.get(r, 0)) for r in set(T) | set(P))

def _dec(x):
    x = Q(x); return Decimal(x.numerator) / Decimal(x.denominator)

def _coef(T, P):
    return sorted((r, Q(T.get(r, 0)) - Q(P.get(r, 0))) for r in set(T) | set(P) if Q(T.get(r, 0)) != Q(P.get(r, 0)))

def _F(cs, t, prec):
    """F(t) and a rigorous bound on its evaluation error at this precision."""
    with localcontext() as c:
        c.prec = prec; t = Decimal(t)
        val = Decimal(0); mag = Decimal(0)
        for r, k in cs:
            p = (Decimal(r).ln() * (1 - t)).exp(); kd = _dec(k)
            val += kd * p; mag += abs(kd) * p
        err = mag * Decimal(10) ** (-(prec - 6))
    return val, err

def _sign(cs, t, prec=60):
    while prec <= 1200:
        v, e = _F(cs, t, prec)
        if abs(v) > e: return 1 if v > 0 else -1
        prec *= 2
    raise ArithmeticError('sign of F undetermined at t=%s' % t)

def _unique(cs, hi, depth=14):
    """Certify at most one root of F on [0, hi] by interval bounds (F excluded from 0, or F' < 0 on the piece)."""
    with localcontext() as c:
        c.prec = 40
        def pw(r, t): return (Decimal(r).ln() * (1 - Decimal(t))).exp()
        def piece(a, b):
            Fl = sum(_dec(k) * (pw(r, b) if k > 0 else pw(r, a)) for r, k in cs)
            Fh = sum(_dec(k) * (pw(r, a) if k > 0 else pw(r, b)) for r, k in cs)
            if Fl > 0 or Fh < 0: return 'noroot'
            Dl = sum(_dec(k) * Decimal(r).ln() * (pw(r, b) if k > 0 else pw(r, a)) for r, k in cs if r > 1)
            return 'mono' if Dl > 0 else 'unknown'
        stack = [(Decimal(0), Decimal(hi), 0)]; mono = []
        while stack:
            a, b, d = stack.pop(); s = piece(a, b)
            if s == 'noroot': continue
            if s == 'mono': mono.append((a, b)); continue
            if d >= depth: return False
            m = (a + b) / 2; stack += [(a, m, d + 1), (m, b, d + 1)]
        mono.sort()
        return all(mono[i][1] == mono[i + 1][0] for i in range(len(mono) - 1))   # one contiguous decreasing block

def kappa(T, P, digits=50):
    """Certified enclosure of the crossing.  Returns dict(lo, hi, S, status).  status NO_CROSSING if S <= 0."""
    cs = _coef(T, P); S = S_of(T, P)
    if S <= 0: return dict(status='NO_CROSSING', S=S, lo=None, hi=None)
    hi = Decimal('0.001')
    while _sign(cs, hi) > 0:
        hi *= 2
        if hi > 64: return dict(status='NO_SIGN_CHANGE', S=S, lo=None, hi=None)
    lo = Decimal(0); uniq = _unique(cs, hi)
    width = Decimal(10) ** (-digits - 2)
    with localcontext() as c:
        c.prec = digits + 30
        while hi - lo > width:
            m = (lo + hi) / 2
            if _sign(cs, m, digits + 30) > 0: lo = m
            else: hi = m
    return dict(status='OK' if uniq else 'OK_UNIQUENESS_UNPROVED', S=S, lo=lo, hi=hi, unique=uniq)

def Dsum(T, P, t=0, prec=60):
    with localcontext() as c:
        c.prec = prec; t = Decimal(t)
        return sum(_dec(k) * Decimal(r).ln() * (Decimal(r).ln() * (1 - t)).exp() for r, k in _coef(T, P) if r > 1)

def F_at(T, P, t, prec=60):
    return _F(_coef(T, P), t, prec)[0]

def price(inv, digits=50):
    T, P = inv['T'], inv['P']; k = kappa(T, P, digits)
    out = dict(S=S_of(T, P), paid_jobs=sum(P.values()), paid_positions=sum(r * v for r, v in P.items()),
               targets=sum(T.values()), target_positions=sum(r * v for r, v in T.items()), kappa=k,
               D0=Dsum(T, P, 0))
    if k.get('lo') is not None: out['Dk'] = Dsum(T, P, k['lo'])
    return out

def kstr(k, n=30):
    if k.get('lo') is None: return k['status']
    return str(k['lo'])[:n + 2]

def break_even_c(T, P, kappa_ref, ports_calls):
    """Linear break-even: extra rank-1 paid per (port x call) at which kappa == kappa_ref.  F(kref; c) = F0 - c*ports_calls."""
    return F_at(T, P, kappa_ref) / ports_calls

# ------------------------------------------------------------------------------------------- ordinary units (#6934 package reading)
def word_ordinary(W):
    """Per-call ordinary terms of a native word (allowance, reviewed upper, routes): our #6934 jclib.word_terms."""
    H = W['hosted']; nD = len(H['Dports']); n = len(W['initial']); live = set(W['live'])
    main = live | {r + 112 for r in live} | set(H.get('X2', [])) | set(H.get('Y2', []))
    dim = [len(b) for b in W['frames']]
    paid = Counter(abs(dim[e[3]] - dim[e[2]]) for e in W['program'] if e[0] == 'MOVE')
    hel = Counter(dim[W['final'][r]] - dim[W['initial'][r]] for r in range(n) if r not in main)
    life = sum(e[0] == 'INIT' for e in W['program']); allow = upper = 0
    for e in W['program']:
        if e[0] in ('INIT', 'CLEAR'): allow += 2
        elif e[0] == 'SCALE':
            q = Q(e[2]); a, d = abs(q.numerator), q.denominator
            allow += 2 * (abs(a.bit_length() - d.bit_length()) + int(q < 0)); upper += 4 * (a.bit_length() + d.bit_length() + 1)
        elif e[0] in ('ADD', 'COPY'):
            q = Q(e[3]); a, d = abs(q.numerator), q.denominator
            allow += 2 * (3 + a.bit_length() - 1 + bin(a).count('1') + d.bit_length() - 1); upper += 4 * (a.bit_length() + bin(a).count('1') + d.bit_length() + 1)
    routes = (sum(paid.values()) + 2 * sum(hel.values()) + 208 + 2 * nD + 4 * 104 + 4 * nD + 4 * life) * 1000
    return dict(allow=allow, upper=upper, routes=routes, n=n, nD=nD)

def _swaps(sel):
    wanted = set(range(len(sel))); return len(list(zip(sorted(set(sel) - wanted), sorted(wanted - set(sel)))))

def _shim(C, ty):
    t = C['types'][ty]; off = t['offset']; ev = []
    for e in C['events']:
        if e[0] == 'J': ev.append(['HOST', e[1]])
        elif e[0] == ty:
            e = list(e[1:])
            if e[0] in ('ADD', 'SWAP', 'QUERY'): e[1] -= off; e[2] -= off
            else: e[1] -= off
            ev.append(e)
    return dict(events=ev, roles=t['roles'], diagonal=t['diagonal'])

def _rest(C, ports):
    ev = C['events']; roles = C['roles']; mx = mn = mp = 0
    for role, (qp, zero, *sel) in enumerate(C['diagonal']):
        axes = ([0] if qp else []) + [a for st, y in enumerate(sel, 1) if y for a in range(9 + 8 * (st - 1), 9 + 8 * st)]
        k = _swaps(axes); mx += 2 * k * ports; mn += 2 * bool(qp) * ports; mp += int(qp == -1) * ports
    ie = qn = qph = 0
    for e in ev:
        if e[0] in ('IDLE_ONE',):
            ie += 2 * _swaps([a for st in e[2] for a in range(9 + 8 * (st - 1), 9 + 8 * st)]) * ports
        elif e[0] == 'QUERY':
            qn += 2 * ports; qph += int(e[3] == -1) * ports
    return (32 * roles * ports * len(ev) + sum(e[0] == 'QUERY' for e in ev) * 16 * ports + roles * ports * 26
            + (mx + mn + mp) * 1000 + ie * 1000 + (qn + qph) * 1000)

def ordinary(C, W, odd_scale=1125):
    """Raw ordinary readings of the #6934 package (literal/actual/upper/recharge/per_input).  IDLE_ODD is not in that
    formula (#7113-era callers): such callers get a flag, not a number for the IDLE_ODD routes."""
    t = word_ordinary(W); ports = caller_ports(C); L = sum(1 for e in C['events'] if e[0] == 'J')
    rest = _rest(_shim(C, 'A'), ports['A']) + _rest(_shim(C, 'B'), ports['B'])
    lam = sum(ports[e[0]] for e in C['events'] if e[0] != 'J' and e[1] == 'LAMBDA'); debit = 1000 * lam
    sc = 4 * (odd_scale.bit_length() + 2) + 4 * (odd_scale.bit_length() + 2)
    per_in = L * t['n'] * sc
    lit = L * 10 ** 7 + rest; act = L * (t['allow'] + t['routes']) + rest; up = L * (t['upper'] + t['routes']) + rest
    return dict(literal=lit, actual=act, upper=up, recharge=up + debit, per_input=up + per_in, per_input_recharge=up + per_in + debit,
                lambda_uses=lam, lambda_debit=debit, idle_odd_present=any(e[0] != 'J' and e[1] == 'IDLE_ODD' for e in C['events']))

# ------------------------------------------------------------------------------------------- one-call convenience
def run(caller_path, native, lambda_mode='ordinary', digits=50):
    C = load(caller_path); ci = caller_invoice(C, lambda_mode)
    inv = invoice(ci, native); pr = price(inv, digits)
    return dict(caller=ci, invoice=inv, price=pr, slots=check_slots(C, native))

def cite(label, pr):
    """One-line citation string for RESULT.md files."""
    k = pr['kappa']
    return '[PRICEKIT %s] %s: S=%s kappa=%s D0=%.4f Dk=%s paid=%d' % (
        VERSION, label, pr['S'], kstr(k, 26), float(pr['D0']), ('%.8f' % float(pr['Dk'])) if 'Dk' in pr else '-', pr['paid_jobs'])

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print('usage: pricekit.py CALLER.json WORD.json[.gz] | NATIVE-RESULT.json'); sys.exit(1)
    X = load(sys.argv[2])
    nat = native_from_word(X) if 'program' in X else native_from_hist(X['native']['paid'], X['native']['helpers'])
    R = run(sys.argv[1], nat)
    print(cite(sys.argv[2], R['price']))
