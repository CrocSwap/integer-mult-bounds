"""Fast exact pricer for the nine-stage bit c of the v = 111, R = 439 punctured word: c = certify(288 * local paid profile + REM, 64, 28416).
REM (idle remainder under the frozen hosting) was read off the pipeline audit of the base word; it reproduces the pipeline c to 24 digits
for the base word and for the 2-move word (research/e8-bit-p111/tune).  Not a substitute for verify.sh.
Prepared with Claude Opus 5.5 (Anthropic), via Claude Code; Apache-2.0."""
import importlib.util,sys,time
from pathlib import Path
from fractions import Fraction as Q
ENG=Path(__file__).resolve().parents[2]/'e8-bit-carrier-skeleton/code/hub/e8-r740-replica32/code/engines'
def load(name):
    sp=importlib.util.spec_from_file_location('e_'+name,ENG/(name+'.py'));mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod);return mod
M=load('moment')
REM={2:13920,4:14208,6:14208,7:21312,42:288}
W=28416;m=64;T=288
def profile(Hpaid,rem=REM):
    P={}
    for r,n in Hpaid.items(): P[r]=P.get(r,0)+T*n
    for r,n in rem.items(): P[r]=P.get(r,0)+n
    return P
def fast_c(Hpaid,rem=REM):
    P=profile(Hpaid,rem)
    mass=sum(r*n for r,n in P.items()); assert m*W-mass==10272,(m*W-mass)
    return M.certify(P,m,W,True)['lower']
if __name__=='__main__':
    t=time.time()
    print(fast_c({1:1321,2:1342,3:80,4:47,5:102,6:10,7:18}),time.time()-t)
