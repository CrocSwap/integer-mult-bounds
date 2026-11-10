"""Conserve pair sums with a reversible nearest Gaussian grid map.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""

def need(ok, why):
    if not ok:
        raise ValueError(why)


def center(real, imag):
    """Choose a phase-covariant minimum-norm parity center."""
    if (real ^ imag) & 1 == 0:
        return 0, 0
    if real & 1:
        return (1 if real > 0 else -1), 0
    return 0, (1 if imag > 0 else -1)


def pair(x, y, width, sign=1, trace=None):
    need(type(width) is int and width >= 2 and type(sign) is int and sign in (-1, 1), 'Pair format')
    need(len(x) == len(y) == 2, 'Gaussian pair')
    trace = trace if trace is not None else {}
    def word(value):
        need(type(value) is int and -(1 << (width-1)) <= value < (1 << (width-1)), 'Signed word overflow')
        trace['checked_values'] = trace.get('checked_values', 0)+1
        trace['peak_integer'] = max(trace.get('peak_integer', 0), abs(value))
        return value
    a,b=map(word,x);c,d=map(word,y)
    sr,si=word(a+c),word(b+d)
    dr,di=word(a-c),word(b-d)
    cr,ci=center(sr,si)
    tr,ti=cr+sign*ci,ci-sign*cr
    nr=word(word(sr-sign*di)+tr)
    ni=word(word(si+sign*dr)+ti)
    need(nr & 1 == ni & 1 == 0, 'Exact pair halves')
    first=word(nr >> 1),word(ni >> 1)
    second=word(sr-first[0]),word(si-first[1])
    trace['butterflies']=trace.get('butterflies',0)+1
    trace['nonzero_roundings']=trace.get('nonzero_roundings',0)+int(bool(cr or ci))
    trace['data_additions']=trace.get('data_additions',0)+10
    trace['data_half_shifts']=trace.get('data_half_shifts',0)+2
    return first,second


def layer(values, bit, width, sign=1, trace=None):
    need(type(bit) is int and bit >= 0 and len(values)>0 and len(values)&(len(values)-1)==0
         and (1 << bit)<len(values), 'Layer dimensions')
    step=1 << bit
    for base in range(0,len(values),2*step):
        for low in range(step):
            left,right=base+low,base+low+step
            values[left],values[right]=pair(values[left],values[right],width,sign,trace)
    return values


def call(values, f, axis, width, adjoint=False, trace=None):
    need(type(f) is int and f >= 1 and type(axis) is int and axis in (0,2)
         and len(values)==8**f and type(adjoint) is bool, 'Literal Gaussian call dimensions')
    stages=range(f-1,-1,-1) if adjoint else range(f)
    for stage in stages:
        layer(values,3*stage+axis,width,-1 if adjoint else 1,trace)
    return values
