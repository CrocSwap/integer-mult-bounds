"""UPHASE adjoint.py: transpose a run (Tellegen / transposition principle).
Reversed op order; ADD d += lam*s  ->  ADD s += lam*d ; charts C -> C^perp (so publics still ascend); INIT <-> CLEAR.
Roles swap: original ('X',t) becomes adjoint ('Y',t) (chart {0}->q_t^perp, content y_t), original ('Y',s) becomes adjoint
('X',s) (chart <q_s> -> V, content x_s), helpers keep their own token.  The adjoint delivers M^T into its X's [P, linear algebra]."""
from fattr import *

def perp_chart(F, N):
    B = basis(F)
    return frozenset(x for x in range(1 << N) if all(not dot(x, b) for b in B))

def adjoint(prog, init, N):
    # chart history of every register
    ch = {k: f for k, (f, c) in init.items()}
    hist = []              # per op: chart of the register(s) before op
    owned_init = {}
    for op in prog:
        if op[0] == 'INIT': ch[op[1]] = op[2]; hist.append(None)
        elif op[0] == 'MOVE': hist.append(ch[op[1]]); ch[op[1]] = op[2]
        elif op[0] == 'CLEAR': hist.append(ch[op[1]]); del ch[op[1]]
        else: hist.append(None)
    final_ch = dict(ch)
    pc = {}
    def P_(F):
        if F not in pc: pc[F] = perp_chart(F, N)
        return pc[F]
    ren = lambda r: (('Y', r[1]) if r[0] == 'X' else ('X', r[1]) if r[0] == 'Y' else r) if isinstance(r, tuple) else r
    ainit = {}
    for k, f in final_ch.items():
        rk = ren(k)
        if isinstance(k, tuple) and k[0] == 'X': c = {('y', k[1]): Fr(1)}
        elif isinstance(k, tuple) and k[0] == 'Y': c = {('x', k[1]): Fr(1)}
        else: c = {('tok', str(k)): Fr(1)}
        ainit[rk] = (P_(f), c)
    aprog = []
    for op, h in zip(reversed(prog), reversed(hist)):
        if op[0] == 'ADD': aprog.append(('ADD', ren(op[3]), op[2], ren(op[1])))
        elif op[0] == 'MOVE': aprog.append(('MOVE', ren(op[1]), P_(h)))
        elif op[0] == 'CLEAR': aprog.append(('INIT', ren(op[1]), P_(h), {}, True))
        elif op[0] == 'INIT': aprog.append(('CLEAR', ren(op[1])))
    return aprog, ainit
