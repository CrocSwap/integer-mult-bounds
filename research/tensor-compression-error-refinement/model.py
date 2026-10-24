"""Independent checker arithmetic for the retained boundary-only finite pages."""
from fractions import Fraction as Q


def need(ok, message):
    if not ok:
        raise ValueError(message)


def inward(x, bits):
    return (-1 if x < 0 else 1)*(abs(x) >> bits)


def records(raw, bits=50):
    need(len(raw) % (2*bits) == 0, 'complete complex records')
    result=[]
    for start in range(0,len(raw),2*bits):
        pair=[]
        for offset in (0,bits):
            word=raw[start+offset:start+offset+bits]
            need(all(b in (0,1) for b in word),'binary signed data')
            v=sum(b << i for i,b in enumerate(word))
            pair.append(v-(1 << bits) if word[-1] else v)
        result.append(tuple(pair))
    return result


def core(values, page):
    """Source selection, two signed solves and normalization at original sites."""
    p,P,n,band=(page[k] for k in ('p','P','m','band'))
    need(len(values)==page['target_length'],'complete target halo')
    result=[]
    for component in (0,1):
        rhs=[values[j][component] << (P-p) for j in page['selection']]
        lower=[]
        for i in range(n):
            dot=sum(a*lower[j] for a,j in zip(page['lower'][i],range(i-band,i)) if j>=0)
            lower.append(inward((rhs[i] << P)-dot,P))
        upper=[0]*n
        for i in range(n-1,-1,-1):
            dot=sum(a*upper[j] for a,j in zip(page['upper'][i][:-1],range(i+1,i+band+1)) if j<n)
            upper[i]=inward(((lower[i] << P)-dot)*page['upper'][i][-1],2*P)
        j=(32*p-1).bit_length()
        start=page['core_offset']
        result.append([inward(upper[i]*page['diagonal'][i],2*P-p+j)
                       for i in range(start,start+page['core_length'])])
    return list(zip(*result))


def line(values, profile):
    result=[None]*profile['s']
    for page,(origin,length),(start,count) in zip(profile['compression_pages'],profile['compression_windows'],profile['cores']):
        need(length==page['target_length'] and count==page['core_length'],'bound core descriptor')
        halo=[values[(origin+i)%profile['t']] for i in range(length)]
        output=core(halo,page)
        for i,v in enumerate(output):
            need(result[start+i] is None,'unique source core')
            result[start+i]=v
    need(all(v is not None for v in result),'complete source partition')
    return result


def axis(data, shape, index, profile):
    rows,columns=shape
    if index==0:
        output=[line([data[i*columns+j] for i in range(rows)],profile) for j in range(columns)]
        return [output[j][i] for i in range(profile['s']) for j in range(columns)],(profile['s'],columns)
    need(index==1,'bounded two-axis checker')
    output=[line(data[i*columns:(i+1)*columns],profile) for i in range(rows)]
    return [v for row in output for v in row],(rows,profile['s'])


def recurrence(initial, error, delta, dimensions):
    """Exact rational illustration; the quantified proof is in PROOF.md."""
    need(0<=initial<=1 and 0<=delta<=Q(1,8) and dimensions>=1,'admitted recurrence')
    radius=initial
    for _ in range(dimensions):
        radius=radius/8+delta
        error=error/8+delta
        need(radius<=1,'local input domain remains admitted')
    return radius,error
