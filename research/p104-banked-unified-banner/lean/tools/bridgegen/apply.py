# BANKFIT apply.py (own transliteration, data-only): BASE-GRAPH + EDITS -> final graph (no verification of their pulses).
import gzip, json, sys, signal
from fractions import Fraction as Fr
from hashlib import sha256
signal.alarm(1100)
def A(row, don, f):
    for i, v in don.items():
        n = row.get(i, 0) + f * v
        if n: row[i] = n
        else: row.pop(i, None)
def co(es):
    r = {k: Fr(v) for k, v in es}; assert len(r) == len(es) and all(r.values()); return r
class N:
    def __init__(s, fo, ini, fin, mv, fm): s.fo, s.ini, s.fin, s.mv, s.fm = fo, ini, fin, mv, fm
    def tr(s):
        def rev(x):
            if x < 0: return s.fo + ~x
            if x >= s.fo: return ~(x - s.fo)
            return x
        e = {k: {} for k in s.mv}; e.update({s.fo + r: {} for r in range(len(s.ini))})
        for node, form in s.fm.items():
            for d, c in form.items(): e[rev(d)][rev(node)] = c
        return N(s.fo, s.fin, s.ini, {k: (b, a) for k, (a, b) in s.mv.items()}, e)
def dot(l, r): return sum(l[k] * r[k] for k in l.keys() & r.keys())
def check_bank(n, w, ch):
    for d in w:
        if d < 0: assert ~d < len(n.ini) and n.ini[~d] == ch
        else: assert d in n.mv and n.mv[d][1] == ch
def subst(row, key, rep):
    if key not in row: return row
    r = row.copy(); A(r, rep, r.pop(key)); return r
def inpar(n, key, w):
    assert w[key] == 1 and all(n.mv[j] == n.mv[key] for j in w)
    oth = {j: v for j, v in w.items() if j != key}; rows = {}
    for j, row in n.fm.items():
        c = dot(row, oth)
        if c: row = row.copy(); A(row, {key: c}, 1)
        rows[j] = row
    pv = rows[key]
    for j, f in oth.items(): rows[j] = rows[j].copy(); A(rows[j], pv, -f)
    return N(n.fo, n.ini, n.fin, n.mv, rows)
def puncture(n, ev):
    first, key, role = n.fo, ev['remove'], ev['role']
    sender, receiver = n.mv[key]; dest = ev['return_chart']
    source, response, cal, ro = (co(ev[k]) for k in ('old_source_form', 'old_terminal_response', 'calibration', 'new_readout'))
    gain = Fr(ev['response'])
    assert gain and source.get(role) and all(n.ini[j] == n.ini[role] for j in source)
    check_bank(n, cal, receiver); check_bank(n, ro, dest)
    rep = {r: (co(row), Fr(sc)) for r, row, sc in ev['repairs']}
    assert rep.keys() >= response.keys() - {role}
    for r, (row, sc) in rep.items(): check_bank(n, row, n.fin[r])
    oi = {~r: -v / source[role] for r, v in source.items() if r != role}
    pk = {~role: Fr(1)}; A(pk, subst(cal, ~role, oi), -1 / gain)
    nr = lambda row: subst(subst(row, ~role, oi), key, pk)
    mv = n.mv.copy(); del mv[key]
    rows = {j: nr(row) for j, row in n.fm.items() if j != key}
    for r, v in response.items():
        if r != role:
            row, sc = rep[r]; rows[first + r] = rows[first + r].copy(); A(rows[first + r], nr(row), -v / sc)
    rows[first + role] = {j: v / gain for j, v in nr(ro).items()}
    ini, fin = n.ini.copy(), n.fin.copy(); ini[role], fin[role] = receiver, dest
    return N(first, ini, fin, mv, rows)
