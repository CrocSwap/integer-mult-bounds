"""Relaxation: price deleting single B gates (ignoring exactness) with exact optimal frames, base cone caps."""
import sys, json, gzip, time, signal
import _paths
import harness as H, frames as F
from word import inline
word, out = sys.argv[1], sys.argv[2]
idxs = [int(x) for x in sys.argv[3].split(',')]
P = H.Pricer(word)
res = {}
for i in idxs:
    t0 = time.time()
    w1 = H.compile_edits(P.base, dict(delete=[i]))
    try:
        signal.signal(signal.SIGALRM, H._alarm); signal.alarm(120)
        g = F.Graph(inline(w1, True), check_literal=False, tail_mutable=True, caps=P.caps, cut_equality=True)
        r = F.optimal_frames(inline(w1, True), P.costs, check_literal=False, graph=g)
        res[i] = dict(delta=r['cost'] - P.base_cost, prof=dict(sorted(r['profile'].items())), cert=r['certified'])
    except F.Infeasible as e: res[i] = dict(status='infeasible')
    except H.Timeout: res[i] = dict(status='timeout')
    except Exception as e: res[i] = dict(status='err:' + repr(e)[:80])
    finally: signal.alarm(0)
    print(i, P.base['B'][i][:5], res[i], '%.1fs' % (time.time() - t0), flush=True)
    json.dump(res, open(out, 'w'))
