import csv,ast,sys
g={8:64,0:0,1:1,2:2,3:4,4:8,5:12,6:20,7:36}
Np={1:63,2:36,3:20,4:12,5:6,6:3,7:1,8:0}
def scen_w(ws,d,s):
    ws=sorted(ws,reverse=True)
    if s==7: return [('ClassI',ws,d,0)]
    if s==6:
        L=[('base',ws,d,0),('alpha',ws,d,1)]
        for x in sorted(set(ws)):
            i=ws.index(x); w2=list(ws); w2[i]=x+1
            L.append(('bump%d'%x,sorted(w2,reverse=True),d,0))
        if 7 in ws:
            i=ws.index(7); L.append(('b3B',ws[:i]+ws[i+1:],d-1,0))
        return L
    return [('s5?',ws,d,0)]
if __name__=="__main__":
    rows=[r for r in csv.DictReader(open('ledger_v2.csv')) if r['audit_status']=='OPEN']
    for r in rows:
        ws=ast.literal_eval(r['weights']); d=int(r['d']); s=int(r['slack'])
        worst=None
        for tag,w2,dd,ex in scen_w(ws,d,s):
            best=-999
            for j in range(2,dd+1):
                comp=w2[dd-j:]; cap=sum(g[w] for w in comp)+ex
                m=(120-Np[j])-cap   # >0 : killed by count lemma
                if m>best: best=m;bj=j
            if worst is None or best<worst[0]: worst=(best,tag,bj)
        print(r['row'],d,s,ws,'count-margin(>0 kills)',worst)
    