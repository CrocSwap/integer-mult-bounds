"""Relaxation: delete single A-section gates (ignoring exactness), exact optimal frames with base caps."""
import sys, json, time, signal
import _paths
import harness as H, frames as F
from word import inline
word, out = sys.argv[1], sys.argv[2]
idxs = [int(x) for x in open(sys.argv[3]).read().split(',')]
P = H.Pricer(word)
res = {}
for i in idxs:
    t0 = time.time()
    w1 = dict(P.base); w1['A'] = [g for j, g in enumerate(P.base['A']) if j != i]
    try:
        signal.signal(signal.SIGALRM, H._alarm); signal.alarm(120)
        g = F.Graph(inline(w1, True), check_literal=False, tail_mutable=True, caps=P.caps, cut_equality=True)
        r = F.optimal_frames(inline(w1, True), P.costs, check_literal=False, graph=g)
        res[i] = dict(delta=r['cost'] - P.base_cost, prof=dict(sorted(r['profile'].items())))
    except F.Infeasible as e: res[i] = dict(status='infeasible')
    except H.Timeout: res[i] = dict(status='timeout')
    except Exception as e: res[i] = dict(status='err:' + repr(e)[:80])
    finally: signal.alarm(0)
    print(i, P.base['A'][i][:5], res[i], '%.1fs' % (time.time() - t0), flush=True)
    json.dump(res, open(out, 'w'))
