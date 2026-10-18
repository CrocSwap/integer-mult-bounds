"""F2 minrank (asymmetric B = W U^T allowed) of the A-orthogonality decoder pattern, by SAT with the clique gauge."""
import sys,time; sys.path.insert(0,sys.path[0])
from klines import *
from minrank_sat import solve_asym
def systems():
    from algebra_lines import e8_roots, left_quat, a2_rotation, lines_over
    roots=e8_roots(); I8=np.eye(8,dtype=np.int64); Li,Lj,Lk=left_quat()
    out={}
    for nm,basis in (('Gauss',[I8,Li]),('Eisen',[I8,a2_rotation(roots)]),('Hurwitz',[I8,Li,Lj,Lk]),('E8',[I8])):
        reps,_=lines_over(roots,basis); out[nm]=System(nm,reps,I8,basis)
    return out
def minrank(S, cmin=None, cmax=None):
    a,K=S.alpha()
    pat={(i,j) for i in range(S.v) for j in range(S.v) if S.NO[i,j]}
    c=cmin or a; res=[]
    while True:
        r=solve_asym(S.v,pat,None,c,'none',K); res.append((c,r['result'],r['sec']))
        print(S.name,c,r['result'],r['sec'],flush=True)
        if r['result']=='SAT': return c,res,r
        c+=1
        if cmax and c>cmax: return None,res,None
if __name__=='__main__':
    nm=sys.argv[1]
    if nm=='K12':
        from k12 import k12_system; S=k12_system()
    else: S=systems()[nm]
    print(nm,'v',S.v,'w',S.w,'alpha',S.alpha()[0])
    minrank(S, int(sys.argv[2]) if len(sys.argv)>2 else None, int(sys.argv[3]) if len(sys.argv)>3 else None)
