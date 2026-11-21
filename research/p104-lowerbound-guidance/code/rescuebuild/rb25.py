"""rb25: inspect a stalled fixed-walk solution: residual blocks, collapsed rows, y.x of pieces."""
import sys,ast;sys.path.insert(0,'.')
from rb1 import *;from rb10 import roles_of
def inspect(k,R,w=0,tries=4):
    S=FSys(k,R,anywalk(k,w));nr,z=S.solve(w,tries=tries);Q,B,A,X,Y=S.unpack(z)
    print('res %.3e'%nr)
    for i,(o,q) in enumerate(S.pc):
        if len(q)>1 or abs(Y[i]@X[i]-1)>1e-3:print(' piece',i,'owner',o,sorted(q),'E',S.E[i],'yx %.3f'%(Y[i]@X[i]),'x',np.round(X[i][S.E[i]],2),'y',np.round(Y[i][S.E[i]],2))
    for r,(M,P) in enumerate(R):
        nb=max(np.abs(B[r]).max(),1e-300);na=max(np.abs(A[r]).max(),1e-300)
        print(' role',r,sorted(M),[sorted(p) for p in P],'|b|max %.2e |a|max %.2e'%(nb,na))
if __name__=='__main__':
    k=int(sys.argv[1]);l=[x for x in open(sys.argv[2]) if 'SURVIVES' in x][int(sys.argv[3])]
    d=ast.literal_eval(l[l.index('((('):].strip());print(l.split('val ')[1].split()[0]);inspect(k,roles_of(d))
