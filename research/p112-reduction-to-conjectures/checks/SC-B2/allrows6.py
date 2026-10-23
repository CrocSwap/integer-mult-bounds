import pickle,collections,json
from rrc6 import dead_j
res=pickle.load(open('../SPANCOVER/opts.pkl','rb'))
def anyj(f,d):
    for j in range(2,min(d,6)+1):
        if f(j): return True
    return False
def robust6(ws,d):
    ok=anyj(lambda j:dead_j(ws[d-j:],j)[0],d) and anyj(lambda j:dead_j(ws[d-j:],j,1)[0],d)
    if not ok: return False
    xs=set()
    for j in range(2,min(d,6)+1): xs|=set(ws[d-j:])
    for x in xs:
        def f(j):
            comp=ws[d-j:]
            if x not in comp: return True     # b* of this weight not in comp at this j -> ClassI-like base (checked above)
            kmin=ws[d-j-1] if d-j-1>=0 else None
            up=list(comp); up.remove(x); up.append(x+1)
            if dead_j(up,j)[0]: return True
            if kmin is None: return False
            sw=list(comp); sw.remove(x); sw.append(kmin)
            return dead_j(sw,j)[0]
        if not anyj(f,d): return False
    return True
c=collections.Counter(); rows=[]
for d,s,ws,e,o in res:
    ws=sorted(ws,reverse=True)
    if s==6:
        r=robust6(ws,d); c[('s6',r)]+=1
print(c)
