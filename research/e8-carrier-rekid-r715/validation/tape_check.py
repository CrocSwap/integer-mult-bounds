"""Independent recomputation of R, the paid-children profile, live stock W and the bit saving c from the EMITTED hosted tape
(v/hosted/GLOBAL-TEMPLATE.json.gz) and the mixed word.  Own record export, own F2 replay of the emitted local programs,
own hosting-window audit, own moment solve (mpmath).  No builder pass/fail summaries are read.
usage: tape_check.py MIXED_WORD.json HOSTED_TEMPLATE.json.gz CLAIM_RESULT.json"""
import sys,json,gzip,hashlib
from collections import Counter,defaultdict
from fractions import Fraction as Fr
import mpmath as mp
wordp,tp,claimp=sys.argv[1:4]
w=json.load(open(wordp)); t=json.loads(gzip.decompress(open(tp,'rb').read())); claim=json.load(open(claimp))
v,R,h=w['v'],w['R'],w['h']; n=2*v+R; lines=w['lines']
# ---- own frame dimensions
def rank(idx):
    rows=[]
    for i in idx:
        x=[Fr(a) for a in lines[i]]
        for r in rows:
            p=next(k for k in range(h) if r[k])
            if x[p]: f=x[p]/r[p]; x=[a-f*b for a,b in zip(x,r)]
        if any(x): rows.append(x)
    return len(rows)
dim=[rank(f) for f in w['frames']]; ZERO=[k for k,d in enumerate(dim) if d==0]; assert len(ZERO)==1; ZERO=ZERO[0]
# ---- (A) own export of the word to the forward record stream, in the template's normalised format
cur=list(w['start']); rec=[]
def move(r,f):
    if cur[r]!=f: rec.append((0,r,cur[r],f,dim[f]-dim[cur[r]],0)); cur[r]=f
def run(gs):
    for f,d,ss in gs:
        for r in [d]+ss: move(r,f)
        for s in ss: rec.append((1,d,s,1,f,0))
run(w['D']); run(w['A'])
temp=n
for k,q in enumerate(w['ret']):
    fq=cur[q]; rec.append((2,q,temp,fq,ZERO,dim[fq]))
    for tt,row in enumerate(w['scatter']):
        if k in row: rec.append((1,v+tt,temp,1,ZERO,0))
    rec.append((3,q,temp,fq,ZERO,0))
run(w['B']); run(w['C'])
for r in range(n): move(r,w['final'][r])
fwd=[]; 
for op,x,y,c,f,z in rec:
    if op==0: fwd.append([0,x,y,c,f,0])
    elif op==1: fwd.append([1,x,y,c,f,0])
    elif op==2: fwd.append([2,x,y,c,f,abs(dim[c]-dim[f]),0])
    else: fwd.append([3,x,y,c,f,z,0])
rev=[]
for op,x,y,c,f,z in reversed(rec):
    if op==0: rev.append([0,x,c,y,f,1])
    elif op==1: rev.append([1,x,y,-c,f,1])
    elif op==3: rev.append([2,x,y,c,f,abs(dim[c]-dim[f]),1])
    else: rev.append([3,x,y,c,f,z,1])
Tf,Tr=t['local_programs']['forward'],t['local_programs']['reverse']
print('(A) own export == emitted forward program: %s (%d records); reverse: %s'%(fwd==Tf,len(fwd),rev==Tr))
adds=sum(1 for z in Tf if z[0]==1); gates=sum(len(ss) for ph in 'DABC' for f,d,ss in w[ph])+sum(len(r) for r in w['scatter'])
print('    ADD records %d == sum of gate operands + scatter rows %d: %s'%(adds,gates,adds==gates))
# ---- (B) own F2 replay of the emitted local programs (forward and reverse), all 955 columns incl. dirt, y_t += x_t
def replay(P):
    val=[1<<i for i in range(n)]; tmp={}
    for z in P:
        op=z[0]
        if op==0: continue
        if op==1: val[z[1]]^=(tmp[z[2]] if z[2]>=n else val[z[2]])
        elif op==2: assert z[2] not in tmp and z[2]>=n; tmp[z[2]]=val[z[1]]
        else: assert tmp[z[2]]==val[z[1]],'erase of a changed centre'; del tmp[z[2]]
    assert not tmp
    ok=all(val[s]==1<<s for s in range(v)) and all(val[v+tt]==(1<<(v+tt))|(1<<tt) for tt in range(v)) and all(val[r]==1<<r for r in range(2*v,n))
    return ok
print('(B) F2 replay of emitted programs on all %d columns (x restored, y_t+=x_t, %d helpers restored): forward %s reverse %s'%(n,R,replay(Tf),replay(Tr)))
# ---- (C) R and live stock from the tape
calls=t['calls']; L,T,m=t['stages'],t['replicas'],t['m']; K=(L-1)//2; DATA=2*K*v*T
Rtape={len(c['owners'])-2*v for c in calls}; maxreg=max(max(z[1],z[2]) for z in Tf if (z[0]!=0 and z[2]<n) or z[0]==0)+0
regs=set()
for z in Tf:
    regs.add(z[1])
    if z[0]!=0 and z[2]<n: regs.add(z[2])
print('(C) R from owners per call:',Rtape,'; registers touched by the local program: %d (%d helpers); word R: %d'%(len(regs),len(regs)-2*v,R))
fam=set()
for c in calls:
    for f,r in c['owners']: fam.add(f)
