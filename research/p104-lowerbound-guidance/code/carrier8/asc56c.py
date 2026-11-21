"""CARRIER8 asc56c.py: PA-relay analysis + level cut on the asc56 U runs (halvpay pickles, our own FANOUT56 data)."""
import pickle, sys, time; sys.path.insert(0, '.')
from pa import *
for f in sys.argv[1:]:
    t0 = time.time()
    d = pickle.load(open(f, 'rb')); prog, init, P = d['prog'], d['init'], d['P']
    F = Fld(0)
    r = analyze(prog, init, P, F, ports=range(96))
    EP = r['EP']; live = [ep for ep in EP if ep['C'] is not None and ep['Ap'] is not None]
    print(f, '| bad', len(r['bad']), 'pinned', r['pinned'][:3], 'R', r['R'], 'own', r['own'], 'drops', r['drops'], 'acyclic', r['acyclic'], r['chk'])
    print('  LS', r.get('LS'))
    print('  epochs', len(EP), 'live', len(live), [(fdim(ep['Ap']), fdim(ep['B']), ep['seg'], ep['drop'], ep['own'], len(ep['N'])) for ep in live])
    # rank-8 sector hypotheses on Q96: rank of W and C restricted to ports < 96, and source/sink chart dims
    Wr = [{t: v for t, v in ep['w'].items() if t < 96} for ep in live]; Cr = [{s: v for s, v in ep['C'].items() if s < 96} for ep in live]
    print('  rank_Q W|Q96', rank(F, Wr), 'rank_Q C|Q96', rank(F, Cr), 'sources dimA\'<=1', all(fdim(ep['Ap']) <= 1 for ep in live if ep['c']),
          'sinks dimB>=8', all(fdim(ep['B']) >= 8 for ep in live if ep['w']), '%.0fs' % (time.time() - t0))
