"""Frame-intersection certificate (Lemma 3.3) for the label classes of the dense pairing; exact bitmask computations."""
import json, os, itertools
from roots import *

HERE = os.path.dirname(os.path.abspath(__file__))

def units():
    """name -> (list of lines, T).  P112 = E8 minus a frame, P104 = E8 minus two frames, 'E7-frame' = E7 minus a 7-frame (data/p104_frames.json)."""
    D = json.load(open(os.path.join(HERE, '..', 'data', 'p104_frames.json')))
    F0, F1 = D['F0'], D['F1']
    out = {n: UNITS[n] for n in ('D4', 'D5', 'D6', 'E6', 'E7', 'E8')}
    out['P112'] = ([E8[i] for i in range(120) if i not in set(F0)], 8)
    out['P104'] = ([E8[i] for i in range(120) if i not in set(F0) | set(F1)], 8)
    adj = orth_graph(E7)
    fr7 = next(c for c in maximal_cliques(adj) if popcount(c) == 7)
    out['E7-frame'] = ([E7[i] for i in range(63) if not fr7 >> i & 1], 7)
    return out

def analyse(L, T):
    v = len(L); Br = b0rows(L); basis = colspace_basis(Br); h = len(basis)
    adj = orth_graph(L)
    cl = list(maximal_cliques(adj)); alpha = max(popcount(c) for c in cl)
    frames = [c for c in cl if popcount(c) == T]
    allcl = span_vectors(basis)
    has_frame = []; unc = []; cert_c = []
    for co, w in allcl:
        if any(f & ~w == 0 for f in frames): has_frame.append((co, w)); continue
        Os = [f & ~w for f in frames]; ok = False
        for E in frames:
            ins = [o for o in Os if o & ~E == 0]
            if ins:
                x = ins[0]
                for o in ins[1:]: x &= o
                if x == 0: ok = True; break
        (cert_c if ok else unc).append((co, w))
    cos = set(c for c, _ in unc)
    sub2 = any((a ^ b) in cos for a, b in itertools.combinations(sorted(cos), 2))
    return dict(v=v, T=T, h=h, alpha=alpha, nframes=len(frames), frames=frames, classes=len(allcl), has_frame=has_frame, cert_c=cert_c,
                unc=unc, sub2=sub2, basis=basis, Br=Br)
