# Which public classes does each owned lifetime feed, and what does it pay?  (#7617)
import sys, resource
sys.path.insert(0, '../../PRICEKIT')
import pricekit as pk
from collections import Counter, defaultdict
W = pk.load('../../ATTACK/STACK7616/best7616.json.gz')
n = W['public']; H = W['hosted']; dim = [len(b) for b in W['frames']]
cls = {}
for r in W['live']: cls[r] = 'X'; cls[r + 112] = 'Y'
for r in H['X2']: cls[r] = 'X2'
for r in H['Y2']: cls[r] = 'Y2'
act = {W['live'][i] for i in H['Dports']}
life = {}; lives = []
for i, e in enumerate(W['program']):
    op, r = e[0], e[1]
    if op == 'INIT':
        life[r] = dict(start=i, frame=dim[e[2]], pay=0, up=0, feeds=Counter(), reads=Counter(), ownfeed=0); lives.append(life[r])
    elif op == 'CLEAR':
        life[r]['end'] = dim[e[2]]; del life[r]
    elif op == 'MOVE' and r >= n:
        d = dim[e[3]] - dim[e[2]]; life[r]['pay'] += abs(d); life[r]['up'] += max(d, 0)
    elif op in ('ADD', 'COPY'):
        s = e[2]
        if s >= n and r < n: life[s]['feeds'][cls.get(r, 'H')] += 1
        if s >= n and r >= n: life[s]['ownfeed'] += 1
        if r >= n and s < n: life[r]['reads'][cls.get(s, 'H')] += 1
print('owned lifetimes', len(lives), 'paying', sum(1 for L in lives if L['pay']), 'mass', sum(L['pay'] for L in lives))
agg = Counter(); aggn = Counter()
for L in lives:
    if not L['pay']: continue
    key = ('feeds:' + '+'.join(sorted(L['feeds'])) or '-') + ' | reads:' + '+'.join(sorted(L['reads']))
    agg[key] += L['pay']; aggn[key] += 1
for k, v in agg.most_common(): print('%4d mass  %3d lives  %s' % (v, aggn[k], k))
print('rss MB', resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2**20)
