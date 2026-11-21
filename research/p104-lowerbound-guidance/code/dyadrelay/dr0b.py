"""LP relaxation duals of the dr2 (SUBDY) model at k: which rows bind."""
import os,sys
sys.argv=[sys.argv[0]]+sys.argv[1:]
import dr2,ic1,ic4,highspy
for k in map(int,sys.argv[1:]):
    h,var=ic4.build(k,os.environ.get('TUR','0')=='1')
    lp=h.getLp();lp.integrality_=[highspy.HighsVarType.kContinuous]*lp.num_col_;h.passModel(lp);h.run()
    print('k',k,'LP %.4f'%(-104*h.getInfo().objective_function_value/k))
    R=ic1.rowdefs(k);du=h.getSolution().row_dual
    for i,r in enumerate(R):
        if abs(du[i])>1e-6:print('  dual',r[0],'%.5f'%du[i])
    x=h.getSolution().col_value
    for key,j in var.items():
        if key[0]=='N' and x[j]>1e-6:print('  N',key[1],'%.3f'%x[j], {L:round(x[var[('Z',key[1],L)]],3) for L in range(1,min(key[1],k-2)+1) if x[var[('Z',key[1],L)]]>1e-6})
