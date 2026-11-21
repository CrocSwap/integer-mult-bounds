import numpy as np
def freplay(C, q, D):
    n, k = C['roles'], C['stages']; P = np.eye(n, dtype=complex)
    for e in C['events']:
        op = e[0]; M = np.eye(n, dtype=complex)
        if op == 'ADD': M[e[1], e[2]] += float(eval(str(e[3])))
        elif op == 'SCALE': M[e[1], e[1]] = float(eval(str(e[2])))
        elif op == 'LAMBDA': s = e[2]; M[e[1], e[1]] = ((1+s*1j)+(1-s*1j)*q*q)/2
        elif op == 'IDLE_ONE': M[e[1], e[1]] = np.prod([D[x-1] for x in e[2]])
        elif op == 'HOST':
            t, s, d, a, b = e[1]-1, e[2], e[3], float(eval(str(e[4]))), float(eval(str(e[5])))
            M[s, d] = a*q; M[d, s] = b*q**3; M[d, d] = 1+a*b; M[s, :] *= D[t]; M[d, :] *= D[t]
        P = M @ P
    T = np.diag([q**dg[0]*np.prod([D[t] for t in range(k) if dg[2+t]]) for dg in C['diagonal']])
    return np.abs(P - T).max()
def ftest(C, trials=3, seed=0):
    rng = np.random.default_rng(seed); out = []
    for _ in range(trials):
        D = rng.uniform(0.5, 1.5, C['stages'])
        out.append(max(freplay(C, q, D) for q in (1, -1, 1j, -1j)))
    return max(out)
