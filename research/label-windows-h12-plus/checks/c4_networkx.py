"""c4: third omega implementation (networkx find_cliques; OPTIONAL: SKIP without networkx): omega of all 144 exceptional pairs equals the recorded value,
plus 20 random sections per representative (940 pairs; FULL=1: 400 per rep) all have omega >= 7."""
import json, os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'lib'))
try: import networkx as nx
except ImportError: print('SKIP c4  networkx not installed'); sys.exit(0)
import common
D = common.load(); Z, NO, reps = D['Z'], D['NO'], D['reps']
G = nx.Graph(); G.add_nodes_from(range(112)); G.add_edges_from((i, j) for i in range(112) for j in range(i + 1, 112) if NO[i, j])
def om(r, i):
    S = [v for v in range(112) if not Z[reps[r]][v] and not Z[i][v]]
    return max((len(c) for c in nx.find_cliques(G.subgraph(S))), default=0)
ex = json.load(open(os.path.join(HERE, '..', 'data', 'exceptional_pairs.json')))
ok = all(om(r, i) == w for r, i, w in ex)
print(('PASS' if ok else 'FAIL') + ' c4.a  networkx omega = recorded omega on all %d exceptional pairs' % len(ex))
rng = random.Random(11); k = 400 if os.environ.get('FULL') == '1' else 20; low = 0; seen = set((r, i) for r, i, _ in ex)
for r in range(47):
    for i in rng.sample(range(440880), k):
        if (r, i) not in seen and om(r, i) < 7: low += 1
print(('PASS' if low == 0 else 'FAIL') + ' c4.b  %d random non-exceptional pairs (%d per representative): omega >= 7 on all' % (47 * k, k))
sys.exit(0 if ok and low == 0 else 1)
