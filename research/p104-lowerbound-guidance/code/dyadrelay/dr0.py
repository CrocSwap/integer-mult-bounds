"""dr0: sizing helper. Aggregated IP (ic4) at k with row families dropped (DROP=regex), report value. Also LP duals (RELAX=1)."""
import os,sys,re
for v in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[v]='1'
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','intcaller'))
import ic1
_o=ic1.rowdefs
def rd(k):
    R=_o(k);d=os.environ.get('DROP')
    return [r for r in R if not (d and re.match(d,r[0]))]
ic1.rowdefs=rd
import ic3,ic4,highspy,numpy as np
for k in map(int,sys.argv[1:]):
    tur=os.environ.get('TUR','1')=='1'
    h,var=ic4.build(k,tur)
    if os.environ.get('RELAX')=='1':
        lp=h.getLp();lp.integrality_=[highspy.HighsVarType.kContinuous]*lp.num_col_;h.passModel(lp)
    h.run();info=h.getInfo();print('k',k,'DROP',os.environ.get('DROP'),'val %.4f'%(-104*info.objective_function_value/k))
    if os.environ.get('RELAX')=='1':
        R=ic1.rowdefs(k);du=h.getSolution().row_dual
        for i,r in enumerate(R):
            if abs(du[i])>1e-9:print('  dual',r[0],'%.5f'%du[i])