def pivot(n, ed):
    drop, lead = ed['remove'], ed['pivot']
    comb = co(ed['combination']); sender = co(ed['sender']); side = co(ed['receiver'])
    assert lead in comb and drop in n.mv and lead in n.mv
    _, mid = n.mv[drop]; old, dest = n.mv[lead]
    uses = {m: r[drop] for m, r in n.fm.items() if drop in r}
    assert old == mid and comb.keys() <= uses.keys()
    assert all(n.mv.get(m) == (mid, dest) for m in uses)
    agg = {}
    for m, w in comb.items(): A(agg, n.fm[m], w)
    resp = agg.get(drop, 0); assert resp
    forms = n.fm.copy(); del forms[drop]; forms[lead] = sender
    for m, w in uses.items():
        if m != lead:
            res = n.fm[m].copy(); A(res, agg, -Fr(w) / resp); assert drop not in res; forms[m] = res
    cb = {lead: Fr(1)}; A(cb, side, -1); rec = {}
    for m, w in uses.items():
        if m == lead: row = {k: -v / comb[lead] for k, v in comb.items() if k != lead}
        else: row = {m: Fr(1)}
        A(row, cb, Fr(w) / resp); rec[m] = row
    for k, row in list(forms.items()):
        aff = row.keys() & rec.keys()
        if aff:
            new = {i: v for i, v in row.items() if i not in aff}
            for i in aff: A(new, rec[i], row[i])
            forms[k] = new
    mv = n.mv.copy(); del mv[drop]; mv[lead] = (ed['source_chart'], dest)
    return N(n.fo, n.ini, n.fin, mv, forms)
def relay(n, ed):
    key, lead = ed['remove'], ed['pivot']
    comb = co(ed['combination']); side = co(ed['receiver']); sender = co(ed['sender'])
    mid = n.mv[key][1]; old, dest = n.mv[lead]
    assert old == mid and all(n.mv.get(j) == (mid, dest) for j in comb)
    check_bank(n, sender, ed['source_chart']); check_bank(n, side, dest)
    return pivot(n, ed)
def repl_many(row, rp):
    used = row.keys() & rp.keys()
    if not used: return row
    r = {i: v for i, v in row.items() if i not in used}
    for i in used: A(r, rp[i], row[i])
    return r
def grouped(n, ev, mains):
    first = n.fo; lanes = ev['lanes']; roles, pivots = set(), set()
    gauges, sources, packets, readouts = {}, {}, {}, {}
    trep = {r: co(row) for r, row in ev['repairs']}
    ini, fin = n.ini.copy(), n.fin.copy()
    for ln in lanes:
        k, r, gain = ln['remove'], ln['role'], Fr(ln['response'])
        sender, receiver = n.mv[k]
        assert gain and 0 <= r < len(ini) and r not in roles | mains and k not in pivots and ini[r] == sender and ini[r] != fin[r]
        d = co(ln['receive_direction'])
        assert d.get(k) == 1 and all(n.mv[j] == (sender, receiver) for j in d) and d.keys().isdisjoint(gauges)
        gauges.update({j: (k, v) for j, v in d.items()})
        rp = co(ln['old_input']); assert all(j < 0 for j in rp); check_bank(n, rp, sender)
        cal, ret = co(ln['calibration']), co(ln['new_readout'])
        check_bank(n, cal, receiver); check_bank(n, ret, fin[r])
        sources[~r] = rp; packets[k] = (r, gain, cal); readouts[first + r] = ret
        ini[r] = receiver; roles.add(r); pivots.add(k)
    assert all(row.keys().isdisjoint(sources) for row in sources.values())
    assert trep.keys().isdisjoint(roles)
    for r, row in trep.items(): check_bank(n, row, fin[r])
    def gauge(row):
        res = row.copy()
        for j in row.keys() & gauges.keys():
            k, v = gauges[j]
            if k != j: A(res, {k: row[j]}, v)
        return res
    rows = {j: gauge(row) for j, row in n.fm.items()}
    for j, (k, f) in gauges.items():
        if j != k: A(rows[j], rows[k], -f)
    inj = {}
    for k, (r, gain, cal) in packets.items():
        pk = {~r: 1 / gain}; A(pk, repl_many(gauge(cal), sources), -1 / gain)
        assert pk.keys().isdisjoint(pivots); inj[k] = pk
    adj = lambda row: repl_many(repl_many(row, sources), inj)
    rows = {j: adj(row) for j, row in rows.items() if j not in pivots}
    for r, row in trep.items():
        rows[first + r] = rows[first + r].copy(); A(rows[first + r], adj(gauge(row)), -1)
    rows.update({j: adj(gauge(row)) for j, row in readouts.items()})
    return N(first, ini, fin, {k: ab for k, ab in n.mv.items() if k not in pivots}, rows)
