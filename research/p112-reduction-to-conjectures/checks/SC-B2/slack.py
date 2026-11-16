import csv,ast,itertools
from cov import parabolic,g,n
Pn={}
for r in range(0,8):
    mx=0
    for I in itertools.combinations(range(8),r):
        mx=max(mx,len(parabolic(I)))
    Pn[r]=mx
print(Pn)
rs=list(csv.DictReader(open('residue.csv')))
for r in rs:
    ws=sorted(ast.literal_eval(r['weights']),reverse=True);d=int(r['d']);s=int(r['s'])
    sl=[]
    for j in range(1,6):
        comp=ws[d-j:];cap=sum(g[w] for w in comp);sl.append(cap-(120-Pn[8-j]))
    print(d,s,ws,sl)
