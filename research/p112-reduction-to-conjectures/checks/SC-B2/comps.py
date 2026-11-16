import csv,ast
from cov import g
rs=list(csv.DictReader(open('residue.csv')))
C={}
for r in rs:
    ws=sorted(ast.literal_eval(r['weights']),reverse=True);d=int(r['d']);s=int(r['s'])
    comp=tuple(ws[d-2:])
    C.setdefault(comp,[]).append((d,s))
def dom(a,b): # a dominated by b: pad
    L=max(len(a),len(b)); a=list(a)+[0]*(L-len(a)); b=list(b)+[0]*(L-len(b))
    return all(x<=y for x,y in zip(a,b))
for comp,v in sorted(C.items(),key=lambda kv:sum(g[w] for w in kv[0])):
    print(sum(g[w] for w in comp)-84,comp,len(v),[ [c2 for c2 in C if c2!=comp and dom(c2,comp)].__len__()])
