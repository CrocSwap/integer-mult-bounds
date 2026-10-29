import csv,ast
g={1:1,2:2,3:4,4:8,5:12,6:20,7:36}; N={0:0,1:1,2:3,3:6,4:12,5:20,6:36,7:63,8:120}
rs=list(csv.DictReader(open('../SC-B/residue.csv')))
killed=[];res=[]
for r in rs:
    w=sorted(ast.literal_eval(r['weights']),reverse=True);d=int(r['d']);s=sum(w)-8*d
    best=None
    for j in range(1,d+1):
        cap=sum(g[x] for x in w[d-j:]); thr=120-N[8-j]
        if best is None or cap-thr<best[0]: best=(cap-thr,j,cap,thr)
    row=(d,s,w,best)
    (killed if best[0]<0 and s==7 else res).append(row)
print(len(killed),len(res))
for x in res: print(x)
w=csv.writer(open('killed.csv','w'));w.writerow(['d','s','weights','j','cap','thr','status'])
for d,s,ws,b in killed: w.writerow([d,s,ws,b[1],b[2],b[3],'KILLED(dim-cap lemma, ClassI)'])
w=csv.writer(open('residue.csv','w'));w.writerow(['d','s','weights','bestj','cap','thr','margin'])
for d,s,ws,b in res: w.writerow([d,s,ws,b[1],b[2],b[3],b[0]])
