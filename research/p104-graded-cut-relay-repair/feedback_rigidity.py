"""Exact native feedback rigidity with arbitrary terminal decoding. Standard library only."""
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations
import json
import gzip
from pathlib import Path
import sys

COMPRESSED='74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326'
EXPANDED='b096d6df2a0c4688296b13ab0cfd50fec1c7dec732819c624ddd7a745a144b69'


def bits(x):
    while x:
        l=x&-x;yield l.bit_length()-1;x^=l


class Echelon:
    def __init__(self,rows=()):
        self.rows={}
        for r in rows:self.add(r)

    def add(self,r):
        while r:
            p=r.bit_length()-1
            if p not in self.rows:self.rows[p]=r;return
            r^=self.rows[p]

    def residue(self,r):
        for p in sorted(self.rows,reverse=True):
            if r>>p & 1:r^=self.rows[p]
        return r

    def separator(self,r):
        res=self.residue(r)
        if not res:return None
        z=res&-res
        for p,u in sorted(self.rows.items()):
            if (z&u).bit_count()%2:z|=1<<p
        assert (z&r).bit_count()%2==1
        return z


def forward(g,indices):
    n=g['public'];low=(1<<n)-1;ch=dict(enumerate(g['start']));v={i:1<<i for i in ch};stock=defaultdict(list)
    for i,c in ch.items():stock[c].append(v[i])
    before={};payload={};dirty=0
    for k,(op,d,*a) in enumerate(g['program']):
        if op=='MOVE':
            assert ch[d]==a[0]
            if k in indices:
                before[k]={c:tuple(row&low for row in vals) for c,vals in stock.items()};payload[k]=v[d]&low
                v[d]^=1<<(n+indices[k])
            ch[d]=a[1];stock[a[1]].append(v[d])
        elif op=='INIT':assert d not in ch;ch[d],v[d]=a[0],0
        elif op=='ADD':s,c=a;assert ch[d]==ch[s]==c;v[d]^=v[s]
        elif op=='SWAP':s,=a;v[d],v[s]=v[s],v[d];ch[d],ch[s]=ch[s],ch[d]
        elif op=='CLEAR':assert d>=n and ch.pop(d)==a[0];dirty+=bool(v.pop(d)&low)
        else:raise ValueError(op)
    assert ch==dict(enumerate(g['final'])) and dirty==3433
    assert [v[i]&low for i in range(n)]==[(1<<i)^((1<<(i-111)) if 111<=i<222 else 0) for i in range(n)]
    assert all(len(Echelon(row&low for row in rows).rows)==len(rows) for rows in stock.values())
    return stock,before,payload,v


def reverse(g,indices):
    n=g['public'];ch=dict(enumerate(g['final']));v={i:1<<i for i in ch};out={}
    for k in range(len(g['program'])-1,-1,-1):
        op,d,*a=g['program'][k]
        if op=='CLEAR':assert d not in v;ch[d]=a[0];v[d]=0
        elif op=='INIT':assert ch.pop(d)==a[0];del v[d]
        elif op=='ADD':s,c=a;assert ch[d]==ch[s]==c;v[s]^=v[d]
        elif op=='SWAP':s,=a;v[d],v[s]=v[s],v[d];ch[d],ch[s]=ch[s],ch[d]
        elif op=='MOVE':
            assert ch[d]==a[1]
            if k in indices:out[k]=v[d]
            ch[d]=a[0]
        else:raise ValueError(op)
    assert ch==dict(enumerate(g['start']))
    return out


