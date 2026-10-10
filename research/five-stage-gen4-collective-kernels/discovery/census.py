import sys, json, struct, collections, itertools
from fractions import Fraction
D = sys.argv[1]
meta = json.load(open(D+'/meta.json')); frames = json.load(open(D+'/frames.json')); init = {int(k):v for k,v in json.load(open(D+'/initial.json')).items()}
n, v, ZERO, FULL = meta['n'], meta['v'], meta['ZERO'], meta['FULL']
cats = meta['category_names']; readcat = cats.index('dirty_read')
ev = list(struct.iter_unpack('<6i', open(D+'/records.bin','rb').read()))
gauge = {int(k) for k in meta['gauge']}
dimf = {int(k):fr['dim'] for k,fr in frames.items()}
helpers = [s for s in range(2*v, n) if init[s]==ZERO and s not in gauge]
H = set(helpers)
# targets as sources before anything? chronology of target use
tsrc = [i for i,e in enumerate(ev) if e[0]==1 and v<=e[2]<2*v]
print('ADDs with a target as source: ', len(tsrc), 'first at', tsrc[0] if tsrc else None, 'cats', collections.Counter(cats[ev[i][5]] for i in tsrc))
reads = collections.defaultdict(list); touch = {}; firstframe = {}; badsrc = set()
for i,e in enumerate(ev):
    op,a,b,c,f,z = e
    if op==1:
        if z==readcat and b in H and f==ZERO and v<=a<2*v and c%2:
            reads[b].append((i,a))
        else:
            for s in (a,b):
                if s in H and s not in touch: touch[s]=i; firstframe[s]=f
            if b in H and z==readcat: badsrc.add(b)
    elif op==2:
        if a in H and a not in touch: touch[a]=i; firstframe[a]=c
    elif op==0:
        pass
print('plain helpers', len(helpers), 'with reads', len(reads), 'bad reads', len(badsrc))
ok = [s for s in helpers if s in reads and s in touch and reads[s][-1][0] < touch[s]]
print('helpers whose reads all precede their first touch:', len(ok), 'read-count hist', sorted(collections.Counter(len(reads[s]) for s in ok).items())[:15])
print('first-frame dim hist', sorted(collections.Counter(dimf[firstframe[s]] for s in ok).items()))
# gap between last read and first touch (records)
gaps = [touch[s]-reads[s][-1][0] for s in ok]; print('gap last-read->first-touch: min', min(gaps), 'median', sorted(gaps)[len(gaps)//2], 'max', max(gaps))
resp = collections.defaultdict(list)
for s in ok:
    key = tuple(sorted(a for cnt,a in collections.Counter(a for i,a in reads[s]).items() if cnt%2)) if False else tuple(sorted(a for a,cnt in collections.Counter(a for i,a in reads[s]).items() if cnt%2))
    resp[key].append(s)
twins = {k:ss for k,ss in resp.items() if len(ss)>1}
print('distinct responses', len(resp), 'twin classes', len(twins), 'class size hist', sorted(collections.Counter(len(ss) for ss in twins.values()).items()))
print('response size hist', sorted(collections.Counter(len(k) for k in resp).items())[:10])
# F2 nullity of all ok responses
def f2rank(vecs):
    basis={}
    for x in vecs:
        while x:
            h=x.bit_length()-1
            if h in basis: x^=basis[h]
            else: basis[h]=x; break
    return len(basis)
vec = {s: sum(1<<(a-v) for a in k) for k,ss in resp.items() for s in ss}
r=f2rank(list(vec.values())); print('response matrix rank', r, 'nullity', len(ok)-r)
def rref(rows):
    M=[[Fraction(x) for x in r] for r in rows]; piv=[]; r=0
    for c in range(len(M[0]) if M else 0):
        p=next((i for i in range(r,len(M)) if M[i][c]),None)
        if p is None: continue
        M[r],M[p]=M[p],M[r]; pv=M[r][c]; M[r]=[x/pv for x in M[r]]
        for i in range(len(M)):
            if i!=r and M[i][c]: m=M[i][c]; M[i]=[x-m*y for x,y in zip(M[i],M[r])]
        piv.append(c); r+=1
    return M[:r],piv
def intersect(f1,f2):
    B1=frames[str(f1)]['B']; A2=frames[str(f2)]['A']
    if not B1: return []
    if not A2: return [[Fraction(x) for x in b] for b in B1]
    M=[[sum(a[k]*b[k] for k in range(24)) for b in B1] for a in A2]
    R,piv=rref(M)
    free=[j for j in range(len(B1)) if j not in piv]; out=[]
    for fj in free:
        l=[Fraction(0)]*len(B1); l[fj]=Fraction(1)
        for row,pc in zip(R,piv): l[pc]=-row[fj]
        out.append([sum(l[i]*B1[i][k] for i in range(len(B1))) for k in range(24)])
    return out
def gnorm(u): return 9*sum(x*x for x in u)-sum(u)**2
def line(vecs):
    R,_=rref(vecs) if vecs else ([],[])
    if not R: return None
    d=len(R)
    def member(u): M,_=rref(R+[u]); return len(M)==d
    for i in range(24):
        for j in range(i+1,24):
            u=[0]*24; u[i]=1; u[j]=-1
            if member([Fraction(x) for x in u]) and gnorm(u)!=0: return ('e_i-e_j',i,j)
    for row in R:
        if gnorm(row)!=0: return ('generic',[str(x) for x in row])
    return None
pairs=[]; stats=collections.Counter(); nocut=0
for key,ss in twins.items():
    used=set()
    for a,b in itertools.combinations(sorted(ss),2):
        if a in used or b in used: continue
        cut=max(reads[a][-1][0],reads[b][-1][0])
        if cut>=min(touch[a],touch[b]): nocut+=1; stats['no common cut']+=1; continue
        I=intersect(firstframe[a],firstframe[b]); L=line(I); stats[(len(I), L[0] if L else None)]+=1
        if L: pairs.append(dict(a=a,b=b,cut=cut,first_a=firstframe[a],first_b=firstframe[b],dima=dimf[firstframe[a]],dimb=dimf[firstframe[b]],dim_intersection=len(I),line=L,targets=list(key))); used.update((a,b))
print('pair census:', sorted(stats.items(), key=lambda x:-x[1])[:15])
print('TWIN PAIRS with common cut and nondegenerate common line:', len(pairs), 'kinds', collections.Counter(p['line'][0] for p in pairs), 'by dims', sorted(collections.Counter((p['dima'],p['dimb']) for p in pairs).items()))
json.dump(dict(pairs=pairs, ok=len(ok), twin_classes=len(twins), nullity=len(ok)-r), open(D+'/census2.json','w'))
# target-prefix: at several cut times, nullity of target responses (over all dirty-read sources, all helpers incl. gauges)
tr=[0]*v; cuts=[]; allreads=[i for i,e in enumerate(ev) if e[0]==1 and e[5]==readcat]
marks=set(allreads[int(len(allreads)*q)-1] for q in (0.1,0.25,0.5,0.75,0.9,1.0))
bitof={s:1<<(s-2*v) for s in range(2*v,n)}
for i,e in enumerate(ev):
    op,a,b,c,f,z=e
    if op==1 and z==readcat and v<=a<2*v and c%2: tr[a-v]^=bitof[b]
    if i in marks:
        nz=[x for x in tr if x]; rk=f2rank(nz); cuts.append((i,len(nz),rk,len(nz)-rk))
print('target response (nonzero targets, rank, nullity) at read-quantile cuts:', cuts)
