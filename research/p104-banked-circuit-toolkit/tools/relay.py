"""pure relay scan: paid t:A->B whose only reader is paid j:B->C with form {t:c}; contract to A->C if nested."""
import sys, os
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bank import load, transpose, load_circuit
import nest
W = load(sys.argv[1]); fr = W['frames']; dim = [len(f) for f in fr]; K = float(os.environ.get("BANK_KAPPA", "0.00373"))
f = lambda r: r ** (1 - K) if r else 0.0
net = load_circuit(sys.argv[2])
for tag, nn in (('forward', net), ('transpose', transpose(net))):
    rd = defaultdict(list)
    for k, row in nn.forms.items():
        for d in row:
            if d >= 0: rd[d].append(k)
    hits = []
    for t, (A, B) in nn.moves.items():
        R = rd[t]
        if len(R) != 1 or R[0] >= nn.first: continue
        j = R[0]
        if set(nn.forms[j]) != {t}: continue
        C = nn.moves[j][1]; r = nest.trank(fr, A, C)
        if r is None or r == 0: continue
        g = f(abs(dim[B] - dim[A])) + f(abs(dim[C] - dim[B])) - f(r)
        if g > 1e-12: hits.append((round(g, 5), t, j, A, B, C))
    print(tag, 'relays', len(hits), sorted(hits, reverse=True)[:8])
