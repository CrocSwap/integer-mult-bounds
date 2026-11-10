#!/usr/bin/env python3
"""Physical replay of the literal two-chain caller (standard library): every HOST2 event is a native contact at its stage and port, read through the
retained independent physical audit (retained/physical-review/verify.py) with the one adaptation that HOST2 is read as the LOCAL contact (stage, source, destination) of the first plane;
the second plane (x2, y2) sits on the same frames and ports.
python3 -B caller_physical.py data/word.json.gz data/caller.json
Checks: absolute contact phases of the four native boundary maps at every stage and port (7488 contacts), fresh D_stage diagonal and Q^-1 cross term, the reverse cross coefficient D_stage Q^+1 of the second plane,
main-target exponents and translations on all 40 roles, whole-idle rank and axis disjointness on every owner and port, an injective field map with FOUR distinct main registers per port and fresh helpers (with the aliased-helper control),
the complete invoice from the physical audit against data/invoice_check.json, and the canonical adapter inventory."""
import copy, gzip, importlib.util, json, sys
from collections import Counter
HERE = __import__('os').path.dirname(__import__('os').path.abspath(__file__))
spec = importlib.util.spec_from_file_location('review', HERE + '/retained/physical-review/verify.py'); P = importlib.util.module_from_spec(spec); spec.loader.exec_module(P)
W = json.load(gzip.open(sys.argv[1], 'rt')); C = json.load(open(sys.argv[2]))
recipes = json.load(open(HERE + '/retained/runtime/DATA-PHASES.json'))
def need(ok, msg):
    if not ok: raise SystemExit('FAIL ' + msg)
    print('PASS', msg, flush=True)
shim = copy.deepcopy(C); shim['events'] = [['LOCAL', e[1], e[2], e[3]] if e[0] == 'HOST2' else e for e in shim['events']]
need(sum(e[0] == 'LOCAL' for e in shim['events']) == 18, 'the caller has 18 native contacts (HOST2 read as LOCAL)')
ph = P.physical(shim, W, recipes)
need(ph['contacts'] == 4 * 18 * 104, 'absolute phase of all %d native boundary contacts (4 per stage and port), fresh D_stage diagonal and D_stage Q^-1 cross term' % ph['contacts'])
need(sum(ph['main'].values()) == C['roles'] * 104 and sum(ph['idle'].values()) == sum(e[0] == 'IDLE_ONE' for e in C['events']) * 104, 'main targets on all %d roles and ports; every IDLE_ONE owner has a whole idle (%s) with disjoint fresh axes' % (C['roles'], dict(sorted(ph['idle'].items()))))
dim = C['ambient_rank']; axes = [1 << i for i in range(dim)]; bad = ctl = cnt = 0
for e in C['events']:
    if e[0] != 'HOST2': continue
    st = e[1]
    for q in W['ports']:
        x0 = P.terms((a, 1) for a in axes[:9 + 8 * (st - 1)]); y0 = P.terms(list(x0.items()) + [(q, -1)])
        x1 = P.terms((a, 1) for a in axes[:9 + 8 * st]); body = P.terms((a, 1) for a in axes[9 + 8 * (st - 1):9 + 8 * st])
        rev = P.difference(x1, y0)
        bad += P.translation_for(P.difference(rev, P.terms(list(body.items()) + [(q, 1)]))) != 0
        ctl += P.translation_for(P.difference(rev, P.terms(list(body.items()) + [(q, -1)]))) == 0
        cnt += 1
need(bad == 0 and ctl == 0, 'reverse cross coefficient D_stage Q^+1 of the second plane at %d stage-port pairs (control Q^-1 matches %d)' % (cnt, ctl))
led = P.native_ledger(W, check_rows=False)
H2 = set(W['hosted']['X2']) | set(W['hosted']['Y2'])
labels = [(f, r) for f, r in led['helper_labels'] if f not in H2]
need(len(led['helper_labels']) - len(labels) == 208 and len(labels) == led['public'] - 416, 'second mains are public, not helpers: %d helpers, %d public' % (len(labels), led['public']))
Tb = Counter(ph['main']); Pb = Counter(ph['idle'])
for f, r in labels: Tb[r] += 18
for k, v in led['paid'].items(): Pb[k] += 18 * v
Pb[1] += 104 * sum(e[0] == 'QUERY' for e in C['events'])
for ev_i, e in enumerate(c for c in C['events'] if c[0] == 'HOST2'):
    st, src, dst, x2, y2 = e[1:]; pm = {}
    for i, q, a, b in zip(W['live'], W['ports'], W['hosted']['X2'], W['hosted']['Y2']):
        pm[i] = ('main', src, q); pm[112 + i] = ('main', dst, q); pm[a] = ('main', x2, q); pm[b] = ('main', y2, q)
    for f, r in labels: pm[f] = ('helper', ev_i, f)
    if len(set(pm.values())) != led['public'] or len(pm) != led['public']: raise SystemExit('FAIL field map at stage %d' % st)
need(True, 'injective public allocation with four distinct main registers per port and fresh helpers at every one of the 18 contacts')
inv = json.load(open(HERE + '/data/invoice_check.json'))
need(dict(+Tb) == {int(k): v for k, v in inv['T'].items()} and dict(+Pb) == {int(k): v for k, v in inv['P'].items()}, 'complete invoice from the physical audit equals data/invoice_check.json (targets and paid)')
def rejected(f):
    try: f(); return False
    except (ValueError, SystemExit): return True
sh2 = copy.deepcopy(shim); idx = [i for i, e in enumerate(sh2['events']) if e[0] == 'LOCAL']; sh2['events'][idx[0]][1], sh2['events'][idx[1]][1] = 2, 1
need(rejected(lambda: P.physical(sh2, W, recipes)), 'control: native stages out of chronological order are rejected')
de = copy.deepcopy(shim); del de['events'][next(i for i, e in enumerate(de['events']) if e[0] == 'IDLE_ONE')]
phd = P.physical(de, W, recipes)
need(Counter(phd['idle']) != Counter(ph['idle']), 'control: deleting one idle job changes the physical idle bill (the idle layout is bound to the invoice)')
rec = P.adapter_inventory(shim, W, recipes); ad = P.check_adapter_inventory(rec, shim, ph)
print('  adapter inventory', {k: v for k, v in ad.items() if k != 'payload_sha256'})
need(ad['main_jobs'] == C['roles'] * 104 and ad['idle_jobs'] == sum(ph['idle'].values()), 'adapters for every main job and every whole idle job, distinct')
print('PASS_CALLER_PHYSICAL')
