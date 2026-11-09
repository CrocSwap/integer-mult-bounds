#!/usr/bin/env python3
"""Physical replay of the JOINT caller: the single joint stream is split mechanically by type tag (A: 96 ports, B: 8 ports); each type is read through the retained
independent physical audit (HOST2/HOST = the LOCAL contact) with native['ports'] restricted to that type's ports.  Totals must cover all 104 ports exactly once.
python3 -B caller_physical.py data/caller.json data/word.json.gz"""
import copy, gzip, importlib.util, json, sys
from collections import Counter
HERE = __import__('os').path.dirname(__import__('os').path.abspath(__file__))
spec = importlib.util.spec_from_file_location('review', HERE + '/retained/physical-review/verify.py'); P = importlib.util.module_from_spec(spec); spec.loader.exec_module(P)
J = json.load(open(sys.argv[1])); W = json.load(gzip.open(sys.argv[2], 'rt')); recipes = json.load(open(HERE + '/retained/runtime/DATA-PHASES.json'))
def need(ok, msg):
    if not ok: raise SystemExit('FAIL ' + msg)
    print('PASS', msg, flush=True)
def shim_of(ty):
    t = J['types'][ty]; off = t['offset']; ev = []
    for e in J['events']:
        if e[0] == 'J': ev.append(['LOCAL', e[1], (e[2] if ty == 'A' else e[3])[0] - off, (e[2] if ty == 'A' else e[3])[1] - off])
        elif e[0] == ty:
            e = list(e[1:])
            if e[0] in ('ADD', 'SWAP', 'QUERY'): e[1] -= off; e[2] -= off
            else: e[1] -= off
            ev.append(e)
    return dict(roles=t['roles'], stages=J['stages'], ambient_rank=J['ambient_rank'], events=ev, diagonal=t['diagonal'])
tot_contacts = tot_main = 0; ports_seen = []; idle_tot = Counter(); idle_exp = Counter()
for ty in 'AB':
    ports = J['types'][ty]['ports']; ports_seen += ports; sh = shim_of(ty)
    nat = dict(W); nat['ports'] = [W['ports'][i] for i in ports]
    ph = P.physical(sh, nat, recipes)
    need(ph['contacts'] == 4 * 18 * len(ports), 'type %s: absolute phase of all %d native boundary contacts (4 per stage and port, %d ports), fresh D_stage diagonal and D_stage Q^-1 cross term' % (ty, ph['contacts'], len(ports)))
    need(sum(ph['main'].values()) == sh['roles'] * len(ports), 'type %s: main targets on all %d roles x %d ports' % (ty, sh['roles'], len(ports)))
    ni = Counter(8 * len(e[2]) for e in sh['events'] if e[0] == 'IDLE_ONE')
    need(Counter({k: v * len(ports) for k, v in ni.items()}) == Counter(ph['idle']), 'type %s: every IDLE_ONE owner has a whole idle on disjoint fresh axes at every port (%s)' % (ty, dict(sorted(ph['idle'].items()))))
    dim = sh['ambient_rank']; axes = [1 << i for i in range(dim)]; bad = ctl = cnt = 0
    for e in sh['events']:
        if e[0] != 'LOCAL': continue
        st = e[1]
        for q in nat['ports']:
            x0 = P.terms((a, 1) for a in axes[:9 + 8 * (st - 1)]); y0 = P.terms(list(x0.items()) + [(q, -1)])
            x1 = P.terms((a, 1) for a in axes[:9 + 8 * st]); body = P.terms((a, 1) for a in axes[9 + 8 * (st - 1):9 + 8 * st])
            rev = P.difference(x1, y0)
            bad += P.translation_for(P.difference(rev, P.terms(list(body.items()) + [(q, 1)]))) != 0
            ctl += P.translation_for(P.difference(rev, P.terms(list(body.items()) + [(q, -1)]))) == 0; cnt += 1
    need(bad == 0 and ctl == 0, 'type %s: reverse cross coefficient D_stage Q^+1 at %d stage-port pairs (control Q^-1 matches %d)' % (ty, cnt, ctl))
    sh2 = copy.deepcopy(sh); idx = [i for i, e in enumerate(sh2['events']) if e[0] == 'LOCAL']; sh2['events'][idx[0]][1], sh2['events'][idx[1]][1] = 2, 1
    try: P.physical(sh2, nat, recipes); r = False
    except (ValueError, SystemExit): r = True
    need(r, 'type %s: control, native stages out of order rejected' % ty)
    tot_contacts += ph['contacts']; tot_main += sum(ph['main'].values())
need(sorted(ports_seen) == list(range(104)) and tot_contacts == 4 * 18 * 104, 'the two types cover all 104 ports exactly once: %d contacts, %d main targets (96*40 + 8*38 = %d)' % (tot_contacts, tot_main, 96 * 40 + 8 * 38))
need(tot_main == 96 * 40 + 8 * 38, 'main target total')
# field map: one injective public allocation per contact
n = len(W['initial']); live = W['live']; X2 = W['hosted']['X2']; Y2 = W['hosted']['Y2']; Aports = J['types']['A']['ports']; Bports = J['types']['B']['ports']
mains = set(live) | {r + 112 for r in live} | set(X2) | set(Y2)
for e in J['events']:
    if e[0] != 'J': continue
    pm = {}
    for i, a, b in zip(sorted(Aports), X2, Y2): pass
    xy = dict(zip(Aports, zip(X2, Y2)))   # X2/Y2 listed in Dports order (as the word declares)
    for i in Aports:
        r = live[i]; pm[r] = ('A', e[2][0], i); pm[r + 112] = ('A', e[2][1], i); pm[xy[i][0]] = ('A', e[2][2], i); pm[xy[i][1]] = ('A', e[2][3], i)
    for i in Bports:
        r = live[i]; pm[r] = ('B', e[3][0], i); pm[r + 112] = ('B', e[3][1], i)
    for f in range(n):
        if f not in mains: pm[f] = ('helper', f)
    assert len(pm) == n and len(set(pm.values())) == n, 'allocation not injective at stage %d' % e[1]
need(n == W['public'] == len(W['final']) and len(mains) == 4 * len(Aports) + 2 * len(Bports) and len(mains) + sum(1 for f in range(n) if f not in mains) == n, 'field map: at every one of the 18 contacts, the %d public registers of the word (counted from the word, equal to its declared public count) map injectively: %d mains (A ports 4, B ports 2) and %d helpers' % (n, len(mains), n - len(mains)))
print('PASS_CALLER_PHYSICAL_JOINT')