print('    distinct owner ids used by the 11 calls:',len(fam),'min/max',min(fam),max(fam),' -> live W =',max(fam)+1,'; template live',t['live'],'; DATA=2KVT =',DATA,'; banks',sum(t['banks_per_stage'].values()))
W=max(fam)+1
# ---- (D) hosting windows (own implementation) and residuals
sched=t['schedule']; last={}; seen=[]; win={}; rk={}; pr={}; idx=0
for pos,e in enumerate(sched):
    if e['kind']=='local_cover_sweep': seen.append((pos,e['stage'],e['pair'])); last[e['pair']]=pos
    elif e['kind']=='bridge': last[e['dst']]=pos; last[e['src']]=pos
    elif e['kind']=='idle':
        win[idx]={s for q,s,p in seen if last.get(e['pair'],-1)<q<pos and p!=e['pair']}; rk[idx]=e['rank']; pr[idx]=e['pair']; idx+=1
width=[8-dim[w['start'][r]] for r in range(2*v,n)]
used=defaultdict(set); hosted={}
for i,cp,off,wd,s,hh in t['hosting']['slots']:
    assert s in win[i] and 0<=cp<2*v and wd==width[hh]>0 and off>=0 and off+wd<=rk[i]
    cells=set(range(off,off+wd)); assert not cells&used[i,cp]; used[i,cp]|=cells
    assert (s,hh) not in hosted; hosted[s,hh]=(i,cp,off,wd)
print('(D) own window audit: %d slots, every (stage,helper) hosted once: %s  (L*R = %d); hosted widths = 8 - entrance dim'%(len(hosted),len(hosted)==L*R,L*R))
nbank=0
for c in calls:
    s,rep,p=c['stage'],c['replica'],c['pair']
    for hh,(f,r) in enumerate(c['owners'][2*v:]):
        if (s,hh) in hosted:
            i,cp,off,wd=hosted[s,hh]; side,port=divmod(cp,v)
            assert r==['hosted',i,off,wd] and f==rep*2*K*v+(2*pr[i]+side)*v+port and pr[i]!=p
        else: nbank+=1
    ids=[(f,tuple(r)) for f,r in c['owners']]; assert len(set(ids))==n
print('    all call owners consistent with the slots; bank assignments:',nbank)
# ---- (E) paid profile: local programs x calls + idle remainders
paid=Counter(); loc=Counter()
for c in calls:
    for z in t['local_programs'][c['orientation']]:
        if z[0]==0 and z[4]: loc[z[4]]+=1
        if z[0]==2: loc[z[5]]+=1
paid.update(loc); idle=Counter()
for i in rk:
    if rk[i]:
        for cp in range(2*v):
            r_=rk[i]-len(used[i,cp])
            if r_: idle[r_]+=T
paid.update(idle)
per=Counter()
for z in fwd:
    if z[0]==0 and z[4]: per[z[4]]+=1
    if z[0]==2: per[z[5]]+=1
print('(E) per-call local profile from my own export:',dict(sorted(per.items())))
print('    local part over the %d calls:'%len(calls),dict(sorted(loc.items())),' idle-child remainders:',dict(sorted(idle.items())))
claimP={int(k):x for k,x in claim['bit_profile'].items()}
print('    paid-children profile (mine):   ',dict(sorted(paid.items())))
print('    paid-children profile (claimed):',dict(sorted(claimP.items())),' EQUAL:',paid==Counter(claimP))
mass=sum(r*x for r,x in paid.items()); DEF=T*(2*K*v-9*8*L)
print('    rank mass',mass,'m*W-mass =',m*W-mass,'deficit formula T(2KV-72L) =',DEF,'ok:',m*W-mass==DEF,'; paid calls',sum(paid.values()),'maxchild',max(paid),'; 2*maxchild^3<m^3:',2*max(paid)**3<m**3)
# ---- (F) c by my own moment solve
mp.mp.dps=60
E=sum(paid.values())
def solve(bad):
    fb=mp.mpf(32)*m*E/(mp.mpf(10)**16*W) if bad else mp.mpf(0)
    f=lambda a: sum(mp.mpf(r*x)/(m*W)*(mp.mpf(m)/r)**a for r,x in paid.items())+fb*mp.mpf(m)**a-1
    lo,hi=mp.mpf(0),mp.mpf('0.01')
    assert f(lo)<0<f(hi)
    for _ in range(200):
        mid=(lo+hi)/2
        if f(mid)<0: lo=mid
        else: hi=mid
    return (lo+hi)/2
cb,cn=solve(True),solve(False)
cl=Fr(claim['bit_lower'])
print('(F) bit c, moment equation sum_r (r n_r/(mW)) (m/r)^c + 32mE/(1e16 W) m^c = 1 :')
print('    mine (with inherited envelope) %s ; without %s'%(mp.nstr(cb,15),mp.nstr(cn,15)))
print('    claimed bit_lower %s = %s ; |diff| = %s ; agrees to 1e-24 (the claim is floored at 1e-24): %s'%(claim['bit_lower'],mp.nstr(mp.mpf(cl.numerator)/cl.denominator,15),mp.nstr(abs(cb-mp.mpf(cl.numerator)/cl.denominator),3),abs(cb-mp.mpf(cl.numerator)/cl.denominator)<mp.mpf(10)**-23))
dg=hashlib.sha256()
for c in calls:
    for z in t['local_programs'][c['orientation']]:
        x=[z[0],c['owners'][z[1]]]
        if z[0]==0: x.extend(z[2:])
        else:
            x.append(c['owners'][z[2]] if z[2]<n else [t['live'],['private',0]]); x.extend(z[3:])
        dg.update(json.dumps(x,separators=(',',':')).encode()); dg.update(b'\n')
print('    emitted program digest (mine) %s  claimed %s  match %s'%(dg.hexdigest()[:16],claim['emitted_program_sha256'][:16],dg.hexdigest()==claim['emitted_program_sha256']))
print('    word sha256', hashlib.sha256(open(wordp,'rb').read()).hexdigest()[:16])
