# R2 class (a): split jobs on #7617 (BIG/LEAKPARK c7617.pkl). Sandwich lemma => a fresh-register network can supply the
# G-pure row e_g at (F,t) only from g's row-clean windows (before its first write, after its last write) at charts z1<=F<=z2,
# at network cost >= f(z2-z1)-f(F-z1)-f(z2-F) (one fresh helper z1->F->z2; 0 if z1==F or z2==F). Upper bound on the
# class: per helper, best over its jobs of tau(a,b) - that cost (ignores the column network, c.d pairing, pool rules).
import gzip,json,pickle,math,collections as C
W=json.load(gzip.open('../../ATTACK/STACK7616/best7616.json.gz','rt'));n=W['public'];P=W['program']
dim=[len(b) for b in W['frames']]
def span(b):
    s={0}
    for v in b:s|={x^v for x in s}
    return frozenset(s)
SP=[span(b) for b in W['frames']]
f=lambda r:r*math.log(r) if r>0 else 0.0
tau=lambda a,b:f(a+b)-f(a)-f(b)
path={r:[(W['initial'][r],-1)] for r in range(n)};fw={};lw={};fr={};lrd={}
for i,e in enumerate(P):
    if e[0]=='MOVE' and e[1]<n:path[e[1]].append((e[3],i))
    elif e[0] in('ADD','COPY','SCALE') and e[1]<n:fw.setdefault(e[1],i);lw[e[1]]=i
    if e[0] in('ADD','COPY') and e[2]<n:fr.setdefault(e[2],i);lrd[e[2]]=i
def chart_at(r,t):
    c=path[r][0][0]
    for ch,i in path[r]:
        if i<=t:c=ch
    return c
D=pickle.load(open('../../BIG/LEAKPARK/c7617.pkl','rb'));J=D['J']
best={};best1={};cnt=C.Counter()
for j in J:
    F=j['F'];g0=tau(j['a'],j['b'])
    for g in j['helpers']:
        early=[c for c,i in path[g] if i<fw.get(g,10**9)];late=[c for c,i in path[g] if i>=0 and i>=lw.get(g,-1)]+[chart_at(g,lw.get(g,-1))]
        # row-clean charts (early: before first write; late: from last write on)
        z1s=[c for c in early if SP[c]<=SP[F]];z2s=[c for c in late if SP[F]<=SP[c]]
        if not z1s or not z2s:cnt['no clean bracket']+=1;continue
        z1=max(z1s,key=lambda c:dim[c]);z2=min(z2s,key=lambda c:dim[c])
        cost=0.0 if (z1==F or z2==F) else f(dim[z2]-dim[z1])-f(dim[F]-dim[z1])-f(dim[z2]-dim[F])
        net=g0-cost;cnt['bracket']+=1
        if cost==0:cnt['free bracket (g row-clean at F)']+=1
        if net>1e-9:cnt['net>0']+=1
        if net>best.get(g,(0,))[0]:best[g]=(net,F,dim[z1],dim[F],dim[z2],j['a'],j['b'])
print(dict(cnt));print('helpers with net>0',len(best),'sum of best nets (D0/call, upper bound) %.2f'%sum(v[0] for v in best.values()))
print(sorted(best.values(),reverse=True)[:8])
# column-clean windows (dual): before first read, after last read
cc=C.Counter()
for j in J:
    F=j['F']
    for g in j['helpers']:
        early=[c for c,i in path[g] if i<fr.get(g,10**9)];late=[c for c,i in path[g] if i>=lrd.get(g,-1)]+[chart_at(g,lrd.get(g,-1))]
        cc[(any(c==F for c in early),any(c==F for c in late))]+=1
print('column-clean at F (early,late):',dict(cc))
# joint bound: need BOTH the row bracket (row-clean windows) and the column bracket (column-clean windows: before first
# read, after last read); network cost >= max(cost_row, cost_col) (generous: one network serving both).
def br(g,F,a_t,b_t):
    early=[c for c,i in path[g] if i<a_t];late=[c for c,i in path[g] if i>=0 and i>=b_t]+[chart_at(g,b_t)]
    z1s=[c for c in early if SP[c]<=SP[F]];z2s=[c for c in late if SP[F]<=SP[c]]
    if not z1s or not z2s:return None
    z1=max(z1s,key=lambda c:dim[c]);z2=min(z2s,key=lambda c:dim[c])
    return 0.0 if (z1==F or z2==F) else f(dim[z2]-dim[z1])-f(dim[F]-dim[z1])-f(dim[z2]-dim[F])
bj={};cj=C.Counter()
for j in J:
    F=j['F'];g0=tau(j['a'],j['b'])
    for g in j['helpers']:
        cr=br(g,F,fw.get(g,10**9),lw.get(g,-1));cc_=br(g,F,fr.get(g,10**9),lrd.get(g,-1))
        if cr is None or cc_ is None:cj['missing bracket']+=1;continue
        net=g0-max(cr,cc_);cj['both']+=1
        if net>1e-9:
            cj['net>0']+=1
            if net>bj.get(g,(0,))[0]:bj[g]=(net,F,j['a'],j['b'],round(cr,2),round(cc_,2))
print('JOINT',dict(cj),'helpers',len(bj),'sum %.2f D0/call'%sum(v[0] for v in bj.values()));print(sorted(bj.values(),reverse=True)[:10])
