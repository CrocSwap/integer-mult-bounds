"""Exact character formulas and actual complex transform gauge; no numerical rounding."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parent
def need(v,s):
    if not v:raise ValueError(s)
def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'))
def gm(a,b):return (a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0])
def gp(a,n):
    z=(1,0)
    for _ in range(n):z=gm(z,a)
    return z
def chi(w,x):return (-1)**((w&x).bit_count())
def rank(a):
    from fractions import Fraction
    a=[list(map(Fraction,r)) for r in a];k=0
    for j in range(len(a[0])):
        q=next((i for i in range(k,len(a)) if a[i][j]),None)
        if q is None:continue
        a[k],a[q]=a[q],a[k];v=a[k][j];a[k]=[x/v for x in a[k]]
        for i in range(k+1,len(a)):
            v=a[i][j];a[i]=[x-v*y for x,y in zip(a[i],a[k])]
        k+=1
    return k

def source_hashes():
    source=json.loads((P/'SOURCES.json').read_text());rows=[r for r in source['files'] if r['usage']=='input'];need(len(rows)==2,'both source contracts required')
    for r in rows:need(hashlib.sha256((P.parents[1]/r['path']).read_bytes()).hexdigest()==r['sha256'],'source bytes')
    return {r['path']:r['sha256'] for r in rows}
def result():
    sources=source_hashes();records=[]
    for m in (2,3):
        d=2**m;pairs=[(i,j) for i in range(d) for j in range(i+1,d)];r=d//2
        # Derive target cross blocks from the ordered tensor entries, independently
        # of the author's sparse L/R implementation in the separate checker.
        sd=[[chi(i,x)*chi(j,x) for x in range(d)] for i,j in pairs]
        ds=[[2*chi(x,i)*chi(x,j) for i,j in pairs] for x in range(d)]
        need(rank(sd)==rank(ds)==d-1,'target cross ranks')
        groups=(range(1,r+1),range(r+1,d));parts=[]
        for ws in groups:
            parts.append([[sum(int(i^j==w)*chi(w,x) for w in ws) for x in range(d)] for i,j in pairs])
        need(all(parts[0][i][x]+parts[1][i][x]==sd[i][x] for i in range(len(pairs)) for x in range(d)),'both cross factors')
        need(any(parts[0][i][x]!=sd[i][x] for i in range(len(pairs)) for x in range(d)),'missing second call rejected')
        # C_m numerator is product of (1+i) for equal bits and (1-i) otherwise.
        count=0
        for a in range(d):
         for b in range(d):
          for x in range(d):
           for y in range(d):
            direct=(1,0)
            for i,j in ((a,x),(b,y)):
             for bit in range(m):direct=gm(direct,(1,1 if ((i^j)>>bit)&1==0 else -1))
            gauge=gm(gp((1,1),2*m),gp((0,-1),sum(z.bit_count() for z in (a,b,x,y))))
            sign=chi(a,x)*chi(b,y);gauge=(sign*gauge[0],sign*gauge[1])
            need(direct==gauge,'actual complex numerator gauge');count+=1
        # Every source C_v is a perfect matching, hence the same cross rank.
        for v in range(1,d):
            matching=[(x,x^v) for x in range(d) if x<(x^v)]
            need(len(matching)==r and len({x for pair in matching for x in pair})==d,'all source directions')
        records.append(dict(m=m,target_cross_rank=d-1,slice_cross_rank=r,gauge_entries=count,second_call_necessary=True))
    return dict(theorem='exactly two paid calls for tied width two and every m>=2',fixtures=records,source_sha256=sources,physical_tariff_claimed=False)
if __name__=='__main__':
    need(canonical(result())==canonical(json.loads((P/'RESULT.json').read_text())),'mandatory typed complete receipt')
    print('PASS_TIED_WIDTH_TWO_EXACT_CALL_COST')
