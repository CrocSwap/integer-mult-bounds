import sys,ast;sys.path.insert(0,'.')
from rb15 import *
def test(k,d,name,starts=4):
    R=roles_of(d);print(name,'chat',round(float(chat(k,R)),3),flush=True)
    b,v=builds(k,R,nw=4,tr=10);print('  fixed walks:', 'BUILDS' if b else 'stall %.2e'%v,flush=True)
    if b:return
    ok,info,S,z,Q=jbuild(k,R,starts=starts);print('  joint walk:', 'BUILDS' if ok else 'no',info,flush=True)
    if not ok:
        b2,v2=builds(k,fullsplit(R),nw=4,tr=10);print('  coord version fixed walks:', 'BUILDS' if b2 else 'stall %.2e'%v2,flush=True)
if __name__=='__main__':
    k=int(sys.argv[1]);d=ast.literal_eval(open(sys.argv[2]).readlines()[1].strip());test(k,d,sys.argv[2])
