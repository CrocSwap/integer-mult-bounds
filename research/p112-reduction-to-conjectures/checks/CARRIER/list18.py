import re
M=[]
for l in open('../L120/land7.out'):
    m=re.match(r'd (\d) slack (\d) (\{.*?\}) (\[.*\])',l.strip())
    if not m: continue
    d=int(m.group(1))
    if d>3: continue
    for (k,ws,e) in eval(m.group(4)): M.append((d,k,ws,e))
g={1:1,2:2,3:4,4:8,5:12,6:20,7:36}
print(len(M))
for d,k,ws,e in M:
    a=len(ws); big=sorted(ws,reverse=True)
    comp=big[d-1:]            # remove the d-1 largest
    print(f'd={d} s={k} e={e} a={a} {ws}  K=remove {big[:d-1]}  complement {comp} cap={sum(g[w] for w in comp)}')
