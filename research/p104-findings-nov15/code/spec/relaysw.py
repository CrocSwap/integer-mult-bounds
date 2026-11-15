# R2 class (c): RELAY frames on #7617. For every pinned transfer j->i at a relay frame F (window as BIG/RELAY pin.py),
# test the SANDWICH condition for any fresh-register (clean-ancilla-must-uncompute) network, j the only holder of its row:
# exists t1<td<t2 in the window with chart_j(t1) <= chart_i(td) <= chart_j(t2) (subspace order), F removed from i and j
# (their F-stay may sit at prev or next chart). Parks (owned, stationary): chart_j(t1) == chart_i(td), t1<td.
import gzip,json,collections as C,math,sys,heapq
W=json.load(gzip.open('../../ATTACK/STACK7616/best7616.json.gz','rt'))
NP=W['public'];NO=W['owned_fields'];P=W['program'];live=W['live'];H=W['hosted']
mains=set(live)|{r+112 for r in live}|set(H['X2'])|set(H['Y2'])
fixed=lambda r:r>=NP or r in mains
dim=[len(b) for b in W['frames']]
def span(b):
    s={0}
    for v in b:s|={x^v for x in s}
    return frozenset(s)
SP=[span(b) for b in W['frames']]
le=lambda a,b:SP[a]<=SP[b]
f=lambda r:r*math.log(r) if r>0 else 0.0
def evframe(e):
    if e[0] in('ADD','COPY'):return e[4]
    if e[0]=='SCALE':return e[3]
    if e[0] in('INIT','CLEAR'):return e[2]
ch={r:[(W['initial'][r],-1)] for r in range(NP)}
for i,e in enumerate(P):
    if e[0]=='MOVE' and e[1]<NP:ch[e[1]].append((e[3],i))
fixedF=set()
for r in mains:
    for fr,_ in ch[r]:fixedF.add(fr)
for e in P:
    fr=evframe(e)
    if fr is not None and (fixed(e[1]) or (e[0] in('ADD','COPY') and fixed(e[2]))):fixedF.add(fr)
stops=C.defaultdict(list)
for h in range(NP):
    if h in mains:continue
    c=ch[h]
    for k in range(1,len(c)-1):stops[c[k][0]].append((h,c[k][1],c[k+1][1],c[k-1][0],c[k+1][0]))
relay=sorted(F for F in stops if F not in fixedF)
gain={F:sum(f(dim[s[4]]-dim[s[3]])-f(dim[F]-dim[s[3]])-f(dim[s[4]]-dim[F]) for s in stops[F]) for F in relay}
print('relay frames',len(relay),'stops',sum(len(stops[F]) for F in relay),'total gain D0/call %.1f'%sum(gain.values()))
endF=C.Counter()
for r in range(NP):
    if r not in mains:
        if W['initial'][r] in gain:endF[W['initial'][r]]+=1
        if W['final'][r] in gain:endF[W['final'][r]]+=1
byreg=C.defaultdict(list)
for t,e in enumerate(P):
    if e[0] in('ADD','COPY'):byreg[e[1]].append(t);byreg[e[2]].append(t)
    elif e[0]!='MOVE':byreg[e[1]].append(t)
ST=C.defaultdict(list);cur=list(W['initial'])+[None]*NO;start=[0]*(NP+NO)
for t,e in enumerate(P):
    if e[0]=='MOVE':ST[e[1]].append((start[e[1]],t,cur[e[1]]));cur[e[1]]=e[3];start[e[1]]=t
for r in range(NP):ST[r].append((start[r],len(P),cur[r]))
def vstays(r,F):
    out=[];L=ST[r]
    for k,(a,b,G) in enumerate(L):
        if G==F and 0<k<len(L)-1:out+= [(a,b,L[k-1][2]),(a,b,L[k+1][2])]
        else:out.append((a,b,G))
    return out
def sandwich(i,j,lo,hi,F,park=False):
    Si=[(max(a,lo),min(b,hi),u) for a,b,u in vstays(i,F) if u!=F and min(b,hi)>max(a,lo)]
    Sj=[(max(a,lo),min(b,hi),z) for a,b,z in vstays(j,F) if z!=F and min(b,hi)>max(a,lo)]
    for a,b,u in Si:
        if park:
            if any(z==u and za<b for za,zb,z in Sj):return True
            continue
        e1=[za for za,zb,z in Sj if le(z,u)];e2=[zb for za,zb,z in Sj if le(u,z)]
        if e1 and e2:
            t1=min(e1);t2=max(e2)
            # need t1<td<t2 with td in (a,b)
            if max(a,t1)<min(b,t2):return True
    return False
stat=C.Counter();frames=[]
for F in relay:
    hs={s[0] for s in stops[F]};allok=True;allpark=True;npin=0
    for t in sorted({t for h in hs for t in byreg[h] if evframe(P[t])==F}):
        e=P[t]
        if e[0]!='ADD':continue
        i,j=e[1],e[2]
        def isblk(u):
            o=P[u]
            if evframe(o)==F or o[0]!='ADD':return False
            return (o[1]==j and o[2]!=i) or (o[2]==i and o[1]!=j)
        before=[u for u in byreg[i]+byreg[j] if u<t and isblk(u)];after=[u for u in byreg[i]+byreg[j] if u>t and isblk(u)]
        lo=max(before) if before else -1;hi=min(after) if after else len(P)
        co=False
        for a,b,G in ST[i]:
            if G==F or b<=lo or a>=hi:continue
            if any(z==G and za<min(b,hi) and zb>max(a,lo) for za,zb,z in ST[j]):co=True;break
        if co:stat['not pinned']+=1;continue
        npin+=1;s=sandwich(i,j,lo,hi,F);p=sandwich(i,j,lo,hi,F,park=True)
        stat[('pinned','sandwich' if s else 'no-sandwich','park' if p else 'no-park')]+=1
        allok&=s;allpark&=p
    frames.append((F,gain[F],npin,allok,allpark,endF[F]))
print(dict(stat))
ok=[x for x in frames if x[3]];okp=[x for x in frames if x[4]]
print('frames all-pinned sandwich-feasible',len(ok),'gain %.1f'%sum(x[1] for x in ok),'(of which F is no helper endpoint:',sum(1 for x in ok if x[5]==0),'gain %.1f)'%sum(x[1] for x in ok if x[5]==0))
print('frames all-pinned park-feasible',len(okp),'gain %.1f'%sum(x[1] for x in okp))
print('frames with 0 pinned transfers',sum(1 for x in frames if x[2]==0))
json.dump(frames,open('relaysw.json','w'))
