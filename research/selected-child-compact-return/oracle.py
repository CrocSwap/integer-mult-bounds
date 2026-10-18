"""Independent direct Gaussian operator, separate from sequential primitives."""
def add(a,b): return a[0]+b[0],a[1]+b[1]
def mul(a,b): return a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]
def phase(a,k):
    x,y=a
    return ((x,y),(-y,x),(-x,-y),(y,-x))[k%4]

def monomial(r,x):
    n=len(r['matrix_rows'])
    y=r['offset'] ^ sum(((row&x).bit_count()%2)<<j for j,row in enumerate(r['matrix_rows']))
    e=r['phase']+sum(r['linear_Z4'][j] for j in range(n) if x>>j&1)
    e+=2*sum(1 for i in range(n) for j in range(i+1,n) if x>>i&1 and x>>j&1 and r['quadratic_rows'][i]>>j&1)
    return y,e%4

def columns(recipe):
    out=[]
    for x in range(1<<len(recipe['right']['matrix_rows'])):
        p,e=monomial(recipe['right'],x);col={}
        for flip in (0,1):
            y,f=monomial(recipe['left'],p^flip)
            col[y]=add(col.get(y,(0,0)),phase((1,-1 if flip else 1),e+f))
        out.append({y:z for y,z in col.items() if z!=(0,0)})
    return out

def tensor_columns(single):
    return [{y0+16*y1:mul(a,b) for y0,a in single[x%16].items()
             for y1,b in single[x//16].items()} for x in range(256)]

def apply(values,layout,cols,outer_rows):
    """Dense oracle only; physical code never calls this indexed scatter."""
    out=[(0,0)]*len(values)
    for row in range(outer_rows):
        for index in range(layout.records):
            state=layout.decode(index)
            x=sum(((state['v'+str(j)]>>k)&1)<<(j+4*k) for j in range(4) for k in range(2))
            for y,c in cols[x].items():
                target=dict(state)
                for j in range(4): target['v'+str(j)]=sum(((y>>(j+4*k))&1)<<k for k in range(2))
                at=row*layout.records+layout.encode(target)
                out[at]=add(out[at],mul(c,values[row*layout.records+index]))
    if any(v%4 for z in out for v in z): raise ValueError('oracle exact grid')
    return [tuple(v//4 for v in z) for z in out]

def axis(values,bits,position):
    mask=1<<(bits-position-1)
    out=[]
    for i,a in enumerate(values):
        z=add(mul((1,1),a),mul((1,-1),values[i^mask]))
        if any(v%2 for v in z): raise ValueError('oracle axis exact grid')
        out.append(tuple(v//2 for v in z))
    return out
