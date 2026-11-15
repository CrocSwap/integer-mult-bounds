import sys, pickle
from lib import *
W = load(); NP, mains, fixed, dim = setup(W); P = W['program']; ch = chains(W)
X = pickle.load(open('explore.pkl', 'rb'))
for F in map(int, sys.argv[1:]):
    S = X['stops'][F]; print('=== F', F, 'dim', dim[F], W['frames'][F])
    for s in S:
        h = s[0]; print('  helper', h, 'chain dims', [dim[c[0]] for c in ch[h]], 'frames', [c[0] for c in ch[h]], 'arr', s[1], 'leave', s[2])
    for i, e in enumerate(P):
        if evframe(e) == F: print('   op', i, e)
