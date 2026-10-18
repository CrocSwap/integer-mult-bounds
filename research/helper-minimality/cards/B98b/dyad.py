"""Dyadic (Z[1/2]) exact synthesis of the end-of-A block state with fewer scratch registers."""
import sys,random
exec(open('synth.py').read().split("tot_save=0")[0])
def split(x):  # Fraction dyadic -> (odd int signed, exp)
    assert x.denominator&(x.denominator-1)==0,x
    n,dn=x.numerator,x.denominator;e=-(dn.bit_length()-1)
    while n and n%2==0:n//=2;e+=1
    return n,e
def synth_dy(rowsv,k,seed=0,maxops=100000):
    rnd=random.Random(seed);n=len(rowsv);cols=sorted({j for r in rowsv for j in r})
    M=[[r.get(j,Q(0)) for j in cols] for r in rowsv];ops=[]
    def addop(t,s,q):
        ops.append(('add',t,s,q));M[t]=[a+q*b for a,b in zip(M[t],M[s])]
    done=[]
    for step in range(k):
        rem=[c for c in range(k) if c not in done]
        if seed: rnd.shuffle(rem)
        best=None
        for c in rem:
            ent=[M[i][c] for i in range(n) if i not in done]
            # row-Euclid on active rows (those whose index not a finished pivot) - lines finished are rows=done cols
            pass
        c=rem[0] if seed else None
        order=rem
        for c in order:
            act=[i for i in range(n) if i not in done and M[i][c]!=0]
            # gcd odd part check without mutating: integer gcd of odd parts
            from math import gcd
            g=0
            for i in act:g=gcd(g,abs(split(M[i][c])[0]))
            if g==1:break
        else: return None
        while True:
            act=[i for i in range(n) if i not in done and M[i][c]!=0]
            if len(act)==1:break
            p=min(act,key=lambda i:(abs(split(M[i][c])[0]),i))
            op,ep=split(M[p][c])
            for i in act:
                if i==p:continue
                oi,ei=split(M[i][c]);m=round(Q(oi,op));
                if m==0:m=1 if (oi>0)==(op>0) else -1
                addop(i,p,-Q(m)*Q(2)**(ei-ep))
        p=act[0]
        if split(M[p][c])[0] not in(1,-1):return None
        # bring into row c (line row c) 
        if p!=c:
            if M[c][c]!=0 or c in done:raise Exception('line row not clear')
            addop(c,p,Q(1));p=c
        q=M[c][c]
        if q!=1:
            ops.append(('scale',c,1/q));M[c]=[x/q for x in M[c]]
        for i in range(n):
            if i!=c and M[i][c]!=0:addop(i,c,-M[i][c])
        done.append(c)
    # after pivots, remaining nonpivot rows must be zero and line rows identity (up to cross terms removed)
    for i in range(n):
        for j in range(k):assert M[i][j]==(1 if i==j else 0),(i,j,M[i][j])
    fw=[('add',o[1],o[2],-o[3]) if o[0]=='add' else ('scale',o[1],1/o[2]) for o in reversed(ops)]
    return fw,cols
def verify2(fw,cols,rowsv):
    k=len(cols);n=len(rowsv);R=[[Q(1) if i==j else Q(0) for j in range(k)] if i<k else [Q(0)]*k for i in range(n)]
    for o in fw:
        if o[0]=='add':R[o[1]]=[a+o[3]*b for a,b in zip(R[o[1]],R[o[2]])]
        else:R[o[1]]=[o[2]*a for a in R[o[1]]]
    return all(R[i]==[r.get(j,Q(0)) for j in cols] for i,r in enumerate(rowsv))
if __name__=='__main__':
    good=['(0, 2, 4, 6)','(0, 2, 5, 7)','(1, 2, 4, 7)','(1, 2, 5, 6)','(1, 3, 4, 6)','(1, 3, 5, 7)','(2, 3, 4, 5)','(2, 3, 6, 7)','(4, 5, 6, 7)']
    tot=0
    for bn in good:
        regs=blocks[bn];S_=set(regs)
        keep=src('B',S_)|src('tail',S_)|src('cut',S_)|src('compensation',S_)|src('cleanup',S_)|{e[2] for e in d['A'] if e[0]=='add' and e[2] in S_ and e[1] not in S_ and e[1]>=v or (e[0]=='add' and e[2] in S_ and e[1]<v and e[1] not in sorted({j for r in regs for j in rows[r]}))}
        cols=sorted({j for r in regs for j in rows[r]})
        rv=[rows[r] for r in cols+sorted(keep)]
        best=None
        for seed in range(6):
            o=synth_dy(rv,8,seed)
            if o and verify2(o[0],o[1],rv):
                if best is None or len(o[0])<len(best[0]):best=o
        drop=sorted(S_-keep);sv=sum(psi[r] for r in drop)
        if best:
            mx=max(abs(o[3]) if o[0]=='add' else abs(o[2]) for o in best[0]);mn=min((abs(o[3]) if o[0]=='add' else abs(o[2])) for o in best[0])
            print(bn,'DYADIC OK keep',len(keep),'drop',len(drop),'ops',len(best[0]),'coef range',mn,mx,'psi_saved',round(sv,1));tot+=sv
        else:print(bn,'no dyadic found keep',len(keep))
    print('sum psi saved',round(tot,1),'= w9-equiv',round(tot/(9*math.log(73/9)),1))
