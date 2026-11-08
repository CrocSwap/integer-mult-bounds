#!/usr/bin/env python3
"""Physical replay of the literal hosted caller (standard library): every HOST event is a native contact at its stage and port, read through the
retained independent physical audit (retained/physical-review/verify.py) with the one adaptation that HOST is read as the LOCAL contact (stage, source, destination).
python3 -B caller_physical.py data/word.json.gz data/caller.json
Checks: absolute contact phases of the four native boundary maps at every stage and port (7488 contacts), fresh D_stage diagonal and Q^-1 forward cross coefficient,
the reverse cross coefficient D_stage Q^+1 that the hosted native adds, main-target exponents and translations, whole-idle rank and axis disjointness on every owner and port,
the field map (injective, fresh helpers, owned/query scratch disjoint) with the aliased-helper control, the complete invoice from the caller, and the canonical adapter inventory."""
import copy, gzip, importlib.util, json, sys
from collections import Counter
HERE = __import__('os').path.dirname(__import__('os').path.abspath(__file__))
spec = importlib.util.spec_from_file_location('review', HERE + '/retained/physical-review/verify.py'); P = importlib.util.module_from_spec(spec); spec.loader.exec_module(P)
W = json.load(gzip.open(sys.argv[1], 'rt')); C = json.load(open(sys.argv[2]))
recipes = json.load(open(HERE + '/retained/runtime/DATA-PHASES.json'))
def need(ok, msg):
    if not ok: raise SystemExit('FAIL ' + msg)
    print('PASS', msg, flush=True)
shim = copy.deepcopy(C); shim['events'] = [['LOCAL', e[1], e[2], e[3]] if e[0] == 'HOST' else e for e in shim['events']]
need(sum(e[0] == 'LOCAL' for e in shim['events']) == 18, 'the caller has 18 hosted native contacts (HOST read as LOCAL)')
ph = P.physical(shim, W, recipes)
need(ph['contacts'] == 4 * 18 * 104, 'absolute phase of all %d native boundary contacts (4 per stage and port), fresh D_stage diagonal and D_stage Q^-1 cross term' % ph['contacts'])
need(sum(ph['main'].values()) == C['roles'] * 104 and sum(ph['idle'].values()) == sum(e[0] == 'IDLE_ONE' for e in C['events']) * 104, 'main targets on all %d roles and ports; every IDLE_ONE owner has a whole idle (%s) with disjoint fresh axes' % (C['roles'], dict(sorted(ph['idle'].items()))))
# reverse cross coefficient of the hosted native (X_out over Y_in = D_stage Q^+1), with the control Q^-1
dim = C['ambient_rank']; axes = [1 << i for i in range(dim)]; bad = ctl = cnt = 0
for e in C['events']:
    if e[0] != 'HOST': continue
    st = e[1]
    for q in W['ports']:
        x0 = P.terms((a, 1) for a in axes[:9 + 8 * (st - 1)]); y0 = P.terms(list(x0.items()) + [(q, -1)])
        x1 = P.terms((a, 1) for a in axes[:9 + 8 * st]); body = P.terms((a, 1) for a in axes[9 + 8 * (st - 1):9 + 8 * st])
        rev = P.difference(x1, y0)
        bad += P.translation_for(P.difference(rev, P.terms(list(body.items()) + [(q, 1)]))) != 0
        ctl += P.translation_for(P.difference(rev, P.terms(list(body.items()) + [(q, -1)]))) == 0
        cnt += 1
need(bad == 0 and ctl == 0, 'reverse cross coefficient D_stage Q^+1 at %d stage-port pairs (control Q^-1 matches %d)' % (cnt, ctl))
led = P.native_ledger(W, check_rows=False)
need(led['helpers'] == Counter({1: 13, 2: 8, 3: 3, 4: 184, 5: 23, 6: 3, 7: 14, 8: 68, 9: 879}) and led['public'] == 1403, 'native ledger of the hosted word: 1195 helpers, 1403 public (endpoint rows checked separately in check.py)')
fld = P.allocation(shim, W, led)
need(fld['invocations'] == 18 and fld['productive_fields'] == C['roles'] * 104 + 18 * 1195 and fld['main_fields'] == C['roles'] * 104, 'field map: %d productive fields, every native helper a distinct fresh field per call, injective public allocation, owned and query scratch disjoint' % fld['productive_fields'])
try: P.allocation(shim, W, led, alias=True); al = False
except ValueError: al = True
need(al, 'control: aliasing helpers across calls is rejected')
bill = P.invoice(shim, led, ph, fld)
inv = json.load(open(HERE + '/data/invoice_check.json'))
need(dict(bill['targets']) == {int(k): v for k, v in inv['T'].items()} and dict(bill['paid']) == {int(k): v for k, v in inv['P'].items()}, 'complete invoice from the physical audit equals the check.py invoice (targets and paid)')
rec = P.adapter_inventory(shim, W, recipes); ad = P.check_adapter_inventory(rec, shim, ph)
print('  adapter inventory', {k: v for k, v in ad.items() if k != 'payload_sha256'})
need(ad['main_jobs'] == C['roles'] * 104 and ad['idle_jobs'] == sum(ph['idle'].values()), 'adapters for every main job and every whole idle job, distinct')
# controls: a swapped native chronology and a deleted idle are rejected
def rejected(f):
    try: f(); return False
    except (ValueError, SystemExit): return True
sw = copy.deepcopy(shim); idx = [i for i, e in enumerate(sw['events']) if e[0] == 'LOCAL']; sw['events'][idx[0]][1], sw['events'][idx[1]][1] = 2, 1
need(rejected(lambda: P.physical(sw, W, recipes)), 'control: native stages out of chronological order are rejected')
de = copy.deepcopy(shim); del de['events'][next(i for i, e in enumerate(de['events']) if e[0] == 'IDLE_ONE')]
need(P.invoice(de, led, P.physical(de, W, recipes), fld)['paid'] != bill['paid'], 'control: deleting one idle job changes the invoice (so the idle layout is bound to the bill)')
print('PASS_CALLER_PHYSICAL')
