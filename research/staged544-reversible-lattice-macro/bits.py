"""Literal ancilla-free generalized-controlled-X circuit simulator.

Each counted step flips one bit under a conjunction of other bits (positive
or negative controls). This is an explicit gate alphabet, NOT a Toffoli count.
Arbitrary controlled-X decomposition into the supplier's native gates is open.
"""
def add(y,x,b,width=None,extend=False,inverse=False):
    width=b if width is None else width
    sources=[(j,j)for j in range(b)]+([(b,b-1)]if extend else [])
    gates=[(j,k,s)for j,s in sources for k in range(width-1,j-1,-1)]
    if inverse:gates.reverse()
    for j,k,s in gates:
        mask=((1<<(k-j))-1)<<j
        if (x>>s&1)and y&mask==mask:y^=1<<k
    return y,len(gates)

def parity_decrement(y,a,c,d,b,reverse=False):
    gates=[(k,which)for k in range(b-1,-1,-1)for which in [0,1]]
    if reverse:gates.reverse()
    for k,which in gates:
        control=(d&1)and ((a&1)==which)and ((c&1)==1-which)
        if control and y&((1<<k)-1)==0:y^=1<<k
    return y,len(gates)

def half(y,a,c,d,b,subtract=False,reverse=False,clean=False):
    """Circuit sequence has one target and one preserved dirty/clean scratch."""
    n=0
    d,k=add(d,a,b,b+1,True);n+=k
    d,k=add(d,c,b,b+1,True,subtract);n+=k
    y,k=add(y,d>>1,b,inverse=reverse);n+=k
    d,k=add(d,c,b,b+1,True,not subtract);n+=k
    d,k=add(d,a,b,b+1,True,True);n+=k
    if not clean:
        y,k=add(y,d>>1,b,inverse=not reverse);n+=k
        y,k=parity_decrement(y,a,c,d,b,reverse);n+=k
    return y,d,n

def negate(x,b):
    x^=(1<<b)-1
    # Add constant one: one positive/negative-controlled flip per output bit.
    for k in range(b-1,-1,-1):
        mask=(1<<k)-1
        if x&mask==mask:x^=1<<k
    return x,2*b

def swap(a,c,b):
    # Three CNOT gates per pair of distinct bits, shown literally by XOR.
    a^=c;c^=a;a^=c
    return a,c,3*b

def pair(x,y,d,b,inverse=False,clean=False):
    ar,ai=x;cr,ci=y;n=0
    ar,k=add(ar,cr,b,inverse=True);n+=k
    ai,k=add(ai,ci,b,inverse=True);n+=k
    if inverse:
        ar,ai,k=swap(ar,ai,b);n+=k
        ai,k=negate(ai,b);n+=k
    cr,d,k=half(cr,ar,ai,d,b,reverse=inverse,clean=clean);n+=k
    ci,d,k=half(ci,ai,ar,d,b,subtract=True,reverse=inverse,clean=clean);n+=k
    if not inverse:
        ar,ai,k=swap(ar,ai,b);n+=k
        ar,k=negate(ar,b);n+=k
    ar,k=add(ar,cr,b);n+=k
    ai,k=add(ai,ci,b);n+=k
    return (ar,ai),(cr,ci),d,n
