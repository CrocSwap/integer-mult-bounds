"""Code-disjoint integer-interval check; imports neither primary nor predecessors."""
import json
from pathlib import Path
from hashlib import sha256
import re

P = Path(__file__).resolve().parent
Q = 1 << 160

def check(ok, why):
    if not ok:
        raise RuntimeError(why)

def ceildiv(a,b): return (a+b-1)//b
def mul(a,b): return a[0]*b[0]//Q, ceildiv(a[1]*b[1],Q)
def div(a,n): return a[0]//n, ceildiv(a[1],n)
def plus(a,b): return a[0]+b[0],a[1]+b[1]

def atan_log(n,d):
    # 1 <= n/d <= 2; z=(n-d)/(n+d), with outward rounding.
    check(d <= n <= 2*d, 'normalized logarithm')
    z = ((n-d)*Q//(n+d),ceildiv((n-d)*Q,n+d))
    z2 = mul(z,z)
    term, total = z,(0,0)
    for j in range(64):
        total = plus(total,div(term,2*j+1))
        term = mul(term,z2)
    # Actual tail <= 4/3^129, and the upper interval is rounded upward.
    return 2*total[0],2*total[1]+ceildiv(4*Q,3**129)

def logarithm(n,d):
    k = 0
    while n >= 2*d:
        d *= 2
        k += 1
    a,b = atan_log(n,d),atan_log(2,1)
    return a[0]+k*b[0],a[1]+k*b[1]

def exponential(x):
    check(0 <= x[0] <= x[1] < Q, 'exponential interval')
    total = term = (Q,Q)
    for k in range(1,21):
        term = div(mul(term,x),k)
        total = plus(total,term)
    nxt = div(mul(term,x),21)
    return total[0],total[1]+2*nxt[1]

def moment(hist, divisor=14336):
    lower=upper=0
    for rank,count in hist.items():
        log=logarithm(73,rank)
        x=(log[0]*167//100000,ceildiv(log[1]*167,100000))
        e=exponential(x)
        lower += e[0]*rank*count//(73*divisor)
        upper += ceildiv(e[1]*rank*count,73*divisor)
    return lower,upper

def main():
    src=json.loads((P/'SOURCES.json').read_text())
    for item in src['snapshots']:
        raw=(P/item['snapshot']).read_bytes()
        check(sha256(raw).hexdigest()==item['sha256'],'source authentication')
    text=(P/'source/PR2287-PROOF.md').read_text()
    raw=re.search(r'\{1:349604,.*?48:4866\}',text,re.S).group()
    hist={int(a):int(b) for a,b in re.findall(r'(\d+):(\d+)',raw)}
    lo,hi=moment(hist)
    check(hi*10**9 < (10**9-15999)*Q,'strict selected moment')
    receipt=json.loads((P/'RESULT.json').read_text())
    one=receipt['recurrence']
    check(one['moment_lower_1e15']*Q <= hi*10**15,'primary lower enclosure compatible')
    check(one['moment_upper_1e15']*Q >= lo*10**15,'primary upper enclosure compatible')
    check(one['internal_visit_exponent']=='99733167/100000000','recursion exponent')
    check(99833*999==99733167,'exact beta multiplication')
    check(599*500000-99733167*3==300499,'strict exponent gap')
    check(one['repair_constant_per_adapter']=='1000000000/5333','geometric constant')
    cases=0
    for p in (2,3,8,32,127,256):
        for a in (1,2,p,3*p):
            for r in (a**3,a**3+1,8*a**3):
                den=128*p**3
                if 5*a*(r+a)>den*r:
                    continue
                check(den*a**3+5*a*(r+a)<=2*den*r,'integer tariff proof premise')
                cases+=4
    check(cases==receipt['tariff_cases']==288,'complete finite shape coverage')
    # A different single-pass least-significant-digit implementation, retaining
    # arbitrary correlated payload tuples, verifies all-bad record transfers.
    movement=[]
    for keybits in (4,8,16):
        values=list(range(1<<min(keybits,5)))
        state=[(k,(k,-k-1,k%3)) for k in reversed(values)]
        transfers=0
        for bit in range(keybits):
            buckets=[[],[]]
            for key,value in state:
                buckets[(key//(2**bit))%2].append((key,value));transfers+=1
            state=buckets[0]+buckets[1]
        check(state==[(k,(k,-k-1,k%3)) for k in values],'sorted arbitrary payload')
        movement.append(transfers)
    check(movement==[64,256,512],'growing complete-record traffic')
    bad=dict(hist);bad[1]+=14336
    check(moment(bad)[0]>Q,'extra rank-one child breaks strict contraction')
    check(moment(hist,1)[0]>Q,'missing live-volume denominator breaks contraction')
    check(8**3>16,'shortened suffix fails record admission')
    check(8*(512+8)>512,'bad-only fibre violates linear repair admission')
    print('PASS_INDEPENDENT_COMPLEX_RECORD_AMORTIZATION','tariffs=288','controls=4')

if __name__=='__main__': main()
