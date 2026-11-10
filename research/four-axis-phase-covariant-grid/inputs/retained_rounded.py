"""Fixed-grid Gaussian calls and literal ports; JoyboyBrian, Codex assistance."""


def need(ok,why):
    if not ok:raise ValueError(why)


def half_even(n):
    q=n>>1
    return q+((n&1)&(q&1))


def checkword(n,width):
    need(type(n) is int and -(1<<(width-1))<=n<(1<<(width-1)),'signed word overflow')
    return n


def call(v,f,axis,width,adjoint=False,trace=None):
    need(type(f) is int and f>=1 and axis in (0,2) and len(v)==8**f,'literal Gaussian call dimensions')
    need(type(width) is int and width>=2,'word width')
    for z in v:
        need(len(z)==2,'complex pair')
        for value in z:checkword(value,width)
    trace=trace if trace is not None else {}
    for j in range(f):
        bit=3*j+axis; step=1<<bit
        for block in range(0,len(v),2*step):
            for low in range(step):
                x=block+low;y=x+step;a,b=v[x];c,d=v[y]
                sr,si=checkword(a+c,width),checkword(b+d,width)
                dr,di=checkword(a-c,width),checkword(b-d,width)
                nums=(sr+di,si-dr,sr-di,si+dr) if adjoint else (sr-di,si+dr,sr+di,si-dr)
                for n in nums:checkword(n,width)
                trace['peak_numerator']=max(trace.get('peak_numerator',0),*(abs(n)for n in nums))
                trace['rounding_events']=trace.get('rounding_events',0)+sum(n&1 for n in nums)
                trace['butterflies']=trace.get('butterflies',0)+1
                out=tuple(half_even(n)for n in nums);v[x]=out[:2];v[y]=out[2:]
    return v


def letters(name):
    need(name in ('P','Q','W','M'),'literal monomial')
    perm=[];phase=[]
    for x in range(8):
        swap=(x&4)|((x&1)<<1)|((x&2)>>1)
        if name=='P':y=x^(4 if x&1 else 0); q=x.bit_count()+y.bit_count()
        elif name=='Q':y=swap;q=x.bit_count()+y.bit_count()
        elif name=='W':y=x;q=2*((x&5).bit_count()%2)
        else:y=swap;q=2*((y>>1)&1)
        perm.append(y);phase.append(q%4)
    return perm,phase


def rotate(z,q):
    a,b=z
    return ((a,b),(-b,a),(-a,-b),(b,-a))[q]


def route(name,f,inverse=False):
    p,q=letters(name)
    if inverse:
        back=[0]*8;ph=[0]*8
        for x,y in enumerate(p):back[y]=x;ph[y]=-q[x]%4
        p,q=back,ph
    out=[]
    for x in range(8**f):
        y=z=0
        for j in range(f):
            a=(x>>(3*j))&7;y|=p[a]<<(3*j);z+=q[a]
        out.append((y,z%4))
    return out


def monomial(v,name,f,width,inverse=False):
    routing=route(name,f,inverse); seen=bytearray(len(v))
    for start in range(len(v)):
        if seen[start]:continue
        x=start;saved=v[x]
        while True:
            seen[x]=1;y,q=routing[x];following=v[y]
            v[y]=tuple(checkword(z,width) for z in rotate(saved,q));x=y;saved=following
            if x==start:break
    # These are owned control fields, explicitly returned zero after use.
    for i in range(len(seen)):seen[i]=0;routing[i]=(0,0)


def mix(t,y,f,width,sign):
    for name,coefficient in [('P',1),('Q',2)]:
        monomial(t,name,f,width)
        for i,((a,b),(c,d)) in enumerate(zip(t,y)):
            ca=checkword(a if coefficient==1 else a<<1,width);cb=checkword(b if coefficient==1 else b<<1,width)
            y[i]=(checkword(c+sign*ca,width),checkword(d+sign*cb,width))
        monomial(t,name,f,width,True)


def port(x,y,f,kind,reverse,width,capture=False):
    need(kind in (2,3),'two or three calls')
    if capture:x=list(x);y=list(y)
    trace={};cuts=[]
    def paid(v,axis,adj=False):
        before=list(v) if capture else None
        call(v,f,axis,width,adj,trace)
        if capture:cuts.append((axis,adj,before,list(v)))
    if reverse:
        if kind==3:
            monomial(y,'M',f,width,True);paid(y,2,True);monomial(y,'W',f,width,True)
        paid(y,0,True);mix(x,y,f,width,-1);paid(x,0,True)
    else:
        paid(x,0);mix(x,y,f,width,1);paid(y,0)
        if kind==3:monomial(y,'W',f,width);paid(y,2);monomial(y,'M',f,width)
    return x,y,trace,cuts


def request_bits(P,f,kind,reverse):
    need(type(P) is int and P>=0 and type(f) is int and f>=1 and kind in (2,3),'accuracy domain')
    if reverse:external=(f+1)//2+2 if kind==2 else f+2
    else:external=f+3 if kind==2 else (3*f+1)//2+3
    return P+external+(f+1)//2+1


def signed_width(H,P,f,kind,reverse):
    need(type(H) is int and H>=0,'magnitude domain')
    return H+request_bits(P,f,kind,reverse)+2*f+(f+1)//2+9