def local_truth_table(n,v,output_mask):
    # Every Boolean perturbation of this small stock can be tested directly.
    size=1<<n;permitted=0
    for perturbation in range(1<<size):
        answer={};works=True
        for w in range(size):
            shifted=w^(v if perturbation>>w&1 else 0);wanted=(w&output_mask).bit_count()%2
            if shifted in answer and answer[shifted]!=wanted:works=False;break
            answer[shifted]=wanted
        iff=all((perturbation>>w & 1)==(perturbation>>(w^v) & 1) for w in range(size))
        assert works==iff;permitted+=works
    assert permitted==1<<(size//2)
    return permitted


def run(path):
    data=Path(path).read_bytes();assert sha256(data).hexdigest()==COMPRESSED
    raw=gzip.decompress(data);assert sha256(raw).hexdigest()==EXPANDED;g=json.loads(raw)
    n=g['public'];low=(1<<n)-1;dims={int(c):s['dim'] for c,s in g['frames'].items()};p=g['program']
    indices={k:i for i,k in enumerate(k for k,r in enumerate(p) if r[0]=='MOVE' and dims[r[2]]>dims[r[3]])};assert len(indices)==27
    stock,before,payload,outputs=forward(g,indices);reverse_noise=reverse(g,indices);res=[];checked=0;hash_probes=sha256()
    for k,bit in indices.items():
        _,owner,src,dst=p[k];grade=dims[src]-dims[dst];sig=sum(1<<o for o,r in outputs.items() if r>>(n+bit)&1)
        assert sig==reverse_noise[k] and sig;affected={g['final'][o] for o in bits(sig)};assert len(affected) in (55,63)
        tiny=sorted(c for c in affected if len(stock[c])==3)
        a,b=next((a,b) for a,b in combinations(tiny,2) if len(Echelon(r&low for r in stock[a]+stock[b]).rows)==6)
        witnesses=[]
        for c in (a,b):
            row=next(o for o in bits(sig) if g['final'][o]==c);u=outputs[row]&low;forms=[r&low for r in stock[c]];shift=sum(((r>>(n+bit))&1)<<j for j,r in enumerate(stock[c]));outmask=next(mask for mask in range(8) if (forms[0] if mask&1 else 0)^(forms[1] if mask&2 else 0)^(forms[2] if mask&4 else 0)==u)
            assert (shift&outmask).bit_count()%2==1;tables=local_truth_table(3,shift,outmask)
            witnesses.append({'chart':c,'odd_public_output':row,'observations':3,'native_output_mask':outmask,'shift_mask':shift,'recoverable_nonlinear_boolean_functions_out_of_256':tables})
        previous=before[k];f=payload[k];assert Echelon(previous[src]).residue(f)==0
        # Setting this logical receipt to zero makes each observed field native XOR tag times f.
        # This supplies entire donor and receiver histories, including all later arrivals.
        suppressed={c:tuple((r&low)^(f if r>>(n+bit)&1 else 0) for r in rows) for c,rows in stock.items()}
        base=Echelon(suppressed[dst]);assert Echelon(suppressed[src]).residue(f)==0
        cases=0
        for c,dim in sorted(dims.items()):
            if abs(dim-dims[dst])>=grade:continue  # grant even incomparable projectors of the right dimensions
            supply=suppressed.get(c,());sp=Echelon();sp.rows=base.rows.copy()
            for r in supply:sp.add(r)
            q=sp.separator(f);assert q is not None and all((q&r).bit_count()%2==0 for r in suppressed[dst]+supply)
            hash_probes.update(f'{k} {c} {q:x}\n'.encode());cases+=1
        checked+=cases;res.append({'clock':k,'owner':owner,'source':src,'destination':dst,'grade':grade,'odd_terminal_charts':len(affected),'independent_stock_rank':6,'witness_pair':witnesses,'cheaper_dimensions_tested':cases})
    assert Counter(x['odd_terminal_charts'] for x in res)==Counter({55:15,63:12})
    return {'source_sha256':COMPRESSED,'expanded_sha256':EXPANDED,'source_pr':8027,'source_head':'fb9b6a7b0d27da1cf98430893a3016bf811e2aa4','native_feedback_positions':27,'cheaper_sender_cases_even_without_nesting':checked,'positive_native_senders':27,'stock_overgrant':'entire suppressed native transcript of each endpoint, including future receipts','separators_fingerprint_sha256':hash_probes.hexdigest(),'certificate':res}

if __name__=='__main__':print(json.dumps(run(sys.argv[1]),sort_keys=True,indent=2))
