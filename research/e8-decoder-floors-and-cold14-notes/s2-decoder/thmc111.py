from bitp import *
P = {39, 52, 57, 71, 76, 78, 103, 109, 114}
live = np.ones(NL, bool); live[list(P)] = False
defic = [p for p in range(1, 512) if rankQ_lines(list(RLIST[p][live[RLIST[p]]])) < 8]
print('P111: reader sets R(p)\\P not spanning Q^8:', len(defic), defic[:20])
s = s_all(P); ch, c = greedy_basis(s)
from collections import Counter
print('star greedy', c, Counter(s.values()))
