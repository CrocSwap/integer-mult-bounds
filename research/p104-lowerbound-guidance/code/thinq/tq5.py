# THINQ tq5: e=0 branch crossing scan (float LP from tq4), per-stage leaf law [P] (cl=k) and global leaf law [CONJ] (cl=1)
import sys; sys.argv=[sys.argv[0]]+sys.argv[1:]
from tq4 import solve, HP
for k in map(int,sys.argv[1:]):
    vP,supP,_=solve(k,0,k); vC,supC,_=solve(k,0,1); vN,_,_=solve(k,0,None)
    print(f'k{k} HP {HP(k):.4f} e0[noleaf] {vN:.4f} e0[P] {vP:.4f} e0[CONJ] {vC:.4f}',flush=True)
    print('   P sup',supP[:5],flush=True)
