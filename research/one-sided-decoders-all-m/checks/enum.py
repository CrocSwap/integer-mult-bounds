# list all multisets with cost(T) < target satisfying dp3 P112 constraints for given d
import sys
exec(open('dp3.py').read().split("    Ws=list(range(Wmax,0,-1))")[0].replace("def run(unit):","def setup(unit):")+"    return ok,g\n")
ok,g=setup('P112')
d=int(sys.argv[1]); target=int(sys.argv[2])
Ws=[7,6,5,4,3,2,1]; out=[]
def rec(i,cnt,wt):
    if wt>=target: return
    if i==len(Ws):
        ws=sorted([w for w in Ws for _ in range(cnt[w])],reverse=True)
        if ok(ws,d): out.append((wt,ws))
        return
    w=Ws[i]
    for c in range(0,(target-wt)//w+1):
        cnt[w]=c; rec(i+1,cnt,wt+c*w)
    cnt[w]=0
rec(0,{w:0 for w in Ws},0)
out.sort()
print(len(out),'multisets'); 
from collections import Counter
print(Counter(len(ws) for _,ws in out))
for x in out[:15]: print(x)
