# Writes cnt_UNIT.pkl = {'lb22': {(R, W): lb}} (only entries with lb <= 7, the only ones cnt9.py / cnt9b.py read) from the recorded data file
# ../data/lb22_le7_UNIT.json, so cnt9.py / cnt9b.py can be replayed without the 44 min (P112) / 32 min (P104) census run.  usage: mk_cnt_pkl.py UNIT
import sys, json, os, pickle
u = sys.argv[1]
d = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', f'lb22_le7_{u}.json')))
pickle.dump({'lb22': {(tuple(R), tuple(W)): x for R, W, x in d['pairs']}}, open(f'cnt_{u}.pkl', 'wb'))
print('wrote cnt_%s.pkl with %d entries' % (u, len(d['pairs'])))