def psplit(n, ev):
    first, role = n.fo, ev['r']
    a, b, c, sender, z = (ev[j] for j in ('A', 'B', 'D', 'E', 'Z'))
    assert (n.ini[role], n.fin[role]) == (a, z)
    sent, local, src, dr, cal, dec, resp, inj = (co(ev[j]) for j in ('send', 'received', 's', 'w', 'cal', 'y', 't', 'inj'))
    check_bank(n, sent, sender); check_bank(n, local, b); check_bank(n, cal, c)
    assert all(n.ini[i] == a for i in src.keys() | dr.keys())
    assert all(n.fin[i] == z for i in dec.keys() | resp.keys())
    for k in inj: assert (n.mv[k][0] if k in n.mv else n.fin[k - first]) == c
    key = next(k for k in range(first) if k not in n.mv)
    mv, rows = dict(n.mv), dict(n.fm); mv[key], rows[key] = (sender, b), sent
    obs = dict(local); obs[key] = Fr(1)
    ss, rs = dot(src, dr), dot(dec, resp); assert ss and rs and resp.get(role)
    steer = {~r: -v / ss for r, v in src.items() if r != role}; steer[~role] = 1 / ss
    def rescale(row):
        f = sum(row.get(~r, 0) * v for r, v in dr.items())
        if not f and ~role not in row: return row
        res = row.copy(); res.pop(~role, None); A(res, steer, f); return res
    rows = {j: rescale(row) for j, row in rows.items()}
    fresh = len(n.ini); amp = {~fresh: 1 / rs}; A(amp, rescale(cal), -1 / rs)
    for j, v in inj.items(): rows[j] = rows[j].copy(); A(rows[j], amp, v)
    ret = {}
    for r, v in dec.items(): A(ret, rows[first + r], v)
    pv = rows[first + role]
    for r, v in resp.items():
        if r != role: rows[first + r] = rows[first + r].copy(); A(rows[first + r], pv, -v / resp[role])
    rows[first + role], rows[first + fresh] = rescale(obs), ret
    fin = n.fin + [z]; fin[role] = b
    return N(first, n.ini + [c], fin, mv, rows)
def sched_ok(n):
    for node, form in n.fm.items():
        ch = n.mv[node][0] if node < n.fo else n.fin[node - n.fo]
        for d in form:
            dc = n.ini[~d] if d < 0 else n.mv[d][1]
            assert dc == ch, 'nonlocal'
def build(gp, ip, ep):
    g = json.loads(gzip.decompress(open(gp, 'rb').read())); lay = json.load(open(ip)); j = json.load(open(ep))
    mv = {k: (a, b) for k, a, b in g['moves']}; rows = {k: co(r) for k, r in g['forms']}
    n = N(g['first_output'], g['initial'], g['final'], mv, rows)
    h = lay['hosted']; mains = set(lay['live']) | {i + 112 for i in lay['live']} | set(h['X2']) | set(h['Y2'])
    evs = j['events'] if isinstance(j, dict) else j
    for ev in evs:
        sp = ev['type'] == 'paid_side_split'; rev = ev['d'] if sp else ev['orientation']
        o = n.tr() if rev else n
        if ev['type'] in ('parallel_bank_puncture', 'parallel_relay'): o = inpar(o, ev['remove'], co(ev['receive_direction']))
        if ev['type'] == 'parallel_relay': out = relay(o, ev)
        elif ev['type'] == 'grouped_puncture': out = grouped(o, ev, mains)
        elif sp: out = psplit(o, ev)
        else: out = puncture(o, ev)
        sched_ok(out)
        n = out.tr() if rev else out
    ser = dict(frames=g['frames'], initial=n.ini, final=n.fin, first_output=n.fo,
               moves=[[k, *v] for k, v in sorted(n.mv.items())],
               forms=[[k, [[i, str(v)] for i, v in sorted(r.items())]] for k, r in sorted(n.fm.items())])
    return ser, n
if __name__ == '__main__':
    ser, n = build(sys.argv[1], sys.argv[2], sys.argv[3])
    print('public', len(n.ini), 'moves', len(n.mv), 'forms', len(n.fm))
    # schedule via Kahn
    from graphlib import TopologicalSorter
    sch = list(TopologicalSorter({k: sorted(i for i in r if i >= 0) for k, r in sorted(n.fm.items())}).static_order())
    ser['schedule'] = sch
    enc = json.dumps(ser, sort_keys=True, separators=(',', ':')).encode()
    print('sha256', sha256(enc).hexdigest())
    json.dump(ser, gzip.open(sys.argv[4], 'wt'))
