# Case A kill check: a's row must be frame x_a ∝ e_m; m in I impossible (x_a = -Σ y2_j e_ij - w, w in W⊥, W⊥∩span e_I = 0, all y2_j≠0);
# m in I^c needs u = e_m + Σ β_j e_ij ⟂ all c_wj with β_j ≠ 0, i.e. m ∈ supp c_wj for all four j. Check over the 128 survivors.
import sys, pickle, numpy as np
from lib import C
surv=pickle.load(open('d4A_surv.pkl','rb')); Ic=(0,1,2,4); bad=0
for c,ws in surv:
    I=[i for i,z in c]
    # exact: does W⊥ contain a vector e_m + Σ β_j e_ij (all β_j≠0)?  solve per m
    for m in Ic:
        if all(C[w][m]!=0 for w in ws): bad+=1
    # and W⊥ ∩ span(e_I) = 0 (4 roots with distinct private coords i_j restricted to I: matrix [c_wj[i]] diagonal-nonzero)
    M=np.array([[C[w][i] for i in I] for w in ws]); assert round(abs(np.linalg.det(M)))!=0
print('configs',len(surv),'with an admissible frame row for term a:',bad)
