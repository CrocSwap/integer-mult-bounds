"""Finite-state reversible implementation of the actual C pair; no floating point.

Chris R / Clear1nsight, substantial OpenAI Codex assistance. Apache-2.0.
The real-word modular arithmetic primitives below are the stated cost model,
not an unreported implementation in native gates or recursive child tariff.
"""
def signed(x,b):
    return x-(1<<b) if x>>(b-1)&1 else x

def half_accumulate(y,a,c,d,b,subtract=False,reverse=False,omit_carry=False):
    """y += floor((signed(a) +/- signed(c))/2), restoring arbitrary dirty d.

    y,a,c have b bits; d has b+1 bits. Seven reversible arithmetic primitives:
    four scratch adds/subtracts, two shifted target adds/subtracts, one
    parity-controlled decrement. Sources a,c are unchanged, even when d wraps.
    """
    m=(1<<b)-1; dm=(1<<(b+1))-1
    aa=signed(a,b); cc=(-1 if subtract else 1)*signed(c,b)
    direction=-1 if reverse else 1
    d=(d+aa)&dm; d=(d+cc)&dm
    y=(y+direction*(d>>1))&m
    d=(d-cc)&dm; d=(d-aa)&dm
    y=(y-direction*(d>>1))&m
    if not omit_carry:y=(y-direction*((d&1)&((a^c)&1)))&m
    return y,d

def pair(x,y,d,b,inverse=False,omit_carry=False):
    """C or inverse C approximation: two complex b-bit words; one dirty word.

    Exact inverse as a finite permutation on all 2^(5b+1) states.
    Numerical C approximation requires the separately stated no-wrap bound.
    """
    m=(1<<b)-1; ar,ai=x; cr,ci=y
    ar=(ar-cr)&m; ai=(ai-ci)&m
    if inverse:ar,ai=ai,(-ar)&m
    cr,d=half_accumulate(cr,ar,ai,d,b,reverse=inverse,omit_carry=omit_carry)
    ci,d=half_accumulate(ci,ai,ar,d,b,subtract=True,reverse=inverse,omit_carry=omit_carry)
    if not inverse:ar,ai=(-ai)&m,ar
    ar=(ar+cr)&m; ai=(ai+ci)&m
    return (ar,ai),(cr,ci),d

def phase(z,p,b=None):
    a,c=z; out=((a,c),(-c,a),(-a,-c),(c,-a))[p%4]
    return tuple(q&((1<<b)-1) for q in out) if b is not None else out

def decode(rec):
    rows=rec['matrix_rows']; q=rec['quadratic_rows']; alpha=rec['linear_Z4']
    perm=[]; ph=[]
    for x in range(512):
        bits=[i for i in range(9)if x>>i&1]
        perm.append(sum(((x&r).bit_count()%2)<<j for j,r in enumerate(rows))^rec['offset'])
        ph.append((rec['phase']+sum(alpha[i]for i in bits)+2*sum((q[i]>>j)&1 for i in bits for j in bits if i<j))%4)
    if len(set(perm))!=512:raise ValueError('nonbijective monomial')
    return perm,ph

def monomial(v,rec,b=None,inverse=False):
    perm,ph=decode(rec); out=[None]*512
    for x,y in enumerate(perm):
        if inverse:out[x]=phase(v[y],-ph[x],b)
        else:out[y]=phase(v[x],ph[x],b)
    return out

def macro(v,d,b,recipe,inverse=False):
    """Actual serialized rank5 L C_[5] R; spectator multiplicity handled outside.

    The reference Python list allocation is a simulator, not claimed hardware
    scratch. The proof's in-place monomial cycle realization is separately billed.
    """
    v=monomial(v,recipe['left']if inverse else recipe['right'],b,inverse)
    axes=range(4,-1,-1) if inverse else range(5)
    for j in axes:
        for x in range(512):
            if not x>>j&1:v[x],v[x^(1<<j)],d=pair(v[x],v[x^(1<<j)],d,b,inverse)
    return monomial(v,recipe['right']if inverse else recipe['left'],b,inverse),d

def exact_macro(v,recipe):
    """Independent exact Gaussian numerator action, denominator 2^5."""
    v=monomial(v,recipe['right'])
    for j in range(5):
        out=[]
        for x,(a,b) in enumerate(v):
            c,d=v[x^(1<<j)]
            out.append((a-b+c+d,b+a+d-c))
        v=out
    return monomial(v,recipe['left'])

def routing_bill(rec):
    perm,ph=decode(rec); seen=set();cycles=[]
    for x in range(512):
        if x in seen:continue
        c=[];y=x
        while y not in seen:seen.add(y);c.append(y);y=perm[y]
        cycles.append(c)
    return {'complex_swaps':sum(len(c)-1 for c in cycles),'real_swaps':2*sum(len(c)-1 for c in cycles)+sum(p%2 for p in ph),'real_negations':sum((0,1,2,1)[p]for p in ph),'phase_histogram':[ph.count(p)for p in range(4)],'cycles':len(cycles)}
