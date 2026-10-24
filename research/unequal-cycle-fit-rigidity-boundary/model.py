"""Exact finite corroboration; the universal theorem is in PROOF.md."""
from fractions import Fraction as Q
from itertools import product

def need(x, message):
    if not x:
        raise ValueError(message)

def rank(a):
    a=[[Q(x) for x in row] for row in a]; r=0
    for j in range(len(a[0]) if a else 0):
        pivot=next((i for i in range(r,len(a)) if a[i][j]),None)
        if pivot is None: continue
        a[r],a[pivot]=a[pivot],a[r]; q=a[r][j]
        a[r]=[v/q for v in a[r]]
        for i in range(len(a)):
            if i!=r:
                q=a[i][j]; a[i]=[x-q*y for x,y in zip(a[i],a[r])]
        r+=1
        if r==len(a): break
    return r

def inspect(m,d):
    n=len(d); s=sum(d); need(len(m)==s and all(len(row)==s for row in m),'shape')
    offsets=[0]
    for x in d: offsets.append(offsets[-1]+x)
    blocks={}
    for i,j in product(range(n),repeat=2):
        b=[row[offsets[j]:offsets[j+1]] for row in m[offsets[i]:offsets[i+1]]]
        if i==j: need(all(b[u][v]==int(u==v) for u,v in product(range(d[i]),repeat=2)),'diagonal')
        elif (i-j)%n not in (1,n-1): need(all(x==0 for row in b for x in row),'forbidden block')
        blocks[i,j]=rank(b)
    alpha=max(sum(d[i] for i in range(n) if mask>>i&1) for mask in range(1<<n)
              if all(not(mask>>i&1 and mask>>((i+1)%n)&1) for i in range(n)))
    return {'widths':d,'rank':rank(m),'minimum_rank':max(alpha,(s+1)//2),
            'edge_ranks_forward':[blocks[i,(i+1)%n] for i in range(n)],
            'edge_ranks_reverse':[blocks[(i+1)%n,i] for i in range(n)]}

def gram(v):
    return [[Q(sum(x*y for x,y in zip(a,b)),sum(x*x for x in a)) for b in v] for a in v]

def witness():
    g=gram([(1,0,0),(1,1,-1),(0,1,0),(0,1,1),(1,0,1)])
    ports=[(0,0),(1,0),(2,0),(3,0),(3,1),(4,0),(4,1)]
    return [[g[i][j] if a==b==0 else Q(a==b==1) for j,b in ports] for i,a in ports]

def canonical(x,p=None):
    n=len(x); p=p or [0]*n
    ports=[[(('edge',i-1 if i else n-1),j) for j in range(x[i-1])]+
           [(('edge',i),j) for j in range(x[i])]+
           [(('private',i),j) for j in range(p[i])] for i in range(n)]
    labels=sum(ports,[])
    return [[Q(a==b) for b in labels] for a in labels],[len(a) for a in ports]

def mul(a,b):
    return [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]

def run():
    m=witness(); d=[1,1,1,2,2]; w=inspect(m,d)
    need(w['rank']==w['minimum_rank']==4,'positive optimum')
    need(w['edge_ranks_forward']==w['edge_ranks_reverse']==[1,1,1,2,1],'all edges')
    need(2*sum(w['edge_ranks_forward'])>sum(d),'channel obstruction')
    z=inspect(gram([(1,0),(1,1),(0,1)]),[1,1,1,0,0])
    need(z['rank']==z['minimum_rank']==2,'zero-width optimum')
    need(z['edge_ranks_forward'][:2]==[1,1],'zero obstruction')
    examples=[]
    for x in ([1,0,1,0,1],[2,1,3,0,2],[1,0,2,1,3,1,2],[0]*5):
        a,widths=canonical(x); rec=inspect(a,widths)
        need(rec['rank']==sum(x)==sum(widths)//2,'half tight')
        need(mul(a,a)==[[2*v for v in row] for row in a],'quadratic identity')
        examples.append(rec)
    # All positive unequal total-six profiles are the rotations of this one.
    six=[]
    for i in range(5):
        widths=[1]*5; widths[i]=2
        candidates=[x for x in product(range(3),repeat=5) if all(x[j-1]+x[j]==widths[j] for j in range(5))]
        need(len(candidates)==1,'unique edge dimensions')
        a,got=canonical(candidates[0]); need(got==widths,'dimensions')
        r=inspect(a,widths); need(r['minimum_rank']==r['rank']==3,'total six');six.append(list(candidates[0]))
    controls=[]
    bad=[row[:] for row in m];bad[0][2]=Q(1)
    try: inspect(bad,d)
    except ValueError as e: need(str(e)=='forbidden block','wrong rejection');controls.append('nonedge rejected')
    else: raise ValueError('nonedge accepted')
    bad=[row[:] for row in m];bad[0][0]=Q(2)
    try: inspect(bad,d)
    except ValueError as e: need(str(e)=='diagonal','wrong rejection');controls.append('diagonal rejected')
    else: raise ValueError('diagonal accepted')
    need(mul(m,m)!=[[2*v for v in row] for row in m],'slack falsely half tight');controls.append('half-total premise necessary')
    need(not all(zv>0 for zv in z['widths']),'zero admitted as positive');controls.append('positive/zero distinction')
    # Independent row scaling is not local similarity: it breaks diagonal fitting.
    bad=[row[:] for row in m];bad[0]=[2*v for v in bad[0]]
    try: inspect(bad,d)
    except ValueError: controls.append('row-only gauge rejected')
    else: raise ValueError('row-only gauge accepted')
    # Real nontrivial scalar local similarity preserves every ordered block rank.
    scales=[Q(2),Q(3),Q(5),Q(7),Q(7),Q(11),Q(11)]
    gauge=[[v*scales[i]/scales[j] for j,v in enumerate(row)] for i,row in enumerate(m)]
    need(inspect(gauge,d)==w,'local similarity invariant');controls.append('local similarity ranks retained')
    return {'claim':'universal proof in PROOF.md; finite exact corroboration only',
            'positive':w,'zero_width':z,'total_six_edge_dimensions':six,
            'half_tight_examples':examples,'controls':controls,
            'positive_matrix':[[str(v) for v in row] for row in m]}
