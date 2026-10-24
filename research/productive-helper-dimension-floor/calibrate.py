"""Finite calibration of the standard Lagrangian rank convention; not a proof for all dimensions.

Prepared with OpenAI Codex assistance; Apache-2.0.
"""
def need(value,message):
    if not value:raise ValueError(message)

def span(rows):
    result={0}
    for row in rows:result|={x^row for x in tuple(result)}
    return frozenset(result)

def basis(rows):
    pivots={}
    for value in rows:
        for bit in sorted(pivots,reverse=True):
            if value&(1<<bit):value^=pivots[bit]
        if value:
            bit=value.bit_length()-1
            for k in list(pivots):
                if pivots[k]&(1<<bit):pivots[k]^=value
            pivots[bit]=value
    return tuple(pivots[k] for k in sorted(pivots,reverse=True))

def all_lagrangians(n):
    mask=(1<<n)-1
    def pairing(a,b):return (((a&mask)&(b>>n)).bit_count()+((b&mask)&(a>>n)).bit_count())%2
    layer={()}
    for k in range(n):
        nxt=set()
        for rows in layer:
            old=span(rows)
            for v in range(1,1<<(2*n)):
                if v not in old and all(pairing(v,x)==0 for x in rows):nxt.add(basis((*rows,v)))
        layer=nxt
    return sorted(layer)

def calibrate():
    results=[]
    for n,count in [(1,3),(2,15),(3,135)]:
        charts=all_lagrangians(n);need(len(charts)==count,'complete small Lagrangian count')
        mask=(1<<n)-1;heights=[len(basis(x&mask for x in L)) for L in charts]
        zero=tuple(1<<j for j in range(n,2*n))
        for L,k in zip(charts,heights):need(len(basis((*L,*zero)))-n==k,'projection height equals distance to vertical')
        for L,k in zip(charts,heights):
            for M,l in zip(charts,heights):
                distance=len(basis((*L,*M)))-n
                need(distance>=abs(k-l),'arbitrary phase chart projection lower bound')
        results.append({'dimension':n,'lagrangians':len(charts),'ordered_pairs':len(charts)**2})
    return results
