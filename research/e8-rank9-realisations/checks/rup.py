# Minimal independent RUP checker (deletions ignored: sound, every kept clause is implied). Usage: rup.py F.cnf P.drat
import sys
def read(fn):
    out=[]
    for l in open(fn):
        if l[0] in 'pc': continue
        t=l.split(); 
        if not t: continue
        d=t[0]=='d'
        lits=[int(x) for x in (t[1:] if d else t)]; assert lits[-1]==0
        out.append((d,lits[:-1]))
    return out
F=[c for _,c in read(sys.argv[1])]; P=read(sys.argv[2])
clauses=[]; watch={}
val={}
def addc(c):
    c=list(dict.fromkeys(c)); k=len(clauses); clauses.append(c)
    for l in c[:2]: watch.setdefault(l,[]).append(k)
    return k
units=[]
def propagate(assign,trail,start):
    i=start
    while i<len(trail):
        lit=trail[i]; i+=1; fl=-lit
        ws=watch.get(fl,[]); keep=[]
        j=0
        while j<len(ws):
            k=ws[j]; j+=1; c=clauses[k]
            if len(c)==1:
                keep.append(k); 
                if assign.get(c[0])==False or assign.get(-c[0]) : pass
            # ensure fl is c[1]
            if c[0]==fl: c[0],c[1]=c[1],c[0]
            if len(c)>1 and c[1]!=fl: keep.append(k); continue
            if assign.get(c[0]) is True: keep.append(k); continue
            found=False
            for m in range(2,len(c)):
                if assign.get(c[m]) is not False:
                    c[1],c[m]=c[m],c[1]; watch.setdefault(c[1],[]).append(k); found=True; break
            if found: continue
            keep.append(k)
            if assign.get(c[0]) is False:
                keep.extend(ws[j:]); watch[fl]=keep; return False
            if assign.get(c[0]) is None:
                assign[c[0]]=True; assign[-c[0]]=False; trail.append(c[0])
        watch[fl]=keep
    return True
def check(c):
    # RUP: assign negation, propagate (with unit clauses), expect conflict
    assign={}; trail=[]
    for l in c:
        if assign.get(-l) is True: continue
        if assign.get(l) is True: return True
        assign[-l]=True; assign[l]=False; trail.append(-l)
    for u in unitlits:
        if assign.get(u) is False: return True
        if assign.get(u) is None: assign[u]=True; assign[-u]=False; trail.append(u)
    return not propagate(assign,trail,0)
unitlits=[]
for c in F:
    if len(c)==1: unitlits.append(c[0])
    else: addc(c)
n=0
for d,c in P:
    if d: continue
    if not check(c): print('FAIL lemma',n,c); sys.exit(1)
    n+=1
    if len(c)==0: print('VERIFIED: empty clause derived by RUP after',n,'lemmas'); sys.exit(0)
    if len(c)==1: unitlits.append(c[0])
    else: addc(c)
print('no empty clause'); sys.exit(2)
