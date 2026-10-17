# writes the CNF of JOINT2/satP.py without solving it: gen_satP.py OUT.cnf nx x1 P  (exec of satP.py up to its solver call)
import sys,os
out,nx,x1,P=sys.argv[1:5]
src=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','JOINT2','satP.py')).read().split("r=subprocess.run")[0]
sys.argv=['satP.py',nx,x1,P,'g']
exec(src)
os.replace(fn,out)
print('cnf',out,'vars',nv,'clauses',len(cl))
