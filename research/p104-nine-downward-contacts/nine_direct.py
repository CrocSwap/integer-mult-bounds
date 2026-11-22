"""Find the exact source of a minimum-cardinality direct-to-zero feedback transcript."""
from collections import Counter, defaultdict
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys


def basis(rows):
    b={}
    for x in rows:
        while x:
            n=x.bit_length()-1
            if n not in b:b[n]=x;break
            x^=b[n]
    return b


def reduce(b,x):
    for n in sorted(b,reverse=True):
        if x>>n&1:x^=b[n]
    return x


def run(path):
    raw=Path(path).read_bytes();assert sha256(raw).hexdigest()=='74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326'
    src=gzip.decompress(raw);assert sha256(src).hexdigest()=='b096d6df2a0c4688296b13ab0cfd50fec1c7dec732819c624ddd7a745a144b69';g=json.loads(src)
    n=g['public'];dims={int(i):r['dim'] for i,r in g['frames'].items()};chart=dict(enumerate(g['start']));v={i:1<<i for i in chart};h=defaultdict(list);snapshots={};F=[]
    for i,c in chart.items():h[c].append(v[i])
    for clock,(op,d,*a) in enumerate(g['program']):
        if op=='MOVE':
            s,t=a;assert chart[d]==s;chart[d]=t
            if dims[s]<dims[t]:h[t].append(v[d])
            if t==0:F.append(v[d])
        elif op=='INIT':assert d not in chart;chart[d],v[d]=a[0],0
        elif op=='ADD':s,c=a;assert chart[d]==chart[s]==c;v[d]^=v[s]
        elif op=='SWAP':s,=a;chart[d],chart[s]=chart[s],chart[d];v[d],v[s]=v[s],v[d]
        elif op=='CLEAR':assert chart.pop(d)==a[0];del v[d]
        else:raise ValueError(op)
        if clock in (11104,18875):snapshots[clock]={c:tuple(xs) for c,xs in h.items()}
    assert len(F)==9 and chart==dict(enumerate(g['final'])) and len(h[0])==516
    result=[]
    for k,m in ((11104,0),(18875,8)):
        at=snapshots[k];z=basis(at[0]+tuple(F[:m]));assert len(z)==516+m
        fb=basis(reduce(z,f) for f in F);assert len(fb)==9-m
        full_rank=[];donors={};fingerprint=sha256()
        for c in sorted(dims):
            H=basis(reduce(z,x) for x in at.get(c,()));both=basis(list(H.values())+list(fb.values()));inter=len(H)+len(fb)-len(both)
            assert inter==(9-m if c==1 else 0)
            for row in (c,len(H),len(both),inter):fingerprint.update(f'{row} '.encode())
            if inter:donors[c]=inter
            if inter==len(fb):full_rank.append(c)
        assert full_rank==[1]
        # Zero public coordinates do not join the grant when m changes. The original nine receipts stay independent.
        assert len(basis(at[0]+tuple(F)))==525
        result.append({'inclusive_native_clock':k,'fixed_chart0_information_rank':len(z),'remaining_target_quotient_rank':len(fb),'charts_checked':len(dims),'lower_charts_having_zero_common_rank':len(dims)-1,'sender_nonzero_intersections':donors,'all_combined_ranks_fingerprint_sha256':fingerprint.hexdigest()})
    return {'source_sha256':sha256(raw).hexdigest(),'word_public_inputs':n,'direct_contacts_into_zero':9,'required_sender':1,'paid_dimension_difference_per_contact':8,'frozen_upward_contact_count':sum(1 for row in g['program'] if row[0]=='MOVE' and dims[row[2]]<dims[row[3]]),'deadline_grants':result}

if __name__=='__main__':print(json.dumps(run(sys.argv[1]),sort_keys=True,indent=2))
