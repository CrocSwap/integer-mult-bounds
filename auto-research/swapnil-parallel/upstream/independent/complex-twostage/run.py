"""Round-six complex saving: two-stage complex network, NStar3 producer with retained totals, copied retained
centres, full batching. Prints the circuit size, the frame/label check (0 bad), the histogram sum check (== s),
the largest child (crude guard needs <= m - 1) and the certified a_c; writes the histogram to hist_<h>.json.
Usage: python3 run.py 24"""
import sys, json, time
from hist import build
from frames import Checker
from cert import cert

if __name__ == '__main__':
    for h in map(int, sys.argv[1:]):
        t0 = time.time()
        d = build(h, copied=True); c = d.pop('c')
        print(dict(h=h, v=d['v'], m=d['m'], R=d['R'], W=d['W'], s=d['s'], hist_sum=d['sum'], sum_ok=d['sum_ok'],
                   maxrank=d['maxrank'], guard_ok=d['maxrank'] <= d['m'] - 1), flush=True)
        ch = Checker(c); dims = {n: len(ch.label(n)) for n in c.active}
        from hist import label_dims
        assert dims == label_dims(c), 'histogram label dims differ from the explicit labels'
        print('labels', ch.run(), flush=True)
        a, gap = cert(d['hist'], d['W'], d['m'])
        print(dict(a_c=str(a), a_c_float=float(a), moment_gap=float(gap), secs=round(time.time() - t0)), flush=True)
        json.dump(dict(h=h, m=d['m'], W=d['W'], s=d['s'], hist={str(k): n for k, n in d['hist'].items()}),
                  open(f'hist_{h}.json', 'w'))
