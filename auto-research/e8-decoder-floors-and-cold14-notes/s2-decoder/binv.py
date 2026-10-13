import numpy as np, sympy
from geo import *
def binv(P):
    BD = sympy.Matrix(B0[np.ix_(P, P)].tolist())
    if BD.det() % 2 == 0: return None
    return np.array(BD.inv_mod(2).tolist(), dtype=int)
if __name__ == '__main__':
    P = [39, 52, 57, 71, 76, 78, 103, 109, 114]
    Bi = binv(P); print(Bi)
    orth = (G[np.ix_(P, P)] == 0).astype(int)
    print('column weights', Bi.sum(0))
