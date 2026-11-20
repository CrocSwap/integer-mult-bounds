"""Verify the exact adjoint second contraction against the first frozen graph."""
import gzip, hashlib, json
from collections import defaultdict
from fractions import Fraction as Q
from pathlib import Path

HERE=Path(__file__).resolve().parent
FIRST='320847d42f2655c3cc0fd29fe670ae77277e9c2f377c1c92f33d7df050872f54'
SECOND='7660985e0b618cdbee13e4190a4c6d5f91fbdf01a8f7a5186fdde8b980c19b48'
READERS={155347,155539,155541,155542,155590,155594,155595,155612,155616,155684,155687,155717,155862,156055}

def load(path,digest):
    obj=json.loads(gzip.decompress(path.read_bytes()))
    assert hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()==digest
    return obj

def adjoint(w):
    first=w['first_output']; n=len(w['initial'])
    moves={k:(b,a) for k,a,b in w['moves']}
    forms={k:{} for k in (*moves,*range(first,first+n))}
    for reader,row in w['forms']:
        donor=reader if reader in moves else ~(reader-first)
        for old,c in row:
            node=old if old>=0 else first+~old
            forms[node][donor]=Q(c)
    order=[k for k in reversed(w['schedule']) if k in moves]+list(range(first,first+n))
    return moves,forms,order

def add(row,other,factor):
    for k,v in other.items():
        q=row.get(k,Q(0))+factor*v
        if q: row[k]=q
        else: row.pop(k,None)

def main():
    a=load(HERE/'CANDIDATE.json.gz',FIRST); b=load(HERE/'DOUBLE-CANDIDATE.json.gz',SECOND)
    assert all(a[k]==b[k] for k in a if k not in ('moves','forms','schedule'))
    am,af,ao=adjoint(a); bm,bf,bo=adjoint(b)
    assert set(am)-set(bm)=={94025} and not set(bm)-set(am)
    assert am[94025]==(304,2) and am[94019]==(2,3) and bm[94019]==(304,3)
    assert all(bm[i]==am[i] for i in bm if i!=94019)
    assert [i for i in ao if i!=94025]==bo
    assert set(af)-set(bf)=={94025} and not set(bf)-set(af)
    assert bf[94019]=={-1288:Q(-1,1536),94034:Q(1,8)}
    assert {i for i in af if 94025 in af[i]}=={94019}
    assert {i for i in af if 94019 in af[i]}==READERS
    for i in set(af)&set(bf)-{94019}:
        row=af[i].copy()
        if i in READERS: add(row,{90072:Q(-1,8),90555:Q(-1,2)},row[94019])
        assert row==bf[i],i
    pos={i:n for n,i in enumerate(ao)}
    assert all(pos[x]<pos[i] for i in READERS for x in (94019,90072,90555))
    needs={94019,94034,90072,90555}
    for i in reversed(ao):
        if i in needs: needs.update(k for k in af[i] if k>=0)
    values={~i:{i:Q(1)} for i in range(len(a['final']))}
    for i in ao:
        if i in needs:
            row={}
            for k,c in af[i].items(): add(row,values[k],c)
            values[i]=row
    identity={}
    for k,c in ((-1288,Q(-1,1536)),(94034,Q(1,8)),(90072,Q(-1,8)),(90555,Q(-1,2))): add(identity,values[k],c)
    assert identity==values[94019]
    print('PASS_EXACT_ADJOINT_SECOND_CONTRACTION',SECOND)

if __name__=='__main__': main()
