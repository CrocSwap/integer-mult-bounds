from rb1 import *
from rb2 import K4_3,K4_4
from rb3 import CS6
def runw(name,k,roles,seeds=2,tries=6,pen=0.0):
    print(name,'chat',round(float(chat(k,roles)),4),flush=True)
    for sd in range(seeds):
        S=WSys(k,roles,pen=pen);nr,z=S.solve(sd,tries=tries)
        print('  free-walk seed',sd,'res %.2e'%nr, S.wdiag(z) if nr<1e-9 else '',flush=True)
if __name__=='__main__':
    for pen in (0.1,0.2): runw("C1",3,C1,pen=pen);runw("K4#3",4,K4_3,pen=pen);runw("K4#4",4,K4_4,pen=pen);runw("CS6",6,CS6,pen=pen)
