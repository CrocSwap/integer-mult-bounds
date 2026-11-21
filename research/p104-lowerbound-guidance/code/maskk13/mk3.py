"""mk3: best invoice (exact type IP, all IC rows incl TURAN) of the family: exactly 2 hubs D=k, exactly 1 role of degree d, exactly 2k-5 roles of degree 2."""
import sys,os
sys.path.insert(0,'../intcaller')
import ic1,numpy as np,highspy
from decimal import Decimal
def fam(k,d):
    T=[t for t in ic1.types(k) if t[0] in (k,d,2)]
    h,R,yc,ac,bc,rows=ic1.build(k,T,True,False)
    inf=highspy.kHighsInf
    for D,cnt in ((k,2),(2,2*k-5),(d,1)):
        if D==d and d in (2,k):continue
        idx=[i for i,(DD,P) in enumerate(T) if DD==D]
        h.addRow(cnt,cnt,len(idx),np.array(idx,dtype=np.int32),np.ones(len(idx)))
    h.run()
    st=h.getModelStatus()
    if st!=highspy.HighsModelStatus.kOptimal:return None
    return -h.getInfo().objective_function_value*104/k
if __name__=='__main__':
    k=int(sys.argv[1])
    for d in range(3,k-1):
        v=fam(k,d)
        print('k',k,'d',d,'best invoice','%.4f'%v if v else None,'ABOVE' if v and v>ic1.BAR else '',flush=True)
