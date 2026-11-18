"""Use the optimum ring matching with a phase-covariant parity choice.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
Adapted from PR7696's ring map. Layer and call structure follows PR6509.
"""

def need(value, message):
    if not value:
        raise ValueError(message)


def partner(point, trace):
    """Match doubled half-grid coordinates without variable division."""
    x,y=point
    r=max(abs(x),abs(y))
    need(x%2==y%2==1, 'Half-grid parity')
    if y==r and x>-r:
        j=(r-x)//2
    elif x==-r and y>-r:
        j=r+(r-y)//2
    elif y==-r and x<r:
        j=2*r+(x+r)//2
    else:
        j=3*r+(y+r)//2
    j=j^1
    if j<r:
        result=(r-2*j,r)
    elif j<2*r:
        offset=j-r;result=(-r,r-2*offset)
    elif j<3*r:
        offset=j-2*r;result=(-r+2*offset,-r)
    else:
        offset=j-3*r;result=(r,-r+2*offset)
    trace['peak_index']=max(trace.get('peak_index',0),j)
    return result


def pair(x,y,width,sign=1,trace=None):
    need(type(width) is int and width>=2 and type(sign) is int and sign in (-1,1), 'Pair format')
    need(len(x)==len(y)==2, 'Gaussian pair')
    trace=trace if trace is not None else {}
    limit=1 << (width-1)
    for value in (*x,*y):
        need(type(value) is int and -limit<=value<limit, 'Signed input range')
    a,b=x;c,d=y;sx,sy=a+c,b+d;dx,dy=a-c,b-d
    mixed=(sx-sy)%2
    if not mixed:
        ex,ey=-sign*dy,sign*dx
    else:
        tx,ty=(dx-dy,-dx-dy) if sign==1 else (dx+dy,dx-dy)
        if sx%2:
            px,py=partner((tx,ty),trace)
        else:
            px,py=partner((-ty,tx),trace)
            px,py=py,-px
        if sign==1:
            ex,ey=(px+py)//2,(px-py)//2
        else:
            ex,ey=(px-py)//2,-(px+py)//2
    need((sx-ex)%2==(sy-ey)%2==0, 'Exact output halves')
    out=((sx+ex)//2,(sy+ey)//2,(sx-ex)//2,(sy-ey)//2)
    for value in out:
        need(-limit<=value<limit, 'Signed output range')
    trace['butterflies']=trace.get('butterflies',0)+1
    trace['nonzero_roundings']=trace.get('nonzero_roundings',0)+mixed
    trace['stored_range_checks']=trace.get('stored_range_checks',0)+8
    return out[:2],out[2:]


def layer(values,bit,width,sign=1,trace=None):
    need(type(bit) is int and bit>=0 and len(values)>0 and len(values)&(len(values)-1)==0 and (1<<bit)<len(values), 'Layer dimensions')
    step=1<<bit
    for base in range(0,len(values),2*step):
        for low in range(step):
            left,right=base+low,base+low+step
            values[left],values[right]=pair(values[left],values[right],width,sign,trace)
    return values


def call(values,f,axis,width,adjoint=False,trace=None):
    need(type(f) is int and f>=1 and type(axis) is int and axis in (0,2) and len(values)==8**f and type(adjoint) is bool, 'Literal Gaussian call dimensions')
    for stage in (range(f-1,-1,-1) if adjoint else range(f)):
        layer(values,3*stage+axis,width,-1 if adjoint else 1,trace)
    return values
