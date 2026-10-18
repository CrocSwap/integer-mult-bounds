import sys,os,pickle,csv,math,gzip,json
from collections import Counter,defaultdict
from fractions import Fraction as Q
sys.dont_write_bytecode=True
sys.path.insert(0,(__import__('os').environ['HM_ROOT']+'/cards/B99/work'))
os.chdir((__import__('os').environ['HM_ROOT']+'/cards/B98b'))
sys.path.insert(0,'.')
import lib
from fr import FL
src_dy=open('dyad.py').read()
ns={}
exec(src_dy.split("if __name__=='__main__':")[0],ns)
d=ns['d'];blocks=ns['blocks'];rows0=ns['rows'];src=ns['src'];psi=ns['psi'];v=ns['v']
F=FL(d)
regs=lambda e:[e[1]]+([e[2]] if e[0]=='add' else [])
good=['(0, 2, 4, 6)','(0, 2, 5, 7)','(1, 2, 4, 7)','(1, 2, 5, 6)','(1, 3, 4, 6)','(1, 3, 5, 7)','(2, 3, 4, 5)','(2, 3, 6, 7)','(4, 5, 6, 7)']
A=[list(e) for e in d['A']]
plans={}
for bn in good:
    regsb=blocks[bn];S_=set(regsb)
    keep=src('B',S_)|src('tail',S_)|src('cut',S_)|src('compensation',S_)|src('cleanup',S_)|{e[2] for e in d['A'] if e[0]=='add' and e[2] in S_ and e[1] not in S_ and e[1]>=v or (e[0]=='add' and e[2] in S_ and e[1]<v and e[1] not in sorted({j for r in regsb for j in rows0[r]}))}
    cols=sorted({j for r in regsb for j in rows0[r]})
    names=cols+sorted(keep)
    rv=[rows0[r] for r in names]
    best=None
    for seed in range(6):
        o=ns['synth_dy'](rv,8,seed)
        if o and ns['verify2'](o[0],o[1],rv):
            if best is None or len(o[0])<len(best[0]):best=o
    plans[bn]=(names,best[0],S_,set(cols),keep)
    print(bn,'cols',cols,'keep',len(keep),'ops',len(best[0]),flush=True)
pickle.dump({k:(a,b,sorted(c),sorted(e),sorted(f)) for k,(a,b,c,e,f) in plans.items()},open((__import__('os').environ['HM_ROOT']+'/cards/B98c/work/plans.pkl'),'wb'))
