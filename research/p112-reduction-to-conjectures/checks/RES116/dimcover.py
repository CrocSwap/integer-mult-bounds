# Dim-Cover test (SC-B2 lemma (b)) per scenario, j given, K0=top d-j. Own driver; engine = SC-B2 cov3 (C) / cov2 (numpy).
import sys,os,itertools,time,csv,ast,json
sys.path.insert(0,'../SC-B2'); os.chdir('../SC-B2')
from cov3 import *
import cov2
sys.path.insert(0,'../AUDIT-SC')
PAR={}
def parab(I):
    if I not in PAR: PAR[I]=frozenset(parabolic(I))
    return PAR[I]
def scen_w(ws,d,s):
    """scenarios as (tag, weights multiset, d, nextra_lines) mirroring rrc_audit.scen"""
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
def alive_for(ws,d,extra,j,eng=cover_set3,verbose=False):
    ws=sorted(ws,reverse=True)
    comp=ws[d-j:]+[1]*extra; cap=sum(g[w] for w in comp); rank=8-j
    al=[]
    for I in itertools.combinations(range(8),rank):
        P_=parab(I); T=[t for t in range(n) if t not in P_]
        if len(T)>cap: continue
        if not any(w>=5 for w in comp): al.append((I,'nobig')); continue
        r=eng(T,comp)
        if r is not False: al.append((I,r))
    return comp,cap,al
if __name__=='__main__':
    rows=[r for r in csv.DictReader(open('../RES116/ledger_v2.csv')) if r['audit_status']=='OPEN']
    want=set(map(int,sys.argv[1].split(','))); J=int(sys.argv[2])
    for r in rows:
        if int(r['row']) not in want: continue
        ws=ast.literal_eval(r['weights']); d=int(r['d']); s=int(r['slack'])
        out=[]
        for tag,w2,dd,ex in scen_w(ws,d,s):
            t=time.time(); comp,cap,al=alive_for(w2,dd,ex,J)
            out.append((tag,comp,cap,len(al),round(time.time()-t,1)))
        print(r['row'],ws,J,out,flush=True)
