"""Explicit bounded-fanin realization; classical X, CNOT and Toffoli only.

Borrowed-bit decomposition credits Barenco et al. quant-ph/9503016 Lemma7.2.
No relative-phase replacements. All borrowed bits are restored locally.
"""
def addition(src,dst,inverse=False,extend=False):
    sources=list(enumerate(src))+([(len(src),src[-1])]if extend else [])
    gates=[(tuple([(s,1)]+[(dst[z],1)for z in range(j,k)]),dst[k])for j,s in sources for k in range(len(dst)-1,j-1,-1)]
    return gates[::-1]if inverse else gates

def negation(dst):
    return [((),t)for t in dst]+[(tuple((dst[z],1)for z in range(k)),dst[k])for k in range(len(dst)-1,-1,-1)]

def swap(a,c):
    return [g for x,y in zip(a,c)for g in [(((x,1),),y),(((y,1),),x),(((x,1),),y)]]

def half(y,a,c,d,subtract=False,reverse=False,clean=False):
    g=addition(a,d,extend=True)+addition(c,d,subtract,True)+addition(d[1:],y,reverse)
    g+=addition(c,d,not subtract,True)+addition(a,d,True,True)
    if not clean:
        g+=addition(d[1:],y,not reverse)
        parity=[(tuple([(d[0],1),(a[0],which),(c[0],1-which)]+[(y[z],0)for z in range(k)]),y[k])for k in range(len(y)-1,-1,-1)for which in [0,1]]
        g+=parity[::-1]if reverse else parity
    return g

def pair_gates(b,inverse=False,clean=False):
    ar=list(range(b));ai=list(range(b,2*b));cr=list(range(2*b,3*b));ci=list(range(3*b,4*b));d=list(range(4*b,5*b+1))
    g=addition(cr,ar,True)+addition(ci,ai,True)
    if inverse:g+=swap(ar,ai)+negation(ai)
    g+=half(cr,ar,ai,d,reverse=inverse,clean=clean)+half(ci,ai,ar,d,True,inverse,clean)
    if not inverse:g+=swap(ar,ai)+negation(ar)
    return g+addition(cr,ar)+addition(ci,ai)

def apply(state,gates):
    for controls,target in gates:
        if all((state>>c&1)==v for c,v in controls):state^=1<<target
    return state

def lower(gate,total_bits):
    controls,target=gate; aa=[c for c,v in controls]; n=len(aa)
    if len(set(aa+[target]))!=n+1:raise ValueError('aliased gate controls')
    xs=[((),c)for c,v in controls if not v]
    if n<=2:return xs+[(tuple((c,1)for c in aa),target)]+xs[::-1]
    dd=[x for x in range(total_bits)if x not in aa and x!=target][:n-2]
    if len(dd)!=n-2:raise ValueError('insufficient dirty spectators')
    A=(((aa[0],1),(aa[1],1)),dd[0])
    chain=[(((dd[j-1],1),(aa[j+1],1)),dd[j])for j in range(1,n-2)]
    F=chain+ [(((dd[-1],1),(aa[-1],1)),target)] +chain[::-1]
    return xs+F+[A]+F+[A]+xs[::-1]

def bill(gates):
    out={'X':0,'CNOT':0,'Toffoli':0,'generalized':len(gates),'max_controls':0}
    for controls,t in gates:
        n=len(controls);out['max_controls']=max(out['max_controls'],n)
        out['X']+=2*sum(v==0 for c,v in controls)
        if n<3:out[('X','CNOT','Toffoli')[n]]+=1
        else:out['Toffoli']+=4*n-8
    return out

def macro_bill(b,clean=False):
    p=bill(pair_gates(b,clean=clean));n=bill(negation(list(range(b))))
    # Full source L/R routing:2512 real swaps and1024 real negations.
    return {key:1280*p[key]+(2512*3*b if key=='CNOT'else 0)+1024*n[key]for key in ['X','CNOT','Toffoli']}
